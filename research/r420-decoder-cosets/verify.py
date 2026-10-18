# Apache-2.0; cxnmai with substantial OpenAI assistance.
"""Run from any cwd with Python 3.11+, standard library only."""
import gzip
import hashlib
import importlib.util
import json
import sys
from functools import reduce
from operator import xor
from pathlib import Path
from checks import controls, replay
from model import INDEX, ROOT, SOURCE, bits, counts, kernel, load, prefix, rebuild
from search import search

HERE = Path(__file__).resolve().parent
CHECKER = ROOT / 'research/e8-bit-r420/code/xcheck.py'
CHECKER_SHA = '5737d18a7826fd51e131035f2d7bebba2e2868af91dd7672a5f11208b036d424'


def main():
    if not __debug__:
        raise SystemExit('Assertions required: do not use python -O')
    recipe = json.loads((HERE/'RECIPE.json').read_text())
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == recipe['source_sha256']
    assert hashlib.sha256(CHECKER.read_bytes()).hexdigest() == CHECKER_SHA
    assert search() == recipe, 'bounded search did not reproduce frozen recipe'
    w = load()
    c = rebuild(w, recipe['operands'])
    assert counts(w) == recipe['before'] and counts(c) == recipe['after']
    assert w['ret'][INDEX] == 583
    assert not any(583 in [g[1]]+g[2] for g in w['A'][-9+INDEX+1:]+w['B'])
    values = prefix(w)
    old_pool = sorted({s for _, _, ss in w['A'][-9:] for s in ss}-set(w['ret']))
    assert len(old_pool) == 80 and not kernel(values, old_pool)
    d6 = [g for g in w['A'][:-9] if len(w['frames'][g[0]]) == 30]
    dead = {g[2][0] for g in d6[:180]}
    pool = dead-set(w['ret'])
    assert len(dead) == 180 and len(pool) == 171
    assert len(kernel(values, sorted(pool))) == 81
    assert not any(pool & set([g[1]]+g[2]) for g in w['B'])
    for move in recipe['moves']:
        assert set(move['toggle']) <= pool
        delta = reduce(xor, (values[r] for r in move['toggle']), 0)
        assert delta and not delta & ((1 << 240)-1)
    toggle = set(recipe['original_operands']) ^ set(recipe['operands'])
    delta = reduce(xor, (values[r] for r in toggle), 0)
    assert delta and not delta & ((1 << 240)-1)
    assert 569 in recipe['operands']  # retained operand is never toggled
    paths, peak = replay(w)
    new_paths, new_peak = replay(c)
    assert paths == new_paths
    rejected = controls(w, c)
    spec = importlib.util.spec_from_file_location('r420_xcheck', CHECKER)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    _, labels, full, hypotheses, conclusion, _ = checker.check(c)
    assert all(hypotheses.values()) and all(conclusion.values())
    # Frame mutation retains every scalar value: reject for geometry, not F2.
    import copy
    bad = copy.deepcopy(c)
    bad['A'][-9+INDEX][0] = 0
    obj = checker.Word(bad)
    try:
        obj.full()
    except checker.Reject as error:
        assert 'climb not nested' in str(error)
        rejected.append('total_at_zero_frame')
    else:
        raise AssertionError('unpaid frame accepted')
    result = dict(columns=full['columns'], labels=labels,
                  counts_before=counts(w), counts_after=counts(c),
                  identical_register_paths=len(paths),
                  positive_forward_before=peak, positive_forward_after=new_peak,
                  changed_dirt_columns=delta.bit_count(), controls=rejected,
                  canonical_word_sha256=hashlib.sha256(json.dumps(
                      c, sort_keys=True, separators=(',', ':')).encode()).hexdigest())
    # Actual predecessor exporter, not an assumed gate-to-record translation.
    import tempfile
    from native import audit
    with tempfile.TemporaryDirectory(prefix='r420-cosets-') as tmp:
        tmp = Path(tmp)
        word = tmp/'candidate.json.gz'
        with gzip.open(word, 'wt') as f:
            json.dump(c, f)
        baseline = audit(SOURCE, tmp/'baseline')
        candidate = audit(word, tmp/'candidate')
    assert baseline['additions']-candidate['additions'] == 244
    assert baseline['rank_histogram'] == candidate['rank_histogram']
    result['native_before'], result['native_after'] = baseline, candidate
    expected = HERE/'EXPECTED.json'
    if '--record' in sys.argv:
        expected.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        assert json.loads(expected.read_text()) == result
    if '--word' in sys.argv:
        with gzip.open(sys.argv[sys.argv.index('--word')+1], 'wt') as f:
            json.dump(c, f)
    print('PASS_R420_DECODER_COSET total=26916->26672 saved=244 columns=660 controls=6 no_new_kappa')


if __name__ == '__main__':
    main()
