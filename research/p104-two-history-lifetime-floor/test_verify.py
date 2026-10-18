#!/usr/bin/env python3
"""Positive replay and semantic failure controls for the lifetime-floor re-pricing."""
from fractions import Fraction as Q
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as v  # noqa: E402


def rejects(action, reason):
    try:
        action()
    except AssertionError as error:
        assert reason in str(error), (reason, str(error))
    else:
        raise AssertionError('control accepted: ' + reason)


def main():
    result = v.compute()
    assert result['pr2920_curve_checked'], 'fetch pull/2920/head to bind the endpoint curve'
    for floor, row in result['floors'].items():
        assert row['lifetimes'] >= int(floor) and row['passes']
    assert (result['floors']['208']['cheap'], result['floors']['208']['units']) == (0, 208)
    assert result['first_rejecting_floor']['lifetimes'] == 423

    module, cmin = v.engine(), v.curve()
    price = v.Price(module, v.SELECTED)
    # Control 1: without the floor, PR2920's optimum violates every reported floor.
    assert v.optimum(price, 0, cmin)[0] == (0, 208)
    # Control 2: a changed one-unit capacity (same total demand) no longer matches PR2920.
    saved, v.TYPES = v.TYPES, [v.TYPES[0], (44, 27, 24)] + v.TYPES[2:]
    try:
        rejects(v.compute, 'curve equals PR2920 receipt')
    finally:
        v.TYPES = saved
    # Control 3: a wrong affine coefficient is caught by the direct relax re-evaluation.
    price.qc = (price.qc[0] / 2, price.qc[1] / 2)
    rejects(lambda: v.optimum(price, 219, cmin), 'affine enclosure agrees')
    # Control 4: at the threshold, one fewer lifetime still passes and the floor itself rejects.
    price = v.Price(module, v.SELECTED)
    assert price(*v.optimum(price, 422, cmin)[0])[1] < 1
    assert all(price(*p)[0] > 1 for p in v.candidates(423, cmin))
    # Control 5: an altered receipt is rejected.
    path = v.PACKAGE / 'RESULT.json'
    original = path.read_text(encoding='utf-8')
    try:
        path.write_text(original.replace('"lifetimes": 423', '"lifetimes": 424'), encoding='utf-8')
        rejects(v.main, 'typed receipt')
    finally:
        path.write_text(original, encoding='utf-8')
    # Control 6: a changed pinned pricing engine is rejected before use.
    engine_path = v.ROOT / 'research/complex-local-word-ceiling/ceiling.py'
    original = engine_path.read_bytes()
    try:
        engine_path.write_bytes(original + b'\n')
        rejects(v.engine, 'pinned input')
    finally:
        engine_path.write_bytes(original)
    print('PASS_POSITIVE_AND_6_CONTROLS')


if __name__ == '__main__':
    main()
