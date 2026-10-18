#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Run an unchanged pinned T74 script with PR1029/PR662 exact state evaluation."""
import argparse
import importlib.util
from pathlib import Path
import runpy
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import need, source_bytes

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result

def main():
    need(__debug__, 'assertions must remain enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vendor', type=Path, required=True)
    parser.add_argument('--script', choices=('bw_adapters.py', 'bw_phases.py'), required=True)
    parser.add_argument('arguments', nargs='+')
    args = parser.parse_args()
    vendor = args.vendor.resolve()
    source_bytes(vendor)
    native = vendor / 'native/new/code/borrow'
    algebra = module('clifford_exact', native / 'vendor/clifford/clifford_exact.py')
    tables = module('t74_exact_tables', vendor / 'accelerators/tables.py')
    sparse = module('t74_exact_sparse', vendor / 'accelerators/sparse_state.py')
    tables.clear_caches()
    algebra.Op.zero_state = lambda self, basis=0: sparse.zero_state(self, tables, basis)
    script = native / args.script
    sys.argv = [str(script), *args.arguments]
    runpy.run_path(str(script), run_name='__main__')

if __name__ == '__main__':
    main()
