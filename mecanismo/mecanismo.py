"""Mecanismo preventivo: detección (regex, NER o híbrido) + heurística + enmascaramiento."""
from .entidad import Entidad
from .fusion import fusionar
from .heuristica import decidir
from .ner_detector import DetectorNER
from .regex_detector import DetectorRegex
from .taxonomia import ETIQUETAS_NER, ETIQUETAS_REGEX, marcador


def enmascarar(texto: str, entidades: list[Entidad]) -> str:
    """Reemplaza cada entidad por su marcador tipado. No guarda el mapeo:
    el proxy no restituye las entidades originales."""
    partes, cursor = [], 0
    for e in sorted(entidades, key=lambda x: x.inicio):
        if e.inicio < cursor:
            continue
        partes += [texto[cursor:e.inicio], marcador(e.etiqueta)]
        cursor = e.fin
    partes.append(texto[cursor:])
    return "".join(partes)


class Mecanismo:
    """modo: "hibrido", "regex" o "ner"."""

    def __init__(self, modo: str = "hibrido", ner: DetectorNER | None = None, usar_heuristica: bool = True):
        self.modo = modo
        self.regex = DetectorRegex() if modo in ("hibrido", "regex") else None
        self.ner = ner if modo in ("hibrido", "ner") else None
        if self.ner is None and modo in ("hibrido", "ner"):
            self.ner = DetectorNER("spacy")
        self.usar_heuristica = usar_heuristica

    def detectar(self, texto: str) -> list[Entidad]:
        r = self.regex.detectar(texto) if self.regex else []
        n = self.ner.detectar(texto) if self.ner else []
        if self.modo == "hibrido":
            return fusionar(texto, r, n, ETIQUETAS_REGEX, ETIQUETAS_NER)
        # sistemas aislados: cada uno con todas las etiquetas que sepa producir
        return fusionar(texto, r, n, None, None)

    def procesar(self, texto: str) -> dict:
        ents = self.detectar(texto)
        decision = decidir(ents) if self.usar_heuristica else {"accion": "ENMASCARAR" if ents else "ENVIAR"}
        enviado = enmascarar(texto, ents) if decision["accion"] == "ENMASCARAR" else texto
        return {"entidades": ents, "decision": decision, "texto_enviado": enviado}
