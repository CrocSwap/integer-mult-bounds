#!/usr/bin/env python3
"""Check the signed and oblique extensions on the two new local words."""

from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'paired-package-review/upstream-followthrough-20261015/current-query-encoder'
CORE_PIN = 'a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa'
SIGNED_PIN = '17122a343fb8a3dd804b2d7042d523aa209d0684447cdba63d84cc5561b6144f'


def require(test, label):
    if not test:
        raise ValueError(label)


def load(path, pin):
    raw = gzip.decompress(path.read_bytes())
    require(sha256(raw).hexdigest() == pin, 'Source pin: ' + str(path))
    return json.loads(raw)


def add(dst, src, q=Q(1)):
    for k, v in src.items():
        z = dst.get(k, 0) + q * v
        if z:
            dst[k] = z
        else:
            dst.pop(k, None)


def product(a, b):
    result = []
    for row in a:
        out = {}
        for j, c in row.items():
            add(out, b[j], c)
        result.append(out)
    return result


def rows(data):
    return [{int(k): Q(v) for k, v in row.items()} for row in data]


def price(op):
    if op[0] in ('clear', 'copy'):
        return 2
    q = Q(*op[-2:])
    a, b = abs(q.numerator), q.denominator
    require(b & (b - 1) == 0, 'Dyadic coefficient')
    if op[0] == 'scale':
        require(a & (a - 1) == 0, 'Unit SCALE')
        return 2 * (abs(a.bit_length() - b.bit_length()) + int(q < 0))
    return 2 * (3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1)


def replay(events, word, backward, selected):
    n = len(word['start'])
    fields = [('L', p) for p in range(n)] + [('C', p) for p in range(8)]
    state = {f: {(f, ()): Q(1)} for f in fields}
    frames = {('L', p): f for p, f in enumerate(word['start'])}
    frames.update({('C', p): 0 for p in range(8)})
    zeros = set()
    checks = 0
    def boundary_field(p):
        require(0 <= p < n + 8, 'Boundary register')
        return ('L', p) if p < n else ('C', p - n)
    for pos, e in enumerate(events):
        if isinstance(e, dict):
            kind, endpoint = e['kind'], e['endpoint']
            t = boundary_field(e['target'])
            require(endpoint in ('input', 'output'), 'Boundary endpoint')
            if kind == 'clear_owned':
                require(t == ('C', 0), 'Only owned C0 is cleared')
                state[t] = {}
                z = e['zero_frame']
                if z == 'I':
                    frames[t] = 0
                else:
                    require(z[0] == 'selected_source' and z[1] in selected, 'Selected zero frame')
                    frames[t] = word['start'][z[1]] if endpoint == 'input' else word['final'][112 + z[1]]
            elif kind == 'physical_copy':
                s = boundary_field(e['source'])
                require(t == ('C', 0) and not state[t] and frames[t] == frames[s], 'Owned same-frame copy')
                state[t] = dict(state[s])
            elif kind == 'intrinsic_line':
                p = e['port']
                old = word['start'][p] if endpoint == 'input' else word['final'][112 + p]
                require(p in selected and t == ('C', 0), 'Selected private line')
                require(frames[t] == old and e['power'] == (-1 if endpoint == 'input' else 1), 'Line sign and frame')
                frames[t] = 0 if endpoint == 'input' else 1
            elif kind == 'physical_add':
                s = boundary_field(e['source'])
                require(s == ('C', 0) and frames[t] == frames[s] == (0 if endpoint == 'input' else 1), 'Physical ADD frame')
                add(state[t], state[s], Q(e['coefficient']))
            else:
                raise ValueError(kind)
            checks += 1
            continue
        tag = e[0]
        if tag == 'scalar':
            op, frame = e[1:]
            t = tuple(op[1])
            if op[0] == 'clear':
                require(t[0] == 'C', 'Only owned C fields are cleared')
                state[t], frames[t] = {}, frame
            else:
                require(frames[t] == frame, ('Scalar target frame', pos))
                if op[0] == 'scale':
                    q = Q(*op[2:])
                    state[t] = {k: q * v for k, v in state[t].items()}
                else:
                    s = tuple(op[2])
                    require(frames[s] == frame and s != t, ('Scalar source frame', pos))
                    if op[0] == 'copy':
                        require(t[0] == 'C', 'Owned COPY')
                        state[t] = dict(state[s])
                    else:
                        require(op[0] == 'add', 'Known scalar')
                        add(state[t], state[s], Q(*op[3:]))
            checks += 1
        elif tag == 'climb':
            t = ('L', e[2])
            require(frames[t] == e[3], 'Native old frame')
            require(len(word['frames'][e[4]]) - len(word['frames'][e[3]]) == e[5], 'Native rank')
            frames[t] = e[4]
        elif tag == 'warp':
            t, symbol = tuple(e[1]), e[2]
            require(frames[t] == e[3], 'Warp old frame')
            frames[t] = e[4]
            if backward:
                symbol = (abs(symbol) + 1000) * (1 if symbol > 0 else -1)
            state[t] = {(source, w[:-1] if w and w[-1] == -symbol else w + (symbol,)): c
                        for (source, w), c in state[t].items()}
        elif tag == 'zero_buffer':
            t = ('Z', e[2])
            if e[1] == 'alloc':
                require(t not in zeros, 'Zero buffer allocated once')
                state[t], frames[t] = {}, 1
                zeros.add(t)
            else:
                require(t in zeros and not state[t], 'Zero buffer returned')
                zeros.remove(t)
        else:
            require(tag in ('phase', 'adapter', 'residual_adapter'), 'Known event')
    require(not zeros, 'No live zero buffer')
    require([frames['L', p] for p in range(n)] == word['final'], 'Live endpoint frames')
    require(all(frames['C', p] == 0 for p in range(8)), 'Owned endpoint frames')
    return state, checks


def line_checks(recipes, word, selected):
    def bit_map(matrix, x):
        return sum(((r & x).bit_count() & 1) << i for i, r in enumerate(matrix))
    seen, columns = set(), 0
    for item in recipes:
        p, inv, rec = item['port'], item['inverse'], item['recipe']
        require((p, inv) not in seen and p in selected, 'Distinct signed line')
        seen.add((p, inv))
        q = word['ports'][p]
        require(q == item['label'] and rec['rank'] == 1, 'Actual native line')
        for side in ('left', 'right'):
            r = rec[side]
            require(not r['phase'] and not any(r['linear_Z4'] + r['quadratic_rows']), 'Exact wrapper phase')
        left, right = rec['left'], rec['right']
        alpha, beta = (Q(1, 2), Q(1, 2)), (Q(1, 2), Q(-1, 2))
        for x in range(512):
            y = bit_map(right['matrix_rows'], x) ^ right['offset']
            actual = {bit_map(left['matrix_rows'], y) ^ left['offset']: alpha,
                      bit_map(left['matrix_rows'], y ^ 1) ^ left['offset']: beta}
            expected = {x: beta if inv else alpha, x ^ q: alpha if inv else beta}
            require(actual == expected, 'Signed line physical kernel')
            columns += 1
    require(seen == {(p, inv) for p in selected for inv in (False, True)}, 'All signed recipes')
    return columns


def main():
    core = load(HERE / 'CLEAN-J-PROGRAMS.json.gz', CORE_PIN)
    old = load(OLD / 'UNIFORM-SIGNED-PROGRAMS.json.gz', SIGNED_PIN)
    s, a = rows(old['signed_S']), rows(old['inverse_S'])
    selected = old['selected_A']
    eye = [{p: Q(1)} for p in range(112)]
    require(product(s, a) == product(a, s) == eye, 'Both inverse orders')
    r = rows(core['R'])
    k = [{j: row[p] / 4 for j, row in enumerate(r) if p in row} for p in range(112)]
    require(product(r, k) == [{j: Q(14)} for j in range(8)], 'Actual full query Gram matrix')
    derived = deepcopy(eye)
    for p, row in enumerate(product(k, r)):
        add(derived[p], row, -1)
    for p in selected:
        add(derived[p], {p: Q(1)}, -1)
    require(derived == s, 'Actual R gives signed S')
    ka = [row if p in selected else {} for p, row in enumerate(k)]
    require(product(r, ka) == [{j: Q(1)} for j in range(8)], 'Selected unit section')
    projection = product(ka, r)
    negative_pi = [{p: Q(-1)} if p in selected else {} for p in range(112)]
    require(product(projection, projection) == projection, 'Oblique projection')
    require(product(projection, a) == negative_pi, 'P S inverse equals minus Pi')
    result = {'schema': 'pr3133-signed-local-extensions-v1', 'source_pins': {'core': CORE_PIN, 'signed': SIGNED_PIN},
              'selected_A': selected, 'S': old['signed_S'], 'inverse_S': old['inverse_S'],
              'line_recipes': old['line_recipes'], 'providers': {}}
    receipt = {'status': 'PASS_PR3133_SIGNED_AND_OBLIQUE_LOCAL_EXTENSIONS', 'providers': {}}
    for provider, item in core['providers'].items():
        word, n = item['canonical'], len(item['canonical']['start'])
        require(n == 632 and len(word['zero_buffers']) == 91, 'Exact new core')
        kernel_columns = line_checks(old['line_recipes'], word, selected)
        recs, reports = {}, {}
        for name in ('forward', 'backward', 'coded_forward', 'coded_backward', 'oblique_backward'):
            source_name = 'coded_backward' if name == 'oblique_backward' else name
            source = deepcopy(old['programs'][source_name])
            before = source.get('input_code', []) + source['prefix']
            after = source['suffix'] + source.get('output_code', [])
            if name == 'oblique_backward':
                before = deepcopy(old['programs']['forward']['prefix']) + before
            for e in before + after:
                if isinstance(e, dict):
                    if e['target'] >= 704:
                        e['target'] += n - 704
                    if e.get('source', -1) >= 704:
                        e['source'] += n - 704
            direction = source['core_orientation']
            retained = item['programs'][direction]
            events = before + retained + after
            state, checks = replay(events, word, direction == 'backward', selected)
            expected = {('L', p): {(('L', p), ()): Q(1)} for p in range(n)}
            expected.update({('C', p): {(('C', p), ()): Q(1)} for p in range(8)})
            expected['C', 0] = {}
            for p in range(112):
                if name.endswith('forward'):
                    if name.startswith('coded'):
                        expected['L', 112 + p] = {(('L', 112 + j), ()): c for j, c in s[p].items()}
                    add(expected['L', 112 + p], {(('L', j), ()): c for j, c in s[p].items()})
                elif name == 'backward':
                    add(expected['L', p], {(('L', 112 + j), ()): c for j, c in s[p].items()}, -1)
                else:
                    expected['L', p] = {(('L', j), ()): c for j, c in a[p].items()}
                    add(expected['L', p], {(('L', 112 + p), ()): Q(-1)})
                    if name == 'oblique_backward' and p in selected:
                        add(expected['L', p], {(('L', p), ()): Q(1)})
                        add(expected['L', 112 + p], {(('L', p), ()): Q(-1)})
            require(all(state[f] == row for f, row in expected.items()), 'All arbitrary input columns: ' + name)
            require(all(not row for f, row in state.items() if f[0] == 'Z'), 'All zero buffer columns')
            counts = Counter(e['kind'] for e in events if isinstance(e, dict))
            scalar = sum(price(e[1]) for e in events if isinstance(e, list) and e[0] == 'scalar')
            scalar += 2 * (counts['clear_owned'] + counts['physical_copy']) + 8 * counts['physical_add']
            profile = Counter(e[5] for e in retained if e[0] == 'climb')
            profile[1] += counts['intrinsic_line']
            mass = sum(rank * count for rank, count in profile.items())
            require(scalar == (172050 if name == 'oblique_backward' else 171938 if name.startswith('coded') else 164626), 'Full scalar invoice')
            require(mass == (5089 if name == 'oblique_backward' else 5081), 'Full rank invoice')
            recs[name] = {'orientation': direction, 'prefix': before, 'core': retained, 'suffix': after, 'events': events}
            reports[name] = {'arbitrary_live_inputs': n, 'arbitrary_C_inputs': 8, 'restored_helpers': n - 224,
                             'returned_zero_buffers': 91, 'C0_exit': 'zero', 'C1_to_C7_exit': 'identity by non-use',
                             'scalar_frame_checks': checks, 'scalar_real_primitives': scalar, 'native_profile': dict(sorted(profile.items())),
                             'native_rank_mass': mass, 'native_children': sum(profile.values()), 'new_line_children': counts['intrinsic_line'],
                             'new_line_wrappers': 2 * counts['intrinsic_line'], 'exact_signed_line_columns': kernel_columns}
            print(provider, name, scalar, mass, flush=True)
        result['providers'][provider] = {'canonical': word, 'programs': recs}
        receipt['providers'][provider] = reports
    raw = (json.dumps(result, sort_keys=True, separators=(',', ':')) + '\n').encode()
    (HERE / 'SIGNED-EXTENSIONS.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    receipt['payload_sha256'] = sha256(raw).hexdigest()
    receipt['checker_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    receipt['scope'] = 'Ten complete local words; all 632 live and eight private arbitrary input columns; all 91 zero buffers. Exact signed line kernels checked. Full retained native phase review, owner allocation, private hosting, finite precision and complete supplier remain separate obligations.'
    (HERE / 'SIGNED-EXTENSIONS.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], receipt['payload_sha256'])


if __name__ == '__main__':
    main()
