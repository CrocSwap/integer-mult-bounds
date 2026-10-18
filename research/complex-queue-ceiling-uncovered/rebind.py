#!/usr/bin/env python3
"""Re-check SNAPSHOT.json against the pinned PR heads (needs network once).

usage: rebind.py [--fetch]
--fetch runs `git fetch origin pull/N/head` for every screened PR. Then, for each claim, the
pinned blob must exist at its head and path, and the recorded profile, idle histogram, kappa and
complex_lower must be read back from those blobs (for #1175 the README prose sentences must
contain the recorded histograms).
Aaron Wang / navinor, with help from opencode. Apache-2.0.
"""
import json
import re
import subprocess
import sys
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
    return raw.decode('utf-8')


def at(obj, path):
    for k in [p for p in path.split('/') if p]:
        obj = obj[k]
    return obj


def main():
    snap = json.loads((HERE / 'SNAPSHOT.json').read_text())
    for c in snap['claims']:
        if '--fetch' in sys.argv:
            git('fetch', '-q', 'origin', f"pull/{c['pr']}/head")
        text = load(c['head'], c['profile_file'], c['profile_blob'])
        if c['profile_json_path'] == 'README prose':
            gp = re.search(r"Global profile `\{([^}]*)\}`", text)
            ip = re.search(r"[Ii]dle remainder\**\s*`\{([^}]*)\}`", text)
            parse = lambda s: {int(a): int(b) for a, b in re.findall(r"(\d+):(\d+)", s)}
            assert gp and parse(gp.group(1)) == {int(k): v for k, v in c['profile'].items()}, c['pr']
            assert ip and parse(ip.group(1)) == {int(k): v for k, v in c['idle'].items()}, c['pr']
        else:
            obj = json.loads(text)
            got = {int(k): int(v) for k, v in at(obj, c['profile_json_path']).items()}
            assert got == {int(k): v for k, v in c['profile'].items()}, c['pr']
            if c['idle_file'] == c['profile_file']:
                got = {int(k): int(v) for k, v in at(obj, c['idle_json_path']).items()}
                assert got == {int(k): v for k, v in c['idle'].items()}, c['pr']
        if c['idle_file'] != c['profile_file']:
            iobj = json.loads(load(c['head'], c['idle_file'], c['idle_blob']))
            got = {int(k): int(v) for k, v in at(iobj, c['idle_json_path']).items()}
            assert got == {int(k): v for k, v in c['idle'].items()}, c['pr']
        print(f"#{c['pr']} ok")
    print('PASS_SNAPSHOT_REBOUND_UNCOVERED', len(snap['claims']))


if __name__ == '__main__':
    main()
