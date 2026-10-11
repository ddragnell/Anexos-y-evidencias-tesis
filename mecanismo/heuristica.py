"""Heurística de decisión basada en riesgo.

Decide si el prompt puede enviarse sin modificación (ENVIAR) o debe
enmascararse antes de su transmisión (ENMASCARAR). Pesos y umbral son
decisiones de diseño sustentadas en la taxonomía (sección 5: no se validan
empíricamente como modelo de riesgo).

1. Peso por etiqueta según criticidad: identificadores directos y
   secretos técnicos pesan más que las entidades contextuales.
2. Precedencia: si aparece una etiqueta crítica (CREDENTIAL, ID_DOC,
   FIN_ID) se enmascara siempre, sin importar el puntaje.
3. Coocurrencia: dos o más cuasi-identificadores distintos (DATE, LOC,
   ORG, NET_DIGITAL, URL, DOC_REF) en el mismo prompt suman 0,3, porque su
   combinación aumenta la identificabilidad aunque ninguno la determine
   por separado.
4. Riesgo = suma de pesos de las etiquetas distintas presentes
   + bonificación; si riesgo >= UMBRAL se enmascara.
Cuando la decisión es ENMASCARAR se enmascaran todas las entidades
detectadas, incluidas las contextuales.
"""
PESOS = {
    "CREDENTIAL": 1.0, "ID_DOC": 1.0, "FIN_ID": 1.0,
    "EMAIL": 0.8, "PHONE": 0.8, "ADDRESS": 0.8, "PER": 0.7,
    "NET_DIGITAL": 0.5, "DOC_REF": 0.4, "URL": 0.3,
    "ORG": 0.3, "LOC": 0.2, "DATE": 0.2,
}
CRITICAS = {"CREDENTIAL", "ID_DOC", "FIN_ID"}
CUASI_COOCURRENCIA = {"DATE", "LOC", "ORG", "NET_DIGITAL", "URL", "DOC_REF"}
BONO_COOCURRENCIA = 0.3
UMBRAL = 0.6


def decidir(entidades) -> dict:
    etiquetas = {e.etiqueta for e in entidades}
    riesgo = sum(PESOS.get(e, 0.0) for e in etiquetas)
    coocurrencia = len(etiquetas & CUASI_COOCURRENCIA) >= 2
    if coocurrencia:
        riesgo += BONO_COOCURRENCIA
    precedencia = sorted(etiquetas & CRITICAS)
    if precedencia:
        motivo = "precedencia: " + ", ".join(precedencia)
    elif riesgo >= UMBRAL:
        motivo = "riesgo >= umbral" + (" (con coocurrencia de cuasi-identificadores)" if coocurrencia else "")
    else:
        motivo = "riesgo < umbral"
    accion = "ENMASCARAR" if precedencia or riesgo >= UMBRAL else "ENVIAR"
    return {"accion": accion, "riesgo": round(riesgo, 3), "coocurrencia": coocurrencia, "motivo": motivo}
