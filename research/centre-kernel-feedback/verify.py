#!/usr/bin/env python3
"""Exact causal transport of the selected terminal-Y error kernel.

Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor implementation is imported. PR2799 supplies the kernel vectors;
PR2622 supplies coefficient digests. Both are authenticated comparison data.
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
PRIME = 2147483647
IGNORED = {'idle_cover_sweep', 'terminal_Y_translations',
           'bank_padding_cover_sweep', 'translate_every_live_family'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(rows):
    # Credited PR2622 coefficient serialization, not executable predecessor code.
    return hashlib.sha256(json.dumps([
        {str(k): str(v) for k, v in sorted(row.items())} for row in rows
    ], separators=(',', ':')).encode()).hexdigest()


def authenticate(raw, pin):
    require(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source SHA256')
    if 'git_blob' in pin:
        require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
                == pin['git_blob'], 'source Git blob')


def load():
    pins = json.loads((HERE/'SOURCES.json').read_text())
    for pin in pins['files']:
        if pin['usage'] == 'input':
            authenticate((ROOT/pin['path']).read_bytes(), pin)
    refs = {}
    for pin in pins['references']:
        raw = gzip.decompress((HERE/pin['local']).read_bytes())
        authenticate(raw, pin)
        refs[pin['local'].removesuffix('.gz')] = json.loads(raw)
    data = {}
    with tarfile.open(ROOT/'research/community-frontier1094-audit/selected-replay.tar.gz') as tar:
        members = tar.getmembers()
        for name, pin in pins['archive_members'].items():
            matches = [m for m in members if m.name == pin['path']]
            require(len(matches) == 1 and matches[0].isfile(), 'unique archive member')
            raw = tar.extractfile(matches[0]).read()
            authenticate(raw, pin)
            data[name] = json.loads(gzip.decompress(raw))
    return data, refs


def add(dst, src, coefficient=1):
    for key, value in src.items():
        new = dst.get(key, 0)+coefficient*value
        if new:
            dst[key] = new
        else:
            dst.pop(key, None)


def scalar(state, op):
    name, dst = op[0], tuple(op[1])
    if name in ('add', 'copy'):
        src = tuple(op[2])
        require(src != dst, 'distinct assignment roles')
    if name == 'add':
        add(state[dst], state[src], Q(op[3], op[4]))
    elif name == 'copy':
        state[dst] = dict(state[src])
    elif name == 'clear':
        state[dst] = {}
    elif name == 'scale':
        q = Q(op[2], op[3])
        state[dst] = {k: q*v for k, v in state[dst].items() if q*v}
    else:
        raise ValueError('unknown scalar instruction')


def local_maps(program, orientation):
    """Forward symbolic replay: ordinary inputs 0..703, insertions 704..711."""
    state = {('L', i): {i: Q(1)} for i in range(704)}
    state.update({('C', i): {712+i: Q(1)} for i in range(8)})
    sources, count = [], 0
    for tag, *args in program:
        if tag == 'scalar':
            scalar(state, args[0])
            count += 1
        elif tag == 'center':
            k = args[0]
            require(k == len(sources) and args[3] == 8, 'ordered rank-eight cuts')
            sources.append(dict(state['C', k]))
            state['C', k][704+k] = Q(1)
        else:
            require(tag in {'phase', 'climb', 'adapter', 'residual_adapter'},
                    'unknown local projection')
    require(len(sources) == 8, 'eight cuts')
    require(all(not state['C', k] for k in range(8)), 'private restoration')
    require(all(j < 704 for row in sources for j in row), 'no within-call cut feedback')
    response = [{} for _ in range(8)]
    for i in range(704):
        row = state['L', i]
        require(all(j < 712 for j in row), 'no initial private influence')
        ordinary = {j: q for j, q in row.items() if j < 704}
        expected = {i: Q(1)}
        if orientation == 'forward' and 112 <= i < 224:
            expected[i-112] = Q(1)
        if orientation == 'backward' and i < 112:
            expected[i+112] = Q(-1)
        require(ordinary == expected, 'complete local ordinary endpoint')
        for j, q in row.items():
            if j >= 704:
                response[j-704][i] = q
    return sources, response, count


def call_key(call):
    return tuple(call[k] for k in ('time', 'replica', 'stage', 'provider_id'))


def validate(data):
    require((data['word']['h'], data['word']['v'], data['word']['R']) == (9, 112, 480),
            'selected 480-helper word')
    template = data['global']
    require(template['live'] == 14336, 'ordinary owner count')
    calls = {call_key(c): c for c in template['calls']}
    require(len(calls) == len(template['calls']) == 144, 'unique calls')
    scheduled = []
    for event in template['execution_schedule']:
        kind = event['kind']
        if kind == 'local_cover_sweep':
            c = calls[call_key(event)]
            require(c['orientation'] in ('forward', 'backward'), 'orientation')
            raw = canonical(data['program'][c['orientation']])
            require(hashlib.sha256(raw).hexdigest() == c['local_program_sha256'], 'call hash')
            owners = [r[0] for r in c['owners']]
            require(len(owners) == len(set(owners)) == 704 and
                    all(type(i) is int and 0 <= i < 14336 for i in owners), 'owner injection')
            start = 896*c['replica']+224*c['pair']
            require(owners[:224] == list(range(start, start+224)), 'stream numbering')
            scheduled.append(c)
        elif kind in ('bridge', 'terminal'):
            require(event['replicas'] == [event['replica']] and 0 <= event['replica'] < 16,
                    'single replica event')
            if kind == 'bridge':
                require(event['src'] != event['dst'] and
                        all(0 <= event[k] < 4 for k in ('src', 'dst')) and
                        event['coefficient'] in (-1, 1), 'bridge schema')
            else:
                require(event['pairs'] == 4, 'terminal pairs')
        else:
            require(kind in IGNORED, 'unknown global projection')
    require(len(scheduled) == len({call_key(c) for c in scheduled}) == 144,
            'complete chronology')
    return calls, scheduled


def global_event(arrays, event):
    kind = event['kind']
    if kind == 'bridge':
        base = 896*event['replica']
        s, d = base+224*event['src'], base+224*event['dst']
        q = event['coefficient']
        for rows in arrays:
            for k in range(112):
                add(rows[d+k], rows[s+k], q)
                add(rows[s+112+k], rows[d+112+k], -q)
    elif kind == 'terminal':
        for rows in arrays:
            for pair in range(4):
                for k in range(112):
                    x = 896*event['replica']+224*pair+k
                    rows[x], rows[x+112] = rows[x+112], {j: -q for j, q in rows[x].items()}
    else:
        require(kind in IGNORED, 'unknown global projection')


def propagate(data, local, calls, injections, tangent=False):
    """Local forward source/response factorization, complete global chronology.

    Tangent uses t=1+eps forward and t^-1=1-eps backward, eps^2=0.
    The transcript is K times the supplied insertion matrix, not initial inputs.
    """
    values = [{} for _ in range(14336)]
    slopes = [{} for _ in values]
    transcript = []
    number = 0
    for event in data['global']['execution_schedule']:
        if event['kind'] != 'local_cover_sweep':
            global_event((values, slopes) if tangent else (values,), event)
            continue
        c = calls[call_key(event)]
        owners = [r[0] for r in c['owners']]
        source, response, _ = local[c['orientation']]
        cuts = []
        for row in source:
            out = {}
            for i, q in row.items():
                add(out, values[owners[i]], q)
            cuts.append(out)
        transcript.extend(cuts)
        for rows in ((values, slopes) if tangent else (values,)):
            for k in range(112):
                x, y = owners[k], owners[k+112]
                if c['orientation'] == 'forward': add(rows[y], rows[x])
                else: add(rows[x], rows[y], -1)
        sign = 1 if c['orientation'] == 'forward' else -1
        for k in range(8):
            for i, q in response[k].items():
                add(values[owners[i]], injections[8*number+k], q)
                if tangent: add(slopes[owners[i]], cuts[k], sign*q)
        number += 1
    require(number == 144, 'all calls propagated')
    return values, transcript, slopes


def transpose(rows, size):
    out = [{} for _ in range(size)]
    for i, row in enumerate(rows):
        for j, q in row.items(): out[j][i] = q
    return out


def row_basis(rows):
    pivots, selected = {}, []
    for index, original in enumerate(rows):
        row = dict(original)
        while row:
            lead = min(row)
            if lead not in pivots:
                q = row[lead]
                pivots[lead] = {i: v/q for i, v in row.items()}
                selected.append(index)
                break
            add(row, pivots[lead], -row[lead])
    return selected, sorted(pivots)


def determinant_mod(rows, selected_rows, selected_columns):
    """Separate dense prime-field minor elimination; no rational pivot states."""
    require(len(selected_rows) == len(selected_columns), 'square minor')
    matrix = [[(q.numerator*pow(q.denominator, -1, PRIME)) % PRIME
               if (q := rows[i].get(j, Q(0))) else 0 for j in selected_columns]
              for i in selected_rows]
    determinant = 1
    for j in range(len(matrix)):
        pivot = next((i for i in range(j, len(matrix)) if matrix[i][j]), None)
        if pivot is None: return 0
        if pivot != j:
            matrix[j], matrix[pivot] = matrix[pivot], matrix[j]
            determinant = -determinant
        a = matrix[j][j]
        determinant = determinant*a % PRIME
        inv = pow(a, -1, PRIME)
        for i in range(j+1, len(matrix)):
            if matrix[i][j]:
                q = matrix[i][j]*inv % PRIME
                for k in range(j+1, len(matrix)):
                    matrix[i][k] = (matrix[i][k]-q*matrix[j][k]) % PRIME
                matrix[i][j] = 0
    return determinant % PRIME


def rank_record(rows):
    chosen, columns = row_basis(rows)
    det = determinant_mod(rows, chosen, columns)
    require(det != 0 or not columns, 'independent modular rank minor')
    return dict(rank=len(columns), rows=chosen, columns=columns,
                determinant_mod_2147483647=det)


def kernel_matrix(reference):
    y = reference['readouts']['Y']
    basis = [{j: Q(1)} for j in y['zero_columns']]
    basis += [{int(j): Q(q) for j, q in row.items()}
              for row in y['noncoordinate_kernel_basis']]
    require(len(basis) == 149 and len(y['zero_columns']) == 128, 'reference kernel size')
    require(len({max(row) for row in basis}) == 149 and
            all(row[max(row)] == 1 for row in basis), 'independent reference basis')
    return basis, transpose(basis, 1152)


def run():
    data, refs = load()
    calls, scheduled = validate(data)
    local = {name: local_maps(data['program'][name], name)
             for name in ('forward', 'backward')}
    for name, (_, response, _) in local.items():
        require(digest(transpose(response, 704)) ==
                refs['pr2622-result.json']['local_error_response_sha256'][name],
                'independent local response coefficients')
    # Replay every baseline error column, not only the inherited kernel.
    ordinary, full_feedback, _ = propagate(data, local, calls, [{j: Q(1)} for j in range(1152)])
    require(digest(ordinary) == refs['pr2622-result.json']['response_sha256'],
            'all baseline response coefficients')
    require(all(j < i for i, row in enumerate(full_feedback) for j in row), 'strict causal feedback')
    yrows = [row if i % 224 >= 112 else {} for i, row in enumerate(ordinary)]
    # Kernel upper bound below; independent field rank provides the lower bound.
    yref = refs['pr2799-result.json']['readouts']['Y']
    # Sparse field elimination of the pinned minor is used for the large baseline.
    allowed = set(yref['selected_error_columns'])
    pivots = {}
    for owner in yref['pivot_output_owners']:
        row = {j: q.numerator*pow(q.denominator, -1, PRIME) % PRIME
               for j, q in yrows[owner].items() if j in allowed}
        row = {j: q for j, q in row.items() if q}
        while row:
            lead = max(row)
            if lead not in pivots:
                inv = pow(row[lead], -1, PRIME)
                pivots[lead] = {j: q*inv % PRIME for j, q in row.items()}
                break
            q = row[lead]
            for j, value in pivots[lead].items():
                new = (row.get(j, 0)-q*value) % PRIME
                if new: row[j] = new
                else: row.pop(j, None)
        else:
            raise ValueError('singular baseline minor')
    require(len(pivots) == 1003, 'baseline rank lower bound')
    basis, injections = kernel_matrix(refs['pr2799-result.json'])
    require(all(scheduled[j//8]['stage'] == 8 and scheduled[j//8]['orientation'] == 'forward'
                for j in yref['zero_columns']), 'coordinate kernel is final forward stage')
    endpoint, feedback, slopes = propagate(data, local, calls, injections, tangent=True)
    require(all(not row for i, row in enumerate(endpoint) if i % 224 >= 112),
            'complete terminal-Y kernel')
    require(all(j >= 128 for row in feedback for j in row), 'terminal coordinates need no repair')
    expected_feedback = []
    for row in full_feedback:
        out = {}
        for j, q in row.items(): add(out, injections[j], q)
        expected_feedback.append(out)
    require(feedback == expected_feedback, 'two computations of K times kernel')
    groups = {}
    for name in ('forward', 'backward'):
        rows = [row if scheduled[i//8]['orientation'] == name else {}
                for i, row in enumerate(feedback)]
        groups[name] = dict(rank_record(rows), sites=sum(bool(r) for r in rows),
                            terms=sum(map(len, rows)))
    sensitivity = [row if i % 224 >= 112 else {} for i, row in enumerate(slopes)]
    sensitivity_rank = rank_record(sensitivity)
    require(sensitivity_rank['rank'] == 21, 'fixed noncoordinate directions change')
    require(all(groups[n]['rank'] == 21 for n in groups), 'two orientation feedback ranks')
    first = 128
    witness = {i: str(row[first]) for i, row in enumerate(sensitivity) if first in row}
    feedback_rows = [{str(j-128): str(q) for j, q in sorted(row.items())} for row in feedback]
    nonunit = sum(q not in (1, -1) for row in feedback for q in row.values())
    nonunit += sum(q not in (1, -1) for row in basis[128:] for q in row.values())
    return dict(status='PASS_CENTRE_KERNEL_FEEDBACK', error_sites=1152,
                call_orientations=[c['orientation'] for c in scheduled],
                expanded_repair_invoice=dict(oracle_H=42, oracle_H_inverse=42,
                    signed_unit_adds=2131+2*nonunit, rational_scales=2*nonunit,
                    clean_work_fields=43, source_fields=21, total_instructions=2215+4*nonunit,
                    formal_dirty_injection_targets=1152, source_written_at_any_prefix=False),
                Y_rank=1003, kernel_dimension=149, terminal_coordinate_directions=128,
                noncoordinate_directions=21, feedback_sites=sum(bool(r) for r in feedback),
                feedback_terms=sum(map(len, feedback)), feedback_sha256=digest(feedback),
                kernel_sha256=digest(basis), baseline_response_sha256=digest(ordinary),
                causal_feedback_sha256=digest(full_feedback),
                local_scalar_instructions={n: local[n][2] for n in local},
                orientation_feedback=groups, reciprocal_tangent=sensitivity_rank,
                reciprocal_tangent_sha256=digest(sensitivity),
                witness_basis=basis[first] and {str(j): str(q) for j, q in basis[first].items()},
                witness_tangent_Y_sha256=digest([{int(i): Q(q) for i, q in witness.items()}]),
                witness_tangent_Y_nonzero=len(witness),
                witness_tangent_Y_first16=dict(list(witness.items())[:16]),
                correction_matrix_noncoordinate=feedback_rows,
                direct_repair_invoice=dict(clean_work_fields=42, forward_oracle_calls=42,
                    inverse_oracle_calls=42, build_and_uncompute_unit_adds=168,
                    injection_weighted_adds=sum(map(len, feedback))+sum(map(len, basis[128:])),
                    correction_weighted_adds=sum(map(len, feedback)),
                    original_kernel_weighted_adds=sum(map(len, basis[128:]))),
                scope='Common-frame scalar projection with arbitrary linear centre operators; no native routing, supplier or kappa claim.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.out and args.out.exists(): raise FileExistsError(args.out)
    result = run()
    correction = {str(i): row for i, row in enumerate(result.pop('correction_matrix_noncoordinate')) if row}
    if args.out:
        args.out.mkdir()
        (args.out/'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
        # One nonempty chronological source row per line, keeping the certificate reviewable.
        lines = [json.dumps(str(i))+': '+json.dumps(row, sort_keys=True) for i, row in correction.items()]
        (args.out/'CORRECTION.json').write_text('{\n  '+',\n  '.join(lines)+'\n}\n')
    else:
        require(canonical(result) == canonical(json.loads((HERE/'RESULT.json').read_text())),
                'typed result receipt mismatch')
        require(canonical(correction) == canonical(json.loads((HERE/'CORRECTION.json').read_text())),
                'typed correction receipt mismatch')
    print(result['status'], 'kernel=149 correction_sites=546 correction_rank=21+21 no_new_kappa')


if __name__ == '__main__': main()
