"""Convierte MEDDOCAN (BRAT .txt/.ann) al formato de exportación de Doccano con
las etiquetas de la taxonomía, para entrenar el NER y para evaluar el
mecanismo sobre anotaciones hechas por terceros.

Correspondencia (las etiquetas sin equivalente se descartan):
  NOMBRE_SUJETO_ASISTENCIA, NOMBRE_PERSONAL_SANITARIO, FAMILIARES_SUJETO_ASISTENCIA -> PER
  CALLE -> ADDRESS          TERRITORIO, PAIS -> LOC
  HOSPITAL, INSTITUCION, CENTRO_SALUD -> ORG       FECHAS -> DATE
  CORREO_ELECTRONICO -> EMAIL      NUMERO_TELEFONO, NUMERO_FAX -> PHONE
  URL_WEB -> URL                   DIREC_PROT_INTERNET -> NET_DIGITAL
Se descartan EDAD, SEXO, PROFESION, OTROS_SUJETO_ASISTENCIA y los ID_* (números
de historia clínica, colegiado o aseguramiento), que no corresponden a los
documentos de identidad de ID_DOC (CC, CE, NIT, pasaporte).

Uso: python scripts/convertir_meddocan.py --meddocan ruta\\meddocan --salida datos/meddocan
     (genera train.jsonl, dev.jsonl y test.jsonl, respetando la partición oficial)
"""
import argparse
import json
from pathlib import Path

MAPEO_MEDDOCAN = {
    "NOMBRE_SUJETO_ASISTENCIA": "PER", "NOMBRE_PERSONAL_SANITARIO": "PER", "FAMILIARES_SUJETO_ASISTENCIA": "PER",
    "CALLE": "ADDRESS", "TERRITORIO": "LOC", "PAIS": "LOC",
    "HOSPITAL": "ORG", "INSTITUCION": "ORG", "CENTRO_SALUD": "ORG",
    "FECHAS": "DATE", "CORREO_ELECTRONICO": "EMAIL", "NUMERO_TELEFONO": "PHONE", "NUMERO_FAX": "PHONE",
    "URL_WEB": "URL", "DIREC_PROT_INTERNET": "NET_DIGITAL",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meddocan", required=True, help="carpeta con train/ dev/ test/ (cada una con brat/)")
    ap.add_argument("--salida", default="datos/meddocan")
    a = ap.parse_args()
    out = Path(a.salida)
    out.mkdir(parents=True, exist_ok=True)
    for split in ("train", "dev", "test"):
        brat = Path(a.meddocan) / split / "brat"
        n = n_ent = 0
        with open(out / f"{split}.jsonl", "w", encoding="utf-8") as f:
            for txt in sorted(brat.glob("*.txt")):
                texto = txt.read_text(encoding="utf-8")
                etq = []
                ann = txt.with_suffix(".ann")
                for linea in ann.read_text(encoding="utf-8").splitlines() if ann.exists() else []:
                    if not linea.startswith("T"):
                        continue
                    _, tipo_pos, valor = linea.split("\t", 2)
                    tipo, *pos = tipo_pos.split(" ")
                    if ";" in " ".join(pos) or tipo not in MAPEO_MEDDOCAN:
                        continue  # spans discontinuos o etiquetas fuera de la taxonomía
                    ini, fin = int(pos[0]), int(pos[1])
                    assert texto[ini:fin] == valor, (txt.name, linea)
                    etq.append([ini, fin, MAPEO_MEDDOCAN[tipo]])
                f.write(json.dumps({"id": f"meddocan-{split}-{txt.stem}", "text": texto, "label": sorted(etq),
                                    "meta": {"fuente": "MEDDOCAN", "split": split}}, ensure_ascii=False) + "\n")
                n += 1
                n_ent += len(etq)
        print(split, n, "documentos,", n_ent, "entidades")


if __name__ == "__main__":
    main()
