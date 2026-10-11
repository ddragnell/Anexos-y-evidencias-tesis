# Datos

Solo se incluye el corpus sintético (`sintetico/dev.jsonl` y `sintetico/test.jsonl`), generado con `scripts/generar_corpus_sintetico.py`. Todos sus datos son ficticios, incluidas las credenciales de ejemplo (claves con formato `sk-proj-`, `AKIA`, `ghp_`, etc.), que no son reales.

Los demás conjuntos no se redistribuyen y se regeneran con los scripts:

| Conjunto | Por qué no se incluye | Cómo obtenerlo |
|---|---|---|
| Corpus anotado en Doccano (300 prompts) | Son prompts reales de usuarios tomados de `erfanzar/GPT-4-Prompts` en Hugging Face, pueden contener datos personales y no se verificó la licencia de redistribución | Descargar el dataset, `scripts/preparar_doccano.py`, anotar en Doccano y `scripts/particionar_doccano.py` |
| Muestra del acuerdo entre anotadores | Es un subconjunto del corpus de Doccano | `scripts/muestra_asesor.py` y `scripts/acuerdo_anotadores.py` |
| MEDDOCAN | Corpus de terceros: se usa bajo su licencia, que debe consultarse en su sitio oficial | Descargar MEDDOCAN (BRAT) y `scripts/convertir_meddocan.py` |
| AI4Privacy (`ai4privacy/open-pii-masking-500k-ai4privacy`, CC BY 4.0) | Se descarga directamente de Hugging Face | `scripts/convertir_ai4privacy.py` |
| WikiANN (`unimelb-nlp/wikiann`, español) | Se descarga directamente de Hugging Face; licencia por confirmar | `scripts/convertir_wikiann.py` |

Por la misma razón, en `resultados/` solo se incluyen las salidas por prompt (`salidas_*.jsonl`) de los conjuntos sintéticos; para Doccano y MEDDOCAN se incluyen las métricas y las tablas.
