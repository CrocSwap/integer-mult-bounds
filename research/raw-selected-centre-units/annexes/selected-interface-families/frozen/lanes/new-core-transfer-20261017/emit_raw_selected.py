#!/usr/bin/env python3
"""Transfer physical selected exchanges with ordered Q and warp operators."""

from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parent
OLD = LANES / 'native-escape-20261017'
PINS = {
    'core': 'a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa',
    'raw_backward': '0d3280c6ad7ce79fba15bc6ff53e32fff1de75d8c17113c6174799e544e6103f',
    'raw_forward': '92d66da6d103963f8727b5e2ecb85f5cb48a220f870d36c433b6b3c6803b7cc9',
    'raw_utility': 'ed9b91708d16226a51fb0f76e3b0c9392553cc316da7c24b9cc1fe21759d6bc0',
}


def need(test, label):
    if not test:
        raise ValueError(label)


def load(path, pin):
    raw = gzip.decompress(path.read_bytes())
    need(sha256(raw).hexdigest() == pin, 'Source pin: ' + str(path))
    return json.loads(raw)


def add(dst, src, q=Q(1)):
    for key, c in src.items():
        c = dst.get(key, 0) + q * c
        if c:
            dst[key] = c
        else:
            dst.pop(key, None)


def operator(row, symbol, power):
    out = {}
    for (source, word), c in row.items():
        w = word[1:] if word and word[0] == (symbol, -power) else ((symbol, power),) + word
        add(out, {(source, w): c})
    return out


def line(row, port, power):
    return operator(row, ('Q', port), power)


def boundary(events, state, n):
    state = deepcopy(state)
    for e in events:
        t, op = e['target'], e['kind']
        need(t < 224 or n <= t < n + 8, 'No borrowed helper boundary target')
        if op == 'clear':
            need(n <= t < n + 8, 'Only owned private fields are cleared')
            state[t] = {}
        elif op == 'copy':
            need(t == n and not state[t], 'Serial owned C0 copy')
            need(e['source'] < 224, 'Data copy source')
            state[t] = dict(state[e['source']])
        elif op == 'line':
            need(t == n and e['power'] in (-1, 1), 'Signed C0 child')
            state[t] = line(state[t], e['port'], e['power'])
        elif op == 'add':
            s = e['source']
            need(s != t and (s < 224 or n <= s < n + 8), 'Legal physical ADD source')
            add(state[t], state[s], Q(e['coefficient']))
        else:
            need(op == 'scale', 'Known physical boundary operation')
            c = Q(e['coefficient'])
            state[t] = {key: c * v for key, v in state[t].items() if c * v}
    return state


def core_replay(events, state, word, backward):
    state = deepcopy(state)
    n = len(word['start'])
    frames = {p: f for p, f in enumerate(word['start'])}
    frames.update({n + p: 0 for p in range(8)})
    zeros = set()
    def slot(token):
        if token[0] == 'L':
            need(0 <= token[1] < n, 'Live register range')
            return token[1]
        if token[0] == 'C':
            need(0 <= token[1] < 8, 'Owned register range')
            return n + token[1]
        need(token[0] == 'Z', 'Native register namespace')
        return ('Z', token[1])
    checks, warps = 0, 0
    for event in events:
        tag = event[0]
        if tag == 'scalar':
            gate, f = event[1:]
            t, op = slot(gate[1]), gate[0]
            if op == 'clear':
                need(isinstance(t, int) and n <= t < n + 8, 'Owned core CLEAR')
                state[t], frames[t] = {}, f
            else:
                need(frames[t] == f, 'Native scalar target frame')
                if op == 'scale':
                    c = Q(*gate[2:4])
                    state[t] = {key: c * v for key, v in state[t].items() if c * v}
                else:
                    s = slot(gate[2])
                    need(s != t and frames[s] == f, 'Native scalar source frame')
                    if op == 'copy':
                        need(isinstance(t, int) and n <= t < n + 8, 'Owned core COPY')
                        state[t] = dict(state[s])
                    else:
                        need(op == 'add', 'Known core scalar')
                        add(state[t], state[s], Q(*gate[3:5]))
            checks += 1
        elif tag == 'climb':
            t, old, new, rank = event[2:6]
            need(frames[t] == old, 'Native old frame')
            need(len(word['frames'][new]) - len(word['frames'][old]) == rank, 'Native rank')
            frames[t] = new
        elif tag == 'warp':
            t, op, old, new = slot(event[1]), event[2], event[3], event[4]
            need(frames[t] == old, 'Warp old frame')
            frames[t] = new
            symbol = ('dual_K' if backward else 'K', abs(op))
            state[t] = operator(state[t], symbol, 1 if op > 0 else -1)
            warps += 1
        elif tag == 'zero_buffer':
            t = ('Z', event[2])
            if event[1] == 'alloc':
                need(t not in zeros, 'Zero-buffer allocation')
                state[t], frames[t] = {}, 1
                zeros.add(t)
            else:
                need(t in zeros and not state[t], 'Zero-buffer restoration')
                zeros.remove(t)
        else:
            need(tag in ('phase', 'adapter', 'residual_adapter'), 'Known native event')
    need(not zeros, 'No live private zero buffer')
    need([frames[p] for p in range(n)] == word['final'], 'All native live endpoint frames')
    need(all(frames[n + p] == 0 for p in range(8)), 'All owned endpoint frames')
    need(all(not row for f, row in state.items() if isinstance(f, tuple)), 'All zero buffer rows')
    return {p: state[p] for p in range(n + 8)}, checks, warps


def map_boundary(events, n):
    events = deepcopy(events)
    for e in events:
        for key in ('target', 'source'):
            if e.get(key, -1) >= 704:
                e[key] += n - 704
    return events


def core_price(events):
    out = 0
    for e in events:
        if e[0] != 'scalar':
            continue
        op = e[1]
        if op[0] in ('clear', 'copy'):
            out += 2
            continue
        c = Q(*op[-2:])
        a, b = abs(c.numerator), c.denominator
        need(b & (b - 1) == 0, 'Dyadic core scalar')
        if op[0] == 'scale':
            need(a & (a - 1) == 0, 'Unit core SCALE')
            out += 2 * (abs(a.bit_length() - b.bit_length()) + int(c < 0))
        else:
            out += 2 * (3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1)
    return out


def main():
    utility_path = OLD / 'emit_raw_selected_backward.py'
    need(sha256(utility_path.read_bytes()).hexdigest() == PINS['raw_utility'], 'Pinned raw boundary price and kernels')
    spec = importlib.util.spec_from_file_location('raw_source', utility_path)
    u = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(u)
    core = load(HERE / 'CLEAN-J-PROGRAMS.json.gz', PINS['core'])
    back = load(OLD / 'RAW-SELECTED-BACKWARD-PROGRAM.json.gz', PINS['raw_backward'])
    front = load(OLD / 'RAW-SELECTED-FORWARD-PROGRAM.json.gz', PINS['raw_forward'])
    selected = back['selected']
    need(selected == front['selected'] == u.A, 'Same selected ports')
    ordinary = [p for p in range(112) if p not in selected]
    r = [{int(p): Q(c) for p, c in row.items()} for row in core['R']]
    d = {p: {a: sum(row.get(p, 0) * row.get(a, 0) for row in r) / 4 for a in selected} for p in ordinary}
    d = {p: {a: c for a, c in row.items() if c} for p, row in d.items()}
    b = {a: {p: d[p][a] for p in ordinary if a in d[p]} for a in selected}
    need(all(sum(b[a].get(p, 0) * d[p].get(z, 0) for p in ordinary) == (13 if a == z else 0)
             for a in selected for z in selected), 'Actual BD=13I')
    output = {'schema': 'pr3133-raw-selected-transfer-v1', 'source_pins': PINS, 'selected_A': selected,
              'line_recipes': back['line_recipes'], 'providers': {}}
    receipt = {'status': 'PASS_PR3133_RAW_SELECTED_ORDERED_OPERATOR_TRANSFER', 'providers': {}}
    for provider, item in core['providers'].items():
        word = item['canonical']
        n = len(word['start'])
        need(n == 632 and len(word['zero_buffers']) == 91, 'Exact provider size')
        columns = u.check_recipes(back['line_recipes'], word['ports'])
        identity = {p: {(p, ()): Q(1)} for p in range(n + 8)}
        cleanup = [{'kind': 'clear', 'target': n + p} for p in range(1, 8)]
        bpre = map_boundary(back['prefix'], n)
        bswap = map_boundary(back['physical_exchange'], n)
        bpost = map_boundary(back['post_lower_shear'], n)
        bfix = map_boundary(back['optional_ordinary_correction'], n)
        fpre = map_boundary(front['optional_input_code'], n)
        fswap = map_boundary(front['input_physical_exchange'], n)
        def evaluate(direction, pre, first, post):
            physical = deepcopy(identity)
            for p in range(112):
                physical[p] = line(physical[p], p, 1)
            physical = boundary(pre + first, physical, n)
            logical = deepcopy(physical)
            for p in range(112):
                logical[p] = line(logical[p], p, -1)
            logical, checks, warps = core_replay(item['programs'][direction], logical, word, direction == 'backward')
            physical = deepcopy(logical)
            for p in range(112):
                physical[112 + p] = line(physical[112 + p], p, -1)
            physical = boundary(post + cleanup, physical, n)
            logical = deepcopy(physical)
            for p in range(112):
                logical[112 + p] = line(logical[112 + p], p, 1)
            return logical, physical, checks, warps
        def expected_backward(coded, corrected):
            out = deepcopy(identity)
            for p in range(n, n + 8):
                out[p] = {}
            for a in selected:
                out[a] = {key: (-12 if coded else 1) * c for key, c in line(identity[112 + a], a, -1).items()}
                for p, c in b[a].items():
                    add(out[a], identity[112 + p], c)
                out[112 + a] = line(identity[a], a, 1)
            for p in ordinary:
                out[p] = dict(identity[p])
                add(out[p], identity[112 + p], -1)
                if not corrected:
                    for a, c in d[p].items():
                        add(out[p], line(identity[a], a, 1), c)
                if not coded:
                    for a, c in d[p].items():
                        add(out[p], line(identity[112 + a], a, -1), -c)
                if coded:
                    for a, c in d[p].items():
                        add(out[112 + p], line(identity[112 + a], a, -1), -c)
            return out
        def expected_forward(coded):
            out = deepcopy(identity)
            for p in range(n, n + 8):
                out[p] = {}
            query = {}
            for a in selected:
                query[a] = {}
                for p, c in b[a].items():
                    add(query[a], identity[p], c)
                add(out[a], line(query[a], a, -1), -1)
            for p in ordinary:
                add(out[112 + p], identity[p])
                for a, c in d[p].items():
                    add(out[112 + p], query[a], -c)
                    if not coded:
                        add(out[112 + p], line(identity[112 + a], a, -1), -c)
            return out
        specs = {
            'B0': ('backward', [], bswap, bpost, expected_backward(False, False), 0, 168896),
            'B8': ('backward', bpre, bswap, bpost, expected_backward(True, False), 8, 173104),
            'B16': ('backward', bpre, bswap, bpost + bfix, expected_backward(True, True), 16, 177312),
            'F0': ('forward', [], fswap, fswap, expected_forward(False), 0, 164944),
            'F8': ('forward', fpre, fswap, fswap, expected_forward(True), 8, 169152),
        }
        programs, reports = {}, {}
        for name, (direction, pre, first, post, expected, extra, total) in specs.items():
            actual, physical, checks, warps = evaluate(direction, pre, first, post)
            need(actual == expected, 'All 640 ordered-operator columns: ' + name)
            need(all(actual[p] == identity[p] for p in range(224, n)), 'All arbitrary helpers restored')
            need(all(not actual[p] for p in range(n, n + 8)), 'All owned private outputs zero')
            if direction == 'backward':
                need(all(physical[112 + a] == identity[a] for a in selected), 'Selected productive Y carries original a')
            native = item['programs'][direction]
            scalar = core_price(native) + u.scalar_price(pre + first + post + cleanup)
            need(core_price(native) == 164514 and scalar == total, 'Complete raw scalar invoice')
            profile = Counter(e[5] for e in native if e[0] == 'climb')
            profile[1] += extra
            need(sum(rk * count for rk, count in profile.items()) == 5073 + extra, 'Raw native invoice')
            need(sum(e['kind'] == 'line' for e in pre + first + post) == extra, 'Exact new line count')
            programs[name] = {'orientation': direction, 'prefix': pre, 'input_exchange': first, 'retained_core': native,
                              'suffix': post, 'owned_cleanup': cleanup,
                              'events': pre + first + native + post + cleanup}
            reports[name] = {'all_formal_input_columns': n + 8, 'arbitrary_helpers_restored': 408, 'owned_private_zero': 8,
                             'private_zero_buffers_restored': 91, 'core_scalar_frame_checks': checks, 'core_warp_events': warps,
                             'scalar_real_primitives': scalar, 'native_profile': dict(sorted(profile.items())),
                             'native_rank_mass': 5073 + extra, 'native_children': sum(profile.values()),
                             'new_rank_one_children': extra, 'new_child_wrappers': 2 * extra,
                             'unused_private_clear_cost': 14, 'exact_signed_line_columns': columns}
            print(provider, name, scalar, 5073 + extra, flush=True)
        controls = {}
        wrong = deepcopy(bpre)
        for e in wrong:
            if e['kind'] == 'line':
                e['power'] = 1
        controls['B_wrong_Q_inverse'] = evaluate('backward', wrong, bswap, bpost)[0] != specs['B8'][4]
        controls['B_missing_exchange'] = evaluate('backward', bpre, [], bpost)[0] != specs['B8'][4]
        controls['B_missing_lower_shear'] = evaluate('backward', bpre, bswap, [])[0] != specs['B8'][4]
        controls['F_missing_output_exchange'] = evaluate('forward', fpre, fswap, [])[0] != specs['F8'][4]
        controls['F_missing_input_code'] = specs['F0'][4] != specs['F8'][4]
        need(all(controls.values()), 'Meaningful raw transfer controls')
        output['providers'][provider] = {'canonical': word, 'programs': programs}
        receipt['providers'][provider] = {'programs': reports, 'controls': controls}
    raw = (json.dumps(output, sort_keys=True, separators=(',', ':')) + '\n').encode()
    (HERE / 'RAW-SELECTED-TRANSFER.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    receipt['payload_sha256'] = sha256(raw).hexdigest()
    receipt['checker_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    receipt['source_pins'] = PINS
    receipt['scope'] = 'Ten exact local ordered-operator words. Q and forward/dual K alphabets are distinct; only adjacent inverse pairs cancel. All640arbitrary columns and91zero buffers checked. No complete controller, owner admission, precision or kappa claim.'
    (HERE / 'RAW-SELECTED-TRANSFER.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], receipt['payload_sha256'])


if __name__ == '__main__':
    main()
