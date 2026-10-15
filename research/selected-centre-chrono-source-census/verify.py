#!/usr/bin/env python3
"""Calls-only common-frame scalar projection: centre-source rank census over all
144 selected local_cover_sweep calls (80 forward, 64 backward).

Scope: PR1918's declared projection (scalar ops exact over Q; climb, adapter and
residual_adapter events are the identity) extended to every selected call in
execution_schedule order.  Bridge, idle_cover_sweep, terminal, bank padding and
translate events are NOT executed; they are counted per dependent pair.  This is
a finite certificate in a declared projection, not a native obstruction.

The replay logic reimplements PR1918 (Adam Gall,
research/selected-centre-composed-source-rank) with credit.  Prepared by
thakrarsagar with substantial AI assistance from Claude (Anthropic, Claude
Opus 5.5).  Apache-2.0.
"""
import argparse
import gzip
import hashlib
import json
import tarfile
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
STATUS = 'PASS_SELECTED_CENTRE_CHRONO_SOURCE_CENSUS'
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
PR1918_RESULT = 'research/selected-centre-composed-source-rank/RESULT.json'
PINS = {
    ARCHIVE: 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6',
    'certificates/selected-result.json': '10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32',
    PR1918_RESULT: '31555505a5eea8e54b3b04c67e4aefa495101f3b43d7fe9fa8dca90776dea668',
}
MEMBERS = {
    'global': ('candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz', '2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760'),
    'program': ('candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz', '241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a'),
    'word': ('candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz', '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219'),
}
PRIME = (1 << 61) - 1
ROLES = 704
PROJECTED_IDENTITY = ('climb', 'adapter', 'residual_adapter')
UNMODELLED = ('bridge', 'idle_cover_sweep')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def add(row, source, q):
    for key, value in list(source.items()):
        new = row.get(key, Q(0)) + q * value
        if new:
            row[key] = new
        else:
            row.pop(key, None)


def rank_q(rows):
    """Exact rank over Q by sparse elimination; returns (rank, pivot columns)."""
    pivots = {}
    for original in rows:
        row = dict(original)
        while row:
            col = min(row)
            if col not in pivots:
                q = row[col]
                pivots[col] = {k: v / q for k, v in row.items()}
                break
            add(row, pivots[col], -row[col])
    return len(pivots), sorted(pivots)


def kernel_q(rows):
    """Exact left-kernel vectors of the row list (one per dependent row)."""
    pivots = {}
    out = []
    for index, original in enumerate(rows):
        row = dict(original)
        combo = {index: Q(1)}
        while row:
            col = min(row)
            if col not in pivots:
                q = row[col]
                prow, pcombo = pivots[col] = ({k: v / q for k, v in row.items()},
                                              {k: v / q for k, v in combo.items()})
                break
            prow, pcombo = pivots[col]
            q = row[col]
            add(row, prow, -q)
            add(combo, pcombo, -q)
        else:
            out.append(combo)
    return out


def rank_mod(rows, p=PRIME):
    """Rank modulo p.  Every denominator here is a power of two, so rank mod p
    is a lower bound for rank over Q; full rank mod p certifies full rank over Q."""
    pivots = {}
    for original in rows:
        row = {}
        for k, v in original.items():
            require(v.denominator % p, 'denominator divisible by p')
            x = v.numerator * pow(v.denominator, -1, p) % p
            if x:
                row[k] = x
        while row:
            col = min(row)
            if col not in pivots:
                inv = pow(row[col], -1, p)
                pivots[col] = {k: v * inv % p for k, v in row.items()}
                break
            q = row[col]
            for k, v in pivots[col].items():
                x = (row.get(k, 0) - q * v) % p
                if x:
                    row[k] = x
                else:
                    row.pop(k, None)
    return len(pivots)


def local_replay(program, word_centres=None):
    """One symbolic replay over the 704 local roles.  Returns the 8 centre-input
    functionals (value of private register C_k at its rank-8 `center` event),
    the endpoint map (only non-identity roles) and the centre-phase bill."""
    state = {('L', i): {i: Q(1)} for i in range(ROLES)}
    centre_inputs = {}
    phase_start = None
    bill = Counter()
    phase = None
    for event in program:
        tag = event[0]
        if tag == 'phase':
            phase = event[1]
            if phase == 'centers' and word_centres is not None:
                phase_start = [dict(state['L', r]) for r in word_centres]
            continue
        if tag == 'scalar':
            op = event[1]
            name, dest = op[0], tuple(op[1])
            if phase == 'centers':
                bill[name] += 1
            if name == 'clear':
                state[dest] = {}
            elif name == 'copy':
                state[dest] = dict(state[tuple(op[2])])
            elif name == 'scale':
                q = Q(op[2], op[3])
                require(q != 0 and dest in state, 'singular or unwritten scale')
                state[dest] = {k: q * v for k, v in state[dest].items()}
            elif name == 'add':
                require(dest in state and tuple(op[2]) in state, 'unwritten add operand')
                require(dest != tuple(op[2]), 'self add')
                add(state[dest], state[tuple(op[2])], Q(op[3], op[4]))
            else:
                raise ValueError('unknown scalar operation')
        elif tag == 'center':
            require(phase == 'centers' and event[4] == 8, 'unexpected centre')
            k = event[1]
            require(k not in centre_inputs and ('C', k) in state, 'duplicate or unwritten centre')
            centre_inputs[k] = dict(state['C', k])
            bill['rank8'] += 1
        else:
            require(tag in PROJECTED_IDENTITY, 'unknown event')
    require(sorted(centre_inputs) == list(range(8)), 'centre index set')
    require(all(not row for key, row in state.items() if key[0] != 'L'), 'dirty private exit')
    require(set(state) - {('L', i) for i in range(ROLES)} <= {('C', k) for k in range(8)},
            'unexpected private register')
    endpoint = {}
    for i in range(ROLES):
        if state['L', i] != {i: Q(1)}:
            endpoint[i] = state['L', i]
    return [centre_inputs[k] for k in range(8)], endpoint, bill, phase_start


def transvection_endpoint(orientation):
    """Declared endpoint: forward L_i += L_{i-112} (112<=i<224); backward
    L_i -= L_{i+112} (0<=i<112).  Checked exactly against each replay."""
    if orientation == 'forward':
        return {i: {i: Q(1), i - 112: Q(1)} for i in range(112, 224)}
    return {i: {i: Q(1), i + 112: Q(-1)} for i in range(112)}


def evaluate_local(form, owners, physical):
    row = {}
    for role, q in form.items():
        add(row, physical[owners[role]], q)
    return row


def schedule_calls(data):
    calls = data['global']['calls']
    key = lambda c: (c['time'], c['replica'], c['stage'], c['provider_id'])
    by_key = {key(c): c for c in calls}
    require(len(by_key) == len(calls) == 144, 'call key collision or count')
    sched = data['global']['execution_schedule']
    positions, ordered = [], []
    for index, event in enumerate(sched):
        if event.get('kind') == 'local_cover_sweep':
            positions.append(index)
            ordered.append(by_key[key(event)])
    require(len(ordered) == 144 and len({id(c) for c in ordered}) == 144, 'schedule/call bijection')
    return ordered, positions


def run(data, pr1918):
    programs = data['program']
    word = data['word']
    source_roles = word['centers']
    require(source_roles == [92, 57, 81, 224, 11, 240, 9, 256], 'source role drift')
    digests = {o: sha(json.dumps(programs[o], sort_keys=True, separators=(',', ':')).encode())
               for o in ('forward', 'backward')}
    local = {}
    for o in ('forward', 'backward'):
        maps, endpoint, bill, start = local_replay(programs[o], source_roles)
        require(endpoint == transvection_endpoint(o), f'{o} endpoint is not the declared role transvection')
        local[o] = (maps, bill, endpoint)
    fwd = programs['forward']
    seg = fwd[fwd.index(['phase', 'centers']) + 1:fwd.index(['phase', 'B'])]
    copies = [e[1] for e in seg if e[0] == 'scalar' and e[1][0] == 'copy']
    require([(tuple(op[1]), tuple(op[2])) for op in copies] == [(('C', k), ('L', r)) for k, r in enumerate(source_roles)],
            'forward centre copies are not C_k <- L[word centers[k]]')
    fwd_start = local_replay(fwd, source_roles)[3]
    require(local['forward'][0] == fwd_start, 'forward centre inputs != PR1918 phase-start cut at word centers')
    ordered, positions = schedule_calls(data)
    for c in ordered:
        require(c['local_program_sha256'] == digests[c['orientation']], 'program binding')
    owners = [[entry[0] for entry in c['owners']] for c in ordered]
    for ow in owners:
        require(len(ow) == len(set(ow)) == ROLES, 'noninjective local owner map')
    universe = set().union(*map(set, owners))
    physical = {owner: {owner: Q(1)} for owner in universe}
    rows_by_call = []
    for c, ow in zip(ordered, owners):
        maps, _, endpoint = local[c['orientation']]
        rows_by_call.append([evaluate_local(form, ow, physical) for form in maps])
        new = {i: evaluate_local(form, ow, physical) for i, form in endpoint.items()}
        for i, value in new.items():
            physical[ow[i]] = value
    # Positive control: PR1918 time0/time1 pair.
    require([(c['time'], c['stage'], c['replica'], c['orientation']) for c in ordered[:2]]
            == [(0, 0, 0, 'forward'), (1, 0, 8, 'forward')], 'PR1918 pair drift')
    first = rows_by_call[0] + rows_by_call[1]
    require([{str(k): str(v) for k, v in sorted(r.items())} for r in first] == pr1918['source_maps'],
            'PR1918 source maps not reproduced')
    require(rank_q(first)[0] == pr1918['source_rank'] == 16, 'PR1918 rank 16 not reproduced')
    require(rank_q(rows_by_call[0] + rows_by_call[0])[0] == 8, 'duplicated-row control')
    require(rank_q(rows_by_call[0] + list(reversed(rows_by_call[0])))[0] == 8, 'reversed-order control')
    restrict = lambda rows, cols: [{k: v for k, v in row.items() if k in cols} for row in rows]
    pr_clean = restrict(first, {o for ow in owners[:2] for o in ow[:112]})
    require(rank_q(pr_clean)[0] == pr1918['rank_restricted_to_224_source_data_owners'] == 16,
            'PR1918 source-data-only rank not reproduced')
    # Diagnostic specializations (NOT the template semantics, where every one of the
    # 14,336 owners is a live data family): zero the initial value of every owner
    # whose first touch in schedule order is a helper role (>=224), or any role >=112.
    first_role = {}
    for ow in owners:
        for role, owner in enumerate(ow):
            first_role.setdefault(owner, role)
    diag_cols = {'zero_helper_first_touch': {o for o, r in first_role.items() if r < 224},
                 'zero_nondata_first_touch': {o for o, r in first_role.items() if r < 112}}
    diag_rows = {name: [restrict(rows, cols) for rows in rows_by_call] for name, cols in diag_cols.items()}
    # Dependency classes.
    data_set = [set(ow[:112]) for ow in owners]
    write_set = [{ow[i] for i in local[c['orientation']][2]} for c, ow in zip(ordered, owners)]
    read_set = [set(ow[:224]) for ow in owners]
    supp = [set().union(*map(set, rows)) for rows in rows_by_call]
    classes = {}
    for i, j in combinations(range(144), 2):
        tags = []
        if data_set[i] & data_set[j]:
            tags.append('shared_data_owner')
        if write_set[i] & read_set[j]:
            tags.append('write_to_later_read')
        if supp[i] & supp[j]:
            tags.append('shared_formal_support')
        if tags:
            classes[i, j] = tags
    sched = data['global']['execution_schedule']
    code = {'shared_data_owner': 'D', 'write_to_later_read': 'W', 'shared_formal_support': 'S'}
    variant_names = ('formal', 'pair_roles_0_223_owners', 'pair_roles_0_111_owners',
                     'zero_helper_first_touch', 'zero_nondata_first_touch')
    pairs = []
    hist = {name: Counter() for name in variant_names}
    deficient = []
    witnesses = []
    for (i, j), tags in sorted(classes.items()):
        rows = rows_by_call[i] + rows_by_call[j]
        variants = {'formal': rows,
                    'pair_roles_0_223_owners': restrict(rows, read_set[i] | read_set[j]),
                    'pair_roles_0_111_owners': restrict(rows, data_set[i] | data_set[j]),
                    'zero_helper_first_touch': diag_rows['zero_helper_first_touch'][i] + diag_rows['zero_helper_first_touch'][j],
                    'zero_nondata_first_touch': diag_rows['zero_nondata_first_touch'][i] + diag_rows['zero_nondata_first_touch'][j]}
        ranks = {name: rank_q(v)[0] for name, v in variants.items()}
        for name, r in ranks.items():
            hist[name][r] += 1
        for name in ('formal', 'pair_roles_0_223_owners'):
            if ranks[name] < 16:
                deficient.append({'calls': [i, j], 'variant': name, 'rank': ranks[name],
                                  'left_kernel': [{str(k): str(v) for k, v in sorted(w.items())}
                                                  for w in kernel_q(variants[name])]})
        reps = {ordered[i]['replica'], ordered[j]['replica']}
        between = Counter(e['kind'] for e in sched[positions[i] + 1:positions[j]]
                          if e.get('kind') in UNMODELLED and reps & set(e['replicas']))
        same_block = (ordered[i]['orientation'], ordered[i]['stage'], ordered[j]['orientation'], ordered[j]['stage']) \
            == ('forward', 0, 'backward', 1) and owners[i][:224] == owners[j][:224]
        if same_block:
            # Exact left-kernel witnesses for the cleanest dependent class (same 224 owners,
            # no intervening schedule event on the replica) under PR1918's column restriction:
            # rows restricted to roles 0..111 variables (b1 writes, not reads, this block).
            vrows = variants['pair_roles_0_111_owners']
            kern = kernel_q(vrows)
            require(len(kern) == 16 - ranks['pair_roles_0_111_owners'], 'kernel dimension')
            for w in kern:
                total = {}
                for index, q in w.items():
                    add(total, vrows[index], q)
                require(not total, 'kernel witness does not annihilate rows')
            require(rank_q(variants['formal'])[0] == 16, 'formal same-block rank')
            # Exact structural identity: on the shared data block D, backward centre k is
            # 1/4 of forward centre k; outside D the rows differ (b1 reads T, f0 reads helper roles).
            d_cols, t_cols = set(owners[i][:112]), set(owners[i][112:224])
            for k in range(8):
                f_d = restrict([rows_by_call[i][k]], d_cols)[0]
                b_d = restrict([rows_by_call[j][k]], d_cols)[0]
                require(f_d and b_d == {c: q / 4 for c, q in f_d.items()},
                        'backward1 centre D-part is not 1/4 of forward0 centre D-part')
            require(not any(restrict(rows_by_call[i], t_cols)), 'forward0 centre reads target block')
            require(rank_q(restrict(rows_by_call[j], t_cols))[0] == 8, 'backward1 target-block rank')
            # Specialization check: zero only the target-block variables (helpers and every
            # other owner stay formal). The forward0 centre also reads helper-role owners, so
            # this is recorded separately from the roles 0..111 restriction.
            t_zero = [{c: q for c, q in row.items() if c not in t_cols} for row in rows]
            rank_t_zero = rank_q(t_zero)[0]
            witnesses.append({'calls': [i, j], 'replica': ordered[i]['replica'],
                              'unmodelled_between': between['bridge'] + between['idle_cover_sweep'],
                              'rank_pair_roles_0_111_owners': ranks['pair_roles_0_111_owners'],
                              'rank_pair_roles_0_223_owners': ranks['pair_roles_0_223_owners'],
                              'rank_target_block_zeroed_others_formal': rank_t_zero,
                              'left_kernel_over_16_rows': [{str(k): str(v) for k, v in sorted(w.items())} for w in kern]})
        pairs.append([i, j, ''.join(code[t] for t in tags), len(data_set[i] & data_set[j]),
                      len(write_set[i] & read_set[j]), len(supp[i] & supp[j])]
                     + [ranks[name] for name in variant_names] + [between['bridge'], between['idle_cover_sweep']])
    require(len(witnesses) == 16, 'expected 16 same-replica forward0->backward1 pairs')
    all_rows = [r for rows in rows_by_call for r in rows]
    by_orient = {o: [r for c, rows in zip(ordered, rows_by_call) if c['orientation'] == o for r in rows]
                 for o in ('forward', 'backward')}
    global_mod = rank_mod(all_rows)
    orient_mod = {o: rank_mod(rows) for o, rows in by_orient.items()}
    global_q = rank_q(all_rows)[0]
    require(global_q >= global_mod, 'rank mod p exceeded rank over Q')
    diagnostics = {}
    for name, per_call in diag_rows.items():
        own = [rank_q(rows)[0] for rows in per_call]
        diagnostics[name] = {
            'formal_owner_columns': len(diag_cols[name]),
            'global_rank_q': rank_q([r for rows in per_call for r in rows])[0],
            'per_call_rank_histogram': {str(k): v for k, v in sorted(Counter(own).items())},
            'per_call_rank_by_orientation_stage': sorted([list(k) + [v] for k, v in Counter(
                (c['orientation'], c['stage'], own[k]) for k, c in enumerate(ordered)).items()]),
        }
    class_counts = Counter()
    for tags in classes.values():
        for t in tags:
            class_counts[t] += 1
    orient_mix = Counter('-'.join(ordered[k]['orientation'] for k in pair) for pair in classes)
    data_pairs = [rec for rec in pairs if 'D' in rec[2]]
    data_pair_kinds = Counter(f"{ordered[rec[0]]['orientation']}{ordered[rec[0]]['stage']}->"
                              f"{ordered[rec[1]]['orientation']}{ordered[rec[1]]['stage']}"
                              f"/same_replica={ordered[rec[0]]['replica'] == ordered[rec[1]]['replica']}"
                              f"/unmodelled_between={rec[-2] + rec[-1]}" for rec in data_pairs)
    supp_sizes = Counter(len(r) for r in all_rows)
    block_0_111_by_class = Counter(f"{rec[2]}/rank_roles_0_111={rec[8]}" for rec in pairs)
    return {
        'status': STATUS,
        'scope': ('Calls-only common-frame scalar projection (PR1918 extended to all 144 selected calls): '
                  'scalar ops exact over Q; climb/adapter/residual_adapter = identity; bridge, idle_cover_sweep, '
                  'terminal, bank padding and translate events NOT executed. Finite certificate, not a native '
                  'obstruction, formal proof or kappa change.'),
        'centre_row_definition': 'value of private register C_k at its rank-8 `center` event (forward: copy of word centers roles)',
        'calls': len(ordered),
        'calls_by_orientation': dict(Counter(c['orientation'] for c in ordered)),
        'call_fields': ['schedule_index', 'time', 'stage', 'replica', 'orientation', 'pair'],
        'call_table': [[positions[k], c['time'], c['stage'], c['replica'], c['orientation'], c['pair']]
                       for k, c in enumerate(ordered)],
        'local_program_sha256': digests,
        'local_centre_input_support_sizes': {o: [len(f) for f in local[o][0]] for o in local},
        'local_centre_phase_bill': {o: dict(sorted(local[o][1].items())) for o in local},
        'local_endpoint': {'forward': 'L_i += L_{i-112} for 112<=i<224', 'backward': 'L_i -= L_{i+112} for 0<=i<112',
                           'private_registers': 'clean at exit'},
        'physical_owner_universe': len(universe),
        'centre_rows': len(all_rows),
        'centre_row_support_size_histogram': {str(k): v for k, v in sorted(supp_sizes.items())},
        'global_rank_q': global_q,
        'global_rank_mod_p': global_mod,
        'prime': PRIME,
        'rank_mod_p_by_orientation': orient_mod,
        'dependent_pairs': len(classes),
        'dependent_pair_class_counts': dict(sorted(class_counts.items())),
        'dependent_pair_orientation_mix': dict(sorted(orient_mix.items())),
        'shared_data_owner_pair_kinds': dict(sorted(data_pair_kinds.items())),
        'dependent_pair_rank_histograms': {name: {str(k): v for k, v in sorted(h.items())} for name, h in hist.items()},
        'deficient_pairs_formal_or_pair_local': deficient,
        'diagnostic_specializations_not_template_semantics': diagnostics,
        'forward0_backward1_same_block_pairs_data_only_kernels': witnesses,
        'roles_0_111_block_rank_by_dependency_class': dict(sorted(block_0_111_by_class.items())),
        'pair_fields': ['call_i', 'call_j', 'classes(D=shared roles0-111 owner, W=write->later read, S=shared formal support)',
                        'shared_data_owners', 'write_to_later_read_owners', 'shared_formal_support_vars',
                        'rank_formal', 'rank_pair_roles_0_223_owners', 'rank_pair_roles_0_111_owners',
                        'rank_zero_helper_first_touch',
                        'rank_zero_nondata_first_touch',
                        'bridges_between_on_pair_replicas', 'idle_cover_sweeps_between_on_pair_replicas'],
        'pairs': pairs,
        'pr1918_control': {'calls': [0, 1], 'source_rank': 16, 'source_data_only_rank': 16, 'source_maps_reproduced': True},
        'controls': ['pr1918_rank16_and_source_maps', 'duplicated_rows_rank8', 'reversed_order_rows_rank8',
                     'forward_centre_inputs_equal_word_centers', 'perturbed_coefficient_changes_or_rejects',
                     'omitted_backward_gather_changes_receipt', 'omitted_final_clear_rejected',
                     'pin_hash_sensitivity_to_bitflip'],
    }


def load(root):
    for path, digest in PINS.items():
        require(sha((root / path).read_bytes()) == digest, f'pin mismatch: {path}')
    data = {}
    raws = {}
    with tarfile.open(root / ARCHIVE, 'r:gz') as archive:
        for key, (path, digest) in MEMBERS.items():
            raw = archive.extractfile(path).read()
            require(sha(raw) == digest, f'member pin mismatch: {path}')
            raws[key] = raw
            data[key] = json.loads(gzip.decompress(raw))
    pr1918 = json.loads((root / PR1918_RESULT).read_text(encoding='utf-8'))
    return data, pr1918, raws


def negative_controls(root, data, raws, local_maps):
    """Each mutation below must be rejected or must change the receipt."""
    done = []
    # (1) pin hash sensitivity: a one-bit flip of the archive or a member changes its
    # SHA256, so load() would reject it. Rejection by load() itself is exercised by the
    # external scratch-copy controls recorded in the README.
    blob = bytearray((root / ARCHIVE).read_bytes())
    blob[len(blob) // 2] ^= 1
    require(sha(bytes(blob)) != PINS[ARCHIVE], 'corrupted archive accepted')
    raw = bytearray(raws['program'])
    raw[-5] ^= 1
    require(sha(bytes(raw)) != MEMBERS['program'][1], 'corrupted member accepted')
    done.append('pin_hash_sensitivity_to_bitflip')
    # (2) perturbed scalar coefficient before the centre cut in the backward program.
    program = [list(e) for e in data['program']['backward']]
    start = program.index(['phase', 'A'])
    cut = program.index(['phase', 'centers'])
    k = next(i for i in range(start, cut) if program[i][0] == 'scalar' and program[i][1][0] == 'add')
    op = list(program[k][1])
    op[3] = op[3] + op[4]  # coefficient a/b -> (a+b)/b
    program[k] = ['scalar', op] + program[k][2:]
    digest = sha(json.dumps(program, sort_keys=True, separators=(',', ':')).encode())
    require(digest != sha(json.dumps(data['program']['backward'], sort_keys=True, separators=(',', ':')).encode()),
            'perturbation did not change program binding')
    try:
        maps, endpoint, _, _ = local_replay(program)
    except ValueError:
        pass
    else:
        require(maps != local_maps['backward'] or endpoint != transvection_endpoint('backward'),
                'perturbed coefficient left local map and endpoint unchanged')
    done.append('perturbed_coefficient_changes_or_rejects')
    # (3) omit one backward centre gather add: centre input must change.
    program = data['program']['backward']
    s, e = program.index(['phase', 'centers']), program.index(['phase', 'B'])
    g = next(i for i in range(s, e) if program[i][0] == 'scalar' and program[i][1][0] == 'add'
             and program[i][1][1][0] == 'C')
    maps, _, _, _ = local_replay(program[:g] + program[g + 1:])
    require(maps != local_maps['backward'], 'omitted gather left centre input unchanged')
    done.append('omitted_backward_gather_changes_receipt')
    # (4) omit the final private clear: dirty exit must be rejected.
    final_clear = e - 1
    require(program[final_clear][0] == 'scalar' and program[final_clear][1][0] == 'clear', 'final clear position')
    try:
        local_replay(program[:final_clear] + program[final_clear + 1:])
    except ValueError as error:
        require('dirty private exit' in str(error), 'omitted clear failed for an unrelated reason')
    else:
        raise ValueError('accepted omitted final clear')
    done.append('omitted_final_clear_rejected')
    return done


def render(result):
    """Stable receipt layout: one top-level key per line, long lists one item per line."""
    def compact(value):
        return json.dumps(value, sort_keys=True)
    lines = []
    for key in sorted(result):
        value = result[key]
        if isinstance(value, list) and len(value) > 8:
            body = ',\n'.join('  ' + compact(item) for item in value)
            lines.append(f' {compact(key)}: [\n{body}\n ]')
        else:
            lines.append(f' {compact(key)}: {compact(value)}')
    return '{\n' + ',\n'.join(lines) + '\n}\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=PACKAGE.parents[1])
    parser.add_argument('--write', action='store_true', help='regenerate the exact result receipt')
    args = parser.parse_args()
    data, pr1918, raws = load(args.root)
    result = run(data, pr1918)
    local_maps = {o: local_replay(data['program'][o])[0] for o in ('forward', 'backward')}
    controls = negative_controls(args.root, data, raws, local_maps)
    require(set(controls) <= set(result['controls']), 'control list drift')
    receipt = PACKAGE / 'RESULT.json'
    if args.write:
        receipt.write_text(render(result), encoding='utf-8')
    else:
        canonical = json.loads(json.dumps(result, sort_keys=True))
        require(canonical == json.loads(receipt.read_text(encoding='utf-8')), 'result receipt differs')
    print(f"{STATUS} calls={result['calls']} rows={result['centre_rows']} "
          f"global_rank_q={result['global_rank_q']} global_rank_mod_p={result['global_rank_mod_p']} "
          f"dependent_pairs={result['dependent_pairs']} "
          f"formal_pair_rank_hist={result['dependent_pair_rank_histograms']['formal']} "
          f"pair_local_rank_hist={result['dependent_pair_rank_histograms']['pair_roles_0_223_owners']} "
          f"deficient_formal_or_pair_local={len(result['deficient_pairs_formal_or_pair_local'])} "
          f"f0_b1_same_block_data_only_ranks={sorted(Counter(w['rank_pair_roles_0_111_owners'] for w in result['forward0_backward1_same_block_pairs_data_only_kernels']).items())} "
          f"f0_b1_target_zeroed_ranks={sorted(Counter(w['rank_target_block_zeroed_others_formal'] for w in result['forward0_backward1_same_block_pairs_data_only_kernels']).items())} "
          f"controls={len(result['controls'])}")


if __name__ == '__main__':
    main()
