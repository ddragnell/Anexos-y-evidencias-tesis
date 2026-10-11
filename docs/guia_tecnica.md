> Guía técnica del desarrollo. Algunas rutas que menciona (`datos/doccano`, `datos/meddocan`, `datos/acuerdo`, `modelos/ner-spacy-meddocan` y los pesos de `modelos/`) no se incluyen en el repositorio; ver `datos/README.md` y `modelos/README.md`. En el repositorio, la demostración se corre desde la raíz con `iniciar_demo.bat`.

# Mecanismo preventivo híbrido (NER + regex + heurística) y proxy

Código del objetivo específico 3 y evaluación del objetivo 4 del trabajo de grado.
Sigue la taxonomía final de la Tabla 6 (13 etiquetas, sin atributos sensibles semánticos)
y la correspondencia de mecanismos de la Tabla 3.

## Estructura

| Ruta | Qué hace |
|---|---|
| `mecanismo/taxonomia.py` | Las 13 etiquetas, su macrogrupo, si son directas (ER_di) o cuasi (ER_qi) y qué detector responde por cada una |
| `mecanismo/regex_detector.py` | Regex + validadores: EMAIL, PHONE, ADDRESS, ID_DOC (CC, CE, NIT con dígito de verificación, pasaporte), FIN_ID (tarjeta con Luhn, IBAN, cuentas con contexto), DATE, CREDENTIAL (prefijos conocidos, palabra clave + valor, alta entropía), NET_DIGITAL (IPv4/IPv6/MAC validadas), URL, DOC_REF |
| `mecanismo/ner_detector.py` | NER con dos backends: `hf` (BERT ajustado, el del trabajo) y `spacy` (es_core_news_sm, respaldo). Normaliza etiquetas de MEDDOCAN a la taxonomía |
| `mecanismo/fusion.py` | Consolidación de solapamientos: regex tiene precedencia en patrones estructurados y el span NER que la solapa se recorta (resuelve el caso del NIT de la sección 8.3) |
| `mecanismo/heuristica.py` | Heurística de decisión: pesos por criticidad, precedencia (CREDENTIAL, ID_DOC, FIN_ID siempre enmascaran), coocurrencia de dos o más cuasi-identificadores distintos (+0,3), umbral 0,6 |
| `mecanismo/mecanismo.py` | Une todo: detectar, decidir y enmascarar con marcadores tipados (`[PER]`, `[ID_DOC]`...). No guarda el mapeo: no hay restitución |
| `mecanismo/presidio_baseline.py` | Línea base: Presidio tal como viene para español (sin reconocedores propios) |
| `mecanismo/metricas.py` | P, R, F1, F2 por etiqueta y micro; ER_di, ER_qi, WP y fuga residual |
| `proxy/servidor.py` | Proxy FastAPI: recibe el prompt, aplica el mecanismo y reenvía a gpt-5-mini con `store=False`. Sin persistencia ni logs de contenido |
| `scripts/generar_corpus_sintetico.py` | Corpus sintético controlado, anotado por construcción, en formato de exportación de Doccano |
| `scripts/evaluar_deteccion.py` | Compara regex, NER, híbrido, híbrido + heurística y Presidio sobre cualquier JSONL de Doccano |
| `scripts/entrenar_ner.py` | Ajuste de BERT (token classification BIO) con el export de Doccano |
| `scripts/evaluar_respuestas.py` | Similitud coseno entre respuestas al prompt original y al enmascarado, con piso de no determinismo |
| `datos/sintetico/` | `dev.jsonl` (280) para análisis de errores y `test.jsonl` (120) para reportar; plantillas disjuntas |
| `resultados/` | Métricas (`metricas.json`), tablas para el documento (`tablas.md`) y salidas por sistema |

## Correr en tu computador (Windows)

```
cd modelo-ner
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download es_core_news_sm
```

1. **Evaluación de detección** (ya corrida aquí con el NER de spaCy):
   `python scripts/evaluar_deteccion.py --datos datos/sintetico/test.jsonl --nombre sintetico_test`
2. **Particionar y entrenar el NER BERT**. Primero `python scripts/particionar_doccano.py --datos ruta\doccano.jsonl` (70/15/15, semilla fija; `prueba.jsonl` queda aislado). Luego entrenar con el export de Doccano (Doccano > Dataset > Export > JSONL)
   y el dev sintético:
   `python scripts/entrenar_ner.py --datos datos/doccano/entrenamiento.jsonl datos/sintetico/dev.jsonl --val datos/doccano/validacion.jsonl --base dccuchile/bert-base-spanish-wwm-cased --salida modelos/ner-bert`
   Si tienes el checkpoint ajustado con MEDDOCAN, pásalo en `--base` (su cabeza de etiquetas se reinicia).
   Para usar el checkpoint de MEDDOCAN sin reentrenar: `--ner-backend hf --ner-modelo ruta\checkpoint`
   (sus etiquetas, como NOMBRE_SUJETO_ASISTENCIA o CALLE, se traducen solas).
2b. **Si aún no tienes corpus anotado**: `python scripts/preparar_doccano.py --entrada ruta\prompts_es.jsonl --n 300` filtra por relevancia, deduplica, toma una muestra estratificada y la pre-anota para importarla en Doccano (revisar cada anotación).
3. **Re-evaluar con BERT**:
   `python scripts/evaluar_deteccion.py --datos datos/sintetico/test.jsonl --nombre test_bert --ner-backend hf --ner-modelo modelos/ner-bert`
   Repetir con `--datos` apuntando al split de prueba del corpus de Doccano. Ese split es la evaluación ciega del trabajo
   (sección 8.3): se corre una sola vez, después de reentrenar BERT, y no se ajusta nada con base en él. Los test sintético
   y MEDDOCAN ya se usaron para corregir el NER (inferencia por fragmentos y regla de ORG), así que no son ciegos.
   Las tablas reportan también el F2 sobre identificadores directos y secretos, criterio principal de la sección 7.4.
4. **Efecto sobre la respuesta** (requiere `set OPENAI_API_KEY=...`; evalúa GPT-5.5 Instant por su identificador de API `chat-latest` y gpt-5-mini, cambia los identificadores con `--modelos`):
   `python scripts/evaluar_respuestas.py --salidas resultados/test_bert/salidas_hibrido_heuristica.jsonl --n 60`
   Hace 3 llamadas por prompt (original, original repetido, enmascarado).
5. **Proxy**: `uvicorn proxy.servidor:app --port 8000` y `POST /v1/prompt {"prompt": "..."}`.
   Con `"enviar": false` solo devuelve la decisión y el texto enmascarado.

## Decisiones de diseño que el documento debe reflejar

- **Convención de anotación**: en CREDENTIAL, ID_DOC, FIN_ID y DOC_REF el span es solo el valor, no la
  palabra clave ("contraseña: [valor]", "NIT [900.123.456-7]"). Una URL que contiene una IP se anota como URL.
- **Responsabilidad por etiqueta en el híbrido**: NER aporta PER, ORG, LOC y ADDRESS; regex aporta el resto
  y también ADDRESS (mecanismo mixto). En los sistemas aislados cada uno aporta todo lo que sabe producir.
- **Heurística**: si decide ENVIAR, el prompt sale sin cambios; si decide ENMASCARAR, se enmascaran todas las
  entidades detectadas, incluidas las contextuales. Pesos y umbral en `mecanismo/heuristica.py`.
- **ER_di / ER_qi** se calculan por mención (TAB lo hace por mención y por entidad); una mención cuenta como
  protegida si todos sus caracteres quedaron bajo algún marcador, sin importar la etiqueta.
- **WP** usa pesos uniformes a nivel de carácter; TAB pondera por contenido informativo con un modelo de lenguaje.
- **Fuga residual**: proporción de entidades de referencia cuyo texto sigue apareciendo en el texto enviado.
- La etiqueta del documento "CREDENTIAL / SECRET" se llama `CREDENTIAL` en el código.

## MEDDOCAN y NER de respaldo

- `scripts/convertir_meddocan.py` pasa MEDDOCAN (BRAT) a JSONL con la taxonomía, respetando la partición
  oficial (`datos/meddocan/train|dev|test.jsonl`; se descartan EDAD, SEXO, PROFESION y los ID_* clínicos).
- `modelos/ner-spacy-meddocan/` es un NER spaCy entrenado aquí (CPU, 4000 pasos) con MEDDOCAN train + el dev
  sintético, para PER, ORG, LOC y ADDRESS; F1 0,93 en MEDDOCAN dev. Es un respaldo mientras se entrena el BERT:
  `--ner-backend spacy --ner-modelo modelos/ner-spacy-meddocan`.
- Para BERT: `python scripts/entrenar_ner.py --datos datos/meddocan/train.jsonl datos/sintetico/dev.jsonl
  --val datos/meddocan/dev.jsonl --salida modelos/ner-bert` (los documentos largos se parten en fragmentos).

## Acuerdo entre anotadores (validación cruzada con el asesor)

1. `python scripts/muestra_asesor.py` → `datos/acuerdo/muestra_asesor.jsonl` (50 textos sin etiquetas, el 15 % del corpus con mínimo 50, estratificado por partición) y `datos/acuerdo/referencia_andres.jsonl`.
2. Un segundo anotador (en esta ejecución, un compañero) anota la muestra en un proyecto aparte de Doccano siguiendo la guía (Anexo D), sin ver la anotación de Andrés, y exporta en JSONL.
3. `python scripts/acuerdo_anotadores.py --asesor ruta/export_asesor.jsonl` → `resultados/acuerdo_anotadores/acuerdo.md` (kappa de Cohen por token y F1 por mención entre anotadores). En esta ejecución el segundo anotador fue un compañero (`--nombre "compañero"`), no el asesor; su export está en `datos/acuerdo/export_companero.jsonl`. La anotación del corpus y los resultados no se modifican con este cálculo.

## Prueba de extremo a extremo del proxy

`colab/prueba_proxy_e2e.ipynb` (sube `colab/proxy-e2e.zip`) corre `scripts/prueba_proxy_e2e.py`: pasa por `proxy/servidor.py` (FastAPI TestClient) los prompts de `sintetico_test_final` y `doccano_prueba_final` con `ner-bert-final`, con un upstream simulado en lugar de la IA, y comprueba que el texto que recibiría la IA y la decisión coincidan con `salidas_hibrido_heuristica.jsonl`. Reporta latencia mediana y p95 y el hardware en `resultados/proxy_e2e/`. No recalcula métricas. El proxy usa por defecto el NER final (`NER_BACKEND=hf`, `modelos/ner-bert-final`).

## Demostración del proxy

`proxy/demo.html` se sirve en `http://localhost:8000/`: se escribe un prompt y se ve la decisión, los tipos de entidad detectados y el texto que se enviaría a la IA (opcionalmente se envía, si hay `OPENAI_API_KEY`).
- En Windows: descomprimir `colab/modelo-ner-demo.zip`, poner la carpeta `ner-bert-final` de Drive en `modelos/` y ejecutar `iniciar_demo.bat` (la primera vez crea un entorno con torch para CPU).
- Respaldo en Colab: `colab/demo_proxy.ipynb` con el mismo zip.
