"""Acuerdo entre anotadores (Andrés y un segundo anotador) sobre la muestra de validación cruzada.

Entradas: datos/acuerdo/referencia_andres.jsonl y el export de Doccano del
proyecto del asesor. Las filas se emparejan por id_origen (en la raíz o en
meta) y, si falta, por el texto normalizado. A las etiquetas del asesor se les aplica el
mismo recorte de bordes que a las de Andrés (particionar_doccano.recortar).

Métricas:
  - Kappa de Cohen por token con etiquetas BIO (todas las etiquetas y O).
  - Kappa de Cohen por token solo sobre los tokens que al menos un anotador
    marcó (evita que la mayoría de O infle el acuerdo).
  - Acuerdo por mención: F1 estricto (mismo span y etiqueta) y parcial
    (solapamiento y misma etiqueta) tomando a Andrés como referencia; el F1 es
    simétrico, así que no depende de quién se tome como referencia.
  - Matriz de confusión por token entre etiquetas.

Uso: python scripts/acuerdo_anotadores.py --asesor ruta\\export_asesor.jsonl
  -> resultados/acuerdo_anotadores/{acuerdo.json, acuerdo.md}
"""
import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from particionar_doccano import recortar  # noqa: E402

TOKEN = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def clave(texto):
    """Texto normalizado para emparejar filas aunque Doccano cambie ids o saltos de línea."""
    return texto.replace("\r\n", "\n").strip()


def etiquetas(d):
    etq = d.get("label") or d.get("entities") or []
    if etq and isinstance(etq[0], dict):
        etq = [[x["start_offset"], x["end_offset"], x["label"]] for x in etq]
    return [list(x[:3]) for x in etq]


def bio(texto, spans):
    out = []
    for m in TOKEN.finditer(texto):
        t = "O"
        for s, e, l in spans:
            if m.start() < e and m.end() > s:
                t = ("B-" if m.start() <= s else "I-") + l
                break
        out.append(t)
    return out


def kappa(a, b):
    n = len(a)
    if not n:
        return float("nan")
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in ca) / (n * n)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    return {"P": p, "R": r, "F1": 2 * p * r / (p + r) if p + r else 0.0, "tp": tp, "fp": fp, "fn": fn}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--referencia", default="datos/acuerdo/referencia_andres.jsonl")
    ap.add_argument("--asesor", required=True)
    ap.add_argument("--salida", default="resultados/acuerdo_anotadores")
    ap.add_argument("--nombre", default="segundo anotador", help="cómo se nombra al segundo anotador en el informe")
    a = ap.parse_args()

    ref = [json.loads(l) for l in open(a.referencia, encoding="utf-8") if l.strip()]
    por_id, por_texto = {}, {}
    for l in open(a.asesor, encoding="utf-8"):
        if not l.strip():
            continue
        d = json.loads(l)
        io = d.get("id_origen", (d.get("meta") or {}).get("id_origen"))
        spans, _ = recortar(d["text"], etiquetas(d))
        if io is not None:
            por_id[io] = spans
        por_texto[clave(d["text"])] = spans

    ta, tb, ta_m, tb_m = [], [], [], []
    menc = {"estricto": defaultdict(lambda: [0, 0, 0]), "parcial": defaultdict(lambda: [0, 0, 0])}
    faltan = 0
    for r in ref:
        sb = por_id.get(r["id_origen"], por_texto.get(clave(r["text"])))
        if sb is None:
            faltan += 1
            continue
        sa = r["label"]
        ba, bb = bio(r["text"], sa), bio(r["text"], sb)
        ta += ba
        tb += bb
        for x, y in zip(ba, bb):
            if x != "O" or y != "O":
                ta_m.append(x)
                tb_m.append(y)
        A, B = {tuple(s) for s in sa}, {tuple(s) for s in sb}
        for s in A:
            menc["estricto"][s[2]][0 if s in B else 2] += 1
        for s in B - A:
            menc["estricto"][s[2]][1] += 1
        sol = lambda s, X: any(t[2] == s[2] and t[0] < s[1] and t[1] > s[0] for t in X)
        for s in A:
            menc["parcial"][s[2]][0 if sol(s, B) else 2] += 1
        for s in B:
            if not sol(s, A):
                menc["parcial"][s[2]][1] += 1

    plano = lambda t: [x[2:] if x != "O" else "O" for x in t]
    conf = Counter(zip(plano(ta), plano(tb)))
    res = {
        "textos": len(ref) - faltan, "sin_pareja": faltan, "tokens": len(ta),
        "kappa_token_bio": kappa(ta, tb),
        "kappa_tokens_marcados": kappa(ta_m, tb_m), "tokens_marcados": len(ta_m),
        "menciones": {m: {**{e: prf(*v) for e, v in sorted(c.items())},
                          "micro": prf(*[sum(v[i] for v in c.values()) for i in range(3)])}
                      for m, c in menc.items()},
        "confusion_token": {f"{x}|{y}": n for (x, y), n in conf.most_common() if x != y},
    }
    out = Path(a.salida)
    out.mkdir(parents=True, exist_ok=True)
    (out / "acuerdo.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    f = lambda v: f"{v:.3f}"
    md = [f"# Acuerdo entre anotadores (Andrés y {a.nombre})", "",
          f"Textos emparejados: {res['textos']} (sin pareja: {faltan}); tokens: {res['tokens']}.", "",
          "| Medida | Valor |", "|---|---|",
          f"| Kappa de Cohen por token (BIO, incluye O) | {f(res['kappa_token_bio'])} |",
          f"| Kappa de Cohen sobre tokens marcados por alguno ({len(ta_m)}) | {f(res['kappa_tokens_marcados'])} |",
          f"| F1 por mención, estricto | {f(res['menciones']['estricto']['micro']['F1'])} |",
          f"| F1 por mención, parcial | {f(res['menciones']['parcial']['micro']['F1'])} |", "",
          "## F1 por mención y etiqueta (estricto / parcial)", "",
          f"| Etiqueta | Andrés | {a.nombre.capitalize()} | Coinciden (estricto) | F1 estricto | F1 parcial |", "|---|---|---|---|---|---|"]
    for e, v in res["menciones"]["estricto"].items():
        if e == "micro":
            continue
        p = res["menciones"]["parcial"][e]
        md.append(f"| {e} | {v['tp'] + v['fn']} | {v['tp'] + v['fp']} | {v['tp']} | {f(v['F1'])} | {f(p['F1'])} |")
    md += ["", f"## Desacuerdos por token más frecuentes (Andrés | {a.nombre})", "", "| Par | Tokens |", "|---|---|"]
    md += [f"| {k} | {n} |" for k, n in list(res["confusion_token"].items())[:15]]
    (out / "acuerdo.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
