"""Ajuste del componente NER (token classification, esquema BIO).

Parte de dccuchile/bert-base-spanish-wwm-cased o del checkpoint ya ajustado
con MEDDOCAN (la cabeza de clasificación se reinicia porque cambian las
etiquetas). Entrena con exportaciones de Doccano en JSONL
({"text", "label": [[ini, fin, etiqueta]]}): el corpus de prompts en
español y, si se indica, el split dev del corpus sintético. El split test
del sintético nunca se usa para entrenar.

Por defecto el NER aprende solo las etiquetas de las que es responsable en
el enfoque híbrido (PER, ORG, LOC, ADDRESS); con --todas aprende las 13.

Uso (después de scripts/particionar_doccano.py):
  python scripts/entrenar_ner.py --datos datos/doccano/entrenamiento.jsonl datos/sintetico/dev.jsonl \
      --val datos/doccano/validacion.jsonl \
      --base dccuchile/bert-base-spanish-wwm-cased --salida modelos/ner-bert --epocas 4
Luego:
  python scripts/evaluar_deteccion.py --datos datos/sintetico/test.jsonl --ner-backend hf --ner-modelo modelos/ner-bert
"""
import argparse
import math
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mecanismo.ner_detector import MAPEO  # noqa: E402
from mecanismo.taxonomia import ETIQUETAS, ETIQUETAS_NER  # noqa: E402


def cargar(rutas, etiquetas):
    docs = []
    for ruta in rutas:
        for linea in open(ruta, encoding="utf-8"):
            d = json.loads(linea)
            etq = d.get("label") or d.get("labels") or d.get("entities") or []
            if etq and isinstance(etq[0], dict):
                etq = [[e["start_offset"], e["end_offset"], e["label"]] for e in etq]
            spans = [(s, e, MAPEO.get(l, l)) for s, e, l in etq]
            docs += fragmentar(d["text"], [x for x in spans if x[2] in etiquetas])
    return docs


def fragmentar(texto, spans, max_chars=600):
    """Parte documentos largos (los casos de MEDDOCAN) en fragmentos de hasta
    max_chars, cortando en saltos de línea o fin de oración y nunca dentro
    de una entidad, para que la truncación a max_len no pierda entidades."""
    if len(texto) <= max_chars:
        return [{"text": texto, "spans": spans}]
    dentro = lambda k: any(s < k < e for s, e, _ in spans)  # noqa: E731
    cortes, ini = [], 0
    while len(texto) - ini > max_chars:
        fin = ini + max_chars
        k = max((m for m in range(ini + max_chars // 3, fin)
                 if texto[m - 1] in "\n." and not dentro(m)), default=None)
        if k is None:
            k = next((m for m in range(fin, ini, -1) if texto[m - 1] == " " and not dentro(m)), fin)
        cortes.append((ini, k))
        ini = k
    cortes.append((ini, len(texto)))
    return [{"text": texto[a:b], "spans": [(s - a, e - a, l) for s, e, l in spans if a <= s and e <= b]}
            for a, b in cortes if texto[a:b].strip()]


def a_bio(doc, tok, l2i, max_len):
    enc = tok(doc["text"], truncation=True, max_length=max_len, return_offsets_mapping=True)
    labels, previo = [], None
    for (a, b), wid in zip(enc["offset_mapping"], enc.word_ids()):
        if wid is None or a == b:
            labels.append(-100)
            continue
        etq = next((s for s in doc["spans"] if s[0] <= a < s[1]), None)
        if etq is None:
            labels.append(l2i["O"])
            previo = None
        else:
            pref = "I" if previo == etq else "B"
            labels.append(l2i[f"{pref}-{etq[2]}"])
            previo = etq
    enc.pop("offset_mapping")
    enc["labels"] = labels
    return enc


def spans_bio(seq):
    """Entidades (tipo, ini, fin) de una secuencia BIO, con el mismo criterio de seqeval:
    un I- sin B- previo del mismo tipo abre una entidad nueva."""
    ents, tipo, ini = set(), None, None
    for i, t in enumerate(list(seq) + ["O"]):
        if tipo is not None and (t == "O" or t.startswith("B-") or t[2:] != tipo):
            ents.add((tipo, ini, i))
            tipo = None
        if t != "O" and tipo is None:
            tipo, ini = t[2:], i
    return ents


def evaluar_bio(y_t, y_p):
    """P/R/F1 a nivel de entidad (coincidencia exacta), por tipo y micro.
    Reemplaza a seqeval, que no se instala en el Python de Colab."""
    from collections import Counter
    tp, np_, ng = Counter(), Counter(), Counter()
    for k, (t, p) in enumerate(zip(y_t, y_p)):
        g, q = spans_bio(t), spans_bio(p)
        for e in g:
            ng[e[0]] += 1
        for e in q:
            np_[e[0]] += 1
        for e in g & q:
            tp[e[0]] += 1
    def prf(a, b, c):
        pr = a / b if b else 0.0
        rc = a / c if c else 0.0
        return pr, rc, (2 * pr * rc / (pr + rc) if pr + rc else 0.0)
    filas = {t: prf(tp[t], np_[t], ng[t]) + (ng[t],) for t in sorted(set(ng) | set(np_))}
    filas["micro"] = prf(sum(tp.values()), sum(np_.values()), sum(ng.values())) + (sum(ng.values()),)
    return filas


def reporte(filas):
    lineas = [f"{'etiqueta':<10}{'P':>8}{'R':>8}{'F1':>8}{'soporte':>9}"]
    for t, (p, r, f, n) in filas.items():
        lineas.append(f"{t:<10}{p:8.3f}{r:8.3f}{f:8.3f}{n:9d}")
    return "\n".join(lineas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datos", nargs="+", required=True)
    ap.add_argument("--base", default="dccuchile/bert-base-spanish-wwm-cased")
    ap.add_argument("--salida", default="modelos/ner-bert")
    ap.add_argument("--todas", action="store_true", help="entrenar las 13 etiquetas")
    ap.add_argument("--epocas", type=float, default=4)
    ap.add_argument("--lr", type=float, default=5e-5)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--max-len", type=int, default=256)
    ap.add_argument("--val", nargs="+", default=None,
                    help="JSONL de validación (p. ej. datos/doccano/validacion.jsonl); si se omite, "
                         "se separa el 15 %% de --datos")
    ap.add_argument("--semilla", type=int, default=13)
    a = ap.parse_args()

    import numpy as np
    from transformers import (AutoModelForTokenClassification, AutoTokenizer, DataCollatorForTokenClassification,
                              Trainer, TrainingArguments, set_seed)
    set_seed(a.semilla)

    etiquetas = ETIQUETAS if a.todas else sorted(ETIQUETAS_NER)
    nombres = ["O"] + [f"{p}-{e}" for e in etiquetas for p in "BI"]
    l2i = {l: i for i, l in enumerate(nombres)}

    if any("test" in Path(r).stem or "prueba" in Path(r).stem for r in a.datos + (a.val or [])):
        sys.exit("El conjunto de prueba no se usa para entrenar ni validar.")
    docs = cargar(a.datos, set(etiquetas))
    if a.val:
        train, val = docs, cargar(a.val, set(etiquetas))
    else:
        random.Random(a.semilla).shuffle(docs)
        k = max(1, int(len(docs) * 0.15))
        val, train = docs[:k], docs[k:]
    print(f"train={len(train)} val={len(val)} etiquetas={etiquetas}")

    tok = AutoTokenizer.from_pretrained(a.base)
    tok.model_max_length = min(tok.model_max_length, 512)
    ds_train = [a_bio(d, tok, l2i, a.max_len) for d in train]
    ds_val = [a_bio(d, tok, l2i, a.max_len) for d in val]
    modelo = AutoModelForTokenClassification.from_pretrained(
        a.base, num_labels=len(nombres), id2label=dict(enumerate(nombres)), label2id=l2i,
        ignore_mismatched_sizes=True)

    def metricas(p):
        pred = np.argmax(p.predictions, axis=-1)
        y_t, y_p = [], []
        for ps, ls in zip(pred, p.label_ids):
            y_t.append([nombres[l] for l in ls if l != -100])
            y_p.append([nombres[q] for q, l in zip(ps, ls) if l != -100])
        return {"f1": evaluar_bio(y_t, y_p)["micro"][2]}

    # 10 % de calentamiento; se calcula en pasos porque transformers 5 eliminó warmup_ratio
    pasos_calentamiento = int(0.1 * math.ceil(len(ds_train) / a.batch) * a.epocas)
    args = TrainingArguments(output_dir=str(Path(a.salida) / "checkpoints"), num_train_epochs=a.epocas,
                             learning_rate=a.lr, per_device_train_batch_size=a.batch,
                             per_device_eval_batch_size=a.batch, eval_strategy="epoch", save_strategy="epoch",
                             load_best_model_at_end=True, metric_for_best_model="f1", save_total_limit=1,
                             weight_decay=0.01, warmup_steps=pasos_calentamiento, logging_steps=20, report_to=[],
                             seed=a.semilla)
    tr = Trainer(model=modelo, args=args, train_dataset=ds_train, eval_dataset=ds_val,
                 data_collator=DataCollatorForTokenClassification(tok), compute_metrics=metricas)
    tr.train()
    tr.save_model(a.salida)
    tok.save_pretrained(a.salida)

    p = tr.predict(ds_val)
    pred = np.argmax(p.predictions, axis=-1)
    y_t = [[nombres[l] for l in ls if l != -100] for ls in p.label_ids]
    y_p = [[nombres[q] for q, l in zip(ps, ls) if l != -100] for ps, ls in zip(pred, p.label_ids)]
    rep = reporte(evaluar_bio(y_t, y_p))
    print(rep)
    (Path(a.salida) / "reporte_validacion.txt").write_text(rep, encoding="utf-8")


if __name__ == "__main__":
    main()
