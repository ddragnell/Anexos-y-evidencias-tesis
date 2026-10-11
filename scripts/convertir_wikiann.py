"""Convierte la configuración en español de unimelb-nlp/wikiann (fragmentos de
Wikipedia con PER, ORG y LOC, incluidas entidades latinoamericanas y
colombianas) al formato de exportación de Doccano, para el preentrenamiento
intermedio del NER junto con AI4Privacy.

Los tokens se unen con un espacio para reconstruir el texto y se calculan
los desplazamientos de cada entidad. Etiquetas: PER -> PER, ORG -> ORG,
LOC -> LOC (la taxonomía no distingue país, ciudad o región).

Se usan el split train para entrenar y una muestra del split validation
para validar; el split test no se usa.

Uso (necesita acceso a Hugging Face; en Colab):
  python scripts/convertir_wikiann.py --salida datos/wikiann
  -> datos/wikiann/entrenamiento.jsonl, validacion.jsonl, resumen.json
"""
import argparse
import json
import random
from collections import Counter
from pathlib import Path

ETIQUETAS_WIKIANN = ["O", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"]


def a_doc(tokens, tags):
    texto, ini, spans, actual = "", [], [], None
    for tok in tokens:
        if texto:
            texto += " "
        ini.append(len(texto))
        texto += tok
    for k, t in enumerate(tags):
        etq = ETIQUETAS_WIKIANN[t]
        if etq.startswith("B-") or (etq.startswith("I-") and (actual is None or actual[2] != etq[2:])):
            actual = [ini[k], ini[k] + len(tokens[k]), etq[2:]]
            spans.append(actual)
        elif etq.startswith("I-"):
            actual[1] = ini[k] + len(tokens[k])
        else:
            actual = None
    return {"text": texto, "label": spans}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="unimelb-nlp/wikiann")
    ap.add_argument("--config", default="es")
    ap.add_argument("--n-val", type=int, default=2000)
    ap.add_argument("--semilla", type=int, default=13)
    ap.add_argument("--salida", default="datos/wikiann")
    a = ap.parse_args()

    from datasets import load_dataset
    out = Path(a.salida)
    out.mkdir(parents=True, exist_ok=True)
    resumen = {"dataset": a.dataset, "config": a.config, "semilla": a.semilla}
    for split, nombre in (("train", "entrenamiento"), ("validation", "validacion")):
        docs = [a_doc(r["tokens"], r["ner_tags"]) for r in load_dataset(a.dataset, a.config, split=split)]
        if split == "validation":
            random.Random(a.semilla).shuffle(docs)
            docs = docs[:a.n_val]
        with open(out / f"{nombre}.jsonl", "w", encoding="utf-8") as f:
            for j, d in enumerate(docs):
                d["meta"] = {"id": f"wikiann-{split}-{j}", "fuente": a.dataset}
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
        resumen[nombre] = {"textos": len(docs), "menciones": dict(Counter(s[2] for d in docs for s in d["label"]))}
    (out / "resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
