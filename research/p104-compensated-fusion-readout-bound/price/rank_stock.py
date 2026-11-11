"""Directed stock price for one nested paid public MOVE pair on exact #7334."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations_with_replacement
from json import dumps, loads
from pathlib import Path
from runpy import run_path

PINS = {
    'READBACK.json':'337668788fb39ec9575887f9c5faf438a880471f78d936357dabf7deeac5de82',
    'receipts/NATIVE-RESULT.json':'c6d1b00a83185ab0062397b363258b1f3f6685d755e9c1d4f7d3e7e511240812',
    'receipts/construct.py':'ecb39578063d7f09153a85370a3b9bb7cbf8b36ff9891033a1cce7a2fe7f7fda',
    'dependencies/7298/pricing.py':'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
    'dependencies/round41/RESULT.json':'1b993aa8c66ffce5d2d9f13cafae320c62230722d599d251fa61afc6534b1bc7',
}


def unique(items):
    doc=dict(items)
    if len(doc)!=len(items):
        raise ValueError('duplicate JSON key')
    return doc


def hist(row):
    return Counter({int(rank):n for rank,n in row.items()})


def main():
    assert __debug__
    files={}
    for key,digest in PINS.items():
        raw=Path(key).read_bytes()
        assert sha256(raw).hexdigest()==digest
        files[key]=raw
    read=lambda key: loads(files[key],object_pairs_hook=unique)
    current=read('READBACK.json')
    assert current['head']=='aaeec8c0acf01e99a5f331ef363a698d9c084ace'
    native=read('receipts/NATIVE-RESULT.json')['native']
    owned=read('dependencies/round41/RESULT.json')
    old_owned=hist(owned['paid_owned_histogram'])
    assert owned['scope_exhausted'] and sum(old_owned.values())==47
    # The exact #7334 constructor retimes public participants, preserves existing owned MOVEs,
    # and adds only a stationary owned lifetime. #7314 likewise preserved these owned MOVEs.
    public=hist(native['paid'])-old_owned
    assert sum(public.values())==6232 and sum(native['helpers'].values())==1101
    paid,targets=(hist(current[key]) for key in ('paid','targets'))
    signed=targets.copy(); signed.subtract(paid)
    k=Q(current['new_raw_interval'][1]); cost=run_path('dependencies/7298/pricing.py')['cost']
    assert cost(signed,k)[1]<0
    prices={}
    for a,b in combinations_with_replacement(sorted(public),2):
        if a+b>9:
            continue
        d=Counter({a+b:-17}); d[a]+=17; d[b]+=17
        candidate=signed.copy(); candidate.update(d)
        new_paid=paid.copy(); new_paid.subtract(d)
        assert sum(new_paid.values())==110502 and all(n>0 for n in new_paid.values())
        assert sum(r*n for r,n in candidate.items())==1424
        with_extra=candidate.copy(); with_extra[1]-=1
        credit,margin,extra=(cost(row,k) for row in (d,candidate,with_extra))
        assert 0<credit[0]<=credit[1]<1 and margin[0]>0>extra[1]
        prices[f'{a}+{b}']={'ranks':[a,b], 'paid_delta':{r:-n for r,n in d.items()},
                            'credit':list(map(str,credit)),'complete_margin':list(map(str,margin)),
                            'margin_with_extra_rank_one':list(map(str,extra))}
    upper=lambda a,b: Q(prices[f'{min(a,b)}+{max(a,b)}']['credit'][1])
    one=max(upper(*row['ranks']) for row in prices.values())
    assert one==upper(4,5)
    capacity=sum(n*upper(r,9-r) for r,n in public.items())/2
    doc={'head':current['head'],'word_git_blob':'73f43007192eb5a38eb5abb591b871df3e52c7cd',
         'admission':'scientific admission pending at preflight; price is conditional on exact #7334 passing',
         'input_sha256':PINS,'crossing_upper':str(k),'public_paid_histogram':dict(public),
         'public_paid_moves':sum(public.values()),'owned_paid_histogram':dict(old_owned),
         'disjoint_move_pair_count_upper':sum(public.values())//2,'public_helper_count':1101,
         'whole_move_capacity_optimistic_upper':str(capacity),
         'one_per_public_helper_optimistic_upper':str(min(capacity,1101*one)),
         'one_edit_optimistic_upper':str(one),'rank_prices':prices,'old_complete_paid':dict(paid),
         'complete_targets':dict(targets),'old_margin':list(map(str,cost(signed,k))),
         'scope':'Predecode price only. Pair arithmetic grants all ordinary and physical costs free; each original paid MOVE contributes at most once.'}
    print(dumps(doc,indent=2,sort_keys=True))


if __name__=='__main__':
    main()
