#!/usr/bin/env python3
"""One bounded floating solve. Never a theorem or admitted supplier.

Apache-2.0; substantial OpenAI Codex assistance and retained source credit.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import shared_maps as S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--functional', type=int, default=1)
    ap.add_argument('--seconds', type=float, default=120.)
    args = ap.parse_args()
    S.need(1 <= args.functional <= 511 and 0 < args.seconds <= 120, 'Bounded single discovery solve')
    spec = importlib.util.spec_from_file_location('owned_shared_prior_discover', S.PRIOR / 'discover.py')
    prior = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prior)
    prior.M = S.M
    S.M.build = S.build
    model = S.build(S.payload(), [args.functional])
    summary = {'free_shared_late_maps': len(model['shared_late_maps']),
               'preserved_prelude_lines': len(model['prelude_lines']),
               'changed_native_rank_tables': model['changed_native_tables'],
               'owned_copies': model['owned_copies']}
    print(json.dumps(summary, sort_keys=True), flush=True)
    result = prior.solve(S.SOURCE, [args.functional], args.seconds, 'none', 'kernel')
    result.update(summary)
    result['changed_contract'] = 'Nonmonotone persistent contacts, all8 paid owned inputs, shared late G; frozen native prelude boundaries'
    result['scope'] = 'BOUNDED_FLOATING_DISCOVERY_ONLY_SHARED_G_SYNTHESIS_AND_NATIVE_ADMISSION_UNRUN'
    (HERE / 'DISCOVERY.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'selected_nodes'}, sort_keys=True))


if __name__ == '__main__':
    main()
