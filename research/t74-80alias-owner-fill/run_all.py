#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""One-command replay of the independent checks of the 80-alias T74 owner fill (standard library only).

Runs, in order and as separate `python3 -I -B` processes:
  1. fill_check80.py  - standalone recount of OWNERS-80.json.gz (R-a..R-g incl. X2 and 73-column charts,
                        16 negative controls, PR2269 fill as positive control, PR2322 private-namespace rule
                        reproduced);
  2. price80.py       - certified native and conservative moment-root brackets (width 1e-40) of the recounted
                        profile, compared with PR2269 b, PR2322 kappa/endpoint and the R = 48 packing cap.
and prints exactly one final PASS_/FAIL_ line.

Inputs: PR2269 head b479fc55 and PR2322 head 002304ef must be in the repository (`--fetch` fetches
refs/pull/2269/head and refs/pull/2322/head from the canonical GitHub repository; a shallow clone is fetched
with --depth=1).  The PR2339 words (commit bf1742ae) are read from git when that commit is present, otherwise
from the sha256/blob-pinned copies in inputs/.

Credits: PR2339 (this author); PR2269 Jeremy Kothe; PR2322 Vlado Vojdanovski; PR2312/PR2302 jeremykothe2;
PR2226 Cinna Davis; PR1319/PR1297 T74 lineage (Rohan Arun et al.).
Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.

Usage:  python3 -I -B run_all.py [--repo PATH] [--fetch] [--remote URL] [--words-from-inputs]
                                 [--skip-positive-control] [--out] [--verbose]
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

if not __debug__:
    sys.stdout.write('FAIL_T74_80ALIAS_RUN_ALL refusing to run under python -O\n')
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DEFAULT = os.path.dirname(os.path.dirname(HERE))
REMOTE_DEFAULT = 'https://github.com/CrocSwap/integer-mult-bounds'
PASS_LINE = 'PASS_T74_80ALIAS_RUN_ALL'
FAIL_LINE = 'FAIL_T74_80ALIAS_RUN_ALL'
REQUIRED = {2269: 'b479fc5567bc09ab9185bffe89b62594f36d74e5', 2322: '002304ef01c4416a127916169ae6d94c1bee052b'}
WORDS_COMMIT = 'bf1742aee4d855efb8bbd44a8419eddb33a679e5'   # PR2339; optional (inputs/ fallback)
STEPS = (('fill_check80.py', 'PASS_T74_80ALIAS_FILL_INDEPENDENT'), ('price80.py', 'PASS_T74_80ALIAS_PRICE'))


def git(repo, *args):
    return subprocess.run(['git', '-C', repo] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def present(repo, commit):
    return git(repo, 'cat-file', '-e', commit + '^{commit}').returncode == 0


def fetch(repo, remote):
    shallow = git(repo, 'rev-parse', '--is-shallow-repository').stdout.decode().strip() == 'true'
    depth = ['--depth=1'] if shallow else []
    log = []
    missing = [pr for pr, sha in sorted(REQUIRED.items()) if not present(repo, sha)]
    if missing:
        refs = ['refs/pull/%d/head' % pr for pr in missing]
        proc = git(repo, 'fetch', '--no-tags', *depth, remote, *refs)
        log.append(dict(cmd='git fetch --no-tags %s%s %s' % (' '.join(depth) + ' ' if depth else '', remote, ' '.join(refs)),
                        returncode=proc.returncode, stderr=proc.stderr.decode('utf-8', 'replace').strip()[-400:]))
        for pr in missing:   # a moved PR head: fetch the pinned commit itself
            if not present(repo, REQUIRED[pr]):
                proc = git(repo, 'fetch', '--no-tags', *depth, remote, REQUIRED[pr])
                log.append(dict(cmd='git fetch %s %s' % (remote, REQUIRED[pr]), returncode=proc.returncode,
                                stderr=proc.stderr.decode('utf-8', 'replace').strip()[-400:]))
    return dict(shallow=shallow, missing_before=missing, log=log)


def sha256_file(path):
    with open(path, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--repo', default=REPO_DEFAULT)
    ap.add_argument('--fetch', action='store_true', help='fetch refs/pull/2269/head and refs/pull/2322/head if missing')
    ap.add_argument('--remote', default=REMOTE_DEFAULT)
    ap.add_argument('--words-from-inputs', action='store_true', help='force the inputs/ copies of the PR2339 words')
    ap.add_argument('--skip-positive-control', action='store_true', help='skip the PR2269-fill positive control')
    ap.add_argument('--out', action='store_true', help='write the child receipts and run_all.receipt.json')
    ap.add_argument('--verbose', action='store_true', help='echo the full output of each step')
    args = ap.parse_args()
    repo = os.path.abspath(args.repo)
    t0 = time.time()
    receipt = dict(runner='run_all.py', python=sys.version.split()[0], steps=[])
    try:
        if args.fetch:
            receipt['fetch'] = fetch(repo, args.remote)
        for pr, sha in sorted(REQUIRED.items()):
            if not present(repo, sha):
                raise RuntimeError('PR%d commit %s missing from %s (use --fetch)' % (pr, sha, repo))
        words_mode = 'git' if present(repo, WORDS_COMMIT) and not args.words_from_inputs else 'inputs'
        receipt['pr2339_words'] = words_mode
        common = ['--repo', repo] + (['--words-from-inputs'] if words_mode == 'inputs' else []) + \
                 (['--out'] if args.out else [])
        finals = {}
        for script, token in STEPS:
            extra = ['--skip-positive-control'] if (script == 'fill_check80.py' and args.skip_positive_control) else []
            cmd = [sys.executable, '-I', '-B', os.path.join(HERE, script)] + common + extra
            s0 = time.time()
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            out = proc.stdout.decode('utf-8', 'replace').rstrip().splitlines()
            last = out[-1] if out else ''
            if args.verbose:
                for line in out:
                    print('  [%s] %s' % (script, line))
            ok = proc.returncode == 0 and last.startswith(token + ' ')
            receipt['steps'].append(dict(script=script, sha256=sha256_file(os.path.join(HERE, script)),
                                         argv=[os.path.basename(c) if c.startswith(HERE) else ('<repo>' if c == repo else c)
                                               for c in cmd[1:]],
                                         returncode=proc.returncode, final_line=last, seconds=round(time.time() - s0, 1)))
            print('[%s] %s in %.1f s' % (script, 'ok' if ok else 'FAILED', time.time() - s0), flush=True)
            if not ok:
                for line in out[-15:]:
                    print('  ' + line)
                raise RuntimeError('%s did not end with %s' % (script, token))
            finals[script] = last
        fill = dict(kv.split('=', 1) for kv in finals['fill_check80.py'].split()[1:] if '=' in kv)
        price = dict(kv.split('=', 1) for kv in finals['price80.py'].split()[1:] if '=' in kv)
        summary = 'roles=%s physical=%s buffers=%s native=%s conservative=%s below_2269=%s below_2322=%s ' \
                  'cap_fraction=%s pr2339_words=%s' % (
                      fill['roles'], fill['physical'], fill['buffers'], price['native'], price['conservative'],
                      price['below_2269'], price['below_2322'], price['cap_fraction'], words_mode)
        receipt['result'] = PASS_LINE + ' ' + summary
    except Exception as exc:
        receipt['result'] = FAIL_LINE
        receipt['failure'] = '%s: %s' % (type(exc).__name__, exc)
        if args.out:
            with open(os.path.join(HERE, 'run_all.receipt.json'), 'w') as fh:
                fh.write(json.dumps(receipt, indent=1, sort_keys=True) + '\n')
        print('%s %s' % (FAIL_LINE, receipt['failure']))
        return 1
    receipt['seconds'] = round(time.time() - t0, 1)
    if args.out:
        with open(os.path.join(HERE, 'run_all.receipt.json'), 'w') as fh:
            fh.write(json.dumps(receipt, indent=1, sort_keys=True) + '\n')
    print(receipt['result'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
