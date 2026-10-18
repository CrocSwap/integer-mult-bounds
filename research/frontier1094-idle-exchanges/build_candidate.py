#!/usr/bin/env python3
"""Build and price pairwise idle 48+48 -> 45+51 exchanges on #1094."""
import argparse, gzip, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
from math_support import read, dot, rank, price, load_engine

OWNER_MAP = ROOT / 'research/complex-t16-rare-pattern-exchanges/OWNERS.json.gz'
BASELINE_ASSEMBLY = ROOT / 'research/community-frontier1094-audit/ASSEMBLY.json'
OUT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


def portable_gzip(raw):
    data = bytearray(gzip.compress(raw, mtime=0)); data[9] = 255
    return bytes(data)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay-root',type=Path,required=True,
        help='Extracted candidate/strict/global directory from selected-replay.tar.gz')
    parser.add_argument('--baseline-hosted-root',type=Path,
        help='Freshly emitted/audited baseline hosted directory; defaults to replay-root/hosted')
    args=parser.parse_args()
    replay=args.replay_root.resolve()
    base, audit = replay / 'base', replay / 'audit'
    hosted=(args.baseline_hosted_root or replay/'hosted').resolve()
    frame_path = hosted / 'IDLE-REMAINDER-FRAMES.json.gz'
    template_path = hosted / 'GLOBAL-TEMPLATE.json.gz'
    phases_path = base / 'work/complex-nine-native/DATA-PHASES.json'
    frames, template = read(frame_path), read(template_path)
    phases = read(phases_path)
    owners = read(OWNER_MAP)
    audit_owner = read(audit / 'OWNERS-AND-PROFILE.json')
    baseline = json.loads(BASELINE_ASSEMBLY.read_text())
    recipes = {x['port']: x for x in phases['recipes']}
    owner_slots = {(x['owner_replica'], x['port'], x['child']) for x in owners}
    grouped = defaultdict(list)
    for row in frames:
        if (row['rank'] == 48 and row['hosted'] == 0 and row['pending_offset'] == 0
                and (row['replica'], row['port'], row['child']) not in owner_slots):
            grouped[row['replica'], row['port']].append(row)

    selected = []
    for (replica, port), rows in sorted(grouped.items()):
        recipe = recipes[port]
        ys = [int(s[k]) for s in recipe['stage_alignment']
              for k in ('entry_Y', 'exit_Y')] + [int(recipe['terminal_Y_translation'])]
        xs = [int(s[k]) for s in recipe['stage_alignment']
              for k in ('entry_X', 'exit_X')]
        used = set()
        for i, left in enumerate(rows):
            if i in used:
                continue
            left_axes = list(map(int, left['orthogonal_axes']))
            for j in range(i + 1, len(rows)):
                if j in used:
                    continue
                right = rows[j]
                right_axes = list(map(int, right['orthogonal_axes']))
                translations = [int(recipe['idle_children'][c]['translation_after'])
                                for c in (left['child'], right['child'])]
                movable = [v for v in left_axes if all(
                    dot(v, x) == 0
                    for x in right_axes + ys + xs + translations)]
                if len(movable) < 3:
                    continue
                moved = movable[:3]
                new_left, new_right = [v for v in left_axes if v not in moved], right_axes + moved
                if rank(new_left) != 45 or rank(new_right) != 51:
                    continue
                selected.append(dict(replica=replica, port=port,
                    left_child=left['child'], right_child=right['child'],
                    left_family=left['family'], right_family=right['family'],
                    old_axes_left=left_axes, old_axes_right=right_axes,
                    moved_axes=moved, new_axes_left=new_left, new_axes_right=new_right,
                    translation_after=translations,
                    stage_X_commutes=True, stage_Y_commutes=True,
                    owner_slots_empty=True, pair_Z4_polynomial_unchanged=True))
                used.update((i, j)); break

    assert len(selected) == 1825, len(selected)
    edits = {(x['replica'], x['port'], x['left_child']): (45, x['new_axes_left']) for x in selected}
    edits.update({(x['replica'], x['port'], x['right_child']): (51, x['new_axes_right']) for x in selected})
    new_frames = []
    for row in frames:
        out = dict(row)
        new = edits.get((row['replica'], row['port'], row['child']))
        if new:
            out['rank'], out['orthogonal_axes'] = new
        new_frames.append(out)

    profile = Counter({int(k): v for k, v in audit_owner['paid_profile'].items()})
    profile[48] -= 2 * len(selected); profile[45] += len(selected); profile[51] += len(selected)
    profile = +profile
    assert sum(r*n for r,n in profile.items()) == audit_owner['rank_mass']
    assert 73**2 > 2*51**2
    assert len(edits) == 3650

    current = baseline
    native = price(profile, False, current, load_engine('moment'),
                   load_engine('base_two_moment'), load_engine('outer'))
    conservative = price(profile, True, current, load_engine('moment'),
                         load_engine('base_two_moment'), load_engine('outer'))
    assert native['kappa_decimal'] > baseline['kappa_decimal']
    overlay = dict(status='PASS_EMITTED_1825_IDLE_48_PAIR_EXCHANGES',
        source_template_sha256=sha(template_path), source_frames_sha256=sha(frame_path),
        source_phases_sha256=sha(phases_path), source_owner_map_sha256=sha(OWNER_MAP),
        source_audit_sha256=sha(audit / 'OWNERS-AND-PROFILE.json'), pairs=selected,
        changed_children=3650, profile={str(k): v for k,v in sorted(profile.items())},
        scope='Replica-local residual pair repartitions; preserves each pair axis union. See OVERLAY-AUDIT.json and replay/ for the independent controller, invoice and assembly receipts.')
    overlay_path = OUT / 'IDLE-PAIR-OVERLAY.json'
    overlay_path.write_text(json.dumps(overlay, indent=2)+'\n')
    template['version'] += '+idle-48-pair-exchanges-v1'
    template['idle_axis_overlay'] = dict(schema='replica-local-idle-axes/1',
        path='IDLE-PAIR-OVERLAY.json', frame_path='IDLE-REMAINDER-FRAMES.json.gz',
        pairs=len(selected), changed_children=3650,
        source_template_sha256=sha(template_path), source_frames_sha256=sha(frame_path))
    for child in template['idle_children']:
        edit = edits.get((child['replica'], child['port'], child['child']))
        if edit:
            child['rank'] = edit[0]
    template_raw, frames_raw = canonical(template), canonical(new_frames)
    (OUT/'GLOBAL-TEMPLATE.json.gz').write_bytes(portable_gzip(template_raw))
    (OUT/'IDLE-REMAINDER-FRAMES.json.gz').write_bytes(portable_gzip(frames_raw))
    if (hosted/'ACTUAL-SIGMAS.json.gz').is_file():
        (OUT/'ACTUAL-SIGMAS.json.gz').write_bytes((hosted/'ACTUAL-SIGMAS.json.gz').read_bytes())
    hosted_data = read(hosted/'HOSTED.json')
    hosted_data.update(status='CANDIDATE_1825_IDLE_PAIR_EXCHANGES',
        template_sha256=hashlib.sha256(template_raw).hexdigest(),
        global_profile=overlay['profile'], rank_mass=sum(int(k)*v for k,v in overlay['profile'].items()),
        maxchild=51, idle_remainder_frames_sha256=hashlib.sha256(frames_raw).hexdigest(),
        idle_pair_overlay_sha256=sha(overlay_path))
    (OUT/'HOSTED.json').write_text(json.dumps(hosted_data,indent=2)+'\n')
    result = dict(status='PASS_FRONTIER1094_IDLE_PAIR_PRICE_CANDIDATE',
        baseline_kappa=baseline['kappa_decimal'], native=native, conservative=conservative,
        selected_pairs=len(selected), changed_children=3650, profile=overlay['profile'],
        profile_delta={'45': len(selected), '48': -2*len(selected), '51': len(selected)},
        source_sha256=dict(template=sha(template_path), frames=sha(frame_path), phases=sha(phases_path),
                           owners=sha(OWNER_MAP), baseline_assembly=sha(BASELINE_ASSEMBLY)),
        scope='Exact phase/profile/price lead; see replay/ADMISSION-RECEIPT.json for the fresh controller, invoice and strict assembly admission.')
    (OUT/'CANDIDATE.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'], 'pairs='+str(len(selected)), 'kappa='+native['kappa_decimal'])


if __name__ == '__main__':
    main()
