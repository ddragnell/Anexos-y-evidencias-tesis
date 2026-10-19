"""Análisis de sensibilidad del umbral de la heurística (sección 8.3).

Usa solo el conjunto sintético de desarrollo, nunca el de prueba, con las
detecciones guardadas del enfoque híbrido final. Para cada umbral de 0,4 a 0,8
cuenta los prompts enmascarados por grupo según la referencia: con algún
identificador directo, con un solo tipo de cuasi-identificador, con dos o más
tipos y sin información sensible, y calcula ER_di, ER_qi y la fuga residual.

Uso:
  python scripts/sensibilidad_umbral.py [DATOS_DEV] [SALIDAS_HIBRIDO]
  -> resultados/sensibilidad_umbral/resumen.json
"""
import sys, json
from pathlib import Path
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from mecanismo import heuristica
from mecanismo.entidad import Entidad
from mecanismo.mecanismo import enmascarar
from mecanismo.metricas import proteccion
from mecanismo.taxonomia import DIRECTAS

args = sys.argv[1:] + [None, None]
datos = args[0] or RAIZ / 'datos/sintetico/dev.jsonl'
salidas = args[1] or RAIZ / 'resultados/sintetico_dev_final/salidas_hibrido.jsonl'
docs = [json.loads(l) for l in open(datos, encoding='utf-8')]
preds = [[Entidad(**e) for e in json.loads(l)['pred']] for l in open(salidas, encoding='utf-8')]
assert len(docs) == len(preds)
gold = [[tuple(x) for x in d['label']] for d in docs]
textos = [d['text'] for d in docs]
cuasi = heuristica.CUASI_COOCURRENCIA
grupo = []
for g in gold:
    etq = {x[2] for x in g}
    if etq & DIRECTAS: grupo.append('directo')
    elif not etq: grupo.append('limpio')
    elif len(etq & cuasi) == 1: grupo.append('un_cuasi')
    else: grupo.append('varios_cuasi')
tot = {k: grupo.count(k) for k in ('directo', 'un_cuasi', 'varios_cuasi', 'limpio')}
print('prompts', len(docs), tot)
res = {}
for u in (0.4, 0.5, 0.6, 0.7, 0.8):
    heuristica.UMBRAL = u
    dec = [heuristica.decidir(p)['accion'] == 'ENMASCARAR' for p in preds]
    masc = [[(e.inicio, e.fin, e.etiqueta) for e in p] if d else [] for p, d in zip(preds, dec)]
    env = [enmascarar(t, p) if d else t for t, p, d in zip(textos, preds, dec)]
    pr = proteccion(textos, gold, masc, env)
    r = {'enmascarados': sum(dec),
         'directo_sin_enmascarar': sum(1 for g, d in zip(grupo, dec) if g == 'directo' and not d),
         'un_cuasi_enmascarados': sum(1 for g, d in zip(grupo, dec) if g == 'un_cuasi' and d),
         'varios_cuasi_enmascarados': sum(1 for g, d in zip(grupo, dec) if g == 'varios_cuasi' and d),
         'limpios_enmascarados': sum(1 for g, d in zip(grupo, dec) if g == 'limpio' and d),
         'ER_di': pr['ER_di'], 'ER_qi': pr['ER_qi'], 'fuga_residual': pr['fuga_residual']}
    res[u] = r
    print(u, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
out = RAIZ / 'resultados' / 'sensibilidad_umbral'
out.mkdir(parents=True, exist_ok=True)
json.dump({'datos': str(datos), 'salidas': str(salidas), 'totales': tot, 'por_umbral': res},
          open(out / 'resumen.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
