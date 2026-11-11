"""Bounded first-read common-lift gate using the pinned contact index."""
from argparse import ArgumentParser
from bisect import bisect_right
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from time import monotonic

from runpy import run_path

INDEX = run_path(str(Path(__file__).with_name('contact_index.py')))
WORD_SHA = INDEX['WORD_SHA']
build, helper_roles, spans, word = (INDEX[key] for key in ('build','helper_roles','spans','word'))

HEAD = '9d0119eb12fbd9fa534b48cd37b68e7099757b91'
EXCLUDED = {863,1355,1568}


def classify(w,index,helpers,deadline):
    stock = set(helpers)
    t = w['program']
    frames = w['frames']
    span = spans(w)
    rows = []
    roles = index['roles']
    for h in helpers:
        if len(rows) >= 1101 or monotonic() >= deadline:
            break
        a,z = w['initial'][h],w['final'][h]
        rank = len(frames[z])-len(frames[a])
        assert span(a) < span(z)
        own = roles.get(str(h),[])
        item = {'h':h,'rank':rank}
        if h in EXCLUDED:
            reason = 'excluded_helper'
        elif rank < 2:
            reason = 'zero_residual_after_rank_one'
        elif not own or own[0][1] != 'source' or t[own[0][0]][0] != 'ADD':
            reason = 'first_contact_not_source_add'
        else:
            add = own[0][0]
            _,g,s,coef,chart = t[add]
            assert s == h and chart == a and Fraction(coef)
            item.update({'g':g,'add':add,'start':a,'end':z})
            if g in EXCLUDED or g not in stock:
                reason = 'partner_not_unprotected_productive_helper'
            else:
                other = roles[str(g)]
                where = bisect_right(other,[add,'source'])
                assert other[where-1] == [add,'destination']
                hnext = own[1][0] if len(own)>1 else None
                gnext = other[where][0] if where < len(other) else None
                item.update({'h_next':hnext,'g_next':gnext})
                he = t[hnext] if hnext is not None else None
                ge = t[gnext] if gnext is not None else None
                if he is None or he[0] != 'MOVE':
                    reason = 'helper_next_not_move'
                elif ge is None or ge[0] != 'MOVE':
                    reason = 'partner_next_not_move'
                else:
                    _,rh,ah,c,oh = he
                    _,rg,ag,d,og = ge
                    assert (rh,rg,ah,ag,oh,og) == (h,g,a,a,False,False)
                    item.update({'helper_move':hnext,'partner_move':gnext,'lift':c,'partner_lift':d})
                    if c != d:
                        reason = 'different_destinations'
                    elif len(frames[c])-len(frames[a]) != 1 or not span(a) < span(c) < span(z):
                        reason = 'nonunit_or_no_positive_residual'
                    else:
                        reason = 'survivor'
        rows.append({**item,'status':reason})
    return rows


def controls():
    tape = [['ADD',1,0,'-3/2',0],['MOVE',1,0,1,False],['MOVE',0,0,1,False],['MOVE',0,1,2,False]]
    sample = {'public':2,'initial':[0,0],'final':[2,1],'frames':[[],[1],[1,2],[2]],'program':tape}
    def first(w):
        idx = loads(dumps(build(w,float('inf'))))
        return classify(w,idx,[0,1],float('inf'))[0]['status']
    assert first(sample) == 'survivor'
    earlier = sample | {'program':[tape[0],['ADD',0,1,'2',0],*tape[1:]]}
    assert first(earlier) == 'helper_next_not_move'
    mismatch = sample | {'final':[2,3],'program':[tape[0],['MOVE',1,0,3,False],*tape[2:]]}
    assert first(mismatch) == 'different_destinations'

    # Two arbitrary, distinct dirty chart arrays and an exact signed map.
    def signed(v):
        return (-v[1],v[0])
    def add(g,h):
        return tuple(x-Fraction(3,2)*y for x,y in zip(g,h,strict=True))
    g,h = (Fraction(4),Fraction(5,7)),(Fraction(2,3),Fraction(8))
    assert signed(add(g,h)) == add(signed(g),signed(h))
    return ['same_lift_positive','intervening_read_blocks','different_lift_blocks','signed_dirty_arrays']


if __name__ == '__main__':
    p = ArgumentParser(description=__doc__)
    p.add_argument('root',type=Path)
    p.add_argument('--price-sha',required=True)
    p.add_argument('--index-sha',required=True)
    a = p.parse_args()
    start = monotonic()
    price = (a.root/'PRICE.json').read_bytes()
    idx = (a.root/'INDEX.json').read_bytes()
    assert sha256(price).hexdigest() == a.price_sha
    assert sha256(idx).hexdigest() == a.index_sha
    frozen,index = loads(price),loads(idx)
    assert frozen['head'] == HEAD and frozen['input_sha256']['inputs/7314/WORD.json.gz'] == WORD_SHA
    assert index['word_sha256'] == WORD_SHA and index['complete'] and index['events_visited'] == 76461
    w = word(a.root)
    helpers = helper_roles(w)
    check = controls()
    rows = classify(w,index,helpers,start+18)
    assert len(helpers) == 1101
    if len(rows) == len(helpers):
        assert Counter(str(row['rank']) for row in rows) == frozen['helpers']
    print(dumps({'head':HEAD,'price_sha256':a.price_sha,'index_sha256':a.index_sha,'events':index['events_visited'],
                 'visited':len(rows),'counts':dict(Counter(r['status'] for r in rows)),
                 'survivors':[r for r in rows if r['status']=='survivor'],
                 'unvisited':helpers[len(rows):],'controls':check,'rows':rows},sort_keys=True,indent=2))
