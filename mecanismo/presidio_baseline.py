"""Línea base: Microsoft Presidio tal como viene, configurado para español.

Usa el motor spaCy con es_core_news_lg, el modelo más grande con reconocimiento
de entidades que spaCy ofrece para español, y los reconocedores predefinidos que
Presidio carga para "es". No se agregan reconocedores propios (cédula, NIT,
credenciales...), porque la línea base mide lo que Presidio cubre sin
adaptación. Sus tipos se traducen a la taxonomía para poder compararlo.
"""
import logging

from .entidad import Entidad

MAPEO_PRESIDIO = {
    "PERSON": "PER", "LOCATION": "LOC", "ORGANIZATION": "ORG", "NRP": None,
    "EMAIL_ADDRESS": "EMAIL", "PHONE_NUMBER": "PHONE", "CREDIT_CARD": "FIN_ID",
    "IBAN_CODE": "FIN_ID", "CRYPTO": "FIN_ID", "IP_ADDRESS": "NET_DIGITAL",
    "MAC_ADDRESS": "NET_DIGITAL", "URL": "URL", "DATE_TIME": "DATE",
    "ES_NIF": "ID_DOC", "ES_NIE": "ID_DOC",
}


class DetectorPresidio:
    nombre = "presidio"

    def __init__(self, modelo_spacy: str = "es_core_news_lg", umbral: float = 0.0):
        logging.getLogger("tldextract").setLevel(logging.CRITICAL)
        logging.getLogger("presidio-analyzer").setLevel(logging.ERROR)
        from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
        from presidio_analyzer.nlp_engine import NlpEngineProvider
        ne = NlpEngineProvider(nlp_configuration={
            "nlp_engine_name": "spacy", "models": [{"lang_code": "es", "model_name": modelo_spacy}]}).create_engine()
        reg = RecognizerRegistry(supported_languages=["es"])
        reg.load_predefined_recognizers(languages=["es"], nlp_engine=ne)
        self.motor = AnalyzerEngine(nlp_engine=ne, registry=reg, supported_languages=["es"])
        self.umbral = umbral

    def detectar(self, texto: str) -> list[Entidad]:
        ents = []
        for r in self.motor.analyze(texto, language="es", score_threshold=self.umbral):
            etq = MAPEO_PRESIDIO.get(r.entity_type)
            if etq:
                ents.append(Entidad(r.start, r.end, etq, texto[r.start:r.end], "presidio", float(r.score),
                                    extra={"tipo_presidio": r.entity_type}))
        # Presidio puede devolver spans solapados: se conserva el de mayor puntaje
        aceptadas = []
        for e in sorted(ents, key=lambda x: (-x.puntaje, -x.largo)):
            if not any(e.solapa(a) for a in aceptadas):
                aceptadas.append(e)
        return sorted(aceptadas, key=lambda x: x.inicio)
