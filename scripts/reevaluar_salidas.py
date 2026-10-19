"""Reevalúa un conjunto con las detecciones guardadas del mecanismo y Presidio recalculado.

Sirve para actualizar las métricas sin volver a correr el NER, cuando cambia la
referencia (por ejemplo, al anotar los países como LOC en el corpus sintético)
o la configuración de Presidio (es_core_news_lg en lugar de es_core_news_sm).
Las detecciones de regex, NER e híbrido se leen de resultados/<origen>/salidas_*.jsonl
y se comprueba que correspondan, texto por texto, a los datos dados.

Uso:
  python scripts/reevaluar_salidas.py --datos datos/sintetico/test.jsonl \
      --origen resultados/sintetico_test_final --nombre sintetico_test_final --guardar-salidas
  -> resultados/<nombre>/{metricas.json, tablas.md[, salidas_*.jsonl]}
Las salidas solo deben guardarse con datos sintéticos o públicos (sección 7.5).
"""
import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "scripts"))

from evaluar_deteccion import cargar, tabla_deteccion  # noqa: E402
from mecanismo.entidad import Entidad  # noqa: E402
from mecanismo.heuristica import decidir  # noqa: E402
from mecanismo.mecanismo import enmascarar  # noqa: E402
from mecanismo.metricas import deteccion, proteccion  # noqa: E402
from mecanismo.taxonomia import DIRECTAS  # noqa: E402


def leer(ruta):
    filas = [json.loads(l) for l in open(ruta, encoding="utf-8")]
    return [r["texto"] for r in filas], [[Entidad(**e) for e in r["pred"]] for r in filas]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datos", required=True)
    ap.add_argument("--origen", required=True, help="carpeta con salidas_regex/ner/hibrido.jsonl")
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--modelo-presidio", default="es_core_news_lg")
    ap.add_argument("--guardar-salidas", action="store_true")
    a = ap.parse_args()

    docs = cargar(a.datos)
    textos = [d["text"] for d in docs]
    gold = [d["gold"] for d in docs]
    preds_por_sistema = {}
    for s in ("regex", "ner", "hibrido"):
        t, p = leer(Path(a.origen) / f"salidas_{s}.jsonl")
        if t != textos:
            raise SystemExit(f"salidas_{s}.jsonl no corresponde a {a.datos}")
        preds_por_sistema[s] = p
    from mecanismo.presidio_baseline import DetectorPresidio
    presidio = DetectorPresidio(a.modelo_presidio)
    preds_por_sistema["presidio"] = [presidio.detectar(t) for t in textos]
    preds_por_sistema["hibrido+heuristica"] = preds_por_sistema["hibrido"]

    out = RAIZ / "resultados" / a.nombre
    out.mkdir(parents=True, exist_ok=True)
    res = {}
    for s, preds in preds_por_sistema.items():
        tuplas = [[(e.inicio, e.fin, e.etiqueta) for e in p] for p in preds]
        if s == "hibrido+heuristica":
            decisiones = [decidir(p) for p in preds]
        else:
            decisiones = [{"accion": "ENMASCARAR" if p else "ENVIAR"} for p in preds]
        masc = [t if dec["accion"] == "ENMASCARAR" else [] for t, dec in zip(tuplas, decisiones)]
        enviados = [enmascarar(tx, p) if dec["accion"] == "ENMASCARAR" else tx
                    for tx, p, dec in zip(textos, preds, decisiones)]
        r = {"deteccion": {"estricto": deteccion(gold, tuplas, "estricto"),
                           "parcial": deteccion(gold, tuplas, "parcial")},
             "proteccion": proteccion(textos, gold, masc, enviados)}
        sens = [any(g[2] in DIRECTAS for g in gd) for gd in gold]
        limpios = [not gd for gd in gold]
        r["decision"] = {
            "prompts": len(docs), "con_id_directo": sum(sens), "limpios": sum(limpios),
            "sensibles_enviados_sin_enmascarar": sum(1 for x, dec in zip(sens, decisiones) if x and dec["accion"] == "ENVIAR"),
            "limpios_enmascarados": sum(1 for x, dec in zip(limpios, decisiones) if x and dec["accion"] == "ENMASCARAR"),
            "enmascarados": sum(dec["accion"] == "ENMASCARAR" for dec in decisiones),
        }
        res[s] = r
        if a.guardar_salidas:
            with open(out / f"salidas_{s.replace('+', '_')}.jsonl", "w", encoding="utf-8") as f:
                for d, p, dec, env in zip(docs, preds, decisiones, enviados):
                    f.write(json.dumps({"id": d.get("id"), "texto": d["text"], "gold": d["gold"],
                                        "pred": [e.dict() for e in p], "decision": dec, "texto_enviado": env},
                                       ensure_ascii=False) + "\n")
    orden = ["regex", "ner", "hibrido", "presidio", "hibrido+heuristica"]
    res = {s: res[s] for s in orden}
    json.dump(res, open(out / "metricas.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    fmt = lambda x: "—" if x is None else f"{x:.3f}"  # noqa: E731
    md = [f"# Resultados de detección: {a.nombre}", "",
          f"Datos: `{a.datos}` ({len(docs)} prompts, {sum(len(g) for g in gold)} entidades de referencia). "
          f"Detecciones de regex, NER e híbrido tomadas de `{a.origen}`; Presidio con {a.modelo_presidio}.", "",
          "## Detección por etiqueta, F1 / F2 (coincidencia estricta: mismo span y etiqueta)", "",
          tabla_deteccion(res, orden, "estricto"), "",
          "## Detección por etiqueta, F1 / F2 (coincidencia parcial: solapamiento y misma etiqueta)", "",
          tabla_deteccion(res, orden, "parcial"), "",
          "## Agregado (micro, estricto)", "",
          "| Sistema | P | R | F1 | F2 | F2 id. directos y secretos |", "|---|---|---|---|---|---|"]
    for s in orden:
        m, di = res[s]["deteccion"]["estricto"]["micro"], res[s]["deteccion"]["estricto"]["directas"]
        md.append(f"| {s} | {m['P']:.3f} | {m['R']:.3f} | {m['F1']:.3f} | {m['F2']:.3f} | {di['F2']:.3f} |")
    md += ["", "## Protección (sobre el texto enviado)", "",
           "| Sistema | ER_di | ER_qi | WP | Fuga residual |", "|---|---|---|---|---|"]
    for s in orden:
        p = res[s]["proteccion"]
        md.append(f"| {s} | {fmt(p['ER_di'])} | {fmt(p['ER_qi'])} | {fmt(p['WP'])} | {fmt(p['fuga_residual'])} |")
    md += ["", "## Decisión a nivel de prompt", "",
           "| Sistema | Enmascarados | Con id. directo enviados sin enmascarar | Limpios enmascarados |", "|---|---|---|---|"]
    for s in orden:
        d = res[s]["decision"]
        md.append(f"| {s} | {d['enmascarados']}/{d['prompts']} | {d['sensibles_enviados_sin_enmascarar']}/{d['con_id_directo']} | {d['limpios_enmascarados']}/{d['limpios']} |")
    (out / "tablas.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[-22:]))


if __name__ == "__main__":
    main()
