#!/usr/bin/env python3
"""Illegal-swap negative controls for verify_idle_overlay3.check_group.  Each mutant of a real legal group must be REJECTED
with the intended reason; the unmutated group must pass.  CLI: --hosted-baseline H0 --hosted H1 --base B --out RECEIPT.json"""
import argparse, copy, json
from pathlib import Path
from verify_idle_overlay import read, dot, check_group


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--hosted-baseline', type=Path, required=True); ap.add_argument('--hosted', type=Path, required=True)
    ap.add_argument('--base', type=Path, required=True); ap.add_argument('--out', type=Path, required=True); a = ap.parse_args()
    ov = read(a.hosted / 'IDLE-PAIR-OVERLAY.json')
    f0 = {(r['replica'], r['port'], r['child']): r for r in read(a.hosted_baseline / 'IDLE-REMAINDER-FRAMES.json.gz')}
    f1 = {(r['replica'], r['port'], r['child']): r for r in read(a.hosted / 'IDLE-REMAINDER-FRAMES.json.gz')}
    rec = {r['port']: r for r in read(a.base / 'work/complex-nine-native/DATA-PHASES.json')['recipes']}
    found = {}
    reasons = {'non_commuting_stage_axis_moved': 'stage translation', 'dst_translation_anticommutes': 'child translation',
               'anticommuting_arrivals_same_child': 'orthonormal', 'receiver_keeps_anticommuting_original': 'orthonormal',
               'rank_52': 'rank above guard', 'axis_lost': 'differs from claimed', 'axis_duplicated': 'differs from claimed'}
    def attempt(name, oa, na, mv, R, kids):
        try:
            check_group(oa, na, mv, R, kids)
        except (AssertionError, ValueError) as e:
            assert reasons[name] in str(e) or name.startswith('axis_') or name == 'rank_52', (name, str(e))
            found.setdefault(name, str(e) or 'ValueError')
            return True
        raise SystemExit('ACCEPTED illegal mutant ' + name)
    for g in ov['groups']:
        rep, port = g['replica'], g['port']; kids = g['children']; R = rec[port]
        oa = [list(map(int, f0[rep, port, c]['orthogonal_axes'])) for c in kids]; na = [list(map(int, f1[rep, port, c]['orthogonal_axes'])) for c in kids]
        check_group(oa, na, g['moves'], R, kids)                                    # honest group passes
        n = len(kids)
        ys = [int(s[k]) for s in R['stage_alignment'] for k in ('entry_Y', 'exit_Y')] + [int(R['terminal_Y_translation'])]
        xs = [int(s[k]) for s in R['stage_alignment'] for k in ('entry_X', 'exit_X')]
        tr = [int(R['idle_children'][c]['translation_after']) for c in kids]
        def moved(src, dst, v):   # mutate (old -> new) by one extra move from the ORIGINAL lists
            na2 = [x[:] for x in oa]; na2[src].remove(v); na2[dst].append(v)
            return na2, [dict(axis=v, src=src, dst=dst)]
        for s in range(n):
            for d in range(n):
                if s == d: continue
                for v in oa[s]:
                    bad_stage = any(dot(v, x) for x in xs + ys)
                    if bad_stage and 'non_commuting_stage_axis_moved' not in found:
                        na2, mv = moved(s, d, v); attempt('non_commuting_stage_axis_moved', oa, na2, mv, R, kids)
                    if not bad_stage and not dot(v, tr[d]) and not dot(v, tr[s]):
                        if any(dot(v, w) for w in oa[d]) and 'receiver_keeps_anticommuting_original' not in found:
                            na2, mv = moved(s, d, v); attempt('receiver_keeps_anticommuting_original', oa, na2, mv, R, kids)
        if 'dst_translation_anticommutes' not in found and g['moves']:
            m0 = g['moves'][0]; R2 = copy.deepcopy(R)      # destination child's terminal translation made to anticommute with the moved axis
            R2['idle_children'][kids[m0['dst']]]['translation_after'] = int(m0['axis'])
            attempt('dst_translation_anticommutes', oa, na, g['moves'], R2, kids)
        if 'axis_lost' not in found and na[0]:
            na2 = [x[:] for x in na]; na2[0] = na2[0][1:]; attempt('axis_lost', oa, na2, g['moves'], R, kids)
        if 'axis_duplicated' not in found and na[0]:
            na2 = [x[:] for x in na]; na2[1] = na2[1] + [na2[0][0]]; attempt('axis_duplicated', oa, na2, g['moves'], R, kids)
        if 'rank_52' not in found and n >= 2:
            ok = [v for v in oa[1] if not any(dot(v, x) for x in xs + ys) and not dot(v, tr[0]) and not dot(v, tr[1])]
            if len(ok) >= 4:
                mv = [dict(axis=v, src=1, dst=0) for v in ok[:4]]; na2 = [x[:] for x in oa]
                for v in ok[:4]: na2[1].remove(v); na2[0].append(v)
                attempt('rank_52', oa, na2, mv, R, kids)
        if 'anticommuting_arrivals_same_child' not in found:
            for d in range(n):
                for s1 in range(n):
                    for s2 in range(s1 + 1, n):
                        if d in (s1, s2): continue
                        for u in oa[s1]:
                            if any(dot(u, x) for x in xs + ys) or dot(u, tr[d]) or dot(u, tr[s1]): continue
                            for w in oa[s2]:
                                if dot(u, w) and not any(dot(w, x) for x in xs + ys) and not dot(w, tr[d]) and not dot(w, tr[s2]):
                                    na2 = [x[:] for x in oa]; na2[s1].remove(u); na2[s2].remove(w); na2[d] += [u, w]
                                    attempt('anticommuting_arrivals_same_child', oa, na2, [dict(axis=u, src=s1, dst=d), dict(axis=w, src=s2, dst=d)], R, kids); break
                            if 'anticommuting_arrivals_same_child' in found: break
                        if 'anticommuting_arrivals_same_child' in found: break
                    if 'anticommuting_arrivals_same_child' in found: break
        if len(found) == len(reasons): break
    assert len(found) == len(reasons), ('controls not all constructed', sorted(set(reasons) - set(found)))
    r = dict(status='PASS_ILLEGAL_SWAP_CONTROLS_REJECTED', controls=found)
    a.out.write_text(json.dumps(r, indent=2) + '\n'); print(r['status'], len(found))


if __name__ == '__main__':
    main()
