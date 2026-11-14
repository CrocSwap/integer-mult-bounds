"""Independent linking and sparse-tape execution check; no author oracle/CPU."""
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
PACKAGE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else (HERE if (HERE / 'compose.py').exists() else HERE / 'frozen')
PINS = {
    'compose.py': 'bddf330f8fb4011e476c768488853738ce44950f43d9aa211cbb159c3c488c5c',
    'inputs/bridge.py': '119b69594a2a33550eec9b6e083db8f496c3fb3d9c1214b6703d687a0a662eba',
    'inputs/leaf/leaf.py': 'bb46c1a55f1119957a52cd61f2cd957f3f7ad1e9b818c54a852bde09a0773744',
    'inputs/leaf/inputs/controller_reference.py': 'e664a748e6b6797d4b60f60a7a7dd68b59a5608acf56b9c5d8b466f363755f73',
}


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def module(path, name):
    out = types.ModuleType(name)
    out.__file__ = str(path)
    sys.modules[name] = out
    exec(compile(path.read_bytes(), str(path), 'exec'), out.__dict__)
    return out


def linking(mutate=None):
    for path, digest in PINS.items():
        need(sha256((PACKAGE / path).read_bytes()).hexdigest() == digest, 'review target changed: ' + path)
    c = module(PACKAGE / 'compose.py', '_review_composition')
    graph, labels = c.compile_composition()
    if mutate is not None:
        graph = mutate(list(graph), labels)
    bridge = module(PACKAGE / 'inputs/bridge.py', '_review_bridge')
    old, oldlabels = bridge.compile_bridge()
    controller = module(PACKAGE / 'inputs/leaf/inputs/controller_reference.py', 'controller_reference')
    leaf = module(PACKAGE / 'inputs/leaf/leaf.py', '_review_leaf')
    child, alphabet = leaf.compile_leaf()
    offset = len(old)
    ports = [3, 2] + list(range(43, 70))
    symbols = {'_': 2, '0': 0, '1': 1, '|': 3}
    need((len(old), len(child), len(graph)) == (6003, 6826, 12829), 'graph lengths')
    need(set(alphabet) == set(symbols), 'source alphabet')
    calls = [i for i, ins in enumerate(old) if ins == ('H', 'PACKED')]
    halts = [i for i, ins in enumerate(child) if ins[0] == 'halt']
    need(len(calls) == len(halts) == 1, 'unique success continuations')
    for i, ins in enumerate(old):
        expected = ('J', offset) if i == calls[0] else ins
        need(graph[i] == expected, 'bridge instruction changed')
    for i, ins in enumerate(child):
        op = ins[0]
        if op == 'read':
            need(all(0 <= d < len(child) for d in ins[2].values()), 'child branch range')
            expected = ('R', ports[ins[1]], {symbols[s]: offset + d for s, d in ins[2].items()})
        elif op == 'write':
            expected = ('W', ports[ins[1]], symbols[ins[2]])
        elif op == 'move':
            need(ins[2] in (-1, 1), 'nonunit source move')
            expected = ('M', ports[ins[1]], ins[2])
        elif op == 'goto':
            need(0 <= ins[1] < len(child), 'child jump range')
            expected = ('J', offset + ins[1])
        elif op == 'halt':
            expected = ('J', oldlabels['EXIT'])
        else:
            raise RuntimeError('unrecognized source opcode')
        need(graph[offset + i] == expected, 'child instruction translation mismatch')
    installed = []
    retired = []
    for t in range(2, 29):
        installed.extend([('move', t, -1), ('write', t, '|'), ('move', t, 1)])
        retired.extend([('move', t, -1), ('write', t, '_'), ('move', t, 1)])
    need(list(child[:81]) == installed, 'private guard installation')
    need(list(child[halts[0] - 81:halts[0]]) == retired, 'private guard retirement')
    need(not any(ins[0] == 'write' and ins[1] == 0 for ins in child), 'child writes header')
    need(all(ins[1] >= 43 for ins in graph if ins[0] == 'W' and ins[2] == 3), 'permanent guard overwritten')
    need(labels['LEAF'] == offset and labels['LEAF_RETURN'] == offset + halts[0], 'continuation labels')
    return graph, labels, bridge.SCHEMA


def encoded_header(values, schema):
    out = []
    for key in schema:
        digits = [int(c) for c in format(values[key], 'b')]
        out.extend([1] * len(digits) + [0] + digits[::-1])
    return out


def encoded_old(values, width):
    out = []
    for real, imag in values:
        for x in (real, imag):
            value = x % (1 << width)
            for bit in range(width):
                out.extend([0, 0, (value >> bit) & 1])
            out.extend([0, 1, 0])
    return out


def complex_product(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def direct_complex_oracle(values):
    cplus, cminus = (F(1, 2), F(1, 2)), (F(1, 2), F(-1, 2))
    result = list(values)
    for low in range(256):
        a, b = values[low], values[low + 256]
        left = tuple(x + y for x, y in zip(complex_product(cplus, a), complex_product(cminus, b)))
        right = tuple(x + y for x, y in zip(complex_product(cminus, a), complex_product(cplus, b)))
        need(all(x.denominator == 1 and -2 <= x < 2 for x in left + right), 'oracle admissibility')
        result[low], result[low + 256] = tuple(map(int, left)), tuple(map(int, right))
    return result


def execute(graph, labels, schema):
    values = [(0, 0)] * 512
    for k in range(256):
        amplitude = (-2, 0) if k % 4 < 2 else (0, -2)
        values[k if k % 2 == 0 else k + 256] = amplitude
    expected = direct_complex_oracle(values)
    need(expected != values, 'nonidentity complex fixture')
    h = dict.fromkeys(schema, 0)
    h.update(outer=1, rows=1, row_bits=9216, within_bits=9, record_bits=18,
             f=1, K=1, cutoff=(1 << 67) + 1, p=(1 << 41) + 3)
    data, header = encoded_old(values, 2), encoded_header(h, schema)
    origins = [-100 - 17 * i for i in range(70)]
    heads = origins[:]
    tapes = []
    for i, origin in enumerate(origins):
        cells = {origin - 2: 7, origin + 20000: 9}
        if i < 43:
            cells[origin - 1] = 3
        for j, bit in enumerate(data if i == 0 else header if i == 1 else []):
            cells[origin + j] = bit
        tapes.append(cells)
    low, high, writes = origins[:], origins[:], [0] * 70
    pc = steps = calls = returns = 0
    guide_snapshot = None
    while steps < 20_000_000:
        if pc == labels['LEAF']:
            calls += 1
            need(writes[0] == writes[1] == 0, 'original owners modified before child')
            guide_snapshot = [(dict(tapes[t]), heads[t]) for t in range(4, 43)]
            need(all(heads[t] == origins[t] for t in (0, 1, 2, 3)), 'entry public heads')
        if pc == labels['LEAF_RETURN']:
            returns += 1
            need(guide_snapshot == [(dict(tapes[t]), heads[t]) for t in range(4, 43)], 'child altered bridge guides')
            need(writes[0] == writes[1] == 0, 'original owners modified during child')
            need(all(heads[t] == origins[t] for t in range(70)), 'child return heads')
            need(all(tapes[t].get(origins[t] - 1, 2) == 2 for t in range(43, 70)), 'child guards not erased')
        ins = graph[pc]
        op = ins[0]
        steps += 1
        if op in ('R', 'W', 'M'):
            t = ins[1]
            low[t], high[t] = min(low[t], heads[t]), max(high[t], heads[t])
        if op == 'R':
            value = tapes[t].get(heads[t], 2)
            need(value in ins[2], 'unexpected missing branch in legal fixture')
            pc = ins[2][value]
        elif op == 'W':
            writes[t] += 1
            if ins[2] == 2:
                tapes[t].pop(heads[t], None)
            else:
                tapes[t][heads[t]] = ins[2]
            pc += 1
        elif op == 'M':
            heads[t] += ins[2]
            low[t], high[t] = min(low[t], heads[t]), max(high[t], heads[t])
            pc += 1
        elif op == 'J':
            pc = ins[1]
        elif op == 'H':
            need(ins[1] == 'DONE', 'unexpected terminal status')
            break
        else:
            raise RuntimeError('unknown joined opcode')
    else:
        raise RuntimeError('independent execution exceeded its bounded budget')
    need((calls, returns) == (1, 1), 'child call/return counts')
    need(heads == origins, 'final head origins')
    need([tapes[0].get(origins[0] + j, 2) for j in range(len(data))] == encoded_old(expected, 2), 'direct complex output')
    need(tapes[0].get(origins[0] + len(data), 2) == 2, 'old output frontier')
    need([tapes[1].get(origins[1] + j, 2) for j in range(len(header))] == header and writes[1] == 0, 'descriptor preservation')
    for i in range(70):
        need(low[i] >= origins[i] - 1 and high[i] < origins[i] + 20000, 'exterior touched')
        need(tapes[i].get(origins[i] - 2) == 7 and tapes[i].get(origins[i] + 20000) == 9, 'opaque exterior changed')
        need(tapes[i].get(origins[i] - 1, 2) == (3 if i < 43 else 2), 'final guard contract')
        if i >= 2:
            need(all(pos < origins[i] or pos >= origins[i] + 20000 for pos in tapes[i]), 'private body not blank')
    history = sum(high[t] - low[t] + 1 for t in range(2, 70))
    need(steps <= 2 ** 24 * (len(data) + len(header) + 1), 'time envelope')
    need(history <= 128 * (len(data) + len(header) + 1), 'history envelope')
    return {'transitions': steps, 'old_bits': len(data), 'header_bits': len(header),
            'private_history': history, 'origins': 'negative and distinct',
            'permanent_guards': 43, 'retired_guards': 27,
            'child_call_return': [calls, returns]}


def main():
    graph, labels, schema = linking()
    result = execute(graph, labels, schema)
    mutants = []
    def bad_port(code, labels):
        for i in range(labels['LEAF'], len(code)):
            if code[i][0] == 'R' and code[i][1] == 2:
                code[i] = ('R', 0, code[i][2])
                return code
        raise RuntimeError('missing mutation site')
    def bad_return(code, labels):
        code[labels['LEAF_RETURN']] = ('J', labels['EXIT'] + 1)
        return code
    for name, mutant in [('wrong-public-port', bad_port), ('off-by-one-return', bad_return)]:
        caught = False
        try:
            linking(mutant)
        except RuntimeError:
            caught = True
        need(caught, 'static mutation escaped independent linking check')
        mutants.append(name)
    plus, minus = (F(1, 2), F(1, 2)), (F(1, 2), F(-1, 2))
    field = [(F(1), F(0)), (F(0), F(0)), (F(0), F(0)), (F(1), F(0))]
    first = None
    for bit in (0, 1):
        out = list(field)
        for i in range(4):
            if i & (1 << bit):
                continue
            j = i | (1 << bit)
            out[i] = tuple(x + y for x, y in zip(complex_product(plus, field[i]), complex_product(minus, field[j])))
            out[j] = tuple(x + y for x, y in zip(complex_product(minus, field[i]), complex_product(plus, field[j])))
        field = out
        if bit == 0:
            first = list(field)
    need(any(x.denominator != 1 for pair in first for x in pair), 'endpoint-only control lost nonintegral prefix')
    need(field == [(0, 0), (1, 0), (1, 0), (0, 0)], 'independent endpoint-only tensor control')
    result.update({'status': 'PASS_INDEPENDENT_LINK_AND_F1', 'graph_sha256': sha256(json.dumps(graph, separators=(',', ':'), sort_keys=True).encode()).hexdigest(),
                   'compose_sha256': sha256((PACKAGE / 'compose.py').read_bytes()).hexdigest(),
                   'all_size_claim': 'reviewed by instruction/ABI induction; finite f1 is a failure control',
                   'heavy_f2_replay': False, 'static_mutants_rejected': mutants,
                   'endpoint_only_f2_algebra_rejected': True})
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
