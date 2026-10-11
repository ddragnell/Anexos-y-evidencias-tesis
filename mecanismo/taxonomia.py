"""Taxonomía final del trabajo (Tabla 6 del documento).

Trece etiquetas en tres macrogrupos. Los atributos sensibles semánticos
(salud, afiliación política, etc.) están excluidos de la detección.
"""

# etiqueta -> (macrogrupo, tipo de identificador para TAB, mecanismo)
TAXONOMIA = {
    "PER":         ("Identificadores directos", "di", "NER + contexto/listas"),
    "EMAIL":       ("Identificadores directos", "di", "Regex + validación"),
    "PHONE":       ("Identificadores directos", "di", "Regex + validación"),
    "ADDRESS":     ("Identificadores directos", "di", "NER + regex/diccionarios"),
    "ID_DOC":      ("Identificadores directos", "di", "Regex + contexto"),
    "FIN_ID":      ("Identificadores directos", "di", "Regex + validadores"),
    "DATE":        ("Cuasi-identificadores contextuales", "qi", "Regex + contexto"),
    "LOC":         ("Cuasi-identificadores contextuales", "qi", "NER"),
    "ORG":         ("Cuasi-identificadores contextuales", "qi", "NER + contexto"),
    "CREDENTIAL":  ("Técnico-empresarial", "di", "Regex + validadores + criterio de entropía"),
    "NET_DIGITAL": ("Técnico-empresarial", "qi", "Regex + validadores"),
    "URL":         ("Técnico-empresarial", "qi", "Regex + contexto"),
    "DOC_REF":     ("Técnico-empresarial", "qi", "Regex + contexto"),
}

ETIQUETAS = list(TAXONOMIA)
DIRECTAS = {e for e, (_, t, _) in TAXONOMIA.items() if t == "di"}
CUASI = {e for e, (_, t, _) in TAXONOMIA.items() if t == "qi"}

# Qué detector es responsable de cada etiqueta en el enfoque híbrido.
# Las mixtas (ADDRESS) aceptan ambas fuentes.
ETIQUETAS_NER = {"PER", "ORG", "LOC", "ADDRESS"}
ETIQUETAS_REGEX = {"EMAIL", "PHONE", "ADDRESS", "ID_DOC", "FIN_ID", "DATE",
                   "CREDENTIAL", "NET_DIGITAL", "URL", "DOC_REF"}


def marcador(etiqueta: str) -> str:
    """Marcador tipado con el que se enmascara la entidad, p. ej. [PER]."""
    return f"[{etiqueta}]"
