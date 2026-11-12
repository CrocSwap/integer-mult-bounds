"""Compare the compressed Cartesian iterator to every joint-cut representative."""
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

from all_terms import choices_all
from free_term import choices_free, two
from validate import exact_rows, inventory, read_word
from validate_free import local_sequences


def run(path):
    w = read_word(path)
    raw, scalar, child = inventory(w)
    joint = {(i,bs,cut): [{pair} for pair in pairs]
             for i,bs,cut,_,pairs in two.choices(w,raw,scalar,child)}
    for i,bs,cut,_,pairs,cuts in choices_free(w,raw,scalar,child):
        term, = [j for j,k in enumerate(cuts) if k != cut]
        joint[i,bs,cut][term].add(pairs[term])
    exhaustive = {(i,bs,pairs) for (i,bs,_), options in joint.items() for pairs in product(*options)}
    actual, max_spread, counts = set(), {}, Counter()
    for i,bs,anchor,ops,pairs,cuts in choices_all(w,raw,scalar,child,counts):
        key = i,bs,pairs
        assert key not in actual
        actual.add(key)
        distinct = len(set(cuts))
        category = ('later' if bs[0]>i else 'earlier',distinct)
        spread = max(cuts)-min(cuts)
        if category not in max_spread or spread>max_spread[category][0]:
            max_spread[category] = spread,i,bs,anchor,ops,cuts
    assert actual==exhaustive
    controls=[]
    for (direction,distinct),(spread,i,bs,anchor,ops,cuts) in sorted(max_spread.items()):
        if distinct<2:
            continue
        before,after=local_sequences(w['program'],i,ops,cuts)
        assert exact_rows(before)==exact_rows(after), (i,bs,cuts)
        controls.append(dict(direction=direction,distinct_cuts=distinct,add=i,blockers=bs,
                             anchor=anchor,ops=ops,cuts=cuts,spread=spread,original_events=len(before)))
    assert len(controls)==6
    digest=sha256(json.dumps(sorted(actual),separators=(',',':')).encode()).hexdigest()
    return dict(status='PASS_EXACT_ALL_TERM_PLANNER',source_word_sha256=two.WORD_SHA,
                counts=counts,all_raw_product_sha256=digest,exact_spread_controls=controls)


if __name__=='__main__':
    print(json.dumps(run(Path(sys.argv[1])),indent=2,sort_keys=True))
