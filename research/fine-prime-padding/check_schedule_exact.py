"""Run the byte-preserved PR1758 second simulation with exact equality.

Its original predicate is numpy.allclose on integer-valued binary64 data.
Here allclose is replaced, for this process only, by strict array equality.
This strengthens the comparison without editing the retained predecessor.
"""
import runpy
from pathlib import Path
import numpy as np

if not __debug__:
    raise RuntimeError('Assertions must be enabled')
# All seven retained cases have g<=7, L<=12, coefficients <=3 and inputs <=5.
# This bounds every partial integer sum well below binary64's exact range.
assert 5*(3*12)**7 < 2**53
calls = []
original = np.allclose

def exact(left, right, *args, **kwargs):
    assert np.all(np.isfinite(left)) and np.all(np.isfinite(right))
    assert np.all(left == np.rint(left)) and np.all(right == np.rint(right))
    assert np.max(np.abs(left)) < 2**53 and np.max(np.abs(right)) < 2**53
    calls.append(bool(np.array_equal(left, right)))
    return calls[-1]

try:
    np.allclose = exact
    runpy.run_path(str(Path(__file__).resolve().parent/'vendor/pr1758/outer/sched_review.py'), run_name='__main__')
finally:
    np.allclose = original
assert len(calls) == 7 and all(calls)
print('PASS_RETAINED_UNION_REVIEW_EXACT_EQUALITY')
