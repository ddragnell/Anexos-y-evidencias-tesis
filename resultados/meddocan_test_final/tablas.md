# Resultados de detección: meddocan_test_final

Datos: `datos/meddocan/test.jsonl (no incluido)` (250 prompts, 3912 entidades de referencia). Detecciones de regex, NER e híbrido tomadas de `resultados/meddocan_test_final` (versión anterior); Presidio con es_core_news_lg.

## Detección por etiqueta, F1 / F2 (coincidencia estricta: mismo span y etiqueta)

| Etiqueta | regex | ner | hibrido | presidio | hibrido+heuristica |
|---|---|---|---|---|---|
| PER | 0.00 / 0.00 | 0.97 / 0.98 | 0.97 / 0.98 | 0.45 / 0.48 | 0.97 / 0.98 |
| EMAIL | 0.99 / 0.99 | 0.00 / 0.00 | 0.99 / 0.99 | 0.99 / 0.99 | 0.99 / 0.99 |
| PHONE | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 |
| ADDRESS | 0.02 / 0.01 | 0.92 / 0.93 | 0.92 / 0.93 | 0.00 / 0.00 | 0.92 / 0.93 |
| DATE | 0.96 / 0.94 | 0.00 / 0.00 | 0.96 / 0.94 | 0.89 / 0.85 | 0.96 / 0.94 |
| LOC | 0.00 / 0.00 | 0.98 / 0.98 | 0.98 / 0.98 | 0.43 / 0.53 | 0.98 / 0.98 |
| ORG | 0.00 / 0.00 | 0.76 / 0.75 | 0.73 / 0.72 | 0.04 / 0.06 | 0.73 / 0.72 |
| **Agregado (micro)** | 0.35 / 0.25 | 0.83 / 0.77 | 0.95 / 0.95 | 0.43 / 0.50 | 0.95 / 0.95 |

## Detección por etiqueta, F1 / F2 (coincidencia parcial: solapamiento y misma etiqueta)

| Etiqueta | regex | ner | hibrido | presidio | hibrido+heuristica |
|---|---|---|---|---|---|
| PER | 0.00 / 0.00 | 0.99 / 0.99 | 0.99 / 0.99 | 0.78 / 0.82 | 0.99 / 0.99 |
| EMAIL | 0.99 / 0.99 | 0.00 / 0.00 | 0.99 / 0.99 | 0.99 / 0.99 | 0.99 / 0.99 |
| PHONE | 0.11 / 0.07 | 0.00 / 0.00 | 0.11 / 0.07 | 0.00 / 0.00 | 0.11 / 0.07 |
| ADDRESS | 0.03 / 0.02 | 0.98 / 0.98 | 0.97 / 0.98 | 0.00 / 0.00 | 0.97 / 0.98 |
| DATE | 0.96 / 0.94 | 0.00 / 0.00 | 0.96 / 0.94 | 0.89 / 0.85 | 0.96 / 0.94 |
| LOC | 0.00 / 0.00 | 0.99 / 0.99 | 0.99 / 0.99 | 0.44 / 0.55 | 0.99 / 0.99 |
| ORG | 0.00 / 0.00 | 0.89 / 0.88 | 0.89 / 0.88 | 0.07 / 0.13 | 0.89 / 0.88 |
| **Agregado (micro)** | 0.35 / 0.25 | 0.85 / 0.79 | 0.97 / 0.97 | 0.52 / 0.60 | 0.97 / 0.97 |

## Agregado (micro, estricto)

| Sistema | P | R | F1 | F2 | F2 id. directos y secretos |
|---|---|---|---|---|---|
| regex | 0.977 | 0.210 | 0.345 | 0.249 | 0.170 |
| ner | 0.952 | 0.738 | 0.831 | 0.773 | 0.837 |
| hibrido | 0.956 | 0.945 | 0.951 | 0.947 | 0.952 |
| presidio | 0.359 | 0.549 | 0.434 | 0.497 | 0.450 |
| hibrido+heuristica | 0.956 | 0.945 | 0.951 | 0.947 | 0.952 |

## Protección (sobre el texto enviado)

| Sistema | ER_di | ER_qi | WP | Fuga residual |
|---|---|---|---|---|
| regex | 0.142 | 0.267 | 0.991 | 0.787 |
| ner | 0.821 | 0.687 | 0.993 | 0.247 |
| hibrido | 0.960 | 0.952 | 0.993 | 0.033 |
| presidio | 0.687 | 0.731 | 0.579 | 0.206 |
| hibrido+heuristica | 0.960 | 0.952 | 0.993 | 0.033 |

## Decisión a nivel de prompt

| Sistema | Enmascarados | Con id. directo enviados sin enmascarar | Limpios enmascarados |
|---|---|---|---|
| regex | 250/250 | 0/250 | 0/0 |
| ner | 250/250 | 0/250 | 0/0 |
| hibrido | 250/250 | 0/250 | 0/0 |
| presidio | 250/250 | 0/250 | 0/0 |
| hibrido+heuristica | 250/250 | 0/250 | 0/0 |
