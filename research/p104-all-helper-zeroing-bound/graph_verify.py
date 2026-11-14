#!/usr/bin/env python3
"""Explicit local module loader for the independent graph funding engines."""
from pathlib import Path
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent / 'graph'


def run():
    modules = {}
    for name in ('helper_funding_common', 'rebuild_engine', 'structure_engine',
                 'subset_engine', 'run_controls'):
        spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        modules[name] = module
    result = modules['run_controls'].run()
    if result['valid_run']['global_rank_Q'] != 463:
        raise ValueError('global original-coordinate funding rank')
    return result


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, sort_keys=True))
