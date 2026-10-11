# Resultados de detección: doccano_validacion_final

Datos: `datos/doccano/validacion.jsonl` (45 prompts, 35 entidades de referencia). NER: hf modelos/ner-bert-final

## Detección por etiqueta, F1 / F2 (coincidencia estricta: mismo span y etiqueta)

| Etiqueta | regex | ner | hibrido | presidio | hibrido+heuristica |
|---|---|---|---|---|---|
| PER | 0.00 / 0.00 | 0.25 / 0.25 | 0.25 / 0.25 | 0.13 / 0.26 | 0.25 / 0.25 |
| DATE | 0.91 / 0.86 | 0.00 / 0.00 | 0.91 / 0.86 | 0.50 / 0.38 | 0.91 / 0.86 |
| LOC | 0.00 / 0.00 | 0.44 / 0.51 | 0.44 / 0.51 | 0.18 / 0.34 | 0.44 / 0.51 |
| ORG | 0.00 / 0.00 | 0.22 / 0.28 | 0.22 / 0.28 | 0.11 / 0.22 | 0.22 / 0.28 |
| NET_DIGITAL | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 |
| URL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 0.93 / 0.93 | 1.00 / 1.00 |
| **Agregado (micro)** | 0.70 / 0.60 | 0.21 / 0.19 | 0.66 / 0.69 | 0.28 / 0.45 | 0.66 / 0.69 |

## Detección por etiqueta, F1 / F2 (coincidencia parcial: solapamiento y misma etiqueta)

| Etiqueta | regex | ner | hibrido | presidio | hibrido+heuristica |
|---|---|---|---|---|---|
| PER | 0.00 / 0.00 | 0.50 / 0.50 | 0.50 / 0.50 | 0.17 / 0.34 | 0.50 / 0.50 |
| DATE | 0.91 / 0.86 | 0.00 / 0.00 | 0.91 / 0.86 | 0.50 / 0.38 | 0.91 / 0.86 |
| LOC | 0.00 / 0.00 | 0.56 / 0.64 | 0.56 / 0.64 | 0.18 / 0.34 | 0.56 / 0.64 |
| ORG | 0.00 / 0.00 | 0.44 / 0.56 | 0.44 / 0.56 | 0.11 / 0.22 | 0.44 / 0.56 |
| NET_DIGITAL | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 |
| URL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 0.93 / 0.93 | 1.00 / 1.00 |
| **Agregado (micro)** | 0.70 / 0.60 | 0.32 / 0.28 | 0.74 / 0.77 | 0.29 / 0.47 | 0.74 / 0.77 |

## Agregado (micro, estricto)

| Sistema | P | R | F1 | F2 | F2 id. directos y secretos |
|---|---|---|---|---|---|
| regex | 1.000 | 0.543 | 0.704 | 0.597 | 0.000 |
| ner | 0.273 | 0.171 | 0.211 | 0.185 | 0.238 |
| hibrido | 0.610 | 0.714 | 0.658 | 0.691 | 0.238 |
| presidio | 0.173 | 0.743 | 0.281 | 0.448 | 0.259 |
| hibrido+heuristica | 0.610 | 0.714 | 0.658 | 0.691 | 0.238 |

## Protección (sobre el texto enviado)

| Sistema | ER_di | ER_qi | WP | Fuga residual |
|---|---|---|---|---|
| regex | 0.000 | 0.613 | 1.000 | 0.457 |
| ner | 0.250 | 0.194 | 0.498 | 0.743 |
| hibrido | 0.250 | 0.806 | 0.918 | 0.171 |
| presidio | 1.000 | 0.806 | 0.528 | 0.171 |
| hibrido+heuristica | 0.250 | 0.484 | 0.882 | 0.486 |

## Decisión a nivel de prompt

| Sistema | Enmascarados | Con id. directo enviados sin enmascarar | Limpios enmascarados |
|---|---|---|---|
| regex | 5/45 | 3/3 | 0/30 |
| ner | 10/45 | 1/3 | 2/30 |
| hibrido | 14/45 | 1/3 | 2/30 |
| presidio | 36/45 | 0/3 | 21/30 |
| hibrido+heuristica | 6/45 | 1/3 | 0/30 |
