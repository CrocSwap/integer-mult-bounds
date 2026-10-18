#!/usr/bin/env python3
"""Show that the best rank-only T740 CP-SAT candidate fails exact operator replay."""
import copy
import gzip
import hashlib
import importlib.util
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT / 'research/source-archives/t740-joint-axis-pr3200'
PHASES = ROOT / 'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json'
BITCERT = ROOT / 'research/r438-native-rehost/CERTIFICATE.json'
OPERATOR_PACKAGE = ROOT / 'research/idle-star-paired-axis-census'


def load(path):
    raw = Path(path).read_bytes()
    if raw[:2] == b'\x1f\x8b':
        raw = gzip.decompress(raw)
    return json.loads(raw)


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    require(spec is not None and spec.loader is not None, 'module spec: ' + name)
    spec.loader.exec_module(module)
    return module


def candidate_profile(verifier, recipes, bins, moves, expected):
    final = verifier.audit(recipes, bins, moves)
    profile = Counter({r: n * 9 * verifier.T for r, n in verifier.LOCAL.items()})
    profile.update(final)
    profile = dict(sorted(profile.items()))
    require({str(k): v for k, v in profile.items()} == expected['profile'],
            'rank-only candidate profile differs from its receipt')
    require(sum(r * n for r, n in profile.items()) == 65088 * verifier.T,
            'rank-only candidate rank mass')
    require(max(profile) <= 51 and 73 * 73 > 2 * max(profile) ** 2,
            'rank-only candidate cap/halving')
    lo, hi = map(F, expected['optimized_complex_root'])
    require(hi - lo == F(1, 10 ** 25), 'rank-only root grid')
    require(verifier.mom(profile, lo)[1] < 1 and verifier.mom(profile, hi)[0] > 1,
            'rank-only candidate exact complex root')
    bit = verifier.BIT
    kappa = min(F(lo.numerator * 10 ** 24 // lo.denominator, 10 ** 24), bit)
    kappa -= F(1, 10 ** 46) + F(1, 10 ** 70)
    require(lo < bit, 'complex endpoint must bind below R438')
    require(kappa == F(expected['optimized_kappa']), 'rank-only hypothetical kappa')
    return profile, kappa, lo


def operator_context(operator):
    operator.authenticate()
    vendor = OPERATOR_PACKAGE / 'vendor'
    base = operator.decode(operator.read_bytes(vendor / 'BASE-FILL.json.gz'))['rows']
    journal = operator.decode(operator.read_bytes(vendor / 'EXCHANGE.json'))
    rows_by_port = operator.project_all_ports(base, operator.journal_edits(base, journal))
    order_base = operator.decode(operator.read_bytes(
        ROOT / 'research/rank7-joint-endframes/allocation/ORDER.json'))
    order = [[stage, replica + 74 * copy] for stage, replica in order_base for copy in range(10)]
    dispatch_rows = operator.decode(operator.read_bytes(
        ROOT / 'research/rank7-joint-endframes/allocation/DISPATCH.json'))
    dispatch = {(stage, replica): tag for stage, replica, tag in dispatch_rows}
    providers = operator.decode(operator.read_bytes(vendor / 'PROVIDERS.json'))
    plan = operator.decode(operator.read_bytes(
        ROOT / 'research/rank7-joint-endframes/allocation/vendor/PLAN.json.gz'))
    template = operator.decode(operator.read_bytes(
        ROOT / 'research/rank7-joint-endframes/allocation/vendor/TEMPLATE.json.gz'))
    recipes = operator.decode(operator.read_bytes(PHASES))['recipes']
    context = operator.prepare_port(0, rows_by_port[0], order, dispatch, providers,
                                    plan, template, recipes)
    blocks = operator.stage_blocks(template)
    return context, blocks, recipes


def main():
    if not __debug__:
        raise SystemExit('assertions required')
    require(hashlib.sha256(PHASES.read_bytes()).hexdigest() ==
            'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
            'DATA-PHASES pin')
    verifier = load_module('pr3200_axis_verifier', ARCHIVE / 'verify.py')
    verifier.PKG = ARCHIVE
    verifier.PHASES = PHASES
    verifier.BITCERT = BITCERT
    verifier.BIT = verifier.check_bit()
    recipes = {r['port']: r for r in json.loads(PHASES.read_bytes())['recipes']}
    bins = load(ARCHIVE / 'BINS.json.gz')
    baseline_moves = load(ARCHIVE / 'MOVES.json.gz')['moves']
    baseline_result = load(ARCHIVE / 'RESULT.json')
    _, baseline_kappa, _ = verifier.run(recipes, bins, baseline_moves, baseline_result)

    payload = load(HERE / 'RANK-ONLY-MOVES.json.gz')
    require(payload['columns'] == ['replica', 'port', 'donor_child', 'receiver_child', 'axis'],
            'rank-only move columns')
    moves = payload['moves']
    expected = load(HERE / 'RANK-ONLY-RESULT.json')
    require(expected['source_head'] == 'f09e5b25381393c604082e58fbe56896b13171b5',
            'PR #3200 source head')
    require(expected['status'] == 'FEASIBLE' and expected['solver_version'] == '9.11.4210',
            'solver must be labelled feasible, not optimal')
    require(expected['admissible_kappa_claim'] is None and
            expected['rank_only_score_is_not_a_supplier_claim'] is True,
            'rank-only result must be labelled inadmissible')
    require(len(moves) == expected['moves'], 'rank-only move count')
    profile, hypothetical_kappa, _ = candidate_profile(verifier, recipes, bins, moves, expected)
    require(hypothetical_kappa > baseline_kappa, 'the rank-only search should show its relaxed gain')
    ceiling = load_module('fixed_word_ceiling', ROOT / 'research/complex-local-word-ceiling/ceiling.py')
    cap_lo, cap_hi = ceiling.ceiling(verifier.LOCAL, 73, 896, 9, 64)
    require((cap_lo, cap_hi) == (F(878223337523, 500000000000000),
                                F(1756446675047, 1000000000000000)),
            'fixed-word packing-ceiling receipt')
    kappa_cap = cap_hi / (1 + cap_hi)
    hypothetical_fraction = hypothetical_kappa / kappa_cap
    require(hypothetical_fraction < 1, 'hypothetical candidate cannot exceed the relaxation ceiling')
    require(F(expected['kappa_gain']) == hypothetical_kappa - baseline_kappa,
            'rank-only hypothetical gain')

    # Authenticate and use the merged source-bound exact eight-stream replay.
    operator = load_module('source_bound_idle_axis_operator', OPERATOR_PACKAGE / 'verify.py')
    context, blocks, port_recipes = operator_context(operator)
    baseline = {c: list(axes) for c, axes in context['residual'].items()}
    baseline_modes = operator.check_baseline(context, baseline, blocks)
    require(baseline_modes == 147, 'exact-operator positive-control modes')
    owner_group = next(g for g in bins['groups'] if g[0] == 0 and g[1] == 0)
    require(owner_group[2] == [[4, 31], [6, 31], [8, 0], [10, 0], [12, 0], [13, 0], [14, 31], [15, 31]],
            'pinned owner-zero port-zero source pattern')
    caps = {c: int(child['rank']) for c, child in enumerate(port_recipes[0]['idle_children'])}
    usage = {c: u for c, u in owner_group[2]}
    require(all(len(baseline[c]) == caps[c] - usage.get(c, caps[c]) for c in range(len(caps))),
            'exact operator context matches PR #3200 BINS')
    group_moves = [m for m in moves if m[0] == 0 and m[1] == 0]
    require(len(group_moves) == 6, 'owner-zero port-zero candidate move count')
    trial = {c: list(axes) for c, axes in baseline.items()}
    for rep, port, source, target, axis in group_moves:
        require(axis in trial[source], 'candidate source axis available in exact context')
        trial[source].remove(axis)
        trial[target].append(axis)
    changed = {c: [len(baseline[c]), len(trial[c])] for c in range(len(caps))
               if len(baseline[c]) != len(trial[c])}
    expected_changed = {'8': [48, 51], '10': [48, 51], '12': [48, 44], '14': [1, 0], '15': [1, 0]}
    require({str(c): value for c, value in changed.items()} == expected_changed,
            'exact operator overlay rank vector')
    for bit in range(53):
        character_before = 1 << bit
        require(operator.replay(context, baseline, character_before, blocks) ==
                operator.replay(context, trial, character_before, blocks),
                f'candidate operator mismatch precedes the frozen witness at bit {bit}')
    character = 1 << 53
    before = operator.replay(context, baseline, character, blocks)
    after = operator.replay(context, trial, character, blocks)
    require(before != after, 'candidate must fail exact physical-operator equality')
    differences = operator.matrix_differences(before, after)
    expected_differences = [[1, 1, [0, 1], [1, 0]],
                             [3, 1, [0, 0], [1, -1]],
                             [6, 6, [0, 1], [-1, 0]]]
    require(differences == expected_differences, 'exact operator mismatch witness')
    witness = load(HERE / 'OPERATOR-WITNESS.json')
    require(witness['first_coordinate_character_mismatch']['character'] == character and
            witness['first_coordinate_character_mismatch']['matrix_differences'] == differences,
            'frozen exact operator witness')

    # The refreshed overlap scan found a newer, numerically higher per-group claim in PR #3251.
    # Its verifier is the PR #3200 rank/profile audit, so bind its frozen output separately and
    # test the same owner-zero port-zero group with the exact eight-stream operator.
    source_rows = {row['path']: row for row in load(HERE / 'SOURCES.json')['files']}
    pr3251_head = 'd7d6254416f0b3ffe659079cca42fd152df63a36'
    pr3251_paths = {
        'BINS.json.gz': 'research/rank7-idle-donors-exact-r438/BINS.json.gz',
        'MOVES.json.gz': 'research/rank7-idle-donors-exact-r438/MOVES.json.gz',
        'RESULT.json': 'research/rank7-idle-donors-exact-r438/RESULT.json',
    }
    pr3251_files = {}
    for name, source_path in pr3251_paths.items():
        row = source_rows.get(source_path)
        require(row is not None and row['usage'] == 'provenance' and
                row['pin'] == f'head:{pr3251_head}:{source_path}',
                'PR #3251 exact source pin: ' + name)
        local_path = HERE / 'vendor' / 'pr3251' / name
        raw = local_path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row['sha256'],
                'vendored PR #3251 artifact differs from its pinned source: ' + name)
        pr3251_files[name] = load(local_path)
    pr3251_bins = pr3251_files['BINS.json.gz']
    pr3251_moves = pr3251_files['MOVES.json.gz']['moves']
    pr3251_result = pr3251_files['RESULT.json']
    require(pr3251_result['status'] == 'PASS_IDLE_DONOR_EXACT_R438_T740' and
            pr3251_result['axis_moves'] == len(pr3251_moves) == 435604,
            'PR #3251 frozen candidate receipt')
    _, pr3251_kappa, _ = verifier.run(recipes, pr3251_bins, pr3251_moves, pr3251_result)
    require(pr3251_kappa > hypothetical_kappa and
            pr3251_kappa == F(pr3251_result['kappa']),
            'PR #3251 rank/profile headline is numerically above the rank-only candidate')
    pr3251_group = next(g for g in pr3251_bins['groups'] if g[0] == 0 and g[1] == 0)
    require(pr3251_group[2] == owner_group[2], 'PR #3251 owner-zero port-zero source pattern')
    pr3251_group_moves = [m for m in pr3251_moves if m[0] == 0 and m[1] == 0]
    require(len(pr3251_group_moves) == 6, 'PR #3251 owner-zero port-zero move count')
    pr3251_trial = {c: list(axes) for c, axes in baseline.items()}
    for rep, port, source, target, axis in pr3251_group_moves:
        require(axis in pr3251_trial[source], 'PR #3251 transfer axis exists in exact source context')
        pr3251_trial[source].remove(axis)
        pr3251_trial[target].append(axis)
    pr3251_changed = {c: [len(baseline[c]), len(pr3251_trial[c])]
                      for c in range(len(caps)) if len(baseline[c]) != len(pr3251_trial[c])}
    require({str(c): value for c, value in pr3251_changed.items()} == expected_changed,
            'PR #3251 exact operator overlay rank vector')
    for bit in range(52):
        character_before = 1 << bit
        require(operator.replay(context, baseline, character_before, blocks) ==
                operator.replay(context, pr3251_trial, character_before, blocks),
                f'PR #3251 operator mismatch precedes frozen witness at bit {bit}')
    pr3251_character = 1 << 52
    pr3251_before = operator.replay(context, baseline, pr3251_character, blocks)
    pr3251_after = operator.replay(context, pr3251_trial, pr3251_character, blocks)
    require(pr3251_before != pr3251_after, 'PR #3251 candidate must fail exact operator equality')
    pr3251_differences = operator.matrix_differences(pr3251_before, pr3251_after)
    require(pr3251_differences == expected_differences,
            'PR #3251 exact operator mismatch witness')
    pr3251_witness = load(HERE / 'PR3251-OPERATOR-WITNESS.json')
    require(pr3251_witness['source_head'] == pr3251_head and
            pr3251_witness['headline_kappa'] == pr3251_result['kappa_decimal'] and
            pr3251_witness['first_coordinate_character_mismatch']['character'] == pr3251_character and
            pr3251_witness['first_coordinate_character_mismatch']['matrix_differences'] == pr3251_differences,
            'frozen PR #3251 exact operator witness')

    # Controls: deleting one rank-only move changes the frozen profile, and a foreign axis
    # is rejected by the predecessor's independent physical-move audit.
    controls = {}
    for name, altered in (('drop_move', moves[1:]),):
        try:
            candidate_profile(verifier, recipes, bins, altered, expected)
        except (ValueError, verifier.Reject) as exc:
            controls[name] = str(exc)
        else:
            raise ValueError('mutation accepted: ' + name)
    foreign = copy.deepcopy(moves)
    foreign[0][4] = 1 << 80
    try:
        candidate_profile(verifier, recipes, bins, foreign, expected)
    except (ValueError, verifier.Reject) as exc:
        controls['foreign_axis'] = str(exc)
    else:
        raise ValueError('mutation accepted: foreign_axis')
    require(len(controls) == 2, 'mutation controls')
    print('PASS_T740_RANK_ONLY_CANDIDATE_REJECTED moves=%d controls=%d hypothetical_kappa=%s cap_fraction=%s checked_before=53 exact_operator_character=2^53 matrix_entries=%d' %
          (len(moves), len(controls), hypothetical_kappa, hypothetical_fraction, len(differences)))
    print('PASS_PR3251_NUMERIC_REPLAY_REJECTED_OPERATOR moves=%d kappa=%s source_head=%s checked_before=52 exact_operator_character=2^52 matrix_entries=%d' %
          (len(pr3251_moves), pr3251_kappa, pr3251_head, len(pr3251_differences)))


if __name__ == '__main__':
    main()
