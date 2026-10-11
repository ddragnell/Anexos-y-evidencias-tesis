"""Prueba de extremo a extremo del proxy (proxy/servidor.py) con el modelo final.

Verifica la integración, no es una evaluación nueva: no recalcula métricas.
Cada prompt se envía al endpoint /v1/prompt con FastAPI TestClient y se comprueba
que lo que el proxy entrega a la IA sea exactamente el texto enmascarado que ya
se evaluó (salidas_hibrido_heuristica.jsonl del conjunto) y que la decisión
coincida.

La IA se sustituye por un upstream simulado que registra el texto que recibe y
responde un texto fijo; no se llama a ninguna API. Se hacen dos pasadas:
  enviar=True   el proxy llama al upstream simulado: se compara lo que este
                recibió con el texto_enviado evaluado.
  enviar=False  el proxy solo devuelve el análisis: se compara el
                texto_enviado y la decisión de la respuesta.
La latencia es la del ciclo completo de la solicitud (cliente -> proxy ->
mecanismo -> upstream simulado -> cliente), por prompt, sin la primera
solicitud de calentamiento.

Uso:
  python scripts/prueba_proxy_e2e.py --modelo modelos/ner-bert-final \
      --conjunto resultados/sintetico_test_final resultados/doccano_prueba_final
  -> resultados/proxy_e2e/{resumen.json, resumen.md, detalle_<conjunto>.jsonl}
"""
import argparse
import json
import os
import platform
import statistics
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def hardware():
    info = {"python": platform.python_version(), "sistema": platform.platform(),
            "cpu": platform.processor() or platform.machine(), "nucleos": os.cpu_count()}
    try:
        import torch
        info["torch"] = torch.__version__
        info["gpu"] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
    except Exception:  # noqa: BLE001
        info["gpu"] = None
    try:
        with open("/proc/cpuinfo") as f:
            nombre = next((l.split(":", 1)[1].strip() for l in f if l.startswith("model name")), None)
        if nombre:
            info["cpu"] = nombre
    except OSError:
        pass
    return info


def percentil(xs, p):
    xs = sorted(xs)
    k = (len(xs) - 1) * p
    i = int(k)
    return xs[i] if i + 1 >= len(xs) else xs[i] + (xs[i + 1] - xs[i]) * (k - i)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default="modelos/ner-bert-final")
    ap.add_argument("--conjunto", nargs="+",
                    default=["resultados/sintetico_test_final", "resultados/doccano_prueba_final"])
    ap.add_argument("--backend", default="hf")
    ap.add_argument("--salida", default="resultados/proxy_e2e")
    a = ap.parse_args()

    os.environ["NER_BACKEND"] = a.backend
    if a.backend == "hf":
        os.environ["NER_MODELO"] = str(Path(a.modelo).resolve())
    sys.path.insert(0, str(RAIZ))
    t0 = time.perf_counter()
    import proxy.servidor as servidor
    from fastapi.testclient import TestClient
    carga = time.perf_counter() - t0

    recibido = []

    def upstream_simulado(texto, modelo=servidor.MODELO_IA):
        recibido.append(texto)
        return "respuesta simulada"

    servidor.llamar_ia = upstream_simulado
    cliente = TestClient(servidor.app)
    cliente.post("/v1/prompt", json={"prompt": "Hola, soy Ana Gómez.", "enviar": False})  # calentamiento
    recibido.clear()

    out = RAIZ / a.salida
    out.mkdir(parents=True, exist_ok=True)
    hw = hardware()
    if a.backend == "hf":
        hw["dispositivo_ner"] = str(servidor.mecanismo.ner.nlp.device)
    resumen = {"hardware": hw, "ner": {"backend": a.backend, "modelo": a.modelo},
               "carga_modelo_s": round(carga, 2), "conjuntos": {}}
    todas = {"enviar": [], "analisis": []}
    for c in a.conjunto:
        nombre = Path(c).name
        filas = [json.loads(l) for l in open(RAIZ / c / "salidas_hibrido_heuristica.jsonl", encoding="utf-8")]
        lat = {"enviar": [], "analisis": []}
        ok = {"upstream": 0, "respuesta": 0, "decision": 0, "analisis_texto": 0, "analisis_decision": 0}
        n_enmasc = 0
        with open(out / f"detalle_{nombre}.jsonl", "w", encoding="utf-8") as f:
            for r in filas:
                esperado, accion = r["texto_enviado"], r["decision"]["accion"]
                n_enmasc += accion == "ENMASCARAR"
                recibido.clear()
                t = time.perf_counter()
                resp = cliente.post("/v1/prompt", json={"prompt": r["texto"], "enviar": True}).json()
                lat["enviar"].append((time.perf_counter() - t) * 1000)
                t = time.perf_counter()
                resp2 = cliente.post("/v1/prompt", json={"prompt": r["texto"], "enviar": False}).json()
                lat["analisis"].append((time.perf_counter() - t) * 1000)
                fila = {
                    "id": r["id"],
                    "upstream_igual": len(recibido) == 1 and recibido[0] == esperado,
                    "respuesta_igual": resp["texto_enviado"] == esperado,
                    "decision_igual": resp["decision"]["accion"] == accion,
                    "analisis_texto_igual": resp2["texto_enviado"] == esperado,
                    "analisis_decision_igual": resp2["decision"]["accion"] == accion,
                    "respuesta_upstream": resp.get("respuesta"),
                    "ms_enviar": round(lat["enviar"][-1], 1), "ms_analisis": round(lat["analisis"][-1], 1),
                }
                if not fila["upstream_igual"]:
                    fila["esperado"], fila["recibido_upstream"] = esperado, recibido[:1]
                for k, campo in (("upstream", "upstream_igual"), ("respuesta", "respuesta_igual"),
                                 ("decision", "decision_igual"), ("analisis_texto", "analisis_texto_igual"),
                                 ("analisis_decision", "analisis_decision_igual")):
                    ok[k] += fila[campo]
                f.write(json.dumps(fila, ensure_ascii=False) + "\n")
        for k in lat:
            todas[k] += lat[k]
        resumen["conjuntos"][nombre] = {
            "prompts": len(filas), "enmascarados": n_enmasc, "coincidencias": ok,
            "latencia_ms": {k: {"mediana": round(statistics.median(v), 1), "p95": round(percentil(v, 0.95), 1),
                                "max": round(max(v), 1)} for k, v in lat.items()},
        }
    resumen["latencia_ms_total"] = {k: {"mediana": round(statistics.median(v), 1),
                                        "p95": round(percentil(v, 0.95), 1)} for k, v in todas.items()}
    (out / "resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")

    md = ["# Prueba de extremo a extremo del proxy", "",
          f"NER: {a.backend} `{a.modelo if a.backend == 'hf' else 'es_core_news_sm'}`. Upstream simulado (no se llama a ninguna API). "
          f"Hardware: {hw['cpu']} ({hw['nucleos']} núcleos)"
          + (f", GPU {hw['gpu']}" if hw.get("gpu") else ", sin GPU")
          + (f", NER en {hw['dispositivo_ner']}" if hw.get("dispositivo_ner") else "") + f"; Python {hw['python']}.",
          f"Carga del proxy y del modelo: {resumen['carga_modelo_s']} s.", "",
          "| Conjunto | Prompts | Enmascarados | Texto recibido por el upstream = texto evaluado | "
          "Decisión igual | Respuesta enviar=False igual | Latencia mediana (ms) | Latencia p95 (ms) |",
          "|---|---|---|---|---|---|---|---|"]
    for nombre, v in resumen["conjuntos"].items():
        c, n, l_ = v["coincidencias"], v["prompts"], v["latencia_ms"]["enviar"]
        md.append(f"| {nombre} | {n} | {v['enmascarados']} | {c['upstream']}/{n} | {c['decision']}/{n} | "
                  f"{min(c['analisis_texto'], c['analisis_decision'])}/{n} | {l_['mediana']} | {l_['p95']} |")
    t = resumen["latencia_ms_total"]
    md += ["", f"Latencia sobre todos los prompts: con upstream simulado mediana {t['enviar']['mediana']} ms, "
           f"p95 {t['enviar']['p95']} ms; solo análisis (enviar=False) mediana {t['analisis']['mediana']} ms, "
           f"p95 {t['analisis']['p95']} ms. Es la latencia que agrega el proxy antes de la llamada a la IA."]
    (out / "resumen.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
