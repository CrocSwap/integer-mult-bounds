#!/usr/bin/env python3
"""Replay the structural optimum and exact obstruction; no improved bound.

--full also reproduces legacy acceptance of the semantically invalid witness.
"""
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parent))
import core as C
import flow_check
import stream_check


def mathematical_report():
    C.sources()
    frames, phases, audit, owners = C.inputs()
    new, groups, table, contexts = C.derive(frames, phases, owners)
    checks = C.check_assignment(frames, new, phases, owners)
    flows = flow_check.census(table)
    profile = C.profile(frames, new, audit)
    report = dict(structure=dict(contexts=len(contexts), groups=len(groups), motifs=table),
        assignment=checks, profile=profile, frame_sha256=C.digest(new), groups_sha256=C.digest(groups),
        flow_sha256=C.digest(flows), flow_summary=[{k: v for k, v in f.items() if k != 'verdicts'} for f in flows])
    return report, new


def compare(got, want, label):
    C.need(C.canonical(got) == C.canonical(want), 'saved certificate mismatch: '+label)


def run(work, full=False):
    C.need(not work.exists(), 'work output already exists')
    if full:
        C.need(__debug__, 'full inherited checks require assertions; omit -O')
    work.mkdir(parents=True)
    expected = C.read(C.PACKAGE/'EXPECTED.json')
    report, frames = mathematical_report()
    compare(report, expected['mathematics'], 'mathematics')
    C.write(work/'MATHEMATICS.json', report)
    C.write(work/'PROFILE.json', report['profile'])
    C.write(work/'FRAMES.json', frames)
    # Retained engines run with assertions even under an optimized structural
    # caller. -I removes inherited PYTHONOPTIMIZE/PYTHONPATH effects.
    subprocess.run([sys.executable, '-I', '-B', str(C.PACKAGE/'pricing.py'),
                    '--profile', str(work/'PROFILE.json'), '--out', str(work/'PRICES.json')], check=True)
    prices = C.read(work/'PRICES.json')
    compare(prices, expected['prices'], 'exact prices')
    old, phases, _, owners = C.inputs()
    obstruction = stream_check.report(old, frames, phases, owners)
    compare(obstruction, expected['stream_obstruction'], 'physical stream obstruction')
    C.write(work/'STREAM-OBSTRUCTION.json', obstruction)
    result = dict(status='PASS_SELECTED1094_IDLE_REASSIGNMENT_OPTIMUM', mathematics=report, prices=prices,
                  admitted=False, stream_obstruction=obstruction, legacy_checks_rerun=False)
    print('PASS_SELECTED1094_IDLE_OPTIMUM groups=1792 motifs=9 rank_vectors=1049', flush=True)
    print(obstruction['status']+' admitted=false', flush=True)
    if full:
        import legacy_checks
        legacy = legacy_checks.run(work/'legacy', frames, report['profile'], prices)
        compare(legacy, expected['legacy_acceptance'], 'reproduced legacy acceptance')
        result.update(legacy_checks_rerun=True, legacy_acceptance=legacy)
        print(legacy['status'], flush=True)
    C.write(work/'RECEIPT.json', result)
    print('receipt_sha256='+C.digest(result), flush=True)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work', type=Path, help='New output directory; existing paths are preserved')
    ap.add_argument('--full', action='store_true', help='Also reproduce legacy acceptance and all 96 inherited controls')
    args = ap.parse_args()
    if args.work:
        run(args.work.resolve(), args.full)
    else:
        with tempfile.TemporaryDirectory(prefix='selected1094-idle-') as parent:
            run(Path(parent)/'replay', args.full)


if __name__ == '__main__':
    main()
