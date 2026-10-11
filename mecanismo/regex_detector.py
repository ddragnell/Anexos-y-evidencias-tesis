"""Detector basado en expresiones regulares con validadores y contexto.

Cubre las etiquetas estructuradas de la taxonomía: EMAIL, PHONE, ADDRESS,
ID_DOC (CC, CE, NIT, PASAPORTE), FIN_ID, DATE, CREDENTIAL, NET_DIGITAL,
URL y DOC_REF. Presidio no trae reconocedores para cédula ni NIT, por eso
se implementan aquí.

Convención de anotación (la misma del corpus): para CREDENTIAL, ID_DOC,
FIN_ID y DOC_REF el span es solo el valor, no la palabra clave que lo
precede ("contraseña: [Xy9#kL2p]", "NIT [900.123.456-7]").
"""
import ipaddress
import re

from .entidad import Entidad

I = re.IGNORECASE
MESES = r"(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|sept?iembre|octubre|noviembre|diciembre)"


# ---------------------------------------------------------------- validadores
def nit_valido(digitos: str, dv: str) -> bool:
    pesos = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
    s = sum(int(d) * p for d, p in zip(reversed(digitos), pesos))
    r = s % 11
    esperado = r if r in (0, 1) else 11 - r
    return esperado == int(dv)


def luhn_valido(numero: str) -> bool:
    d = [int(c) for c in numero][::-1]
    total = sum(d[0::2]) + sum(sum(divmod(2 * x, 10)) for x in d[1::2])
    return total % 10 == 0


def iban_valido(iban: str) -> bool:
    s = iban.replace(" ", "").upper()
    if not 15 <= len(s) <= 34:
        return False
    s = s[4:] + s[:4]
    return int("".join(str(int(c, 36)) for c in s)) % 97 == 1


# Marcadores de posición evidentes ("TU_API_KEY", "<tu_contraseña>", "****",
# "your-api-key-here"): la guía de anotación (sección 7.3) no los marca.
P_MARCADOR = re.compile(
    r"^[<\[{(]|[>\]})]$|^[*xX•.\-_]+$|(?:^|[^a-z])(?:tu|su|mi|your|my)[_\- ]|"
    r"x{4,}|\*{3,}|changeme|example|ejemplo|placeholder|dummy|(?:^|[^a-z])(?:aqu[ií]|here|insert)|reemplaza", re.I)


def es_marcador(valor: str) -> bool:
    return bool(P_MARCADOR.search(valor))


def parece_secreto(valor: str) -> bool:
    """Validador del candidato a credencial: debe mezclar clases de
    caracteres, para no enmascarar palabras comunes, y no ser un marcador
    de posición."""
    if len(valor) < 6 or es_marcador(valor):
        return False
    clases = sum([any(c.islower() for c in valor), any(c.isupper() for c in valor),
                  any(c.isdigit() for c in valor), any(not c.isalnum() for c in valor)])
    return clases >= 2


def _limpia_cola(texto: str, ini: int, fin: int) -> int:
    while fin > ini and texto[fin - 1] in ".,;:)]}\"'¿?¡!":
        fin -= 1
    return fin


# ---------------------------------------------------------------- patrones
P_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
P_URL = re.compile(r"\b(?:https?://|www\.)[^\s<>\"']+", I)
P_PHONE = re.compile(
    r"(?<![\w.])(?:\+?57[\s.-]?)?(?:\(?60\d\)?[\s.-]?\d{3}[\s.-]?\d{4}|\(?3\d{2}\)?[\s.-]?\d{3}[\s.-]?\d{4})"
    r"(?:\s?(?:ext\.?|extensión)\s?\d{1,5})?(?![\w])", I)
P_PHONE_INTL = re.compile(r"(?<![\w])\+(?!57)\d{1,3}[\s.-]?\(?\d{1,4}\)?(?:[\s.-]?\d{2,4}){2,4}(?![\w])")
P_NIT = re.compile(r"(?<![\d.])(\d{3}\.?\d{3}\.?\d{3})\s?-\s?(\d)(?![\d])")
P_NIT_CTX = re.compile(r"\bNIT\.?\s*(?:n[°ºo.]\s*|número\s*|:\s*)?(\d{3}\.?\d{3}\.?\d{3,4})(?![\d-])", I)
P_CC_CTX = re.compile(
    r"\b(?:c[ée]dula(?:\s+de\s+ciudadan[íi]a)?|C\.\s?C\.?|CC|documento(?:\s+de\s+identidad)?|"
    r"identificaci[óo]n|identificad[oa]\s+con(?:\s+(?:la\s+)?(?:c[ée]dula|CC|C\.C\.))?|T\.\s?I\.?|tarjeta\s+de\s+identidad)"
    r"\s*(?:n[°ºo.]+\s*|número\s*|#\s*|:\s*)?(\d{1,3}(?:\.\d{3}){1,3}|\d{6,10})(?![\d.]\d)", I)
P_CE_CTX = re.compile(r"\b(?:c[ée]dula\s+de\s+extranjer[íi]a|C\.\s?E\.?|CE)\s*(?:n[°ºo.]+\s*|número\s*|:\s*)?(\d{1,3}(?:\.\d{3}){1,2}|\d{5,8})(?![\d])", I)
P_PASAPORTE = re.compile(r"\bpasaporte\s*(?:n[°ºo.]+\s*|número\s*|:\s*)?([A-Z]{1,3}\d{5,9})\b", I)
P_NUM_PUNTOS = re.compile(r"(?<![\d.$])(\d{1,3}\.\d{3}\.\d{3}(?:\.\d{3})?)(?![\d.,]|\s*(?:pesos|COP|USD|millones|de pesos))", I)
P_TARJETA = re.compile(r"(?<![\d])(?:\d[ -]?){12,18}\d(?![\d])")
P_IBAN = re.compile(r"\b[A-Z]{2}\d{2}(?:\s?[A-Z0-9]{4}){3,7}(?:\s?[A-Z0-9]{1,4})?\b")
P_CUENTA = re.compile(
    r"\b(?:cuenta|cta\.?)(?:\s+(?:de\s+)?(?:ahorros|corriente|bancaria|n[óo]mina))?(?:\s+(?:n[°ºo.]+|número|#))?\s*:?\s*"
    r"(?:(?:en|de|del)\s+[A-ZÁÉÍÓÚ][\wáéíóú]+(?:\s+[A-ZÁÉÍÓÚ][\wáéíóú]+)?\s+(?:n[°ºo.]+|número|#)?\s*)?"
    r"(\d[\d-]{5,22}\d)", I)
P_FECHA = re.compile(
    rf"\b(?:\d{{1,2}}[/-]\d{{1,2}}[/-](?:\d{{4}}|\d{{2}})|\d{{4}}-\d{{2}}-\d{{2}}|"
    rf"\d{{1,2}}\s+de\s+{MESES}(?:\s+(?:de|del)\s+\d{{4}})?|{MESES}\s+(?:de|del)\s+\d{{4}})\b", I)
P_IPV4 = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?(?![\d.]\d)")
P_IPV6 = re.compile(r"(?<![\w:])(?:[0-9a-f]{1,4}:){2,7}(?::|[0-9a-f]{1,4})(?:[0-9a-f:]*)(?![\w:])", I)
P_MAC = re.compile(r"\b(?:[0-9A-F]{2}[:-]){5}[0-9A-F]{2}\b", I)
P_SECRETOS = [
    re.compile(r"\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{20,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]+?-----END [A-Z ]*PRIVATE KEY-----"),
]
P_SECRETO_CTX = re.compile(
    r"(?:\b|_)(?:contraseña|password|passwd|pwd|clave(?:\s+de\s+acceso)?|token(?:\s+de\s+acceso)?|api[_ -]?key|access[_ ]key(?:[_ ]id)?|"
    r"secret(?:o)?(?:[_ ]access[_ ]key)?|client[_ ]secret|bearer|pin)\b(?:\s+(?:es|era|sería|a|quedó|en|por|del?\s+\w+|actual|nueva|temporal)\b){0,3}"
    r"\s*[:=]?\s*[\"'`]?([^\s\"'`,;)}]{6,})", I)
# candidato de alta entropía sin palabra clave: >= 24 caracteres alfanuméricos mezclando clases
P_ALTA_ENTROPIA = re.compile(r"(?<![\w/.@-])[A-Za-z0-9_\-]{24,}(?![\w/.@-])")
P_CONN = re.compile(r"\b[a-z][a-z0-9+]*://[^\s:/@]+:([^\s@/]+)@", I)
P_DOCREF = re.compile(
    r"\b(?:contrato|radicado|factura(?:\s+electr[óo]nica)?|orden\s+de\s+compra|OC|ticket|caso|incidente|"
    r"expediente|proceso|cotizaci[óo]n|p[óo]liza|requerimiento|solicitud)\s*(?:n[°ºo.]+\s*|número\s*|#\s*|:\s*)?"
    r"([A-Z]{0,5}[-_]?\d[\w-]{2,}\d|[A-Z]{2,5}-\d{3,})", I)
P_DOCREF_SUELTO = re.compile(r"\b(?:INC|REQ|CHG|RITM|FE|OC|CTR|RAD)-?\d{4,}\b")
P_DIRECCION = re.compile(
    r"\b(?:calle|cl\.?|carrera|cra\.?|kra\.?|kr\.?|cr\.?|avenida(?:\s+calle|\s+carrera)?|av\.?|diagonal|dg\.?|"
    r"transversal|tv\.?|circular|cir\.?|autopista)\s*\d{1,3}\s?[A-Z]?(?:\s?bis)?(?:\s?sur)?\s*"
    r"(?:#|nro\.?|n[°ºo.]+|no\.?|número)\s*\d{1,3}\s?[A-Z]?\s*-\s*\d{1,3}(?:\s?sur)?"
    r"(?:\s*,?\s*(?:apartamento|apto|oficina|of\.?|torre|interior|int\.?|local|piso|casa|bloque)\.?\s*[\w-]+)*", I)


class DetectorRegex:
    nombre = "regex"

    def detectar(self, texto: str) -> list[Entidad]:
        ents: list[Entidad] = []

        def add(ini, fin, etq, sub=None, p=1.0):
            ents.append(Entidad(ini, fin, etq, texto[ini:fin], "regex", p, sub))

        for m in P_EMAIL.finditer(texto):
            add(m.start(), m.end(), "EMAIL")
        for m in P_URL.finditer(texto):
            add(m.start(), _limpia_cola(texto, m.start(), m.end()), "URL")
        for m in P_PHONE.finditer(texto):
            add(m.start(), m.end(), "PHONE")
        for m in P_PHONE_INTL.finditer(texto):
            if sum(c.isdigit() for c in m.group()) >= 8:
                add(m.start(), m.end(), "PHONE", p=0.8)

        # ID_DOC
        for m in P_NIT.finditer(texto):
            dig = re.sub(r"\D", "", m.group(1))
            if nit_valido(dig, m.group(2)):
                add(m.start(), m.end(), "ID_DOC", "NIT")
        for m in P_NIT_CTX.finditer(texto):
            add(m.start(1), m.end(1), "ID_DOC", "NIT")
        for m in P_CE_CTX.finditer(texto):
            add(m.start(1), m.end(1), "ID_DOC", "CE")
        for m in P_CC_CTX.finditer(texto):
            add(m.start(1), m.end(1), "ID_DOC", "CC")
        for m in P_PASAPORTE.finditer(texto):
            add(m.start(1), m.end(1), "ID_DOC", "PASAPORTE")
        for m in P_NUM_PUNTOS.finditer(texto):  # 1.036.456.789 sin contexto
            add(m.start(1), m.end(1), "ID_DOC", "CC", 0.6)

        # FIN_ID
        for m in P_TARJETA.finditer(texto):
            dig = re.sub(r"\D", "", m.group())
            if 13 <= len(dig) <= 19 and dig[0] in "3456" and luhn_valido(dig):
                add(m.start(), m.end(), "FIN_ID", "TARJETA")
        for m in P_IBAN.finditer(texto):
            if iban_valido(m.group()):
                add(m.start(), m.end(), "FIN_ID", "IBAN")
        for m in P_CUENTA.finditer(texto):
            if sum(c.isdigit() for c in m.group(1)) >= 6:
                add(m.start(1), m.end(1), "FIN_ID", "CUENTA")

        for m in P_FECHA.finditer(texto):
            add(m.start(), m.end(), "DATE")

        # NET_DIGITAL
        for m in P_IPV4.finditer(texto):
            try:
                ipaddress.ip_network(m.group(), strict=False)
                add(m.start(), m.end(), "NET_DIGITAL", "IPV4")
            except ValueError:
                pass
        for m in P_IPV6.finditer(texto):
            try:
                ipaddress.IPv6Address(m.group())
                add(m.start(), m.end(), "NET_DIGITAL", "IPV6")
            except ValueError:
                pass
        for m in P_MAC.finditer(texto):
            add(m.start(), m.end(), "NET_DIGITAL", "MAC")

        # CREDENTIAL
        for p in P_SECRETOS:
            for m in p.finditer(texto):
                if not es_marcador(m.group()):
                    add(m.start(), m.end(), "CREDENTIAL")
        for m in P_SECRETO_CTX.finditer(texto):
            fin = _limpia_cola(texto, m.start(1), m.end(1))
            if parece_secreto(texto[m.start(1):fin]):
                add(m.start(1), fin, "CREDENTIAL", p=0.9)
        for m in P_ALTA_ENTROPIA.finditer(texto):
            v = m.group()
            if sum([any(c.islower() for c in v), any(c.isupper() for c in v), any(c.isdigit() for c in v)]) == 3 \
                    and not es_marcador(v):
                add(m.start(), m.end(), "CREDENTIAL", p=0.7)
        for m in P_CONN.finditer(texto):
            if not es_marcador(m.group(1)):
                add(m.start(1), m.end(1), "CREDENTIAL", p=0.9)

        for m in P_DOCREF.finditer(texto):
            add(m.start(1), m.end(1), "DOC_REF", p=0.8)
        for m in P_DOCREF_SUELTO.finditer(texto):
            add(m.start(), m.end(), "DOC_REF", p=0.8)

        for m in P_DIRECCION.finditer(texto):
            add(m.start(), _limpia_cola(texto, m.start(), m.end()), "ADDRESS")

        return ents
