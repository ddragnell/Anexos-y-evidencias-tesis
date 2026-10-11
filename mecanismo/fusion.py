"""Consolidación de solapamientos entre detectores (enfoque híbrido).

Reglas:
1. Cada detector solo aporta las etiquetas de las que es responsable
   (taxonomia.ETIQUETAS_NER / ETIQUETAS_REGEX); ADDRESS acepta ambos.
2. Entre spans del mismo detector que se solapan gana el más largo y,
   a igual largo, el de mayor puntaje.
3. Los spans de regex (patrones validados) tienen precedencia sobre los
   de NER. Un span NER que solapa uno de regex se recorta a la parte que
   no solapa, si lo que queda es una entidad plausible; si no, se descarta.
   Así "NIT 900.123.456-7 de Bancolombia" queda como ID_DOC + ORG en vez
   de una sola ORG que cubre el NIT (caso observado en la sección 8.3).
"""
import re

from .entidad import Entidad

PALABRAS_BORDE = {"de", "del", "la", "el", "los", "las", "en", "y", "con", "a", "al",
                  "nit", "cc", "c.c.", "correo", "tel", "teléfono", "celular",
                  "no", "no.", "n°", "nº", "#", "número"}


# desempate entre spans de igual largo y puntaje: el tipo más crítico gana
PRIORIDAD = {e: i for i, e in enumerate(["CREDENTIAL", "FIN_ID", "ID_DOC", "EMAIL", "URL", "PHONE", "NET_DIGITAL",
                                         "ADDRESS", "PER", "DOC_REF", "ORG", "LOC", "DATE"])}


def _greedy(ents: list[Entidad], aceptadas: list[Entidad] | None = None) -> list[Entidad]:
    aceptadas = list(aceptadas or [])
    for e in sorted(ents, key=lambda x: (-x.largo, -x.puntaje, PRIORIDAD.get(x.etiqueta, 99))):
        if not any(e.solapa(a) for a in aceptadas):
            aceptadas.append(e)
    return aceptadas


def _recortar(e: Entidad, bloqueos: list[Entidad], texto: str) -> Entidad | None:
    libres = [(e.inicio, e.fin)]
    for b in bloqueos:
        nuevos = []
        for ini, fin in libres:
            if b.fin <= ini or b.inicio >= fin:
                nuevos.append((ini, fin))
                continue
            if ini < b.inicio:
                nuevos.append((ini, b.inicio))
            if b.fin < fin:
                nuevos.append((b.fin, fin))
        libres = nuevos
    mejor = None
    for ini, fin in libres:
        tokens = list(re.finditer(r"\S+", texto[ini:fin]))
        while tokens and tokens[0].group().lower().strip(",.:;") in PALABRAS_BORDE:
            tokens.pop(0)
        while tokens and tokens[-1].group().lower().strip(",.:;") in PALABRAS_BORDE:
            tokens.pop()
        if not tokens:
            continue
        a, b = ini + tokens[0].start(), ini + tokens[-1].end()
        while b > a and texto[b - 1] in ",.;:":
            b -= 1
        if sum(c.isalpha() for c in texto[a:b]) >= 3 and (mejor is None or b - a > mejor[1] - mejor[0]):
            mejor = (a, b)
    if mejor is None:
        return None
    return Entidad(mejor[0], mejor[1], e.etiqueta, texto[mejor[0]:mejor[1]], e.fuente, e.puntaje, e.subtipo)


def fusionar(texto: str, regex: list[Entidad], ner: list[Entidad],
             etiquetas_regex: set[str] | None, etiquetas_ner: set[str] | None) -> list[Entidad]:
    if etiquetas_regex is not None:
        regex = [e for e in regex if e.etiqueta in etiquetas_regex]
    if etiquetas_ner is not None:
        ner = [e for e in ner if e.etiqueta in etiquetas_ner]
    finales = _greedy(regex)
    ner_recortadas = []
    for e in ner:
        r = _recortar(e, finales, texto) if any(e.solapa(f) for f in finales) else e
        if r:
            ner_recortadas.append(r)
    finales = _greedy(ner_recortadas, finales)
    return sorted(finales, key=lambda x: x.inicio)
