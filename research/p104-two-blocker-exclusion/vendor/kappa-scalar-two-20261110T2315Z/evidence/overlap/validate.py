"""Replay all overlap packet placements on their complete normalized intervals."""
from collections import Counter
import json
from pathlib import Path
import sys

from overlap import choices_overlap, two

sys.path.insert(0,str(Path(__file__).parents[1]/'planner'))
from validate_free import exact_rows, inventory, local_sequences, read_word


def run(path):
    w=read_word(path)
    raw,scalar,child=inventory(w)
    stats=Counter()
    rows=[]
    for i,bs,cut,ops,pairs,cuts in choices_overlap(w,raw,scalar,child,stats):
        before,after=local_sequences(w['program'],i,ops,cuts)
        target=exact_rows(before)
        assert target==exact_rows(after)
        _,bad=local_sequences(w['program'],i,ops[:-1],cuts[:-1])
        assert target!=exact_rows(bad)
        rows.append(dict(add=i,blockers=bs,cut=cut,ops=ops,pairs=pairs,interval=len(before)))
    assert stats['overlapping plans']==7
    return dict(source_word_sha256=two.WORD_SHA,counts=stats,plans=rows)


if __name__=='__main__':
    print(json.dumps(run(Path(sys.argv[1])),indent=2,sort_keys=True))
