#!/usr/bin/env python3
"""Compact read-only replay; verbose scientific stdout stays private.

Prepared by Chris R / Clear1nsight with substantial OpenAI Codex assistance.
Apache-2.0.
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('passive_saved_portable', HERE / 'portable.py')
loader = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = loader
spec.loader.exec_module(loader)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', choices=['all', 'integrity', 'author', 'independent', 'controls'], default='all')
    args = parser.parse_args()
    report = {'status': 'PASS_PASSIVE_SAVED_QUERY_CEILING', 'phase': args.phase,
              'native_source': '86e474038e05f99a76d41f71d81946ad2327e4a4',
              'macro_cuts': 9, 'observed_banks': 39, 'zero_diagonal_inputs': 104,
              'late_grade7_words': 5408, 'target_grade': 9,
              'passive_only': True, 'sufficiently_large_width': True,
              'physical_emission': False, 'new_kappa': None}
    if args.phase == 'integrity':
        loader.integrity()
    else:
        with loader.private_stage() as (stage, requests, work):
            if args.phase in ('all', 'author'):
                report['author_exact_stdout_receipts'] = loader.author_replay(stage, requests, work)
            if args.phase in ('all', 'independent'):
                report['independent_exact_stdout_receipt'] = loader.independent_replay(stage, work)
            if args.phase in ('all', 'controls'):
                report['wrapper_mutation_rejections'] = loader.controls(stage, requests, work)
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
