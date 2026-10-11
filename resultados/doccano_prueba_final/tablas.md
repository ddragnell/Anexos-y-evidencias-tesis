# Resultados de detección: doccano_prueba_final

Datos: `datos/doccano/prueba.jsonl` (45 prompts, 51 entidades de referencia). NER: hf modelos/ner-bert-final

## Detección por etiqueta, F1 / F2 (coincidencia estricta: mismo span y etiqueta)

| Etiqueta | regex | ner | hibrido | presidio | hibrido+heuristica |
|---|---|---|---|---|---|
| PER | 0.00 / 0.00 | 0.79 / 0.86 | 0.79 / 0.86 | 0.46 / 0.57 | 0.79 / 0.86 |
| DATE | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| LOC | 0.00 / 0.00 | 0.40 / 0.36 | 0.40 / 0.36 | 0.00 / 0.00 | 0.40 / 0.36 |
| ORG | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 |
| NET_DIGITAL | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 |
| URL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 0.88 / 0.81 | 1.00 / 1.00 |
| **Agregado (micro)** | 0.38 / 0.28 | 0.65 / 0.64 | 0.80 / 0.84 | 0.38 / 0.50 | 0.80 / 0.84 |

## Detección por etiqueta, F1 / F2 (coincidencia parcial: solapamiento y misma etiqueta)

| Etiqueta | regex | ner | hibrido | presidio | hibrido+heuristica |
|---|---|---|---|---|---|
| PER | 0.00 / 0.00 | 0.82 / 0.89 | 0.82 / 0.89 | 0.55 / 0.67 | 0.82 / 0.89 |
| DATE | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| LOC | 0.00 / 0.00 | 0.80 / 0.71 | 0.80 / 0.71 | 0.05 / 0.10 | 0.80 / 0.71 |
| ORG | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 |
| NET_DIGITAL | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 |
| URL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 0.88 / 0.81 | 1.00 / 1.00 |
| **Agregado (micro)** | 0.38 / 0.28 | 0.69 / 0.68 | 0.84 / 0.87 | 0.43 / 0.58 | 0.84 / 0.87 |

## Agregado (micro, estricto)

| Sistema | P | R | F1 | F2 | F2 id. directos y secretos |
|---|---|---|---|---|---|
| regex | 1.000 | 0.235 | 0.381 | 0.278 | 0.000 |
| ner | 0.681 | 0.627 | 0.653 | 0.637 | 0.861 |
| hibrido | 0.746 | 0.863 | 0.800 | 0.837 | 0.861 |
| presidio | 0.264 | 0.647 | 0.375 | 0.502 | 0.572 |
| hibrido+heuristica | 0.746 | 0.863 | 0.800 | 0.837 | 0.861 |

## Protección (sobre el texto enviado)

| Sistema | ER_di | ER_qi | WP | Fuga residual |
|---|---|---|---|---|
| regex | 0.000 | 0.706 | 1.000 | 0.765 |
| ner | 0.941 | 0.118 | 0.766 | 0.333 |
| hibrido | 0.941 | 0.824 | 0.904 | 0.098 |
| presidio | 0.912 | 0.941 | 0.566 | 0.176 |
| hibrido+heuristica | 0.941 | 0.647 | 0.891 | 0.157 |

## Decisión a nivel de prompt

| Sistema | Enmascarados | Con id. directo enviados sin enmascarar | Limpios enmascarados |
|---|---|---|---|
| regex | 5/45 | 11/12 | 0/27 |
| ner | 12/45 | 1/12 | 0/27 |
| hibrido | 16/45 | 1/12 | 0/27 |
| presidio | 34/45 | 0/12 | 17/27 |
| hibrido+heuristica | 13/45 | 1/12 | 0/27 |
