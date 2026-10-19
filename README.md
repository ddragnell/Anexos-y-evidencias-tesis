# Mecanismo preventivo de información sensible en prompts para IA generativa

Trabajo de grado de Andrés Saldarriaga. Este repositorio contiene el mecanismo híbrido que detecta información personal y secretos técnicos en un prompt antes de enviarlo a una IA generativa (regex con validadores + NER BERT + heurística de riesgo), el proxy que lo aplica, los scripts de entrenamiento y evaluación, y los resultados reportados en el documento.

![Página de demostración del proxy](proxy/captura_demo.png)

## Resultados principales

Prueba ciega sobre 45 prompts de erfanzar/GPT-4-Prompts anotados en Doccano (ejecutada una sola vez):

| Sistema | F1 | F2 | F2 id. directos y secretos | Fuga residual | Prompts limpios enmascarados |
|---|---|---|---|---|---|
| **Híbrido (este trabajo)** | **0,800** | **0,837** | **0,861** | 0,098 | **0/27** |
| Presidio (línea base, es_core_news_lg) | 0,503 | 0,633 | 0,714 | **0,059** | 12/27 |

- Presidio deja menos fuga en la prueba ciega porque enmascara mucho más texto (WP 0,624 frente a 0,904 del híbrido) y 12 de los 27 prompts limpios.
- MEDDOCAN test: F2 0,947 (Presidio 0,497). Corpus sintético test, que verifica la implementación: F2 0,967 (Presidio 0,616).
- Acuerdo entre anotadores (50 textos, segundo anotador: un compañero): kappa de Cohen por token 0,919; F1 por mención 0,835.
- Sesgo de pre-anotación (`scripts/sesgo_preanotacion.py`): la pre-anotación coincide más con la referencia del autor (F1 0,529) que con la del segundo anotador (0,427), pero el híbrido obtiene resultados parecidos frente a las dos (0,938 y 0,933 en los 7 prompts de prueba de la muestra).
- Proxy de extremo a extremo con el modelo final: 165/165 prompts enviados exactamente con el texto evaluado; latencia mediana 15,9 ms (p95 28,4 ms) en Colab con GPU T4.
- Prueba de no persistencia del proxy (`scripts/prueba_no_persistencia.py`): 165 prompts sin ninguna escritura de archivos ni registros, y todas las llamadas con `store=False`.
- Análisis de sensibilidad del umbral de la heurística en el sintético de desarrollo (`scripts/sensibilidad_umbral.py`): los umbrales 0,6 y 0,7 dan las mismas decisiones.

Detalle en [`resultados/resumen_final.md`](resultados/resumen_final.md).

## Estructura

| Carpeta | Contenido |
|---|---|
| `docs/` | Matriz de revisión de literatura (Anexos A y B de la tesis) |
| `mecanismo/` | Taxonomía de 13 etiquetas, detector regex, detector NER, fusión, heurística, enmascaramiento, métricas y línea base Presidio |
| `proxy/` | Proxy FastAPI (`servidor.py`) y página de demostración (`demo.html`) |
| `scripts/` | Generación del corpus sintético, conversión de MEDDOCAN, AI4Privacy y WikiANN, preparación y partición del corpus de Doccano, entrenamiento del NER, evaluación de detección y de respuestas, acuerdo entre anotadores y prueba del proxy |
| `colab/` | Notebooks de Google Colab con los que se entrenó y evaluó (GPU T4) |
| `datos/` | Corpus sintético (`dev` y `test`). Los demás datos no se incluyen; ver [`datos/README.md`](datos/README.md) |
| `modelos/` | Reportes de validación. Los pesos no se incluyen; ver [`modelos/README.md`](modelos/README.md) |
| `resultados/` | Métricas (`metricas.json`) y tablas (`tablas.md`) de cada evaluación |
| `docs/guia_tecnica.md` | Guía técnica detallada: decisiones de diseño y comandos de cada paso |

## Cadena de entrenamiento del NER final

BETO (`dccuchile/bert-base-spanish-wwm-cased`) → AI4Privacy (español) + WikiANN (español) → MEDDOCAN train → corpus de Doccano (entrenamiento) + MEDDOCAN train. La selección se hizo solo con conjuntos de validación; la partición de prueba de Doccano se usó una única vez.

## Probar el proxy

1. Descarga el modelo final (ver [`modelos/README.md`](modelos/README.md)) en `modelos/ner-bert-final/`.
2. En Windows, doble clic en `iniciar_demo.bat`. En otro sistema:
   ```
   pip install torch transformers fastapi uvicorn openai
   uvicorn proxy.servidor:app --port 8000
   ```
3. Abre `http://localhost:8000/`. La API está en `POST /v1/prompt` con `{"prompt": "...", "enviar": false}`.

Enviar el texto enmascarado a la IA es opcional y requiere `OPENAI_API_KEY`. El proxy no guarda prompts, entidades ni respuestas, y llama a OpenAI con `store=False`.

## Limitaciones conocidas

- Nombres sueltos en minúscula (por ejemplo "soy andrés") pueden no detectarse: el modelo distingue mayúsculas.
- ORG es la etiqueta con menor desempeño y menor acuerdo entre anotadores.
- La prueba ciega tiene pocas menciones por etiqueta; conviene leer el agregado.
