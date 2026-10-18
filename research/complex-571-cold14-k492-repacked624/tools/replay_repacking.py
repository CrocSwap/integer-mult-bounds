"""Reproduce the recorded owner repacking from the pinned PR622 data.

This is a nomination exporter. The unchanged package verifier admits it.
Prepared by Jeremy Diviney with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    if not __debug__:
        raise RuntimeError('Run without -O: nomination checks require assertions')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base-data', type=Path, required=True)
    ap.add_argument('--moves', type=Path, default=Path(__file__).resolve().parents[1] / 'data/REPACKING.json')
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    recipe = json.loads(a.moves.read_bytes())
    praw = (a.base_data / 'PLAN.json').read_bytes()
    oraw = (a.base_data / 'OWNERS.json.gz').read_bytes()
    assert sha(praw) == recipe['source_plan_sha256']
    assert sha(oraw) == recipe['source_owners_sha256']
    plan = json.loads(praw)
    roles = json.loads(gzip.decompress(oraw))
    by_id = {(r['time'], r['helper']): r for r in roles}
    assert len(by_id) == len(roles) == 35424
    changed = set()
    for time, helper, width, before, after in recipe['moves']:
        assert (time, helper) not in changed
        changed.add((time, helper))
        r = by_id[time, helper]
        assert r['width'] == width
        assert [r['owner_replica'], r['child'], r['port']] == before
        o, ch, port = after
        assert 0 <= o < 8 and 0 <= port < 112
        cap, window = plan['windows'][f'{o},{ch}']
        assert time in window and width <= cap
        family = o * 896 + (2 * plan['pairs'][str(ch)] + plan['sides'][str(ch)]) * 112 + port
        r.update(owner_replica=o, child=ch, port=port, copy=o*112+port, family=family)
    # Moves are simultaneous. Check the complete resulting map before exporting.
    bins = defaultdict(list)
    seen = set()
    for r in roles:
        k = r['family'], r['time']
        assert k not in seen
        seen.add(k)
        bins[r['owner_replica'], r['child'], r['port']].append(r)
    idle = Counter()
    for key, (cap, window) in plan['windows'].items():
        o, ch = map(int, key.split(','))
        for port in range(112):
            off = 0
            for r in sorted(bins[o, ch, port], key=lambda r: (r['time'], r['helper'])):
                assert r['time'] in window
                r['offset'] = off
                off += r['width']
            assert off <= cap
            if off < cap:
                idle[cap-off] += 1
    paid = idle.copy()
    for c in plan['provider_calls']:
        paid.update({int(r): n for r, n in plan['provider_registry'][c['provider']]['actual_paid_profile'].items()})
    assert 73*plan['live'] - sum(r*n for r,n in paid.items()) == plan['deficit']
    assert dict(sorted(idle.items())) == {int(r): n for r,n in recipe['idle_profile'].items()}
    roles.sort(key=lambda r: (r['time'], r['helper']))
    raw = json.dumps(roles, sort_keys=True, separators=(',', ':')).encode()
    assert sha(raw) == recipe['result_owners_content_sha256']
    plan.update(profile={str(r): n for r,n in sorted(paid.items())},
                mode='recorded-coordinated-owner-swaps', solver_status='FEASIBLE_NOT_OPTIMAL', gap=None,
                source_plan_sha256=sha(praw), source_owners_sha256=sha(oraw), assignment_sha256=sha(raw))
    a.out.mkdir(parents=True, exist_ok=False)
    (a.out / 'PLAN.json').write_text(json.dumps(plan, indent=2) + '\n')
    (a.out / 'OWNERS.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    print('NOMINATION REPRODUCED; strict admission required;', len(changed), 'placements')


if __name__ == '__main__':
    main()
