"""Genera el corpus sintético controlado de escenarios empresariales.

Cada prompt se arma desde una plantilla con ranuras ({PER}, {ID_DOC_CC}...)
y las anotaciones se registran al rellenar, de modo que el corpus queda
anotado por construcción. Todos los valores son ficticios (los secretos no
son funcionales). Salida en el formato de exportación de Doccano
(Sequence Labeling, JSONL): {"text", "label": [[ini, fin, etiqueta]], "meta"}.

Las plantillas se reparten entre dev y test sin compartir plantilla, para
que la evaluación en test no premie la memorización de una plantilla.

Uso: python scripts/generar_corpus_sintetico.py --n 400 --semilla 13
"""
import argparse
import json
import random
import re
import string
from pathlib import Path

NOMBRES = ["Andrés", "Valentina", "Juan Camilo", "María José", "Santiago", "Luisa Fernanda", "Carlos",
           "Daniela", "Sebastián", "Laura", "Felipe", "Natalia", "Mateo", "Paula Andrea", "Jorge",
           "Camila", "Alejandro", "Isabella", "Julián", "Manuela", "Esteban", "Sara", "Diego", "Mariana",
           "Óscar", "Ana María", "Ricardo", "Juliana", "Hernán", "Gloria", "Wilson", "Yesenia", "Fabián"]
APELLIDOS = ["Ramírez", "Gómez", "Restrepo", "Ospina", "Zapata", "Vélez", "Castaño", "Henao", "Montoya",
             "Rodríguez", "Martínez", "López", "García", "Hernández", "Muñoz", "Álvarez", "Jaramillo",
             "Arango", "Correa", "Cárdenas", "Giraldo", "Mejía", "Quintero", "Salazar", "Toro", "Rendón",
             "Betancur", "Echeverri", "Londoño", "Uribe", "Patiño", "Valencia", "Moreno", "Duque"]
ORGS = ["Bancolombia", "Ecopetrol", "Grupo Éxito", "EPM", "Grupo Nutresa", "Sura", "Avianca", "Davivienda",
        "Cementos Argos", "Claro Colombia", "Inversiones La Montaña S.A.S.", "TecnoAndes Ltda.",
        "Logística del Valle S.A.S.", "Consultores Aburrá S.A.", "Distribuidora El Poblado S.A.S.",
        "Soluciones Cafeteras S.A.S.", "Banco de Bogotá", "Comfama", "Alpina", "Rappi",
        "Transportes Antioquia S.A.", "Clínica Las Américas", "Universidad de Medellín"]
LOCS = ["Medellín", "Bogotá", "Cali", "Barranquilla", "Envigado", "Itagüí", "Sabaneta", "Rionegro",
        "Bucaramanga", "Pereira", "Manizales", "Cartagena", "Antioquia", "Cundinamarca", "Bello",
        "El Poblado", "Laureles", "Chapinero", "Miami", "Ciudad de Panamá", "Quito"]
DOMINIOS_EMP = ["empresa.com.co", "tecnoandes.co", "inversioneslamontana.com", "logisticadelvalle.co",
                "consultoresaburra.com"]
DOMINIOS_PER = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.es"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
         "octubre", "noviembre", "diciembre"]
VIAS = ["Calle", "Cl.", "Carrera", "Cra.", "Cr", "Avenida", "Av.", "Diagonal", "Transversal", "Circular"]


def _sin_tildes(s):
    return s.translate(str.maketrans("áéíóúñÁÉÍÓÚÑ", "aeiounAEIOUN"))


class Gen:
    def __init__(self, rnd: random.Random):
        self.r = rnd
        self.persona = None

    def nueva_persona(self):
        r = self.r
        nombre = r.choice(NOMBRES)
        aps = r.sample(APELLIDOS, 2)
        forma = r.random()
        completo = f"{nombre} {aps[0]}" if forma < 0.55 else f"{nombre} {aps[0]} {aps[1]}"
        self.persona = (nombre, aps, completo)
        return completo

    # --- generadores por ranura
    def PER(self):
        return self.nueva_persona()

    def PER2(self):  # otra persona distinta, sin cambiar la persona actual
        p = self.persona
        x = self.nueva_persona()
        self.persona = p
        return x

    def EMAIL(self):
        r = self.r
        if self.persona is None:
            self.nueva_persona()
        nombre, aps, _ = self.persona
        n = _sin_tildes(nombre.split()[0].lower())
        a = _sin_tildes(aps[0].lower())
        local = r.choice([f"{n}.{a}", f"{n[0]}{a}", f"{n}{a}{r.randint(1, 99)}", f"{n}_{a}"])
        return f"{local}@{r.choice(DOMINIOS_EMP + DOMINIOS_PER)}"

    def PHONE(self):
        r = self.r
        if r.random() < 0.75:
            n = f"3{r.randint(0, 2)}{r.randint(0, 9)}{r.randint(1000000, 9999999)}"
            fmt = r.choice(["{a} {b} {c}", "{a}{b}{c}", "+57 {a} {b} {c}", "{a}-{b}-{c}", "+57{a}{b}{c}", "({a}) {b} {c}"])
            return fmt.format(a=n[:3], b=n[3:6], c=n[6:])
        ind = r.choice(["604", "601", "602", "605"])
        n = f"{r.randint(2000000, 4999999)}"
        return r.choice([f"{ind} {n[:3]} {n[3:]}", f"({ind}) {n[:3]} {n[3:]}", f"+57 {ind} {n}"]) + \
            (f" ext. {r.randint(100, 9999)}" if r.random() < 0.3 else "")

    def ID_DOC_CC(self):
        r = self.r
        n = str(r.choice([r.randint(1000000, 99999999), r.randint(1000000000, 1199999999)]))
        if r.random() < 0.6:
            return f"{int(n):,}".replace(",", ".")
        return n

    def ID_DOC_NIT(self):
        from mecanismo.regex_detector import nit_valido
        r = self.r
        base = f"{r.choice([8, 9])}{r.randint(0, 99999999):08d}"
        dv = next(str(d) for d in range(10) if nit_valido(base, str(d)))
        fmt = r.random()
        if fmt < 0.5:
            return f"{base[:3]}.{base[3:6]}.{base[6:]}-{dv}"
        if fmt < 0.85:
            return f"{base}-{dv}"
        return base

    def ID_DOC_CE(self):
        return str(self.r.randint(100000, 9999999))

    def ID_DOC_PAS(self):
        r = self.r
        return "".join(r.choices(string.ascii_uppercase, k=r.choice([2, 2, 3]))) + str(r.randint(100000, 99999999))

    def FIN_ID_TARJETA(self):
        r = self.r
        largo = 15 if r.random() < 0.15 else 16
        pref = "37" if largo == 15 else r.choice(["4", "5"])
        d = [int(c) for c in pref] + [r.randint(0, 9) for _ in range(largo - len(pref) - 1)]
        for dv in range(10):
            from mecanismo.regex_detector import luhn_valido
            if luhn_valido("".join(map(str, d + [dv]))):
                break
        s = "".join(map(str, d + [dv]))
        sep = r.choice([" ", "-", ""])
        if largo == 16:
            return sep.join(s[i:i + 4] for i in range(0, 16, 4))
        return sep.join([s[:4], s[4:10], s[10:]])

    def FIN_ID_CUENTA(self):
        r = self.r
        return r.choice([f"{r.randint(100, 999)}-{r.randint(100000, 999999)}-{r.randint(10, 99)}",
                         f"{r.randint(10000000000, 99999999999)}", f"{r.randint(1000, 9999)}{r.randint(100000, 999999)}"])

    def ADDRESS(self):
        r = self.r
        v = r.choice(VIAS)
        a = f"{r.randint(1, 120)}{r.choice(['', '', 'A', 'B', ' Sur'])}"
        b = f"{r.randint(1, 99)}{r.choice(['', '', 'A', 'B'])}"
        sep = r.choice(["#", "# ", "No. ", "N° ", "nro. "])
        s = f"{v} {a} {sep}{b}-{r.randint(1, 99)}"
        if r.random() < 0.4:
            s += r.choice([f" apto {r.randint(101, 1504)}", f", oficina {r.randint(201, 905)}", f" interior {r.randint(1, 9)}"])
        return s

    def DATE(self):
        r = self.r
        d, m, y = r.randint(1, 28), r.randint(1, 12), r.choice([1985, 1990, 1994, 2024, 2025, 2026, 2026])
        return r.choice([f"{d:02d}/{m:02d}/{y}", f"{d} de {MESES[m - 1]} de {y}", f"{y}-{m:02d}-{d:02d}",
                         f"{d} de {MESES[m - 1]}", f"{d}-{m:02d}-{y}"])

    def LOC(self):
        return self.r.choice(LOCS)

    def ORG(self):
        return self.r.choice(ORGS)

    def CRED_PWD(self):
        r = self.r
        base = r.choice(["Medellin", "Clave", "Acceso", "Admin", "Empresa", "Sistemas", "Verano", "Bodega"])
        return base + r.choice(["#", "*", "@", "$", "!", ""]) + str(r.randint(10, 2026)) + r.choice(["", "*", "."])[:1].replace(".", "")

    def CRED_KEY(self):
        r = self.r
        al = string.ascii_letters + string.digits
        t = r.random()
        if t < 0.35:
            return "sk-proj-" + "".join(r.choices(al, k=40))
        if t < 0.55:
            return "AKIA" + "".join(r.choices(string.ascii_uppercase + string.digits, k=16))
        if t < 0.75:
            return "ghp_" + "".join(r.choices(al, k=36))
        if t < 0.88:
            return "eyJhbGciOiJIUzI1NiJ9." + "".join(r.choices(al, k=30)) + "." + "".join(r.choices(al + "_-", k=28))
        return "".join(r.choices(al, k=32))  # token genérico sin prefijo

    def NET_IP(self):
        r = self.r
        return r.choice([f"192.168.{r.randint(0, 20)}.{r.randint(2, 254)}", f"10.{r.randint(0, 255)}.{r.randint(0, 255)}.{r.randint(2, 254)}",
                         f"172.{r.randint(16, 31)}.{r.randint(0, 255)}.{r.randint(2, 254)}", f"{r.randint(23, 200)}.{r.randint(0, 255)}.{r.randint(0, 255)}.{r.randint(2, 254)}"])

    def NET_MAC(self):
        r = self.r
        return r.choice([":", "-"]).join(f"{r.randint(0, 255):02X}" for _ in range(6))

    def URL(self):
        r = self.r
        dom = r.choice(DOMINIOS_EMP)
        return r.choice([f"https://intranet.{dom}/{r.choice(['rrhh', 'nomina', 'proyectos/q3', 'soporte'])}",
                         f"https://{r.choice(['erp', 'crm', 'jira', 'portal'])}.{dom}/{r.choice(['login', 'clientes/4821', 'dashboard'])}",
                         f"http://10.{r.randint(0, 50)}.{r.randint(0, 255)}.{r.randint(2, 254)}:{r.choice([8080, 3000, 8443])}/admin",
                         f"www.{dom}/{r.choice(['facturacion', 'empleados'])}"])

    def DOC_REF(self):
        r = self.r
        return r.choice([f"CTR-{r.choice([2025, 2026])}-{r.randint(1, 999):04d}", f"{r.choice([2025, 2026])}-{r.randint(1, 99999):06d}",
                         f"FE-{r.randint(1000, 99999)}", f"INC{r.randint(1000000, 9999999)}", f"OC-{r.randint(1000, 9999)}",
                         f"REQ-{r.randint(10000, 99999)}"])


RANURA_A_ETIQUETA = {
    "PER": "PER", "PER2": "PER", "EMAIL": "EMAIL", "PHONE": "PHONE", "ADDRESS": "ADDRESS",
    "ID_DOC_CC": "ID_DOC", "ID_DOC_NIT": "ID_DOC", "ID_DOC_CE": "ID_DOC", "ID_DOC_PAS": "ID_DOC",
    "FIN_ID_TARJETA": "FIN_ID", "FIN_ID_CUENTA": "FIN_ID", "DATE": "DATE", "LOC": "LOC", "ORG": "ORG",
    "CRED_PWD": "CREDENTIAL", "CRED_KEY": "CREDENTIAL", "NET_IP": "NET_DIGITAL", "NET_MAC": "NET_DIGITAL",
    "URL": "URL", "DOC_REF": "DOC_REF",
}

# (escenario, plantilla). Los textos sin ranuras son prompts limpios.
PLANTILLAS = [
    # RRHH
    ("rrhh", "Redacta un correo formal para {PER} ({EMAIL}) informándole que su solicitud de vacaciones a partir del {DATE} fue aprobada."),
    ("rrhh", "Necesito una carta laboral para {PER}, identificado con cédula {ID_DOC_CC}, que trabaja en {ORG} desde el {DATE} como analista de datos."),
    ("rrhh", "Resume esta hoja de vida: {PER}, C.C. {ID_DOC_CC}, nacido el {DATE} en {LOC}, celular {PHONE}, dirección {ADDRESS}. Experiencia de 5 años en desarrollo backend."),
    ("rrhh", "Ayúdame a escribir el mensaje de bienvenida para {PER}, que empieza el lunes en la sede de {LOC}. Su jefe será {PER2} y lo puede contactar al {PHONE}."),
    ("rrhh", "Calcula la liquidación de {PER} con documento de identidad {ID_DOC_CC}: salario de $4.200.000, ingresó el {DATE} y se retira el {DATE}. La nómina se paga a la cuenta de ahorros {FIN_ID_CUENTA}."),
    ("rrhh", "Escribe una evaluación de desempeño constructiva para {PER} del equipo de {ORG}; en el último trimestre cumplió el 85% de sus metas."),
    ("rrhh", "Tengo un candidato extranjero, {PER}, con cédula de extranjería {ID_DOC_CE} y pasaporte {ID_DOC_PAS}. ¿Qué documentos le pido para contratarlo?"),
    # finanzas
    ("finanzas", "Genera un recordatorio de pago para el cliente {ORG}, NIT {ID_DOC_NIT}, por la factura {DOC_REF} con vencimiento el {DATE}."),
    ("finanzas", "Revisa si este cobro es correcto: la tarjeta {FIN_ID_TARJETA} a nombre de {PER} tuvo un cargo de $1.250.000 el {DATE}."),
    ("finanzas", "Prepara la orden de pago al proveedor {ORG} con NIT {ID_DOC_NIT}, a la cuenta corriente {FIN_ID_CUENTA} de {ORG}, por $18.400.000."),
    ("finanzas", "Explícame cómo registrar en contabilidad el anticipo del contrato {DOC_REF} firmado con {ORG} el {DATE}."),
    ("finanzas", "Mi tarjeta corporativa {FIN_ID_TARJETA} fue rechazada en {LOC}. Redacta un correo a {EMAIL} pidiendo el desbloqueo."),
    ("finanzas", "Concilia estos movimientos de la cuenta {FIN_ID_CUENTA}: abono de $3.000.000 de {ORG} y débito de $450.000 por comisiones."),
    # soporte TI
    ("ti", "El servidor {NET_IP} no responde desde esta mañana; los logs muestran timeout al conectar con la base de datos. ¿Qué reviso primero?"),
    ("ti", "Configura este archivo .env para producción: DB_HOST={NET_IP}, DB_USER=admin, DB_PASSWORD={CRED_PWD}, OPENAI_API_KEY={CRED_KEY}."),
    ("ti", "¿Por qué falla este script? requests.get('{URL}', headers={'Authorization': 'Bearer {CRED_KEY}'}) devuelve 401."),
    ("ti", "El usuario {PER} ({EMAIL}) no puede entrar a {URL}. Ya le reseteé la contraseña a {CRED_PWD} pero sigue el error. Ticket {DOC_REF}."),
    ("ti", "Escribe una regla de firewall que bloquee la MAC {NET_MAC} y permita solo tráfico desde {NET_IP} hacia el puerto 443."),
    ("ti", "Documenta el incidente {DOC_REF}: el equipo con IP {NET_IP} de la sede {LOC} perdió conexión el {DATE}."),
    ("ti", "Revisa este código: client = boto3.client('s3', aws_access_key_id='{CRED_KEY}', aws_secret_access_key='{CRED_KEY}')"),
    ("ti", "Mi token de GitHub {CRED_KEY} dejó de funcionar al hacer push. ¿Cómo genero uno nuevo con permisos de repo?"),
    # legal / contratos
    ("legal", "Redacta una cláusula de confidencialidad para el contrato {DOC_REF} entre {ORG} y {ORG}, con domicilio en {ADDRESS}, {LOC}."),
    ("legal", "Resume el radicado {DOC_REF} interpuesto por {PER}, C.C. {ID_DOC_CC}, contra {ORG} el {DATE}."),
    ("legal", "Elabora un poder especial para que {PER} represente a {PER2}, identificado con cédula de ciudadanía {ID_DOC_CC}, ante notaría en {LOC}."),
    ("legal", "Revisa este otrosí al contrato {DOC_REF}: se modifica la fecha de terminación al {DATE} y el valor a $95.000.000."),
    # ventas / CRM
    ("ventas", "Escribe un correo de seguimiento a {PER} de {ORG} ({EMAIL}, {PHONE}) sobre la cotización {DOC_REF} que le enviamos."),
    ("ventas", "Clasifica a este cliente: {PER}, vive en {ADDRESS}, {LOC}, compró 3 veces este año y su último pedido fue el {DATE}."),
    ("ventas", "Prepara un guion de llamada para ofrecer el plan empresarial a {ORG}; el contacto es {PER} al {PHONE}."),
    ("ventas", "Envíale a {EMAIL} un resumen de la reunión del {DATE} con {ORG} sobre la renovación del contrato."),
    # atención al cliente
    ("servicio", "Responde amablemente a esta queja: 'Soy {PER}, mi pedido {DOC_REF} no ha llegado a {ADDRESS} y nadie contesta al {PHONE}.'"),
    ("servicio", "Un cliente escribió desde {EMAIL} diciendo que le cobraron dos veces en la tarjeta terminada en la {FIN_ID_TARJETA}. Redacta la respuesta."),
    ("servicio", "Traduce al inglés este mensaje para {PER} en {LOC}: su caso {DOC_REF} quedó resuelto y el reembolso llega en 5 días hábiles."),
    # gerencia / operaciones
    ("operaciones", "Haz un resumen ejecutivo de la reunión con {PER} y {PER2} de {ORG} en {LOC}: se acordó ampliar la bodega antes del {DATE}."),
    ("operaciones", "Organiza la logística del envío a {ADDRESS} en {LOC}; quien recibe es {PER}, teléfono {PHONE}."),
    ("operaciones", "Crea un acta de entrega del portátil serial PX-4471 a {PER}, cédula {ID_DOC_CC}, con MAC {NET_MAC}."),
    ("operaciones", "Pásame a tabla estos datos del proveedor: {ORG}, NIT {ID_DOC_NIT}, contacto {PER}, correo {EMAIL}, teléfono {PHONE}, dirección {ADDRESS}."),
    # solo contextuales (la heurística puede decidir ENVIAR)
    ("contextual", "Dame ideas para una campaña de fin de año dirigida a pymes de {LOC}."),
    ("contextual", "¿Qué ventajas tiene abrir una sede en {LOC} frente a {LOC} para una empresa de software?"),
    ("contextual", "Redacta un post de LinkedIn celebrando la alianza con {ORG}."),
    ("contextual", "Prepara la agenda del comité del {DATE} con los temas de presupuesto y contratación."),
    ("contextual", "Escribe una nota interna: el portal {URL} estará en mantenimiento el fin de semana."),
    # limpios
    ("limpio", "Explícame la diferencia entre un contrato a término fijo y uno indefinido en Colombia."),
    ("limpio", "Escribe una función en Python que valide si una cadena es un correo electrónico."),
    ("limpio", "Resume en cinco viñetas las buenas prácticas para gestionar contraseñas en una empresa."),
    ("limpio", "¿Cómo calculo el IVA del 19% sobre una factura de $2.500.000?"),
    ("limpio", "Redacta una política de uso aceptable de herramientas de inteligencia artificial para empleados."),
    ("limpio", "Dame una plantilla de acta de reunión con secciones de asistentes, temas y compromisos."),
    ("limpio", "¿Qué significa el error 502 Bad Gateway en un servidor Nginx versión 1.24.0?"),
    ("limpio", "Propón indicadores para medir la rotación de personal del área comercial en el tercer trimestre."),
    ("limpio", "Traduce al español: 'Please review the attached quarterly report before Friday.'"),
    ("limpio", "Escribe una consulta SQL que cuente los pedidos por mes del año 2025."),
    ("limpio", "Genera 10 preguntas para una entrevista de un cargo de analista de datos junior."),
    ("limpio", "¿Qué dice la Ley 1581 de 2012 sobre el tratamiento de datos personales?"),
]

RANURA = re.compile(r"\{([A-Z_0-9]+)\}")


def rellenar(plantilla: str, g: Gen):
    g.persona = None
    texto, etiquetas, cursor = "", [], 0
    for m in RANURA.finditer(plantilla):
        texto += plantilla[cursor:m.start()]
        valor = getattr(g, m.group(1))()
        ini = len(texto)
        texto += valor
        etiquetas.append([ini, len(texto), RANURA_A_ETIQUETA[m.group(1)]])
        cursor = m.end()
    texto += plantilla[cursor:]
    return texto, etiquetas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--semilla", type=int, default=13)
    ap.add_argument("--salida", default="datos/sintetico")
    a = ap.parse_args()
    r = random.Random(a.semilla)
    g = Gen(r)
    # partición por plantilla, estratificada por escenario: ~70% dev, ~30% test
    por_escenario = {}
    for i, (esc, _) in enumerate(PLANTILLAS):
        por_escenario.setdefault(esc, []).append(i)
    # se repite el sorteo hasta que test contenga las 13 etiquetas
    todas = set(RANURA_A_ETIQUETA.values())
    for intento in range(1000):
        rs = random.Random(a.semilla * 1000 + intento)
        split = {}
        for esc, ids in por_escenario.items():
            ids = ids[:]
            rs.shuffle(ids)
            k = max(1, round(len(ids) * 0.3))
            for j, i in enumerate(ids):
                split[i] = "test" if j < k else "dev"
        en_test = {RANURA_A_ETIQUETA[x] for i, (_, pl) in enumerate(PLANTILLAS) if split[i] == "test"
                   for x in RANURA.findall(pl)}
        if en_test == todas:
            break
    out = Path(a.salida)
    out.mkdir(parents=True, exist_ok=True)
    archivos = {s: open(out / f"{s}.jsonl", "w", encoding="utf-8") for s in ("dev", "test")}
    for k in range(a.n):
        i = k % len(PLANTILLAS)
        esc, pl = PLANTILLAS[i]
        texto, etq = rellenar(pl, g)
        reg = {"id": f"sint-{k:04d}", "text": texto, "label": etq,
               "meta": {"fuente": "sintetico", "escenario": esc, "plantilla": i, "split": split[i]}}
        archivos[split[i]].write(json.dumps(reg, ensure_ascii=False) + "\n")
    for f in archivos.values():
        f.close()
    print({s: sum(1 for _ in open(out / f"{s}.jsonl", encoding="utf-8")) for s in archivos})


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    main()
