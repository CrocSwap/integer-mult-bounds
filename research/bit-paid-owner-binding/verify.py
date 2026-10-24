#!/usr/bin/env python3
"""Bind actual BIT paid owners to the existing lockstep audit. Apache-2.0.

JoyboyBrian, substantial OpenAI Codex assistance. No new allocator or native
operator implementation is supplied; the existing contracts remain explicit.
"""
from collections import Counter
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import struct
import sys

HERE = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def local_word(records, state, dimensions, backward, clear_record=None):
    n, temp = state['n'], state['n']
    frame = [state['final' if backward else 'initial'][str(i)] for i in range(n)]+[-1]
    value = [1 << i for i in range(n)]+[0]
    ordered = list(enumerate(records))
    if backward:
        ordered.reverse()
    jobs, episodes, current = [], [], None
    for sequence, (record, (op, x, y, c, f, z)) in enumerate(ordered):
        if record == clear_record:
            value[temp] = 0
        if op == 0:
            old, new = (c, y) if backward else (y, c)
            require(frame[x] == old, 'native MOVE entrance')
            frame[x] = new
            if f:
                require(0 <= x < n or current is not None, 'paid owner is not live')
                jobs.append([f, x, record, 'MOVE'])
        elif op == 1:
            require(frame[x] == frame[y] == f and x != y, 'native ADD entrance')
            require(current is None or x != current['source'], 'COPY source mutated')
            require(x != temp, 'unexpected write to private copy')
            if y == temp:
                require(current is not None, 'read of unavailable private copy')
                current['last_read_sequence'] = sequence
                current['last_read_record'] = record
                current['last_read_destination'] = x
                current['last_read_value'] = value[temp]
            value[x] ^= value[y] if c & 1 else 0
        elif op == (3 if backward else 2):
            require(current is None and y == temp and value[temp] == 0, 'private COPY entrance')
            require(frame[x] == c, 'COPY source frame')
            rank = abs(dimensions[c]-dimensions[f])
            require(rank == 7, 'retained rank-seven COPY contract')
            current = {'begin_sequence': sequence, 'begin_record': record, 'source': x,
                       'private_field': temp, 'paid_job': len(jobs), 'rank': rank}
            jobs.append([rank, temp, record, 'COPY_JOB'])
            frame[temp], value[temp] = f, value[x]
        else:
            require(op == (2 if backward else 3) and current is not None
                    and y == temp and x == current['source'], 'private ERASE owner')
            require(value[temp] == value[x], 'private COPY exact cleanup')
            require(current['begin_sequence'] < current['last_read_sequence'] < sequence,
                    'private clear precedes last read')
            require(current['last_read_value'] != 0, 'vacuous early-clear control')
            current.update(end_sequence=sequence, end_record=record)
            episodes.append(current)
            frame[temp], value[temp], current = -1, 0, None
    require(current is None and value[temp] == 0 and len(episodes) == 9, 'private lifetime not closed')
    require(frame[:n] == [state['initial' if backward else 'final'][str(i)] for i in range(n)],
            'native frame endpoint')
    require(Counter(job[0] for job in jobs) == Counter({1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}),
            'local paid-owner profile')
    return jobs, episodes


def raw_unit(controller, local, state):
    p, ports = controller['pairs'], state['v']
    thick = controller['invoice']['thick_stages']
    helpers, data = state['R'], 2*p*ports
    width = data+len(thick)*helpers
    roles = []
    for slot, term in enumerate(controller['diagonal']):
        require(term & 1, 'main central projector missing')
        rank = 1+7*(term >> 1).bit_count()
        roles.extend([rank]*ports)
    roles.extend([8]*(len(thick)*helpers))
    require(len(roles) == width, 'productive role inventory')
    jobs = []
    for event_index, event in enumerate(controller['physical_events']):
        op = event[0]
        if op == 'LOCAL':
            _, stage, pair, backward = event
            require(stage in thick, 'uncredited full stage')
            for rank, owner, record, kind in local[bool(backward)]:
                if owner == state['n']:
                    field = width
                elif owner < 2*ports:
                    side, port = divmod(owner, ports)
                    field = (2*pair+(1-side if backward else side))*ports+port
                else:
                    field = data+thick.index(stage)*helpers+owner-2*ports
                jobs.append([rank, field, event_index, record, kind])
        elif op == 'QUERY_SHEAR':
            # The exact source contract issues its rank-one call on private Z.
            for port in range(ports):
                jobs.append([1, width, event_index, port, 'THIN_OWNED_JOB'])
        elif op == 'IDLE':
            _, pair, selected = event
            rank = 7*len(set(selected).intersection(thick))
            if rank:
                for side in range(2):
                    for port in range(ports):
                        jobs.append([rank, (2*pair+side)*ports+port, event_index, port, 'IDLE_JOB'])
        else:
            require(op in ('ADD','SWAP','SIGNED_SWAP'), 'unknown source event')
    require(Counter(roles) == Counter({int(k):v for k,v in controller['invoice']['targets'].items()}),
            'productive target histogram')
    require(Counter(j[0] for j in jobs) == Counter({int(k):v for k,v in controller['invoice']['paid'].items()}),
            'actual paid-owner histogram')
    require(all(0 <= j[1] <= width for j in jobs), 'paid job on nonexistent owner')
    return {'schema': 'actual-bit-paid-owners/v1',
            'job_columns': ['rank','physical_field','controller_event','local_record_or_port','kind'],
            'productive_field_ranks': roles, 'owned_private_field': width, 'paid_jobs': jobs}


def whole_job(request, target, multiplicity):
    require(request == target*multiplicity, 'incomplete arbitrary-input job substitution')


def local_product(owners, episodes, records, state, dimensions):
    old = runpy.run_path(str(HERE/'vendor/live_roles.py'))
    Compiler, Violation = old['Compiler'], old['Violation']
    roles, jobs = owners['productive_field_ranks'], owners['paid_jobs']
    first = next(i for i in range(len(roles)) if roles[i] != roles[0])
    indices = (0, first)
    ell = next(i for i, job in enumerate(jobs) if job[-1] == 'COPY_JOB')
    rank, field = jobs[ell][:2]
    require(field == owners['owned_private_field'], 'source fixture is not the private COPY query')
    bindings = [(('U', j, field), rank*roles[j]) for j in indices]
    require(len({f for f, _ in bindings}) == 2, 'positive product aliases')
    for j, (_, request) in zip(indices, bindings):
        whole_job(request, roles[j], rank)
    C = Compiler(None)  # Existing stack primitive only; no new compiler/allocator.
    trace = []
    for j, (physical, request) in zip(indices, bindings):
        parent = ('U-copy', j, 'owned')
        child = ('V-at-paid-position', ell, j)
        C.push(physical, parent, None)
        C.push(physical, child, parent)
        trace.append({'event':'enter-child', 'field':physical, 'rank':request,
                      'parent':parent, 'child':child})
    own = ('V-at-paid-position', ell, 'owned')
    C.push(own, ('V-private-center', ell), None)
    require(own not in {f for f, _ in bindings}, 'V center aliases a suspended U center')
    C.pop(own, ('V-private-center', ell))
    for j, (physical, _) in reversed(list(zip(indices, bindings))):
        C.pop(physical, ('V-at-paid-position', ell, j))
        trace.append({'event':'return-child', 'field':physical})
        C.pop(physical, ('U-copy', j, 'owned'))
    require(all(not v for v in C.stack.values()), 'source-derived local stack not restored')
    rejected = []
    A = Compiler(None)
    f0, f1 = bindings[0][0], bindings[1][0]
    A.push(f0, ('parent',0), None)
    A.push(f1, ('parent',1), None)
    try:
        A.push(f0, ('child',1), ('parent',1))
    except Violation:
        rejected.append('two_U_copy_fields_aliased')
    try:
        whole_job(rank, roles[first], rank)
    except ValueError:
        rejected.append('unscaled_partial_job_rejected')
    A.push(f0, ('child',0), ('parent',0))
    try:
        A.pop(f0, ('parent',0))
    except Violation:
        rejected.append('parent_clear_while_child_live')
    sample = episodes[False][0]
    # Mutate the actual local scalar trace immediately before its last buffer read.
    try:
        local_word(records, state, dimensions, False, clear_record=sample['last_read_record'])
    except ValueError as error:
        require(str(error) == 'private COPY exact cleanup', 'early-clear control failed for another reason')
        rejected.append('clear_before_actual_last_ADD_changes_output')
    require(len(rejected) == 4, 'semantic control accepted')
    return {'common_paid_position':ell, 'U_paid_owner':field, 'U_paid_rank':rank,
            'selected_V_roles':list(indices), 'V_target_ranks':[roles[j] for j in indices],
            'source_derived_local_stack_trace':trace, 'semantic_rejections':rejected,
            'early_clear_witness':{'local_record':sample['last_read_record'],
                                   'destination':sample['last_read_destination'],
                                   'lost_input_polynomial_hex':hex(sample['last_read_value'])},
            'v2_productive_arrays':len(roles)**2, 'v2_paid_jobs':len(jobs)**2,
            'cartesian_events_materialized':False}


def evidence():
    pins = json.loads((HERE/'SOURCES.json').read_text())
    for row in pins['retained_files']:
        require(hashlib.sha256((HERE/row['retained_path']).read_bytes()).hexdigest() == row['sha256'],
                'retained source differs')
    state = json.loads((HERE/'vendor/local-states.json').read_text())
    frames = json.loads((HERE/'vendor/frames.json').read_text())['frames']
    dimensions = {int(k):v['dim'] for k,v in frames.items()}
    records = list(struct.iter_unpack('<6i', (HERE/'vendor/local-records.bin').read_bytes()))
    local, episodes = {}, {}
    for backward in (False, True):
        local[backward], episodes[backward] = local_word(records, state, dimensions, backward)
    controller = json.loads((HERE/'vendor/BIT-CONTROLLER.json').read_text())
    owners = raw_unit(controller, local, state)
    result = {'schema':'bit-paid-owner-binding/v1', 'local_records':len(records),
              'base_productive_arrays':len(owners['productive_field_ranks']),
              'base_paid_jobs':len(owners['paid_jobs']), 'COPY_lifetimes':{str(k):v for k,v in episodes.items()},
              'raw_owner_payload_sha256':hashlib.sha256(canonical(owners)).hexdigest(),
              'product':local_product(owners, episodes, records, state, dimensions),
              'source_sha256':{str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in sorted(HERE.rglob('*')) if p.is_file()
                               and p.name not in ('RESULT.json','OWNER-JOBS.json.gz')}}
    return result, owners


def main():
    require(sys.argv[1:] in ([],['--write-artifacts']), 'unexpected argument')
    result, owners = evidence()
    encoded = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if sys.argv[1:] == ['--write-artifacts']:
        (HERE/'RESULT.json').write_text(encoded)
        (HERE/'OWNER-JOBS.json.gz').write_bytes(gzip.compress(canonical(owners), mtime=0))
    else:
        require((HERE/'RESULT.json').read_text() == encoded, 'receipt differs')
        require(json.loads(gzip.decompress((HERE/'OWNER-JOBS.json.gz').read_bytes())) == owners,
                'decompressed actual-owner payload differs')
    print('PASS_BIT_PAID_OWNER_BINDING')


if __name__ == '__main__':
    main()
