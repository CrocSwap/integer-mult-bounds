"""Emit and check STRUCTURAL conditions of a known-invalid idle-axis overlay.

The output protocol follows Gonzalo-Mier PR1252; the general reassignment
domain follows Jeremy Kothe PR1324. The compatibility optimum is proved here.
"""
import argparse
import copy
import gzip
import hashlib
from pathlib import Path
import shutil
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import core as C

NAMES = ('GLOBAL-TEMPLATE.json.gz', 'IDLE-REMAINDER-FRAMES.json.gz', 'HOSTED.json', 'ACTUAL-SIGMAS.json.gz')


def emit(baseline, output, frames, profile, phases_path, owners_path):
    C.need(not output.exists(), 'overlay output already exists')
    output.mkdir(parents=True)
    old = C.read(baseline/'IDLE-REMAINDER-FRAMES.json.gz')
    phases, owners = C.read(phases_path), C.read(owners_path)
    checked = C.check_assignment(old, frames, phases, owners)
    template = C.read(baseline/'GLOBAL-TEMPLATE.json.gz')
    rows = {C.label(r): r for r in frames}
    record = dict(status='PASS_STRUCTURAL_SELECTED1094_IDLE_ASSIGNMENT',
                  source_template_sha256=C.sha(baseline/NAMES[0]),
                  source_frames_sha256=C.sha(baseline/NAMES[1]),
                  source_phases_sha256=C.sha(phases_path), source_owner_map_sha256=C.sha(owners_path),
                  profile={str(r): n for r, n in profile.items()}, assignment_sha256=C.digest(frames),
                  checks=checked)
    C.write(output/'IDLE-PAIR-OVERLAY.json', record)  # Legacy on-disk protocol name.
    template['version'] += '+simultaneous-idle-assignment-v1'
    template['idle_axis_overlay'] = dict(schema='replica-local-idle-axes/1', path='IDLE-PAIR-OVERLAY.json',
        frame_path=NAMES[1], source_template_sha256=record['source_template_sha256'],
        source_frames_sha256=record['source_frames_sha256'])
    for r in template['idle_children']:
        r['rank'] = rows[C.label(r)]['rank']
    for name, obj in ((NAMES[0], template), (NAMES[1], frames)):
        (output/name).write_bytes(gzip.compress(C.canonical(obj), mtime=0))
    shutil.copyfile(baseline/NAMES[3], output/NAMES[3])
    summary = C.read(baseline/NAMES[2])
    summary.update(status='UNADMITTED_SELECTED1094_IDLE_ASSIGNMENT',
                   template_sha256=C.digest(template), global_profile=record['profile'],
                   rank_mass=sum(r*n for r, n in profile.items()), maxchild=max(profile),
                   idle_remainder_frames_sha256=C.digest(frames),
                   idle_pair_overlay_sha256=C.sha(output/'IDLE-PAIR-OVERLAY.json'))
    C.write(output/NAMES[2], summary)
    return check(baseline, output, phases_path, owners_path)


def check(baseline, candidate, phases_path, owners_path):
    old, new = (C.read(p/NAMES[1]) for p in (baseline, candidate))
    phases, owners = C.read(phases_path), C.read(owners_path)
    result = C.check_assignment(old, new, phases, owners)
    record = C.read(candidate/'IDLE-PAIR-OVERLAY.json')
    C.need(record['status'] == 'PASS_STRUCTURAL_SELECTED1094_IDLE_ASSIGNMENT', 'overlay status')
    for name, path in [('source_template_sha256', baseline/NAMES[0]), ('source_frames_sha256', baseline/NAMES[1]),
                       ('source_phases_sha256', phases_path), ('source_owner_map_sha256', owners_path)]:
        C.need(record[name] == C.sha(path), 'overlay source binding: '+name)
    C.need(record['assignment_sha256'] == C.digest(new) and record['checks'] == result, 'overlay receipt changed')
    t0, t1 = (C.read(p/NAMES[0]) for p in (baseline, candidate))
    C.need(t1['version'] == t0['version']+'+simultaneous-idle-assignment-v1', 'template version')
    meta = t1.pop('idle_axis_overlay')
    C.need(meta == dict(schema='replica-local-idle-axes/1', path='IDLE-PAIR-OVERLAY.json', frame_path=NAMES[1],
                       source_template_sha256=record['source_template_sha256'], source_frames_sha256=record['source_frames_sha256']),
           'overlay template binding')
    t1['version'] = t0['version']
    a, b = t0.pop('idle_children'), t1.pop('idle_children')
    C.need(t0 == t1 and len(a) == len(b), 'non-idle template change')
    rows = {C.label(r): r for r in new}
    for x, y in zip(a, b):
        need_rank = rows[C.label(x)]['rank']
        C.need(y == dict(x, rank=need_rank), 'idle template/frame mismatch')
    h0, h1 = (C.read(p/NAMES[2]) for p in (baseline, candidate))
    profile = C.profile(old, new, {'paid_profile': h0['global_profile']})
    expected_summary = dict(h0, status='UNADMITTED_SELECTED1094_IDLE_ASSIGNMENT',
        template_sha256=C.digest(C.read(candidate/NAMES[0])), global_profile={str(r): n for r, n in profile.items()},
        rank_mass=sum(r*n for r, n in profile.items()), maxchild=max(profile),
        idle_remainder_frames_sha256=C.digest(new), idle_pair_overlay_sha256=C.sha(candidate/'IDLE-PAIR-OVERLAY.json'))
    C.need(h1 == expected_summary and h1['global_profile'] == record['profile'], 'hosted summary/profile mismatch')
    C.need(C.read(baseline/NAMES[3]) == C.read(candidate/NAMES[3]), 'hosted sigma changed')
    return dict(status='PASS_STRUCTURAL_SELECTED1094_IDLE_OVERLAY', **result,
                profile=h1['global_profile'], frame_semantic_sha256=C.digest(new))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true', required=True)
    for key in ('baseline', 'candidate', 'phases', 'owners'):
        ap.add_argument('--'+key, type=Path, required=True)
    args = ap.parse_args()
    C.sources()
    result = check(args.baseline, args.candidate, args.phases, args.owners)
    print(result['status'])
