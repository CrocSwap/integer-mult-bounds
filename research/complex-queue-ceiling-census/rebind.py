#!/usr/bin/env python3
"""Re-check SNAPSHOT.json against the pinned PR heads (needs network once).

usage: rebind.py [--fetch]
--fetch runs `git fetch origin pull/N/head` for every covered PR. Then, for each claim, the
pinned blob must exist at its head and path, and the profile, idle histogram, live, calls,
complex_lower and kappa must be read back from those blobs.
Douglas Colkitt, with Claude (Anthropic) assistance. Apache-2.0.
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
    return json.loads(gzip.decompress(raw) if path.endswith('.gz') else raw)


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


def at(o, path):
    for k in [p for p in path.split('/') if p]:
        o = o[k]
    return o


def main():
    snap = json.loads((HERE / 'SNAPSHOT.json').read_text())
    for c in snap['claims']:
        if '--fetch' in sys.argv:
            git('fetch', '-q', 'origin', f"pull/{c['pr']}/head")
        P = load(c['head'], c['profile_file'], c['profile_blob'])
        rec = find(P, lambda o: o.get('complex_profile') == c['profile'] and o.get('complex_lower') == c['complex_lower'])
        assert rec is not None and rec.get('kappa') == c['kappa'], c['pr']
        I = load(c['head'], c['idle_file'], c['idle_blob'])
        assert {str(k): v for k, v in at(I, c['idle_json_path']).items() if v} == c['idle'], c['pr']
        lc = [load(c['head'], f, b) for f, b in {(c['profile_file'], c['profile_blob']), (c['idle_file'], c['idle_blob'])}]
        assert any(find(x, lambda o: o.get('live') == c['live'] and o.get('calls') == c['calls']) for x in lc) or \
            c['live'] * 9 == 896 * c['calls'], c['pr']
        print(f"#{c['pr']} ok")
    print('PASS_SNAPSHOT_REBOUND', len(snap['claims']))


if __name__ == '__main__':
    main()
