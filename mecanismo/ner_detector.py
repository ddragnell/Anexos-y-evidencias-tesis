"""Componente NER.

Dos backends con la misma interfaz:
- "hf": modelo de token classification de Hugging Face, p. ej. el
  dccuchile/bert-base-spanish-wwm-cased ajustado con MEDDOCAN o con el
  corpus de Doccano (scripts/entrenar_ner.py). Es el backend del trabajo.
- "spacy": es_core_news_sm (PER/ORG/LOC). Sirve como respaldo cuando el
  modelo BERT no está disponible y es también el NER que usa Presidio.

Las etiquetas del modelo se normalizan a la taxonomía con MAPEO.
"""
import re

from .entidad import Entidad
from .taxonomia import ETIQUETAS

# Etiquetas de MEDDOCAN, spaCy y CoNLL -> taxonomía. Lo que no aparece se ignora
# (EDAD, SEXO, PROFESION, MISC...). Las del corpus propio ya coinciden.
MAPEO = {
    # spaCy / CoNLL
    "PER": "PER", "PERSON": "PER", "ORG": "ORG", "LOC": "LOC", "GPE": "LOC",
    # MEDDOCAN
    "NOMBRE_SUJETO_ASISTENCIA": "PER", "NOMBRE_PERSONAL_SANITARIO": "PER",
    "FAMILIARES_SUJETO_ASISTENCIA": "PER",
    "CALLE": "ADDRESS", "TERRITORIO": "LOC", "PAIS": "LOC",
    "HOSPITAL": "ORG", "INSTITUCION": "ORG", "CENTRO_SALUD": "ORG",
    "FECHAS": "DATE", "CORREO_ELECTRONICO": "EMAIL",
    "NUMERO_TELEFONO": "PHONE", "NUMERO_FAX": "PHONE",
    "ID_SUJETO_ASISTENCIA": "ID_DOC", "ID_TITULACION_PERSONAL_SANITARIO": "ID_DOC",
    "ID_ASEGURAMIENTO": "ID_DOC", "ID_CONTACTO_ASISTENCIAL": "ID_DOC", "ID_EMPLEO": "ID_DOC",
    "URL_WEB": "URL", "DIREC_PROT_INTERNET": "NET_DIGITAL",
}
MAPEO.update({e: e for e in ETIQUETAS})


NO_ENTIDAD = {"nit", "cc", "c.c.", "ce", "cel", "tel", "id", "api", "ip", "url", "pdf", "sas", "s.a.s."}
POS_NO_NOMBRE = {"VERB", "AUX", "INTJ", "ADV", "ADP", "PRON", "DET", "SCONJ", "CCONJ", "NUM"}


def _plausible(span) -> bool:
    """Filtro de contexto para el NER de spaCy (modelo pequeño y ruidoso):
    descarta spans sin mayúscula inicial, palabras clave de formulario
    (NIT, CC, tel...) y spans de una sola palabra que son verbos,
    interjecciones o palabras vacías ("Hola", "Vivo", "Pagar")."""
    if not any(t.text[:1].isupper() for t in span) or span.text.lower().strip("¿?¡!") in NO_ENTIDAD:
        return False
    if any(c in span.text for c in "_=") or span.text.startswith(("¿", "¡")):  # identificadores de código, preguntas
        return False
    if len(span) == 1:
        t = span[0]
        if t.i == 0:  # los prompts suelen abrir con un verbo en imperativo ("Revisa", "Redacta")
            return False
        # palabra común o verbo conjugado ("Redacta" -> "redactar"): el lema difiere de la forma
        if t.pos_ in POS_NO_NOMBRE or t.is_stop or (t.lemma_ and t.lemma_.lower() != t.text.lower()):
            return False
    return True


# Regla de contexto para ORG: secuencia de palabras con mayúscula seguida de una
# forma societaria colombiana. No usa listas de empresas.
P_SOCIEDAD = re.compile(
    r"\b(?:[A-ZÁÉÍÓÚÑ][\wáéíóúñ&.-]*\s+(?:(?:de|del|la|las|los|el)\s+)?){1,5}"
    r"(?:S\.\s?A\.\s?S\.?|S\.\s?A\.?|Ltda\.?|E\.\s?S\.\s?P\.?|SAS|S\.\s?en\s?C\.?)(?![\w])")


def _sociedades(texto: str) -> list[Entidad]:
    return [Entidad(m.start(), m.end(), "ORG", m.group(), "ner", 0.9) for m in P_SOCIEDAD.finditer(texto)]


class DetectorNER:
    nombre = "ner"

    def __init__(self, backend: str = "spacy", modelo: str | None = None, umbral: float = 0.5):
        self.backend = backend
        self.umbral = umbral
        if backend == "spacy":
            import spacy
            self.nlp = spacy.load(modelo or "es_core_news_sm")
        elif backend == "hf":
            from transformers import pipeline
            # stride: los textos largos se procesan en ventanas solapadas en vez de truncarse
            self.nlp = pipeline("token-classification", model=modelo,
                                aggregation_strategy="first", stride=64)
            # algunos tokenizadores no declaran su longitud máxima y entonces no se hacen ventanas
            tok = self.nlp.tokenizer
            tok.model_max_length = min(tok.model_max_length, self.nlp.model.config.max_position_embeddings, 512)
        else:
            raise ValueError(backend)

    def detectar(self, texto: str) -> list[Entidad]:
        ents = []
        if self.backend == "spacy":
            for e in self.nlp(texto).ents:
                etq = MAPEO.get(e.label_)
                if etq and _plausible(e):
                    ents.append(Entidad(e.start_char, e.end_char, etq, e.text, "ner", 0.85))
            ents += _sociedades(texto)
        else:
            # Se procesa por fragmentos de hasta 600 caracteres, igual que en el
            # entrenamiento (scripts/entrenar_ner.py), y se corrigen los desplazamientos.
            for base, frag in _fragmentos(texto):
                for e in self.nlp(frag):
                    etq = MAPEO.get(e["entity_group"].removeprefix("B-").removeprefix("I-"))
                    if etq and e["score"] >= self.umbral:
                        ini, fin = base + e["start"], base + e["end"]
                        # el tokenizador puede incluir el espacio inicial en el span
                        while ini < fin and texto[ini].isspace():
                            ini += 1
                        ents.append(Entidad(ini, fin, etq, texto[ini:fin], "ner", float(e["score"])))
            ents += _sociedades(texto)
        return ents


def _fragmentos(texto: str, max_chars: int = 600):
    """Corta en saltos de línea o fin de oración (o, si no hay, en un espacio)."""
    ini = 0
    while len(texto) - ini > max_chars:
        fin = ini + max_chars
        k = max((m for m in range(ini + max_chars // 3, fin) if texto[m - 1] in "\n."), default=None)
        if k is None:
            k = next((m for m in range(fin, ini, -1) if texto[m - 1] == " "), fin)
        yield ini, texto[ini:k]
        ini = k
    yield ini, texto[ini:]
