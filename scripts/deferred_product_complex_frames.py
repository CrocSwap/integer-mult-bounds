#!/usr/bin/env python3
"""Word-level gate-frame replay of the selected complex producer (independent of the matcher's accounting).

The shipped word (certificates/deferred-product-complex-word.json.gz) must encode exactly the shipped DAG
(same operand pairs, centre roots and piece roots). scripts/deferred_product/complex_frames.py then expands
the full signed two-stage copied-center word (early pass at 0, V at <t>, mixer at labels, centre copies at 0,
pieces at t^perp, inverse mixer and -V at F; stage two reversed with complemented frames and exchanged
banks), checks nesting and nondegenerate whole residuals on every move, and rebuilds the paid histogram,
which must equal PR #104's profile of the shipped row. Alternating rank-2 residuals are allowed: PR #104
(notes/stopped-product-complex.tex) executes every nondegenerate binary residual, alternating forms
included, as one child by the retained Gauss normal form (notes/endpoint-gauge-complex.tex).
"""
import gzip, json, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.argv = [sys.argv[0], '--allow-alternating']          # read by the frame module at import
from deferred_product import complex_frames as cf
import stopped_product_network as spn


def main():
    assert not sys.flags.optimize, 'Run without -O'
    word = json.loads(gzip.decompress((ROOT / 'certificates/deferred-product-complex-word.json.gz').read_bytes()))
    dag = json.loads(gzip.decompress((ROOT / 'certificates/deferred-product-complex-dag.json.gz').read_bytes()))
    v = dag['v']
    assert (word['h'], word['v']) == (dag['h'], v) == (24, 2024)
    flat = dag['args']
    assert len(word['args']) == v + 1 + len(flat) // 2
    for k in range(len(flat) // 2):
        assert list(word['args'][v + 1 + k]) == [flat[2 * k], flat[2 * k + 1]], 'word and DAG differ'
    assert sorted(n for _, n, _ in word['retained']) == sorted(dag['A']), 'centre roots differ'
    assert sorted(n for _, n, _ in word['pieces']) == sorted(dag['D'] + dag['P']), 'piece roots differ'
    w = cf.Word(word)
    events, initial, final, bad, ok_final = cf.forward(w)
    breaks, end = cf.reflect(w, events, initial, final)
    paid, cls = cf.paid_histogram(w, events)
    row = json.loads((ROOT / 'certificates/deferred-product-complex-input.json').read_text())
    expected = spn.profile(row)['child_multiplicities']
    h = w.h
    assert not bad, bad[:3]
    assert ok_final and breaks == 0 and end, 'stage-one endpoints or stage-two reflection'
    assert cls['aux'] == w.R * h and cls['data'] == 2 * v * (h - 1) and cls['center'] == len(w.rout) * (h - 1)
    assert dict(paid) == {int(t): n for t, n in expected.items()}, 'paid histogram differs from the row profile'
    print('PASS complex word: %d moves, 0 violations, reflection continuous, histogram == row profile; '
          'alternating rank-2 residuals %d (one-child Gauss normal form)' % (
              sum(1 for e in events if e[0] == 'move'), cf.ALTERNATING.get(2, 0)))


if __name__ == '__main__':
    main()
