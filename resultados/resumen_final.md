# Resultados finales del modelo híbrido (ner-bert-final)

Modelo NER: BETO → AI4Privacy-es + WikiANN-es → MEDDOCAN train (B1) → Doccano entrenamiento + MEDDOCAN train (3 épocas).
Partición del corpus Doccano (exportación corregida, 300 prompts, semilla 13, 70/15/15): entrenamiento 210, validación 45, prueba 45.

| Partición | PER | LOC | ORG | DATE | URL | NET_DIGITAL | EMAIL | Total |
|---|---|---|---|---|---|---|---|---|
| Entrenamiento | 102 | 62 | 25 | 56 | 26 | 3 | 2 | 276 |
| Validación | 4 | 7 | 3 | 6 | 14 | 1 | 0 | 35 |
| Prueba | 34 | 3 | 1 | 3 | 9 | 1 | 0 | 51 |

## 1. Validación (selección; no ciega)

Reporte de validación del NER (Doccano validación + MEDDOCAN dev, estricto): micro F1 0,953 (PER 0,963; LOC 0,980; ADDRESS 0,912; ORG 0,820).

| Conjunto | Sistema | P | R | F1 | F2 | F2 id. directos y secretos | ER_di | ER_qi | Fuga |
|---|---|---|---|---|---|---|---|---|---|
| Doccano validación (35 ent.) | híbrido | 0,610 | 0,714 | 0,658 | 0,691 | 0,238 | 0,250 | 0,806 | 0,171 |
| Doccano validación | Presidio | 0,173 | 0,743 | 0,281 | 0,448 | 0,259 | 1,000 | 0,806 | 0,171 |
| Sintético dev (727 ent.) | híbrido | 0,961 | 0,908 | 0,934 | 0,918 | 0,977 | 0,992 | 0,877 | 0,045 |

La validación Doccano tiene solo 4 menciones de identificador directo (PER), así que su F2 de directos (0,238) es muy inestable.

## 2. Prueba ciega Doccano (ejecutada una sola vez, sin ajustes posteriores)

45 prompts reales, 51 entidades de referencia, 12 prompts con identificador directo.

| Sistema | P | R | F1 | F2 | F2 id. directos y secretos | ER_di | ER_qi | WP | Fuga residual | Con id. directo enviados sin enmascarar | Limpios enmascarados |
|---|---|---|---|---|---|---|---|---|---|---|---|
| regex | 1,000 | 0,235 | 0,381 | 0,278 | 0,000 | 0,000 | 0,706 | 1,000 | 0,765 | 11/12 | 0/27 |
| NER | 0,681 | 0,627 | 0,653 | 0,637 | 0,861 | 0,941 | 0,118 | 0,766 | 0,333 | 1/12 | 0/27 |
| **híbrido** | 0,746 | 0,863 | **0,800** | **0,837** | **0,861** | 0,941 | 0,824 | 0,904 | **0,098** | 1/12 | 0/27 |
| Presidio | 0,264 | 0,647 | 0,375 | 0,502 | 0,572 | 0,912 | 0,941 | 0,566 | 0,176 | 0/12 | 17/27 |
| híbrido + heurística | 0,746 | 0,863 | 0,800 | 0,837 | 0,861 | 0,941 | 0,647 | 0,891 | 0,157 | 1/12 | 0/27 |

Lectura:
- El híbrido supera a Presidio en F2 (0,837 frente a 0,502) y en F2 de identificadores directos (0,861 frente a 0,572), con menos fuga residual (0,098 frente a 0,176) y mucha mejor preservación del texto (WP 0,904 frente a 0,566).
- Presidio no deja ningún prompt con identificador directo sin enmascarar, pero enmascara 17 de 27 prompts limpios; el híbrido deja 1 de 12 (prompt 159, "Amdahl", apellido dentro de "ley de Amdahl") y no toca ningún prompt limpio.
- La heurística no cambia la detección; reduce el enmascaramiento de cuasi-identificadores (ER_qi 0,824 → 0,647) y sube la fuga a 0,157.
- Errores del híbrido (9 prompts): ORG (0/1, "Imperio Otomano"), NET_DIGITAL ("GPT-4"), límites de PER ("Francisco y"), falsos PER en "hermanito", "hijos", "3 años".
- Limitación: algunas discrepancias parecen errores u omisiones de la anotación de referencia (prompt 250, "Ivan Velez" anotado como LOC; nombres como "Alexi", "Héctor", "Juana", "María" sin anotar en 186, 9 y 299). Por el protocolo de prueba ciega la referencia no se corrigió después de ver los resultados; las cifras son conservadoras.
- La prueba tiene pocas menciones por etiqueta (LOC 3, ORG 1, DATE 3); las métricas por etiqueta tienen alta varianza y conviene reportar el agregado.

## 3. Pruebas no ciegas (8.3): comparación con el modelo B0 (BETO → MEDDOCAN)

| Conjunto | Modelo | P | R | F1 | F2 | ER_di | ER_qi | Fuga | Limpios enmascarados |
|---|---|---|---|---|---|---|---|---|---|
| Sintético test | anterior (BERT MEDDOCAN) | 1,000 | 0,946 | 0,972 | 0,957 | 1,000 | 0,903 | 0,054 | 0/28 |
| Sintético test | final | 0,964 | 0,961 | 0,962 | 0,961 | 1,000 | 0,948 | 0,029 | 7/28 |
| MEDDOCAN test | anterior | 0,958 | 0,948 | 0,953 | 0,950 | 0,961 | 0,955 | 0,032 | – |
| MEDDOCAN test | final | 0,956 | 0,945 | 0,951 | 0,947 | 0,960 | 0,952 | 0,033 | – |

- MEDDOCAN se mantiene (diferencias de 0,003): el ajuste con Doccano no degradó el dominio clínico.
- En el sintético sube el recall y baja la fuga, pero aparecen 7 prompts limpios enmascarados: todos por "Colombia" marcado como LOC, que el corpus sintético no anota en prompts limpios y el corpus Doccano sí. Es una diferencia de convención de anotación entre los dos corpus, no un error de detección en sentido estricto. Hay además 3 confusiones LOC/ORG ("Sabaneta", "Laureles", "Cundinamarca" como ORG).
- Con la heurística el sintético test queda en 0/28 limpios enmascarados y fuga 0,129.
