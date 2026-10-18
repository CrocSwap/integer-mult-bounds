#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Reproducer for two crash bugs in PR1345's research/bit589-transport-atlas/atlas.py (head b54a856a).

Bug 1, lines 248-250 and 282-284. The single-transport census counts improvements in
stat['improving'] and then builds out[sec] = dict(ops=..., **dict(stat), ..., improving=improving[:5]).
As soon as one improving transport exists, dict() receives 'improving' twice:
    TypeError: dict() got multiple values for keyword argument 'improving'
Fix (hunk 1 of atlas.patch): count under stat['improving_count']. On PR589's word the key never
appears, so PR1345's recorded output is unchanged.

Bug 2, lines 375 and 416. best = (d, moves) with d = (lo, hi), so `d[0] < best[0]` compares a
Fraction with a tuple at the second improving combination:
    TypeError: '<' not supported between instances of 'Fraction' and 'tuple'
Fix (hunks 2 and 3): best[0][0]. Line 416 (shared-register pairs) is reached on the R438 word;
line 375 (whole components) is not reached on these words because every component exceeds the
200000-combination budget, so it is shown at expression level.

Runs (parallel subprocesses, PR1345's atlas file in a minimal temporary tree with the pinned wlib
and engine copies):
  pristine_r438   PR1345 bytes on PR1043's R438 word        -> TypeError at line 282
  fix1_r438       hunk 1 only on the R438 word              -> TypeError at line 416
  patched_r438    atlas.patch on the R438 word              -> exit 0; finds op 2027 -> slots 154/155/425 at frame 79
  patched_pr589   atlas.patch on PR589's word               -> output equals PR1345's result.json
  pristine_pr589  (--full) PR1345 bytes on PR589's word     -> output equals PR1345's result.json
The atlas keeps its hard-coded PR589 saving c in every run here (no line-28 substitution).

Usage: python3 -I -B research/<slug>/atlas_bugs.py [--full] [--out [RECEIPT.json]] [--jobs N] [--repo ROOT]
The last line starts with PASS_ or FAIL_.
New material by Sagar Thakrar (thakrarsagar) with substantial AI assistance (Claude Code, Anthropic).
"""
import argparse
import difflib
import gzip
import importlib.util
import json
import sys
import tempfile
import time
from fractions import Fraction as Q
from pathlib import Path

TAG = 'PR1345_ATLAS_BUGS'
if not __debug__:
    print('FAIL_%s refusing to run under python -O' % TAG)
    sys.exit(2)

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('c2_transport_lib', HERE / 'lib.py')
L = importlib.util.module_from_spec(_spec)
sys.modules['c2_transport_lib'] = L
_spec.loader.exec_module(L)
require = L.require

BUG1 = "TypeError: dict() got multiple values for keyword argument 'improving'"
BUG2 = "TypeError: '<' not supported between instances of 'Fraction' and 'tuple'"


def census_assertions(r):
    """PR1345 verify.sh's census checks, transcribed."""
    A, B = r['A'], r['B']
    P = r['simultaneous_pairs']
    return (A['improving'] == [] and B['improving'] == [] and A['legal'] == 5830 and B['legal'] == 3561
            and A['same_profile'] == 5580 and B['same_profile'] == 3226 and A['strictly_worse'] == 250
            and B['strictly_worse'] == 335 and A.get('unresolved', 0) == 0 and B.get('unresolved', 0) == 0
            and [p['scored'] for p in P] == [225152, 218448]
            and all(p.get('improving', 0) == 0 and p.get('unresolved', 0) == 0 for p in P)
            and len(r['replay_spot_check']) == 8)


def expression_controls():
    """Line 375/416 condition evaluated on the values the atlas would hold at the second improvement."""
    pristine = L.atlas_source('pristine').splitlines()
    patched = L.atlas_source('patched').splitlines()
    out = {}
    for line in (375, 416):
        cond_old = pristine[line - 1].strip()
        cond_new = patched[line - 1].strip()
        require(cond_old.startswith('if best is None or d[0] < best[0]:') and cond_new.endswith('best[0][0]:'),
                'unexpected source at line %d' % line)
        expr_old, expr_new = cond_old[3:-1], cond_new[3:-1]
        env = dict(d=(Q(-2), Q(-1)), best=((Q(-1), Q(-1)), [(0, 0, 0)]))
        try:
            eval(expr_old, {}, dict(env))
        except TypeError as error:
            old = 'TypeError: ' + str(error)
        else:
            raise L.Fail('pristine line %d condition did not raise' % line)
        require(old == BUG2, 'line %d: wrong error %s' % (line, old))
        require(eval(expr_new, {}, dict(env)) is True, 'patched line %d condition' % line)
        out[str(line)] = dict(pristine=old, patched='True (d[0] = -2 < best[0][0] = -1)')
    return out


def patch_controls(source):
    text = L.atlas_patch_text()
    patched = L.apply_patch(source, text)
    diff = ''.join(difflib.unified_diff(source.splitlines(True), patched.splitlines(True),
                                        'a/' + L.ATLAS_REL, 'b/' + L.ATLAS_REL))
    require(diff == text, 'atlas.patch is not the minimal difflib diff of its own application')
    hunks = L.parse_patch(text)
    require(len(hunks) == 3 and [h[0] for h in hunks] == [247, 372, 413], 'hunk layout')
    changed = sum(1 for l in text.splitlines() if l.startswith('-') and not l.startswith('---'))
    require(changed == 3, 'patch changes exactly three lines')
    bad = text.replace("                 stat['worse'] += 1\n", "                 stat['worse'] += 2\n", 1)
    require(bad != text, 'control construction')
    try:
        L.apply_patch(source, bad)
    except L.Fail as error:
        rejected = str(error)
    else:
        raise L.Fail('corrupted patch context was accepted')
    return dict(changed_lines=[250, 375, 416], minimal_roundtrip=True, corrupted_context_rejected=rejected)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--repo', default=L.default_repo(__file__), help='repository root')
    ap.add_argument('--out', nargs='?', const=str(HERE / 'atlas_bugs.receipt.json'),
                    help='write a JSON receipt (default: next to this script)')
    ap.add_argument('--full', action='store_true', help='also run the pristine atlas on PR589 (one more run)')
    ap.add_argument('--jobs', type=int, default=4, help='parallel subprocesses')
    args = ap.parse_args()
    t0 = time.time()
    rec = dict(status='RUNNING', script='atlas_bugs.py', environment=L.environment(),
               main_commit_of_pins=L.MAIN_COMMIT, pr1043_head=L.PR1043_HEAD, pr1345_head=L.PR1345_HEAD)
    try:
        repo = L.Repo(args.repo)
        rec['pins'] = dict(main=repo.verify_all(), vendor=L.verify_vendor(), atlas_patch=L.ATLAS_PATCH_PIN)
        B = L.vendor_module('pr1043_build', 'vendor/pr1043/build.py')
        pristine = L.atlas_source('pristine')
        rec['patch'] = patch_controls(pristine)
        rec['line375_416_expression'] = expression_controls()
        expected = json.loads(L.vendor_bytes('vendor/pr1345/result.json'))
        require(census_assertions(expected), 'PR1345 result.json fails its own census')
        with tempfile.TemporaryDirectory(prefix='c2-atlas-') as tmp:
            tmp = Path(tmp)
            r439_bytes = repo.read(L.R439_REL)
            (tmp / 'words').mkdir()
            w589 = tmp / 'words' / 'bitE8mut-p111-tuned.json.gz'   # basename recorded in result.json
            w589.write_bytes(r439_bytes)
            r438 = B.build(json.loads(gzip.decompress(r439_bytes)))
            require(L.content_sha(r438) == L.CONTENT['r438'], 'R438 rebuild')
            w438 = tmp / 'words' / 'r438.json.gz'
            L.save_word(w438, r438)
            trees = {v: L.atlas_tree(repo, tmp, v, L.atlas_source(v)) for v in ('pristine', 'fix1', 'patched')}
            jobs = {'pristine_r438': L.python_argv(trees['pristine'], w438),
                    'fix1_r438': L.python_argv(trees['fix1'], w438),
                    'patched_r438': L.python_argv(trees['patched'], w438),
                    'patched_pr589': L.python_argv(trees['patched'], w589)}
            if args.full:
                jobs['pristine_pr589'] = L.python_argv(trees['pristine'], w589)
            runs = L.run_parallel(jobs, args.jobs)
        res = {}
        for name, r in runs.items():
            line, last = L.traceback_tail(r['stderr'])
            res[name] = dict(rc=r['rc'], seconds=r['seconds'], traceback_line=line, error=last if r['rc'] else None)
        # bug 1
        require(runs['pristine_r438']['rc'] != 0 and res['pristine_r438']['error'] == BUG1
                and res['pristine_r438']['traceback_line'] in (282, 283, 284), 'bug 1 not reproduced')
        # bug 2 (hunk 1 alone moves the crash to the shared-register pair census)
        require(runs['fix1_r438']['rc'] != 0 and res['fix1_r438']['error'] == BUG2
                and res['fix1_r438']['traceback_line'] == 416, 'bug 2 not reproduced')
        # patched R438: completes and reports the known improving transport
        require(runs['patched_r438']['rc'] == 0, 'patched atlas failed on R438: ' + runs['patched_r438']['stderr'][-300:])
        o438 = json.loads(runs['patched_r438']['stdout'].strip().splitlines()[-1])
        found = sorted((x[1], x[2], x[3]) for x in o438['A']['improving'])
        require(found == [(L.OP_INDEX, s, L.NEW_FRAME) for s in (L.SLOT,) + L.ALT_SLOTS]
                and o438['A']['improving_count'] == 3 and o438['B']['improving'] == []
                and all(x[4] < 0 and x[5] < 0 for x in o438['A']['improving']), 'patched R438 improving singles')
        pairA, pairB = o438['simultaneous_pairs']
        require(pairA['improving'] > 1 and pairA['best_improving'] is not None and pairB.get('improving', 0) == 0,
                'patched R438 pairs')
        require(o438 != expected, 'R438 output equals the PR589 result (comparison would be vacuous)')
        res['patched_r438'].update(
            improving_singles=[list(x) for x in o438['A']['improving']], improving_count=o438['A']['improving_count'],
            A_census={k: v for k, v in o438['A'].items() if k != 'improving'},
            B_census={k: v for k, v in o438['B'].items() if k != 'improving'},
            improving_pairs=dict(A=pairA['improving'], B=pairB.get('improving', 0)),
            best_improving_pair=pairA['best_improving'], pairs=o438['simultaneous_pairs'])
        # patched PR589: exactly PR1345's recorded output
        for name in ('patched_pr589',) + (('pristine_pr589',) if args.full else ()):
            require(runs[name]['rc'] == 0, name + ' failed: ' + runs[name]['stderr'][-300:])
            out = json.loads(runs[name]['stdout'].strip().splitlines()[-1])
            require(out == expected, name + ' differs from PR1345 result.json')
            require(census_assertions(out), name + ' fails the census')
            res[name]['equals_pr1345_result_json'] = True
        mutated = json.loads(json.dumps(expected))
        mutated['A']['same_profile'] += 1
        require(mutated != expected and not census_assertions(mutated), 'result sensitivity control')
        rec['runs'] = res
        rec['negative_controls'] = dict(
            pristine_r438_crashes=res['pristine_r438']['error'], fix1_r438_crashes=res['fix1_r438']['error'],
            line375_pristine_condition=rec['line375_416_expression']['375']['pristine'],
            corrupted_patch_rejected=rec['patch']['corrupted_context_rejected'],
            mutated_result_json_not_equal=True, r438_output_differs_from_pr589_result=True)
        rec['status'] = 'PASS'
        rec['seconds'] = round(time.time() - t0, 1)
        line = ('PASS_%s bug1=TypeError@%d(pristine,R438) bug2=TypeError@416(hunk1-only,R438) '
                'patched_R438=ok(improving singles 2027->154/155/425@79, pairs A=%d) '
                'patched_PR589=result.json%s patch=3 lines'
                % (TAG, res['pristine_r438']['traceback_line'], pairA['improving'],
                   ' pristine_PR589=result.json' if args.full else ''))
        rec['final_line'] = line
        if args.out:
            L.write_receipt(args.out, rec)
        print(line)
    except Exception as error:
        rec['status'] = 'FAIL'
        rec['error'] = '%s: %s' % (type(error).__name__, error)
        rec['seconds'] = round(time.time() - t0, 1)
        if args.out:
            try:
                L.write_receipt(args.out, rec)
            except Exception:
                pass
        print('FAIL_%s %s' % (TAG, rec['error']))
        sys.exit(1)


if __name__ == '__main__':
    main()
