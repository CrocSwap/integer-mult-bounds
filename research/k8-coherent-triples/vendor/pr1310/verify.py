"""Exact coupled gauge closure; Philipp / GPT-6 Astra, Apache-2.0.

Pair arrangement algorithm adapted from Hanson Sun's PR1214 exact_census,
with the full nonzero PR1263 gauge and boundary prices explicitly retained.
"""
from collections import Counter, defaultdict
from itertools import combinations
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def need(condition,message):
    if not condition: raise ValueError(message)

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':')).encode()

def sha(data): return hashlib.sha256(data).hexdigest()

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def sources():
    pins=json.loads((HERE/'PREDECESSORS.json').read_bytes())
    need(pins['pr1263']=='5fbaca13028846bddbb001e8e07addc2ab8e5816','1263 pin')
    need(pins['pr1214']=='26162c56ec9c50a80e49949f36d4dd9a137a76a6','1214 pin')
    expected={'vendor/pr1214-exact-pairs.py'}|{'vendor/pr1263/'+name for name in ('verify.py','independent.py','GAUGES.json','PREDECESSORS.json','README.md','vendor/pr1161/engine.py','vendor/pr1161/SOURCES.json','vendor/pr1161/BASE-SELECTED.json','vendor/pr1161/PROVENANCE.md','vendor/pr1161/PROOF.md')}
    need(set(pins['files'])==expected,'complete predecessor inventory')
    for path,digest in pins['files'].items():
        need(sha((HERE/path).read_bytes())==digest,'predecessor source '+path)
    prior=load_module('credited_pr1263',HERE/'vendor/pr1263/verify.py')
    prior.ROOT=ROOT
    lib=prior.engine()
    return prior,lib

def exact_census(lib, events, helpers, gauges):
    """Affine-cell vertices certify all integer exponents; axes allow one helper."""
    allowed = set(helpers)
    incident = {h: Counter() for h in helpers}
    shared = defaultdict(Counter)
    for event in events:
        if event[0] != 'scalar' or event[1][0] != 'add':
            continue
        g = event[1]
        p, e = lib.parts(lib.Q(g[3], g[4]))
        t = g[1][1] if g[1][0] == 'L' else None
        s = g[2][1] if g[2][0] == 'L' else None
        e += gauges.get(t, 0) - gauges.get(s, 0)
        for h, sign in ((t, 1), (s, -1)):
            if h in allowed:
                incident[h][p == 1, e, sign] += 1
        if t in allowed and s in allowed:
            a, b = sorted((t, s))
            shared[a, b][p == 1, e, t == a] += 1

    def f(unit, exponent):
        return abs(exponent) - int(unit and exponent == 0)

    cache = {}

    def single(h, k):
        if (h, k) not in cache:
            cache[h, k] = 2 * (abs(k + gauges.get(h, 0)) - abs(gauges.get(h, 0))) + sum(n * (f(u, e + sign * k) - f(u, e))
                for (u, e, sign), n in incident[h].items())
        return cache[h, k]

    rows = []
    counts = Counter()
    best = None
    for a, b in combinations(helpers, 2):
        edges = shared.get((a, b), {})
        # Removing shared edges leaves vertical/horizontal slope-change lines.
        ta, tb = incident[a].copy(), incident[b].copy()
        diagonals = set()
        for (u, e, target_first), n in edges.items():
            sa = 1 if target_first else -1
            ta[u, e, sa] -= n
            tb[u, e, -sa] -= n
            diagonals.add(-sa * e)
        vertical = {-gauges.get(a, 0)} | {-s * e for (u, e, s), n in ta.items() if n}
        horizontal = {-gauges.get(b, 0)} | {-s * e for (u, e, s), n in tb.items() if n}
        vertices = {(k, ell) for k in vertical for ell in horizontal}
        vertices.update((k, k - d) for k in vertical for d in diagonals)
        vertices.update((ell + d, ell) for ell in horizontal for d in diagonals)
        pair_best = None
        evaluated = []
        for ka, kb in sorted(vertices):
            correction = 0
            for (u, e, target_first), n in edges.items():
                kt, ks = (ka, kb) if target_first else (kb, ka)
                correction += n * (f(u, e + kt - ks) - f(u, e + kt) - f(u, e - ks) + f(u, e))
            delta = single(a, ka) + single(b, kb) + correction
            key = (delta, abs(ka) + abs(kb), ka, kb)
            evaluated.append([ka, kb, delta])
            if pair_best is None or key < pair_best:
                pair_best = key
        delta, _, ka, kb = pair_best
        rows.append([a, b, len(vertices), delta, ka, kb, sha(canonical(evaluated))])
        counts['pairs'] += 1
        counts['interacting_pairs' if edges else 'separable_pairs'] += 1
        counts['vertices'] += len(vertices)
        key = (delta, a, b, abs(ka) + abs(kb), ka, kb)
        if best is None or key < best:
            best = key
    d, a, b, _, ka, kb = best
    return {'helpers': helpers, 'domain': 'all integer exponent pairs, including zero',
            **counts, 'rows': rows,
            'winner': {'helpers': [a, b], 'exponents': [ka, kb], 'delta_real': d,
                       'separate_single_delta_real': single(a, ka) + single(b, kb),
                       'interaction_delta_real': d - single(a, ka) - single(b, kb)}}



def compute():
    prior,lib=sources()
    word,programs,*_=lib.load()
    helpers=prior.domain(lib,word,programs)
    original=json.loads((HERE/'vendor/pr1263/GAUGES.json').read_bytes())
    answer={'seed':35,'base':'bce54fb3f895cbe5cd4c0eb477c3afeed100190f',
            'eligible_helpers':helpers,'orientations':{}}
    for orientation in ('forward','backward'):
        gauges={int(h):k for h,k in original[orientation].items()}
        old=prior.transform(lib,word,programs[orientation],gauges)
        trace=[]
        for step in range(25):
            row=exact_census(lib,programs[orientation],helpers,gauges)
            trace.append(row)
            win=row['winner']
            if win['delta_real']>=0: break
            for h,k in zip(win['helpers'],win['exponents']):
                gauges[h]=gauges.get(h,0)+k
                if gauges[h]==0:del gauges[h]
        else:raise ValueError('descent cap reached')
        candidate=prior.transform(lib,word,programs[orientation],gauges)
        before=lib.invoice(old,'copy-init');after=lib.invoice(candidate,'copy-init')
        baseline=lib.invoice(programs[orientation],'copy-init')
        need(before['paid_profile']==after['paid_profile']==baseline['paid_profile'],'paid profile identity')
        need([e for e in old if e[0]!='scalar']==[e for e in candidate if e[0]!='scalar'],'all nonscalar events')
        need(before['real_primitives']-after['real_primitives']==3,'coupled saving')
        need(after['real_primitives']-before['real_primitives']==sum(r['winner']['delta_real'] for r in trace),'descent invoice')
        need(trace[-1]['pairs']==27966 and all(r[3]==0 for r in trace[-1]['rows']),'complete pair stationarity')
        for record in trace:
            rows=record.pop('rows')
            record['rows_sha256']=sha(canonical(rows))
            record['pair_minima_sha256']=sha(canonical([[r[0],r[1],r[3]] for r in rows]))
            record['improving_pairs']=[r for r in rows if r[3]<0]
            record['minimum_histogram']=sorted(Counter(r[3] for r in rows).items())
        answer['orientations'][orientation]={'trace':trace,'gauges':gauges,
            'baseline':baseline,'predecessor':before,'candidate':after,
            'candidate_sha256':sha(canonical(candidate)),
            'endpoint':lib.replay(candidate,orientation),
            'predecessor_endpoint':lib.replay(old,orientation)}
    answer['status']='PASS_COUPLED_GAUGE_STATIONARITY'
    return answer

def check_certificate(result,expected):
    need(canonical(result)==canonical(expected),'complete certificate equality')

if __name__=='__main__':
    result=compute();path=HERE/'CERTIFICATE.json'
    if '--write' in sys.argv:
        need(not path.exists(),'refusing certificate overwrite');path.write_bytes(canonical(result)+b'\n')
    else:check_certificate(result,json.loads(path.read_bytes()))
    print(result['status'])
    for orientation,r in result['orientations'].items():
        print(orientation,'pairs',r['trace'][-1]['pairs'],'vertices',r['trace'][-1]['vertices'],
              'original',r['baseline']['complex_primitives'],'new',r['candidate']['complex_primitives'])
