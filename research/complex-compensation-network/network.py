# SPDX-License-Identifier: Apache-2.0
"""Restored dyadic target/helper networks on the selected complex boundary.

conorholds, with substantial OpenAI Codex assistance.
Basis conjugation and the forest starting point are credited in README.md.
"""
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def strict_json(raw):
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, 'duplicate JSON key: ' + key)
            out[key] = value
        return out
    def nonfinite(value):
        raise ValueError('nonfinite JSON: ' + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load():
    pins = strict_json((HERE / 'REFERENCE-PINS.json').read_bytes())
    names = {'CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz',
             'LOCAL-CHECKS.json', 'INDEPENDENT-LOCAL-REPLAY.json',
             'native_emitter.py', 'native_auditor.py'}
    require(set(pins) == names, 'reference inventory')
    raw = {}
    for name in sorted(names):
        data = (HERE / 'reference' / name).read_bytes()
        require(sha(data) == pins[name], 'reference hash: ' + name)
        raw[name] = gzip.decompress(data) if name.endswith('.gz') else data
    source_rows = strict_json((HERE / 'SOURCES.json').read_bytes())['files']
    for name, suffix in [('native_emitter.py', '/hpe_emit_local.py'),
                         ('native_auditor.py', '/hpe_audit_local.py')]:
        matches = [r for r in source_rows if r['path'].endswith(suffix)]
        require(len(matches) == 1 and sha(raw[name]) == matches[0]['sha256'],
                'native executable provenance: ' + name)
    word = strict_json(raw['CANONICAL-WORD.json.gz'])
    recipe = strict_json((HERE / 'RECIPE.json').read_bytes())
    require(sha(raw['CANONICAL-WORD.json.gz']) == recipe['word_sha256'], 'word payload')
    require((word['v'], word['R'], word['h']) == (112, 480, 9), 'selected geometry')
    return word, recipe, strict_json(raw['LOCAL-PROGRAMS.json.gz']), strict_json(raw['LOCAL-CHECKS.json']), pins


def add_price(q):
    q = Q(q)
    if not q:
        return 0
    a, b = abs(q.numerator), q.denominator
    require(b & (b - 1) == 0, 'non-dyadic add')
    return 2 * (3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1)


def price(gate):
    if gate[0] == 'add':
        return add_price(Q(gate[3], gate[4]))
    require(gate[0] == 'scale', 'gate opcode')
    q = Q(gate[2], gate[3]); a, b = abs(q.numerator), q.denominator
    require(a and a & (a - 1) == 0 and b & (b - 1) == 0, 'scale is not a power of two')
    return 2 * (abs(a.bit_length() - b.bit_length()) + int(q < 0))


def add(t, s, q):
    q = Q(q)
    require(t != s and q != 0, 'zero or aliased addition')
    return ['add', t, s, q.numerator, q.denominator, 0]


def scale(t, q):
    q = Q(q)
    require(q > 0 and q != 1, 'trivial or negative scale')
    out = ['scale', t, q.numerator, q.denominator, 0]
    price(out)
    return out


def inverse(gate):
    out = gate.copy()
    if out[0] == 'add':
        out[3] *= -1
    else:
        out[2], out[3] = out[3], out[2]
    return out


def dual(gate):
    # Inverse transpose is a homomorphism: retain chronological order.
    out = inverse(gate)
    if out[0] == 'add':
        out[1], out[2] = out[2], out[1]
    return out


def matrix(word, sources, grid):
    v = word['v']; index = {s: j for j, s in enumerate(sources)}
    require(len(index) == len(sources) and sources == sorted(index), 'ordered unique helpers')
    require(sources == sorted({e[2] for e in word['compensation']}), 'all original compensation helpers')
    require(all(2*v <= s < 2*v+word['R'] and word['start'][s] == 0
                and word['final'][s] == 1 for s in sources), 'ineligible helper')
    out = [[0] * len(sources) for _ in range(v)]
    seen = set()
    for tag, t, s, n, d, f in word['compensation']:
        require(tag == 'add' and v <= t < 2*v and f == 0 and n != 0 and grid % d == 0,
                'original compensation shape')
        require((t, s) not in seen, 'duplicate matrix entry')
        seen.add((t, s)); out[t-v][index[s]] = n * (grid // d)
    return out


def construct(word, recipe):
    require(recipe['schema_version'] == 1, 'recipe schema')
    grid = recipe['grid_denominator']; sources = recipe['sources']; v = word['v']
    require(type(grid) is int and grid == 256, 'coefficient grid')
    require(isinstance(sources, list) and all(type(s) is int for s in sources), 'helper IDs')
    original = matrix(word, sources, grid); residual = [r.copy() for r in original]
    prep = []; operations = recipe['operations']
    require(isinstance(operations, list) and operations, 'missing basis word')
    for operation in operations:
        require(isinstance(operation, list) and len(operation) == 5, 'basis operation shape')
        kind, a, b, num, den = operation
        require(kind in ('T', 'H', 'TS', 'HS') and type(a) is int
                and type(num) is int and type(den) is int, 'basis operation types')
        require(num != 0 and abs(num) <= 2 and den in (1, 2)
                and Q(num, den).numerator == num and Q(num, den).denominator == den, 'basis alphabet')
        limit = v if kind.startswith('T') else len(sources)
        require(0 <= a < limit, 'basis operand range')
        if kind.endswith('S'):
            require(b is None and Q(num, den) in (Q(1, 2), Q(2)), 'scale alphabet')
            values = residual[a] if kind == 'TS' else [r[a] for r in residual]
            require(all(x % den == 0 for x in values), 'scale leaves exact coefficient grid')
            changed = [num * (x // den) for x in values]
            if kind == 'TS':
                residual[a] = changed; prep.append(scale(v+a, Q(num, den)))
            else:
                for row, x in zip(residual, changed):
                    row[a] = x
                prep.append(scale(sources[a], Q(den, num)))
        else:
            require(type(b) is int and 0 <= b < limit and a != b, 'shear operand range or alias')
            if kind == 'T':
                require(all(x % den == 0 for x in residual[b]), 'target shear coefficient grid')
                residual[a] = [x + num * (y // den) for x, y in zip(residual[a], residual[b])]
                prep.append(add(v+a, v+b, Q(num, den)))
            else:
                require(all(row[a] % den == 0 for row in residual), 'helper shear coefficient grid')
                for row in residual:
                    row[b] -= num * (row[a] // den)
                prep.append(add(sources[a], sources[b], Q(num, den)))
    middle = [add(v+i, sources[j], Q(x, grid)) for i, row in enumerate(residual)
              for j, x in enumerate(row) if x]
    gates = prep + middle + [inverse(e) for e in reversed(prep)]
    report = dict(before_real=sum(map(price, word['compensation'])), after_real=sum(map(price, gates)),
                  before_macros=len(word['compensation']), after_macros=len(gates),
                  boundary_operations=len(prep))
    report['saving_real'] = report['before_real'] - report['after_real']
    require(report == recipe['claimed'], 'complete paid recipe counts')
    require(report['saving_real'] > 0 and report['after_macros'] < report['before_macros'], 'no complete gain')
    require(all(word['start'][r] == 0 for gate in gates
                for r in (gate[1:3] if gate[0] == 'add' else gate[1:2])), 'nonzero-frame boundary gate')
    report.update(middle_macros=len(middle), active_helpers=len(sources),
                  target_operations=sum(e[0].startswith('T') for e in operations),
                  helper_operations=sum(e[0].startswith('H') for e in operations),
                  scale_operations=sum(e[0].endswith('S') for e in operations),
                  coefficient_histogram=dict(sorted(Counter(str(Q(x, grid)) for row in residual for x in row if x).items())))
    return gates, report, prep, residual


def event(gate, backward=False):
    gate = dual(gate) if backward else gate
    if gate[0] == 'add':
        op = ['add', ['L', gate[1]], ['L', gate[2]], gate[3], gate[4]]
    else:
        op = ['scale', ['L', gate[1]], gate[2], gate[3]]
    return ['scalar', op, gate[-1]]


def splice(word, programs, replacement, cleanup):
    result = {}
    for name, events in programs.items():
        require(name in ('forward', 'backward'), 'orientation')
        back = name == 'backward'
        end = events.index(['phase', 'entry_adapters'])
        expected = [['phase', 'zero_frame_precondition']] + [event(g, back) for g in word['precondition'] + word['compensation']]
        require(events[:end] == expected, 'baseline boundary binding')
        result[name] = [['phase', 'zero_frame_precondition']] + [event(g, back) for g in word['precondition'] + replacement] + events[end:]
        start = result[name].index(['phase', 'full_frame_cleanup'])+1
        finish = start+len(word['cleanup'])
        require(result[name][start:finish] == [event(g, back) for g in word['cleanup']], 'baseline cleanup binding')
        result[name][start:finish] = [event(g, back) for g in cleanup]
        require([e for e in result[name] if e[0] != 'scalar'] ==
                [e for e in events if e[0] != 'scalar'], 'changed non-scalar event')
    return result
