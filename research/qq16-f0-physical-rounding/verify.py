"""Deterministic component rounding in the literal native QQ16 F0 word.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
Exact vector primitives are retained unchanged from Tekalign/PR3017.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import tarfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MEMBERS = {
    'slots/local/CANONICAL-WORD.json.gz': '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219',
    'slots/local/CLIFFORD-RECIPES.json': 'd0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731',
    'slots/local/RESIDUAL-ADAPTERS.json': '383f40aadd00a4ac700dfd0d4c22d6c6c0be9a9863116e4d69c7acd23bafae0c',
}
N = types.ModuleType('exact_native_pr3017')
_NATIVE = HERE / 'vendor/pr3017/native.py'
# Authenticate source, and compile bytes rather than loading cached bytecode.
if hashlib.sha256(_NATIVE.read_bytes()).hexdigest() != '999eb1230798b25821de7771ecfa86381e137124059b30ccef167169d176ee8e':
    raise ValueError('vendored native source pin')
exec(compile(_NATIVE.read_bytes(), str(_NATIVE), 'exec'), N.__dict__)
need = N.need


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


def read_json(path, limit=1_000_000):
    raw = path.read_bytes()
    need(len(raw) <= limit, 'JSON size bound')
    return json.loads(raw, object_pairs_hook=unique)


def load(root=ROOT):
    sources = read_json(HERE / 'SOURCES.json')
    for entry in sources['files']:
        if entry['usage'] == 'input':
            raw = (root / entry['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == entry['sha256'], 'source pin: ' + entry['path'])
    objects = []
    with tarfile.open(root / 'research/community-frontier1042-audit/selected-replay.tar.gz') as archive:
        for name, expected in MEMBERS.items():
            matches = [m for m in archive.getmembers() if m.name == name]
            need(len(matches) == 1 and matches[0].isfile() and matches[0].size <= 12_000_000,
                 'unique bounded regular archive member')
            raw = archive.extractfile(matches[0]).read()
            need(hashlib.sha256(raw).hexdigest() == expected, 'archive member pin: ' + name)
            payload = gzip.decompress(raw) if name.endswith('.gz') else raw
            need(len(payload) <= 12_000_000, 'archive payload bound')
            objects.append(json.loads(payload, object_pairs_hook=unique))
    packet_raw = gzip.decompress((root / 'research/joint-query/certificate.json.gz').read_bytes())
    need(len(packet_raw) <= 12_000_000, 'certificate payload bound')
    packet = json.loads(packet_raw, object_pairs_hook=unique)
    need(packet['schema'] == 'conserved-qq16-full-cover-native-words-v1', 'certificate schema')
    return (packet, *objects)


def expand(packet):
    events = []
    for event in packet['programs']['F_0']:
        if event[0] == 'retained_core':
            need(event[1:3] == ['forward', 0], 'forward stage zero')
            events.extend(packet['core_words']['forward'])
        elif event[0] in ('cover_sweep', 'private_sweep'):
            events.extend(event[2])
        else:
            events.append(event)
    need(len(events) == 26099, 'literal event count')
    need(Counter(e[0] for e in events) == {
        'scalar': 21025, 'climb': 3486, 'adapter': 1090,
        'residual_adapter': 480, 'phase': 10, 'native_line': 8}, 'event inventory')
    need(events[3887] == ['scalar', ['add', ['L', 112], ['L', 224], -1, 2], 0], 'first rounding site')
    need(events[4060] == ['scalar', ['add', ['L', 139], ['L', 224], -1, 2], 0], 'second rounding site')
    return events


def reg(token):
    kind, index = token
    need(kind in ('L', 'C') and type(index) is int, 'register token')
    need(0 <= index < (704 if kind == 'L' else 8), 'register bound')
    return index + 704 * (kind == 'C')


@lru_cache(32768)
def rn_integer(n, bits):
    """RN-even of an integer significand; exponent is irrelevant and unbounded."""
    need(type(bits) is int and 2 <= bits <= 256, 'significand bound')
    sign, a = (-1 if n < 0 else 1), abs(n)
    shift = max(0, a.bit_length() - bits)
    if not shift:
        return n
    quotient, remainder = divmod(a, 1 << shift)
    if 2 * remainder > 1 << shift or (2 * remainder == 1 << shift and quotient % 2):
        quotient += 1
    return sign * (quotient << shift)


def rounded(value, bits):
    return N.vector((rn_integer(x, bits) for x in value[0]),
                    (rn_integer(x, bits) for x in value[1]), value[2])


def component_hist(value):
    return {part: dict(sorted(Counter(str(Q(x, 2**value[2])) for x in row).items()))
            for part, row in zip(('real', 'imag'), value[:2])}


def squared_norm(value):
    return Q(sum(x*x for x in value[0] + value[1]), 2**(2*value[2]))


def initial(bits, signal=Q(1), dirty=True):
    state = [N.ZERO] * 712
    state[112] = N.scaled(N.ONE, signal)
    if dirty:
        state[224] = N.scaled(N.ONE, signal * 2**(bits + 12))
    return state


def execute(events, packet, recipes, residuals, state, bits=None, round_at=None):
    """Direct physical vectors; no scalar projection or frame reduction executes the word."""
    children = {(r['old'], r['new']): r for r in recipes['children']}
    adapters = {(r['role'], r['port']): r for r in recipes['endpoint_adapters']}
    need(len(children) == len(recipes['children']) and len(adapters) == 224, 'unique native recipes')
    state, faults = list(state), []
    for index, event in enumerate(events):
        kind = event[0]
        if kind == 'scalar':
            gate = event[1]
            dst = reg(gate[1])
            if gate[0] == 'clear':
                need(dst >= 704, 'only owned CLEAR')
                state[dst] = N.ZERO
            elif gate[0] == 'scale':
                coefficient = Q(gate[2], gate[3])
                n = abs(coefficient.numerator)
                need(n > 0 and n & (n-1) == 0, 'exact power-of-two SCALE')
                state[dst] = N.scaled(state[dst], coefficient)
            else:
                need(gate[0] == 'add', 'known scalar operation')
                src = reg(gate[2])
                need(src != dst, 'distinct ADD operands')
                coefficient = Q(gate[3], gate[4])
                product = N.scaled(state[src], coefficient)
                if bits is not None:
                    need(rounded(product, bits) == product, 'exact scalar coefficient product on witness')
                exact = N.plus(state[dst], product)
                actual = rounded(exact, bits) if bits is not None and (
                    round_at is None or index in round_at) else exact
                if actual != exact:
                    delta = N.plus(actual, N.scaled(exact, Q(-1)))
                    faults.append({'event': index, 'gate': gate, 'exact': component_hist(exact),
                                   'rounded': component_hist(actual), 'error': component_hist(delta)})
                state[dst] = actual
        elif kind == 'climb':
            _, _, dst, old, new, rank = event
            recipe = children[old, new]
            need(recipe['rank'] == rank, 'child rank')
            if state[dst] != N.ZERO:
                state[dst] = N.recipe(state[dst], recipe)
        elif kind == 'adapter':
            _, direction, dst, _ = event
            if direction == 'old_to_new' and dst < 112:
                state[dst] = N.mono(state[dst], N.monomial_key(adapters['source', dst]['left']))
            elif direction == 'new_to_old' and 112 <= dst < 224:
                state[dst] = N.mono(state[dst], N.monomial_key(adapters['target', dst-112]['left']), True)
            else:
                need(direction in ('old_to_new', 'new_to_old'), 'adapter direction')
        elif kind == 'residual_adapter':
            direction, dst, a = event[1:4]
            b = event[4] if len(event) == 5 else 1
            need(direction in ('pre', 'post'), 'residual direction')
            key = str(a) if b == 1 else f'{a}:{b}'
            part = 'right' if direction == 'pre' else 'left'
            state[dst] = N.mono(state[dst], N.monomial_key(residuals['recipes'][key][part]), True)
        elif kind == 'native_line':
            dst = reg(event[1])
            state[dst] = N.recipe(state[dst], packet['native_line_recipes'][event[2]]['recipe'])
        else:
            need(kind == 'phase', 'known physical event')  # phase events are control markers
    return state, faults


def expected(entry, signal=Q(1)):
    result = list(entry)
    for index, error in ((112, -1), (114, Q(-1, 2)), (137, Q(-1, 2)),
                         (190, Q(-1, 2)), (211, Q(-1, 2))):
        result[index] = N.plus(result[index], N.scaled(N.ONE, signal * error))
    return result


def witness(events, packet, recipes, residuals, bits):
    entry = initial(bits)
    ideal, exact_faults = execute(events, packet, recipes, residuals, entry)
    need(ideal == entry and not exact_faults, 'exact physical endpoint')
    actual, faults = execute(events, packet, recipes, residuals, entry, bits)
    need(actual == expected(entry), 'all physical endpoint amplitudes')
    need([row['event'] for row in faults] == [3887, 4060], 'only two actual rounding sites')
    need(all(row['error'] == {'real': {'-1/2': 512}, 'imag': {'0': 512}} for row in faults),
         'all rounded component errors')
    need(actual[224:704] == entry[224:704] and actual[704:] == [N.ZERO]*8,
         'exact physical helper return and private zero')
    delta = [[i, component_hist(N.plus(a, N.scaled(b, Q(-1))))]
             for i, (a, b) in enumerate(zip(actual, ideal)) if a != b]
    return {'precision': bits, 'dirty_amplitude': str(2**(bits+12)), 'faults': faults,
            'endpoint_errors': delta, 'initial_data_squared_norm': '512',
            'maximum_error_squared_norm': '512', 'relative_error': '1',
            'ideal_endpoint_sha256': digest(ideal), 'rounded_endpoint_sha256': digest(actual),
            'all_480_helpers_exactly_restored': True, 'all_8_private_fields_zero': True}


def audit(root=ROOT):
    packet, word, recipes, residuals = load(root)
    events = expand(packet)
    cases = [witness(events, packet, recipes, residuals, bits) for bits in (8, 24, 53, 113)]
    return {'schema_version': 1, 'status': 'PASS_QQ16_F0_PHYSICAL_ROUNDING',
            'scope': 'finite native F0; component RN at scalar ADDs; exact native operators; unbounded exponents',
            'events': len(events), 'event_sha256': digest(events), 'active_axes': 9,
            'payload_coordinates': N.DIM, 'endpoint_amplitudes_per_case': 712*N.DIM,
            'native_operator_internals_rounded': False, 'cases': cases,
            'selected_frontier_changed': False, 'no_new_kappa': True}


def verify_receipt(path, result):
    need(canonical(read_json(path)) == canonical(result), 'receipt mismatch')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--write', type=Path, help='create an absent receipt')
    args = parser.parse_args()
    result = audit(args.root.resolve())
    if args.write:
        with args.write.open('x') as stream:
            stream.write(json.dumps(result, sort_keys=True, indent=2) + '\n')
    else:
        verify_receipt(HERE / 'RESULT.json', result)
    print(result['status'])
    print('4 finite precisions; 26,099 literal events each; exact helper/private return; no new kappa.')


if __name__ == '__main__':
    main()
