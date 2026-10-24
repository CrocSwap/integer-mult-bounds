#!/usr/bin/env python3
"""Source-bound forward helper-query interface; not a complete caller.
Dillon / dillona, substantial OpenAI Codex assistance. Apache-2.0.
Native producer and exact Clifford implementation retain their source credit.
Read-only by default; --write emits the mathematical receipt.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_PAYLOAD = 'cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'
N = 9


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def authenticate():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for record in manifest['files']:
        if record['usage'] == 'input':
            data = (ROOT / record['path']).read_bytes()
            need(sha256(data).hexdigest() == record['sha256'], 'Changed live source: ' + record['path'])
    raw = gzip.decompress((ROOT / 'research/native-center-free-code/SOURCE-WORD.json.gz').read_bytes())
    need(sha256(raw).hexdigest() == SOURCE_PAYLOAD, 'Changed scientific source payload')
    source = json.loads(raw)
    coded = json.loads(gzip.decompress((ROOT / 'research/native-center-free-code/CODED-WORDS.json.gz').read_bytes()))
    core = load_module('helper_query_native_core', ROOT / 'research/native-center-free-code/native_core.py')
    ce = load_module('helper_query_clifford', ROOT / 'research/coded-native-caller/clifford_exact.py')
    return source, coded, core, ce


def add(a, b, coefficient):
    for key, value in b.items():
        value = a.get(key, Q(0)) + coefficient * value
        if value:
            a[key] = value
        else:
            a.pop(key, None)


def scalar_row(row, cold):
    need(all(owner in cold and not word for owner, word in row),
         'First departure must be scalar and read only cold helpers')
    return {owner: value for (owner, word), value in row.items()}


def replay(source, coded, core):
    """Regenerate every final row and first departure, without a saved registry."""
    c = coded['canonical']
    need({k:v for k,v in c.items() if k != 'local_profile'} ==
         {k:v for k,v in source['canonical'].items() if k != 'local_profile'}, 'Changed native charts')
    program = coded['programs']['forward']
    offset = len(program) - len(source['programs']['forward'])
    need(offset == 6596, 'Source compensation length')
    need(program[offset:] == core.clear_centers(source['programs']['forward']),
         'Source event mapping after center deletion')
    cold = {i for i in range(224, 632) if c['start'][i] == 0}
    rows = [core.identity(i) for i in range(632)] + [{}]
    charts = c['start'][:] + [None]
    first, paid = {}, Counter()
    for event, e in enumerate(program):
        kind = e[0]
        if kind == 'scalar':
            gate, chart = e[1:]
            dst = gate[1][1] + (632 if gate[1][0] == 'C' else 0)
            if gate[0] == 'clear':
                need(dst == 632, 'Persistent owner erasure')
                rows[dst], charts[dst] = {}, chart
                continue
            need(charts[dst] == chart, 'Scalar destination chart')
            if gate[0] in ('copy', 'add'):
                src = gate[2][1] + (632 if gate[2][0] == 'C' else 0)
                need(charts[src] == chart, 'Scalar source chart')
                if gate[0] == 'copy':
                    need(dst == 632, 'Persistent owner overwrite')
                    rows[dst] = rows[src].copy()
                else:
                    need(dst != src, 'Self ADD')
                    core.add(rows[dst], rows[src], Q(gate[3], gate[4]))
            elif gate[0] == 'scale':
                rows[dst] = {key: Q(gate[2], gate[3]) * value for key, value in rows[dst].items()}
            else:
                raise ValueError('Unknown scalar opcode')
        elif kind == 'warp':
            _, role, op, before, after = e
            role = role[1] + (632 if role[0] == 'C' else 0)
            need(charts[role] == before, 'Warp chart')
            rows[role] = core.warp(rows[role], op, False)
            charts[role] = after
        elif kind == 'climb':
            _, _, role, before, after, rank = e
            need(charts[role] == before, 'Climb chart')
            need(rank == len(c['frames'][after]) - len(c['frames'][before]) and rank > 0,
                 'Climb Gaussian rank')
            if role in cold and role not in first:
                need(before == 0, 'Cold first-departure chart')
                first[role] = dict(role=role, event=event, source_event=event-offset,
                                   chart=after, rank=rank, row=scalar_row(rows[role], cold))
            charts[role] = after
            paid[rank] += 1
        else:
            need(kind in ('phase', 'adapter', 'residual_adapter'), 'Unexpected instruction')
    need(set(first) == cold and len(cold) == 358, 'All cold first departures')
    need(charts[:632] == c['final'] and not rows[632], 'Final charts and owned center')
    A = json.loads((ROOT / 'research/native-center-free-code/CODE.json').read_text())['A']
    for i in range(632):
        expected = core.identity(i)
        if 112 <= i < 224:
            for j in range(112):
                core.add(expected, core.identity(j), Q(A[i-112][j]))
        need(rows[i] == expected, 'Arbitrary-input endpoint row ' + str(i))
    need(dict(paid) == {1:2201, 2:412, 3:510, 4:127, 5:40}, 'Source paid profile')
    return c, first, paid


def inverse(matrix):
    n = len(matrix)
    a, b = [dict(row) for row in matrix], [{i: Q(1)} for i in range(n)]
    ops = []
    for j in range(n):
        pivot = next((i for i in range(j, n) if a[i].get(j)), None)
        need(pivot is not None, 'Singular cold-helper basis')
        if pivot != j:
            a[j], a[pivot] = a[pivot], a[j]
            b[j], b[pivot] = b[pivot], b[j]
            ops.append(['swap', j, pivot])
        value = a[j][j]
        if value != 1:
            a[j] = {k: v / value for k, v in a[j].items()}
            b[j] = {k: v / value for k, v in b[j].items()}
            ops.append(['scale', j, str(1/value)])
        for i in range(n):
            if i != j and a[i].get(j):
                value = -a[i][j]
                add(a[i], a[j], value)
                add(b[i], b[j], value)
                ops.append(['add', i, j, str(value)])
    need(a == [{i: Q(1)} for i in range(n)], 'Elimination identity')
    return b, ops


def compile_scalar(ops):
    result = []
    for op in ops:
        if op[0] == 'swap':
            a, b = op[1:]
            result.extend([['add', a, b, '1'], ['add', b, a, '-1'],
                           ['add', a, b, '1'], ['scale', b, '-1']])
        else:
            result.append(op)
    return result


def reverse_scalar(ops):
    return [[op[0], *op[1:-1], str(-Q(op[-1]) if op[0] == 'add' else 1/Q(op[-1]))]
            for op in reversed(ops)]


def apply_scalar(ops, rows):
    rows = [dict(row) for row in rows]
    for op in ops:
        if op[0] == 'add':
            need(op[1] != op[2], 'Self scalar ADD')
            add(rows[op[1]], rows[op[2]], Q(op[3]))
        else:
            need(op[0] == 'scale' and Q(op[2]) != 0, 'Reversible SCALE')
            rows[op[1]] = {j: Q(op[2])*v for j, v in rows[op[1]].items()}
    return rows


def encode(rows):
    return [[[j, str(v)] for j, v in sorted(row.items())] for row in rows]


def reject(test, label):
    try:
        test()
    except ValueError:
        return label
    raise ValueError('Mutation was not rejected: ' + label)


def verify_hoist(coded, core, owners, inv, entrance, queries):
    """Move the selected children before the scalar entrance program.

    Cold input labels here denote w = D_K xi.  Observation copies are tracked
    before their separately phase-checked monomial readouts; the native word
    never reads those copies, so their readouts can run immediately.
    """
    c = coded['canonical']
    raw_start, observation_start, count = 633, 745, 112
    rows = [core.identity(i) for i in range(observation_start + count)]
    charts = c['start'][:] + [None] * (1 + 2 * count)
    paid, ordinary = Counter(), Counter()
    program, cuts = [], []

    def clear(slot, chart):
        need(slot >= 632, 'Hoist cannot clear a persistent owner')
        rows[slot], charts[slot] = {}, chart
        ordinary['owned_clear'] += 1
        program.append(['owned_clear', slot, chart])

    def copy(dst, src, chart):
        need(dst >= 633 and charts[src] == chart, 'Owned copy chart')
        rows[dst], charts[dst] = rows[src].copy(), chart
        ordinary['owned_copy'] += 1
        program.append(['owned_copy', dst, src, chart])

    def replacement(owner, raw, target_chart, transport_charts=True):
        need(charts[owner] == 0 and charts[raw] == target_chart,
             'Hoist replacement chart')
        need(rows[owner] == rows[raw], 'Hoist replacement input row')
        rows[owner], rows[raw] = rows[raw], rows[owner]
        if transport_charts:
            charts[owner], charts[raw] = charts[raw], charts[owner]
        need(charts[owner] == target_chart and charts[raw] == 0,
             'Whole-field swap must transport physical chart tags')

    for query in queries:
        q, owner, chart = (query[k] for k in ('query_index', 'native_role', 'first_chart'))
        event = coded['programs']['forward'][query['coded_event']]
        need(event[0] == 'climb' and event[2:] == [owner, 0, chart, 1],
             'Hoisted event is the exact funded first H1 child')
        raw, observation = raw_start + q, observation_start + q
        clear(raw, 0)
        copy(raw, owner, 0)
        charts[raw] = chart
        paid[1] += 1
        program.append(['relocated_child', raw, query['coded_event']])
        clear(observation, chart)
        copy(observation, raw, chart)
        # Its O_s readout is checked in the base bank.  Leave this isolated
        # copy in its raw representation for the all-input symbolic replay.
        program.append(['readout_on_observation', observation, q])

    for op in entrance:
        dst = owners[op[1]]
        need(charts[dst] == 0, 'Hoist entrance target chart')
        if op[0] == 'add':
            src = owners[op[2]]
            need(charts[src] == 0, 'Hoist entrance source chart')
            core.add(rows[dst], rows[src], Q(op[3]))
        else:
            need(op[0] == 'scale' and Q(op[2]), 'Hoist entrance SCALE')
            rows[dst] = {key: Q(op[2]) * value for key, value in rows[dst].items()}
    for i, owner in enumerate(owners):
        need(rows[owner] == {(owners[j], ()): a for j, a in inv[i].items()},
             'Hoist entrance on every cold input')

    by_event = {q['coded_event']: q for q in queries}
    need(len(by_event) == count, 'Distinct hoisted child events')
    controls = []
    for event_index, e in enumerate(coded['programs']['forward']):
        if event_index in by_event:
            query = by_event[event_index]
            owner, raw = query['native_role'], raw_start + query['query_index']
            need(rows[owner] == core.identity(owner), 'First departure after T inverse')
            if not controls:
                original_row = rows[raw]
                rows[raw] = core.identity(0)
                controls.append(reject(lambda: replacement(owner, raw, query['first_chart']),
                                       'wrong held query argument'))
                rows[raw] = original_row
                controls.append(reject(lambda: replacement(owner, raw, query['first_chart'], False),
                                       'swap without physical chart transport'))
                # The rejected no-tag swap exchanged equal rows only.
            replacement(owner, raw, query['first_chart'])
            ordinary['physical_field_swap'] += 1
            program.append(['replace_child_by_swap', event_index, owner, raw])
            clear(raw, 0)
            cuts.append([event_index, owner, query['first_chart'], raw])
            continue
        kind = e[0]
        if kind == 'scalar':
            gate, chart = e[1:]
            dst = gate[1][1] + (632 if gate[1][0] == 'C' else 0)
            if gate[0] == 'clear':
                need(dst == 632, 'Native persistent owner erasure')
                rows[dst], charts[dst] = {}, chart
                continue
            need(charts[dst] == chart, 'Native scalar destination chart after hoist')
            if gate[0] in ('copy', 'add'):
                src = gate[2][1] + (632 if gate[2][0] == 'C' else 0)
                need(charts[src] == chart, 'Native scalar source chart after hoist')
                if gate[0] == 'copy':
                    need(dst == 632, 'Native persistent owner overwrite')
                    rows[dst] = rows[src].copy()
                else:
                    core.add(rows[dst], rows[src], Q(gate[3], gate[4]))
            elif gate[0] == 'scale':
                rows[dst] = {key: Q(gate[2], gate[3])*a for key, a in rows[dst].items()}
            else:
                raise ValueError('Unknown native scalar instruction')
        elif kind == 'warp':
            _, ref, op, before, after = e
            owner = ref[1] + (632 if ref[0] == 'C' else 0)
            need(charts[owner] == before, 'Native warp chart after hoist')
            rows[owner], charts[owner] = core.warp(rows[owner], op, False), after
        elif kind == 'climb':
            _, _, owner, before, after, rank = e
            need(charts[owner] == before, 'Native child chart after hoist')
            need(rank == len(c['frames'][after]) - len(c['frames'][before]) and rank > 0,
                 'Native child rank after hoist')
            charts[owner] = after
            paid[rank] += 1
        else:
            need(kind in ('phase', 'adapter', 'residual_adapter'), 'Unknown native marker')

    A = json.loads((ROOT / 'research/native-center-free-code/CODE.json').read_text())['A']
    oi = {owner: i for i, owner in enumerate(owners)}
    for owner in range(632):
        expected = core.identity(owner)
        if owner in oi:
            expected = {(owners[j], ()): a for j, a in inv[oi[owner]].items()}
        elif 112 <= owner < 224:
            for j in range(112):
                core.add(expected, core.identity(j), Q(A[owner-112][j]))
        need(rows[owner] == expected, 'Hoisted arbitrary-input endpoint ' + str(owner))
    need(charts[:632] == c['final'], 'Hoisted final physical charts')
    need(all(not row for row in rows[632:observation_start]), 'Hoisted raw workspace and native center zero')
    for query in queries:
        observation = observation_start + query['query_index']
        need(rows[observation] == core.identity(query['native_role']) and
             charts[observation] == query['first_chart'], 'Early observation retained intact')
        clear(observation, query['first_chart'])
    need(all(not row for row in rows[632:]), 'All arbitrary owned inputs removed and outputs cleared')
    need(paid == Counter({1:2201, 2:412, 3:510, 4:127, 5:40}), 'Hoist paid inventory unchanged')
    need(ordinary == {'owned_clear':448, 'owned_copy':224, 'physical_field_swap':112},
         'Hoist ordinary-work invoice')
    return dict(schema='native-helper-query-hoist/1', status='PASS_EARLY_112_FUNDED_HELPER_QUERIES',
                original_inputs_checked=632, arbitrary_owned_inputs_checked=225,
                raw_observation_rows_checked=112, replacement_cuts_checked=112,
                all_owned_outputs_zero_after_consumer_clear=True,
                source_paid=dict(sorted(paid.items())), added_gaussian_children=0,
                ordinary_work=dict(ordinary), extra_scalar_passes=0,
                owned_fields_additional_to_native=224,
                added_owned_fields_over_chronological_observer=112,
                prologue_after='All diagonal K maps, before the existing T-inverse program.',
                source_readout_boundary='Observation copies are tracked raw; the same 112 exact-phase O_s identities normalize them independently.',
                recipe_semantics='Ordered patch recipe, not a standalone instruction stream.',
                splice=dict(source='research/native-center-free-code/CODED-WORDS.json.gz:programs.forward',
                            prologue_items=6 * count,
                            after_prologue='Execute BANK.json entrance_scalar_program on the cold owners.',
                            source_events='Replay every original source event in order; replace only the listed child events by their tagged SWAP and owned CLEAR.',
                            after_source='Apply unchanged BANK.json cold_completions, exit_scalar_program and inverse K maps.',
                            observation_clears='The final 112 recipe items are consumer obligations after each observation last use.'),
                program=program, replacement_cuts=cuts, rejected_controls=controls)


def run():
    source, coded, core, ce = authenticate()
    c, first, paid = replay(source, coded, core)
    owners = sorted(first)
    oi = {owner: i for i, owner in enumerate(owners)}
    T = [{oi[j]: v for j, v in first[owner]['row'].items()} for owner in owners]
    inv, elimination = inverse(T)
    entrance = compile_scalar(elimination)
    exit_program = reverse_scalar(entrance)
    identity = [{i: Q(1)} for i in range(358)]
    need(apply_scalar(entrance, identity) == inv, 'Literal entrance on all 358 inputs')
    need(apply_scalar(exit_program, identity) == T, 'Literal exit on all 358 inputs')
    need(apply_scalar(exit_program, inv) == identity, 'T times inverse')
    need(apply_scalar(entrance, T) == identity, 'Inverse times T')

    def equal(a, b):
        return a.tab == b.tab and a.zero_state() == b.zero_state()

    def rank(op):
        return ce.rank([x for x, z, phase in op.tab[N:]])

    def literal(word):
        op = ce.ident(N)
        for e in word:
            if e[0] == 'P': term = ce.perm(N, tuple(e[1]))
            elif e[0] == 'D': term = ce.diag(N, tuple(e[1]), tuple(e[2]))
            elif e[0] == 'X': term = ce.xgate(N, e[1])
            elif e[0] == 'phase': term = ce.Op(N, ce.identity(N), [tuple(e)])
            elif e[0] == 'C': term = ce.cgate(N, e[1], e[2])
            else: raise ValueError('Unknown literal Clifford instruction')
            op = op.then(term)
        return op

    def receipt(op):
        vector, denominator = op.zero_state()
        anchor = next(i for i, value in enumerate(vector) if value != (0, 0))
        return dict(word=op.circuit, signed_tableau=op.tab, fourier_rank=rank(op),
                    zero_column_anchor=[anchor, vector[anchor], denominator])

    normal = json.loads((ROOT / 'research/coded-native-caller/NORMALIZERS.json').read_text())
    ks = {record['q']: literal(record['K_word']) for record in normal['ports']}
    R, common_Q = ce.canonical_frame(N, c['frames'][1]), ce.cgate(N, 1)
    eligible = [record for record in first.values()
                if record['rank'] == 1 and len(c['frames'][c['final'][record['role']]]) == 9
                and c['frames'][record['chart']][0].bit_count() % 2
                and c['frames'][record['chart']][0] != 511]
    need(len(eligible) == 198, 'Native H1 query census')
    selected = sorted(eligible, key=lambda record: record['event'])[:112]
    queries = []
    for i, record in enumerate(selected):
        line = c['frames'][record['chart']][0]
        K = ks[line]
        E = ce.canonical_frame(N, c['frames'][record['chart']])
        need(rank(E) == 1, 'Physical rank of the relocated first child')
        response = common_Q.adjoint().then(K).then(E).adjoint()
        need(rank(K) == rank(response) == 0, 'Monomial query wrappers')
        need(equal(K.then(E).then(response), common_Q), 'Exact common-Q response')
        need(equal(K.then(R).then(K.adjoint()), R), 'Exact R centralizer')
        km, _ = ce.monomial(K)
        rm, _ = ce.monomial(response)
        need(equal(km, K) and equal(rm, response), 'Compiled query phase')
        need(all(e[0] in ('P','D','X','phase') for e in km.circuit+rm.circuit), 'No hidden query Gaussian')
        queries.append(dict(query_index=i, mode_coordinate=oi[record['role']], native_role=record['role'],
                            coded_event=record['event'], source_event=record['source_event'],
                            first_chart=record['chart'], line=line,
                            input_K=receipt(km), response=receipt(rm)))

    completions = []
    cold_profile, hot_profile, added = Counter(), Counter(), Counter()
    for role in range(224, 632):
        birth, final = c['start'][role], c['final'][role]
        target = len(c['frames'][final]) - len(c['frames'][birth])
        (cold_profile if role in oi else hot_profile)[target] += 1
        if role not in oi or target == 9:
            continue
        F = ce.canonical_frame(N, c['frames'][final])
        complement = F.adjoint().then(R)
        child_recipe, compiled = ce.lower_child(complement)
        need(rank(complement) == child_recipe['rank'] == 9-target, 'Cold completion Gaussian rank')
        need(equal(compiled, complement) and equal(F.then(compiled), R), 'Exact completed cold return')
        gaussian = [e for e in compiled.circuit if e[0] == 'C']
        need(len(gaussian) == 9-target and all(e[2] == 1 for e in gaussian), 'One literal complement child')
        positions = [i for i,e in enumerate(compiled.circuit) if e[0] == 'C']
        need(positions == list(range(positions[0], positions[0]+9-target)), 'Contiguous Gaussian block')
        need([e[1] for e in gaussian] == [1 << i for i in range(9-target)], 'Complement child axes')
        added[9-target] += 1
        completions.append(dict(native_role=role, original_rank=target, final_chart=final,
                                charged_child_rank=9-target, operator=receipt(compiled)))
    need(dict(cold_profile) == {4:26, 8:6, 9:326}, 'Cold productive census')
    need(dict(hot_profile) == {4:2, 7:7, 8:41}, 'Hot productive census')
    need(dict(added) == {1:6, 5:26}, 'Cold completion bill')
    controls = []
    bad = {(0, ()): Q(1)}
    controls.append(reject(lambda: scalar_row(bad, set(owners)), 'foreign-main first-departure contamination'))
    singular = [dict(row) for row in T]
    singular[0] = dict(singular[1])
    controls.append(reject(lambda: inverse(singular), 'singular helper basis'))
    first_query = queries[0]
    K, response = literal(first_query['input_K']['word']), literal(first_query['response']['word'])
    E = ce.canonical_frame(N, c['frames'][first_query['first_chart']])
    wrong = ce.Op(N, response.tab, response.circuit+[('phase', 1)])
    controls.append(reject(lambda: need(equal(K.then(E).then(wrong), common_Q), 'Absolute query phase'),
                           'absolute phase invisible to tableau'))
    omitted = next(record for record in completions if record['original_rank'] == 8)
    F = ce.canonical_frame(N, c['frames'][omitted['final_chart']])
    controls.append(reject(lambda: need(equal(F, R), 'Missing H1 completion'), 'omitted cold-H8 completion'))
    final_paid = paid + added
    targets = hot_profile + Counter({9:358})
    counts = Counter(op[0] for op in entrance)
    need(counts == {'add':3210, 'scale':204}, 'Expanded scalar invoice')
    result = dict(schema='native-helper-query-bank/1', status='PASS_FORWARD_NATIVE_112_HELPER_QUERY_BANK',
                  scientific_source_payload_sha256=SOURCE_PAYLOAD, direction='forward_only',
                  original_owner_count=632, original_helper_count=408, cold_helper_owners=owners,
                  hot_helper_owners=[i for i in range(224,632) if i not in oi],
                  query_count=112, eligible_existing_H1_queries=198, queries=queries,
                  T_rows=encode(T), inverse_rows=encode(inv),
                  entrance_scalar_program=entrance, exit_scalar_program=exit_program,
                  cold_completions=completions,
                  invoice=dict(source_paid=dict(sorted(paid.items())), query_gaussian_delta={},
                               completion_paid_delta=dict(sorted(added.items())),
                               completed_paid=dict(sorted(final_paid.items())),
                               old_cold_targets=dict(sorted(cold_profile.items())),
                               unchanged_hot_targets=dict(sorted(hot_profile.items())),
                               new_helper_targets=dict(sorted(targets.items())),
                               added_paid_rank_mass=sum(k*v for k,v in added.items())),
                  ordinary_work=dict(entrance_adds=3210, entrance_scales=204, exit_adds=3210, exit_scales=204,
                                     basis_monomial_field_maps=224, response_monomial_field_maps=112,
                                     observation_copies=112, observation_initial_clears=112,
                                     observation_terminal_clears=112, owned_observation_fields=112,
                                     basis_scratch_fields=0, completion_wrapper_field_maps_upper=64),
                  checks=dict(all_arbitrary_endpoint_rows=632, all_scalar_basis_inputs=358,
                              exact_phase_queries=112, exact_phase_completions=32,
                              T_nonzeros=sum(map(len,T)), inverse_nonzeros=sum(map(len,inv)),
                              inverse_elimination_operations=len(elimination), rejected_controls=controls),
                  inherited_obligations=['Physical implementation of authenticated native operations and their cost model.',
                                         'All-width evaluation lemma from CODED-PROOF.md and PHYSICAL.md.',
                                         'No backward observer, complete caller, global rounding budget, TM tariff or new kappa.'])
    hoist = verify_hoist(coded, core, owners, inv, entrance, queries)
    return json.loads(json.dumps(result)), json.loads(json.dumps(hoist))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result, hoist = run()
    for filename, receipt in [('BANK.json', result), ('HOIST.json', hoist)]:
        path = HERE / filename
        if args.write:
            path.write_text(json.dumps(receipt, sort_keys=True, separators=(',', ':')) + '\n')
        else:
            need(json.loads(path.read_text()) == receipt, 'Changed mathematical ' + filename + ' receipt')
    print(result['status'], json.dumps(result['checks'], sort_keys=True))
    print(hoist['status'], json.dumps({key: hoist[key] for key in
          ('original_inputs_checked', 'arbitrary_owned_inputs_checked',
           'replacement_cuts_checked', 'ordinary_work', 'rejected_controls')}, sort_keys=True))


if __name__ == '__main__':
    main()
