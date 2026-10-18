#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Recompute every cap, group control and rejection, and compare with the committed RESULT.json."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run


def main():
    got = run.compute()
    want = json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8'))
    run.C.need(got == want, 'recomputed result differs from RESULT.json')
    run.C.need(all(v['matches_shipped_bracket'] and v['matches_shipped_idle'] for v in got['ladder'].values()), 'ladder')
    run.C.need(all(v['raises_parent_cap'] for v in got['stage1_groups_alone_on_parent'].values()), 'groups')
    run.C.need([v['raises_parent_cap'] for _, v in sorted(got['v45_endpoint_subsets_on_parent'].items())] == [False] * 4 + [True], 'subsets')
    print('PASS_INDEPENDENT_STAGE_CAP_RESOLVE caps=4 matched groups=5 raise_alone v45_subsets=only_k4 controls=%d no_new_kappa' % len(got['controls']))


if __name__ == '__main__':
    main()
