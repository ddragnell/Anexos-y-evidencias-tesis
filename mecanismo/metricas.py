"""Métricas de la dimensión detección y protección (sección 6.2.6, Tabla 5).

Detección, por etiqueta, agregada (micro) y agregada sobre los
identificadores directos y secretos ("directas", criterio de la sección 7.4):
- P, R, F1 y F2 a nivel de entidad. "estricto": mismo span y etiqueta.
  "parcial": mismo tipo y solapamiento de al menos un carácter.
Protección, sobre el texto que realmente se envía:
- ER_di / ER_qi (TAB, Pilán et al., 2022): proporción de menciones de
  referencia de identificadores directos / cuasi-identificadores que
  quedaron completamente enmascaradas, con cualquier marcador.
- WP: precisión de enmascaramiento a nivel de carácter (qué parte de lo
  enmascarado era información de referencia). TAB pondera cada token por
  su contenido informativo; aquí se usan pesos uniformes.
- Fuga residual (PII Leak Rate, Asiri et al., 2025): proporción de
  entidades de referencia cuyo texto sigue apareciendo literalmente en el
  texto enviado.
"""
from collections import defaultdict

from .taxonomia import CUASI, DIRECTAS, ETIQUETAS


def fbeta(p, r, beta):
    return 0.0 if p + r == 0 else (1 + beta ** 2) * p * r / (beta ** 2 * p + r)


def _prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    return {"P": p, "R": r, "F1": fbeta(p, r, 1), "F2": fbeta(p, r, 2), "soporte": tp + fn, "tp": tp, "fp": fp, "fn": fn}


def deteccion(gold_docs, pred_docs, modo="estricto"):
    """gold_docs/pred_docs: listas (por documento) de tuplas (ini, fin, etiqueta)."""
    c = defaultdict(lambda: [0, 0, 0])
    for gold, pred in zip(gold_docs, pred_docs):
        usados = set()
        for g in gold:
            match = None
            for j, p in enumerate(pred):
                if j in usados or p[2] != g[2]:
                    continue
                if (modo == "estricto" and p[0] == g[0] and p[1] == g[1]) or \
                   (modo == "parcial" and p[0] < g[1] and g[0] < p[1]):
                    match = j
                    break
            if match is None:
                c[g[2]][2] += 1
            else:
                usados.add(match)
                c[g[2]][0] += 1
        for j, p in enumerate(pred):
            if j not in usados:
                c[p[2]][1] += 1
    por_etiqueta = {e: _prf(*c[e]) for e in ETIQUETAS if sum(c[e])}
    tot = [sum(v[i] for v in c.values()) for i in range(3)]
    # criterio principal de la sección 7.4: F2 sobre identificadores directos y secretos
    tot_di = [sum(v[i] for e, v in c.items() if e in DIRECTAS) for i in range(3)]
    return {"por_etiqueta": por_etiqueta, "micro": _prf(*tot), "directas": _prf(*tot_di)}


def proteccion(textos, gold_docs, enmascarados_docs, enviados):
    """enmascarados_docs: spans que el sistema reemplazó en el texto enviado
    (vacío si la heurística decidió ENVIAR). enviados: texto final."""
    cub_di = tot_di = cub_qi = tot_qi = 0
    fuga = tot = 0
    chars_masc = chars_masc_ok = 0
    fuga_por_etq = defaultdict(lambda: [0, 0])
    for texto, gold, masc, env in zip(textos, gold_docs, enmascarados_docs, enviados):
        cubierto = [False] * len(texto)
        for ini, fin, _ in masc:
            for k in range(ini, fin):
                cubierto[k] = True
        en_gold = [False] * len(texto)
        for ini, fin, etq in gold:
            for k in range(ini, fin):
                en_gold[k] = True
            completo = all(cubierto[ini:fin])
            if etq in DIRECTAS:
                tot_di += 1
                cub_di += completo
            elif etq in CUASI:
                tot_qi += 1
                cub_qi += completo
            filtrado = texto[ini:fin].strip().lower() in env.lower()
            tot += 1
            fuga += filtrado
            fuga_por_etq[etq][0] += filtrado
            fuga_por_etq[etq][1] += 1
        for k in range(len(texto)):
            if cubierto[k] and not texto[k].isspace():
                chars_masc += 1
                chars_masc_ok += en_gold[k]
    return {
        "ER_di": cub_di / tot_di if tot_di else None,
        "ER_qi": cub_qi / tot_qi if tot_qi else None,
        "WP": chars_masc_ok / chars_masc if chars_masc else None,
        "fuga_residual": fuga / tot if tot else None,
        "fuga_por_etiqueta": {e: v[0] / v[1] for e, v in fuga_por_etq.items()},
        "n_di": tot_di, "n_qi": tot_qi,
    }
