"""Exact bounded two-sided CK compensation construction.

Ross Richardson with substantial OpenAI Codex assistance, Apache-2.0.
Target forests follow dd-hemant PR816; helper shears follow David Awad PR807.
This implementation is new; no pending PR code is imported.
"""
from collections import deque
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVIDER = 'research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck'
SEED = 38
BASE = 'f567884aeb8851b6e794af1184119a3bfbe1e631'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def load():
    pins = read(HERE / 'SOURCES.json')
    for item in pins['files']:
        path = ROOT / item['path']
        raw = path.read_bytes()
        payload = gzip.decompress(raw) if item.get('encoding') == 'gzip' else raw
        require(hashlib.sha256(payload).hexdigest() == item['sha256'], 'source pin: ' + item['path'])
    p = ROOT / PROVIDER
    w = read(p / 'CANONICAL-WORD.json.gz')
    ps = read(p / 'LOCAL-PROGRAMS.json.gz')
    checks = read(p / 'LOCAL-CHECKS.json')
    spec = read(ROOT / 'research/complex-k492-owner-repair/data/SPEC.json')['providers']['ck']
    for name in ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz', 'LOCAL-CHECKS.json'):
        require(digest(read(p/name)) == spec['artifact_semantic_sha256'][name], 'historical SPEC binding: '+name)
    for orientation in ps:
        require(digest(ps[orientation]) == checks[orientation]['sha256'], 'program binding')
        require(digest(ps[orientation]) == spec['program_hashes'][orientation], 'historical program binding')
    return w, ps, checks


@lru_cache(None)
def price_quarter(x):
    """Inherited binary-Horner price of the coefficient x/4, in one component."""
    if not x:
        return 0
    a, d = abs(x), 2
    while d and not a % 2:
        a //= 2
        d -= 1
    return 3 + a.bit_length() - 1 + a.bit_count() + d


def matrix(w):
    rows = sorted({e[1] for e in w['compensation']})
    cols = sorted({e[2] for e in w['compensation']})
    require(len(rows) == 112 and len(cols) == 254, 'CK compensation shape')
    require(set(rows).isdisjoint(cols), 'disjoint source/target banks')
    require(all(w['start'][r] == 0 for r in rows + cols), 'common frame zero')
    require(all(w['final'][r] == 1 for r in cols), 'helpers must be unwrapped at entry')
    ri, ci = {r: i for i, r in enumerate(rows)}, {c: i for i, c in enumerate(cols)}
    C = [[0] * len(cols) for _ in rows]
    for tag, target, source, a, b, frame in w['compensation']:
        require(tag == 'add' and frame == 0, 'compensation instruction')
        q = Q(a, b) * 4
        require(q.denominator == 1, 'quarter-grid compensation')
        C[ri[target]][ci[source]] += q.numerator
    return rows, cols, C


def rowcost(row):
    return sum(map(price_quarter, row))


def forest(C):
    """Kruskal on signed row differences plus superroot, deterministic ties."""
    n = len(C)
    edges = [(rowcost(C[i]), -1, i, 0) for i in range(n)]
    for i in range(n):
        for j in range(i):
            for sign in (-1, 1):
                edges.append((8 + rowcost([a - sign*b for a, b in zip(C[i], C[j])]), j, i, sign))
    edges.sort(key=lambda e: (e[0], digest([SEED, list(e)])))
    parent = list(range(n + 1))
    def root(i):
        i += 1
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    chosen = []
    for weight, a, b, sign in edges:
        ar, br = root(a), root(b)
        if ar != br:
            parent[ar] = br
            chosen.append([weight, a, b, sign])
            if len(chosen) == n:
                break
    adj = {i: [] for i in range(-1, n)}
    for weight, a, b, sign in chosen:
        adj[a].append((b, sign)); adj[b].append((a, sign))
    visited = {-1}; queue = deque([(-1, 0)]); oriented = []
    while queue:
        a, depth = queue.popleft()
        for b, sign in sorted(adj[a]):
            if b not in visited:
                visited.add(b); queue.append((b, depth + 1))
                if a != -1:
                    oriented.append([b, a, sign, depth])
    require(len(visited) == n+1, 'forest connectivity')
    oriented.sort(key=lambda x: (-x[3], x[0], x[1]))
    D = [row[:] for row in C]
    for child, par, sign, _ in oriented:
        D[child] = [a - sign*b for a, b in zip(C[child], C[par])]
    total = sum(e[0] for e in chosen)
    require(total == sum(map(rowcost, D)) + 8*len(oriented), 'forest pricing')
    return oriented, D, {'edges': len(edges), 'price': total,
                         'chosen': chosen, 'census_sha256': digest(edges)}


def helpers(D):
    columns = list(map(list, zip(*D)))
    n = len(columns)
    costs = list(map(rowcost, columns))
    census = hashlib.sha256(); profitable = []
    count = 0
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            for sign in (-1, 1):
                # H: h_a += sign*h_b. Column b changes under right H^-1.
                gain = costs[b] - rowcost([v-sign*u for u, v in zip(columns[a], columns[b])]) - 8
                rec = [a, b, sign, gain]
                census.update(canonical(rec) + b'\n'); count += 1
                if gain > 0:
                    profitable.append(rec)
    profitable.sort(key=lambda x: (-x[3], digest([SEED, x])))
    used = set(); selected = []
    for a, b, sign, gain in profitable:
        if a not in used and b not in used:
            used.update((a,b)); selected.append([a,b,sign,gain])
    E = [row[:] for row in D]
    for a,b,sign,gain in selected:
        for row in E:
            row[b] -= sign*row[a]
    actual_gain = sum(map(rowcost,D)) - sum(map(rowcost,E)) - 8*len(selected)
    require(actual_gain == sum(x[3] for x in selected), 'disjoint helper gains')
    return selected, E, {'cases': count, 'profitable': len(profitable),
                         'census_sha256': census.hexdigest(), 'gain': actual_gain}


def addition(target, source, q):
    q = Q(q)
    require(target != source and q, 'invalid addition')
    return ['add', target, source, q.numerator, q.denominator, 0]


def construct(w):
    targets, sources, C = matrix(w)
    T, D, tree = forest(C)
    H, E, pair = helpers(D)
    prepT = [addition(targets[c], targets[p], -s) for c,p,s,_ in T]
    prepH = [addition(sources[a], sources[b], s) for a,b,s,_ in H]
    residual = [addition(t, sources[j], Q(x,4)) for t,row in zip(targets,E)
                for j,x in enumerate(row) if x]
    def inverse(es):
        return [addition(e[1],e[2],-Q(e[3],e[4])) for e in reversed(es)]
    panel = prepT + prepH + residual + inverse(prepH) + inverse(prepT)
    recipe = {'seed': SEED, 'targets': targets, 'sources': sources,
              'target_forest': T, 'helper_pairs': H,
              'forest_search': tree, 'helper_search': pair,
              'baseline_panel_price': sum(map(rowcost,C)),
              'two_sided_panel_price': sum(map(rowcost,E))+8*(len(T)+len(H)),
              'baseline_additions': len(w['compensation']),
              'candidate_additions': len(panel), 'residual_additions': len(residual),
              'residual_quarters_sha256': digest(E), 'panel_sha256': digest(panel)}
    require(recipe['baseline_panel_price'] - recipe['two_sided_panel_price'] > 0, 'no complete saving')
    return panel, recipe


def scalar(e, backward):
    _,t,s,a,b,_ = e
    if backward:
        t,s,a = s,t,-a
    return ['scalar', ['add',['L',t],['L',s],a,b], 0]


def replace_programs(w, original, panel):
    result = {}
    begin = 1 + len(w['precondition'])
    end = begin + len(w['compensation'])
    for name, events in original.items():
        require(events[0] == ['phase','zero_frame_precondition'], 'program phase')
        require(events[end] == ['phase','entry_adapters'], 'compensation boundary')
        require(events[begin:end] == [scalar(e,name=='backward') for e in w['compensation']], 'literal compensation binding')
        result[name] = events[:begin] + [scalar(e,name=='backward') for e in panel] + events[end:]
        require([e for e in events if e[0]!='scalar'] ==
                [e for e in result[name] if e[0]!='scalar'], 'non-scalar preservation')
    return result


def lower(op):
    """Literal inherited (unoptimized) binary Horner with dirty work erased."""
    tag, target = op[0], tuple(op[1]); work = ('W',0)
    require(target != work, 'work aliases target')
    if tag == 'clear':
        return [('clear',target)]
    if tag == 'copy':
        return [('copy',target,tuple(op[2]))]
    if tag == 'scale':
        q = Q(op[2],op[3]); a,b = abs(q.numerator),q.denominator
        require(a and a&(a-1)==0 and b&(b-1)==0, 'scale not signed power of two')
        shift = a.bit_length()-b.bit_length()
        return [('double' if shift>0 else 'halve',target)]*abs(shift) + ([('negate',target)] if q<0 else [])
    require(tag == 'add', 'unknown scalar operation')
    source = tuple(op[2]); q=Q(op[3],op[4]); a,b=abs(q.numerator),q.denominator
    require(source not in (target,work) and q and b&(b-1)==0, 'invalid dyadic add')
    ops=[('clear',work)]
    for i,bit in enumerate(bin(a)[2:]):
        if i: ops.append(('double',work))
        if bit=='1': ops.append(('add',work,source,1))
    ops += [('halve',work)]*(b.bit_length()-1)
    ops += [('add',target,work,1 if q>0 else -1),('clear',work)]
    return ops


def primitives(events):
    for event in events:
        if event[0]=='scalar':
            yield from lower(event[1])


def fraction_replay(events, n=716, centers=8):
    """Fresh full arbitrary-input scalar projection; nonscalars checked separately."""
    refs=[('L',i) for i in range(n)]+[('C',i) for i in range(centers)]+[('W',0)]
    state={r:{i:Q(1)} for i,r in enumerate(refs)}
    env={r:Q(1) for r in refs}; peak=Q(1); count=0; grid=0
    for op in primitives(events):
        tag,t=op[:2]; count+=1
        if tag=='clear': state[t]={};env[t]=Q(0)
        elif tag=='copy': state[t]=dict(state[op[2]]);env[t]=env[op[2]]
        elif tag in ('double','halve','negate'):
            q={'double':Q(2),'halve':Q(1,2),'negate':Q(-1)}[tag]
            state[t]={i:q*x for i,x in state[t].items()};env[t]*=abs(q)
        else:
            _,_,s,sign=op
            env[t]+=env[s]
            for i,x in list(state[s].items()):
                value=state[t].get(i,Q(0))+sign*x
                if value: state[t][i]=value
                else: state[t].pop(i,None)
        peak=max(peak,env[t])
        grid=max(grid,max((x.denominator.bit_length()-1 for x in state[t].values()),default=0))
    return state, {'real_primitives':2*count,'prefix_l1':str(peak),
                   'prefix_bits':peak.numerator.bit_length()-peak.denominator.bit_length()+1,
                   'maximum_denominator_power':grid}


def endpoint(state, backward, n=716, v=112):
    for i in range(n):
        expected={i:Q(1)}
        if backward and i<v: expected[v+i]=Q(-1)
        if not backward and v<=i<2*v: expected[i-v]=Q(1)
        require(state['L',i]==expected, 'endpoint logical row '+str(i))
    require(all(not row for r,row in state.items() if r[0]!='L'), 'private input not cleared')
