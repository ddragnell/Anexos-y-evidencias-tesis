"""Proxy de intermediación.

Recibe el prompt, ejecuta el mecanismo (detección híbrida + heurística +
enmascaramiento) y reenvía a la IA generativa solo el texto resultante.
No persiste nada: no escribe prompts, entidades ni respuestas en disco ni
en logs, y la llamada a OpenAI se hace con store=False. No restituye las
entidades: si la IA responde "Estimado [PER]", el usuario recibe eso.

Ejecutar:
  set OPENAI_API_KEY=...            (Windows)   /   export OPENAI_API_KEY=...
  uvicorn proxy.servidor:app --port 8000
  Por defecto usa el NER final (NER_BACKEND=hf, NER_MODELO=modelos/ner-bert-final).
  (respaldo sin BERT) set NER_BACKEND=spacy

Demostración: abrir http://localhost:8000/ (página proxy/demo.html).

Probar:
  curl -X POST localhost:8000/v1/prompt -H "Content-Type: application/json" \
       -d "{\"prompt\": \"Redacta un correo para Ana Gómez, CC 1.036.456.789\"}"
"""
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi import FastAPI  # noqa: E402
from fastapi.responses import HTMLResponse  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from mecanismo.mecanismo import Mecanismo  # noqa: E402
from mecanismo.ner_detector import DetectorNER  # noqa: E402

logging.getLogger("uvicorn.access").disabled = True  # sin trazas de las solicitudes

MODELO_IA = os.getenv("MODELO_IA", "gpt-5-mini")
NER_BACKEND = os.getenv("NER_BACKEND", "hf")
NER_MODELO = os.getenv("NER_MODELO", str(Path(__file__).resolve().parents[1] / "modelos" / "ner-bert-final")
                       if NER_BACKEND == "hf" else None)
# mecanismo completo: detección híbrida + heurística + enmascaramiento
mecanismo = Mecanismo("hibrido", ner=DetectorNER(NER_BACKEND, NER_MODELO))
app = FastAPI(title="Proxy preventivo de información sensible")


class Solicitud(BaseModel):
    prompt: str
    enviar: bool = True   # False: solo devuelve el análisis, sin llamar a la IA


def llamar_ia(texto: str, modelo: str = MODELO_IA) -> str:
    from openai import OpenAI
    cliente = OpenAI()
    r = cliente.responses.create(model=modelo, input=texto, store=False)
    return r.output_text


@app.post("/v1/prompt")
def procesar(s: Solicitud):
    r = mecanismo.procesar(s.prompt)
    salida = {
        "decision": r["decision"],
        # al cliente solo se le informa el tipo de cada entidad, no su valor
        "entidades": [e.etiqueta for e in r["entidades"]],
        "texto_enviado": r["texto_enviado"],
    }
    if s.enviar:
        try:
            salida["respuesta"] = llamar_ia(r["texto_enviado"])
        except Exception as e:  # noqa: BLE001  sin clave, sin red, etc.: el análisis igual se devuelve
            salida["error_ia"] = type(e).__name__
    return salida


@app.get("/", response_class=HTMLResponse)
def demo():
    """Página de demostración: escribe un prompt y muestra la decisión y el texto enviado."""
    return (Path(__file__).resolve().parent / "demo.html").read_text(encoding="utf-8")
