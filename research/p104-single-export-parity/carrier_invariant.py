# SPDX-License-Identifier: Apache-2.0
"""Forward certificate for the unmatched chart-510 export at #8036 (99878b566bfc).

Ali Romman supplied the pinned 111-port tape. The local reader lists are the
Clear1nsight #8036 lists. The formal MOVE-noise certificate extends that work.
Run with Python 3.10+ and a path to the original strong-bit.json.gz or its folder.
"""
import argparse
from functools import reduce
from gzip import decompress
from hashlib import sha256
import json
from operator import xor
from pathlib import Path


SHA = '74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'
EXPANDED_SHA = 'b096d6df2a0c4688296b13ab0cfd50fec1c7dec732819c624ddd7a745a144b69'
LENSES = {
    'a': (10037, 2829, 2335, 29847, 3525, 231,
          (2336,2344,2416,2439,2448,2451,2482,2655,2698)),
    'b': (10034, 2828, 2337, 29578, 3496, 222,
          (2359,2362,2372,2394,2397,2408,2416,2419,2425,2431,2434,2465,
           2484,2518,2530,2571,2576,2584,2600,2617,2623,2626,2778)),
}


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            k = row.bit_length()
            if k not in pivots:
                pivots[k] = row
                break
            row ^= pivots[k]
    return len(pivots)


def support(word):
    return [i for i in range(word.bit_length()) if word >> i & 1]


def combine(rows, coeffs):
    return reduce(xor,(rows[i] for i in support(coeffs)),0)


def mask(bits):
    return sum(1 << i for i in bits)


def tape(word, missing):
    original = word['program']
    if missing is None:
        return list(enumerate(original))
    start, reg, donor, first, dest, _, lenders = LENSES[missing]
    assert original[start:start+3] == [['INIT',reg,510], ['ADD',reg,donor,510], ['MOVE',reg,510,1]]
    assert original[first] == ['ADD',dest,reg,1]
    for j in range(start+3, first):
        row = original[j]
        assert reg != row[1] and (row[0] not in ('ADD','SWAP') or reg != row[2])
    localized = [['INIT',reg,1]] + [['ADD',reg,j,1] for j in lenders]
    return (list(enumerate(original[:start])) + [(None,row) for row in localized]
            + list(enumerate(original[start+3:],start+3)))


def forward(word, tape, *, noise=False, oracle=None):
    """Each z_e is fresh. It modifies its MOVE payload before further free operations."""
    n = word['public']
    charts = dict(enumerate(word['start']))
    fields = {i:1<<i for i in charts}
    retired, carriers, top_history = [], [], []
    for i in fields:
        if charts[i] == 1:
            top_history.append(fields[i])
    for clock,(op,i,*args) in tape:
        if oracle is not None and clock == oracle[0]:
            _,reg,added = oracle
            assert charts[reg] == 1
            fields[reg] ^= added
        if op == 'INIT':
            assert i >= n and i not in fields
            charts[i],fields[i] = args[0],0
        elif op == 'ADD':
            j,chart = args
            assert charts[j] == charts[i] == chart
            fields[i] ^= fields[j]
        elif op == 'SWAP':
            j, = args
            charts[i], charts[j] = charts[j], charts[i]
            fields[i], fields[j] = fields[j], fields[i]
            if charts[j] == 1:
                top_history.append(fields[j])
        elif op == 'CLEAR':
            assert i >= n and charts.pop(i) == args[0]
            retired.append((i,args[0],bool(fields.pop(i))))
            continue
        else:
            assert op == 'MOVE' and charts[i] == args[0] and clock is not None
            if noise:
                fields[i] ^= 1 << (n + len(carriers))
            carriers.append(clock)
            charts[i] = args[1]
        if charts[i] == 1:
            top_history.append(fields[i])
    assert charts == dict(enumerate(word['final']))
    return [fields[i] for i in range(n)],carriers,retired,top_history


def verify(word, which, base, base_noisy, baseline_carriers, old_clears):
    n = word['public']
    selected = tape(word, which)
    new, carrier_clocks, retired, history = forward(word,selected)
    noisy, noisy_clocks, _, _ = forward(word,selected,noise=True)
    assert carrier_clocks == noisy_clocks and len(carrier_clocks) == 2802
    start, reg, _, first, _, probe, _ = LENSES[which]
    difference = [old ^ changed for old,changed in zip(base,new)]
    residuals = set(difference) - {0}
    assert len(residuals) == 1
    residual, = residuals
    signature = mask(i for i,v in enumerate(difference) if v)
    assert all(i >= 222 and (word['start'][i],word['final'][i]) == (0,1) for i in support(residual))
    assert all(word['final'][i] == 1 for i in support(signature))
    assert [residual.bit_count(),signature.bit_count()] == ([29,12] if which=='a' else [18,7])
    assert len(new) == n == 630 and rank(new) == 629
    # M is involutive, r is supported on original helper outputs fixed by M.
    ell = combine(base,residual)
    assert ell == residual and (ell & signature).bit_count() % 2 == 1
    collision = mask(i for i,row in enumerate(base) if (row & signature).bit_count() % 2)
    assert all((row & collision).bit_count() % 2 == 0 for row in new+history)
    assert rank(new+history) == 629
    assert combine(noisy,ell) == 0 and rank(noisy) == 629
    native_noise = combine(base_noisy,ell)
    assert native_noise & ((1<<n)-1) == residual
    native_hits = [baseline_carriers[i] for i in support(native_noise >> n)]
    assert start+2 in native_hits
    assert [(i,c) for i,c,_ in retired] == [(i,c) for i,c,_ in old_clears] and len(retired) == 3433
    # One original helper value brought to chart 1 restores each affected row.
    assert (word['start'][probe],word['final'][probe]) == (0,1) and signature >> probe & 1
    assert (new[probe] ^ (1 << probe)) == residual
    decoded = [v ^ ((new[probe] ^ (1<<probe)) if signature >> i & 1 else 0) for i,v in enumerate(new)]
    assert decoded == base
    # Oracle control at the first actual reader. The paid schedule supplies no such oracle.
    fixed,_,_,_ = forward(word,selected,oracle=(first,reg,residual))
    assert fixed == base
    fresh_bit = 1 << (n + len(carrier_clocks))
    perturbed,_,_,_ = forward(word,selected,noise=True,oracle=(first,reg,fresh_bit))
    assert combine(perturbed,ell) == fresh_bit
    assert [v ^ w for v,w in zip(noisy,perturbed)] == [fresh_bit if signature >> i & 1 else 0 for i in range(n)]
    return {'missing_native_move':start+2, 'retained_native_move':10036 if which=='a' else 10039,
            'residual_input_support':support(residual), 'affected_output_support':support(signature),
            'public_rank':rank(new), 'public_rank_with_all_ordinary_chart1_history':rank(new+history),
            'ordinary_chart1_history_rank':rank(history), 'formal_noise_columns':len(carrier_clocks),
            'formal_noise_output_rank':rank(noisy), 'formal_noise_left_parity':0,
            'baseline_controls_with_nonzero_noise_pairing':native_hits, 'terminal_helper_probe':probe,
            'oracle_control':{'before_native_clock':first,'owner':reg,'chart':1,'recovers_rows':len(fixed)},
            'retained_clears':len(retired),'nonzero_clears_on_arbitrary_inputs':sum(b for _,_,b in retired)}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('tape',type=Path);a=p.parse_args()
    path=a.tape/'strong-bit.json.gz' if a.tape.is_dir() else a.tape
    raw=path.read_bytes();expanded=decompress(raw)
    assert sha256(raw).hexdigest()==SHA and sha256(expanded).hexdigest()==EXPANDED_SHA
    word=json.loads(expanded);old=tape(word,None)
    base,base_clocks,clears,_=forward(word,old)
    assert base==[(1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(630)]
    base_noisy,noise_clocks,_,_=forward(word,old,noise=True)
    assert noise_clocks==base_clocks and len(base_clocks)==2803 and len(old)==39600
    print(json.dumps({'tape_sha256':SHA, **{f'omit_{which}':verify(word,which,base,base_noisy,base_clocks,clears)
                                          for which in ('a','b')}},indent=2,sort_keys=True))


if __name__=='__main__':main()
