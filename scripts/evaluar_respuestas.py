"""Efecto del enmascaramiento sobre la respuesta (segunda dimensión).

Para cada prompt enmascarado por el mecanismo se piden a la IA dos
respuestas: con el prompt original y con el enmascarado. La métrica es la
similitud coseno entre los embeddings de oraciones de ambas respuestas
(Reimers & Gurevych, 2019). Como la IA no es determinista, también se pide
una segunda respuesta al prompt original: sim(original, original') es el
piso de variación propia del modelo, contra el que se lee el efecto.

Solo se usan prompts sintéticos o públicos: el prompt original nunca debe
contener datos reales (sección 5).

Requiere OPENAI_API_KEY. Se evalúan dos modelos por la API, con store=False:
- gpt-6-luna, el modelo predeterminado de ChatGPT para los planes Free y Go
  desde el 7 de octubre de 2026 (notas de versión de ChatGPT). No tiene una
  versión fija: el script registra la fecha y el identificador que devuelve la API.
- gpt-5-mini, versión fija de referencia.
(Antes se usaba el alias "chat-latest", que desde el 7 de octubre de 2026 apunta
al modelo de los planes de pago y no al del plan gratuito.)
Temperatura: se pide 0; si el modelo no admite el parámetro (los de
razonamiento GPT-5 no lo admiten) se usa el valor predeterminado y se
registra así.
Embeddings: sentence-transformers/paraphrase-multilingual-mpnet-base-v2.

Uso:
  python scripts/evaluar_respuestas.py --salidas resultados/sintetico_test_final/salidas_hibrido_heuristica.jsonl \
      --modelos gpt-6-luna gpt-5-mini --n 60
"""
import argparse
import json
import random
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


ADMITE_TEMPERATURA = {}  # modelo -> bool, se descubre en la primera llamada


def responder(cliente, modelo, texto, intentos=4):
    """Devuelve (texto de la respuesta, identificador de versión del modelo)."""
    import openai
    for k in range(intentos):
        kwargs = {"model": modelo, "input": texto, "store": False}
        if ADMITE_TEMPERATURA.get(modelo, True):
            kwargs["temperature"] = 0
        try:
            r = cliente.responses.create(**kwargs)
            ADMITE_TEMPERATURA.setdefault(modelo, "temperature" in kwargs)
            return r.output_text, r.model
        except openai.BadRequestError as e:
            if "temperature" in kwargs and "temperature" in str(e).lower():
                ADMITE_TEMPERATURA[modelo] = False  # reintenta sin temperatura
                continue
            raise
        except (openai.NotFoundError, openai.AuthenticationError, openai.PermissionDeniedError):
            raise  # modelo inexistente o clave inválida: reintentar no sirve
        except Exception as e:  # límites de tasa / red
            if k == intentos - 1:
                raise
            time.sleep(2 ** (k + 1))
            print("reintento:", type(e).__name__)
    raise RuntimeError("sin respuesta")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salidas", required=True, help="salidas_<sistema>.jsonl de evaluar_deteccion.py")
    ap.add_argument("--modelos", nargs="+", default=["gpt-6-luna", "gpt-5-mini"])
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--embeddings", default="sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
    ap.add_argument("--semilla", type=int, default=13)
    ap.add_argument("--no-guardar-respuestas", action="store_true",
                    help="no conservar los textos de las respuestas, solo las métricas")
    a = ap.parse_args()

    from datetime import datetime, timezone

    from openai import OpenAI
    from sentence_transformers import SentenceTransformer, util

    filas = [json.loads(l) for l in open(a.salidas, encoding="utf-8")]
    filas = [f for f in filas if f["decision"]["accion"] == "ENMASCARAR"]
    random.Random(a.semilla).shuffle(filas)
    filas = filas[:a.n]

    cliente = OpenAI()
    emb = SentenceTransformer(a.embeddings)
    out = Path(a.salidas).parent
    resumenes = {}
    for modelo in a.modelos:
        fecha = datetime.now(timezone.utc).isoformat(timespec="seconds")
        resultados, versiones = [], set()
        for i, f in enumerate(filas, 1):
            r_orig, v1 = responder(cliente, modelo, f["texto"])
            r_orig2, v2 = responder(cliente, modelo, f["texto"])
            r_masc, v3 = responder(cliente, modelo, f["texto_enviado"])
            versiones |= {v1, v2, v3}
            v = emb.encode([r_orig, r_orig2, r_masc], convert_to_tensor=True, normalize_embeddings=True)
            fila = {"id": f["id"], "sim_original_vs_enmascarado": float(util.cos_sim(v[0], v[2])),
                    "sim_original_vs_original": float(util.cos_sim(v[0], v[1])),
                    "marcadores_en_respuesta": sum(r_masc.count(f"[{e}]") for e in
                                                   {p["etiqueta"] for p in f["pred"]})}
            if not a.no_guardar_respuestas:
                fila.update({"prompt_enmascarado": f["texto_enviado"], "respuesta_original": r_orig,
                             "respuesta_original_2": r_orig2, "respuesta_enmascarada": r_masc})
            resultados.append(fila)
            print(f"[{modelo}] {i}/{len(filas)} sim={fila['sim_original_vs_enmascarado']:.3f} "
                  f"piso={fila['sim_original_vs_original']:.3f}")

        sufijo = modelo.replace("/", "_")
        with open(out / f"respuestas_{sufijo}.jsonl", "w", encoding="utf-8") as fh:
            for r in resultados:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        s1 = [r["sim_original_vs_enmascarado"] for r in resultados]
        s0 = [r["sim_original_vs_original"] for r in resultados]
        est = lambda xs: {"media": statistics.mean(xs), "mediana": statistics.median(xs),  # noqa: E731
                          "desv": statistics.pstdev(xs), "min": min(xs)}
        resumenes[modelo] = {
            "n": len(resultados), "fecha_ejecucion_utc": fecha, "versiones_api": sorted(versiones),
            "temperatura": 0 if ADMITE_TEMPERATURA.get(modelo) else "predeterminada (no admite el parámetro)",
            "embeddings": a.embeddings,
            "sim_original_vs_enmascarado": est(s1), "sim_original_vs_original": est(s0),
            "respuestas_con_marcadores": sum(r["marcadores_en_respuesta"] > 0 for r in resultados)}

    json.dump(resumenes, open(out / "respuestas_resumen.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps(resumenes, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
