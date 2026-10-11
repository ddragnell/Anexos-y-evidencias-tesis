"""Evaluación de detección y protección: regex vs NER vs híbrido vs Presidio.

Lee un JSONL en formato de exportación de Doccano ({"text", "label"}),
que puede ser el corpus sintético o el corpus anotado en Doccano, corre
cada sistema y guarda:
  resultados/<nombre>/metricas.json   todas las métricas
  resultados/<nombre>/tablas.md       tablas listas para el documento
  resultados/<nombre>/salidas_<sistema>.jsonl  entidades y texto enviado
(Las salidas se conservan porque el corpus es sintético/público, como
prevé la sección 5.)

Sistemas:
  regex              solo expresiones regulares (enmascara todo lo detectado)
  ner                solo NER
  hibrido            NER + regex con consolidación (enmascara todo)
  hibrido+heuristica el mecanismo completo: la heurística decide si enmascarar
  presidio           línea base

Uso:
  python scripts/evaluar_deteccion.py --datos datos/sintetico/test.jsonl --nombre sintetico_test
  python scripts/evaluar_deteccion.py --datos doccano.jsonl --ner-backend hf --ner-modelo ruta/al/modelo
"""
import argparse
import json
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

from mecanismo.mecanismo import Mecanismo, enmascarar  # noqa: E402
from mecanismo.heuristica import decidir  # noqa: E402
from mecanismo.metricas import deteccion, proteccion  # noqa: E402
from mecanismo.ner_detector import DetectorNER  # noqa: E402
from mecanismo.presidio_baseline import DetectorPresidio  # noqa: E402
from mecanismo.taxonomia import DIRECTAS, ETIQUETAS  # noqa: E402


def cargar(ruta):
    docs = []
    for linea in open(ruta, encoding="utf-8"):
        d = json.loads(linea)
        etq = d.get("label") or d.get("labels") or d.get("entities") or []
        if etq and isinstance(etq[0], dict):  # export de Doccano con objetos
            etq = [[e["start_offset"], e["end_offset"], e["label"]] for e in etq]
        d["gold"] = [tuple(x) for x in etq if x[2] in ETIQUETAS]
        docs.append(d)
    return docs


def tabla_deteccion(res, sistemas, modo):
    filas = ["| Etiqueta | " + " | ".join(sistemas) + " |", "|---|" + "---|" * len(sistemas)]
    for e in ETIQUETAS + ["micro"]:
        celdas = []
        for s in sistemas:
            d = res[s]["deteccion"][modo]
            m = d["micro"] if e == "micro" else d["por_etiqueta"].get(e)
            celdas.append("—" if not m or m["soporte"] == 0 else f"{m['F1']:.2f} / {m['F2']:.2f}")
        if any(c != "—" for c in celdas):
            filas.append(f"| {'**Agregado (micro)**' if e == 'micro' else e} | " + " | ".join(celdas) + " |")
    return "\n".join(filas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datos", required=True)
    ap.add_argument("--nombre", default=None)
    ap.add_argument("--ner-backend", default="spacy", choices=["spacy", "hf"])
    ap.add_argument("--ner-modelo", default=None)
    ap.add_argument("--sin-presidio", action="store_true")
    a = ap.parse_args()

    docs = cargar(a.datos)
    nombre = a.nombre or Path(a.datos).stem
    out = Path(__file__).resolve().parents[1] / "resultados" / nombre
    out.mkdir(parents=True, exist_ok=True)

    ner = DetectorNER(a.ner_backend, a.ner_modelo)
    detectores = {
        "regex": Mecanismo("regex"),
        "ner": Mecanismo("ner", ner=ner),
        "hibrido": Mecanismo("hibrido", ner=ner),
    }
    if not a.sin_presidio:
        detectores["presidio"] = DetectorPresidio()

    textos = [d["text"] for d in docs]
    gold = [d["gold"] for d in docs]
    res, preds_por_sistema = {}, {}
    for nombre_s, det in detectores.items():
        preds = [det.detectar(t) for t in textos]
        preds_por_sistema[nombre_s] = preds
    # el mecanismo completo reutiliza la detección del híbrido
    preds_por_sistema["hibrido+heuristica"] = preds_por_sistema["hibrido"]

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
        # decisión a nivel de prompt: un prompt con algún identificador directo de
        # referencia debe salir enmascarado; uno sin entidades de referencia, intacto.
        sens = [any(g[2] in DIRECTAS for g in gd) for gd in gold]
        limpios = [not gd for gd in gold]
        env_sin_masc = sum(1 for s_, dec in zip(sens, decisiones) if s_ and dec["accion"] == "ENVIAR")
        limp_masc = sum(1 for l_, dec in zip(limpios, decisiones) if l_ and dec["accion"] == "ENMASCARAR")
        r["decision"] = {
            "prompts": len(docs), "con_id_directo": sum(sens), "limpios": sum(limpios),
            "sensibles_enviados_sin_enmascarar": env_sin_masc,
            "limpios_enmascarados": limp_masc,
            "enmascarados": sum(dec["accion"] == "ENMASCARAR" for dec in decisiones),
        }
        res[s] = r
        if s != "hibrido":
            pass
        with open(out / f"salidas_{s.replace('+', '_')}.jsonl", "w", encoding="utf-8") as f:
            for d, p, dec, env in zip(docs, preds, decisiones, enviados):
                f.write(json.dumps({"id": d.get("id"), "texto": d["text"], "gold": d["gold"],
                                    "pred": [e.dict() for e in p], "decision": dec, "texto_enviado": env},
                                   ensure_ascii=False) + "\n")

    json.dump(res, open(out / "metricas.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    sistemas = list(res)
    md = [f"# Resultados de detección: {nombre}", "",
          f"Datos: `{a.datos}` ({len(docs)} prompts, {sum(len(g) for g in gold)} entidades de referencia). "
          f"NER: {a.ner_backend} {a.ner_modelo or ''}", "",
          "## Detección por etiqueta, F1 / F2 (coincidencia estricta: mismo span y etiqueta)", "",
          tabla_deteccion(res, sistemas, "estricto"), "",
          "## Detección por etiqueta, F1 / F2 (coincidencia parcial: solapamiento y misma etiqueta)", "",
          tabla_deteccion(res, sistemas, "parcial"), "",
          "## Agregado (micro, estricto)", "",
          "| Sistema | P | R | F1 | F2 | F2 id. directos y secretos |", "|---|---|---|---|---|---|"]
    for s in sistemas:
        m = res[s]["deteccion"]["estricto"]["micro"]
        di = res[s]["deteccion"]["estricto"]["directas"]
        md.append(f"| {s} | {m['P']:.3f} | {m['R']:.3f} | {m['F1']:.3f} | {m['F2']:.3f} | {di['F2']:.3f} |")
    md += ["", "## Protección (sobre el texto enviado)", "",
           "| Sistema | ER_di | ER_qi | WP | Fuga residual |", "|---|---|---|---|---|"]
    fmt = lambda x: "—" if x is None else f"{x:.3f}"  # noqa: E731
    for s in sistemas:
        p = res[s]["proteccion"]
        md.append(f"| {s} | {fmt(p['ER_di'])} | {fmt(p['ER_qi'])} | {fmt(p['WP'])} | {fmt(p['fuga_residual'])} |")
    md += ["", "## Decisión a nivel de prompt", "",
           "| Sistema | Enmascarados | Con id. directo enviados sin enmascarar | Limpios enmascarados |", "|---|---|---|---|"]
    for s in sistemas:
        d = res[s]["decision"]
        md.append(f"| {s} | {d['enmascarados']}/{d['prompts']} | {d['sensibles_enviados_sin_enmascarar']}/{d['con_id_directo']} | {d['limpios_enmascarados']}/{d['limpios']} |")
    (out / "tablas.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
