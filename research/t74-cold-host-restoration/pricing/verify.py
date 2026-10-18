#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Portable stdout-only entry point; execute the checked source, never bytecode."""
import json
import pathlib
import sys
sys.dont_write_bytecode = True
path = pathlib.Path(__file__).resolve().with_name('verify_budget_certificates.py')
namespace = {'__name__': 'cold_host_pricing_replay', '__file__': str(path)}
exec(compile(path.read_bytes(), str(path), 'exec'), namespace)
if __name__ == '__main__':
    print(json.dumps(namespace['run'](), indent=2))
