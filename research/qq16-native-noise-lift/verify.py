#!/usr/bin/env python3
"""Exact local native lift of PR3189's one B1,2 child-error channel.

Prepared for commdata2338, with substantial OpenAI Codex assistance.
Apache-2.0. Native vector primitives are credited live input from Tekalign/PR3017.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import tarfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ORIGIN, WIRE, TARGET, OUT = 13489, 344, 26472, 93
EXPECTED = Q(-81921, 262144)
MEMBERS = {
    'slots/local/CANONICAL-WORD.json.gz': '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219',
    'slots/local/CLIFFORD-RECIPES.json': 'd0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731',
    'slots/local/RESIDUAL-ADAPTERS.json': '383f40aadd00a4ac700dfd0d4c22d6c6c0be9a9863116e4d69c7acd23bafae0c',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def decode(raw, cap=12_000_000):
    need(len(raw) <= cap, 'JSON size cap')
    return json.loads(raw, object_pairs_hook=unique)


def load(root=ROOT):
    for entry in decode((HERE / 'SOURCES.json').read_bytes())['files']:
        if entry['usage'] == 'input':
            need(hashlib.sha256((root / entry['path']).read_bytes()).hexdigest()
                 == entry['sha256'], 'source pin: ' + entry['path'])
    path = root / 'research/qq16-native-dirty-fault/native.py'
    native = types.ModuleType('source_authenticated_native')
    exec(compile(path.read_bytes(), str(path), 'exec'), native.__dict__)
    packet = decode(gzip.decompress((root / 'research/joint-query/certificate.json.gz').read_bytes()))
    need(packet['schema'] == 'conserved-qq16-full-cover-native-words-v1', 'packet schema')
    objects = []
    with tarfile.open(root / 'research/community-frontier1042-audit/selected-replay.tar.gz') as archive:
        for name, pin in MEMBERS.items():
            members = [m for m in archive.getmembers() if m.name == name]
            need(len(members) == 1 and members[0].isfile()
                 and members[0].size <= 12_000_000, 'unique regular bounded member')
            raw = archive.extractfile(members[0]).read()
            need(hashlib.sha256(raw).hexdigest() == pin, 'archive member pin: ' + name)
            objects.append(decode(gzip.decompress(raw) if name.endswith('.gz') else raw))
    prior = decode((root / 'research/qq16-noise-lattice-audit/RESULT.json').read_bytes())
    witness = prior['cases']['B_1_2']['child_attainment']
    need(witness['origin'] == {'event': ORIGIN, 'kind': 'climb', 'wire': WIRE}
         and witness['attainment'] == {'event': TARGET, 'wire': OUT,
                                      'bits': 18, 'coefficient': str(EXPECTED)}, 'predecessor witness')
    return native, packet, *objects


def expand(packet):
    result, core_start = [], None
    for e in packet['programs']['B_1_2']:
        if e[0] == 'retained_core':
            need(core_start is None and e[1:3] == ['backward', 1], 'one backward stage-one core')
            core_start = len(result)
            result.extend(packet['core_words']['backward'])
        elif e[0] in ('private_sweep', 'cover_sweep'):
            result.extend(e[2])
        else:
            result.append(e)
    need(core_start == 1864 and len(result) == 27019, 'expanded word binding')
    need(result[ORIGIN] == ['climb', 'A', WIRE, 226, 236, 1], 'injection child')
    need(result[TARGET] == ['scalar', ['add', ['L', OUT], ['L', 103], -1, 8], 1], 'attaining scalar')
    need(all(e[0] in ('scalar', 'climb', 'adapter', 'residual_adapter', 'phase')
             for e in result[ORIGIN + 1:]), 'suffix is wholly inside the local native core')
    return result


def reg(token):
    kind, at = token
    need(kind in ('L', 'C') and type(at) is int
         and 0 <= at < (704 if kind == 'L' else 8), 'register')
    return at + (704 if kind == 'C' else 0)


def scalar_channel(events, origin=ORIGIN, wire=WIRE):
    values = [Q(0)] * 712
    values[wire] = Q(1)
    peak, attaining, cut = 0, None, None
    for at in range(origin + 1, len(events)):
        e = events[at]
        if e[0] == 'scalar':
            g, dst = e[1], reg(e[1][1])
            if g[0] == 'clear':
                values[dst] = Q(0)
            elif g[0] == 'scale':
                values[dst] *= Q(g[2], g[3])
            else:
                need(g[0] == 'add', 'scalar kind')
                values[dst] += Q(g[3], g[4]) * values[reg(g[2])]
            bits = values[dst].denominator.bit_length() - 1
            if bits > peak:
                peak, attaining = bits, [at, dst, str(values[dst])]
        if at == TARGET:
            cut = values[OUT]
    return {'guard': peak, 'first_attainment': attaining, 'target': str(cut),
            'endpoint': [str(v) for v in values]}


def indexes(recipes):
    children = {(r['old'], r['new']): r for r in recipes['children']}
    endpoints = {(r['role'], r['port']): r for r in recipes['endpoint_adapters']}
    need(len(children) == len(recipes['children']) and len(endpoints) == 224, 'recipe uniqueness')
    return children, endpoints


def step(N, e, state, children, endpoints, residuals):
    kind = e[0]
    if kind == 'scalar':
        g, dst = e[1], reg(e[1][1])
        if g[0] == 'clear':
            need(dst >= 704, 'owned CLEAR only')
            state[dst] = N.ZERO
        elif g[0] == 'scale':
            state[dst] = N.scaled(state[dst], Q(g[2], g[3]))
        else:
            need(g[0] == 'add', 'scalar operation')
            state[dst] = N.plus(state[dst], N.scaled(state[reg(g[2])], Q(g[3], g[4])))
    elif kind == 'climb':
        _, _, dst, old, new, rank = e
        recipe = children[old, new]
        need(recipe['rank'] == rank, 'child rank')
        if state[dst] != N.ZERO:
            state[dst] = N.recipe(state[dst], recipe)
    elif kind == 'adapter':
        _, direction, dst, _ = e
        need(direction in ('old_to_new', 'new_to_old'), 'adapter direction')
        if direction == 'old_to_new' and dst < 112:
            state[dst] = N.mono(state[dst], N.monomial_key(endpoints['source', dst]['left']))
        elif direction == 'new_to_old' and 112 <= dst < 224:
            state[dst] = N.mono(state[dst], N.monomial_key(endpoints['target', dst-112]['left']), True)
    elif kind == 'residual_adapter':
        direction, dst, a = e[1:4]
        b = e[4] if len(e) == 5 else 1
        need(direction in ('pre', 'post'), 'residual direction')
        key = str(a) if b == 1 else f'{a}:{b}'
        part = 'right' if direction == 'pre' else 'left'
        state[dst] = N.mono(state[dst], N.monomial_key(residuals['recipes'][key][part]), True)
    else:
        need(kind == 'phase', 'unknown local native event')
        return None
    return dst


def summary(value):
    re, im, exponent = value
    return {'denominator_exponent': exponent, 'sha256': digest(value),
            'real_histogram': dict(sorted(Counter(str(Q(v, 1 << exponent)) for v in re).items())),
            'imag_histogram': dict(sorted(Counter(str(Q(v, 1 << exponent)) for v in im).items())),
            'squared_norm': str(Q(sum(v*v for v in re + im), 1 << (2*exponent)))}


def native_channel(N, events, word, recipes, residuals, origin=ORIGIN, wire=WIRE,
                   injection=None, stop=None):
    children, endpoints = indexes(recipes)
    injected = N.frame(word['frames'][236]) if injection is None else injection
    state = [N.ZERO] * 712
    state[wire] = injected
    cut, first, peak, max_component = None, None, injected[2], Q(0)
    trace = hashlib.sha256()
    occupied = Counter()
    occupied_residuals = []
    occupied_native_events = []
    for at in range(origin + 1, (stop + 1) if stop is not None else len(events)):
        e = events[at]
        dst = step(N, e, state, children, endpoints, residuals)
        if dst is not None:
            value = state[dst]
            if value != N.ZERO:
                occupied[e[0]] += 1
                if e[0] not in ('scalar', 'phase'):
                    occupied_native_events.append([at, e])
                if e[0] == 'residual_adapter':
                    occupied_residuals.append([at, dst, digest(value)])
            if value[2] > peak:
                peak = value[2]
                first = [at, dst]
            bound = Q(max(abs(v) for v in value[0] + value[1]), 1 << value[2])
            max_component = max(max_component, bound)
            trace.update(canonical([at, dst, digest(value)]) + b'\n')
        if at == TARGET:
            cut = state[OUT]
    return state, {'injection': {'real': list(injected[0]), 'imag': list(injected[1]),
                                'exponent': injected[2], **summary(injected)},
                   'target': summary(cut) if cut is not None else None,
                   'guard': peak, 'first_attainment': first,
                   'max_abs_component': str(max_component),
                   'changed_field_trace_sha256': trace.hexdigest(),
                   'occupied_event_counts': dict(sorted(occupied.items())),
                   'occupied_native_events': occupied_native_events,
                   'occupied_residuals': occupied_residuals}, cut


def build(root=ROOT):
    N, packet, word, recipes, residuals = load(root)
    events = expand(packet)
    projection = scalar_channel(events)
    need(projection['target'] == str(EXPECTED) and projection['guard'] == 18, 'projection positive control')
    state, result, cut = native_channel(N, events, word, recipes, residuals)
    need(cut == N.scaled(N.ONE, EXPECTED), 'native attaining vector')
    need(result['guard'] == 18, 'physical completed-event guard')
    need(result['injection']['exponent'] == 0, 'integer Gaussian injection')
    need(set(result['injection']['real'] + result['injection']['imag']) <= {-1, 0, 1}, 'bounded injection')
    need(Q(result['injection']['squared_norm']) == 512, 'injection norm')
    need((EXPECTED * (1 << 17)).denominator == 2, 'seventeen-position negative control')
    need((EXPECTED * (1 << 18)).denominator == 1, 'eighteen-position positive control')
    output = {str(i): summary(v) for i, v in enumerate(state) if v != N.ZERO}
    return {'schema': 'qq16-native-noise-lift/v1', 'program': 'B_1_2',
            'core_offset': 1864, 'event_count': len(events),
            'origin': {'event': ORIGIN, 'wire': WIRE, 'instruction': events[ORIGIN]},
            'attainment': {'event': TARGET, 'wire': OUT, 'instruction': events[TARGET],
                          'coefficient': str(EXPECTED)},
            'suffix_event_counts': dict(sorted(Counter(e[0] for e in events[ORIGIN+1:]).items())),
            'suffix_sha256': digest(events[ORIGIN+1:]),
            'projection': projection, 'native': result, 'nonzero_outputs': output,
            'nonzero_data_fields': [i for i in range(224) if state[i] != N.ZERO],
            'nonzero_helpers': [i for i in range(224, 704) if state[i] != N.ZERO],
            'nonzero_private': [i for i in range(704, 712) if state[i] != N.ZERO]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='exclusively create an absent receipt')
    args = parser.parse_args()
    result = build()
    if args.write:
        with args.write.open('x') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
    else:
        want = decode((HERE / 'RESULT.json').read_bytes())
        need(canonical(result) == canonical(want), 'complete receipt differs')
    print('PASS_QQ16_NATIVE_NOISE_LIFT guard=18 coefficient=-81921/262144'
          f" data_fields={len(result['nonzero_data_fields'])}"
          f" helpers={len(result['nonzero_helpers'])} private={len(result['nonzero_private'])}")


if __name__ == '__main__':
    main()
