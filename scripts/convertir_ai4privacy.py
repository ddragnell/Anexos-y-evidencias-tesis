"""Convierte el subconjunto en español de ai4privacy/open-pii-masking-500k-ai4privacy
(CC BY 4.0) al formato de exportación de Doccano con las etiquetas de la
taxonomía, para un preentrenamiento intermedio del NER antes del ajuste con
MEDDOCAN y con el corpus anotado en Doccano.

Solo se conservan las etiquetas de las que el NER es responsable en el
enfoque híbrido; el resto se descarta (queda como O):
  GIVENNAME, SURNAME (y variantes de nombre) -> PER, uniendo nombre y
      apellidos contiguos en una sola mención; TITLE ("Sr.", "Dra.") no se
      incluye, como pide la guía de anotación (sección 7.3).
  STREET + BUILDINGNUM contiguos (y SECONDARYADDRESS) -> ADDRESS; el código
      postal y la ciudad no forman parte de la dirección.
  CITY (y STATE, COUNTRY si existen) -> LOC.
El conjunto no tiene etiqueta de organización, así que ORG no se aprende en
esta etapa: el modelo se vuelve a ajustar después con MEDDOCAN, que sí la tiene.

Solo se usa el split train del dataset (se separa una validación propia con
semilla fija); su split validation no se usa.

Uso (necesita acceso a Hugging Face; en Colab):
  python scripts/convertir_ai4privacy.py --n 20000 --salida datos/ai4privacy
  -> datos/ai4privacy/entrenamiento.jsonl, validacion.jsonl, resumen.json
"""
import argparse
import json
import random
import re
from collections import Counter
from pathlib import Path

GRUPO = {
    "PER": {"GIVENNAME", "SURNAME", "FIRSTNAME", "LASTNAME", "MIDDLENAME", "NAME", "FULLNAME"},
    "ADDRESS": {"STREET", "BUILDINGNUM", "STREETADDRESS", "SECONDARYADDRESS"},
    "LOC": {"CITY", "STATE", "COUNTRY", "COUNTY"},
}
A_TAXONOMIA = {l: t for t, ls in GRUPO.items() for l in ls}
# separadores permitidos entre partes contiguas de una misma mención
SEP = {"PER": re.compile(r"[ \t\-]{1,3}"), "ADDRESS": re.compile(r"[ \t,#ºª°.nN-]{1,5}")}


def a_spans(texto, mascara):
    """privacy_mask -> [[ini, fin, etiqueta]] de la taxonomía, uniendo partes contiguas."""
    partes = sorted((m["start"], m["end"], A_TAXONOMIA[m["label"]]) for m in mascara if m["label"] in A_TAXONOMIA)
    spans = []
    for s, e, t in partes:
        if spans and spans[-1][2] == t and t in SEP and SEP[t].fullmatch(texto[spans[-1][1]:s] or " "):
            spans[-1][1] = e
        else:
            spans.append([s, e, t])
    return spans


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="ai4privacy/open-pii-masking-500k-ai4privacy")
    ap.add_argument("--idioma", default="es")
    ap.add_argument("--n", type=int, default=20000, help="textos de entrenamiento (muestra con semilla fija)")
    ap.add_argument("--n-val", type=int, default=2000)
    ap.add_argument("--semilla", type=int, default=13)
    ap.add_argument("--salida", default="datos/ai4privacy")
    a = ap.parse_args()

    from datasets import load_dataset
    ds = load_dataset(a.dataset, split="train", streaming=True)
    filas, inventario, locales = [], Counter(), Counter()
    for r in ds:
        if r.get("language") != a.idioma:
            continue
        mascara = r["privacy_mask"]
        if isinstance(mascara, str):
            mascara = json.loads(mascara)
        inventario.update(m["label"] for m in mascara)
        locales[r.get("locale")] += 1
        filas.append({"text": r["source_text"], "label": a_spans(r["source_text"], mascara),
                      "meta": {"id": r.get("id"), "locale": r.get("locale"), "fuente": a.dataset}})

    rnd = random.Random(a.semilla)
    rnd.shuffle(filas)
    val, train = filas[:a.n_val], filas[a.n_val:a.n_val + a.n]
    out = Path(a.salida)
    out.mkdir(parents=True, exist_ok=True)
    for nombre, docs in (("entrenamiento", train), ("validacion", val)):
        with open(out / f"{nombre}.jsonl", "w", encoding="utf-8") as f:
            for d in docs:
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
    resumen = {
        "dataset": a.dataset, "idioma": a.idioma, "filas_idioma": len(filas), "locales": dict(locales),
        "entrenamiento": len(train), "validacion": len(val), "semilla": a.semilla,
        "etiquetas_origen": dict(inventario.most_common()),
        "etiquetas_usadas": {l: t for l, t in A_TAXONOMIA.items() if l in inventario},
        "menciones_taxonomia": dict(Counter(s[2] for d in train for s in d["label"])),
    }
    (out / "resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
