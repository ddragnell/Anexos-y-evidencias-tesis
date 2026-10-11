# Resultados de detección: sintetico_dev_final

Datos: `datos/sintetico/dev.jsonl` (280 prompts, 727 entidades de referencia). NER: hf modelos/ner-bert-final

## Detección por etiqueta, F1 / F2 (coincidencia estricta: mismo span y etiqueta)

| Etiqueta | regex | ner | hibrido | hibrido+heuristica |
|---|---|---|---|---|
| PER | 0.00 / 0.00 | 0.92 / 0.93 | 0.92 / 0.93 | 0.92 / 0.93 |
| EMAIL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| PHONE | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| ADDRESS | 1.00 / 1.00 | 0.81 / 0.80 | 0.98 / 0.99 | 0.98 / 0.99 |
| ID_DOC | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| FIN_ID | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| DATE | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| LOC | 0.00 / 0.00 | 0.96 / 0.95 | 0.96 / 0.95 | 0.96 / 0.95 |
| ORG | 0.00 / 0.00 | 0.66 / 0.58 | 0.66 / 0.58 | 0.66 / 0.58 |
| CREDENTIAL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| NET_DIGITAL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| URL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| DOC_REF | 0.91 / 0.90 | 0.00 / 0.00 | 0.91 / 0.90 | 0.91 / 0.90 |
| **Agregado (micro)** | 0.73 / 0.63 | 0.51 / 0.41 | 0.93 / 0.92 | 0.93 / 0.92 |

## Detección por etiqueta, F1 / F2 (coincidencia parcial: solapamiento y misma etiqueta)

| Etiqueta | regex | ner | hibrido | hibrido+heuristica |
|---|---|---|---|---|
| PER | 0.00 / 0.00 | 0.95 / 0.96 | 0.95 / 0.96 | 0.95 / 0.96 |
| EMAIL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| PHONE | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| ADDRESS | 1.00 / 1.00 | 0.95 / 0.94 | 0.98 / 0.99 | 0.98 / 0.99 |
| ID_DOC | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| FIN_ID | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| DATE | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| LOC | 0.00 / 0.00 | 0.98 / 0.96 | 0.98 / 0.96 | 0.98 / 0.96 |
| ORG | 0.00 / 0.00 | 0.76 / 0.67 | 0.76 / 0.67 | 0.76 / 0.67 |
| CREDENTIAL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| NET_DIGITAL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| URL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| DOC_REF | 0.98 / 0.97 | 0.00 / 0.00 | 0.98 / 0.97 | 0.98 / 0.97 |
| **Agregado (micro)** | 0.74 / 0.64 | 0.55 / 0.44 | 0.96 / 0.94 | 0.96 / 0.94 |

## Agregado (micro, estricto)

| Sistema | P | R | F1 | F2 | F2 id. directos y secretos |
|---|---|---|---|---|---|
| regex | 0.993 | 0.580 | 0.733 | 0.633 | 0.733 |
| ner | 0.903 | 0.359 | 0.514 | 0.408 | 0.400 |
| hibrido | 0.961 | 0.908 | 0.934 | 0.918 | 0.977 |
| hibrido+heuristica | 0.961 | 0.908 | 0.934 | 0.918 | 0.977 |

## Protección (sobre el texto enviado)

| Sistema | ER_di | ER_qi | WP | Fuga residual |
|---|---|---|---|---|
| regex | 0.687 | 0.455 | 1.000 | 0.415 |
| ner | 0.366 | 0.422 | 0.996 | 0.593 |
| hibrido | 0.992 | 0.877 | 0.999 | 0.045 |
| hibrido+heuristica | 0.992 | 0.778 | 0.999 | 0.091 |

## Decisión a nivel de prompt

| Sistema | Enmascarados | Con id. directo enviados sin enmascarar | Limpios enmascarados |
|---|---|---|---|
| regex | 210/280 | 0/179 | 0/56 |
| ner | 159/280 | 45/179 | 0/56 |
| hibrido | 222/280 | 0/179 | 0/56 |
| hibrido+heuristica | 196/280 | 0/179 | 0/56 |
