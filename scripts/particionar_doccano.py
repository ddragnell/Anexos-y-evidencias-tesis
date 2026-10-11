"""Divide el export de Doccano en entrenamiento (70 %), validación (15 %) y prueba (15 %).

La partición es aleatoria con semilla fija y se hace una sola vez, antes de
cualquier ajuste. prueba.jsonl no se usa para entrenar el NER, modificar
las regex ni fijar pesos y umbral de la heurística; se usa una sola vez en
la evaluación final.

Uso: python scripts/particionar_doccano.py --datos ruta\\doccano.jsonl --salida datos/doccano
"""
import argparse
import hashlib
import json
import random
from pathlib import Path

BORDE = " \t\n\r.,;:\"'"


def recortar(texto, etiquetas):
    """Quita espacios y signos de puntuación que quedaron en los bordes de un
    span al anotar ("España " -> "España"). No cambia qué se anotó."""
    out, n = [], 0
    for s, e, l in etiquetas:
        s0, e0 = s, e
        while s < e and texto[s] in BORDE:
            s += 1
        while e > s and texto[e - 1] in BORDE:
            e -= 1
        n += (s, e) != (s0, e0)
        if s < e:
            out.append([s, e, l])
    return out, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datos", required=True)
    ap.add_argument("--salida", default="datos/doccano")
    ap.add_argument("--semilla", type=int, default=13)
    a = ap.parse_args()
    filas = [l for l in open(a.datos, encoding="utf-8") if l.strip()]
    # orden canónico por texto antes de barajar: la partición no depende del orden del export
    filas.sort(key=lambda l: hashlib.sha1(json.loads(l)["text"].encode("utf-8")).hexdigest())
    random.Random(a.semilla).shuffle(filas)
    recortados = 0
    n = len(filas)
    n_tr, n_va = round(n * 0.70), round(n * 0.15)
    partes = {"entrenamiento": filas[:n_tr], "validacion": filas[n_tr:n_tr + n_va], "prueba": filas[n_tr + n_va:]}
    out = Path(a.salida)
    out.mkdir(parents=True, exist_ok=True)
    for nombre, fs in partes.items():
        with open(out / f"{nombre}.jsonl", "w", encoding="utf-8") as f:
            for l in fs:
                d = json.loads(l)
                etq = d.get("label") or d.get("entities") or []
                if etq and isinstance(etq[0], dict):
                    etq = [[x["start_offset"], x["end_offset"], x["label"]] for x in etq]
                d["label"], k = recortar(d["text"], etq)
                recortados += k
                d.setdefault("meta", {})
                if isinstance(d["meta"], dict):
                    d["meta"]["split"] = nombre
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
    print({k: len(v) for k, v in partes.items()}, "spans con bordes recortados:", recortados)


if __name__ == "__main__":
    main()
