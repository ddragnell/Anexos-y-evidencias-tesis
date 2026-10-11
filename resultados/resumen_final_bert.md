# Resultados finales con BERT (dccuchile/bert-base-spanish-wwm-cased + MEDDOCAN)

Validación del NER (MEDDOCAN dev, estricto): P 0,951 · R 0,959 · F1 0,955 (PER 0,963; LOC 0,983; ADDRESS 0,927; ORG 0,794).

## Detección (micro, coincidencia estricta)

| Conjunto | Sistema | P | R | F1 | F2 |
|---|---|---|---|---|---|
| Sintético test (120 prompts, 280 entidades) | Regex | 1,000 | 0,643 | 0,783 | 0,692 |
| | NER BERT | 0,913 | 0,336 | 0,491 | 0,384 |
| | Presidio | 0,656 | 0,511 | 0,574 | 0,534 |
| | **Híbrido** | **1,000** | **0,946** | **0,972** | **0,957** |
| MEDDOCAN test (250 documentos, 3912 entidades) | Regex | 0,977 | 0,210 | 0,345 | 0,249 |
| | NER BERT | 0,954 | 0,741 | 0,834 | 0,776 |
| | Presidio | 0,246 | 0,404 | 0,306 | 0,358 |
| | **Híbrido** | **0,958** | **0,948** | **0,953** | **0,950** |

## Protección (sobre el texto enviado)

| Conjunto | Sistema | ER_di | ER_qi | WP | Fuga residual |
|---|---|---|---|---|---|
| Sintético test | Presidio | 0,688 | 0,606 | 0,934 | 0,325 |
| | Híbrido | 1,000 | 0,903 | 1,000 | 0,054 |
| | Híbrido + heurística | 1,000 | 0,742 | 1,000 | 0,143 |
| MEDDOCAN test | Presidio | 0,526 | 0,627 | 0,487 | 0,410 |
| | Híbrido (= con heurística) | 0,961 | 0,955 | 0,993 | 0,032 |

## Decisión a nivel de prompt (sintético test)

| Sistema | Enmascarados | Con id. directo enviados sin enmascarar | Limpios enmascarados |
|---|---|---|---|
| Presidio | 102/120 | 0/62 | 14/28 |
| Híbrido | 87/120 | 0/62 | 0/28 |
| Híbrido + heurística | 70/120 | 0/62 | 0/28 |

## Efecto de las correcciones (inferencia por fragmentos y regla de ORG), híbrido estricto

| Conjunto | Antes F1 | Después F1 | Antes ER_di | Después ER_di |
|---|---|---|---|---|
| Sintético test | 0,950 | 0,972 | 1,000 | 1,000 |
| MEDDOCAN test | 0,847 | 0,953 | 0,794 | 0,961 |

## Errores para la discusión

- Sintético: el híbrido no tiene falsos positivos en ORG/LOC. Los 15 falsos negativos son marcas sin forma societaria (Alpina, Rappi, Avianca, Sura, Bancolombia, Claro Colombia) y barrios o municipios colombianos (El Poblado, Chapinero, Laureles, Sabaneta, Itagüí, Bello, Medellín). MEDDOCAN es clínico y de España, así que el modelo no ha visto estos nombres. El corpus de Doccano debería cerrar esa brecha.
- MEDDOCAN: PHONE da F1 0 porque las regex siguen el formato colombiano y MEDDOCAN usa números españoles (es una limitación de alcance, no un error). 
- Heurística: no enmascara ningún prompt limpio, pero deja pasar cuasi-identificadores aislados, por eso ER_qi baja de 0,903 a 0,742. Es el costo de no sobreenmascarar.

## Efecto del enmascaramiento sobre la respuesta (60 prompts enmascarados del sintético test, híbrido + heurística)

Similitud coseno con sentence-transformers/paraphrase-multilingual-mpnet-base-v2; 3 llamadas por prompt (original, original repetido, enmascarado), store=False. Ninguno de los dos modelos admite temperatura, así que se usó el valor predeterminado.

| Modelo (versión que devuelve la API, fecha UTC) | Original vs. original (piso de variación) | Original vs. enmascarado | Diferencia |
|---|---|---|---|
| GPT-5.5 Instant (`chat-latest`, 2026-10-10) | 0,963 (mediana 0,975) | 0,709 (mediana 0,744) | 0,254 |
| gpt-5-mini (`gpt-5-mini-2025-08-07`, 2026-10-10) | 0,851 (mediana 0,861) | 0,706 (mediana 0,712) | 0,145 |

Por número de marcadores en el prompt enviado:

| Modelo | 1-2 marcadores (15) | 3 o más (45) |
|---|---|---|
| GPT-5.5 Instant | 0,796 | 0,680 |
| gpt-5-mini | 0,771 | 0,684 |

- 59 de 60 respuestas al prompt enmascarado repiten los marcadores ([PER], [EMAIL]…): el modelo no inventa datos, conserva el hueco.
- La API devuelve `chat-latest` como versión, sin identificador de instantánea; por eso se registra la fecha de ejecución.
