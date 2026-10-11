# Resultados de detección: meddocan_dev_b1

Datos: `datos/meddocan/dev.jsonl` (250 prompts, 4070 entidades de referencia). NER: hf modelos/ner-bert-b1

## Detección por etiqueta, F1 / F2 (coincidencia estricta: mismo span y etiqueta)

| Etiqueta | regex | ner | hibrido | hibrido+heuristica |
|---|---|---|---|---|
| PER | 0.00 / 0.00 | 0.97 / 0.97 | 0.97 / 0.97 | 0.97 / 0.97 |
| EMAIL | 0.99 / 0.99 | 0.00 / 0.00 | 0.99 / 0.99 | 0.99 / 0.99 |
| PHONE | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 |
| ADDRESS | 0.00 / 0.00 | 0.93 / 0.94 | 0.93 / 0.93 | 0.93 / 0.93 |
| DATE | 0.93 / 0.90 | 0.00 / 0.00 | 0.93 / 0.90 | 0.93 / 0.90 |
| LOC | 0.00 / 0.00 | 0.99 / 0.98 | 0.99 / 0.98 | 0.99 / 0.98 |
| ORG | 0.00 / 0.00 | 0.84 / 0.85 | 0.83 / 0.84 | 0.83 / 0.84 |
| **Agregado (micro)** | 0.35 / 0.26 | 0.83 / 0.76 | 0.95 / 0.95 | 0.95 / 0.95 |

## Detección por etiqueta, F1 / F2 (coincidencia parcial: solapamiento y misma etiqueta)

| Etiqueta | regex | ner | hibrido | hibrido+heuristica |
|---|---|---|---|---|
| PER | 0.00 / 0.00 | 0.99 / 0.99 | 0.99 / 0.99 | 0.99 / 0.99 |
| EMAIL | 0.99 / 0.99 | 0.00 / 0.00 | 0.99 / 0.99 | 0.99 / 0.99 |
| PHONE | 0.12 / 0.08 | 0.00 / 0.00 | 0.12 / 0.08 | 0.12 / 0.08 |
| ADDRESS | 0.00 / 0.00 | 0.99 / 0.99 | 0.99 / 0.99 | 0.99 / 0.99 |
| DATE | 0.93 / 0.90 | 0.00 / 0.00 | 0.93 / 0.90 | 0.93 / 0.90 |
| LOC | 0.00 / 0.00 | 0.99 / 0.99 | 0.99 / 0.99 | 0.99 / 0.99 |
| ORG | 0.00 / 0.00 | 0.92 / 0.93 | 0.92 / 0.93 | 0.92 / 0.93 |
| **Agregado (micro)** | 0.35 / 0.26 | 0.85 / 0.78 | 0.97 / 0.97 | 0.97 / 0.97 |

## Agregado (micro, estricto)

| Sistema | P | R | F1 | F2 | F2 id. directos y secretos |
|---|---|---|---|---|---|
| regex | 0.979 | 0.215 | 0.353 | 0.255 | 0.160 |
| ner | 0.959 | 0.728 | 0.828 | 0.765 | 0.841 |
| hibrido | 0.963 | 0.943 | 0.953 | 0.947 | 0.950 |
| hibrido+heuristica | 0.963 | 0.943 | 0.953 | 0.947 | 0.950 |

## Protección (sobre el texto enviado)

| Sistema | ER_di | ER_qi | WP | Fuga residual |
|---|---|---|---|---|
| regex | 0.133 | 0.281 | 0.992 | 0.783 |
| ner | 0.826 | 0.669 | 0.991 | 0.256 |
| hibrido | 0.959 | 0.949 | 0.991 | 0.037 |
| hibrido+heuristica | 0.959 | 0.949 | 0.991 | 0.037 |

## Decisión a nivel de prompt

| Sistema | Enmascarados | Con id. directo enviados sin enmascarar | Limpios enmascarados |
|---|---|---|---|
| regex | 250/250 | 0/250 | 0/0 |
| ner | 250/250 | 0/250 | 0/0 |
| hibrido | 250/250 | 0/250 | 0/0 |
| hibrido+heuristica | 250/250 | 0/250 | 0/0 |
