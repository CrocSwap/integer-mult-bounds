#!/usr/bin/env python3
"""Source-bound whole-call hosting projection for PR1817's unmerged retiming.

Prepared by @ToikY with substantial OpenAI Codex assistance. Apache-2.0.
The unchanged predecessor batch generator is credited in README.md.
"""
import argparse
from collections import Counter, defaultdict, deque
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
PREFIX = 'candidate/strict/global/'
BATCH_SHA = 'c9f0cbe4337e9c443ac2a10512111f60ab8d0459d2aae9de5176305d3a3bddc5'
MEMBERS = [
    PREFIX + 'PLAN.json',
    PREFIX + 'hosted/GLOBAL-TEMPLATE.json.gz',
    PREFIX + 'hosted/HOSTED.json',
    PREFIX + 'hosted/ACTUAL-SIGMAS.json.gz',
    PREFIX + 'hosted/IDLE-REMAINDER-FRAMES.json.gz',
    PREFIX + 'base/split-centres/GLOBAL-TEMPLATE.json.gz',
    PREFIX + 'base/work/complex-nine-native/DATA-PHASES.json',
    PREFIX + 'base/providers/gauge44/CANONICAL-WORD.json.gz',
    PREFIX + 'base/providers/gauge44/LOCAL-PROGRAMS.json.gz',
    PREFIX + 'base/providers/gauge44/LOCAL-CHECKS.json',
]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def input_pins():
    inventory = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    result = {}
    for row in inventory['files']:
        if row['usage'] != 'input':
            continue
        path = (ROOT / row['path']).resolve()
        need(path.is_relative_to(ROOT) and path.is_file() and not path.is_symlink(), 'input path')
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        need(sha == row['sha256'], 'source drift: ' + row['path'])
        result[row['path']] = sha
    need(ARCHIVE in result, 'undeclared selected archive')
    need(hashlib.sha256((HERE / 'predecessor/batch.py').read_bytes()).hexdigest() == BATCH_SHA,
         'vendored PR1817 generator drift')
    return result


def load_members():
    members, hashes = {}, {}
    with tarfile.open(ROOT / ARCHIVE, 'r:gz') as archive:
        for name in MEMBERS:
            stream = archive.extractfile(name)
            need(stream is not None, 'missing archive member: ' + name)
            raw = stream.read()
            payload = gzip.decompress(raw) if name.endswith('.gz') else raw
            hashes[name] = {'source_sha256': hashlib.sha256(raw).hexdigest(),
                            'payload_sha256': hashlib.sha256(payload).hexdigest()}
            members[name] = json.loads(payload)
    return members, hashes


def touched(event):
    tag = event[0]
    if tag == 'climb':
        return {('L', event[2])}
    if tag in ('adapter', 'residual_adapter'):
        return {('L', event[2])}
    if tag == 'center':
        return {('C', event[1])}
    if tag == 'scalar':
        op = event[1]
        need(op[0] in ('copy', 'add', 'clear', 'scale'), 'unknown scalar')
        roles = {tuple(op[1])}
        if op[0] in ('copy', 'add'):
            roles.add(tuple(op[2]))
        return roles
    raise ValueError('unknown local event: ' + tag)


def phases(events):
    blocks = []
    for event in events:
        if event[0] == 'phase':
            blocks.append((event[1], []))
        else:
            need(bool(blocks), 'event before phase')
            blocks[-1][1].append(event)
    need(len({name for name, _ in blocks}) == len(blocks), 'duplicate phase')
    return blocks


def is_rank_one(event):
    return event[0] == 'climb' and event[5] == 1


def occurrence_projection(original, candidate):
    """Match identical occurrences, then preserve every shared-role dependency."""
    queues = defaultdict(deque)
    for index, event in enumerate(original):
        queues[encoded(event)].append(index)
    mapped = []
    for event in candidate:
        queue = queues[encoded(event)]
        need(bool(queue), 'event inventory changed')
        mapped.append(queue.popleft())
    need(not any(queues.values()), 'event omitted')
    old, new = defaultdict(list), defaultdict(list)
    for index, event in enumerate(original):
        for role in touched(event):
            old[role].append(index)
    for index in mapped:
        for role in touched(original[index]):
            new[role].append(index)
    need(dict(old) == dict(new), 'shared-role dependency order changed')
    return mapped, old


def audit_local(original, candidate, word):
    old_blocks, new_blocks = phases(original), phases(candidate)
    need([n for n, _ in old_blocks] == [n for n, _ in new_blocks], 'phase boundary changed')
    old_frames, new_frames = list(word['start']), list(word['start'])
    rows, moved = [], 0
    for (name, old), (_, new) in zip(old_blocks, new_blocks):
        need([e for e in old if not is_rank_one(e)] == [e for e in new if not is_rank_one(e)],
             'non-rank-one skeleton changed')
        mapping, traces = occurrence_projection(old, new)
        moved += sum(i != j for i, j in enumerate(mapping))
        for body, frames in ((old, old_frames), (new, new_frames)):
            for event in body:
                if event[0] == 'climb':
                    _, part, role, before, after, rank = event
                    need(part == name and frames[role] == before, 'climb frame or phase')
                    need(rank == len(word['frames'][after]) - len(word['frames'][before]) > 0,
                         'climb rank changed')
                    frames[role] = after
        need(old_frames == new_frames, 'phase-cut frames changed')
        rows.append({'phase': name, 'events': len(old), 'touched_roles': len(traces),
                     'role_trace_sha256': digest([[list(r), seq] for r, seq in sorted(traces.items())]),
                     'phase_exit_frames_sha256': digest(old_frames)})
    need(old_frames == new_frames == word['final'], 'whole-call endpoint frames')
    return {'events': len(original), 'phases': rows, 'permuted_positions': moved,
            'original_program_sha256': digest(original), 'retimed_program_sha256': digest(candidate),
            'same_all_role_occurrence_traces': True,
            'whole_call_entry_sha256': digest(word['start']),
            'whole_call_exit_sha256': digest(word['final'])}


def local_controls(programs, retimed, word):
    def rejected(label, bad):
        try:
            audit_local(programs['forward'], bad, word)
        except ValueError as error:
            return {'control': label, 'rejected_by': str(error)}
        raise ValueError('control accepted: ' + label)
    original = retimed['forward']
    bad = copy.deepcopy(original)
    for index in range(1, len(bad)):
        if is_rank_one(bad[index]) and bad[index-1][0] == 'scalar' and (
                'L', bad[index][2]) in touched(bad[index-1]):
            bad[index-1], bad[index] = bad[index], bad[index-1]
            break
    else:
        raise ValueError('no shared-role control site')
    controls = [rejected('cross_own_scalar', bad)]
    bad = copy.deepcopy(original)
    marker = bad.index(['phase', 'centers'])
    index = max(i for i in range(marker) if is_rank_one(bad[i]))
    event = bad.pop(index)
    bad.insert(bad.index(['phase', 'centers'])+1, event)
    controls.append(rejected('cross_phase_boundary', bad))
    bad = copy.deepcopy(original)
    bad.pop(next(i for i, event in enumerate(bad) if is_rank_one(event)))
    controls.append(rejected('omit_climb', bad))
    bad = copy.deepcopy(original)
    index = next(i for i, event in enumerate(bad) if event[0] == 'adapter')
    bad[index][0] = 'unrecognized_shared_scratch_operation'
    controls.append(rejected('unknown_operator', bad))
    return controls


def compute():
    pins = input_pins()
    members, hashes = load_members()
    word = members[PREFIX + 'base/providers/gauge44/CANONICAL-WORD.json.gz']
    programs = members[PREFIX + 'base/providers/gauge44/LOCAL-PROGRAMS.json.gz']
    checks = members[PREFIX + 'base/providers/gauge44/LOCAL-CHECKS.json']
    need((word['v'], word['h'], word['R'], len(word['start']), len(word['final'])) ==
         (112, 9, 480, 704, 704), 'selected geometry')
    spec = importlib.util.spec_from_file_location('credited_batch', HERE / 'predecessor/batch.py')
    batch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(batch)
    retimed, local, batches = {}, {}, {}
    for orientation in ('forward', 'backward'):
        events, counts = [], {}
        for name, body in phases(programs[orientation]):
            new, groups, _, _ = batch.batch_phase(body)
            for group in groups:
                need(len(group) == 16 and len({e[2] for e in group}) == 16
                     and all(is_rank_one(e) for e in group), 'distinct-register batch certificate')
            events.append(['phase', name])
            events.extend(new)
            if groups:
                counts[name] = len(groups)
        need(sum(counts.values()) == 134, 'predecessor batch count')
        retimed[orientation], batches[orientation] = events, counts
        local[orientation] = audit_local(programs[orientation], events, word)
        profile = dict(sorted(Counter(e[-1] for e in events if e[0] in ('climb', 'center')).items()))
        need(profile == {int(k): v for k, v in word['local_profile'].items()} ==
             {int(k): v for k, v in checks[orientation]['paid_profile'].items()},
             'literal original-rank paid profile')
        local[orientation]['unchanged_literal_paid_profile'] = profile
        # LOCAL-CHECKS uses the exact emitter's compact event encoding.
        need(local[orientation]['original_program_sha256'] == checks[orientation]['sha256'],
             'selected program publication binding')
    geom_spec = importlib.util.spec_from_file_location('boundary_geometry', HERE / 'boundedgeometry.py')
    geometry = importlib.util.module_from_spec(geom_spec)
    geom_spec.loader.exec_module(geometry)
    geometric = geometry.audit_geometry(members, word)
    calls = members[PREFIX + 'hosted/GLOBAL-TEMPLATE.json.gz']['calls']
    stale_calls = 0
    for call in calls:
        orientation = call['orientation']
        need(call['local_program_sha256'] == local[orientation]['original_program_sha256'],
             'selected complete-call program binding')
        stale_calls += call['local_program_sha256'] != local[orientation]['retimed_program_sha256']
    need(stale_calls == 144, 'retiming did not exercise program rebinding boundary')
    paid = Counter({int(r): n*len(calls) for r, n in
                    local['forward']['unchanged_literal_paid_profile'].items()})
    paid.update({int(r): n for r, n in geometric['idle_rank_profile'].items()})
    plan = members[PREFIX + 'PLAN.json']
    need(dict(paid) == {int(r): n for r, n in plan['profile'].items()},
         'unchanged global frame-child profile')
    geometric['global_frame_child_profile'] = dict(sorted(paid.items()))
    geometric['global_rank_mass'] = sum(r*n for r, n in paid.items())
    need(73*14336-geometric['global_rank_mass'] == plan['deficit'], 'global deficit')
    controls = local_controls(programs, retimed, word)
    controls.extend({'control': name, **row} for name, row in
                    geometry.run_geometry_controls(members, word).items())
    need(input_pins() == pins, 'sources changed during replay')
    result = {'status': 'PASS_DIAGONAL_RETIMING_HOST_BOUNDARY', 'input_sha256': pins,
            'archive_members': hashes, 'predecessor_head': 'ac3a759e874e8e526bc884fc2cb8eb114695b063',
            'predecessor_generator_sha256': BATCH_SHA, 'batches': batches,
            'local_projections': local, 'whole_call_geometry': geometric, 'controls': controls,
            'retimed_programs_requiring_new_call_bindings': stale_calls,
            'conclusion': 'The original-rank retimed streams preserve the audited whole-call hosting projection.',
            'strict_admission': 'New program hashes differ; frozen native/phase/invoice receipts cannot be reused as admission.',
            'rank16_child_constructed': False, 'new_kappa': False}
    # JSON histogram keys are strings; normalize before strict canonical comparison.
    return json.loads(json.dumps(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', type=Path)
    args = parser.parse_args()
    if args.write_result:
        need(not args.write_result.exists(), 'output already exists')
    result = compute()
    if args.write_result:
        with args.write_result.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
    else:
        expected = json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8'))
        need(encoded(result) == encoded(expected), 'receipt mismatch')
    print('PASS_DIAGONAL_RETIMING_HOST_BOUNDARY orientations=2 batches=134 calls=144 no_rank16_admission no_new_kappa')


if __name__ == '__main__':
    main()
