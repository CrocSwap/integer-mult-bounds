#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bind the literal owner restriction to the two actual FOUR428 native words.

Prepared for Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
This bridge retains the parent controller geometry. It is not a global emit,
physical-stock invoice, supplier admission or outer-bound certificate.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent.parent
OLD = EVIDENCE.parent/'anticipatory-stage-evidence'
PARENT = OLD/'parent'
BUDGET = EVIDENCE/'budget'
PINS = {
    'parent/code/generated_identity.py': 'c8af22719c0f3097a991a3f6ccac8f090afd2faba554745733d9ea88f2c25708',
    'parent/new/PLAN.json': 'bf1abd33c8ba946371cae37e021747343ef6603a31297bcc962197cc23f535e2',
    'parent/GLOBAL-TEMPLATE.json.gz': '1d31424c4e27e26a35a9932ca778e43f1f3577589275422cc642aa68b31112db',
    'owners/DATA-PHASES.json': 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
    'vendor/pr2339/inputs/gauge44.canonical.json.gz': '65c6d17ffee2eacf27bff438f37fc549c9ed0c909cbc7a52976cc75cf2d15b91',
    'vendor/pr2339/inputs/extra.canonical.json.gz': 'd7e48dcbafa236a2e1e41f7958244211506f7c7630fe6a2d43d2bdf17b7ae015',
}
BUDGET_PINS = {
    'RESTRICTED-OWNERS.json.gz': 'cbc1b15a63288d64432d0548774b83526ae1d196b5a6594c0d8f0f4f0418d847',
    'RESTRICTED-VERIFICATION.json': 'fd08d043b055200f035fdb856579bf3c5541e3c37b48f8e86ae05624950ef819',
}
NATIVE_RECEIPT_PIN = '4027c9407082ec95a0db9b9c67e63f6e83d75349af726ca7e44e9ff33b0c0e60'


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def payload_sha(path):
    return hashlib.sha256(gzip.decompress(path.read_bytes())).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n')


def span(vectors):
    result = {0}
    for vector in vectors:
        need(type(vector) is int and 0 <= vector < 512, 'invalid nine-bit frame vector')
        result |= {value ^ vector for value in tuple(result)}
    need(len(result) == 2**len(vectors), 'dependent frame basis')
    return frozenset(result)


def recount(word, programs):
    """Finite set-subspace chronology, independent of transport's RREF code."""
    need((word['v'],word['h'],word['R']) == (112,9,428), 'candidate dimensions')
    frames = [span(f) for f in word['frames']]
    dimensions = [len(f) for f in word['frames']]
    need(frames[0] == {0} and len(frames[1]) == 512, 'zero and full frame IDs')
    need(len(word['start']) == len(word['final']) == 652, 'candidate frame-vector size')
    current = list(word['start'])
    paid = Counter()
    warp_maps = {}
    for item in word['warps']:
        columns = item['G_columns']
        need(len(columns) == 9 and len(span(columns)) == 512, 'invertible warp')
        values = []
        for x in range(512):
            y = 0
            for bit,column in enumerate(columns):
                if x & (1 << bit):
                    y ^= column
            values.append(y)
        warp_maps[item['op']] = values

    def climb(register, destination):
        need(type(register) is int and 0 <= register < 652, 'local register range')
        origin = current[register]
        need(frames[origin] <= frames[destination], 'nonnested local climb')
        delta = dimensions[destination]-dimensions[origin]
        if delta:
            paid[delta] += 1
        current[register] = destination

    def gate(event):
        if event[0] == 'warp':
            _,register,operator,origin,destination = event
            need(current[register] == origin, 'warp chronology')
            mapping = warp_maps[abs(operator)]
            source,target = (origin,destination) if operator > 0 else (destination,origin)
            need(frozenset(mapping[x] for x in frames[source]) == frames[target], 'warp frame image')
            current[register] = destination
        else:
            need(event[0] in ('add','scale'), 'unknown local scalar gate')
            for register in event[1:3] if event[0] == 'add' else event[1:2]:
                climb(register,event[-1])

    # These preceding operations are frame-zero macros, already scalar-replayed
    # by the native certificates; no unpriced nonzero-rank operation is allowed.
    for event in word['precondition']+word['compensation']:
        need(event[0] in ('add','scale','tadd'), 'unknown zero-frame gate')
        registers = event[1:2] if event[0] == 'scale' else event[1:3]
        need(event[-1] == 0 and all(current[r] == 0 for r in registers), 'nonzero precondition frame')
    for event in word['A']:
        gate(event)
    levels = {int(t): f for t,f in word['target_levels'].items()}
    need(set(levels) == {23,34,50,108}, 'exact four lifted targets')
    need(all(current[112+t] == levels.get(t,0) for t in range(112)), 'target-level chronology')
    need(all(word['frames'][f] == [30] for f in levels.values()), 'lifted target line')
    forward,backward = [],[]
    for index,(register,frame) in enumerate(zip(word['centers'],word['center_frames'])):
        need(current[register] == frame, 'center carrier frame')
        served = set()
        for event in word['cut']:
            need(event[0] == 'add' and 112 <= event[1] < 224 and event[2] in word['centers'], 'COPY cut shape')
            if event[2] == register:
                served.add(levels.get(event[1]-112,0))
        need(0 in served, 'center descent reaches zero')
        segments = []
        origin = frame
        for destination in sorted(served, key=lambda f: -dimensions[f]):
            need(frames[destination] <= frames[origin], 'nested COPY levels')
            rank = dimensions[origin]-dimensions[destination]
            if rank:
                paid[rank] += 1
                segments.append(['center',index,origin,destination,rank])
            origin = destination
        forward.extend(segments)
        backward.extend([e[:2]+[e[3],e[2],e[4]] for e in reversed(segments)])
    need([e for e in programs['forward'] if e[0] == 'center'] == forward, 'forward COPY segment binding')
    need([e for e in programs['backward'] if e[0] == 'center'] == backward, 'backward COPY segment binding')
    need(Counter(e[4] for e in forward) == {1:4,7:4,8:4}, 'twelve COPY children')
    for section in ('B','tail'):
        for event in word[section]:
            gate(event)
    for register,frame in enumerate(word['final']):
        climb(register,frame)
    profile = {str(r):n for r,n in sorted(paid.items())}
    need(profile == {str(r):n for r,n in word['local_profile'].items()}, 'independent paid-profile recount')
    for orientation,events in programs.items():
        literal = Counter(e[-1] for e in events if e[0] in ('climb','center'))
        need(literal == paid, 'literal program rank profile')
    widths = [dimensions[word['final'][r]]-dimensions[word['start'][r]] for r in range(224,652)]
    return dict(profile=profile,widths=widths,center_segments=dict(forward=forward,backward=backward),
                target_levels={str(t):word['frames'][f] for t,f in sorted(levels.items())})


def main():
    need(__debug__, 'Optimized Python unsupported by inherited checks')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=HERE)
    args = parser.parse_args()
    for name,pin in PINS.items():
        need(sha(OLD/name) == pin, 'parent/source pin')
    for name,pin in BUDGET_PINS.items():
        need(sha(BUDGET/name) == pin, 'restricted-owner evidence pin')
    need(sha(EVIDENCE/'NATIVE-RESULT.json') == NATIVE_RECEIPT_PIN, 'native receipt source pin')
    native_receipt = read(EVIDENCE/'NATIVE-RESULT.json')
    need(native_receipt['status'] == 'PASS_FINITE_NATIVE_BOTH_FOUR_ALIAS_WORDS_NO_GLOBAL_ADMISSION', 'native receipt status')
    original_plan = read(PARENT/'new/PLAN.json')
    plan = copy.deepcopy(original_plan)
    roles = read(BUDGET/'RESTRICTED-OWNERS.json.gz')
    owners_receipt = read(BUDGET/'RESTRICTED-VERIFICATION.json')
    need(owners_receipt['status'] == 'PASS_428_HELPER_LITERAL_RESTRICTION_WINDOWS_AXES_PROFILE_AND_EXACT_COST', 'owner geometry status')
    spec = importlib.util.spec_from_file_location('parent_semantic_identity', PARENT/'code/generated_identity.py')
    identity = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(identity)
    interfaces, native_pins, controls = {},{},[]
    for provider,tag in (('gauge44','base'),('extra','extra')):
        directory = args.native/tag
        files = {}
        for name in original_plan['provider_registry'][provider]['artifact_sha256']:
            pin = native_receipt['outputs_sha256'][tag+'/'+name]
            need(sha(directory/name) == pin, 'native artifact source pin')
            files[name] = pin
        native_pins[provider] = files
        word,programs,checks,replay,phase = [read(directory/name) for name in
            ('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json','INDEPENDENT-LOCAL-REPLAY.json','CLIFFORD-REVIEW.json')]
        need(replay['status'] == 'PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY', 'native scalar receipt status')
        need(phase['status'] == 'PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES', 'native phase receipt status')
        need(replay['canonical_word_sha256'] == files['CANONICAL-WORD.json.gz'] and
             replay['local_programs_sha256'] == files['LOCAL-PROGRAMS.json.gz'], 'native scalar source binding')
        need(phase['canonical_word_sha256'] == files['CANONICAL-WORD.json.gz'] and
             phase['recipe_sha256'] == files['CLIFFORD-RECIPES.json'] and
             phase['all_child_equalities_include_global_phase'] is True, 'native phase source binding')
        result = recount(word,programs)
        original = read(OLD/f'vendor/pr2339/inputs/{provider}.canonical.json.gz')
        need(word['ports'] == original['ports'] == original_plan['provider_registry'][provider]['ports'], 'ordered data ports')
        for boundary in ('start','final'):
            need([span(word['frames'][f]) for f in word[boundary][:224]] ==
                 [span(original['frames'][f]) for f in original[boundary][:224]], 'data boundary frame interface')
        need([span(word['frames'][f]) for f in word['center_frames']] ==
             [span(original['frames'][f]) for f in original['center_frames']], 'ordered center-frame interface')
        need(len(word['helper_origin']) == len(set(word['helper_origin'])) == 428, 'native helper origin inventory')
        for row in roles:
            if plan['provider_calls'][row['time']]['provider'] == provider:
                need(word['helper_origin'][row['helper']] == row['origin_helper'], 'owner/native helper origin binding')
                need(result['widths'][row['helper']] == row['width'], 'owner/native helper width binding')
        for orientation in ('forward','backward'):
            need(result['profile'] == replay['paid_profiles'][orientation] == checks[orientation]['paid_profile'], 'native rank-profile binding')
            need(replay['local'][orientation]['all_exact_columns'] == 652 and
                 replay['local'][orientation]['private_work_erased'] is True and
                 replay['local'][orientation]['zero_buffers_returned_to_zero'] == 76, 'native endpoint obligation')
        need(len(word['zero_buffers']) == 76, 'private zero buffer inventory')
        desc = plan['provider_registry'][provider]
        desc.update(actual_paid_profile=result['profile'], artifact_semantic_sha256=identity.artifact_identities(directory),
                    artifact_sha256=files,orientation_program_sha256={o:checks[o]['sha256'] for o in ('backward','forward')},
                    centers=word['centers'],ports=word['ports'],widths=result['widths'],directory='providers/'+provider)
        for call in plan['provider_calls']:
            if call['provider'] == provider:
                call['local_program_sha256'] = checks[call['orientation']]['sha256']
        interfaces[provider] = dict(target_levels=result['target_levels'],center_segments=result['center_segments'],
                                   unchanged_data_boundaries=True,unchanged_ordered_center_frames=True,
                                   helpers=428,zero_buffers=76,canonical_word_sha256=files['CANONICAL-WORD.json.gz'])
        bad = copy.deepcopy(word)
        bad['target_levels']['23'] = 0
        try: recount(bad,programs)
        except ValueError as exc: need(str(exc) == 'target-level chronology', 'wrong target mutation rejection')
        else: raise ValueError('forged target level accepted')
        controls.append(provider+': changed target level')
        bad = copy.deepcopy(programs)
        bad['forward'].remove(next(e for e in bad['forward'] if e[0] == 'center'))
        try: recount(word,bad)
        except ValueError as exc: need(str(exc) == 'forward COPY segment binding', 'wrong COPY mutation rejection')
        else: raise ValueError('missing center child accepted')
        controls.append(provider+': omitted split COPY child')
    for item in plan['per_call_widths']:
        call = plan['provider_calls'][item['time']]
        need((item['stage'],item['replica']) == (call['stage'],call['replica']), 'per-call width address')
        item['widths'] = plan['provider_registry'][call['provider']]['widths']
    profile = Counter({int(r):n for r,n in owners_receipt['idle'].items()})
    for call in plan['provider_calls']:
        profile.update({int(r):n for r,n in plan['provider_registry'][call['provider']]['actual_paid_profile'].items()})
    need(profile == {int(r):n for r,n in owners_receipt['profile'].items()}, 'owner/native global profile binding')
    plan['profile'] = {str(r):n for r,n in sorted(profile.items())}
    plan['assignment_sha256'] = sha(BUDGET/'RESTRICTED-OWNERS.json.gz')
    plan['assignment_content_sha256'] = payload_sha(BUDGET/'RESTRICTED-OWNERS.json.gz')
    plan['replica_lift']['owners_file_sha256'] = plan['assignment_sha256']
    plan['source_plan_sha256'] = sha(PARENT/'new/PLAN.json')
    plan['source_owners_sha256'] = original_plan['assignment_sha256']
    plan['status'] = 'CANDIDATE_FOUR428_LITERAL_RESTRICTION_NATIVE_BOUND'
    plan['mode'] = 'mixed-t74-four428-literal-restriction'
    plan['solver_status'] = 'No optimizer: delete nine original helpers and compact each inherited pending bin'
    plan['candidate_native_interfaces'] = interfaces
    args.out.mkdir(parents=True,exist_ok=True)
    shutil.copy2(BUDGET/'RESTRICTED-OWNERS.json.gz',args.out/'OWNERS.json.gz')
    shutil.copy2(PARENT/'GLOBAL-TEMPLATE.json.gz',args.out/'GLOBAL-TEMPLATE.json.gz')
    dispatch = [[c['stage'],c['replica'],c['provider']] for c in plan['provider_calls']]
    write(args.out/'DISPATCH.json',dispatch)
    write(args.out/'PROFILE.json',plan['profile'])
    write(args.out/'PLAN.json',plan)
    write(args.out/'CONSTRUCTION.json',dict(status='PASS_FOUR428_LITERAL_OWNER_GEOMETRY_NATIVE_PROFILE_BRIDGE',
          helpers_per_call=428,roles=len(roles),idle=owners_receipt['idle'],dispatch=dict(Counter(x[2] for x in dispatch)),
          scope='Literal restriction geometry verified separately; native interface and profiles bound here. Complete global emission, physical invoice and outer admission remain required.'))
    receipt = dict(status='PASS_FOUR428_OWNER_NATIVE_GEOMETRY_BRIDGE_NO_GLOBAL_ADMISSION',
                   base='7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261',seed=39,
                   roles=len(roles),native_pins=native_pins,interfaces=interfaces,controls=controls,
                   source_pins=PINS,budget_pins=BUDGET_PINS,native_receipt_sha256=NATIVE_RECEIPT_PIN,
                   output_pins={n:sha(args.out/n) for n in ('PLAN.json','OWNERS.json.gz','PROFILE.json','CONSTRUCTION.json','DISPATCH.json','GLOBAL-TEMPLATE.json.gz')},
                   global_template_role='Unmodified lifted source envelope for the global emitter, not the emitted FOUR428 construction.',
                   physical_scope='66818 = 66304 data + 8 centers + 428 tableau + 2 coefficient + 76 private zero buffers; complete allocation and invoice are separate obligations.',
                   scope='Exact data-boundary frames and ordered center frames preserved. Internal target line30 and twelve nested COPY segments independently recounted and bound to both native programs; all428 helper origins bound to the285048-role literal restriction. No complete global or outer admission.')
    write(args.out/'BRIDGE-CHECK.json',receipt)
    print(receipt['status'])


if __name__ == '__main__':
    main()
