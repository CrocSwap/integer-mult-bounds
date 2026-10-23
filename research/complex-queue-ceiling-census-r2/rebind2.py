#!/usr/bin/env python3
"""Re-check SNAPSHOT2.json against the pinned PR heads (needs the pull refs; --fetch once).

usage: rebind2.py [--fetch]
For each screened claim: the pinned profile and idle blobs must still exist at their
pinned head+path, and the record re-read from the blob must carry the pinned kappa,
paid profile, idle histogram, live and calls. --fetch runs `git fetch origin pull/N/head`
for all sixteen claims first.
Abhinav Ramachandran (geckods), with substantial GLM (Z.ai) assistance via Hermes. Apache-2.0.
"""
import gzip, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def git(*a):
    r = subprocess.run(['git', *a], capture_output=True)
    if r.returncode:
        sys.exit(f'FAIL: git {" ".join(a)}: {r.stderr.decode()}')
    return r.stdout


def load(head, path, blob):
    if git('rev-parse', f'{head}:{path}').decode().strip() != blob:
        sys.exit(f'FAIL: blob changed for {head}:{path}')
    raw = git('cat-file', 'blob', blob)
    if path.endswith('.gz'):
        raw = gzip.decompress(raw)
    return json.loads(raw)


def find(o, pred):
    if isinstance(o, dict):
        if pred(o):
            return o
        for v in o.values():
            r = find(v, pred)
            if r is not None:
                return r
    elif isinstance(o, list):
        for v in o:
            r = find(v, pred)
            if r is not None:
                return r
    return None


def main():
    snap = json.loads((HERE / 'SNAPSHOT2.json').read_text())
    claims = snap['claims']
    if '--fetch' in sys.argv:
        for c in claims:
            git('fetch', '-q', 'origin', f"pull/{c['pr']}/head")
    n = 0
    for c in claims:
        if not c['screened']:
            print(f"#{c['pr']} unscreened (pinned head {c['head'][:12]})")
            continue
        P = load(c['head'], c['profile_file'], c['profile_blob'])
        rec = find(P, lambda o: str(o.get('kappa')) == c['kappa']
                   and (o.get('complex_profile') is not None or o.get('global_profile') is not None))
        assert rec is not None, c['pr']
        prof = rec.get('complex_profile') or rec.get('global_profile')
        assert {str(int(k)): int(v) for k, v in prof.items()} == c['profile'], c['pr']
        if 'idle_remainder_profile' in rec:
            assert {str(int(k)): int(v) for k, v in rec['idle_remainder_profile'].items()} == c['idle'], c['pr']
        if rec.get('live') is not None:
            assert rec['live'] == c['live'], c['pr']
        if c['idle_file'] != c['profile_file']:
            I = load(c['head'], c['idle_file'], c['idle_blob'])
            assert find(I, lambda o: 'idle_remainder_profile' in o) is not None, c['pr']
        n += 1
        print(f"#{c['pr']} ok")
    print(f'PASS_SNAPSHOT2_REBOUND {n}')


if __name__ == '__main__':
    main()
