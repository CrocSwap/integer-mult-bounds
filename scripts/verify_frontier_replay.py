#!/usr/bin/env python3
"""Run the frozen PR741/799 verifiers with mandatory PR741 receipt coverage.

The historical scripts and their proof-record hashes remain unchanged. A run
is complete only when this entrypoint writes its top-level RESULT.json.
Coverage finding: Lucas (@ljste), PR838. Integration: Chinmay (@chinmayarvind23), with
substantial OpenAI Codex assistance. Apache-2.0. No new mathematical bound.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from verify_frontier741_bindings import check as check_composition, read, require

ROOT = Path(__file__).resolve().parents[1]

# Contract of the frozen complex-sw4-frame8/verify.py producer. Its 34 fixed
# outputs and ten local outputs are deliberately independent of the candidate
# receipt. Tests bind this list to the producer and the retained complete run.
EXPECTED_STAGES = (
    'ancestral558-fresh', 'gauge44-exact-construction', 'notri56-construction',
    'notri-control-g44', 'layered66-construction', 'p6n-cold72-construction',
    'four-promotions', 'promotion-controls', 'sw4-read-exchanges',
    'eight-B-frame-construction', 'all728-columns-native', 'both-native-ledgers',
    'independent-native-controls', 'residual-wrappers', 'all-native-phase-edges',
    'independent-scalar-frames-cones', 'inherited-cold-controls',
    'eight-frame-controls', 'owner-construction-controls',
    'strict-global-admission', 'independent-literal-map-moment',
    'independent-two-engine-outer47',
)
EXPECTED_ARTIFACTS = frozenset((
    'RESULT.json', 'ANCESTRAL-LINK.json', 'STAGES.json',
    'INDEPENDENT-LOCAL.json', 'INDEPENDENT-MAP.json', 'INDEPENDENT-PRICE.json',
    'RECONSTRUCTED-OWNERS.json.gz', 'OWNER-CONSTRUCTION-CONTROLS.json',
    'FRAME-CONTROLS.json', 'cold-controls/COLD-END-CONTROLS.json',
    'PROMO-CONTROLS.json', 'promoted/FULL-WORD.json.gz', 'p6n/STEPS.json',
    'p6n/controls/COLD-END-CONTROLS.json', 'p6n/p6n/FULL-WORD.json.gz',
    'sw4/BUILD.json', 'sw4/FULL-WORD.json.gz', 'frames/BUILD.json',
    'frames/FULL-WORD.json.gz', 'gauge44/STEPS.json', 'notri56/STEPS.json',
    'notri56/cold44/CONSTRUCTION.json', 'notri-control/STEPS.json',
    'layered66/STEPS.json', 'layered66/swap/PIVOT-SWAP.json',
    'layered66/controls/COLD-END-CONTROLS.json', 'global-replay/REPLAY.json',
    'global-replay/ASSEMBLY.json', 'global-replay/STAGES.json',
    'global-replay/ADMISSION-CONTROLS.json', 'global-replay/BIT-SUPPLIER-CONTROLS.json',
    'global-replay/global/audit/OWNERS-AND-PROFILE.json',
    'global-replay/global/audit/PREFIX-AND-INVOICE.json',
    'global-replay/global/audit/ASYNC-AUDIT.json',
    'local/CANONICAL-WORD.json.gz', 'local/CLIFFORD-RECIPES.json',
    'local/CLIFFORD-REVIEW.json', 'local/FULL-WORD.json.gz',
    'local/INDEPENDENT-LOCAL-REPLAY.json', 'local/LOCAL-CHECKS.json',
    'local/LOCAL-PROGRAMS.json.gz', 'local/RESIDUAL-ADAPTERS.json',
    'local/SCALAR-FRAME-AUDIT.json', 'local/WRAPPER-CHECKS.json',
))


def check_coverage(complex_dir):
    receipt = read(complex_dir / 'RECEIPT.json')
    stages = receipt['stages']
    require(tuple(s['name'] for s in stages) == EXPECTED_STAGES and
            all(s['exit_code'] == 0 for s in stages), 'Required replay stages differ')
    require(set(receipt['artifacts']) == EXPECTED_ARTIFACTS,
            'Required replay artifact inventory differs')
    require(read(complex_dir / 'STAGES.json') == stages,
            'Receipt stages differ from recorded execution stages')


def check_ancestry(ancestor):
    """Enforce coverage, then retain every original source/hash/math check."""
    check_coverage(ancestor / 'complex')
    return check_composition(ancestor / 'bit', ancestor / 'complex')


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--frontier', choices=('741', '799'), required=True)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--ancestor', type=Path,
                   help='PR799 only: reuse a complete historical PR741 output '
                        '(or the replay/ directory of this entrypoint)')
    a = p.parse_args(argv)
    work = a.work.resolve()
    if sys.flags.optimize or work.exists() or work.is_relative_to(ROOT):
        p.error('Use enabled assertions and a fresh output directory outside the repository')
    if a.ancestor is not None and a.frontier != '799':
        p.error('--ancestor is only supported for frontier 799')
    ancestor = a.ancestor.resolve() if a.ancestor is not None else None
    # Reject incomplete reused evidence before starting any supplier work.
    if ancestor is not None:
        check_ancestry(ancestor)
    work.mkdir(parents=True)
    replay = work / 'replay'
    command = [sys.executable, '-B', str(ROOT / ('scripts/verify_frontier' + a.frontier + '.py')),
               '--work', str(replay)]
    if ancestor is not None:
        command += ['--ancestor', str(ancestor)]
    subprocess.run(command, cwd=ROOT, check=True)
    if ancestor is None:
        ancestor = replay if a.frontier == '741' else replay / 'ancestor'
    check_ancestry(ancestor)
    result = read(replay / 'RESULT.json')
    result['receipt_coverage'] = dict(stages=len(EXPECTED_STAGES), artifacts=len(EXPECTED_ARTIFACTS))
    # Nested files are the historical producer's output. Publish the public
    # completion record only after the additional evidence checks succeed.
    (work / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('PASS_COMPLETE_REPLAY_RECEIPT_COVERAGE', result['decimal'], flush=True)


if __name__ == '__main__':
    main()
