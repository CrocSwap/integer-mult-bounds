#!/usr/bin/env python3
"""Delete exact unconsumed centre-assembly/inverse pairs, including dirty state.

Apache-2.0; substantial OpenAI assistance. The native writer and final verifier
are reused with attribution from the frozen causal-continuation package. The
new search checks literal rational perturbations, never numerical similarity.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import importlib.util
import json
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
BASE = RESEARCH / 'kappa-global-routing/integrated-complex'
CHECKER = RESEARCH / 'kappa-causal-continuation/buffer-borrowing/verify_buffers.py'
CHECKER_SHA = '106b4d5e052427230df452f0c901d5390a0583782960b80a8af94d9a984022c7'
CLIFFORD = RESEARCH / 't74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py'
TAGS = ('THREE-base', 'THREE-extra', 'FOUR-base', 'FOUR-extra')


def need(ok, why):
    if not ok: raise ValueError(why)


def digest(path): return sha256(path.read_bytes()).hexdigest()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def save(path, value):
    data = json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
    path.write_bytes(gzip.compress(data, mtime=0))


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj
    spec.loader.exec_module(obj)
    return obj


def apply(v, rows, event, backward=False):
    if event[0] == 'warp':
        r = tuple(event[1]); rows[r] = v.warp(rows[r], event[2], backward)
    elif event[0] == 'scalar':
        g = event[1]; r = tuple(g[1])
        if g[0] == 'add': v.add(rows[r], rows[tuple(g[2])], Q(g[3], g[4]))
        else:
            need(g[0] == 'scale', 'No owned field in the clean-J baseline')
            rows[r] = {k: Q(g[2], g[3])*x for k, x in rows[r].items()}


def index_sections(program):
    phase = None; result = {'A': [], 'full_frame_cleanup': []}
    for i, e in enumerate(program):
        if e[0] == 'phase': phase = e[1]
        if phase in result and e[0] in ('scalar', 'warp'): result[phase].append(i)
    return result


def exact_candidate_screen(v, canonical, program, R):
    """Test the final 48 assembly gates, with their actual scheduled inverses."""
    indices = index_sections(program)
    need(len(indices['A']) == len(canonical['A']), 'Native A gate correspondence')
    need(len(indices['full_frame_cleanup']) == len(canonical['cleanup']), 'Cleanup gate correspondence')
    options = []; unmatched = []
    for j in range(len(canonical['A']) - 48, len(canonical['A'])):
        g = canonical['A'][j]
        need(g[0] == 'add' and len(canonical['frames'][g[-1]]) in (7, 8), 'Final centre-assembly grammar')
        inverse = g[:]; inverse[3] *= -1; inverse[-1] = 1
        hits = [i for i, h in enumerate(canonical['cleanup']) if h == inverse]
        if len(hits) == 1:
            cj = hits[0]
            options.append((j, cj, indices['A'][j], indices['full_frame_cleanup'][cj]))
        else: unmatched.append({'A_index': j, 'gate': g, 'matching_inverse_occurrences': hits})
    sites = {k for option in options for k in option[2:]}
    effects = {}; rows = {('L', i): v.identity(('L', i)) for i in range(632)}
    for i, e in enumerate(program):
        if i in sites:
            g = e[1]
            effects[i] = (tuple(g[1]), {k: -Q(g[3], g[4])*x for k, x in rows[tuple(g[2])].items()})
        apply(v, rows, e)
    need(all(row == v.expected(r, R, False, True) for r, row in rows.items()), 'Pinned baseline endpoint')
    accepted = []; rejected = []
    for aj, cj, ai, ci in options:
        delta = {('L', i): {} for i in range(632)}
        live_data_effect = False
        for i in range(ai, len(program)):
            if i in (ai, ci):
                target, effect = effects[i]; v.add(delta[target], effect, Q(1))
            else: apply(v, delta, program[i])
            if i < indices['full_frame_cleanup'][0]:
                e = program[i]
                if e[0] == 'scalar' and e[1][0] in ('add', 'scale'):
                    r = tuple(e[1][1])
                    if r[0] == 'L' and 112 <= r[1] < 224 and delta[r]: live_data_effect = True
        bad = [(r, row) for r, row in delta.items() if row]
        item = {'A_index': aj, 'cleanup_index': cj, 'A_gate': canonical['A'][aj],
                'cleanup_gate': canonical['cleanup'][cj],
                'native_scalar_sites': [ai, ci], 'Y_difference_before_cleanup': live_data_effect}
        if not bad:
            item['all_632_arbitrary_input_columns_exactly_preserved'] = True
            accepted.append(item)
        else:
            r, row = bad[0]; key, value = next(iter(sorted(row.items())))
            item['first_exact_nonzero_residual'] = {'output': list(r), 'input': list(key[0]),
                                                   'operator_word': list(key[1]), 'coefficient': str(value)}
            item['changed_output_fields'] = len(bad)
            rejected.append(item)
    need(all(not a['Y_difference_before_cleanup'] for a in accepted), 'No changed data consumer before cleanup')
    return accepted, rejected, unmatched


def prefix_growth(v, program, backward):
    rows = {('L', i): v.identity(('L', i)) for i in range(632)}
    maximum_l1 = Q(1); max_coefficient = Q(1); max_numerator = 1; max_denominator = 1
    witness = {'event': -1, 'register': ['L', 0]}
    for i, event in enumerate(program):
        apply(v, rows, event, backward)
        if event[0] not in ('scalar', 'warp'): continue
        role = tuple(event[1] if event[0] == 'warp' else event[1][1])
        values = [abs(x) for x in rows[role].values()]
        norm = sum(values, Q(0))
        if norm > maximum_l1:
            maximum_l1 = norm; witness = {'event': i, 'register': list(role)}
        if values:
            max_coefficient = max(max_coefficient, max(values))
            max_numerator = max(max_numerator, max(x.numerator for x in values))
            max_denominator = max(max_denominator, max(x.denominator for x in values))
    return {'max_formal_row_l1': str(maximum_l1), 'max_abs_coefficient': str(max_coefficient),
            'max_abs_numerator': max_numerator, 'max_denominator': max_denominator,
            'l1_witness': witness, 'independent_input_columns': 632,
            'scope': 'Exact logical scalar/monomial prefixes over arbitrary inputs; no rounded child error bound.'}


def monomial(ce, recipe, n):
    result = ce.diag(n, tuple(recipe['quadratic_rows']), tuple(recipe['linear_Z4']))
    result = result.then(ce.perm(n, tuple(recipe['matrix_rows']))).then(ce.xgate(n, recipe['offset']))
    return result.then(ce.Op(n, ce.identity(n), [('phase', recipe['phase'])]))


def conjugate(ce, op):
    n = op.n; result = ce.ident(n)
    for g in op.circuit:
        if g[0] == 'P': part = ce.perm(n, g[1])
        elif g[0] == 'X': part = ce.xgate(n, g[1])
        elif g[0] == 'C': part = ce.cgate(n, g[1], -g[2])
        elif g[0] == 'D': part = ce.diag(n, g[1], tuple(-x % 4 for x in g[2]))
        else:
            need(g[0] == 'phase', 'Known Clifford primitive')
            part = ce.Op(n, ce.identity(n), [('phase', -g[1] % 4)])
        result = result.then(part)
    return result


def check_new_edges(canonical, old_program, new_program, cache):
    ce = load(CLIFFORD, 'function_composition_clifford')
    old = {(e[3], e[4]) for e in old_program if e[0] == 'climb'}
    new = {(e[3], e[4]) for e in new_program if e[0] == 'climb'}
    reports = []
    for a, b in sorted(new - old):
        A, B = canonical['frames'][a], canonical['frames'][b]
        key = tuple(A), tuple(B)
        if key not in cache:
            source = ce.canonical_frame(9, A).adjoint().then(ce.canonical_frame(9, B))
            records = {}
            for name, op in (('forward', source), ('inverse_transpose', conjugate(ce, source))):
                recipe, _ = ce.lower_child(op)
                need(recipe['rank'] == len(B)-len(A), 'Exact new physical child rank')
                decoded = monomial(ce, recipe['right'], 9).then(ce.fourier(9, range(recipe['rank']))).then(monomial(ce, recipe['left'], 9))
                need(decoded.tab == op.tab and decoded.zero_state() == op.zero_state(), 'Decoded Clifford equality including global phase')
                records[name] = recipe
            cache[key] = records
        reports.append({'old_frame': a, 'new_frame': b, 'old_basis': A, 'new_basis': B,
                        'rank': len(B)-len(A), 'exact_physical_recipes': cache[key]})
    return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=HERE/'pruned-native')
    args = parser.parse_args(); args.out.mkdir(parents=True, exist_ok=True)
    need(digest(CHECKER) == CHECKER_SHA, 'Frozen independent checker')
    v = load(CHECKER, 'function_composition_independent'); v.authenticate()
    base_receipt = read(BASE/'RESULT.json')
    R = [{int(k): Q(x) for k, x in row.items()} for row in v.read(v.PACKET)['R_rows']]
    providers = {}; phase_cache = {}
    for tag in TAGS:
        path = BASE/(tag+'-CANONICAL.json.gz')
        need(digest(path) == base_receipt['providers'][tag]['artifacts'][path.name], 'Pinned baseline canonical')
        old = read(path); old_native = v.emit_original(old)
        yes, no, unmatched = exact_candidate_screen(v, old, old_native['forward'], R)
        candidate = deepcopy(old)
        a_drop = {r['A_index'] for r in yes}; c_drop = {r['cleanup_index'] for r in yes}
        candidate['A'] = [g for i, g in enumerate(old['A']) if i not in a_drop]
        candidate['cleanup'] = [g for i, g in enumerate(old['cleanup']) if i not in c_drop]
        native = v.emit_original(candidate)
        histogram = Counter(e[5] for e in native['forward'] if e[0] == 'climb')
        candidate['local_profile'] = {str(r): n for r, n in sorted(histogram.items())}
        candidate['edges'] = [list(e) for e in sorted({(e[3], e[4]) for e in native['forward'] if e[0] == 'climb'})]
        checks = {}
        for name in ('forward', 'backward'):
            checks[name] = {'independent_literal_replay': v.replay(native[name], candidate, R, name == 'backward', True),
                            'baseline_prefix_growth': prefix_growth(v, old_native[name], name == 'backward'),
                            'new_prefix_growth': prefix_growth(v, native[name], name == 'backward')}
        phases = check_new_edges(candidate, old_native['forward'], native['forward'], phase_cache)
        # Removing the computation while retaining its inverse must be rejected.
        negative = deepcopy(candidate)
        first = yes[0]
        negative['cleanup'].insert(0, first['cleanup_gate'])
        bad_program = v.emit_original(negative)
        rejected_control = False
        try: v.replay(bad_program['forward'], negative, R, False, True)
        except ValueError as error:
            rejected_control = 'operator mismatch' in str(error)
        need(rejected_control, 'Unpaired deletion negative control')
        cp = args.out/(tag+'-CANONICAL.json.gz'); np = args.out/(tag+'-NATIVE-WORD.json.gz')
        save(cp, candidate); save(np, native)
        providers[tag] = {'baseline_canonical_sha256': digest(path), 'candidate_pairs_tested': len(yes)+len(no),
                          'accepted_pairs': yes, 'rejected_pairs': no, 'unmatched_pairs': unmatched,
                          'old_paid_profile': old['local_profile'], 'new_paid_profile': candidate['local_profile'],
                          'old_paid_rank_mass': sum(int(r)*n for r, n in old['local_profile'].items()),
                          'new_paid_rank_mass': sum(int(r)*n for r, n in candidate['local_profile'].items()),
                          'recursive_calls_removed': sum(old['local_profile'].values())-sum(histogram.values()),
                          'scalar_ADDs_removed': 2*len(yes), 'checks': checks,
                          'new_physical_edges': phases, 'unpaired_deletion_negative_control_rejected': True,
                          'artifacts': {cp.name: digest(cp), np.name: digest(np)}}
        print('PASS pruned native', tag, len(yes), 'pairs;', dict(sorted(histogram.items())), flush=True)
    result = {'schema': 'consumer-driven-clean-J-native-pruning/1',
              'status': 'PASS_ALL_FOUR_BOTH_DIRECTIONS_632_ARBITRARY_FIELDS',
              'generator_sha256': digest(Path(__file__)), 'baseline_receipt_sha256': digest(BASE/'RESULT.json'),
              'independent_interpreter_sha256': CHECKER_SHA, 'phase_compiler_path': str(CLIFFORD.relative_to(RESEARCH.parent)),
              'phase_compiler_sha256': digest(CLIFFORD), 'providers': providers,
              'native_word_new_children_phase_lowered': True, 'local_data_and_helper_endpoints_unchanged': True,
              'same_632_field_inventory': True, 'zero_owned_fields': True, 'zero_external_cleanup_fields': True,
              'no_new_kappa_claimed': True, 'query_producer_contract_preserved': False,
              'scope': 'Exact ideal clean-J local endpoints only. Final historical query assemblies are partially removed because this local word has no centre consumers. A caller that reads those historical queries cannot substitute this word without reconstructing and pricing its producer interface. The full caller and rounded induction remain open.'}
    (args.out/'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(result['status'], flush=True)


if __name__ == '__main__': main()
