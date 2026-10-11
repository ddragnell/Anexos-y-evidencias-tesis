"""Filtra por relevancia los prompts en español de GPT-4-Prompts y los
pre-anota con el mecanismo para importarlos en Doccano.

Entrada: el JSONL (o CSV/TXT, un prompt por línea) que ya quedó después
del filtro de idioma. Se aceptan los campos "text", "prompt" o "content".

Pasos (todos reproducibles con semilla fija):
1. Limpieza: quita espacios repetidos y descarta textos de menos de
   --min-palabras o más de --max-caracteres.
2. Deduplicación exacta (texto normalizado en minúsculas).
3. Relevancia: puntaje = palabras clave de contexto empresarial/técnico
   presentes + 2 si el mecanismo detecta alguna entidad de la taxonomía
   distinta de LOC y DATE.
   Se descartan los de puntaje 0 (saludos, chistes, trivia sin contexto).
4. Muestra estratificada de --n prompts: la mitad con entidades
   detectadas y la otra mitad relevantes sin entidades, para no inflar
   la proporción de prompts sensibles.
5. Pre-anotación: las entidades que detecta el mecanismo híbrido se
   escriben en "label" para que en Doccano solo haya que corregir.
   Las anotaciones deben revisarse una por una: la pre-anotación no es
   la referencia.

Salida: datos/doccano/para_anotar.jsonl ({"text", "label", "meta"}),
listo para Doccano > Dataset > Import > JSONL (columna de etiquetas: label),
y un resumen con los conteos de cada paso para reportar en el documento.

Uso:
  python scripts/preparar_doccano.py --entrada ruta\\prompts_es.jsonl --n 300
"""
import argparse
import csv
import json
import random
import re
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

from mecanismo.mecanismo import Mecanismo  # noqa: E402
from mecanismo.ner_detector import DetectorNER  # noqa: E402

PALABRAS_CONTEXTO = [
    # empresa y trabajo
    "empresa", "cliente", "proveedor", "empleado", "trabajador", "jefe", "gerente", "equipo", "reunión",
    "proyecto", "contrato", "factura", "pago", "cuenta", "banco", "nómina", "salario", "vacaciones",
    "hoja de vida", "currículum", "entrevista", "cargo", "carta", "correo", "email", "informe", "reporte",
    "presupuesto", "ventas", "cotización", "pedido", "envío", "inventario", "política", "legal", "abogado",
    "demanda", "cláusula", "acta", "propuesta", "negocio", "marketing", "campaña", "soporte", "ticket",
    # datos personales
    "nombre", "teléfono", "celular", "dirección", "cédula", "documento", "identificación", "nacimiento",
    "fecha", "datos personales",
    # técnico
    "código", "servidor", "base de datos", "contraseña", "usuario", "api", "token", "clave", "script",
    "python", "sql", "error", "configuración", "red", "ip", "login", "sistema", "aplicación",
]
P_CONTEXTO = re.compile(r"\b(?:" + "|".join(re.escape(p) for p in PALABRAS_CONTEXTO) + r")\b", re.I)


def leer(ruta):
    p = Path(ruta)
    if p.suffix.lower() == ".csv":
        with open(p, encoding="utf-8", newline="") as f:
            for fila in csv.DictReader(f):
                yield fila.get("text") or fila.get("prompt") or fila.get("content") or "", {}
    elif p.suffix.lower() == ".txt":
        for l in open(p, encoding="utf-8"):
            yield l.strip(), {}
    else:
        for l in open(p, encoding="utf-8"):
            if l.strip():
                d = json.loads(l)
                meta = d.get("meta") if isinstance(d.get("meta"), dict) else {}
                yield d.get("text") or d.get("prompt") or d.get("content") or "", meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrada", required=True)
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--min-palabras", type=int, default=5)
    ap.add_argument("--max-caracteres", type=int, default=2000)
    ap.add_argument("--semilla", type=int, default=13)
    ap.add_argument("--salida", default="datos/doccano/para_anotar.jsonl")
    ap.add_argument("--sin-preanotacion", action="store_true")
    ap.add_argument("--ner-backend", default="spacy", choices=["spacy", "hf"])
    ap.add_argument("--ner-modelo", default="modelos/ner-spacy-meddocan",
                    help="NER para el filtro y la pre-anotación (por defecto el entrenado con MEDDOCAN)")
    a = ap.parse_args()

    conteo = {"leidos": 0, "tras_longitud": 0, "tras_deduplicar": 0, "relevantes": 0,
              "relevantes_con_entidades": 0}
    vistos, candidatos = set(), []
    mec = Mecanismo("hibrido", ner=DetectorNER(a.ner_backend, a.ner_modelo))
    for i, (texto, meta) in enumerate(leer(a.entrada)):
        conteo["leidos"] += 1
        texto = re.sub(r"[ \t]+", " ", texto).strip()
        if len(texto.split()) < a.min_palabras or len(texto) > a.max_caracteres:
            continue
        conteo["tras_longitud"] += 1
        clave = texto.lower()
        if clave in vistos:
            continue
        vistos.add(clave)
        conteo["tras_deduplicar"] += 1
        kw = len(set(m.group().lower() for m in P_CONTEXTO.finditer(texto)))
        ents = mec.detectar(texto)
        # LOC y DATE solos no vuelven relevante un prompt ("capital de Francia")
        puntaje = kw + (2 if any(e.etiqueta not in ("LOC", "DATE") for e in ents) else 0)
        if puntaje == 0:
            continue
        conteo["relevantes"] += 1
        conteo["relevantes_con_entidades"] += bool(ents)
        candidatos.append({"text": texto, "ents": ents, "puntaje": puntaje,
                           "meta": {**meta, "fila_origen": i, "puntaje_relevancia": puntaje}})

    r = random.Random(a.semilla)
    con = [c for c in candidatos if c["ents"]]
    sin = [c for c in candidatos if not c["ents"]]
    r.shuffle(con)
    r.shuffle(sin)
    k = min(len(con), a.n // 2)
    muestra = con[:k] + sin[:a.n - k]
    r.shuffle(muestra)

    out = Path(a.salida)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for j, c in enumerate(muestra):
            etq = [] if a.sin_preanotacion else [[e.inicio, e.fin, e.etiqueta] for e in c["ents"]]
            f.write(json.dumps({"text": c["text"], "label": etq,
                                "meta": {**c["meta"], "id": f"gpt4p-{j:04d}", "fuente": "erfanzar/GPT-4-Prompts"}},
                               ensure_ascii=False) + "\n")
    conteo["muestra"] = len(muestra)
    conteo["muestra_con_preanotacion"] = sum(bool(c["ents"]) for c in muestra)
    json.dump(conteo, open(out.with_name("resumen_filtrado.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps(conteo, indent=1))


if __name__ == "__main__":
    main()
