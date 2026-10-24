#!/usr/bin/env python3
"""Check all eight native services for the dyadic involution pair."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json

HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
ACCEPTED = HERE.parent/'row-capture-native-review-20261020'
HELPER = ACCEPTED/'check.py'
PIN = '5b8f2839db4fd4b0e4b24d5b8f8938c74a15497ae0e58f324896cf431d3ecb84'
if sha256(HELPER.read_bytes()).hexdigest() != PIN:
    raise ValueError('Independent helper pin')
spec = importlib.util.spec_from_file_location('independent_row_review', HELPER)
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)
q.read(HELPER, PIN)
need, read, frozen = q.need, q.read, q.frozen
P = q.P
SOURCE = q.RAW/'row-involution-native-20261020'
ALG = LANES/'controller-followthrough-20261017/row-involution-20261020'


def pair_matrices(cyclic):
    h, hi, covered = q.unit(112), q.unit(112), set()
    for item in cyclic['pair_codes']:
        ports = item['ports']
        need(len(ports) == 2 and not covered.intersection(ports), 'Disjoint actual pair')
        covered.update(ports)
        need(not set(ports).intersection(P) or set(ports) <= set(P), 'Complete selected pair')
        a, b = map(F, item['matrix'][0])
        c, d = map(F, item['matrix'][1])
        det = a*d-b*c
        need(abs(det) == 2, 'Actual signed pair determinant')
        inverse = [[d/det, -b/det], [-c/det, a/det]]
        for i, p in enumerate(ports):
            h[p] = {r: F(v) for r, v in zip(ports, item['matrix'][i]) if F(v)}
            hi[p] = {r: v for r, v in zip(ports, inverse[i]) if v}
    need(len(covered) == 48 and q.mul(h, hi) == q.unit(112) and q.mul(hi, h) == q.unit(112),
         'Actual physical pair transform inverse orders')
    return h, hi


def matrices(raw, algebra, cyclic):
    e = q.rows(raw['model']['response'])
    u, v = q.rows(raw['model']['correction_U']), q.rows(raw['model']['correction_V'])
    vp = [{j: row[p] for j, p in enumerate(P) if p in row} for row in v]
    vpt = q.transpose(vp, 16)
    vi = [{j: x/(2 if j < 8 else 1) for j, x in row.items()} for row in vpt]
    need(q.mul(vi, vp) == q.unit(16) and q.mul(vp, vi) == q.unit(16), 'Actual pivot inverse')
    vrur = []
    for row in v:
        acc = {}
        for p, x in row.items():
            if p not in P:
                q.add(acc, u[p], x)
        vrur.append(acc)
    rhs = [{i: F(-2)} for i in range(16)]
    for row, old in zip(rhs, vrur):
        q.add(row, old, F(-1))
    up = q.mul(vi, rhs)
    new_u = [dict(row) for row in u]
    for p, row in zip(P, up):
        new_u[p] = row
    need(q.mul(v, new_u) == [{i: F(-2)} for i in range(16)], 'Completion centre action')
    a = q.unit(112)
    for row, correction in zip(a, q.mul(new_u, v)):
        q.add(row, correction)
    at = q.transpose(a, 112)
    need(q.mul(a, a) == q.unit(112) and q.mul(at, at) == q.unit(112), 'Both involutions')
    displacement = [dict(row) for row in a]
    for i, row in enumerate(displacement):
        q.add(row, {i: F(1)}, F(-1))
    need(q.rank(displacement) == 16, 'Actual displacement rank16')
    source_change = [dict(row) for row in a]
    for row, old in zip(source_change, e):
        q.add(row, old, F(-1))
    need(q.rank(source_change) == 16, 'Actual source change rank16')
    need(sum(row.get(i, F(0)) for i, row in enumerate(a)) == 80, 'Actual trace80')
    need(all(a[p] == e[p] for p in range(112) if p not in P), 'Only selected physical rows change')
    h, hi = pair_matrices(cyclic)
    drows = q.mul(v, hi)
    mode = q.unit(112)
    seen = set()
    for j, d in enumerate(drows):
        size, p = len(d), P[j]
        need(size == (6 if j < 8 else 8) and d.get(p) == 1 and set(d.values()) <= {F(-1), F(1)},
             'Actual signed block and positive pivot')
        need(not seen.intersection(d), 'Disjoint mode blocks')
        seen.update(d)
        for i, value in d.items():
            q.add(mode[i], d, -value+(size-2 if i == p else 0))
    need(seen == set(range(112)), 'Sixteen blocks cover all actual ports')
    need(q.mul(q.mul(hi, mode), h) == a, 'Separate signed-mode construction')
    mode_at = q.mul(q.mul(h, at), hi)
    need(mode_at == q.transpose(mode, 112), 'Physical transpose in actual mode coordinates')
    for name, value in [('response', a), ('response_transpose', at),
                        ('response_inverse', a), ('response_inverse_transpose', at),
                        ('correction_U', new_u), ('correction_V', v),
                        ('mode_response', mode), ('mode_response_transpose', mode_at),
                        ('original_response', e)]:
        need(q.rows(algebra[name]) == value, 'Independent matrix binding: '+name)
    need(algebra['pivots'] == P, 'Actual ordered pivots')
    return {'A': a, 'AT': at}, {'A': mode, 'AT': mode_at}, q.mul(q.mul(h, e), hi), {
        'block_sizes': [len(r) for r in drows], 'rank_A_minus_I': 16,
        'rank_A_minus_E': 16, 'trace_A': 80,
        'centre_action': '-2I16', 'both_involution_orders': True,
        'determinant': '1', 'determinant_proof': 'Sixteen rank-one mode blocks each have determinant1+d^T u=-1.',
    }


def retuned_events(old, oldmode, newmode, cyclic):
    parameters = {r['id']: r for r in cyclic['parameters']}
    events, updates, claimed = deepcopy(old['events']), [], set()
    for item in old['transfer_records']:
        index = item['event']
        need(index not in claimed, 'Distinct actual transfer slot')
        claimed.add(index)
        if item['part'] == 'large48':
            par = parameters[item['parameter']]
            carriers = cyclic['cyclic_carriers'][par['vertex']]
            r, c = carriers[par['row']], carriers[par['column']]
        else:
            need(item['part'] == 'small64', 'Actual transfer family')
            r, c = item['target_port'], item['source_port']
        before, after = oldmode[r][c], newmode[r][c]
        event = events[index]
        need(event[0] == 'scalar' and event[1][0] == 'add', 'Actual scalar transfer event')
        sign = F(event[1][3])/before
        need(sign in (F(-1), F(1)) and after and after.denominator == 1,
             'Original support and exact orientation')
        if before != after:
            updates.append({'original_event': index, 'mode_row': r, 'mode_column': c,
                            'old_coefficient': str(sign*before), 'new_coefficient': str(sign*after)})
        event[1][3] = str(sign*after)
    need(len(updates) == 96, 'Exactly96 changed source transfer slots')
    return events, updates


def expected_columns(response, direction):
    out = q.unit(640)
    for r, row in enumerate(response):
        if direction == 'forward':
            q.add(out[112+r], row)
        else:
            for c, value in row.items():
                q.add(out[c], {112+r: -value})
    return q.transpose(out, 640)


def check_word(word, old, reference, algebra, response, oldmode, mode, cyclic, name, direction, ledger):
    selected = {112+p for p in P}
    retuned, updates = retuned_events(old, oldmode, mode, cyclic)
    kept, removed, indices = [], [], []
    for i, event in enumerate(retuned):
        target = event[1] if event[0] == 'native' else event[1][1]
        read_selected = event[0] == 'scalar' and event[1][0] == 'add' and event[1][2] in selected
        if target in selected or (direction == 'backward' and read_selected):
            removed.append(event)
        else:
            need(not read_selected, 'No retained selected-target read')
            kept.append(event)
            indices.append(i)
    need(word['retained_original_event_indices'] == indices, 'Exact retained index ledger')
    need(len(removed) == 250 and Counter(e[4] for e in removed if e[0] == 'native') == {1: 128},
         'Exactly250 selected-path events removed')
    need(ledger['changed_original_transfer_weights'] == updates, 'Exact retuning receipt')
    need(ledger['removed_events'] == len(removed) and
         ledger['removed_scalar_primitives_after_retuning'] ==
         q.price([e[1] for e in removed if e[0] == 'scalar']), 'Exact removal invoice')
    query = []
    for op, target, origin, value in algebra['final_query_words'][name]:
        if direction == 'forward':
            query.append(['scalar', [op, 112+target, None if origin is None else origin-112, value], 1])
        elif op == 'scale':
            query.append(['scalar', [op, 112+target, None, str(1/F(value))], 1])
        else:
            need(op == 'add', 'Late query grammar')
            query.append(['scalar', ['add', origin-112, 112+target, str(-F(value))], 1])
    progress = [['native', 112+p, 0, 1, 9, 'capture-full'] for p in P]
    need(word['events'] == kept+progress+query, 'Exact native and scalar chronology')
    need(word['stage_ranges'] == {
        'retained_core': [0, len(kept)], 'selected_full_progress': [len(kept), len(kept)+16],
        'late_query': [len(kept)+16, len(word['events'])]}, 'Exact stage boundaries')
    for key in ('frames', 'start', 'final', 'input_views', 'output_views'):
        need(word[key] == reference[key], 'Exact accepted physical geometry: '+key)
    need(word['native_recipes'] == reference['native_recipes'], 'Every accepted native phase record')
    current = list(word['start'])
    count, used = Counter(), set()
    for i, event in enumerate(word['events']):
        if i == len(kept):
            need(all(current[p] == 1 for p in range(112)) and
                 all(current[p] == 0 for p in selected), 'Late source cut and unadvanced selected Y')
        if event[0] == 'native':
            _, field, before, after, rank, key = event
            need(0 <= field < 224 and current[field] == before, 'Exact native input frame')
            need(rank == word['native_recipes'][key]['rank'], 'Exact native rank')
            if key == 'capture-full':
                need(field in selected and (before, after, rank) == (0, 1, 9), 'Accepted FULL child binding')
            else:
                need(key == str(before)+':'+str(after), 'Accepted ordered native frame pair')
            current[field] = after
            count[rank] += 1
            used.add(key)
        else:
            _, scalar, frame = event
            op, target, origin, _ = scalar
            need(0 <= target < 224 and current[target] == frame, 'Exact scalar target frame')
            if op == 'add':
                need(0 <= origin < 224 and current[origin] == frame and origin != target,
                     'Exact scalar source frame')
            else:
                need(op == 'scale' and origin is None, 'Exact scale grammar')
    need(current == word['final'] and used == set(word['native_recipes']), 'Complete frame and recipe ledger')
    need(count == {1: 1392, 2: 64, 3: 48, 9: 16}, 'Complete profile')
    scalars = [e[1] for e in word['events'] if e[0] == 'scalar']
    columns = q.reverse(scalars, 640)
    need(columns == expected_columns(response, direction), 'All640 independent input columns')
    rows, growth = q.prefix(scalars, 640)
    need(q.transpose(rows, 640) == columns and rows[224:] == q.unit(640)[224:],
         'Separate forward row pass and416 arbitrary outside roles')
    if direction == 'backward':
        need(rows[112:224] == q.unit(640)[112:224], 'All target baselines restored')
    norm = {('A', 'forward'): '70', ('A', 'backward'): '22',
            ('AT', 'forward'): '30', ('AT', 'backward'): '62'}[name, direction]
    need(growth == {'row_one_norm': norm, 'binary_height': 1}, 'Exact complete content prefix bound')
    core_price, query_price = (6456, 2960) if name == 'A' else (6952, 1984)
    need(q.price(scalars) == core_price+query_price and
         q.price([e[1] for e in kept if e[0] == 'scalar']) == core_price and
         q.price([e[1] for e in query]) == query_price, 'Complete local scalar invoice')
    need(q.reverse([e[1] for e in kept if e[0] == 'scalar'], 640) != columns,
         'Omitted late query control')
    if direction == 'backward':
        reversed_query = [e[1] for e in kept if e[0] == 'scalar']+[e[1] for e in reversed(query)]
        need(q.reverse(reversed_query, 640) != columns, 'Wrong reversed inverse-transpose chronology')
    return {
        'input_columns': 640, 'unchanged_arbitrary_roles': 416,
        'native_profile': dict(sorted(count.items())), 'native_children': sum(count.values()),
        'native_mass': sum(k*v for k, v in count.items()), 'real_scalar_primitives': core_price+query_price,
        'retained_scalar_primitives': core_price, 'late_query_scalar_primitives': query_price,
        'input_views': 112, 'output_views': 96, 'native_side_maps_upper_bound': 3008,
        'new_fields': 0, 'private_fields': 0, 'odd_scans': 0, 'growth': growth,
        'retuned_source_slots': len(updates), 'removed_events': len(removed),
        'phase_scope': 'All native recipes, exact frame arrays, and boundary maps are inherited byte-for-byte.',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    frozen(ACCEPTED, 'FREEZE.json', '488dc693d6e7d48e8024455c9c3f2f899f94a8e9058aef28ad38f7c46c7d8532')
    frozen(ALG, 'FREEZE.json', '538ec208e510af7ee29aff4783d304e393c967697a6612e5c42e38fbc0ab9be2')
    read(ALG/'LIMITS-FREEZE.json', '775c1b565ec0aa969f2dbecebb04f4b9a82a561e7e7d842c2b1abae7a75509a6')
    read(ALG/'COMPLETION-LIMITS.md', '91bd564b31766300cc89b87cf808439135d89c27bde655a2fc1842646c304607')
    frozen(SOURCE, 'FREEZE.json', 'ad8a365247b60ff3621e701bb88d8692cc4f545ae09b3ec8fbe8d69b7f348ea1')
    raw = json.loads(read(q.RAW/'odd16-normal-v2/EXTENSION-PROGRAM.json.gz',
                          'd466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4', True))
    algebra = json.loads(read(ALG/'run-normal/ROW-INVOLUTION.json',
                              'a25551b3b99b82477fde561a742fabe1114acbfe6c67cd14284747aaac3dd95b'))
    reference = json.loads(read(q.NATIVE/'direct-normal/DIRECT-FULL-CAPTURE.json.gz',
                                'fa3342f8b4ddf286f6f67922f4184486ec0162610e4de6a457de3eed0750504c', True))
    cyclic = json.loads(read(LANES/'independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json',
                             '3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585'))
    payload = json.loads(read(SOURCE/'run-normal-final/ROW-INVOLUTION-NATIVE.json.gz',
                              'aa5356c5cb618984ba3c76c40a255ebd26a66f0a88ac9f57792ab8f6677f9a30', True))
    responses, modes, oldmode, algebra_report = matrices(raw, algebra, cyclic)
    need(payload['selected_ports'] == P and payload['ports'] == raw['model']['ports'], 'Actual port arrays')
    need(set(payload['providers']) == {'base', 'extra'} and
         payload['providers']['base'] == payload['providers']['extra'], 'Both providers')
    for name in responses:
        need(q.rows(payload['responses'][name]) == responses[name], 'Actual response contract')
    reports = {}
    for provider, families in payload['providers'].items():
        need(set(families) == {'A', 'AT'}, 'Both response matrices')
        reports[provider] = {}
        for name, directions in families.items():
            need(set(directions) == {'forward', 'backward'}, 'Both shear directions')
            reports[provider][name] = {}
            for direction, word in directions.items():
                reports[provider][name][direction] = check_word(
                    word, raw['providers'][provider][direction], reference['providers'][provider],
                    algebra, responses[name], oldmode, modes[name], cyclic, name, direction,
                    payload['transfer_ledgers'][provider][name][direction])
            fword = directions['forward']
            bword = directions['backward']
            fs = [e[1] for e in fword['events'][slice(*fword['stage_ranges']['late_query'])]]
            bs = [e[1] for e in bword['events'][slice(*bword['stage_ranges']['late_query'])]]
            fm = q.transpose(q.reverse(fs, 224), 224)
            bm = q.transpose(q.reverse(bs, 224), 224)
            ft = q.transpose(fm, 224)
            need(q.mul(ft, bm) == q.unit(224) and q.mul(bm, ft) == q.unit(224),
                 'Both exact isolated-query inverse-transpose orders')
    report = {
        'status': 'PASS_INDEPENDENT_NATIVE_ROW_INVOLUTIONS',
        'algebra': algebra_report, 'literal_words': reports,
        'new_phase_operators': 0, 'phase_source_review':
        '488dc693d6e7d48e8024455c9c3f2f899f94a8e9058aef28ad38f7c46c7d8532',
        'negative_controls': ['omitted late query', 'reversed backward-query chronology'],
        'scope': 'All eight complete local mixed-output words. Common-frame gauge words and routed caller, decoder, recursive host, or supplier cost are not established here.',
    }
    args.out.mkdir(parents=True, exist_ok=True)
    for name, value in [('REVIEW.json', report), ('INPUTS.json', q.INPUTS)]:
        (args.out/name).write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    print(report['status'], flush=True)


if __name__ == '__main__':
    main()
