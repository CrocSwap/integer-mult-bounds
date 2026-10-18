"""Exact finite witnesses for the separately calibrated endpoint-gauge model.

Python standard library only. The all-size theorem is a written proof;
finite witnesses do not prove the complete multiplication theorem.
"""
from collections import Counter, deque
from pathlib import Path
import hashlib
import json
import sys


class Rejected(ValueError):
    pass


def check(condition, reason):
    if not condition:
        raise Rejected(reason)


def ports(h):
    check(type(h) is int and h >= 6 and h % 2 == 0, 'even dimension at least six')
    return [(i, j) for j in range(h) for i in range(h)
            if i != j and i // (h//2) == j // (h//2)]


def change(state, mask, sign, h):
    answer = state
    for axis in range(h):
        if mask >> axis & 1:
            shift = 2*axis
            value = ((state >> shift & 3) + sign) % 4
            answer = (answer & ~(3 << shift)) | (value << shift)
    return answer


def corner(h, i, j):
    return ((1 << h)-1) ^ (1 << i) ^ (1 << j)


def direct(h, fused=False):
    ps = ports(h)
    word = [('add', h+t, j, -1) for t, (_, j) in enumerate(ps)]
    for j in range(h):
        previous = 0
        for t, (i, source) in enumerate(ps):
            if source != j:
                continue
            current = corner(h, i, j)
            if previous == 0:
                word.append(('phase', j, current, 1))
            else:
                removed, added = previous & ~current, current & ~previous
                if fused:
                    word += [('translate', j, removed, 1),
                             ('phase', j, removed | added, 1)]
                else:
                    word += [('phase', j, removed, -1), ('phase', j, added, 1)]
            word.append(('add', h+t, j, 1))
            previous = current
        word.append(('phase', j, previous, -1))
    return word


def stress(h):
    """Overlapping target gauges, with the negative reads moved after positives."""
    ps = ports(h)
    gauges = {h+t: (1 << ((i+j) % h), (-1 if t % 2 else 1))
              for t, (i, j) in enumerate(ps)}
    word = [('phase', target, mask, sign) for target, (mask, sign) in gauges.items()]
    original = direct(h)
    reads_late = [op for op in original if op[0] == 'add' and op[3] == -1]
    for op in [op for op in original if not (op[0] == 'add' and op[3] == -1)] + reads_late:
        if op[0] == 'add':
            _, target, source, _ = op
            mask, sign = gauges[target]
            word += [('phase', source, mask, sign), op, ('phase', source, mask, -sign)]
        else:
            word.append(op)
    word += [('phase', target, mask, -sign) for target, (mask, sign) in gauges.items()]
    return word


def validate(h, word):
    ps = ports(h)
    width = h + len(ps)
    gauge = [0]*width
    reads = Counter()
    hist = Counter()
    translations = 0
    for op in word:
        check(isinstance(op, (tuple, list)) and len(op) == 4, 'operation shape')
        kind, a, b, sign = op
        check(type(a) is int and 0 <= a < width and type(b) is int
              and type(sign) is int and sign in (-1, 1), 'operation carrier')
        if kind == 'add':
            check(h <= a < width and 0 <= b < h and b == ps[a-h][1], 'declared-source read only')
            i, j = ps[a-h]
            relative = 0
            for axis in range(h):
                relative |= (((gauge[b] >> (2*axis) & 3) - (gauge[a] >> (2*axis) & 3)) % 4) << (2*axis)
            wanted = change(0, corner(h, i, j), 1, h) if sign == 1 else 0
            check(relative == wanted, 'individual read calibration')
            reads[a, sign] += 1
        elif kind in ('phase', 'translate'):
            check(0 < b < 1 << h, 'mask range')
            if kind == 'phase':
                check(b.bit_count() <= h-2, 'phase rank cap')
                hist[b.bit_count()] += 1
                gauge[a] = change(gauge[a], b, sign, h)
            else:
                check(sign == 1, 'translation is an involution')
                translations += 1
                gauge[a] = change(gauge[a], b, 2, h)
        else:
            raise Rejected('unknown operation')
    check(not any(gauge), 'closed endpoint gauges')
    check(reads == Counter({(a, sign): 1 for a in range(h, width) for sign in (-1, 1)}), 'two reads per port')
    return dict(roles=width, scalar_adds=sum(reads.values()),
                phase_histogram={str(r): hist[r] for r in sorted(hist)},
                phase_calls=sum(hist.values()), rank_mass=sum(r*n for r, n in hist.items()),
                translations=translations)


def normalize(h, word):
    """A rank-mass detour normalizer; the all-p existence argument is separate."""
    original = validate(h, word)
    check(all(op[0] != 'translate' for op in word), 'oriented normalizer alphabet')
    ps = ports(h)
    gauge = [0]*original['roles']
    target_bill = Counter()
    visits = {}
    output = [('add', h+t, j, -1) for t, (_, j) in enumerate(ps)]
    def emit(op):
        if output and op[0] == 'phase' and output[-1][:3] == op[:3] and output[-1][3] == -op[3]:
            output.pop()
        else:
            output.append(op)
    for kind, a, b, sign in word:
        if kind == 'phase':
            gauge[a] = change(gauge[a], b, sign, h)
            if a < h:
                emit((kind, a, b, sign))
            else:
                target_bill[a] += b.bit_count()
        elif sign == 1:
            q = gauge[a]
            path = []
            for axis in range(h):
                value = q >> (2*axis) & 3
                path.extend([('phase', b, 1 << axis, -1 if value == 3 else 1)]
                            * min(value, 4-value))
            visits[a] = (len(path), target_bill[a])
            for k, wire, mask, orientation in reversed(path):
                emit((k, wire, mask, -orientation))
            emit(('add', a, b, 1))
            for op in path:
                emit(op)
    for a, (distance, prefix) in visits.items():
        check(distance <= prefix and distance <= target_bill[a]-prefix, 'both target paths pay the detour')
    normalized = validate(h, output)
    check(normalized['rank_mass'] <= original['rank_mass'], 'rank-mass monotonicity')
    check(all(op[1] < h for op in output if op[0] == 'phase'), 'source-only normalized phases')
    return output


def symbolic(h, word):
    """Sparse full old-input matrix over integer Laurent monomials modulo z_i^4=1."""
    info = validate(h, word)
    rows = [{(a, 0): 1} for a in range(info['roles'])]
    for kind, a, b, sign in word:
        if kind == 'add':
            for key, value in rows[b].items():
                rows[a][key] = rows[a].get(key, 0) + sign*value
                if not rows[a][key]:
                    del rows[a][key]
        else:
            increment = sign if kind == 'phase' else 2
            rows[a] = {(input_column, change(exponent, b, increment, h)): value
                       for (input_column, exponent), value in rows[a].items()}
    expected = [{(a, 0): 1} for a in range(info['roles'])]
    for t, (i, j) in enumerate(ports(h)):
        expected[h+t].update({(j, change(0, corner(h, i, j), 1, h)): 1, (j, 0): -1})
    check(rows == expected, 'full symbolic old-input operator')
    return info


def rotate(z, exponent):
    a, b = z
    return ((a, b), (-b, a), (-a, -b), (b, -a))[exponent % 4]


def fourier(h, word):
    """Independent dense Gaussian-integer replay through the intrinsic F2 projector."""
    width = h + len(ports(h))
    full = (1 << h)-1
    normals = [full ^ (1 << i) for i in range(h)]
    zero, one = (0, 0), (1, 0)
    peak = 1
    for character in range(1 << h):
        def exponent(mask):
            projected = 0
            for axis in range(h):
                if mask >> axis & 1 and (normals[axis] & character).bit_count() % 2:
                    projected ^= normals[axis]
            return projected.bit_count() % 4
        rows = [[one if a == b else zero for b in range(width)] for a in range(width)]
        for kind, a, b, sign in word:
            if kind == 'add':
                rows[a] = [(x+sign*u, y+sign*v) for (x, y), (u, v) in zip(rows[a], rows[b])]
            else:
                if kind == 'phase':
                    power = sign*exponent(b)
                else:
                    translation = 0
                    for axis in range(h):
                        if b >> axis & 1:
                            translation ^= normals[axis]
                    power = 2*((translation & character).bit_count() % 2)
                rows[a] = [rotate(z, power) for z in rows[a]]
            peak = max(peak, sum(abs(x)+abs(y) for x, y in rows[a]))
        wanted = [[one if a == b else zero for b in range(width)] for a in range(width)]
        for t, (i, j) in enumerate(ports(h)):
            x, y = rotate(one, exponent(corner(h, i, j)))
            wanted[h+t][j] = (x-1, y)
        check(rows == wanted, 'dense dirty operator at every Fourier character')
    return dict(operator_entries=(1 << h)*width*width, peak_gaussian_row_l1=peak)


def metric_cases():
    states = 0
    for h in (4, 6):
        masks = [mask for mask in range(1, 1 << h) if mask.bit_count() <= h-2]
        distance = {0: 0}
        queue = deque([0])
        while queue:
            state = queue.popleft()
            for mask in masks:
                for sign in (-1, 1):
                    nxt = change(state, mask, sign, h)
                    if nxt not in distance:
                        distance[nxt] = distance[state]+1
                        queue.append(nxt)
        check(len(distance) == 4**h, 'complete phase-group coverage')
        for i in range(h):
            for j in range(h):
                if i != j:
                    difference = change(change(0, 1 << i, -1, h), 1 << j, 1, h)
                    check(distance[difference] == 2, 'oriented mixed-sign distance')
        states += len(distance)
    return states


def verify():
    cases = []
    for h in (6, 8, 10):
        noisy = stress(h)
        for name, word in [('oriented', direct(h)), ('translation-closed', direct(h, True)),
                           ('interleaved', noisy), ('source-detours', normalize(h, noisy))]:
            info = symbolic(h, word)
            info.update(fourier(h, word))
            if name in ('oriented', 'translation-closed', 'source-detours'):
                check(info['rank_mass'] == h*(3*h-8), 'attained rank-mass formula')
                check(info['peak_gaussian_row_l1'] == 3, 'complete growth control')
            if name == 'oriented':
                check(info['phase_calls'] == h*(h-2) and info['translations'] == 0, 'oriented inventory')
            if name == 'translation-closed':
                check(info['phase_calls'] == h*h//2 and info['translations'] == h*(h-4)//2, 'translation invoice')
            encoded = json.dumps(word, separators=(',', ':')).encode()
            cases.append(dict(h=h, mode=name, word_sha256=hashlib.sha256(encoded).hexdigest(), **info))
    return dict(status='PASS_CALIBRATED_ENDPOINT_TOURS', cases=cases,
                phase_group_states=metric_cases(), new_kappa_claimed=False,
                scope='separate restored sources; two individually calibrated reads per separate dirty target')


if __name__ == '__main__':
    check(len(sys.argv) <= 2, 'usage: verify.py [NEW_RECEIPT.json]')
    if len(sys.argv) == 2:
        check(not Path(sys.argv[1]).exists(), 'existing output refused')
    result = verify()
    text = json.dumps(result, sort_keys=True, indent=2)+'\n'
    if len(sys.argv) == 2:
        with Path(sys.argv[1]).open('x') as stream:
            stream.write(text)
    print(text, end='')
