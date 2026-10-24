"""Exact p1/p2 caller and physical-owner probes for the new 120-port lift.

Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
This records a conditional ledger and an unclosed terminal correction.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj
    spec.loader.exec_module(obj)
    return obj


def plus(a, b, c=1):
    out = dict(a)
    for key, value in b.items():
        out[key] = out.get(key, 0)+c*value
        if not out[key]:
            del out[key]
    return out


def prepend(poly, stage):
    return {(stage,)+word: value for word, value in poly.items()}


def sum_polys(terms):
    out = {}
    for poly, coefficient in terms:
        if coefficient:
            out = plus(out, poly, coefficient)
    return out


def controller(C, p, keep):
    """Use the retained role DAG over genuinely noncommuting T_s symbols."""
    coefficients, events, idle = C.controller(p, keep)
    factored = C.factor(coefficients)
    n = 2*p
    matrix = [[{(): Q(1)} if i == j else {} for j in range(n)] for i in range(n)]
    for event in events:
        kind = event[0]
        if kind == 'LOCAL':
            _, stage, pair, backward = event
            x, y = 2*pair, 2*pair+1
            dst, src, sign = (x, y, -1) if backward else (y, x, 1)
            matrix[dst] = [plus(a, b, sign) for a, b in zip(matrix[dst], matrix[src])]
            for role in (x, y):
                matrix[role] = [prepend(poly, stage) for poly in matrix[role]]
        elif kind == 'IDLE':
            _, pair, stages = event
            for stage in stages:
                for role in (2*pair, 2*pair+1):
                    matrix[role] = [prepend(poly, stage) for poly in matrix[role]]
        elif kind == 'ADD':
            _, dst, src, sign = event
            matrix[dst] = [plus(a, b, sign) for a, b in zip(matrix[dst], matrix[src])]
        else:
            assert kind == 'SIGNED_SWAP'
            _, a, b = event
            matrix[a], matrix[b] = matrix[b], [{w: -v for w, v in poly.items()} for poly in matrix[a]]
    left = [[sum_polys((matrix[k][j], factored['left'][i][k]) for k in range(n))
             for j in range(n)] for i in range(n)]
    out = [[sum_polys((left[i][k], factored['right'][k][j]) for k in range(n))
            for j in range(n)] for i in range(n)]
    words = [tuple(s for s in reversed(range(2*p+1)) if term[s+1]) for term in factored['diagonal']]
    assert out == [[{words[i]: Q(1)} if i == j else {} for j in range(n)] for i in range(n)]
    target = Counter()
    for term in factored['diagonal']:
        target[1+8*sum(term[1:])] += 120
    idle_profile = Counter()
    for rec in idle:
        if rec['retained']:
            idle_profile[rec['rank']] += 240
    calls = 2*p+1
    # Ordinary-port conversion creates sixteen H1 calls per local.
    # The remaining helpers are independent; coupled main targets are conditional.
    conditional_surplus = sum(k*v for k, v in target.items())-sum(k*v for k, v in idle_profile.items())-calls*(1920+32)
    assert conditional_surplus == 88*calls-120
    direct_head = 240*p
    return dict(p=p, keep=keep, stage_calls=calls,
                all_noncommuting_coefficient_entries_checked=n*n,
                diagonal_words=[list(w) for w in words],
                target_profile_if_ordinary_main_endpoints_close=dict(sorted(target.items())),
                retained_idle_paid_profile=dict(sorted(idle_profile.items())),
                local_paid_minus_remaining_helpers=1952,
                conditional_first_moment_surplus_before_terminal_normalization=conditional_surplus,
                direct_individual_Q_heads_H1=direct_head,
                conditional_surplus_after_direct_heads=conditional_surplus-direct_head,
                left=C.serialize_matrix(factored['left']), right=C.serialize_matrix(factored['right']),
                scope='Noncommuting algebra only. Stage T_s includes physical gauges and coupled S factors; this is not an independent Gaussian main-job theorem.')


def actual_mapped(n, matrix, routes):
    return [{(j, n.product(routes[i], routes[j])): c for j, c in row.items()}
            for i, row in enumerate(matrix)]


def apply_mapped(n, matrix, vector):
    out = []
    for row in matrix:
        new = {}
        for (j, route), coefficient in row.items():
            for address, value in vector[j].items():
                at = n.act(route, address)
                new[at] = new.get(at, 0)+coefficient*value
                if not new[at]:
                    del new[at]
        out.append(new)
    return out


def word_witness(n, stages, lhs, rhs):
    for field in range(120):
        for address in [0]+list(n.AXES[:25]):
            original = [{} for _ in range(120)]
            original[field] = {address: Q(1)}
            outputs = []
            for word in [lhs, rhs]:
                actual = original
                for stage, inv in word:
                    actual = apply_mapped(n, stages[stage][int(inv)], actual)
                outputs.append(actual)
            if outputs[0] != outputs[1]:
                output = next(i for i in range(120) if outputs[0][i] != outputs[1][i])
                diff = plus(outputs[0][output], outputs[1][output], -1)
                at = min(diff)
                return dict(input_port=field, input_address=address,
                            output_port=output, output_address=at,
                            coefficient=str(diff[at]))
    raise AssertionError('Requested negative-control words have no basis witness')


def terminal_frames(n, F, phases, recipes, owner_ports):
    """Distinguish a Gaussian target from the conjugated correction's hole."""
    records = []
    for interval in [[0, 1, 2], [2, 3, 4], [0, 1, 2, 3, 4]]:
        def target(recipe):
            fresh = [(a, 1) for s in interval if s for a in n.AXES[9+8*(s-1):9+8*s]]
            head = [(a, 1) for a in n.AXES[:9]] if 0 in interval else [(recipe['q'], 1)]
            return n.frame(head+fresh)
        for stage in interval:
            common = n.move_frame(target(recipes[0]), n.source_route(phases, stage, owner_ports[0]))
            good = []
            holes = []
            for port, (recipe, owner) in enumerate(zip(recipes, owner_ports)):
                q = recipe['q']; g = n.source_route(phases, stage, owner)
                positive = target(recipe)
                negative = n.frame(list(positive)+[(q, -2)])
                for sign, frame in [(1, positive), (-1, negative)]:
                    good.append(dict(port=port, sign=sign, view=F.between(n, frame, g, common)))
                # Conjugation Q^-1 M Q acts M on this intermediate frame.
                hole = n.frame(list(positive)+[(q, -1)])
                holes.append(n.move_frame(hole, g))
            ref = n.polynomial(holes[0])
            mismatch = None
            for port, hole in enumerate(holes[1:], 1):
                got = n.polynomial(hole)
                if ref[1] != got[1]:
                    axis = next(i for i, (a, b) in enumerate(zip(ref[1], got[1])) if a != b)
                    bit = ((ref[1][axis]^got[1][axis]) & -(ref[1][axis]^got[1][axis])).bit_length()-1
                    mismatch = dict(reference_port=0, differing_port=port,
                                    quadratic_pair=[axis, bit],
                                    reference_coefficient=(ref[1][axis] >> bit) & 1,
                                    differing_coefficient=(got[1][axis] >> bit) & 1)
                    break
            assert mismatch is not None
            records.append(dict(interval=interval, corrected_stage=stage,
                                target_positive_and_negative_phase_views=good,
                                conjugated_correction_intermediate_frame='positive target minus q',
                                intermediate_hole_has_no_common_phase_frame_under_these_routes=mismatch))
    return dict(positive_and_negative_target_contacts=sum(len(rec['target_positive_and_negative_phase_views']) for rec in records),
                all_target_contacts_pass=True,
                every_intermediate_hole_has_polar_mismatch=True,
                records=records,
                implication='The terminal T_s themselves are free at both signed Gaussian target frames. The negative-bank endpoint instead needs Q^-1 M Q; its inner T_s contacts are at target−q and have a quadratic mismatch. These statements are compatible. No lower bound on another coupled normalizer follows.')


def main():
    L = load(HERE/'lift_native.py', 'lift_caller_native')
    Qc = load(ROOT/'research/query-thinned-controllers/controller.py', 'lift_query_controller')
    _, C = Qc.engines()
    n = load(ROOT/'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/native_common.py', 'lift_owner_native')
    F = load(ROOT/'research/kappa-rebuild/controller/frame_exchange.py', 'lift_frame_contacts')
    packet, phases = n.load_sources()
    N = load(ROOT/'research/kappa-rebuild/complex/rebuild_native.py', 'lift_geometry_native')
    geo = N.geometry(n.HERE/'sources/certificate.json.gz')
    B, cc, S, inverse = L.matrices(geo)
    # Give each new ordinary port the actual normal of one selected main port.
    aux_recipes = [phases['recipes'][p] for p in geo['selected']]
    recipes = phases['recipes']+aux_recipes
    owner_ports = list(range(112))+list(geo['selected'])
    contacts = []
    for stage in range(5):
        for backward in (False, True):
            sign = -1 if backward else 1
            spectator = n.frame((a, 1) for a in n.AXES[9:9+8*stage])
            for port, (recipe, owner) in enumerate(zip(recipes, owner_ports)):
                q = recipe['q']; route = n.source_route(phases, stage, owner)
                input_x = n.frame([(q, 1)]) if stage == 0 else n.completed(stage-1)
                input_y = () if stage == 0 else n.frame(list(input_x)+[(q, -1)])
                local_x = n.frame(list(spectator)+[(q, sign)])
                local_y = spectator
                full = n.frame(list(spectator)+[(a, sign) for a in n.AXES[:9]])
                local_end_y = n.frame(list(full)+[(q, -sign)])
                output_x = n.completed(stage)
                output_y = n.frame(list(output_x)+[(q, -1)])
                views = dict(entry_X=F.between(n, input_x, route, local_x),
                             entry_Y=F.between(n, input_y, route, local_y),
                             exit_X=F.between(n, full, route, output_x),
                             exit_Y=F.between(n, local_end_y, route, output_y))
                if port >= 112:
                    # Physical inverse rank-one Gaussian, conjugated in B,
                    # connects auxiliary start q to native ZERO and native
                    # FULL to the new ordinary target FULL-q.
                    line = n.frame([(q, -sign)])
                    assert n.polynomial(n.frame(list(local_x)+list(line))) == n.polynomial(spectator)
                    assert n.polynomial(n.frame(list(full)+list(line))) == n.polynomial(local_end_y)
                contacts.append(dict(stage=stage, backward=backward, port=port, q=q,
                                     owner_recipe=owner, maps=views))
    # Exact stage-dependent global port operators; inverse is genuine S^-1.
    stages = []
    for stage in range(3):
        routes = [n.source_route(phases, stage, p) for p in owner_ports]
        stages.append((actual_mapped(n, S, routes), actual_mapped(n, inverse, routes)))
    witness = word_witness(n, stages, [(0, False), (1, True), (2, False)], [])
    IL = load(HERE/'involutive_lift.py', 'caller_involutive_lift')
    _, _, T = IL.matrix(geo)
    t_stages = []
    for stage in range(3):
        routes = [n.source_route(phases, stage, p) for p in owner_ports]
        mapped = actual_mapped(n, T, routes)
        t_stages.append((mapped, mapped))
    involutive_witnesses = dict(
        chronological_triple_not_identity=word_witness(n, t_stages, [(0, False), (1, False), (2, False)], []),
        chronological_triple_not_T0=word_witness(n, t_stages, [(0, False), (1, False), (2, False)], [(0, False)]),
        chronological_triple_not_T2=word_witness(n, t_stages, [(0, False), (1, False), (2, False)], [(2, False)]),
        consecutive_stages_do_not_commute=word_witness(n, t_stages, [(0, False), (1, False)], [(1, False), (0, False)]))
    # In the fictitious single chart, S*S^-1*S is S, not I either.
    assert L.mm(S, L.mm(inverse, S)) == S
    assert S != [{i: Q(1)} for i in range(120)]
    data = dict(status='PASS_EXACT_NEW_PRIMITIVE_CALLER_PROBES_NO_KAPPA_CLAIM',
                author='Cao Yifan', new_kappa=False,
                p1=controller(C, 1, 0),
                p2_a0=controller(C, 2, Qc.keep_mask(2, 0)),
                p2_a1=controller(C, 2, Qc.keep_mask(2, 1)),
                converted_auxiliary_normals=[rec['q'] for rec in aux_recipes],
                converted_auxiliary_owner_recipes=list(geo['selected']),
                auxiliary_conversion_paid_H1=16,
                auxiliary_conversion_target_rank_mass_lost=16,
                ordinary_120_port_phase_contacts_checked=len(contacts),
                auxiliary_inverse_line_contacts_checked=5*2*8*2,
                contacts=contacts,
                p1_physical_nonidentity_hole_monodromy='S_2 S_1^{-1} S_0',
                p1_actual_owner_witness=witness,
                same_chart_triple_is_S_not_identity=True,
                involutive_T_actual_owner_witnesses=involutive_witnesses,
                involutive_T_single_chart_parity='T^2=I, so T^3=T only if all stage transports are identified. Actual stages do not have this parity closure.',
                terminal_target_and_inner_hole_frame_probe=terminal_frames(n, F, phases, recipes, owner_ports),
                necessary_reopen_condition='An exact complete terminal/coupled recursive-job normalizer costing less than the available conditional slack. Uniform full-Gaussian commutation alone does not establish matching entry/exit encodings.',
                stage_scope='Local canonical charts and all corresponding exact signed owner/phase maps. The sixteen inverse-line calls are explicit operators whose whole native scheduling and finite precision must be integrated before supplier admission.',
                source_sha256={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in [Path(__file__), HERE/'lift_native.py', HERE/'involutive_lift.py', Path(Qc.__file__), Path(C.__file__), Path(n.__file__), Path(F.__file__)]})
    raw = json.dumps(data, sort_keys=True, separators=(',', ':')).encode()
    (HERE/'CALLER-PROBES.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    summary = {k: data[k] for k in ['status', 'p1_actual_owner_witness', 'ordinary_120_port_phase_contacts_checked', 'auxiliary_inverse_line_contacts_checked']}
    summary['ledgers'] = [{k: data[key][k] for k in ['p', 'keep', 'conditional_first_moment_surplus_before_terminal_normalization', 'conditional_surplus_after_direct_heads']} for key in ['p1', 'p2_a0', 'p2_a1']]
    summary['involutive_T_actual_owner_witnesses'] = involutive_witnesses
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
