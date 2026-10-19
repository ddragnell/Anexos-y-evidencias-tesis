"""Sesgo de pre-anotación y validación cruzada (secciones 8.2 y 8.4 de la tesis).

Compara, en los 50 prompts de la validación cruzada:
  - la pre-anotación del mecanismo con la anotación del autor y con la del segundo anotador;
  - las detecciones del enfoque híbrido con ambas anotaciones, en los prompts de prueba
    y de validación que forman parte de la muestra.

Las dos anotaciones se recortan igual que en scripts/acuerdo_anotadores.py
(particionar_doccano.recortar), para que un espacio en el borde no cuente como desacuerdo.
Los datos de Doccano y de la validación cruzada no se publican (sección 7.5), así que este
script solo se puede ejecutar con la copia local de esos archivos.

Uso:
  python scripts/sesgo_preanotacion.py
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from particionar_doccano import recortar  # noqa: E402


def leer(ruta):
    return [json.loads(l) for l in open(ruta, encoding="utf-8") if l.strip()]


def clave(texto):
    return texto.replace("\r\n", "\n").strip()


def spans(texto, etiquetas):
    return {tuple(x[:3]) for x in recortar(texto, [list(x[:3]) for x in etiquetas])[0]}


def f1(ref, pred):
    tp = len(ref & pred)
    p = tp / len(pred) if pred else 0.0
    r = tp / len(ref) if ref else 0.0
    return {"coinciden": tp, "referencia": len(ref), "prediccion": len(pred),
            "F1": round(2 * p * r / (p + r), 3) if p + r else 0.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--autor", default="datos/acuerdo/referencia_andres.jsonl")
    ap.add_argument("--segundo", default="datos/acuerdo/export_companero.jsonl")
    ap.add_argument("--preanotacion", default="datos/doccano/para_anotar.jsonl")
    ap.add_argument("--salidas", nargs="+", default=["resultados/doccano_prueba_final/salidas_hibrido.jsonl",
                                                    "resultados/doccano_validacion_final/salidas_hibrido.jsonl"])
    a = ap.parse_args()

    autor = leer(a.autor)
    segundo = {d["id_origen"]: d for d in leer(a.segundo)}
    pre = {clave(d["text"]): d.get("label", []) for d in leer(a.preanotacion)}
    detecciones = {}
    for ruta in a.salidas:
        conjunto = "prueba" if "prueba" in ruta else "validacion"
        for d in leer(ruta):
            detecciones[clave(d["texto"])] = (conjunto, {(e["inicio"], e["fin"], e["etiqueta"]) for e in d["pred"]})

    A, B, P = set(), set(), set()
    sin_pre = {"autor": Counter(), "segundo": Counter()}
    por_conjunto = {"prueba": [set(), set(), set()], "prueba+validacion": [set(), set(), set()]}
    for i, r in enumerate(autor):
        t = r["text"]
        s = segundo[r["id_origen"]]
        sa, sb = spans(t, r["label"]), spans(s["text"], s["label"])
        sp = spans(t, pre.get(clave(t), []))
        A |= {(i,) + x for x in sa}
        B |= {(i,) + x for x in sb}
        P |= {(i,) + x for x in sp}
        for nombre, conj in (("autor", sa), ("segundo", sb)):
            for ini, fin, etq in conj:
                if not any(etq == pe and ini < pf and fin > pi for pi, pf, pe in sp):
                    sin_pre[nombre][etq] += 1
        if clave(t) in detecciones:
            conjunto, h = detecciones[clave(t)]
            claves = ["prueba+validacion"] + (["prueba"] if conjunto == "prueba" else [])
            for k in claves:
                por_conjunto[k][0] |= {(i,) + x for x in sa}
                por_conjunto[k][1] |= {(i,) + x for x in sb}
                por_conjunto[k][2] |= {(i,) + x for x in h}

    res = {
        "preanotacion_vs_autor": f1(A, P),
        "preanotacion_vs_segundo": f1(B, P),
        "no_preanotadas": {k: {"total": sum(v.values()), **v} for k, v in sin_pre.items()},
        "hibrido": {k: {"vs_autor": f1(v[0], v[2]), "vs_segundo": f1(v[1], v[2])} for k, v in por_conjunto.items()},
    }
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
