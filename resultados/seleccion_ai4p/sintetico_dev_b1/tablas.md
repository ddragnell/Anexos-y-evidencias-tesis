# Resultados de detección: sintetico_dev_b1

Datos: `datos/sintetico/dev.jsonl` (280 prompts, 727 entidades de referencia). NER: hf modelos/ner-bert-b1

## Detección por etiqueta, F1 / F2 (coincidencia estricta: mismo span y etiqueta)

| Etiqueta | regex | ner | hibrido | hibrido+heuristica |
|---|---|---|---|---|
| PER | 0.00 / 0.00 | 0.90 / 0.93 | 0.90 / 0.93 | 0.90 / 0.93 |
| EMAIL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| PHONE | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| ADDRESS | 1.00 / 1.00 | 0.67 / 0.74 | 0.94 / 0.97 | 0.94 / 0.97 |
| ID_DOC | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| FIN_ID | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| DATE | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| LOC | 0.00 / 0.00 | 0.93 / 0.92 | 0.95 / 0.93 | 0.95 / 0.93 |
| ORG | 0.00 / 0.00 | 0.62 / 0.54 | 0.62 / 0.54 | 0.62 / 0.54 |
| CREDENTIAL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| NET_DIGITAL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| URL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| DOC_REF | 0.91 / 0.90 | 0.00 / 0.00 | 0.91 / 0.90 | 0.91 / 0.90 |
| **Agregado (micro)** | 0.73 / 0.63 | 0.49 / 0.40 | 0.92 / 0.91 | 0.92 / 0.91 |

## Detección por etiqueta, F1 / F2 (coincidencia parcial: solapamiento y misma etiqueta)

| Etiqueta | regex | ner | hibrido | hibrido+heuristica |
|---|---|---|---|---|
| PER | 0.00 / 0.00 | 0.92 / 0.95 | 0.93 / 0.95 | 0.93 / 0.95 |
| EMAIL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| PHONE | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| ADDRESS | 1.00 / 1.00 | 0.84 / 0.93 | 0.94 / 0.97 | 0.94 / 0.97 |
| ID_DOC | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| FIN_ID | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| DATE | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| LOC | 0.00 / 0.00 | 0.94 / 0.93 | 0.96 / 0.94 | 0.96 / 0.94 |
| ORG | 0.00 / 0.00 | 0.74 / 0.64 | 0.74 / 0.64 | 0.74 / 0.64 |
| CREDENTIAL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| NET_DIGITAL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| URL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| DOC_REF | 0.98 / 0.97 | 0.00 / 0.00 | 0.98 / 0.97 | 0.98 / 0.97 |
| **Agregado (micro)** | 0.74 / 0.64 | 0.53 / 0.43 | 0.95 / 0.93 | 0.95 / 0.93 |

## Agregado (micro, estricto)

| Sistema | P | R | F1 | F2 | F2 id. directos y secretos |
|---|---|---|---|---|---|
| regex | 0.993 | 0.580 | 0.733 | 0.633 | 0.733 |
| ner | 0.836 | 0.351 | 0.494 | 0.397 | 0.398 |
| hibrido | 0.948 | 0.900 | 0.923 | 0.909 | 0.975 |
| hibrido+heuristica | 0.948 | 0.900 | 0.923 | 0.909 | 0.975 |

## Protección (sobre el texto enviado)

| Sistema | ER_di | ER_qi | WP | Fuga residual |
|---|---|---|---|---|
| regex | 0.687 | 0.455 | 1.000 | 0.415 |
| ner | 0.379 | 0.419 | 0.996 | 0.578 |
| hibrido | 0.995 | 0.874 | 0.999 | 0.041 |
| hibrido+heuristica | 0.995 | 0.787 | 0.999 | 0.081 |

## Decisión a nivel de prompt

| Sistema | Enmascarados | Con id. directo enviados sin enmascarar | Limpios enmascarados |
|---|---|---|---|
| regex | 210/280 | 0/179 | 0/56 |
| ner | 160/280 | 44/179 | 0/56 |
| hibrido | 222/280 | 0/179 | 0/56 |
| hibrido+heuristica | 198/280 | 0/179 | 0/56 |
