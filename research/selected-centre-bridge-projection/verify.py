#!/usr/bin/env python3
"""Exact scalar controller projection, not a native supplier replay.

Prepared for BigCactusLabs with substantial OpenAI Codex assistance. Apache-2.0.
Projection: Adam Gall / PR1918 and thakrarsagar / PR2199.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
PREFIX = 'candidate/strict/global/'
MEMBERS = {
    'template': (PREFIX + 'hosted/GLOBAL-TEMPLATE.json.gz',
                 '2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760'),
    'programs': (PREFIX + 'base/providers/gauge44/LOCAL-PROGRAMS.json.gz',
                 '241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a'),
    'word': (PREFIX + 'base/providers/gauge44/CANONICAL-WORD.json.gz',
             '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219'),
}
IDENTITY_LOCAL = {'climb', 'adapter', 'residual_adapter'}
IDENTITY_GLOBAL = {'idle_cover_sweep', 'terminal_Y_translations',
                   'bank_padding_cover_sweep', 'translate_every_live_family'}
STATUS = 'PASS_SELECTED_CENTRE_BRIDGE_PROJECTION'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def axpy(target, source, coefficient):
    for column, value in source.items():
        value = target.get(column, Q(0)) + coefficient * value
        if value:
            target[column] = value
        else:
            target.pop(column, None)


def scaled(row, factor):
    return {column: value * factor for column, value in row.items() if value * factor}


def rank(rows):
    """Exact rational elimination; no float or modular rank decisions."""
    basis = {}
    for incoming in rows:
        row = incoming.copy()
        while row:
            pivot = min(row)
            if pivot not in basis:
                basis[pivot] = scaled(row, 1 / row[pivot])
                break
            axpy(row, basis[pivot], -row[pivot])
    return len(basis), sorted(basis)


def rows_digest(rows):
    return digest(canonical([[[i, str(q)] for i, q in sorted(row.items())] for row in rows]))


def load():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for source in pins['files']:
        if source['usage'] == 'input':
            require(digest((ROOT / source['path']).read_bytes()) == source['sha256'],
                    'source pin mismatch: ' + source['path'])
    data = {}
    with tarfile.open(ROOT / ARCHIVE) as archive:
        for key, (name, expected) in MEMBERS.items():
            stream = archive.extractfile(name)
            require(stream is not None, 'missing archive member: ' + name)
            raw = stream.read()
            require(digest(raw) == expected, 'archive member mismatch: ' + name)
            payload = gzip.decompress(raw)
            data[key] = json.loads(payload)
            if key == 'template':
                data['template_payload_sha256'] = digest(payload)
    assembly = json.loads((ROOT / 'research/community-frontier1094-audit/ASSEMBLY.json').read_text())
    require(data['template_payload_sha256'] == assembly['template_sha256'],
            'assembly does not bind the template')
    require(data['word']['R'] == 480, 'expected selected 480-helper word')
    return data


def local_forms(program, orientation):
    """Interpret literal scalar events on all 704 formal input columns."""
    state = {('L', i): {i: Q(1)} for i in range(704)}
    cuts = {}
    inventory = Counter()
    for event in program:
        tag = event[0]
        inventory[tag] += 1
        if tag == 'scalar':
            op = event[1]
            action, dst = op[0], tuple(op[1])
            if action == 'clear':
                state[dst] = {}
            elif action == 'copy':
                state[dst] = state[tuple(op[2])].copy()
            elif action == 'scale':
                state[dst] = scaled(state[dst], Q(op[2], op[3]))
            elif action == 'add':
                src = tuple(op[2])
                require(dst != src, 'aliased scalar addition')
                axpy(state[dst], state[src], Q(op[3], op[4]))
            else:
                raise ValueError('unknown scalar operation: ' + action)
        elif tag == 'center':
            k = event[1]
            require(k not in cuts and event[4] == 8, 'invalid centre event')
            cuts[k] = state['C', k].copy()
        else:
            require(tag == 'phase' or tag in IDENTITY_LOCAL, 'unknown local event')
    require(sorted(cuts) == list(range(8)), 'missing centre cuts')
    require(all(not row for (kind, _), row in state.items() if kind != 'L'),
            'private workspace not cleared')
    for i in range(704):
        expected = {i: Q(1)}
        if orientation == 'forward' and 112 <= i < 224:
            expected[i - 112] = Q(1)
        if orientation == 'backward' and i < 112:
            expected[i + 112] = Q(-1)
        require(state['L', i] == expected, orientation + ' local endpoint mismatch')
    return [cuts[k] for k in range(8)], dict(sorted(inventory.items()))


def owner(replica, pair, side, port):
    return replica * 896 + (2 * pair + side) * 112 + port


def validate_schedule(template, programs):
    require(template['live'] == 14336, 'physical-owner domain changed')
    calls = {call['time']: call for call in template['calls']}
    require(len(template['calls']) == 144 and sorted(calls) == list(range(144)), 'call times not bijective')
    hashes = {key: digest(canonical(programs[key])) for key in ('forward', 'backward')}
    per_replica = {replica: [] for replica in range(16)}
    seen = []
    for event in template['execution_schedule']:
        kind = event['kind']
        if kind == 'local_cover_sweep':
            call = calls[event['time']]
            for key in ('provider_id', 'replica', 'stage', 'time'):
                require(call[key] == event[key], 'call/schedule mismatch: ' + key)
            require(call['provider_id'] == 'gauge44', 'unknown provider')
            require(call['local_program_sha256'] == hashes[call['orientation']], 'call/program binding mismatch')
            require(call['orientation'] == ('backward' if call['stage'] % 2 else 'forward'), 'orientation mismatch')
            ids = [entry[0] for entry in call['owners']]
            require(len(ids) == len(set(ids)) == 704, 'aliased local roles')
            require(all(type(i) is int and 0 <= i < 14336 for i in ids), 'owner out of range')
            expected = [owner(call['replica'], call['pair'], side, port) for side in range(2) for port in range(112)]
            require(ids[:224] == expected, 'data layout does not match bridge ports')
            per_replica[call['replica']].append(dict(kind='local', pair=call['pair'],
                reverse=call['orientation'] == 'backward', stage=call['stage']))
            seen.append(call['time'])
        elif kind in ('bridge', 'terminal'):
            require(event['replicas'] == [event['replica']], 'ambiguous event replica')
            keys = ('kind', 'src', 'dst', 'coefficient') if kind == 'bridge' else ('kind', 'pairs')
            per_replica[event['replica']].append({key: event[key] for key in keys})
        else:
            require(kind in IDENTITY_GLOBAL, 'unknown global event: ' + kind)
    require(seen == list(range(144)), 'chronological calls changed')
    require(all(recipe == template['recipe'] for recipe in per_replica.values()), 'replica controller mismatch')
    return calls


def run_projection(template, calls, forms, with_bridges, bridge_sign=1):
    physical = [{i: Q(1)} for i in range(14336)]
    rows, labels = [], []
    for event in template['execution_schedule']:
        kind = event['kind']
        if kind == 'local_cover_sweep':
            call = calls[event['time']]
            ids = [entry[0] for entry in call['owners']]
            orientation = call['orientation']
            for k, form in enumerate(forms[orientation]):
                row = {}
                for role, coefficient in form.items():
                    axpy(row, physical[ids[role]], coefficient)
                rows.append(row)
                labels.append([call['time'], call['stage'], call['replica'], k])
            for port in range(112):
                dst, src, sign = ((ids[112 + port], ids[port], 1) if orientation == 'forward'
                                  else (ids[port], ids[112 + port], -1))
                axpy(physical[dst], physical[src], sign)
        elif with_bridges and kind == 'bridge':
            rep, dst, src, sign = (event[k] for k in ('replica', 'dst', 'src', 'coefficient'))
            sign *= bridge_sign
            for port in range(112):
                axpy(physical[owner(rep, dst, 0, port)], physical[owner(rep, src, 0, port)], sign)
                axpy(physical[owner(rep, src, 1, port)], physical[owner(rep, dst, 1, port)], -sign)
        elif with_bridges and kind == 'terminal':
            for pair in range(4):
                for port in range(112):
                    x, y = (owner(event['replica'], pair, side, port) for side in (0, 1))
                    physical[x], physical[y] = physical[y], scaled(physical[x], -1)
        # Address/frame/phase events are identities in this projection only.
    return rows, labels, physical


def controller(recipe, omit=None):
    """Separate 8-by-8 controller check; omit one of the 18 half-bridges."""
    matrix = [{i: Q(1)} for i in range(8)]
    bridge_half = 0
    for event in recipe:
        kind = event['kind']
        if kind == 'local':
            x = 2 * event['pair']
            if event['reverse']:
                axpy(matrix[x], matrix[x + 1], -1)
            else:
                axpy(matrix[x + 1], matrix[x], 1)
        elif kind == 'bridge':
            dst, src, sign = event['dst'], event['src'], event['coefficient']
            for a, b, q in ((2 * dst, 2 * src, sign), (2 * src + 1, 2 * dst + 1, -sign)):
                if bridge_half != omit:
                    axpy(matrix[a], matrix[b], q)
                bridge_half += 1
        elif kind == 'terminal':
            for pair in range(4):
                x = 2 * pair
                matrix[x], matrix[x + 1] = matrix[x + 1], scaled(matrix[x], -1)
        else:
            raise ValueError('unknown recipe event')
    return matrix, bridge_half


def result(data):
    template, programs = data['template'], data['programs']
    forms, local_counts = {}, {}
    for orientation in ('forward', 'backward'):
        forms[orientation], local_counts[orientation] = local_forms(programs[orientation], orientation)
    calls = validate_schedule(template, programs)
    full, labels, final = run_projection(template, calls, forms, True)
    old, old_labels, old_final = run_projection(template, calls, forms, False)
    require(labels == old_labels, 'comparison cut labels differ')
    predecessor = json.loads((ROOT / 'research/selected-centre-chrono-source-census/RESULT.json').read_text())
    support_histogram = {str(k): v for k, v in Counter(map(len, old)).items()}
    require(support_histogram == predecessor['centre_row_support_size_histogram'],
            'calls-only predecessor support histogram differs')
    require({key: list(map(len, value)) for key, value in forms.items()}
            == predecessor['local_centre_input_support_sizes'], 'local cut support sizes differ')
    call_table = [[index, event['time'], event['stage'], event['replica'],
                   calls[event['time']]['orientation'], calls[event['time']]['pair']]
                  for index, event in enumerate(template['execution_schedule'])
                  if event['kind'] == 'local_cover_sweep']
    require(call_table == predecessor['call_table'], 'predecessor call chronology differs')
    require(all(row == {i: Q(1)} for i, row in enumerate(final)), 'full projected endpoint is not identity')
    old_rank, _ = rank(old)
    require(old_rank == 1152, 'calls-only predecessor rank not reproduced')
    full_rank, pivots = rank(full)
    require(full_rank == 1152, 'complete centre-source rank differs')
    reversed_rows, reversed_labels, reversed_final = run_projection(
        template, calls, forms, True, bridge_sign=-1)
    require(reversed_labels == labels, 'sign-control cut labels differ')
    require(all(row == {i: Q(1)} for i, row in enumerate(reversed_final)),
            'uniform sign reversal did not preserve endpoint identity')
    reversed_rank, _ = rank(reversed_rows)
    require(reversed_rank == 1152, 'uniform sign reversal did not preserve full source rank')
    reversed_changed = [i for i, (a, b) in enumerate(zip(full, reversed_rows)) if a != b]
    require(reversed_changed, 'uniform sign reversal did not change cuts')
    changed_index = reversed_changed[0]
    good_row, bad_row = full[changed_index], reversed_rows[changed_index]
    witness_column = min(k for k in good_row.keys() | bad_row.keys()
                         if good_row.get(k, 0) != bad_row.get(k, 0))
    first_changed = next(i for i, (a, b) in enumerate(zip(old, full)) if a != b)
    old_row, new_row = old[first_changed], full[first_changed]
    first_column = min(k for k in old_row.keys() | new_row.keys()
                       if old_row.get(k, 0) != new_row.get(k, 0))
    matrix, halves = controller(template['recipe'])
    identity = [{i: Q(1)} for i in range(8)]
    require(matrix == identity and halves == 18, 'signed controller does not close')
    require(all(controller(template['recipe'], i)[0] != identity for i in range(18)),
            'omitted half-bridge did not change endpoint')
    require(rank([full[0], full[0]])[0] == 1, 'duplicate-row rank control failed')
    return {
        'status': STATUS,
        'scope': 'Exact common-frame scalar projection; no native routing or supplier claim.',
        'template_payload_sha256': data['template_payload_sha256'],
        'event_counts': dict(sorted(Counter(e['kind'] for e in template['execution_schedule']).items())),
        'local_event_counts': local_counts,
        'calls': len(calls), 'centre_rows': len(full),
        'full_projected_endpoint_identity_owners': len(final),
        'calls_only_nonidentity_owners': sum(row != {i: Q(1)} for i, row in enumerate(old_final)),
        'calls_only_rank_q': old_rank, 'bridge_rank_q': full_rank,
        'bridge_rank_pivot_columns_sha256': digest(canonical(pivots)),
        'changed_centre_rows': sum(a != b for a, b in zip(full, old)),
        'first_changed_basis_witness': {
            'cut_time_stage_replica_centre': labels[first_changed],
            'initial_owner_with_value_one': first_column,
            'all_other_initial_owners': 0,
            'calls_only_cut_value': str(old_row.get(first_column, Q(0))),
            'bridge_cut_value': str(new_row.get(first_column, Q(0))),
        },
        'changed_centre_calls': sorted({label[0] for label, a, b in zip(labels, full, old) if a != b}),
        'calls_only_rows_sha256': rows_digest(old), 'bridge_rows_sha256': rows_digest(full),
        'uniform_bridge_sign_reversal': {
            'rank_q': reversed_rank,
            'endpoint_identity_owners': len(reversed_final),
            'changed_centre_rows': len(reversed_changed),
            'rows_sha256': rows_digest(reversed_rows),
            'first_changed_basis_witness': {
                'cut_time_stage_replica_centre': labels[changed_index],
                'initial_owner_with_value_one': witness_column,
                'all_other_initial_owners': 0,
                'correct_cut_value': str(good_row.get(witness_column, Q(0))),
                'reversed_bridge_cut_value': str(bad_row.get(witness_column, Q(0))),
            },
        },
        'controls': {'omitted_half_bridges_change_endpoint': 18, 'duplicate_row_rank': 1},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='regenerate exact receipt')
    args = parser.parse_args()
    receipt = result(load())
    path = HERE / 'RESULT.json'
    if args.write:
        path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    else:
        require(receipt == json.loads(path.read_text()), 'result receipt differs')
    print(STATUS, 'rank=' + str(receipt['bridge_rank_q']),
          'changed_rows=' + str(receipt['changed_centre_rows']),
          'endpoint_owners=' + str(receipt['full_projected_endpoint_identity_owners']))


if __name__ == '__main__':
    main()
