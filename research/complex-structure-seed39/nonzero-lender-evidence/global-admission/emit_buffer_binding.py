#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Emit concrete private arenas and all666 local-to-global family bindings.

The emitted templates contain explicit CLEAR gates at zero allocation/free.
iter_call_events resolves every remaining local L operand to its assigned
physical family, including adapter/climb/center operands. No Z label remains.
The route descriptors retain the inherited cover charts; this is one layer
of the complete controller, not an outer-bound certificate.
"""
import argparse
from collections import Counter, defaultdict
import copy
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parent
OLD = CANDIDATE.parent / 'anticipatory-stage-evidence'
LIVE, HELPERS, INPUTS, ZEROS = 66304, 428, 652, 76
ZERO_START, PHYSICAL = 66742, 66818


def require(ok, why):
    if not ok:
        raise ValueError(why)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def raw(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def program_digest(events):
    return hashlib.sha256(raw(events)).hexdigest()


def lower_program(events, zero_labels, zero_start=ZERO_START):
    slots = {z: zero_start+i for i, z in enumerate(sorted(zero_labels))}
    require(len(slots) == ZEROS and zero_start >= ZERO_START, 'private arena overlaps inherited reserve')
    active = set()
    lowered = []
    phase = None
    clear_count = 0

    def ref(ref):
        kind, r = ref
        if kind == 'L':
            require(0 <= r < INPUTS, 'native L out of range')
            return ['L', r]
        if kind == 'C':
            require(0 <= r < 8 and not active, 'center and zero arena lifetimes overlap')
            return ['F', LIVE+r]
        require(kind == 'Z' and r in active, 'unallocated private zero reference')
        return ['F', slots[r]]

    for event in events:
        e = copy.deepcopy(event)
        tag = e[0]
        if tag == 'phase':
            phase = e[1]
        elif tag == 'zero_buffer':
            _, action, label = e
            require(phase == 'full_frame_cleanup' and label in slots, 'private zero phase or label')
            if action == 'alloc':
                require(label not in active, 'duplicate private zero allocation')
                active.add(label)
                lowered += [['private_zero', 'alloc', slots[label]], ['scalar', ['clear', ['F', slots[label]]], 1]]
            else:
                require(action == 'free' and label in active, 'private zero free without allocation')
                lowered += [['scalar', ['clear', ['F', slots[label]]], 1], ['private_zero', 'free', slots[label]]]
                active.remove(label)
            clear_count += 1
            continue
        elif tag == 'scalar':
            gate = e[1]
            gate[1] = ref(gate[1])
            if gate[0] in ('add', 'copy'):
                gate[2] = ref(gate[2])
                require(gate[1] != gate[2], 'private operand alias')
        elif tag == 'warp':
            e[1] = ref(e[1])
        elif tag in ('adapter', 'residual_adapter', 'climb'):
            require(not active, 'private zero overlaps recursive or adapter phase')
            e[2] = ref(['L', e[2]])
        elif tag == 'center':
            require(not active, 'private zero overlaps center')
            e[1] = ref(['C', e[1]])
        else:
            raise ValueError('unknown native event '+str(tag))
        lowered.append(e)
    require(not active and clear_count == 2*ZEROS, 'complete private zero lifecycle')
    return lowered, slots


def event_refs(event):
    if event[0] == 'scalar':
        gate = event[1]
        return [gate[1]] + ([gate[2]] if gate[0] in ('add', 'copy') else [])
    if event[0] in ('warp', 'center'):
        return [event[1]]
    if event[0] in ('adapter', 'residual_adapter', 'climb'):
        return [event[2]]
    return []


def resolve_event(event, families):
    e = copy.deepcopy(event)
    for ref in event_refs(e):
        kind, number = ref
        if kind == 'L':
            ref[:] = ['F', families[number]]
        else:
            require(kind == 'F' and LIVE <= number < PHYSICAL, 'nonliteral private reference')
    return e


def iter_call_events(binding, call):
    """Actual interpreter entry point: output has only physical family refs."""
    program = binding['providers'][call['provider']][call['orientation']]['events']
    families = [x[0] for x in call['owners']]
    require(len(families) == len(set(families)) == INPUTS, 'whole call family injectivity')
    for event in program:
        yield resolve_event(event, families)


def idle_basis(q):
    z = next(i for i in range(9) if not (q >> i) & 1)
    u = q ^ (1 << z)
    order = list(range(9))
    order[0], order[z] = order[z], order[0]
    return [(1 << i) ^ (u if u >> i & 1 else 0) for i in order] + [1 << i for i in range(9, 73)]


def build():
    planfile = OLD / 'parent/new/PLAN.json'
    parentfile = OLD / 'parent/GLOBAL-TEMPLATE.json.gz'
    rolesfile = CANDIDATE / 'budget/RESTRICTED-OWNERS.json.gz'
    receiptfile = CANDIDATE / 'budget/RESTRICTED-VERIFICATION.json'
    phasefile = OLD / 'owners/DATA-PHASES.json'
    require(sha(planfile) == 'bf1abd33c8ba946371cae37e021747343ef6603a31297bcc962197cc23f535e2', 'call plan source pin')
    require(sha(parentfile) == '1d31424c4e27e26a35a9932ca778e43f1f3577589275422cc642aa68b31112db', 'parent source pin')
    plan, parent, roles, owner = map(read, [planfile, parentfile, rolesfile, receiptfile])
    phases = read(phasefile)
    require(owner['owner_sha256'] == sha(rolesfile) and owner['roles'] == 666*HELPERS, 'literal owner binding')
    require(parent['exact_data_phase_recipe_sha256'] == sha(phasefile), 'exact data phase binding')
    oldcalls = {(x['stage'],x['replica']): x for x in parent['calls']}
    bycall = defaultdict(dict)
    for row in roles:
        key = row['stage'], row['replica']
        require(row['helper'] not in bycall[key], 'duplicate owner role')
        bycall[key][row['helper']] = row
    providers, pins = {}, {}
    for pid, tag in [('gauge44', 'base'), ('extra', 'extra')]:
        directory = CANDIDATE / 'native-evidence' / tag
        word, programs, replay, checks = map(read, [directory / x for x in
            ['CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz', 'INDEPENDENT-LOCAL-REPLAY.json', 'LOCAL-CHECKS.json']])
        require(word['R'] == HELPERS and len(word['zero_buffers']) == ZEROS, 'native inventory')
        require(replay['canonical_word_sha256'] == sha(directory/'CANONICAL-WORD.json.gz') and
                replay['local_programs_sha256'] == sha(directory/'LOCAL-PROGRAMS.json.gz'), 'native replay binding')
        require(word['local_profile'] == owner['local_profiles'][pid], 'native global profile binding')
        providers[pid] = {}
        for orientation, events in programs.items():
            require(program_digest(events) == checks[orientation]['sha256'], 'local event digest')
            r = replay['local'][orientation]
            require(r['all_exact_columns'] == INPUTS and r['private_work_erased'] and r['zero_buffers_returned_to_zero'] == ZEROS, 'native zero proof')
            lowered, slots = lower_program(events, word['zero_buffers'])
            providers[pid][orientation] = dict(events=lowered, slots=slots,
                    native_program_sha256=program_digest(events), lowered_program_sha256=program_digest(lowered),
                    explicit_clear_macros=2*ZEROS, explicit_clear_real_components=4*ZEROS,
                    native_private_work_erased=True, native_columns=INPUTS)
        pins[pid] = {x: sha(directory/x) for x in ['CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz', 'INDEPENDENT-LOCAL-REPLAY.json', 'LOCAL-CHECKS.json']}
    calls = []
    sigmas = hashlib.sha256()
    unique_sigmas = set()
    for selected in sorted(plan['provider_calls'], key=lambda c:c['time']):
        key = selected['stage'], selected['replica']
        old = oldcalls[key]
        owners = copy.deepcopy(old['owners'][:224])
        require(set(bycall[key]) == set(range(HELPERS)), 'missing owner helper')
        pid = selected['provider']
        ports = plan['provider_registry'][pid]['ports']
        for helper in range(HELPERS):
            z = bycall[key][helper]
            family, child, offset, width, port = (z[k] for k in ['family','child','offset','width','port'])
            B = idle_basis(ports[port])
            pending = list(map(int, phases['recipes'][port]['idle_children'][child]['orthogonal_axes']))
            occupied = [B.index(v) for v in pending[offset:offset+width]]
            spectators = [j for j in range(73) if j not in occupied][:9-width]
            sigma = [B[j] for j in occupied + spectators + [j for j in range(73) if j not in occupied and j not in spectators]]
            require(len(sigma) == len(set(sigma)) == 73, 'owner chart basis')
            sh = hashlib.sha256(json.dumps(sigma,separators=(',',':')).encode()).hexdigest()
            unique_sigmas.add(sh)
            sigmas.update(json.dumps([key[0],key[1],helper,family,sh],separators=(',',':')).encode()+b'\n')
            route = [4,child,offset,width,spectators] if width < 9 else [3,child,offset]
            owners.append([family,route])
        families = [x[0] for x in owners]
        require(len(families) == len(set(families)) == INPUTS and all(0 <= f < LIVE for f in families), 'call family namespace')
        require(selected['orientation'] == old['orientation'], 'orientation changed')
        calls.append(dict(time=selected['time'], stage=key[0], replica=key[1], provider=pid,
                          orientation=selected['orientation'], owners=owners,
                          lowered_program_sha256=providers[pid][selected['orientation']]['lowered_program_sha256']))
    require(len(calls) == 666 and [c['time'] for c in calls] == list(range(666)), 'serialized call chronology')
    require(sigmas.hexdigest() == owner['actual_sigma_stream_sha256'], 'owner chart stream differs')
    require(len(unique_sigmas) == owner['unique_residual_spectator_charts'], 'unique chart count differs')
    return dict(kind='EXPLICIT_LOCAL_PHYSICAL_FAMILY_BINDING', live=LIVE, physical=PHYSICAL,
                private_namespace=dict(centers=[LIVE,LIVE+8],reserved_tableau=[LIVE+8,LIVE+8+HELPERS],
                                       coefficient=[ZERO_START-2,ZERO_START],private_zero_buffers=[ZERO_START,PHYSICAL]),
                providers=providers, calls=calls, all_calls_serialized=True,
                source_sha256=dict(plan=sha(planfile),parent=sha(parentfile),owners=sha(rolesfile),owner_receipt=sha(receiptfile),data_phases=sha(phasefile),native=pins),
                owner_sigma_stream_sha256=sigmas.hexdigest(),unique_owner_sigmas=len(unique_sigmas),
                private_route=dict(cover_class='current local cover class d',
                    local_chart='first9 coordinates, identity spectators on remaining64',
                    frame='declared native FULL frame1 for allZscalar andZwarp accesses',
                    entry_zero='explicit clear',exit_zero='native all-column restoration then explicit clear'),
                dispatch='For each serialized call, invoke iter_call_events(binding,call). It resolves allL operands through the literal652-entry owners list; C/Z operands already name dedicated physical families. Preserve every event coefficient, frame and relative order.',
                scope='Concrete family binding and explicit private CLEAR layer for all666 native calls. Parent cover/idle/bridge controller, global frame/routing audit, finite invoice and outer bound are separate components.')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, default=HERE/'GLOBAL-BUFFER-BINDING.json.gz')
    args = ap.parse_args()
    binding = build()
    args.out.write_bytes(gzip.compress(raw(binding),mtime=0))
    print('EMITTED_666_CALL_652_STREAM_76_ZERO_PHYSICAL_BINDING', sha(args.out))


if __name__ == '__main__':
    main()
