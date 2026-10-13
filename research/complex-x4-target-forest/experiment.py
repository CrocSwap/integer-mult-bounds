"""Selected-X4 signed target forests; Ross Richardson + OpenAI Codex, Apache-2.0.

Forest mechanism: Oscar Fennell PR759, dd-hemant PR816; X4 pair precedent:
ToikY PR901. No pending implementation is imported.
"""
import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier799-audit/integrated799-replay.tar.gz'
WORDPIN = 'research/gauge44-frames-x/construction/jx/LOCAL-PINS-jx-X4.json'
WORK = ('W', 0)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for path, digest in pins['files'].items():
        require(sha((ROOT / path).read_bytes()) == digest, 'source pin: ' + path)
    data = {}
    with tarfile.open(ROOT / ARCHIVE) as archive:
        for name, digest in pins['members'].items():
            payload = archive.extractfile(name).read()
            if name.endswith('.gz'):
                payload = gzip.decompress(payload)
            require(sha(payload) == digest, 'member pin: ' + name)
            data[Path(name).name.split('.')[0]] = json.loads(payload)
    word, programs, checks = (data[k] for k in ('CANONICAL-WORD', 'LOCAL-PROGRAMS', 'LOCAL-CHECKS'))
    inherited = data['INDEPENDENT-LOCAL-REPLAY']['local']
    selected = json.loads((ROOT / WORDPIN).read_text())
    require(pins['members']['native/local/CANONICAL-WORD.json.gz'] == selected['canonical_sha256'], 'selected word binding')
    for orientation in ('forward', 'backward'):
        require(sha(canonical(programs[orientation])) == selected['program_sha256'][orientation] == checks[orientation]['sha256'], 'selected program binding')
        checks[orientation]['inherited_prefix_upper'] = inherited[orientation]['prefix_l1_upper']
        checks[orientation]['charged_payload_bits'] = inherited[orientation]['charged_payload_bits']
    return word, programs, checks


def cost(q):
    q = Q(q)
    if not q:
        return 0
    a, d = abs(q.numerator), q.denominator
    require(d & (d - 1) == 0, 'non-dyadic')
    return 3 + a.bit_length() - 1 + bin(a).count('1') + d.bit_length() - 1


def matrix(word):
    rows = {r: {} for r in range(112, 224)}
    for tag, t, s, n, d, frame in word['compensation']:
        require(tag == 'add' and frame == 0 and t in rows and 224 <= s < 728, 'compensation shape')
        require(s not in rows[t], 'duplicate coefficient')
        rows[t][s] = Q(n, d)
    return rows


def difference(a, b, sign):
    return {s: q for s in a.keys() | b.keys() if (q := a.get(s, 0) - sign * b.get(s, 0))}


def edges_for(rows):
    edges = []
    for t, row in sorted(rows.items()):
        edges.append([-1, t, 0, sum(cost(q) for q in row.values())])
        for u in sorted(rows):
            if u >= t:
                break
            for sign in (-1, 1):
                weight = 8 + sum(cost(q) for q in difference(row, rows[u], sign).values())
                edges.append([u, t, sign, weight])
    return edges


def synthesize(word):
    rows = matrix(word)
    edges = edges_for(rows)
    parent = {v: v for v in [-1, *rows]}
    def root(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    selected = []
    # All edge weights are exact. The OS seed only breaks tied costs.
    for e in sorted(edges, key=lambda e: (e[3], sha(canonical([34, *e[:3]])))):
        u, v, _, _ = e
        a, b = root(u), root(v)
        if a != b:
            parent[a] = b
            selected.append(e)
    require(len(selected) == 112, 'disconnected forest')
    return {'seed': 34, 'edges': selected, 'complex_primitive_floor': sum(e[3] for e in selected),
            'census_edges': len(edges), 'census_sha256': sha(canonical(edges))}


def forest(word, recipe):
    rows = matrix(word)
    graph = {v: [] for v in [-1, *rows]}
    require(len(recipe['edges']) == 112, 'tree edge count')
    for u, v, sign, weight in recipe['edges']:
        require(u in graph and v in graph and u != v and sign in (-1, 0, 1), 'bad tree edge')
        require((sign == 0) == (-1 in (u, v)), 'bad root sign')
        graph[u].append((v, sign)); graph[v].append((u, sign))
    parents, order = {}, [-1]
    for u in order:
        for v, sign in sorted(graph[u]):
            if v == parents.get(u, (None,))[0]:
                continue
            require(v not in order, 'tree cycle')
            parents[v] = (u, sign)
            order.append(v)
    require(len(order) == 113, 'tree disconnected')
    preparation = [['add', t, p, -s, 1, 0] for t in reversed(order[1:]) for p, s in [parents[t]] if p != -1]
    middle = []
    for t in order[1:]:
        p, sign = parents[t]
        row = rows[t] if p == -1 else difference(rows[t], rows[p], sign)
        middle += [['add', t, h, q.numerator, q.denominator, 0] for h, q in sorted(row.items())]
    restoration = [['add', t, p, s, 1, 0] for t in order[1:] for p, s in [parents[t]] if p != -1]
    return preparation + middle + restoration, len(preparation), parents


def event(op, orientation):
    tag, t, s, n, d, frame = op
    if orientation == 'backward':
        t, s, n = s, t, -n
    return ['scalar', [tag, ['L', t], ['L', s], n, d], frame]


def replace(program, word, new, orientation):
    start = 1 + len(word['precondition'])
    stop = start + len(word['compensation'])
    require(program[start:stop] == [event(op, orientation) for op in word['compensation']], 'compensation boundary')
    result = program[:start] + [event(op, orientation) for op in new] + program[stop:]
    require([e for e in program if e[0] != 'scalar'] == [e for e in result if e[0] != 'scalar'], 'non-scalar changed')
    return result


def lower(op):
    tag, t = op[0], tuple(op[1])
    if tag == 'clear':
        return [('clear', t)]
    if tag == 'copy':
        return [('copy', t, tuple(op[2]))]
    if tag == 'scale':
        q = Q(op[2], op[3]); a, d = abs(q.numerator), q.denominator
        require(a and a & (a-1) == 0 and d & (d-1) == 0, 'non-dyadic scale')
        shift = a.bit_length() - d.bit_length()
        return [('double' if shift > 0 else 'halve', t)] * abs(shift) + ([('negate', t)] if q < 0 else [])
    require(tag == 'add', 'unknown scalar')
    s, q = tuple(op[2]), Q(op[3], op[4])
    require(s != t and s != WORK and t != WORK and q, 'invalid add')
    out = [('clear', WORK)]
    for i, digit in enumerate(bin(abs(q.numerator))[2:]):
        if i:
            out.append(('double', WORK))
        if digit == '1':
            out.append(('add', WORK, s))
    out += [('halve', WORK)] * (q.denominator.bit_length() - 1)
    out += [('add' if q > 0 else 'subtract', t, WORK), ('clear', WORK)]
    require(len(out) == cost(q), 'lowering cost')
    return out


def step(rows, op):
    tag, t = op[:2]
    if tag == 'clear':
        rows[t] = {}
    elif tag == 'copy':
        rows[t] = rows[op[2]].copy()
    elif tag in ('double', 'halve', 'negate'):
        q = {'double': Q(2), 'halve': Q(1, 2), 'negate': Q(-1)}[tag]
        rows[t] = {j: q*x for j,x in rows[t].items()}
    elif tag in ('add', 'subtract'):
        sign = 1 if tag == 'add' else -1
        for j, x in rows[op[2]].items():
            q = rows[t].get(j, 0) + sign*x
            if q:
                rows[t][j] = q
            else:
                rows[t].pop(j, None)
    else:
        raise ValueError('unknown primitive')


def replay(program, orientation):
    regs = [('L', i) for i in range(728)] + [('C', i) for i in range(8)] + [WORK]
    rows = {r: {i: Q(1)} for i, r in enumerate(regs)}
    envelopes = {r: Q(1) for r in regs}
    peak = Q(1); depth = 0
    counts, paid = Counter(), Counter()
    digest = hashlib.sha256(); macros = 0
    for e in program:
        if e[0] == 'climb':
            paid[e[5]] += 1
        elif e[0] == 'center':
            paid[e[4]] += 1
        elif e[0] != 'scalar':
            require(e[0] in ('phase','adapter','residual_adapter'), 'unknown event')
        if e[0] != 'scalar':
            continue
        macros += 1
        for op in lower(e[1]):
            step(rows, op)
            tag, t = op[:2]
            if tag == 'clear': envelopes[t] = Q(0)
            elif tag == 'copy': envelopes[t] = envelopes[op[2]]
            elif tag in ('add','subtract'): envelopes[t] += envelopes[op[2]]
            elif tag == 'double': envelopes[t] *= 2
            elif tag == 'halve': envelopes[t] /= 2
            peak = max(peak, envelopes[t])
            # Exact dyadic grid depth of every actual intermediate row.
            depth = max(depth, max((q.denominator.bit_length()-1 for q in rows[t].values()), default=0))
            counts[tag] += 2
            digest.update(canonical([e[2], op]) + b'\n')
        if e[1][0] == 'add':
            require(not rows[WORK], 'work not cleared at macro boundary')
    for i in range(728):
        expected = {i: Q(1)}
        if orientation == 'forward' and 112 <= i < 224: expected[i-112] = Q(1)
        if orientation == 'backward' and i < 112: expected[i+112] = Q(-1)
        require(rows[('L',i)] == expected, 'full arbitrary-input map at ' + str(i))
    require(all(not rows[r] for r in regs if r[0] != 'L'), 'private input not erased')
    return {'real_primitives':sum(counts.values()), 'macros':macros, 'primitive_counts':dict(sorted(counts.items())),
            'primitive_sha256':digest.hexdigest(), 'program_sha256':sha(canonical(program)),
            'positive_prefix_upper':str(peak), 'prefix_bits':peak.numerator.bit_length()-peak.denominator.bit_length()+1,
            'exact_fractional_bits':depth, 'arbitrary_input_columns':len(regs),
            'paid_profile':{str(k):v for k,v in sorted(paid.items())}}


def boundary(word, operations, orientation, target_inputs=True):
    rows = {('L',i):({i:Q(1)} if target_inputs or not 112 <= i < 224 else {}) for i in range(728)}
    rows[WORK] = {728: Q(1)}
    for op in operations:
        for primitive in lower(event(op, orientation)[1]): step(rows, primitive)
    return rows


def controls(word, new, prep):
    old = boundary(word,word['compensation'],'forward')
    require(boundary(word,new,'forward') == old, 'compensation mismatch')
    # A missing preparation is invisible with zero target input: check this trap.
    require(boundary(word,new[prep:],'forward',False) == boundary(word,word['compensation'],'forward',False), 'zero-target control setup')
    mutants = {'missing_preparation':new[prep:], 'missing_restoration':new[:-prep],
               'wrong_order':list(reversed(new)), 'missing_middle':new[:prep]+new[prep+1:]}
    changed = [x[:] for x in new]; changed[prep][3] *= -1; mutants['wrong_coefficient_sign']=changed
    for label, ops in mutants.items():
        require(boundary(word,ops,'forward') != old, 'control passed: '+label)
    require(boundary(word,new,'backward') == boundary(word,word['compensation'],'backward'), 'dual boundary')
    return sorted(mutants)
