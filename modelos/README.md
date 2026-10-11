# Modelos

Los pesos de los modelos no están en el repositorio por su tamaño (unos 420 MB cada uno). Aquí quedan sus reportes de validación.

| Carpeta | Modelo | Dónde está |
|---|---|---|
| `ner-bert-final/` | Modelo final usado en la evaluación ciega y en el proxy | ENLACE_AL_MODELO_FINAL |
| `ner-bert/` | BETO ajustado solo con MEDDOCAN (comparación) | No publicado |

Para usar el modelo final, descarga la carpeta completa (`config.json`, `model.safetensors`, archivos del tokenizador) y déjala en `modelos/ner-bert-final/`.
