# Prueba de extremo a extremo del proxy

NER: hf `/content/drive/MyDrive/modelos-ner/ner-bert-final`. Upstream simulado (no se llama a ninguna API). Hardware: Intel(R) Xeon(R) CPU @ 2.00GHz (2 núcleos), GPU Tesla T4, NER en cuda:0; Python 3.13.15.
Carga del proxy y del modelo: 30.89 s.

| Conjunto | Prompts | Enmascarados | Texto recibido por el upstream = texto evaluado | Decisión igual | Respuesta enviar=False igual | Latencia mediana (ms) | Latencia p95 (ms) |
|---|---|---|---|---|---|---|---|
| sintetico_test_final | 120 | 70 | 120/120 | 120/120 | 120/120 | 16.4 | 22.0 |
| doccano_prueba_final | 45 | 13 | 45/45 | 45/45 | 45/45 | 14.0 | 57.2 |

Latencia sobre todos los prompts: con upstream simulado mediana 15.9 ms, p95 28.4 ms; solo análisis (enviar=False) mediana 16.1 ms, p95 26.4 ms. Es la latencia que agrega el proxy antes de la llamada a la IA.
