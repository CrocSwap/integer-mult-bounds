#!/usr/bin/env python3
"""Run the inherited signed-product check against the actual candidate runtime.

Counts show whether this finite product crosses the typed native-word boundary.
"""
import json
from pathlib import Path
import runpy
import sys

runtime = Path(sys.argv[1]).resolve()
peer = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(runtime))
from installations import ENTRY, TERMINAL
from strong_complex import digest
from grades import numerical_source
from typed_raw import TypedRaw
from retimed_supplier import Positive

atlas = numerical_source()[0]
assert digest(atlas.graph) == 'ed3bea7186f962f3a8a8ae389cecce3d1ef48a7a832cf9af6c9048a6b5919b35'
counts = {'typed_native_calls': 0, 'positive_run_calls': 0, 'direct_positive_calls': 0, 'recursive_positive_calls': 0}
native = TypedRaw.native
run = Positive._run

def traced_native(self, *args, **kwargs):
    counts['typed_native_calls'] += 1
    return (yield from native(self, *args, **kwargs))

def traced_run(self, field, low, selected, columns, root_width):
    from retimed_supplier import power_le
    counts['positive_run_calls'] += 1
    if selected <= self.carrier or power_le(selected, self.denominator, root_width):
        counts['direct_positive_calls'] += 1
    else:
        counts['recursive_positive_calls'] += 1
    return run(self, field, low, selected, columns, root_width)

TypedRaw.native = traced_native
Positive._run = traced_run
module = runpy.run_path(str(peer / 'verify.py'))
sys.path.insert(0, str(runtime))
module['product'](runtime)
print('CANDIDATE_PRODUCT_PATH_COUNTERS', json.dumps(counts, sort_keys=True), flush=True)
print('PASS_CANDIDATE_RESTORED_SIGNED_PRODUCT', flush=True)
