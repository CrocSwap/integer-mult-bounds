"""Independently authored P104 X90 retiming replay and complete native audit.

A separate OpenAI Codex review agent wrote the dense scalar implementation,
literal rewrite, expected-root reconstruction and native occurrence/column
audit. No candidate search, builder, model or primary verifier is imported.
Dense rows use scaled integers, not the primary checker's sparse Fractions.

Native arithmetic uses the authenticated independent interpreter credited to
Ali Romman/PR1862 and retained by Chafik Boukhalfa's native-channel package.
This is independent AI-agent checking, not independent human/formal review.
"""
import copy
import hashlib
import itertools
import json
import types
from collections import Counter
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
FULL = [256, 128, 64, 32, 16, 8, 4, 2, 1]
MID = [258, 130, 64, 32, 16, 10, 6, 1]
PAIRS = (([400, 80], 7), ([391], 8))

def check(condition, label):
    if not condition:
        raise ValueError(label)


def space(vectors):
    values = {0}
    for vector in vectors:
        check(type(vector) is int and 0 < vector < 512, 'binary vector range')
        values |= {value ^ vector for value in values}
    check(len(values) == 1 << len(vectors), 'independent frame basis')
    return frozenset(values)


def normalized(values, exponent):
    if not any(values):
        return values, 0
    while exponent and all(v % 2 == 0 for v in values):
        values = [v // 2 for v in values]
        exponent -= 1
    return values, exponent


def coefficient(value):
    fields = str(value).split('/')
    check(len(fields) in (1, 2), 'rational scalar syntax')
    num = int(fields[0])
    den = int(fields[1]) if len(fields) == 2 else 1
    check(den > 0 and den & (den - 1) == 0, 'dyadic denominator')
    return num, den.bit_length() - 1


def add_rows(target, source, scalar):
    p, q = coefficient(scalar)
    ta, td = target
    sa, sd = source
    exponent = max(td, sd + q)
    values = [(a << (exponent - td)) + p * (b << (exponent - sd - q))
              for a, b in zip(ta, sa)]
    return normalized(values, exponent)


def replay(word):
    names = sorted(word['initial_frames'])
    check(len(names) == 358, '358 independent initial registers')
    width = len(names)
    values = {name: ([int(i == j) for i in range(width)], 0)
              for j, name in enumerate(names)}
    frames = {name: space(frame) for name, frame in word['initial_frames'].items()}
    counts, ranks = Counter(), Counter()
    erased = []
    max_exponent = 0
    for index, event in enumerate(word['program']):
        op, *args = event
        counts[op] += 1
        try:
            if op == 'transport':
                reg, old, new, rank = args
                old, new = space(old), space(new)
                check(reg in frames and frames[reg] == old, 'transport source frame')
                check(old <= new or new <= old, 'nested transport frames')
                actual = abs(len(old).bit_length() - len(new).bit_length())
                check(type(rank) is int and rank == actual and rank > 0, 'transport rank')
                frames[reg] = new
                ranks[rank] += 1
            elif op == 'add':
                target, source, scalar, frame = args
                check(target != source and target in values and source in values, 'ADD registers')
                frame = space(frame)
                check(frames[target] == frame and frames[source] == frame, 'ADD common frame')
                values[target] = add_rows(values[target], values[source], scalar)
                max_exponent = max(max_exponent, values[target][1])
            elif op == 'sign':
                reg, scalar, frame = args
                check(reg in values and frames[reg] == space(frame), 'sign frame')
                check(str(scalar) == '-1', 'sign is minus one')
                row, exponent = values[reg]
                values[reg] = [-v for v in row], exponent
            elif op == 'zero':
                reg, frame = args
                check(reg not in values and reg not in frames, 'fresh private register')
                values[reg] = [0] * width, 0
                frames[reg] = space(frame)
            elif op == 'erase':
                reg, frame = args
                check(reg in values and reg not in names and frames[reg] == space(frame), 'private erase frame')
                check(not any(values[reg][0]), 'exact private zero erasure')
                del values[reg]
                del frames[reg]
                erased.append(index)
            else:
                raise ValueError('unknown opcode')
        except (KeyError, ValueError) as exc:
            raise ValueError(f'event {index}: {exc}') from exc
    check(set(values) == set(names), 'all and only public outputs')
    check(frames == {name: space(frame) for name, frame in word['final_frames'].items()}, 'final frames')
    return values, {'events': len(word['program']), 'operations': dict(sorted(counts.items())),
                    'profile': dict(sorted(ranks.items())), 'rank_mass': sum(k*v for k, v in ranks.items()),
                    'columns': width, 'zero_erasure_events': erased, 'maximum_row_denominator_exponent': max_exponent}


def make_candidate(word):
    """Literal separate rewrite; no dependence on parent implementation."""
    check(word['program'][3897] == ['transport', 'X90', [400, 80], MID, 6], 'anchor X90 arrival')
    check(word['program'][4643] == ['transport', 'N90', [391], MID, 7], 'anchor N90 arrival')
    check(word['program'][4644] == ['add', 'X90', 'N90', '1/2', MID], 'anchor ADD')
    check(word['program'][4645] == ['transport', 'N90', MID, FULL, 1], 'anchor N90 departure')
    check(word['program'][5048] == ['sign', 'X90', '-1', MID], 'anchor sign')
    check(word['program'][5152] == ['transport', 'X90', MID, FULL, 1], 'anchor X90 departure')
    result = copy.deepcopy(word)
    out = []
    for index, event in enumerate(word['program']):
        if index in (3897, 4643, 4645, 5152):
            continue
        if index == 4644:
            out.extend([['transport', 'X90', [400, 80], FULL[:], 7],
                        ['transport', 'N90', [391], FULL[:], 8]])
            event = ['add', 'X90', 'N90', '1/2', FULL[:]]
        elif index == 5048:
            event = ['sign', 'X90', '-1', FULL[:]]
        out.append(copy.deepcopy(event))
    result['program'] = out
    return result


def expected_rows(word, fixture):
    """Reconstruct ordinary doubled-coordinate E8 Gram; no source executable."""
    root_lines = set()
    for i, j in itertools.combinations(range(8), 2):
        for sign in (-2, 2):
            row = [0] * 8
            row[i], row[j] = 2, sign
            root_lines.add(tuple(row))
    for signs in itertools.product((-1, 1), repeat=7):
        root = (1,) + signs
        if sum(v < 0 for v in root) % 2 == 0:
            root_lines.add(root)
    check(len(root_lines) == 120, '120 canonical E8 root lines')
    removed = {tuple(row) for row in fixture['section4_explicit_P104']['F0'] + fixture['section4_explicit_P104']['C']}
    roots = sorted(root_lines - removed)
    check(len(removed) == 16 and removed <= root_lines and len(roots) == 104, 'P104 punctures')
    names = sorted(word['initial_frames'])
    indices = {name: i for i, name in enumerate(names)}
    expected = {}
    for name in names:
        row = [0] * len(names)
        row[indices[name]] = 8
        if name.startswith('X'):
            s = int(name[1:])
            for t in range(104):
                gram = sum(a*b for a, b in zip(roots[t], roots[s]))
                numerator = 8 * int(t == s) if t < 2 else gram
                row[indices[f'Y{t}']] -= numerator
        expected[name] = normalized(row, 3)
    return expected


def reject(label, mutate, candidate, expected):
    bad = copy.deepcopy(candidate)
    mutate(bad['program'])
    try:
        values, _ = replay(bad)
        check(values == expected, 'complete expected public matrix')
    except ValueError as exc:
        return {'control': label, 'rejection': str(exc)}
    raise ValueError('semantic control incorrectly accepted: ' + label)


def run_dense(old, geom, candidate_word):
    candidate = make_candidate(old)
    check(candidate_word == candidate, 'committed candidate equals independent reconstruction')
    original_map, original_bill = replay(old)
    candidate_map, candidate_bill = replay(candidate)
    expected = expected_rows(old, geom)
    check(original_map == expected, 'predecessor complete advertised matrix')
    check(candidate_map == expected, 'candidate complete advertised matrix')
    check(original_map == candidate_map, 'all 358x358 rational coefficients')
    helpers = [n for n in expected if not n.startswith(('X', 'Y'))]
    check(len(helpers) == 150, '150 independent dirty helper inputs')
    delta = {rank: candidate_bill['profile'].get(rank, 0) - original_bill['profile'].get(rank, 0)
             for rank in sorted(set(original_bill['profile']) | set(candidate_bill['profile']))}
    delta = {rank: count for rank, count in delta.items() if count}
    check(delta == {1: -2, 6: -1, 8: 1}, 'local transport delta')
    check(candidate_bill['rank_mass'] == original_bill['rank_mass'] == 3542, 'unchanged rank mass')
    add = next(i for i, e in enumerate(candidate['program']) if e[:4] == ['add', 'X90', 'N90', '1/2'])
    sign = next(i for i, e in enumerate(candidate['program']) if e == ['sign', 'X90', '-1', FULL])
    private_add = next(i for i,e in enumerate(candidate['program']) if e[0] == 'add' and e[1] == 'C')
    controls = [
        reject('ADD stale middle frame', lambda p: p[add].__setitem__(4, MID[:]), candidate, expected),
        reject('sign stale middle frame', lambda p: p[sign].__setitem__(3, MID[:]), candidate, expected),
        reject('ADD coefficient changed', lambda p: p[add].__setitem__(3, '-1/2'), candidate, expected),
        reject('post-ADD sign omitted', lambda p: p.pop(sign), candidate, expected),
        reject('rank-8 child undercharged', lambda p: p[add-1].__setitem__(4, 7), candidate, expected),
        reject('private cleanup changed', lambda p: p[private_add].__setitem__(3, 0), candidate, expected),
        reject('dirty helper return changed', lambda p: p.append(['sign', 'N90', '-1', FULL[:]]), candidate, expected)
    ]
    equivalent = copy.deepcopy(candidate)
    equivalent['program'][add][4] = list(reversed(FULL))
    equiv_map, _ = replay(equivalent)
    check(equiv_map == expected, 'equivalent noncanonical frame basis accepted')
    return {'status': 'PASS_INDEPENDENT_DENSE_P104_X90_RETIMING', 'baseline': original_bill, 'candidate': candidate_bill,
            'delta': delta, 'public_matrix_entries_checked': len(expected)**2,
            'dirty_helpers_restored': len(helpers), 'semantic_controls': controls,
            'equivalent_frame_basis_accepted': True,
            'scope': 'Exact scalar and frame replay with prescribed canonical chart transports; native recipe lowering is not imported or audited here.'}



def conjugate(circuit):
    result = []
    for gate in circuit:
        tag = gate[0]
        if tag == 'C':
            gate = ('C', gate[1], -gate[2])
        elif tag == 'D':
            gate = ('D', gate[1], tuple((-v) % 4 for v in gate[2]))
        elif tag == 'phase':
            gate = ('phase', -gate[1] % 4)
        else:
            check(tag in ('P', 'X'), 'known real native gate')
        result.append(gate)
    return tuple(result)


def rank(vectors):
    # The pivot step uses the least significant bit, independently of the
    # compiler's/elimination checker's usual highest-bit convention.
    pivots = {}
    for value in vectors:
        while value:
            pivot = value & -value
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    return len(pivots)


def run_native(data, native, word):
    records = data['transports']
    check(len(records) == 2, 'exactly two new native recipes')
    rows = []
    for old, expected_rank in PAIRS:
        matches = [record for record in records if record['old'] == old and record['new'] == FULL]
        check(len(matches) == 1, 'unique direct transport binding')
        record = matches[0]
        recipe = record['recipe']
        check(recipe['rank'] == expected_rank, 'correct native child rank')
        expected_reg = 'X90' if old == [400, 80] else 'N90'
        check(record['role'] == expected_reg, 'native register role')
        literal = ['transport', expected_reg, old, FULL, expected_rank]
        occurrences = [i for i, event in enumerate(word['program']) if event == literal]
        check(len(occurrences) == 1, 'one occurrence per direct recipe')
        add_index = next(i for i, event in enumerate(word['program'])
                         if event == ['add', 'X90', 'N90', '1/2', FULL])
        expected_offset = 2 if expected_reg == 'X90' else 1
        check(occurrences[0] == add_index - expected_offset, 'native immediately before retimed ADD')
        for occurrence in occurrences:
            check(word['program'][occurrence] == ['transport', expected_reg, old, FULL, expected_rank],
                  'exact new occurrence binding')
        delta_old = conjugate(native.frame(tuple(old), 9))
        delta_mid = conjugate(native.frame(tuple(MID), 9))
        delta_full = conjugate(native.frame(tuple(FULL), 9))
        direct = native.adjoint(delta_old) + delta_full
        original_composition = (native.adjoint(delta_old) + delta_mid
                                + native.adjoint(delta_mid) + delta_full)
        lowered = native.recipe(recipe)
        check(rank([x for x, z, phase in native.tableau(direct)[9:]]) == expected_rank,
              'intrinsic symplectic transport rank')
        for column in range(512):
            expected = native.state(direct, column)
            check(native.state(lowered, column) == expected, f'complete lowered native column {column}')
            check(native.state(original_composition, column) == expected, f'complete old-composite column {column}')
        # An otherwise correct Clifford may differ by global phase. Full exact
        # Gaussian columns must reject that, even when signed Paulis agree.
        phase_bad = lowered + (('phase', 1),)
        check(native.tableau(phase_bad) == native.tableau(lowered), 'phase control leaves Pauli action fixed')
        check(native.state(phase_bad, 0) != native.state(direct, 0), 'global phase control rejected')
        conjugation_bad = native.adjoint(native.frame(tuple(old), 9)) + native.frame(tuple(FULL), 9)
        check(native.state(conjugation_bad, 0) != native.state(direct, 0), 'ordinary versus conjugated chart control rejected')
        rows.append({'old_frame': old, 'new_frame': FULL, 'rank': expected_rank,
                     'lowered_recipe_columns': 512, 'literal_old_composition_columns': 512,
                     'wrong_global_phase_rejected': True, 'missing_conjugation_rejected': True})
    return {'status': 'PASS_INDEPENDENT_ALL_NATIVE_COLUMNS', 'total_exact_gaussian_column_equalities': 2048, 'transports': rows,
            'scope': 'Two new 512-address operators, including exact global phase and both literal old transport composites. Other native recipes are inherited.'}



def authenticated_inputs():
    """Read and authenticate exact bytes, with no Git or network dependency."""
    source_manifest = json.loads((P / 'SOURCES.json').read_bytes())
    predecessor_manifest = json.loads((P / 'PREDECESSORS.json').read_bytes())
    sources = source_manifest['files']
    predecessors = predecessor_manifest['files']
    check(len({entry['path'] for entry in sources}) == len(sources), 'unique source pins')
    check(len({entry['local'] for entry in predecessors}) == len(predecessors), 'unique predecessor pins')

    def read_pin(entries, key, name, root):
        matches = [entry for entry in entries if entry[key] == name]
        check(len(matches) == 1, 'exactly one input pin: ' + name)
        record = matches[0]
        path = (root / name).resolve()
        check(path.is_relative_to(root.resolve()), 'input stays below source root')
        data = path.read_bytes()
        check(hashlib.sha256(data).hexdigest() == record['sha256'], 'input SHA256: ' + name)
        blob = b'blob ' + str(len(data)).encode('ascii') + b'\0' + data
        check(hashlib.sha1(blob).hexdigest() == record['git_blob'], 'input Git blob: ' + name)
        return data

    word_bytes = read_pin(predecessors, 'local', 'inputs/PR2662-WORD.json', P)
    fixture_bytes = read_pin(sources, 'path', 'research/p104-native-channel/inputs/P104-FIXTURE.json', ROOT)
    interpreter_bytes = read_pin(sources, 'path', 'research/p104-native-channel/vendor/native_verify.py', ROOT)
    return json.loads(word_bytes), json.loads(fixture_bytes), interpreter_bytes


def main():
    # Every consumed external input has been authenticated before exec, and exec
    # receives those same bytes rather than reopening a path after verification.
    old, geometry, interpreter_bytes = authenticated_inputs()
    candidate = json.loads((P / 'WORD.json').read_bytes())
    recipes = json.loads((P / 'NATIVE.json').read_bytes())
    dense = run_dense(old, geometry, candidate)
    module = types.ModuleType('authenticated_independent_native_interpreter')
    exec(compile(interpreter_bytes, '<authenticated native_verify.py>', 'exec'), module.__dict__)
    native = run_native(recipes, module, candidate)
    print('PASS_INDEPENDENT_P104_ADD_RETIMING'
          + ' matrix_entries=' + str(dense['public_matrix_entries_checked'])
          + ' dirty_helpers=' + str(dense['dirty_helpers_restored'])
          + ' zero_erases=' + str(dense['candidate']['operations']['erase'])
          + ' transports=' + str(dense['candidate']['operations']['transport'])
          + ' rank_mass=' + str(dense['candidate']['rank_mass'])
          + ' gaussian_equalities=' + str(native['total_exact_gaussian_column_equalities'])
          + ' scalar_controls=' + str(len(dense['semantic_controls']))
          + ' native_controls=4 no_new_kappa')


if __name__ == '__main__':
    main()
