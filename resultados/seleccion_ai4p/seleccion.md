# Selección del NER: B0 (MEDDOCAN) vs. B1 (AI4Privacy-es + WikiANN-es → MEDDOCAN)

Elegido solo con validación; no se usó ningún conjunto de prueba. Ninguno usa el sintético dev para entrenar.

| Conjunto de validación | Métrica (híbrido, estricto) | B0 | B1 |
|---|---|---|---|
| MEDDOCAN dev (solo NER, reporte BIO) | F1 micro | 0,956 | 0,959 |
| MEDDOCAN dev | F1 / F2 | 0,950 / 0,944 | 0,953 / 0,947 |
| MEDDOCAN dev | ER_di / ER_qi | 0,962 / 0,950 | 0,959 / 0,949 |
| Sintético dev | F1 / F2 | 0,912 / 0,889 | 0,923 / 0,909 |
| Sintético dev | F2 id. directos y secretos | 0,980 | 0,975 |
| Sintético dev | ER_di / ER_qi | 0,995 / 0,781 | 0,995 / 0,874 |
| Sintético dev | Fuga residual | 0,077 | 0,041 |

Por etiqueta en sintético dev (F1 estricto, híbrido): LOC 0,87 → 0,95; ORG 0,52 → 0,62; ADDRESS 0,98 → 0,94; PER 0,94 → 0,90.
En MEDDOCAN dev: ORG 0,80 → 0,83; el resto igual.

Decisión: B1. Mejora la protección de cuasi-identificadores (ER_qi +0,09) y reduce la fuga a la mitad en el sintético dev sin
empeorar MEDDOCAN dev ni la protección de identificadores directos (ER_di igual). Cede algo en PER y ADDRESS del sintético dev.
Datos de la etapa intermedia: 20.000 textos de AI4Privacy-es (split train; PER, LOC, ADDRESS) y los 20.000 de WikiANN-es train (PER, ORG, LOC).
