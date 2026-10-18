#!/usr/bin/env python3
"""Reverse adjoints and terminal stream quotients of selected centre errors.

Arham Tahir, with substantial OpenAI Codex assistance. Apache-2.0.
PR2622 (ywz65) supplies the full-response claim and pinned comparison receipt;
the adjoint and quotient calculation here import no predecessor implementation.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
IDENTITY_EVENTS = {'idle_cover_sweep', 'terminal_Y_translations',
                   'bank_padding_cover_sweep', 'translate_every_live_family'}
PRIME = 2147483647


def need(ok, why):
    if not ok:
        raise ValueError(why)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def add(dest, source, coefficient=1):
    for k, value in source.items():
        new = dest.get(k, 0) + coefficient*value
        if new:
            dest[k] = new
        else:
            dest.pop(k, None)


def reverse_scalar(dual, op):
    name, dest = op[0], tuple(op[1])
    if name == 'add':
        source = tuple(op[2])
        need(source != dest, 'distinct ADD roles')
        add(dual[source], dual[dest], F(op[3], op[4]))
    elif name == 'scale':
        dual[dest] = {k: v*F(op[2], op[3]) for k, v in dual[dest].items()}
    elif name == 'clear':
        dual[dest] = {}
    elif name == 'copy':
        source = tuple(op[2])
        need(source != dest, 'distinct COPY roles')
        add(dual[source], dual[dest])
        dual[dest] = {}
    else:
        raise ValueError('unknown scalar op')


def digest(rows):
    # PR2622's explicitly credited canonical encoding, to compare coefficients.
    return sha(json.dumps([{str(k): str(v) for k, v in sorted(r.items())}
                           for r in rows], separators=(',', ':')).encode())


def load():
    sources = json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))
    for pin in sources['files']:
        if pin['usage'] == 'input':
            raw = (ROOT/pin['path']).read_bytes()
            need(sha(raw) == pin['sha256'], 'source SHA256: '+pin['path'])
            need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
                 == pin['git_blob'], 'source Git blob')
    ref = sources['reference_receipt']
    raw = (HERE/ref['local']).read_bytes()
    need(sha(raw) == ref['sha256'], 'reference receipt bytes')
    need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
         == ref['git_blob'], 'reference Git blob')
    reference = json.loads(raw)
    data = {}
    with tarfile.open(ROOT/'research/community-frontier1094-audit/selected-replay.tar.gz', 'r:gz') as archive:
        members = archive.getmembers()
        for key, pin in sources['archive_members'].items():
            matches = [m for m in members if m.name == pin['path']]
            need(len(matches) == 1 and matches[0].isfile(), 'unique source member')
            raw = archive.extractfile(matches[0]).read()
            need(sha(raw) == pin['sha256'], 'member SHA256: '+key)
            data[key] = json.loads(gzip.decompress(raw))
    return data, reference


def local_adjoint(program):
    """Every final ordinary output is an independent formal covector.

    Reverse assignment rules, including singular CLEAR/COPY, give the derivative
    at each literal private-centre insertion and the complete no-error transpose.
    """
    dual = {('L', i): {i: F(1)} for i in range(704)}
    dual.update({('C', i): {} for i in range(8)})
    cuts = {}
    scalar_count = 0
    for event in reversed(program):
        tag = event[0]
        if tag == 'scalar':
            scalar_count += 1
            reverse_scalar(dual, event[1])
        elif tag == 'center':
            k = event[1]
            need(k not in cuts and event[4] == 8, 'unique rank-eight error site')
            cuts[k] = dict(dual['C', k])
        else:
            need(tag in {'phase', 'climb', 'adapter', 'residual_adapter'},
                 'unknown projected local event')
    need(set(cuts) == set(range(8)), 'eight local error sites')
    need(all(not dual['C', k] for k in range(8)), 'no initial private influence')
    return [cuts[k] for k in range(8)], [dual['L', i] for i in range(704)], scalar_count


def endpoint_transpose(orientation):
    out = [{i: F(1)} for i in range(704)]
    for i in range(112):
        if orientation == 'forward':
            out[i][i+112] = F(1)
        else:
            out[i+112][i] = F(-1)
    return out


def call_key(c):
    return tuple(c[k] for k in ('time', 'replica', 'stage', 'provider_id'))


def validate(data):
    template, programs = data['global'], data['program']
    need(template['live'] == 14336, 'selected live owner count')
    need((data['word']['h'], data['word']['v'], data['word']['R']) == (9, 112, 480),
         'selected 480-helper provider')
    calls = {call_key(c): c for c in template['calls']}
    need(len(calls) == len(template['calls']) == 144, 'unique calls')
    scheduled = []
    for event in template['execution_schedule']:
        kind = event['kind']
        if kind == 'local_cover_sweep':
            c = calls[call_key(event)]
            need(c['orientation'] in ('forward', 'backward'), 'orientation')
            need(sha(canonical(programs[c['orientation']])) == c['local_program_sha256'],
                 'literal call program binding')
            owners = [r[0] for r in c['owners']]
            need(len(owners) == len(set(owners)) == 704 and
                 all(type(i) is int and 0 <= i < 14336 for i in owners), 'owner injection')
            start = 896*c['replica']+224*c['pair']
            need(owners[:224] == list(range(start, start+224)), 'stream owner numbering')
            scheduled.append(c)
        elif kind in ('bridge', 'terminal'):
            need(event['replicas'] == [event['replica']] and 0 <= event['replica'] < 16,
                 'single replica event')
            if kind == 'bridge':
                need(event['src'] != event['dst'] and
                     all(0 <= event[k] < 4 for k in ('src', 'dst')) and
                     event['coefficient'] in (-1, 1), 'paired bridge schema')
            else:
                need(event['pairs'] == 4, 'terminal exchange schema')
        else:
            need(kind in IDENTITY_EVENTS, 'unrecognised schedule event')
    need(len(scheduled) == 144 and len({call_key(c) for c in scheduled}) == 144,
         'complete unique chronology')
    return calls, scheduled


def reverse_response(data, local, calls, scheduled, flip_bridges=False):
    """Suffix covectors; compute B_call^T times the current suffix transpose."""
    dual = [{i: F(1)} for i in range(14336)]
    number = {call_key(c): i for i, c in enumerate(scheduled)}
    columns = [None]*1152
    for event in reversed(data['global']['execution_schedule']):
        kind = event['kind']
        if kind == 'local_cover_sweep':
            c = calls[call_key(event)]
            owners = [r[0] for r in c['owners']]
            for k, form in enumerate(local[c['orientation']]):
                out = {}
                for role, value in form.items():
                    add(out, dual[owners[role]], value)
                columns[8*number[call_key(c)]+k] = out
            for port in range(112):
                x, y = owners[port], owners[port+112]
                if c['orientation'] == 'forward':
                    add(dual[x], dual[y])
                else:
                    add(dual[y], dual[x], -1)
        elif kind == 'bridge':
            base = 896*event['replica']
            s, d = base+224*event['src'], base+224*event['dst']
            coefficient = event['coefficient']*(-1 if flip_bridges else 1)
            for port in range(112):
                add(dual[s+port], dual[d+port], coefficient)
                add(dual[d+112+port], dual[s+112+port], -coefficient)
        elif kind == 'terminal':
            base = event['replica']*896
            for pair in range(4):
                for port in range(112):
                    x = base+224*pair+port
                    dual[x], dual[x+112] = ({k: -v for k, v in dual[x+112].items()}, dual[x])
        else:
            need(kind in IDENTITY_EVENTS, 'unknown reverse schedule event')
    need(all(c is not None for c in columns), 'all error derivatives')
    need(all(row == {i: F(1)} for i, row in enumerate(dual)),
         'complete no-error endpoint transpose identity')
    return columns


def transpose(columns, n=14336):
    rows = [{} for _ in range(n)]
    for k, column in enumerate(columns):
        for i, value in column.items():
            rows[i][k] = value
    return rows


def eliminate_columns(columns):
    """Exact dependencies among columns, retaining their actual error vectors."""
    pivots, relations = {}, []
    chosen = []
    for index, original in enumerate(columns):
        row, combination = dict(original), {index: F(1)}
        while row:
            lead = min(row)
            if lead not in pivots:
                scale = row[lead]
                pivots[lead] = ({i: v/scale for i, v in row.items()},
                                {i: v/scale for i, v in combination.items()})
                chosen.append(index)
                break
            reduced, coefficients = pivots[lead]
            scale = -row[lead]
            add(row, reduced, scale)
            add(combination, coefficients, scale)
        else:
            relations.append(combination)
    # Each relation has its own last nonzero coordinate, proving independence.
    need(len({max(r) for r in relations}) == len(relations), 'independent kernel basis')
    need(all(r[max(r)] == 1 for r in relations), 'unit leading kernel coefficients')
    for relation in relations:
        image = {}
        for j, q in relation.items():
            add(image, columns[j], q)
        need(not image, 'exact kernel relation')
    return len(pivots), relations, chosen, sorted(pivots)


def minor_determinant(columns, chosen, owners):
    """Separate field elimination on the displayed square minor, largest pivots.

    It uses no rational elimination states or kernel combinations. A nonzero
    determinant mod PRIME proves the displayed rational rank lower bound.
    """
    need(len(chosen) == len(owners) and len(set(owners)) == len(owners), 'square minor')
    allowed = set(owners)
    basis, determinant = {}, 1
    leading = []
    for j in chosen:
        row = {i: (q.numerator*pow(q.denominator, -1, PRIME)) % PRIME
               for i, q in columns[j].items() if i in allowed}
        row = {i: v for i, v in row.items() if v}
        while row:
            lead = max(row)
            if lead not in basis:
                scale = row[lead]
                determinant = determinant*scale % PRIME
                inverse = pow(scale, -1, PRIME)
                basis[lead] = {i: v*inverse % PRIME for i, v in row.items()}
                leading.append(lead)
                break
            q = row[lead]
            for i, v in basis[lead].items():
                value = (row.get(i, 0)-q*v) % PRIME
                if value: row[i] = value
                else: row.pop(i, None)
        else:
            return 0
    need(set(leading) == allowed, 'minor output pivots')
    # Rows are the chosen error columns; account for the output-column ordering.
    order = {owner: i for i, owner in enumerate(owners)}
    inversions = sum(order[a] > order[b] for i, a in enumerate(leading) for b in leading[i+1:])
    return (-determinant if inversions % 2 else determinant) % PRIME


def image(columns, values):
    out = {}
    for j, q in values.items():
        add(out, columns[j], q)
    return out


def literal(data, calls, scheduled, values):
    """Fresh numeric forward replay, without local endpoint/adjoint formulas."""
    state = [F(0)]*14336
    number = {call_key(c): i for i, c in enumerate(scheduled)}
    count = 0
    for event in data['global']['execution_schedule']:
        kind = event['kind']
        if kind == 'local_cover_sweep':
            c = calls[call_key(event)]
            owners = [r[0] for r in c['owners']]
            local = {('L', i): state[owner] for i, owner in enumerate(owners)}
            # Arbitrary private differences are killed by the required CLEAR.
            local.update({('C', i): F(17+i, 3) for i in range(8)})
            for instruction in data['program'][c['orientation']]:
                tag = instruction[0]
                if tag == 'scalar':
                    count += 1
                    op = instruction[1]
                    name, dest = op[0], tuple(op[1])
                    if name == 'add': local[dest] += F(op[3], op[4])*local[tuple(op[2])]
                    elif name == 'scale': local[dest] *= F(op[2], op[3])
                    elif name == 'copy': local[dest] = local[tuple(op[2])]
                    elif name == 'clear': local[dest] = F(0)
                    else: raise ValueError('unknown literal op')
                elif tag == 'center':
                    local['C', instruction[1]] += values.get(8*number[call_key(c)]+instruction[1], F(0))
                else:
                    need(tag in {'phase', 'climb', 'adapter', 'residual_adapter'},
                         'unknown literal projection')
            need(all(local['C', i] == 0 for i in range(8)), 'literal private exit')
            for i, owner in enumerate(owners): state[owner] = local['L', i]
        elif kind == 'bridge':
            base = 896*event['replica']
            s, d = base+224*event['src'], base+224*event['dst']
            for i in range(112):
                state[d+i] += event['coefficient']*state[s+i]
                state[s+112+i] -= event['coefficient']*state[d+112+i]
        elif kind == 'terminal':
            for pair in range(4):
                for i in range(112):
                    x = 896*event['replica']+224*pair+i
                    state[x], state[x+112] = state[x+112], -state[x]
        else:
            need(kind in IDENTITY_EVENTS, 'unknown literal schedule event')
    return {i: v for i, v in enumerate(state) if v}, count


def run():
    data, reference = load()
    calls, scheduled = validate(data)
    local, counts, local_digests = {}, {}, {}
    for orientation in ('forward', 'backward'):
        cuts, endpoint, count = local_adjoint(data['program'][orientation])
        need(endpoint == endpoint_transpose(orientation), 'local transpose endpoint')
        local[orientation], counts[orientation] = cuts, count
        local_digests[orientation] = digest(transpose(cuts, 704))
        need(local_digests[orientation] == reference['local_error_response_sha256'][orientation],
             'independent local error coefficient comparison')
    columns = reverse_response(data, local, calls, scheduled)
    response_digest = digest(transpose(columns))
    need(response_digest == reference['response_sha256'], 'independent full response coefficient comparison')
    full_rank, relations, full_chosen, full_owners = eliminate_columns(columns)
    need(full_rank == 1152 and not relations, 'full response injectivity corroboration')
    full_determinant = minor_determinant(columns, full_chosen, full_owners)
    need(full_determinant, 'independent full response minor')
    readouts = {}
    for name, keep_x in [('X', True), ('Y', False)]:
        restricted = [{i: q for i, q in col.items() if ((i % 224) < 112) == keep_x}
                      for col in columns]
        rank, kernel, selected_columns, pivot_owners = eliminate_columns(restricted)
        determinant = minor_determinant(restricted, selected_columns, pivot_owners)
        need(determinant, 'independent '+name+' readout rank minor')
        nontrivial = [r for r in kernel if len(r) > 1]
        witness = min(nontrivial or kernel, key=lambda r: (len(r), max(r))) if kernel else None
        record = dict(rank=rank, nullity=1152-rank, kernel_basis_sha256=digest(kernel),
                      zero_columns=[j for j, col in enumerate(restricted) if not col],
                      noncoordinate_kernel_basis=[{str(j): str(q) for j, q in sorted(r.items())}
                                                  for r in nontrivial],
                      dependence_among_nonzero_columns=sum(bool(c) for c in restricted)-rank,
                      kernel_support_histogram=dict(sorted(Counter(len(r) for r in kernel).items())),
                      minor_determinant_mod_2147483647=determinant,
                      selected_error_columns=selected_columns, pivot_output_owners=pivot_owners)
        if witness:
            expected = image(columns, witness)
            need(expected and not image(restricted, witness), 'nonzero hidden endpoint witness')
            actual, count = literal(data, calls, scheduled, witness)
            need(actual == expected, 'complete literal hidden-error witness')
            record.update(witness={str(i): str(v) for i, v in sorted(witness.items())},
                          witness_sites=[dict(error=j, time=scheduled[j//8]['time'],
                                              replica=scheduled[j//8]['replica'],
                                              stage=scheduled[j//8]['stage'],
                                              orientation=scheduled[j//8]['orientation'],
                                              centre=j % 8, coefficient=str(q))
                                         for j, q in sorted(witness.items())],
                          witness_final={str(i): str(v) for i, v in sorted(actual.items())},
                          literal_scalar_instructions=count)
        readouts[name] = record
    wrong = reverse_response(data, local, calls, scheduled, flip_bridges=True)
    need(digest(transpose(wrong)) != response_digest, 'bridge sign coefficient control')
    duplicate = [dict(c) for c in columns]
    duplicate[1] = dict(duplicate[0])
    duplicate_rank = eliminate_columns(duplicate)[0]
    need(duplicate_rank == 1151, 'duplicate site column control')
    return dict(status='PASS_SELECTED_CENTRE_STREAM_READOUTS',
                projection='Frames, idle and address operations are identity; all scalar calls, bridges, continuations and signed terminal exchanges execute.',
                error_sites=1152, full_rank=full_rank, response_sha256=response_digest,
                full_minor_determinant_mod_2147483647=full_determinant,
                common_observable_row_space_dimension=sum(r['rank'] for r in readouts.values())-full_rank,
                local_response_sha256=local_digests, local_scalar_instructions=counts,
                schedule_counts=dict(sorted(Counter(e['kind'] for e in data['global']['execution_schedule']).items())),
                readouts=readouts, controls=['flipped_bridge_coefficients_change_response',
                                            'duplicate_error_column_has_rank_1151'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.out and args.out.exists():
        raise FileExistsError(args.out)
    result = run()
    if args.out:
        with args.out.open('x', encoding='utf-8', newline='\n') as output:
            output.write(json.dumps(result, sort_keys=True, indent=2)+'\n')
    else:
        saved = json.loads((HERE/'RESULT.json').read_text(encoding='utf-8'))
        need(canonical(saved) == canonical(result), 'typed result receipt mismatch')
    print(result['status'], 'X_rank='+str(result['readouts']['X']['rank']),
          'Y_rank='+str(result['readouts']['Y']['rank']), 'full_rank=1152')


if __name__ == '__main__':
    main()
