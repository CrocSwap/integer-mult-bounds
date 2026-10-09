#!/usr/bin/env python3
"""Replay the selected h24 all-disjoint rational-center complex producer from its shipped addition DAG.

Every support, core, cover, label type and rank is recomputed from the operand pairs
(scripts/deferred_product/replayed.py); the unchanged PR #104 matcher
(scripts/endpoint_gauge/match_complex_general.cpp) then rebuilds the role count and the
physical histogram, which must equal certificates/deferred-product-complex-input.json.
Same flow as scripts/stopped_product_producer.py (icekylinx), with the replayed build.
"""
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from copied_centers.corners import require
from copied_centers.physical import copied_histogram
from endpoint_gauge_producer import compare
from deferred_product.replayed import build


def main():
    require(sys.flags.optimize == 0, 'Run without -O: mathematical assertions must remain enabled')
    expected = json.loads((ROOT / 'certificates/deferred-product-complex-input.json').read_text())
    require((expected['h'], expected['central_disjoint'], expected['center_denominator']) == (24, 24, 21),
            'Wrong rational-center parameters')
    compiler = os.environ.get('CXX', 'c++')
    with tempfile.TemporaryDirectory(prefix='deferred-product-') as directory:
        work = Path(directory)
        prefix = work / 'complex_replayed_d24'
        construction = build(ROOT / 'certificates/deferred-product-complex-dag.json.gz', prefix)
        program = work / 'match_complex_general'
        subprocess.run([*shlex.split(compiler), '-O3', '-std=c++17',
                        str(ROOT / 'scripts/endpoint_gauge/match_complex_general.cpp'), '-o', str(program)], check=True)
        matched = json.loads(subprocess.check_output(
            [str(program), str(prefix) + '.bin', str(prefix) + '.labels'], text=True))
    compare(matched, expected, 'complex h=24 replayed rational centers')
    require(construction['R'] == matched['baseline_R'], 'Wrong raw complex roles')
    copied_histogram(matched)
    print('PASS replayed complex producer: R=%d (baseline %d, matched %d), histogram equal' % (
        matched['R'], matched['baseline_R'], matched['matched']))


if __name__ == '__main__':
    main()
