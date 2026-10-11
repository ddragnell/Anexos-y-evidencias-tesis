# Resultados de detección: meddocan_test_nerentrenado

Datos: `datos/meddocan/test.jsonl` (250 prompts, 3912 entidades de referencia). NER: spacy modelos/ner-spacy-meddocan

## Detección por etiqueta, F1 / F2 (coincidencia estricta: mismo span y etiqueta)

| Etiqueta | regex | ner | hibrido | presidio | hibrido+heuristica |
|---|---|---|---|---|---|
| PER | 0.00 / 0.00 | 0.94 / 0.92 | 0.94 / 0.93 | 0.22 / 0.26 | 0.94 / 0.93 |
| EMAIL | 0.99 / 0.99 | 0.00 / 0.00 | 0.99 / 0.99 | 0.99 / 0.99 | 0.99 / 0.99 |
| PHONE | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 |
| ADDRESS | 0.02 / 0.01 | 0.55 / 0.54 | 0.55 / 0.54 | 0.00 / 0.00 | 0.55 / 0.54 |
| DATE | 0.96 / 0.94 | 0.00 / 0.00 | 0.96 / 0.94 | 0.88 / 0.85 | 0.96 / 0.94 |
| LOC | 0.00 / 0.00 | 0.77 / 0.69 | 0.77 / 0.69 | 0.28 / 0.35 | 0.77 / 0.69 |
| ORG | 0.00 / 0.00 | 0.77 / 0.73 | 0.75 / 0.71 | 0.02 / 0.03 | 0.75 / 0.71 |
| **Agregado (micro)** | 0.35 / 0.25 | 0.69 / 0.61 | 0.84 / 0.80 | 0.30 / 0.36 | 0.84 / 0.80 |

## Detección por etiqueta, F1 / F2 (coincidencia parcial: solapamiento y misma etiqueta)

| Etiqueta | regex | ner | hibrido | presidio | hibrido+heuristica |
|---|---|---|---|---|---|
| PER | 0.00 / 0.00 | 0.96 / 0.94 | 0.96 / 0.94 | 0.38 / 0.45 | 0.96 / 0.94 |
| EMAIL | 0.99 / 0.99 | 0.00 / 0.00 | 0.99 / 0.99 | 0.99 / 0.99 | 0.99 / 0.99 |
| PHONE | 0.11 / 0.07 | 0.00 / 0.00 | 0.11 / 0.07 | 0.04 / 0.05 | 0.11 / 0.07 |
| ADDRESS | 0.03 / 0.02 | 0.96 / 0.95 | 0.96 / 0.95 | 0.00 / 0.00 | 0.96 / 0.95 |
| DATE | 0.96 / 0.94 | 0.00 / 0.00 | 0.96 / 0.94 | 0.89 / 0.85 | 0.96 / 0.94 |
| LOC | 0.00 / 0.00 | 0.79 / 0.71 | 0.79 / 0.71 | 0.29 / 0.36 | 0.79 / 0.71 |
| ORG | 0.00 / 0.00 | 0.87 / 0.83 | 0.87 / 0.83 | 0.03 / 0.06 | 0.87 / 0.83 |
| **Agregado (micro)** | 0.35 / 0.25 | 0.76 / 0.67 | 0.90 / 0.86 | 0.35 / 0.42 | 0.90 / 0.86 |

## Agregado (micro, estricto)

| Sistema | P | R | F1 | F2 |
|---|---|---|---|---|
| regex | 0.977 | 0.210 | 0.345 | 0.249 |
| ner | 0.892 | 0.564 | 0.691 | 0.608 |
| hibrido | 0.913 | 0.771 | 0.836 | 0.796 |
| presidio | 0.239 | 0.418 | 0.304 | 0.363 |
| hibrido+heuristica | 0.913 | 0.771 | 0.836 | 0.796 |

## Protección (sobre el texto enviado)

| Sistema | ER_di | ER_qi | WP | Fuga residual |
|---|---|---|---|---|
| regex | 0.142 | 0.267 | 0.991 | 0.787 |
| ner | 0.784 | 0.500 | 0.978 | 0.376 |
| hibrido | 0.923 | 0.764 | 0.982 | 0.162 |
| presidio | 0.528 | 0.594 | 0.494 | 0.408 |
| hibrido+heuristica | 0.923 | 0.764 | 0.982 | 0.162 |

## Decisión a nivel de prompt

| Sistema | Enmascarados | Con id. directo enviados sin enmascarar | Limpios enmascarados |
|---|---|---|---|
| regex | 250/250 | 0/250 | 0/0 |
| ner | 250/250 | 0/250 | 0/0 |
| hibrido | 250/250 | 0/250 | 0/0 |
| presidio | 250/250 | 0/250 | 0/0 |
| hibrido+heuristica | 250/250 | 0/250 | 0/0 |
