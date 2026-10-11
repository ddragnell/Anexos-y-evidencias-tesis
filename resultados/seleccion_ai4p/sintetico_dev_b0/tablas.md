# Resultados de detección: sintetico_dev_b0

Datos: `datos/sintetico/dev.jsonl` (280 prompts, 727 entidades de referencia). NER: hf modelos/ner-bert-b0

## Detección por etiqueta, F1 / F2 (coincidencia estricta: mismo span y etiqueta)

| Etiqueta | regex | ner | hibrido | hibrido+heuristica |
|---|---|---|---|---|
| PER | 0.00 / 0.00 | 0.93 / 0.93 | 0.94 / 0.94 | 0.94 / 0.94 |
| EMAIL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| PHONE | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| ADDRESS | 1.00 / 1.00 | 0.57 / 0.56 | 0.98 / 0.99 | 0.98 / 0.99 |
| ID_DOC | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| FIN_ID | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| DATE | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| LOC | 0.00 / 0.00 | 0.83 / 0.81 | 0.87 / 0.82 | 0.87 / 0.82 |
| ORG | 0.00 / 0.00 | 0.52 / 0.44 | 0.52 / 0.44 | 0.52 / 0.44 |
| CREDENTIAL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| NET_DIGITAL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| URL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| DOC_REF | 0.91 / 0.90 | 0.00 / 0.00 | 0.91 / 0.90 | 0.91 / 0.90 |
| **Agregado (micro)** | 0.73 / 0.63 | 0.46 / 0.36 | 0.91 / 0.89 | 0.91 / 0.89 |

## Detección por etiqueta, F1 / F2 (coincidencia parcial: solapamiento y misma etiqueta)

| Etiqueta | regex | ner | hibrido | hibrido+heuristica |
|---|---|---|---|---|
| PER | 0.00 / 0.00 | 0.96 / 0.97 | 0.97 / 0.97 | 0.97 / 0.97 |
| EMAIL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| PHONE | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| ADDRESS | 1.00 / 1.00 | 0.93 / 0.91 | 0.98 / 0.99 | 0.98 / 0.99 |
| ID_DOC | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| FIN_ID | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| DATE | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| LOC | 0.00 / 0.00 | 0.85 / 0.82 | 0.89 / 0.84 | 0.89 / 0.84 |
| ORG | 0.00 / 0.00 | 0.71 / 0.60 | 0.71 / 0.60 | 0.71 / 0.60 |
| CREDENTIAL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| NET_DIGITAL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| URL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| DOC_REF | 0.98 / 0.97 | 0.00 / 0.00 | 0.98 / 0.97 | 0.98 / 0.97 |
| **Agregado (micro)** | 0.74 / 0.64 | 0.52 / 0.41 | 0.95 / 0.92 | 0.95 / 0.92 |

## Agregado (micro, estricto)

| Sistema | P | R | F1 | F2 | F2 id. directos y secretos |
|---|---|---|---|---|---|
| regex | 0.993 | 0.580 | 0.733 | 0.633 | 0.733 |
| ner | 0.836 | 0.315 | 0.458 | 0.360 | 0.380 |
| hibrido | 0.955 | 0.873 | 0.912 | 0.889 | 0.980 |
| hibrido+heuristica | 0.955 | 0.873 | 0.912 | 0.889 | 0.980 |

## Protección (sobre el texto enviado)

| Sistema | ER_di | ER_qi | WP | Fuga residual |
|---|---|---|---|---|
| regex | 0.687 | 0.455 | 1.000 | 0.415 |
| ner | 0.354 | 0.326 | 0.991 | 0.618 |
| hibrido | 0.995 | 0.781 | 0.997 | 0.077 |
| hibrido+heuristica | 0.995 | 0.698 | 0.997 | 0.117 |

## Decisión a nivel de prompt

| Sistema | Enmascarados | Con id. directo enviados sin enmascarar | Limpios enmascarados |
|---|---|---|---|
| regex | 210/280 | 0/179 | 0/56 |
| ner | 148/280 | 47/179 | 0/56 |
| hibrido | 219/280 | 0/179 | 0/56 |
| hibrido+heuristica | 195/280 | 0/179 | 0/56 |
