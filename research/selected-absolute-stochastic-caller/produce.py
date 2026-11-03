"""Check every distinct selected native edge with two exact representations."""

import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from sampler import need, route


def matrix_monomial(z, rec):
    real, imag = z
    dest, phases = route(rec)
    rr, ii = np.empty_like(real), np.empty_like(imag)
    for src, (dst, p) in enumerate(zip(dest, phases)):
        a, b = real[src], imag[src]
        if p == 0:
            rr[dst], ii[dst] = a, b
        elif p == 1:
            rr[dst], ii[dst] = -b, a
        elif p == 2:
            rr[dst], ii[dst] = -a, -b
        else:
            rr[dst], ii[dst] = b, -a
    return rr, ii


def recipe_matrix(rec):
    re, im = matrix_monomial((np.eye(512, dtype=np.int64), np.zeros((512,512), dtype=np.int64)), rec['right'])
    for axis in range(rec['rank']):
        lo = np.array([j for j in range(512) if not j >> axis & 1])
        hi = lo ^ (1 << axis)
        sr, si, dr, di = re[lo]+re[hi], im[lo]+im[hi], re[lo]-re[hi], im[lo]-im[hi]
        re[lo], im[lo], re[hi], im[hi] = sr-di, si+dr, sr+di, si-dr
    return matrix_monomial((re, im), rec['left'])


def main():
    need(__debug__, 'source assertions remain enabled')
    for item in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if item['usage'] == 'input':
            need(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest() == item['sha256'], 'source bytes')
    src = ROOT/'research/staged544-mixed-fourth-entry/native/vendor/native/new/code/borrow'
    sys.path[:0] = [str(src), str(src/'vendor/clifford')]
    import bw_gauss
    from clifford_exact import canonical_frame, lower_child
    word = json.loads(gzip.decompress((ROOT/'research/p104-helper470-twin-rung-removal/WORD.json.gz').read_bytes()))
    charts, recipes, ranks, counts = {}, {}, [], Counter()
    controls = 0
    for e in word['program']:
        if e[0] != 'MOVE':
            ranks.append(0)
            continue
        old, new = e[2:4]
        key = f'{old},{new}'
        if key not in recipes:
            for t in (old,new):
                if t not in charts:
                    charts[t] = canonical_frame(9, word['frames'][t])
            rec, compiled = lower_child(charts[old].adjoint().then(charts[new]))
            need(1 <= rec['rank'] <= 8, 'selected native rank')
            actual_re, actual_im = recipe_matrix(rec)
            re, im, exponent = bw_gauss.frame(
                bw_gauss.frame(bw_gauss.eye(9), word['frames'][old], 9, -1),
                word['frames'][new], 9)
            need(exponent <= 18 and np.max(np.abs(re)) <= 1 << 18 and
                 np.max(np.abs(im)) <= 1 << 18 and np.max(np.abs(actual_re)) <= 1 << 8 and
                 np.max(np.abs(actual_im)) <= 1 << 8, 'integer matrix range')
            need(np.array_equal(actual_re << exponent, re << rec['rank']) and
                 np.array_equal(actual_im << exponent, im << rec['rank']), 'all columns of every native edge')
            if not recipes:
                need(not (np.array_equal(-actual_im << exponent, re << rec['rank']) and
                          np.array_equal(actual_re << exponent, im << rec['rank'])), 'global phase mutation is rejected')
                need(not (np.array_equal(actual_re << exponent, re << rec['rank']) and
                          np.array_equal(-actual_im << exponent, im << rec['rank'])), 'conjugate mutation is rejected')
                controls = 2
            recipes[key] = rec
        rank = recipes[key]['rank']
        ranks.append(rank)
        counts[rank] += 1
    out = Path(sys.argv[1])
    data = {'recipes':recipes,'ranks':ranks}
    encoded = (json.dumps(data,sort_keys=True,separators=(',',':'))+'\n').encode()
    (out/'native.json').write_bytes(encoded)
    (out/'source-summary.json').write_text(json.dumps({
        'events':len(word['program']),'distinct_edges':len(recipes),'frames':len(charts),
        'full_operator_columns':len(recipes)*512,'move_events':sum(counts.values()),
        'rank_counts':{str(k):v for k,v in sorted(counts.items())},
        'native_stage_count_per_tensor_axis':sum(k*v for k,v in counts.items()),
        'all_recipe_sha256':hashlib.sha256(encoded).hexdigest(),
        'source_assertions_enabled':__debug__,'operator_mutation_controls':controls},indent=2)+'\n')


if __name__ == '__main__':
    main()
