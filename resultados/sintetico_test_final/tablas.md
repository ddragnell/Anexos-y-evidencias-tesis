# Resultados de detección: sintetico_test_final

Datos: `datos/sintetico/test.jsonl` (120 prompts, 287 entidades de referencia). Detecciones de regex, NER e híbrido tomadas de `resultados/sintetico_test_final` (versión anterior); Presidio con es_core_news_lg.

## Detección por etiqueta, F1 / F2 (coincidencia estricta: mismo span y etiqueta)

| Etiqueta | regex | ner | hibrido | presidio | hibrido+heuristica |
|---|---|---|---|---|---|
| PER | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 | 0.94 / 0.96 | 1.00 / 1.00 |
| EMAIL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| PHONE | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 0.48 / 0.70 | 1.00 / 1.00 |
| ADDRESS | 1.00 / 1.00 | 0.77 / 0.76 | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 |
| ID_DOC | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 |
| FIN_ID | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 0.93 / 0.90 | 1.00 / 1.00 |
| DATE | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 0.69 / 0.58 | 1.00 / 1.00 |
| LOC | 0.00 / 0.00 | 0.93 / 0.89 | 0.93 / 0.89 | 0.70 / 0.82 | 0.93 / 0.89 |
| ORG | 0.00 / 0.00 | 0.69 / 0.65 | 0.69 / 0.65 | 0.69 / 0.69 | 0.69 / 0.65 |
| CREDENTIAL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 |
| NET_DIGITAL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 0.88 / 0.95 | 1.00 / 1.00 |
| URL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 0.48 / 0.38 | 1.00 / 1.00 |
| DOC_REF | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 |
| **Agregado (micro)** | 0.77 / 0.68 | 0.54 / 0.43 | 0.98 / 0.97 | 0.66 / 0.62 | 0.98 / 0.97 |

## Detección por etiqueta, F1 / F2 (coincidencia parcial: solapamiento y misma etiqueta)

| Etiqueta | regex | ner | hibrido | presidio | hibrido+heuristica |
|---|---|---|---|---|---|
| PER | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 | 0.94 / 0.96 | 1.00 / 1.00 |
| EMAIL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| PHONE | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 0.48 / 0.70 | 1.00 / 1.00 |
| ADDRESS | 1.00 / 1.00 | 0.90 / 0.89 | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 |
| ID_DOC | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 |
| FIN_ID | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 0.93 / 0.90 | 1.00 / 1.00 |
| DATE | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 0.69 / 0.58 | 1.00 / 1.00 |
| LOC | 0.00 / 0.00 | 0.93 / 0.89 | 0.93 / 0.89 | 0.70 / 0.82 | 0.93 / 0.89 |
| ORG | 0.00 / 0.00 | 0.69 / 0.65 | 0.69 / 0.65 | 0.69 / 0.69 | 0.69 / 0.65 |
| CREDENTIAL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 |
| NET_DIGITAL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 0.88 / 0.95 | 1.00 / 1.00 |
| URL | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 0.57 / 0.45 | 1.00 / 1.00 |
| DOC_REF | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 | 0.00 / 0.00 | 1.00 / 1.00 |
| **Agregado (micro)** | 0.77 / 0.68 | 0.55 / 0.44 | 0.98 / 0.97 | 0.66 / 0.62 | 0.98 / 0.97 |

## Agregado (micro, estricto)

| Sistema | P | R | F1 | F2 | F2 id. directos y secretos |
|---|---|---|---|---|---|
| regex | 1.000 | 0.627 | 0.771 | 0.678 | 0.622 |
| ner | 0.947 | 0.376 | 0.539 | 0.428 | 0.580 |
| hibrido | 0.989 | 0.962 | 0.975 | 0.967 | 1.000 |
| presidio | 0.736 | 0.592 | 0.656 | 0.616 | 0.634 |
| hibrido+heuristica | 0.989 | 0.962 | 0.975 | 0.967 | 1.000 |

## Protección (sobre el texto enviado)

| Sistema | ER_di | ER_qi | WP | Fuga residual |
|---|---|---|---|---|
| regex | 0.568 | 0.673 | 1.000 | 0.373 |
| ner | 0.528 | 0.278 | 1.000 | 0.606 |
| hibrido | 1.000 | 0.951 | 1.000 | 0.028 |
| presidio | 0.704 | 0.704 | 0.987 | 0.226 |
| hibrido+heuristica | 1.000 | 0.735 | 1.000 | 0.150 |

## Decisión a nivel de prompt

| Sistema | Enmascarados | Con id. directo enviados sin enmascarar | Limpios enmascarados |
|---|---|---|---|
| regex | 77/120 | 8/62 | 0/21 |
| ner | 71/120 | 3/62 | 0/21 |
| hibrido | 97/120 | 0/62 | 0/21 |
| presidio | 104/120 | 0/62 | 7/21 |
| hibrido+heuristica | 70/120 | 0/62 | 0/21 |
