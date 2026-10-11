# Resultados de detección: meddocan_test_bert

Datos: `datos/meddocan/test.jsonl` (250 prompts, 3912 entidades de referencia). NER: hf modelos/ner-bert

## Detección por etiqueta, F1 / F2 (coincidencia estricta: mismo span y etiqueta)

| Etiqueta | regex | ner | hibrido | presidio | hibrido+heuristica |
|---|---|---|---|---|---|
| PER | 0.00 / 0.00 | 0.97 / 0.98 | 0.97 / 0.98 | 0.19 / 0.23 | 0.97 / 0.98 |
| EMAIL | 0.99 / 0.99 | 0.00 / 0.00 | 0.99 / 0.99 | 0.99 / 0.99 | 0.99 / 0.99 |
| PHONE | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 |
| ADDRESS | 0.02 / 0.01 | 0.92 / 0.93 | 0.92 / 0.93 | 0.00 / 0.00 | 0.92 / 0.93 |
| DATE | 0.96 / 0.94 | 0.00 / 0.00 | 0.96 / 0.94 | 0.88 / 0.85 | 0.96 / 0.94 |
| LOC | 0.00 / 0.00 | 0.98 / 0.98 | 0.98 / 0.98 | 0.30 / 0.36 | 0.98 / 0.98 |
| ORG | 0.00 / 0.00 | 0.83 / 0.82 | 0.80 / 0.79 | 0.01 / 0.03 | 0.80 / 0.79 |
| **Agregado (micro)** | 0.35 / 0.25 | 0.83 / 0.78 | 0.95 / 0.95 | 0.31 / 0.36 | 0.95 / 0.95 |

## Detección por etiqueta, F1 / F2 (coincidencia parcial: solapamiento y misma etiqueta)

| Etiqueta | regex | ner | hibrido | presidio | hibrido+heuristica |
|---|---|---|---|---|---|
| PER | 0.00 / 0.00 | 0.99 / 0.99 | 0.99 / 0.99 | 0.38 / 0.45 | 0.99 / 0.99 |
| EMAIL | 0.99 / 0.99 | 0.00 / 0.00 | 0.99 / 0.99 | 0.99 / 0.99 | 0.99 / 0.99 |
| PHONE | 0.11 / 0.07 | 0.00 / 0.00 | 0.11 / 0.07 | 0.04 / 0.05 | 0.11 / 0.07 |
| ADDRESS | 0.03 / 0.02 | 0.98 / 0.99 | 0.98 / 0.99 | 0.00 / 0.00 | 0.98 / 0.99 |
| DATE | 0.96 / 0.94 | 0.00 / 0.00 | 0.96 / 0.94 | 0.89 / 0.85 | 0.96 / 0.94 |
| LOC | 0.00 / 0.00 | 0.98 / 0.98 | 0.99 / 0.98 | 0.31 / 0.37 | 0.99 / 0.98 |
| ORG | 0.00 / 0.00 | 0.91 / 0.89 | 0.91 / 0.89 | 0.04 / 0.07 | 0.91 / 0.89 |
| **Agregado (micro)** | 0.35 / 0.25 | 0.85 / 0.79 | 0.97 / 0.97 | 0.37 / 0.43 | 0.97 / 0.97 |

## Agregado (micro, estricto)

| Sistema | P | R | F1 | F2 |
|---|---|---|---|---|
| regex | 0.977 | 0.210 | 0.345 | 0.249 |
| ner | 0.954 | 0.741 | 0.834 | 0.776 |
| hibrido | 0.958 | 0.948 | 0.953 | 0.950 |
| presidio | 0.246 | 0.404 | 0.306 | 0.358 |
| hibrido+heuristica | 0.958 | 0.948 | 0.953 | 0.950 |

## Protección (sobre el texto enviado)

| Sistema | ER_di | ER_qi | WP | Fuga residual |
|---|---|---|---|---|
| regex | 0.142 | 0.267 | 0.991 | 0.787 |
| ner | 0.822 | 0.691 | 0.994 | 0.246 |
| hibrido | 0.961 | 0.955 | 0.993 | 0.032 |
| presidio | 0.526 | 0.627 | 0.487 | 0.410 |
| hibrido+heuristica | 0.961 | 0.955 | 0.993 | 0.032 |

## Decisión a nivel de prompt

| Sistema | Enmascarados | Con id. directo enviados sin enmascarar | Limpios enmascarados |
|---|---|---|---|
| regex | 250/250 | 0/250 | 0/0 |
| ner | 250/250 | 0/250 | 0/0 |
| hibrido | 250/250 | 0/250 | 0/0 |
| presidio | 250/250 | 0/250 | 0/0 |
| hibrido+heuristica | 250/250 | 0/250 | 0/0 |
