#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run the three independent checks of PR #2269 (borrow43 on the T74 words) and require each PASS line.

Object: CrocSwap/integer-mult-bounds PR #2269 (jeremykothe2), head
b479fc5567bc09ab9185bffe89b62594f36d74e5, package research/gmx-t74-borrow43/
(claimed conditional kappa from b = 0.0016962471390584742207696...).

  words_check.py  task A: both BORROW-WORD-43{base,extra}: GF(2) warp algebra,
                  frame climbs and paid profiles, exact replay over Q<F_43>.
  fill_check.py   task B: the 291,042-role OWNERS fill: windows, slices, idle
                  remainders, global profile, mass and physical-stock facts.
  price_check.py  task C: global profile from the A and B recounts, and the
                  exact moment-root bracket around b.

Each check runs in its own process with this interpreter as `python -I -B`.
Every check must exit 0 with its PASS line as the last stdout line, otherwise
this script prints FAIL_T74_BORROW43_INDEPENDENT_CHECK with the failures.

Inputs (the PR head blobs) come from one of:
  --git-dir PATH  a git checkout that contains the head commit (default: the
                  checkout this script lives in).  Blobs are read with
                  `git cat-file` and pinned by git blob id and sha256.
                  To obtain the commit:  git fetch https://github.com/CrocSwap/integer-mult-bounds pull/2269/head
  --blob-dir DIR  an exported copy, e.g.
                    git -C REPO archive b479fc5567bc09ab9185bffe89b62594f36d74e5 research/gmx-t74-borrow43 | tar -x -C DIR
                  DIR may be the export root or DIR/research/gmx-t74-borrow43.
                  The same pins are verified on the files.
A preflight step lists every pinned input of the three checks and fails with a
clear message if any is unavailable or does not match its pins.

Runner negative controls (fast, always run): a sub-check that exits nonzero, a
sub-check that exits 0 without its PASS line, and one altered pin in the
preflight must each be rejected.

--out first removes, then rewrites words_check.receipt.json,
fill_check.receipt.json, price_check.receipt.json and check_all.receipt.json
next to the scripts (all four are deterministic in the default git mode).

The final stdout line is
  PASS_T74_BORROW43_INDEPENDENT_CHECK words=PASS fill=PASS price=PASS runner_controls=3 commit=... mode=...
or FAIL_T74_BORROW43_INDEPENDENT_CHECK failures=<name:rc:last line;...> mode=...

Credit: PR2269 (jeremykothe2); PR2226 (Cinna Davis / 1337isnot1337, with
OpenAI Codex) anticipatory dirty borrowing; PR2260 (Dugongue); the T74 lineage
PR1319/PR1297 (Rohan Arun), PR1625 (mdumitrean), the pivot-554 kernel (PR1672
lineage); the icekylinx and Zhihao Chen (jacklightChen) checker lineage.  No package code is
imported or run by any of the checks.

Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.

Usage:  python3 -I -B check_all.py [--git-dir PATH [--fetch] | --blob-dir DIR] [--out]
"""

import sys

if sys.flags.optimize:
    sys.stdout.write('refusing to run under python -O\nFAIL_T74_BORROW43_INDEPENDENT_CHECK\n')
    sys.exit(2)

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import time

PASS_LINE = 'PASS_T74_BORROW43_INDEPENDENT_CHECK'
FAIL_LINE = 'FAIL_T74_BORROW43_INDEPENDENT_CHECK'
COMMIT = 'b479fc5567bc09ab9185bffe89b62594f36d74e5'
PKG = 'research/gmx-t74-borrow43'
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_GIT_DIR = os.path.dirname(os.path.dirname(HERE))
RECEIPT_NAME = 'check_all.receipt.json'

# name, script, PASS token (start of the last stdout line), receipt file, receipt field, receipt value
CHECKS = [
    ('words', 'words_check.py', 'PASS_T74_BORROW43_WORDS_INDEPENDENT', 'words_check.receipt.json',
     'result', 'PASS_T74_BORROW43_WORDS_INDEPENDENT'),
    ('fill', 'fill_check.py', 'PASS_INDEPENDENT_T74_BORROW43_FILL_RECOUNT', 'fill_check.receipt.json',
     'status', 'PASS_INDEPENDENT_T74_BORROW43_FILL_RECOUNT'),
    ('price', 'price_check.py', 'PASS_T74_BORROW43_PRICE_INDEPENDENT', 'price_check.receipt.json',
     'result', 'PASS_T74_BORROW43_PRICE_INDEPENDENT'),
]


def sha256_file(path):
    with open(path, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def git_blob_id(data):
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def load_module(script):
    """Load one of our own check modules (definitions only; nothing runs at import)."""
    path = os.path.join(HERE, script)
    spec = importlib.util.spec_from_file_location('t74b43_all_' + script[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def required_pins():
    """package-relative path -> (git blob id, sha256), the union over the three checks; pins must agree."""
    req = {}

    def add(rel, blob, sha, who):
        if rel in req and req[rel][:2] != (blob, sha):
            raise ValueError('inconsistent pins for %s (%s vs %s)' % (rel, req[rel][2], who))
        req.setdefault(rel, (blob, sha, who))

    words = load_module('words_check.py')
    for key in sorted(words.PINS):
        rel, blob, sha = words.PINS[key]
        add(rel, blob, sha, 'words_check')
    fill = load_module('fill_check.py')
    for rel in sorted(fill.PINS):
        blob, sha = fill.PINS[rel]
        add(rel, blob, sha, 'fill_check')
    price = load_module('price_check.py')
    for rel in sorted(price.PINS):
        blob, sha = price.PINS[rel]
        add(rel, blob, sha, 'price_check')
    for mod, name in ((words, 'words_check'), (price, 'price_check')):
        if mod.COMMIT != COMMIT:
            raise ValueError(name + ' pins a different commit')
    if fill.HEAD != COMMIT:
        raise ValueError('fill_check pins a different commit')
    return req


FETCH_URL = 'https://github.com/CrocSwap/integer-mult-bounds'


def git(git_dir, *args):
    return subprocess.run(['git', '-C', git_dir] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def preflight_git(git_dir, req):
    problems = []
    got = git(git_dir, 'rev-parse', '--git-dir')
    if got.returncode != 0:
        return ['%s is not a git checkout (%s)' % (git_dir, got.stderr.decode('utf-8', 'replace').strip())]
    got = git(git_dir, 'cat-file', '-t', COMMIT)
    if got.returncode != 0 or got.stdout.strip() != b'commit':
        return ['commit %s (PR #2269 head) is not available in %s; fetch it with `git -C %s fetch '
                'https://github.com/CrocSwap/integer-mult-bounds pull/2269/head` or pass --blob-dir with an exported '
                'copy' % (COMMIT, git_dir, git_dir)]
    got = git(git_dir, 'ls-tree', '-r', COMMIT, PKG + '/')
    if got.returncode != 0:
        return ['cannot list %s at %s in %s' % (PKG, COMMIT, git_dir)]
    tree = {}
    for line in got.stdout.decode('utf-8').splitlines():
        meta, path = line.split('\t', 1)
        tree[path] = meta.split()[2]
    for rel in sorted(req):
        blob, sha, who = req[rel]
        oid = tree.get(PKG + '/' + rel)
        if oid is None:
            problems.append('%s/%s (needed by %s) is missing at %s' % (PKG, rel, who, COMMIT))
        elif oid != blob:
            problems.append('%s/%s resolves to %s, pinned %s' % (PKG, rel, oid, blob))
    if not problems:
        blobs = sorted(set(v[0] for v in req.values()))
        got = subprocess.run(['git', '-C', git_dir, 'cat-file', '--batch-check'], input=('\n'.join(blobs) + '\n').encode(),
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in got.stdout.decode('utf-8').splitlines():
            if line.endswith(' missing'):
                problems.append('blob %s is not readable in %s' % (line.split()[0], git_dir))
    return problems


def preflight_blob_dir(root, req):
    problems = []
    for rel in sorted(req):
        blob, sha, who = req[rel]
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            problems.append('%s (needed by %s) is missing' % (path, who))
            continue
        with open(path, 'rb') as fh:
            data = fh.read()
        if git_blob_id(data) != blob or hashlib.sha256(data).hexdigest() != sha:
            problems.append('%s does not match its pins (git blob %s, sha256 %s...)' % (path, blob, sha[:16]))
    return problems


def run_check(name, script, token, mode_args, out_args, quiet=False):
    cmd = [sys.executable, '-I', '-B', os.path.join(HERE, script)] + mode_args + out_args
    t0 = time.time()
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elapsed = time.time() - t0
    out = proc.stdout.decode('utf-8', 'replace')
    err = proc.stderr.decode('utf-8', 'replace')
    lines = [x for x in out.splitlines() if x.strip()]
    last = lines[-1] if lines else ''
    ok = proc.returncode == 0 and (last == token or last.startswith(token + ' '))
    if quiet:
        return dict(ok=ok, returncode=proc.returncode, last_line=last, elapsed=elapsed)
    for x in lines:
        print('  [%s] %s' % (name, x))
    for x in err.splitlines():
        if x.strip():
            print('  [%s:stderr] %s' % (name, x))
    print('  [%s] exit %d, %.1f s, %s' % (name, proc.returncode, elapsed, 'PASS' if ok else 'FAIL'), flush=True)
    return dict(ok=ok, returncode=proc.returncode, last_line=last, elapsed=elapsed)


def controls(mode, mode_args, req, git_dir, blob_root):
    """Negative controls of this runner: each must be rejected by the check it targets."""
    results = []
    price_token = CHECKS[2][2]
    # 1. a sub-check that fails (inputs missing) must be reported as a failure (exit status / last line)
    res = run_check('control', 'price_check.py', price_token,
                    ['--blob-dir', os.path.join(HERE, 'no-such-export-dir')], [], quiet=True)
    results.append(dict(name='sub-check run on a missing export exits nonzero', target='runner.exit_and_pass_line',
                        ok=not res['ok'] and res['returncode'] != 0, detail=res['last_line'][:120]))
    # 2. exit status 0 without the PASS line (argparse --help) must not count as a PASS
    res = run_check('control', 'price_check.py', price_token, ['--help'], [], quiet=True)
    results.append(dict(name='sub-check exits 0 without its PASS line', target='runner.exit_and_pass_line',
                        ok=not res['ok'] and res['returncode'] == 0, detail=res['last_line'][:120]))
    # 3. a single altered pin must be caught by the preflight
    rel = 'outer/B.json'
    bad = dict(req)
    blob, sha, who = bad[rel]
    bad[rel] = (blob[:-1] + ('0' if blob[-1] != '0' else '1'), sha, who)
    probs = preflight_blob_dir(blob_root, bad) if mode == 'blob-dir' else preflight_git(git_dir, bad)
    results.append(dict(name='one altered git blob pin (%s)' % rel, target='runner.preflight',
                        ok=len(probs) == 1 and rel in probs[0], detail=(probs[0] if probs else 'not detected')[:160]))
    return results


def main():
    ap = argparse.ArgumentParser(description='Run words_check, fill_check and price_check for PR #2269')
    group = ap.add_mutually_exclusive_group()
    group.add_argument('--git-dir', default=None,
                       help='git checkout containing %s (default: %s)' % (COMMIT, DEFAULT_GIT_DIR))
    group.add_argument('--blob-dir', default=None, help='exported copy of %s (export root or the package dir)' % PKG)
    ap.add_argument('--out', action='store_true', help='write the receipts next to the scripts')
    ap.add_argument('--fetch', action='store_true',
                    help='git mode only: if the pinned commit is absent, fetch refs/pull/2269/head from %s first '
                         '(the commit id and every input blob are still verified against their pins)' % FETCH_URL)
    args = ap.parse_args()
    started = time.time()
    failures = []
    try:
        req = required_pins()
    except Exception as e:   # our own modules are inconsistent: never pass
        print('cannot collect the pinned inputs: %s: %s' % (type(e).__name__, e))
        print(FAIL_LINE + ' failures=pins')
        return 1
    if args.blob_dir is not None:
        root = os.path.abspath(args.blob_dir)
        nested = os.path.join(root, PKG)
        if os.path.isdir(nested):
            root = nested
        if not os.path.isdir(root):
            problems = ['--blob-dir %s is not a directory' % args.blob_dir]
        else:
            problems = preflight_blob_dir(root, req)
        mode, mode_args = 'blob-dir', ['--blob-dir', root]
    else:
        git_dir = os.path.abspath(args.git_dir or DEFAULT_GIT_DIR)
        if args.fetch:
            have = git(git_dir, 'cat-file', '-t', COMMIT)
            if have.returncode != 0 or have.stdout.strip() != b'commit':
                print('fetching refs/pull/2269/head from %s (commit %s absent)' % (FETCH_URL, COMMIT), flush=True)
                got = git(git_dir, 'fetch', '--no-tags', '--quiet', FETCH_URL, 'refs/pull/2269/head')
                if got.returncode != 0:
                    print('fetch failed: %s' % got.stderr.decode('utf-8', 'replace').strip())
        problems = preflight_git(git_dir, req)
        mode, mode_args = 'git', ['--repo', git_dir]
    print('preflight (%s): %d pinned inputs across the three checks' % (mode, len(req)))
    if problems:
        print('inputs unavailable or not matching their pins:')
        for p in problems[:20]:
            print('  ' + p)
        if len(problems) > 20:
            print('  ... %d more' % (len(problems) - 20))
        print('%s failures=inputs_unavailable(%d) mode=%s' % (FAIL_LINE, len(problems), mode))
        return 1
    print('preflight: all %d inputs present and pinned' % len(req), flush=True)
    if args.out:   # never leave a receipt of an earlier run next to a failed one
        for receipt_name in [c[3] for c in CHECKS] + [RECEIPT_NAME]:
            if os.path.exists(os.path.join(HERE, receipt_name)):
                os.remove(os.path.join(HERE, receipt_name))
    ctl = controls(mode, mode_args, req, None if mode == 'blob-dir' else git_dir,
                   root if mode == 'blob-dir' else None)
    for c in ctl:
        print('runner control: %s -> %s (target %s)' % (c['name'], 'REJECTED-OK' if c['ok'] else 'NOT REJECTED',
                                                        c['target']))
        if not c['ok']:
            failures.append('control:' + c['name'])
    results = {}
    for name, script, token, receipt_name, field, value in CHECKS:
        print('== %s (%s)' % (name, script), flush=True)
        if args.out:
            out_args = ['--out', os.path.join(HERE, receipt_name)] if name == 'words' else ['--out']
        else:
            out_args = []
        res = run_check(name, script, token, mode_args, out_args)
        if res['ok'] and args.out:
            path = os.path.join(HERE, receipt_name)
            try:
                with open(path) as fh:
                    rec = json.load(fh)
                res['receipt_sha256'] = sha256_file(path)
                if rec.get(field) != value:
                    res['ok'] = False
                    res['last_line'] += ' (receipt %s=%r)' % (field, rec.get(field))
            except (OSError, ValueError) as e:
                res['ok'] = False
                res['last_line'] += ' (receipt unreadable: %s)' % e
        results[name] = res
        if not res['ok']:
            failures.append('%s:rc=%d:%s' % (name, res['returncode'], res['last_line'][:120]))
    print('elapsed %.1f s' % (time.time() - started))
    status = PASS_LINE if not failures else FAIL_LINE
    if args.out:
        receipt = dict(
            checker='check_all.py', object=dict(pr=2269, commit=COMMIT, package=PKG + '/'), mode=mode,
            python=sys.version.split()[0], interpreter_flags='-I -B',
            pinned_inputs=dict((PKG + '/' + rel, dict(git_blob=v[0], sha256=v[1], used_by=v[2]))
                               for rel, v in sorted(req.items())),
            scripts=dict((script, sha256_file(os.path.join(HERE, script)))
                         for script in ['check_all.py'] + [c[1] for c in CHECKS]),
            checks=dict((name, dict(script=script, pass_token=token, ok=results[name]['ok'],
                                    last_line=results[name]['last_line'],
                                    receipt=receipt_name, receipt_sha256=results[name].get('receipt_sha256')))
                        for name, script, token, receipt_name, _f, _v in CHECKS),
            runner_controls=ctl,
            result=status,
            credits='PR2269 jeremykothe2; PR2226 Cinna Davis / 1337isnot1337; PR2260 Dugongue; T74 lineage PR1319/'
                    'PR1297 (Rohan Arun), PR1625 (mdumitrean), pivot-554 kernel; icekylinx and Zhihao Chen (jacklightChen) checker '
                    'lineage. Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.')
        with open(os.path.join(HERE, RECEIPT_NAME), 'w') as fh:
            json.dump(receipt, fh, indent=1, sort_keys=True)
            fh.write('\n')
        print('receipt written: %s' % os.path.join(HERE, RECEIPT_NAME))
    if failures:
        print('%s failures=%s mode=%s' % (FAIL_LINE, ';'.join(failures), mode))
        return 1
    print('%s words=PASS fill=PASS price=PASS runner_controls=%d commit=%s mode=%s' % (
        PASS_LINE, len(ctl), COMMIT[:12], mode))
    return 0


if __name__ == '__main__':
    sys.exit(main())
