"""Prueba de no persistencia del proxy (proxy/servidor.py).

Comprueba que, mientras procesa prompts, el proxy no escribe archivos ni deja
su contenido en registros (logs). No mide la detección: solo el tratamiento
de los datos que declara la sección 7.5.

La IA se sustituye por un servicio simulado local, al que el cliente oficial
de OpenAI se conecta mediante OPENAI_BASE_URL; no se llama a ninguna API
externa. El servicio simulado guarda en memoria lo que recibe para comprobar
que cada solicitud lleva store=False.

Mientras se procesan las solicitudes se comprueba:
  1. Escrituras: un audit hook de Python (sys.addaudithook) registra toda
     apertura de un archivo en modo de escritura, creación o adición y toda
     operación que cree, renombre o borre archivos o carpetas.
  2. Archivos: se compara una instantánea (ruta, tamaño y fecha de
     modificación) del repositorio, del directorio de trabajo y del
     directorio temporal antes y después de las solicitudes.
  3. Registros: se capturan los registros de logging con la configuración
     por defecto y la salida estándar y de error, y se busca en ellos el
     texto de cada prompt y el valor de cada entidad anotada.
La carga del modelo y una solicitud de calentamiento ocurren antes de activar
los controles, porque solo se evalúa el procesamiento de los prompts.

Uso:
  python scripts/prueba_no_persistencia.py --backend hf --modelo modelos/ner-bert-final \
      --datos datos/sintetico/test.jsonl datos/doccano/prueba.jsonl
  -> resultados/no_persistencia/resumen.json (solo conteos, sin el contenido de los prompts)
"""
import argparse
import contextlib
import io
import json
import logging
import os
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

FLAGS_ESCRITURA = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC
EVENTOS_ARCHIVO = {"os.remove", "os.rename", "os.mkdir", "os.rmdir", "os.truncate", "os.symlink",
                   "os.link", "shutil.copyfile", "shutil.copytree", "shutil.move", "shutil.rmtree"}
escrituras = []
controles_activos = False


def auditar(evento, args):
    if not controles_activos:
        return
    if evento == "open":
        ruta, modo, flags = args
        if (isinstance(modo, str) and any(c in modo for c in "wax+")) or \
           (modo is None and isinstance(flags, int) and flags & FLAGS_ESCRITURA):
            escrituras.append({"evento": evento, "ruta": str(ruta)})
    elif evento in EVENTOS_ARCHIVO:
        escrituras.append({"evento": evento, "ruta": str(args[0])})


def instantanea(carpetas):
    estado = {}
    for c in carpetas:
        for raiz, _, archivos in os.walk(c):
            for a in archivos:
                p = os.path.join(raiz, a)
                try:
                    st = os.stat(p)
                    estado[p] = (st.st_size, st.st_mtime_ns)
                except OSError:
                    pass
    return estado


class ServicioSimulado(BaseHTTPRequestHandler):
    """Responde como la API Responses de OpenAI y guarda en memoria lo recibido."""
    recibido = []

    def do_POST(self):  # noqa: N802
        cuerpo = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        ServicioSimulado.recibido.append(cuerpo)
        r = json.dumps({"id": "resp_simulada", "object": "response", "created_at": 0, "status": "completed",
                        "model": cuerpo.get("model"), "output": [{
                            "type": "message", "id": "msg_simulado", "role": "assistant", "status": "completed",
                            "content": [{"type": "output_text", "text": "respuesta simulada", "annotations": []}]}],
                        "parallel_tool_calls": False, "tool_choice": "auto", "tools": []}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(r)))
        self.end_headers()
        self.wfile.write(r)

    def log_message(self, *args):  # el servicio simulado tampoco registra nada
        pass


def cargar(ruta):
    docs = []
    for linea in open(ruta, encoding="utf-8"):
        d = json.loads(linea)
        etq = d.get("label") or d.get("labels") or d.get("entities") or []
        if etq and isinstance(etq[0], dict):
            etq = [[e["start_offset"], e["end_offset"], e["label"]] for e in etq]
        docs.append((d["text"], [d["text"][s:e].strip() for s, e, *_ in etq]))
    return docs


def main():
    global controles_activos
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="hf")
    ap.add_argument("--modelo", default="modelos/ner-bert-final")
    ap.add_argument("--datos", nargs="+", default=["datos/sintetico/test.jsonl", "datos/doccano/prueba.jsonl"])
    ap.add_argument("--salida", default="resultados/no_persistencia")
    a = ap.parse_args()

    servidor_ia = ThreadingHTTPServer(("127.0.0.1", 0), ServicioSimulado)
    threading.Thread(target=servidor_ia.serve_forever, daemon=True).start()
    os.environ["OPENAI_BASE_URL"] = f"http://127.0.0.1:{servidor_ia.server_port}/v1"
    os.environ["OPENAI_API_KEY"] = "clave-ficticia"
    os.environ["NO_PROXY"] = ",".join(filter(None, [os.environ.get("NO_PROXY"), "127.0.0.1", "localhost"]))
    os.environ["no_proxy"] = os.environ["NO_PROXY"]
    os.environ["NER_BACKEND"] = a.backend
    if a.backend == "hf":
        os.environ["NER_MODELO"] = str(Path(a.modelo).resolve())

    sys.path.insert(0, str(RAIZ))
    import proxy.servidor as servidor
    from fastapi.testclient import TestClient
    cliente = TestClient(servidor.app)
    cliente.post("/v1/prompt", json={"prompt": "Hola, soy Ana Gómez.", "enviar": True})  # calentamiento
    ServicioSimulado.recibido.clear()

    docs = [d for ruta in a.datos for d in cargar(RAIZ / ruta)]
    carpetas = sorted({str(RAIZ), os.getcwd(), tempfile.gettempdir()})
    capturado = io.StringIO()
    manejador = logging.StreamHandler(capturado)
    manejador.setLevel(logging.NOTSET)
    logging.getLogger().addHandler(manejador)
    salida, error = io.StringIO(), io.StringIO()
    sys.addaudithook(auditar)

    antes = instantanea(carpetas)
    respuestas = []
    controles_activos = True
    with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(error):
        for texto, _ in docs:
            respuestas.append(cliente.post("/v1/prompt", json={"prompt": texto, "enviar": True}).json())
    controles_activos = False
    despues = instantanea(carpetas)
    logging.getLogger().removeHandler(manejador)

    cambios = sorted(p for p in set(antes) | set(despues) if antes.get(p) != despues.get(p))
    registros = capturado.getvalue() + salida.getvalue() + error.getvalue()
    valores = [v for texto, ents in docs for v in [texto, *ents] if len(v) >= 3]
    en_registros = sum(v in registros for v in valores)
    recibido = ServicioSimulado.recibido
    resumen = {
        "ner_backend": a.backend, "conjuntos": a.datos, "prompts": len(docs),
        "carpetas_vigiladas": len(carpetas), "archivos_vigilados": len(antes),
        "aperturas_en_escritura_u_operaciones_de_archivo": len(escrituras),
        "archivos_creados_o_modificados": len(cambios),
        "caracteres_registrados_en_logs_stdout_stderr": len(registros),
        "valores_buscados": len(valores), "valores_encontrados_en_registros": en_registros,
        "solicitudes_al_servicio_simulado": len(recibido),
        "solicitudes_con_store_false": sum(r.get("store") is False for r in recibido),
        "respuestas_con_error_ia": sum("error_ia" in r for r in respuestas),
    }
    resumen["sin_persistencia"] = (not escrituras and not cambios and not registros
                                   and len(recibido) == len(docs) == resumen["solicitudes_con_store_false"]
                                   and not resumen["respuestas_con_error_ia"])
    if escrituras or cambios:  # solo rutas, nunca contenido
        resumen["detalle_rutas"] = sorted({e["ruta"] for e in escrituras} | set(cambios))[:50]
    out = RAIZ / a.salida
    out.mkdir(parents=True, exist_ok=True)
    (out / "resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False, indent=1))
    servidor_ia.shutdown()


if __name__ == "__main__":
    main()
