#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact discrete-curvature audit and conditional rank-fusion budget.

All power evaluations use grade_price.py's outward dyadic-root enclosures.
The baseline full binary invoice is rebuilt from the authenticated native word
and the pinned paired caller; this does not validate a changed physical caller.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
GRAPH_SHA = '74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'
GRAPH_RAW_SHA = 'b096d6df2a0c4688296b13ab0cfd50fec1c7dec732819c624ddd7a745a144b69'
CALLER_SHA = '757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b'
TARIFF_SHA = 'd1b15db0625855e18f64fecc87e037a635da3cd9413e55c22157ab5c51b6873c'
T = 1 - Q('0.00389046')
TARGET = {4:612, 8:14520, 15:444, 22:444, 29:444, 36:444,
          43:444, 50:444, 57:444, 64:444, 127:222}
PAID = {1:48972, 2:44892, 3:1980, 4:1512, 5:1044, 6:2916, 7:480,
        14:444, 21:444, 28:444, 35:444, 42:444, 49:444, 56:444}
EXPECTED_DIFFERENCES = [2149,2967,2539,2067,1554,1020,505]
RELAXED = Counter({8:505, 7:11, 6:100, 3:11})


def tariff():
    path = HERE / 'grade_price.py'
    assert sha256(path.read_bytes()).hexdigest() == TARIFF_SHA
    spec = importlib.util.spec_from_file_location('p104_curvature_tariff', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_graph(path):
    raw = Path(path).read_bytes()
    assert sha256(raw).hexdigest() == GRAPH_SHA
    expanded = gzip.decompress(raw)
    assert sha256(expanded).hexdigest() == GRAPH_RAW_SHA
    return json.loads(expanded)


def read_caller(path):
    raw = Path(path).read_bytes()
    assert sha256(raw).hexdigest() == CALLER_SHA
    return json.loads(gzip.decompress(raw))


def prices(ranks):
    power = tariff().price
    return {0:(Q(0),Q(0)), **{r:power(r,T) for r in sorted(set(ranks)) if r}}


def moment(hist, values):
    assert all(isinstance(n,int) and n >= 0 and r > 0 for r,n in hist.items())
    return tuple(sum(n*values[r][i] for r,n in hist.items()) for i in (0,1))


def raw_surplus(target, paid, values):
    a,b=moment(target,values); c,d=moment(paid,values)
    return a-d,b-c


def h_values(hist, maximum):
    return [sum(n*max(r-j,0) for r,n in hist.items()) for j in range(1,maximum)]


def validate_profiles(native, relaxed):
    assert all(isinstance(n,int) and n>=0 and 1<=r<=8 for h in (native,relaxed)
               for r,n in h.items())
    assert sum(r*n for r,n in native.items()) == sum(r*n for r,n in relaxed.items()) == 4750
    hn,hr=h_values(native,8),h_values(relaxed,8)
    differences=[y-x for x,y in zip(hn,hr)]
    assert differences == EXPECTED_DIFFERENCES
    return hn,hr,differences


def dimensions(g):
    return {int(c):s['dim'] for c,s in g['frames'].items()}


def reconstruct_invoice(g,caller):
    dim=dimensions(g); ports=caller['ports']; rank=caller['body_rank']
    local=sum(x[0]=='LOCAL' for x in caller['events'])
    assert (ports,rank,local)==(111,7,36)
    target,paid=Counter(),Counter()
    for row in caller['diagonal']:
        target[1+rank*len(row['stages'])]+=ports
    for src,dst in zip(g['start'][2*ports:],g['final'][2*ports:],strict=True):
        target[abs(dim[dst]-dim[src])]+=local
    for row in g['program']:
        if row[0]=='MOVE':paid[abs(dim[row[3]]-dim[row[2]])]+=local
    for row in caller['events']:
        if row[0]=='QUERY':paid[1]+=ports
        elif row[0]=='IDLE_ONE':paid[len(row[2])*rank]+=ports
    assert dict(target)==TARGET and dict(paid)==PAID
    assert sum(target.values())==18906 and sum(paid.values())==104904
    assert sum(r*n for r,n in paid.items())==285600
    return target,paid


def native_upward(g):
    dim=dimensions(g);h=Counter()
    for row in g['program']:
        if row[0]=='MOVE':
            diff=dim[row[3]]-dim[row[2]]
            if diff>0:h[diff]+=1
    return h


def ordered_contacts(g):
    """Original chronological chart incidences only; not necessarily usable."""
    dim=dimensions(g);past=defaultdict(list);counts=Counter();fours=[]
    for clock,row in enumerate(g['program']):
        if row[0]!='MOVE':continue
        _,owner,src,dst=row;grade=dim[dst]-dim[src]
        if grade<=0:continue
        for t0,o0,s0,g0 in past[src]:
            if g0+grade>8:continue
            counts[(g0,grade)]+=1
            if (g0,grade)==(4,4):
                fours.append({'first_clock':t0,'first_owner':o0,'first_source':s0,
                              'hinge_chart':src,'second_clock':clock,
                              'second_owner':owner,'second_destination':dst})
        past[dst].append((clock,owner,src,grade))
    assert counts[(2,2)]==4227 and counts[(4,4)]==1
    assert fours == [{'first_clock':7112,'first_owner':2241,'first_source':0,
                      'hinge_chart':509,'second_clock':7210,'second_owner':2252,
                      'second_destination':1}]
    return counts,fours


def text_bounds(pair, digits=18):
    scale=10**digits
    def fmt(n):
        sign='-' if n<0 else '';n=abs(n)
        return f'{sign}{n//scale}.{n%scale:0{digits}d}'
    return [fmt((pair[0]*scale).__floor__()),fmt((pair[1]*scale).__ceil__())]


def overlaps(a,b):
    return max(a[0],b[0]) <= min(a[1],b[1])


def check(graph_path,caller_path):
    assert not sys.flags.optimize
    graph=read_graph(graph_path);caller=read_caller(caller_path)
    native=native_upward(graph)
    hn,hr,diff=validate_profiles(native,RELAXED)
    target,paid=reconstruct_invoice(graph,caller)
    counts,fours=ordered_contacts(graph)
    vals=prices(set(range(1,58))|set(target)|set(paid))
    w={j:(2*vals[j][0]-vals[j-1][1]-vals[j+1][1],
          2*vals[j][1]-vals[j-1][0]-vals[j+1][0]) for j in range(1,57)}
    assert all(a>0 and a<=b for a,b in w.values())
    # Check the discrete identity on every unit rank through the full paid
    # caller's maximum rank 56; linearity then covers every integer histogram.
    for r in range(1,57):
        lo=Q(r)-sum((r-j)*w[j][1] for j in range(1,r))
        hi=Q(r)-sum((r-j)*w[j][0] for j in range(1,r))
        assert overlaps((lo,hi),vals[r])
    components=[(n*w[j][0],n*w[j][1]) for j,n in enumerate(diff,1)]
    total=(sum(x[0] for x in components),sum(x[1] for x in components))
    no=moment(native,vals); rel=moment(RELAXED,vals)
    assert overlaps(total,(no[0]-rel[1],no[1]-rel[0]))
    assert Q('25.059996283598193') < total[1] and total[0] < Q('25.059996283598194')
    hp=h_values(paid,56);base_rank=sum(r*n for r,n in paid.items())
    full_identity=(Q(base_rank)-sum(hp[j-1]*w[j][1] for j in range(1,56)),
                   Q(base_rank)-sum(hp[j-1]*w[j][0] for j in range(1,56)))
    assert overlaps(full_identity,moment(paid,vals))
    # Exact intervals certify the best sum<=8 fusion at the target. The
    # all-t analytic statement follows separately from concavity/homogeneity.
    def fusion(a,b):
        return (vals[a][0]+vals[b][0]-vals[a+b][1],
                vals[a][1]+vals[b][1]-vals[a+b][0])
    best=fusion(4,4)
    for a in range(1,8):
        for b in range(1,9-a):
            if (a,b)!=(4,4):assert fusion(a,b)[1]<best[0]
    baseline=raw_surplus(target,paid,vals)
    previous=(Q('-0.132405116496822168'),Q('-0.132405116496822167'))
    assert overlaps(baseline,previous)
    assert baseline[1]+6*best[1]<0 and baseline[0]+7*best[0]>0
    def changed(m):
        result=paid.copy();result[4]-=2*m;result[8]+=m
        assert min(result.values())>=0
        assert sum(r*n for r,n in result.items())==base_rank
        return raw_surplus(target,result,vals)
    six,seven=changed(6),changed(7)
    assert six[1]<0 and seven[0]>0
    assert overlaps(six,(baseline[0]+6*best[0],baseline[1]+6*best[1]))
    assert overlaps(seven,(baseline[0]+7*best[0],baseline[1]+7*best[1]))
    return {
      'source_graph_sha256':GRAPH_SHA,'source_caller_sha256':CALLER_SHA,
      'target_kappa':'0.00389046','exponent_t':str(T),
      'upward_rank_sum':4750,'native_h':hn,'relaxed_h':hr,'relaxed_minus_native_h':diff,
      'component_discount_enclosures':[text_bounds(x) for x in components],
      'total_relaxation_gap':text_bounds(total),
      'maximum_rank_sum_8_fusion':{'ranks':[4,4],'saving':text_bounds(best)},
      'full_binary_caller_paid_count':sum(paid.values()),'full_binary_caller_rank_sum':base_rank,
      'conditional_baseline_raw_surplus':text_bounds(baseline),
      'six_best_fusions_raw_surplus':text_bounds(six),
      'seven_best_fusions_raw_surplus':text_bounds(seven),
      'original_ordered_incidence_counts':{'4+4':counts[(4,4)],'2+2':counts[(2,2)]},
      'only_4_plus_4_original_incidence_pair':fours[0],
      'scope':'Price and chronological chart-incidence only; no readable fusion, physical supplier, powered outer test, or kappa improvement claimed.'
    }


if __name__=='__main__':
    print(json.dumps(check(sys.argv[1],sys.argv[2]),indent=2,sort_keys=True))
