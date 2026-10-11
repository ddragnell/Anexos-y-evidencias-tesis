"""Prepara la muestra para la validación cruzada de la anotación con el asesor
(acuerdo entre anotadores, sección 7.3): el 15 % del corpus anotado en Doccano,
con un mínimo de 50 textos, elegido al azar con semilla fija.

Se generan dos archivos:
  muestra_asesor.jsonl     solo el texto (sin etiquetas), para importar en un
                           proyecto aparte de Doccano y que el asesor anote a
                           ciegas siguiendo la guía (Anexo D).
  referencia_andres.jsonl  las mismas filas con la anotación de Andrés, para
                           calcular el acuerdo con scripts/acuerdo_anotadores.py.

La muestra se estratifica por partición (entrenamiento, validación y prueba,
en proporción a su tamaño) y usa un generador aleatorio propio, distinto del
de la partición, para que no se concentre en una sola parte. No cambia
ninguna partición ni ningún resultado.

Uso: python scripts/muestra_asesor.py --datos datos/doccano --salida datos/acuerdo
"""
import argparse
import hashlib
import json
import math
import random
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datos", default="datos/doccano")
    ap.add_argument("--salida", default="datos/acuerdo")
    ap.add_argument("--fraccion", type=float, default=0.15)
    ap.add_argument("--minimo", type=int, default=50)
    ap.add_argument("--semilla", type=int, default=13)
    a = ap.parse_args()
    partes = {}
    for parte in ("entrenamiento", "validacion", "prueba"):
        fs = [json.loads(l) for l in open(Path(a.datos) / f"{parte}.jsonl", encoding="utf-8") if l.strip()]
        for d in fs:
            d["particion"] = parte
        fs.sort(key=lambda d: hashlib.sha1(d["text"].encode("utf-8")).hexdigest())
        partes[parte] = fs
    total = sum(len(fs) for fs in partes.values())
    n = min(total, max(a.minimo, math.ceil(a.fraccion * total)))
    # reparto proporcional por resto mayor
    cuota = {p: n * len(fs) / total for p, fs in partes.items()}
    k = {p: int(c) for p, c in cuota.items()}
    for p in sorted(cuota, key=lambda p: cuota[p] - k[p], reverse=True)[:n - sum(k.values())]:
        k[p] += 1
    rnd = random.Random(f"acuerdo-{a.semilla}")
    muestra = [d for p, fs in partes.items() for d in rnd.sample(fs, k[p])]
    rnd.shuffle(muestra)
    out = Path(a.salida)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "muestra_asesor.jsonl", "w", encoding="utf-8") as f:
        for d in muestra:
            f.write(json.dumps({"text": d["text"], "id_origen": d["id"]}, ensure_ascii=False) + "\n")
    with open(out / "referencia_andres.jsonl", "w", encoding="utf-8") as f:
        for d in muestra:
            f.write(json.dumps({"id_origen": d["id"], "text": d["text"], "label": d["label"],
                                "particion": d["particion"]}, ensure_ascii=False) + "\n")
    print(f"{n} de {total} textos {k} -> {out}")


if __name__ == "__main__":
    main()
