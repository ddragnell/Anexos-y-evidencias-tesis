# Resultados de detección: meddocan_test

Datos: `/tmp/claude-0/meddocan_jsonl/test.jsonl` (250 prompts, 3912 entidades de referencia). NER: spacy 

## Detección por etiqueta, F1 / F2 (coincidencia estricta: mismo span y etiqueta)

| Etiqueta | regex | ner | hibrido | presidio | hibrido+heuristica |
|---|---|---|---|---|---|
| PER | 0.00 / 0.00 | 0.26 / 0.28 | 0.26 / 0.28 | 0.22 / 0.26 | 0.26 / 0.28 |
| EMAIL | 0.99 / 0.99 | 0.00 / 0.00 | 0.99 / 0.99 | 0.99 / 0.99 | 0.99 / 0.99 |
| PHONE | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 |
| ADDRESS | 0.02 / 0.01 | 0.00 / 0.00 | 0.02 / 0.01 | 0.00 / 0.00 | 0.02 / 0.01 |
| DATE | 0.96 / 0.94 | 0.00 / 0.00 | 0.96 / 0.94 | 0.88 / 0.85 | 0.96 / 0.94 |
| LOC | 0.00 / 0.00 | 0.31 / 0.36 | 0.31 / 0.36 | 0.28 / 0.35 | 0.31 / 0.36 |
| ORG | 0.00 / 0.00 | 0.03 / 0.05 | 0.03 / 0.05 | 0.02 / 0.03 | 0.03 / 0.05 |
| **Agregado (micro)** | 0.35 / 0.25 | 0.20 / 0.21 | 0.36 / 0.40 | 0.30 / 0.36 | 0.36 / 0.40 |

## Detección por etiqueta, F1 / F2 (coincidencia parcial: solapamiento y misma etiqueta)

| Etiqueta | regex | ner | hibrido | presidio | hibrido+heuristica |
|---|---|---|---|---|---|
| PER | 0.00 / 0.00 | 0.44 / 0.48 | 0.44 / 0.48 | 0.38 / 0.45 | 0.44 / 0.48 |
| EMAIL | 0.99 / 0.99 | 0.00 / 0.00 | 0.99 / 0.99 | 0.99 / 0.99 | 0.99 / 0.99 |
| PHONE | 0.11 / 0.07 | 0.00 / 0.00 | 0.11 / 0.07 | 0.04 / 0.05 | 0.11 / 0.07 |
| ADDRESS | 0.03 / 0.02 | 0.00 / 0.00 | 0.03 / 0.02 | 0.00 / 0.00 | 0.03 / 0.02 |
| DATE | 0.96 / 0.94 | 0.00 / 0.00 | 0.96 / 0.94 | 0.89 / 0.85 | 0.96 / 0.94 |
| LOC | 0.00 / 0.00 | 0.32 / 0.37 | 0.32 / 0.37 | 0.29 / 0.36 | 0.32 / 0.37 |
| ORG | 0.00 / 0.00 | 0.05 / 0.08 | 0.05 / 0.08 | 0.03 / 0.06 | 0.05 / 0.08 |
| **Agregado (micro)** | 0.35 / 0.25 | 0.26 / 0.28 | 0.41 / 0.46 | 0.35 / 0.42 | 0.41 / 0.46 |

## Agregado (micro, estricto)

| Sistema | P | R | F1 | F2 |
|---|---|---|---|---|
| regex | 0.977 | 0.210 | 0.345 | 0.249 |
| ner | 0.182 | 0.224 | 0.201 | 0.214 |
| hibrido | 0.300 | 0.434 | 0.355 | 0.399 |
| presidio | 0.239 | 0.418 | 0.304 | 0.363 |
| hibrido+heuristica | 0.300 | 0.434 | 0.355 | 0.399 |

## Protección (sobre el texto enviado)

| Sistema | ER_di | ER_qi | WP | Fuga residual |
|---|---|---|---|---|
| regex | 0.142 | 0.267 | 0.991 | 0.787 |
| ner | 0.392 | 0.351 | 0.489 | 0.609 |
| hibrido | 0.528 | 0.616 | 0.586 | 0.396 |
| presidio | 0.528 | 0.594 | 0.494 | 0.408 |
| hibrido+heuristica | 0.528 | 0.616 | 0.586 | 0.396 |

## Decisión a nivel de prompt

| Sistema | Enmascarados | Con id. directo enviados sin enmascarar | Limpios enmascarados |
|---|---|---|---|
| regex | 250/250 | 0/250 | 0/0 |
| ner | 250/250 | 0/250 | 0/0 |
| hibrido | 250/250 | 0/250 | 0/0 |
| presidio | 250/250 | 0/250 | 0/0 |
| hibrido+heuristica | 250/250 | 0/250 | 0/0 |
