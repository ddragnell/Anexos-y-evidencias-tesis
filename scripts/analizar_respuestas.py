"""Análisis complementario del efecto del enmascaramiento sobre la respuesta.

Se ejecuta después de scripts/evaluar_respuestas.py, sobre las respuestas que
ese script guardó; no hace llamadas a la IA.

1. Dispersión: para cada prompt calcula la diferencia entre la similitud de las
   dos respuestas al prompt original (variación propia) y la similitud entre la
   respuesta original y la enmascarada, y reporta su media, desviación estándar,
   cuartiles, mínimo, máximo y cuántas diferencias son menores o iguales a cero.
2. Efecto mecánico: como el modelo conserva los marcadores («Estimado [PER]»),
   parte de la caída se debe solo a que la respuesta enmascarada dice [PER] donde
   la original dice el nombre. Para separarlo, en las dos respuestas originales
   se reemplazan las mismas entidades que se enmascararon en el prompt por sus
   marcadores (en PER, también cada palabra del nombre por separado, porque la
   respuesta suele usar solo el nombre de pila) y se recalculan ambas similitudes.

Uso:
  python scripts/analizar_respuestas.py --salidas resultados/sintetico_test_final/salidas_hibrido_heuristica.jsonl \
      --modelos gpt-6-luna gpt-5-mini
  -> respuestas_analisis.json y respuestas_analisis_por_prompt.jsonl en la carpeta de las salidas
"""
import argparse
import json
import re
import statistics
from pathlib import Path


def marcar(texto, entidades):
    """Reemplaza en texto los valores de las entidades por su marcador tipado."""
    pares = [(e["texto"], e["etiqueta"]) for e in entidades if e["texto"].strip()]
    for e in entidades:  # palabras sueltas de los nombres de persona
        if e["etiqueta"] == "PER":
            pares += [(w, "PER") for w in e["texto"].split() if len(w) >= 3 and w[:1].isupper()]
    n = 0
    for valor, etq in sorted(set(pares), key=lambda p: -len(p[0])):
        texto, k = re.subn(r"(?<!\w)" + re.escape(valor) + r"(?!\w)", f"[{etq}]", texto)
        n += k
    return texto, n


MARCADOR = re.compile(r"\[[A-Z_/ ]+\]")


def grupo(prompt_enmascarado):
    return "1-2" if len(MARCADOR.findall(prompt_enmascarado)) <= 2 else "3+"


def resumen(xs):
    q = statistics.quantiles(xs, n=4)
    return {"media": statistics.mean(xs), "desv": statistics.stdev(xs), "q1": q[0], "mediana": q[1], "q3": q[2],
            "min": min(xs), "max": max(xs), "n_menor_o_igual_a_cero": sum(x <= 0 for x in xs)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salidas", required=True, help="el mismo archivo usado en evaluar_respuestas.py")
    ap.add_argument("--modelos", nargs="+", default=["gpt-6-luna", "gpt-5-mini"])
    ap.add_argument("--embeddings", default="sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
    a = ap.parse_args()

    from sentence_transformers import SentenceTransformer, util
    emb = SentenceTransformer(a.embeddings)
    entidades = {json.loads(l)["id"]: json.loads(l)["pred"] for l in open(a.salidas, encoding="utf-8")}
    carpeta = Path(a.salidas).parent
    salida, filas_por_prompt = {}, []
    for modelo in a.modelos:
        filas = [json.loads(l) for l in open(carpeta / f"respuestas_{modelo.replace('/', '_')}.jsonl", encoding="utf-8")]
        dif, dif_aj, s_om_aj, s_oo_aj, reemplazos, por_prompt = [], [], [], [], [], []
        for f in filas:
            ents = entidades[f["id"]]
            o1, n1 = marcar(f["respuesta_original"], ents)
            o2, _ = marcar(f["respuesta_original_2"], ents)
            v = emb.encode([o1, o2, f["respuesta_enmascarada"]], convert_to_tensor=True, normalize_embeddings=True)
            om, oo = float(util.cos_sim(v[0], v[2])), float(util.cos_sim(v[0], v[1]))
            dif.append(f["sim_original_vs_original"] - f["sim_original_vs_enmascarado"])
            s_om_aj.append(om)
            s_oo_aj.append(oo)
            dif_aj.append(oo - om)
            reemplazos.append(n1)
            por_prompt.append({"modelo": modelo, "id": f["id"], "grupo": grupo(f["prompt_enmascarado"]),
                               "sim_original_vs_original": f["sim_original_vs_original"],
                               "sim_original_vs_enmascarado": f["sim_original_vs_enmascarado"],
                               "sim_original_marcada_vs_original_2_marcada": oo,
                               "sim_original_marcada_vs_enmascarado": om})
        salida[modelo] = {
            "n": len(filas),
            "diferencia": resumen(dif),
            "con_marcadores_en_la_original": {
                "sim_original_marcada_vs_enmascarado": resumen(s_om_aj),
                "sim_original_marcada_vs_original_2_marcada": resumen(s_oo_aj),
                "diferencia": resumen(dif_aj),
                "respuestas_originales_con_reemplazos": sum(n > 0 for n in reemplazos),
            },
            "por_marcadores": {},
        }
        for g in ("1-2", "3+"):
            fs = [x for x in por_prompt if x["grupo"] == g]
            media = lambda k: statistics.mean(x[k] for x in fs)  # noqa: E731
            salida[modelo]["por_marcadores"][g] = {
                "n": len(fs),
                "sim_original_vs_original": media("sim_original_vs_original"),
                "sim_original_vs_enmascarado": media("sim_original_vs_enmascarado"),
                "sim_original_marcada_vs_original_2_marcada": media("sim_original_marcada_vs_original_2_marcada"),
                "sim_original_marcada_vs_enmascarado": media("sim_original_marcada_vs_enmascarado"),
            }
        filas_por_prompt.extend(por_prompt)
    with open(carpeta / "respuestas_analisis_por_prompt.jsonl", "w", encoding="utf-8") as fh:
        for x in filas_por_prompt:
            fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    (carpeta / "respuestas_analisis.json").write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(salida, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
