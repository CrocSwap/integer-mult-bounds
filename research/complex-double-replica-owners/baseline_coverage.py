#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Hao Yan (@FanPUYen)
"""Require the accepted PR741 replay's fixed stage and artifact coverage.

Prepared with substantial OpenAI Codex assistance. The omission risk was
identified by Lucas in PR838 and Chinmay in PR847. These fixed inventories
were read from the accepted PR741 verify.py and its native local outputs;
no pending implementation is imported. This complements the unchanged
upstream source/artifact/log binding checker, which must run afterward.
Receipt coverage is not authentication of a claimed execution history.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

MANIFEST_SHA256 = 'b9b39c206fcd2613382b0dcbda23a371e8781d1bedaf8e2f8e7df1e79dc1fa89'
SPEC_SHA256 = '7fc2bd2e3c0ac13729c1fa1f0f327a4eb7c72373ba58e5ed3954b30e23c803be'
STAGE_NAMES = (
    'ancestral558-fresh', 'gauge44-exact-construction', 'notri56-construction',
    'notri-control-g44', 'layered66-construction', 'p6n-cold72-construction',
    'four-promotions', 'promotion-controls', 'sw4-read-exchanges',
    'eight-B-frame-construction', 'all728-columns-native', 'both-native-ledgers',
    'independent-native-controls', 'residual-wrappers', 'all-native-phase-edges',
    'independent-scalar-frames-cones', 'inherited-cold-controls', 'eight-frame-controls',
    'owner-construction-controls', 'strict-global-admission',
    'independent-literal-map-moment', 'independent-two-engine-outer47',
)
ARTIFACT_NAMES = frozenset((
    'RESULT.json', 'ANCESTRAL-LINK.json', 'STAGES.json', 'INDEPENDENT-LOCAL.json',
    'INDEPENDENT-MAP.json', 'INDEPENDENT-PRICE.json', 'RECONSTRUCTED-OWNERS.json.gz',
    'OWNER-CONSTRUCTION-CONTROLS.json', 'FRAME-CONTROLS.json',
    'cold-controls/COLD-END-CONTROLS.json', 'PROMO-CONTROLS.json',
    'promoted/FULL-WORD.json.gz', 'p6n/STEPS.json', 'p6n/controls/COLD-END-CONTROLS.json',
    'p6n/p6n/FULL-WORD.json.gz', 'sw4/BUILD.json', 'sw4/FULL-WORD.json.gz',
    'frames/BUILD.json', 'frames/FULL-WORD.json.gz', 'gauge44/STEPS.json',
    'notri56/STEPS.json', 'notri56/cold44/CONSTRUCTION.json', 'notri-control/STEPS.json',
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


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(ancestor):
    complex_dir = Path(ancestor).resolve()/'complex'
    receipt_path, stages_path = complex_dir/'RECEIPT.json', complex_dir/'STAGES.json'
    receipt = read(receipt_path)
    require(receipt['manifest_sha256'] == MANIFEST_SHA256 and receipt['spec_sha256'] == SPEC_SHA256,
            'PR741 fixed coverage source identity')
    require(tuple(stage['name'] for stage in receipt['stages']) == STAGE_NAMES,
            'PR741 fixed ordered stage coverage')
    require(all(stage['exit_code'] == 0 for stage in receipt['stages']), 'PR741 unsuccessful stage')
    require(set(receipt['artifacts']) == ARTIFACT_NAMES, 'PR741 fixed artifact coverage')
    require(read(stages_path) == receipt['stages'], 'PR741 STAGES receipt consistency')
    return dict(status='PASS_FIXED_PR741_STAGE_AND_ARTIFACT_COVERAGE',
                ordered_stage_count=len(STAGE_NAMES), mandatory_artifact_count=len(ARTIFACT_NAMES),
                source_manifest_sha256=MANIFEST_SHA256, source_spec_sha256=SPEC_SHA256,
                complex_receipt_sha256=sha(receipt_path), stages_sha256=sha(stages_path),
                scope='Fixed coverage and receipt/STAGES agreement only. The unchanged maintainer binding must also verify every artifact and log digest. This does not authenticate execution history or fabricated logs.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ancestor', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Output file must be new')
    result = check(args.ancestor)
    args.out.write_bytes((json.dumps(result, indent=2)+'\n').encode('utf-8'))
    print(result['status'])


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        print('FAIL:', error, file=sys.stderr)
        raise SystemExit(1)
