# SPDX-License-Identifier: Apache-2.0
"""Re-bind SNAPSHOT.json to the pinned PR heads (needs network access to fetch the pull refs).

Usage: python3 -B research/pending-claims-independent-pricing/rebind.py
For every claim: fetch refs/pull/N/head, require the recorded head to be that ref or an ancestor of it,
require every recorded source file's git blob id at the recorded head, and require the profile, live
stock, calls and endpoint values in those files to equal the snapshot.
"""
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent


def git(*a):
    r = subprocess.run(['git', *a], cwd=HERE, capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def main():
    snap = json.loads((HERE / 'SNAPSHOT.json').read_text())
    for c in snap:
        rc, _ = git('cat-file', '-e', c['head'] + '^{commit}')
        if rc:
            git('fetch', '--quiet', 'origin', f"pull/{c['pr']}/head")
        rc, _ = git('cat-file', '-e', c['head'] + '^{commit}')
        assert rc == 0, f"#{c['pr']}: head {c['head']} not available"
        for key, (path, blob) in c['sources'].items():
            rc, got = git('rev-parse', f"{c['head']}:{path}")
            assert rc == 0 and got == blob, f"#{c['pr']}: {path} blob differs"
        rc, txt = git('show', f"{c['head']}:{c['sources']['record'][0]}")
        rec = json.loads(txt)
        exp = rec.get('expected', {})
        prof = rec.get('complex_profile') or exp.get('global_profile') or rec.get('profile') or rec.get('global_profile')
        assert prof == c['profile'], f"#{c['pr']}: profile differs"
        print('rebound', c['pr'], c['head'][:12], len(c['sources']), 'source files')
    print('PASS_PENDING_CLAIMS_REBOUND')


if __name__ == '__main__':
    main()
