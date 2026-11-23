"""Replay the strict frame-family price, two-vertex counts and neutral native controls."""

from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from itertools import combinations
from math import isqrt
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from geometry import dimension, endpoint_options, finite_control, flags, space_count, space_mask
import gaussian_review as review

UNIT = 2**192
TARGET = Q(39, 10000)


def frozen(name, expected):
    raw = gzip.decompress((HERE / name).read_bytes())
    if sha256(raw).hexdigest() != expected:
        raise ValueError(f"Frozen input differs at {name}")
    return json.loads(raw)


@cache
def tariff(rank):
    """Enclose rank^(1−TARGET) using successive directed square roots."""
    assert rank > 0
    root_lo = root_hi = rank * UNIT
    prod_lo = prod_hi = UNIT
    rem = TARGET
    for _ in range(152):
        root_lo = isqrt(root_lo * UNIT)
        root_hi = 1 + isqrt(root_hi * UNIT - 1)
        rem *= 2
        if rem >= 1:
            rem -= 1
            prod_lo = prod_lo * root_lo // UNIT
            prod_hi = -(-prod_hi * root_hi // UNIT)
    if rem:
        prod_hi = -(-prod_hi * root_hi // UNIT)
    numerator = rank * UNIT**2
    return numerator // prod_hi, -(-numerator // prod_lo)


def bounds(hist):
    low = high = 0
    for rank, count in hist.items():
        a, b = tariff(rank)
        low += min(count*a, count*b)
        high += max(count*a, count*b)
    return low, high


def classify(hist):
    low, high = bounds(hist)
    if high < 0:
        return "worse"
    if low > 0:
        return "gain"
    if low == high == 0:
        return "tie"
    raise ArithmeticError("An interval straddled zero")


def source_graph(g):
    starts = defaultdict(Counter)
    ends = defaultdict(Counter)
    paid = defaultdict(Counter)
    ranks = list(map(len,g["frames"]))
    spaces = list(map(space_mask,g["frames"]))
    main = set(g["main_roles"])
    assert len(main) == 400 and len(g["initial"]) == len(g["final"]) == 1291
    assert len(g["paid_schedule"]) == len(g["moves"]) == len(set(g["paid_schedule"])) == 5674
    assert {k for k,a,b in g["moves"]} == set(g["paid_schedule"])
    assert (g["weights"],g["scales"],g["splits"],g["native_calls"]) == ([5,451],[1,2],1008,48)
    static_paid = Counter(dict(g["fixed_paid"]))
    productive = Counter(dict(g["fixed_productive"]))
    gross = static_paid.copy()
    for _,a,b in g["moves"]:
        assert spaces[a] != spaces[b] and (spaces[a] & spaces[b]) in (spaces[a],spaces[b])
        paid[a][b] += 1
        paid[b][a] += 1
        gross[abs(ranks[a]-ranks[b])] += 48
    for i,(a,b) in enumerate(zip(g["initial"],g["final"],strict=True)):
        if i not in main:
            assert spaces[a] != spaces[b] and spaces[a] & spaces[b] == spaces[a]
            starts[a][b] += 1
            ends[b][a] += 1
            productive[ranks[b]-ranks[a]] += 48
    anchors = {g[key][i] for key in ("initial","final") for i in main}
    helper_sites = (set(starts)|set(ends))-anchors
    internal = set(paid) - set(g["initial"]) - set(g["final"])
    assert not internal & helper_sites and len(anchors) == 210 and len(helper_sites) == 62
    assert len(internal) == 706 and len(paid)==978
    return paid,starts,ends,ranks,spaces,internal,helper_sites,gross,productive


def single_delta(i,d,paid,starts,ends,ranks):
    delta = Counter()
    for h in set(paid[i])|set(starts[i])|set(ends[i]):
        weight = starts[i][h] + ends[i][h] - paid[i][h]
        delta[abs(d-ranks[h])] += weight
        delta[abs(ranks[i]-ranks[h])] -= weight
    return delta


def single_prices(sites, paid, starts, ends, ranks, spaces):
    per_site = {}
    feasible = different_dims = changes = 0
    closest = None
    neutral_frames = {}
    for i in sites:
        count = Counter()
        original = 0
        for option in endpoint_options(i,None,paid,starts,ends,ranks,spaces):
            d = option[0]
            number = space_count(option)
            feasible += number
            if d == ranks[i]:
                original += number
                continue
            different_dims += 1
            changes += number
            hist = single_delta(i,d,paid,starts,ends,ranks)
            result = classify(hist)
            count[result] += number
            if result == "tie":
                assert number == 1
                unique = option[1] if dimension(option[1])==d else option[2]
                assert dimension(unique)==d
                neutral_frames[i] = unique
            if result == "worse":
                lo, hi = bounds(hist)
                if closest is None or hi > closest[0]:
                    closest = (hi,i,d,lo)
        assert original == 1
        per_site[i] = count
    return per_site,neutral_frames,(feasible,different_dims,changes),closest


def pair_prices(internal, paid, starts, ends, ranks, spaces, singles):
    adjacent = {(i,j) for i in internal for j in paid[i] if i<j and j in internal}
    all_eligible, exclusive = Counter(),Counter()
    dimension_cases = Counter()
    for i,j in adjacent:
        peers_i = [(ranks[h],n) for h,n in paid[i].items() if h!=j]
        peers_j = [(ranks[h],n) for h,n in paid[j].items() if h!=i]
        shared = paid[i][j]
        def paid_bins(u,v):
            result=Counter({abs(u-v):shared})
            for h,n in peers_i:
                result[abs(u-h)] += n
            for h,n in peers_j:
                result[abs(v-h)] += n
            return result
        old = paid_bins(ranks[i],ranks[j])
        options_i=endpoint_options(i,j,paid,starts,ends,ranks,spaces)
        options_j=endpoint_options(j,i,paid,starts,ends,ranks,spaces)
        row=Counter()
        for a in options_i:
            for b in options_j:
                u,v=a[0],b[0]
                if u==v:
                    continue
                number=flags(a,b) if u<v else flags(b,a)
                if number:
                    difference=old.copy()
                    difference.subtract(paid_bins(u,v))
                    kind=classify(difference)
                    dimension_cases[kind]+=1
                    row[kind]+=number
        all_eligible.update(row)
        row["tie"]-=1
        row.subtract(singles[i])
        row.subtract(singles[j])
        assert all(n>=0 for n in row.values())
        exclusive.update(row)
    distant=Counter()
    for i,j in combinations(sorted(internal),2):
        if (i,j) in adjacent:
            continue
        a,b=singles[i],singles[j]
        assert not a["gain"] and not b["gain"]
        tie=a["tie"]*b["tie"]
        distant["tie"]+=tie
        distant["worse"]+=sum(a.values())*sum(b.values())-tie
    return len(adjacent),dict(dimension_cases),dict(all_eligible),exclusive,distant


def neutral_actions(g, factors, neutral_frames, paid, spaces):
    replacements=dict(factors["substitutions"])
    assert set(replacements)==set(neutral_frames)
    frames=g["frames"].copy()
    for i,basis in replacements.items():
        assert space_mask(basis)==neutral_frames[i]
        assert spaces[i]!=neutral_frames[i] and not set(paid[i])&set(replacements)
        frames[i]=basis
    touched={(a,b) for _,a,b in g["moves"] if a in replacements or b in replacements}
    records={(a,b):r for a,b,r in factors["pairs"]}
    assert set(records)==touched and len(touched)==len(factors["pairs"])==72
    for (a,b),record in records.items():
        assert record["rank"]==abs(len(frames[b])-len(frames[a]))>0
        actual=review.recipe(record)
        expected=review.adjoint(review.frame(frames[a],9))+review.frame(frames[b],9)
        review.equal(actual,expected,"strict frame transfer")
        if [a,b,record["rank"]]==factors["full_replay"]["all_column_control"]:
            for basis in range(512):
                assert review.state(actual,basis)==review.state(expected,basis)
            shifted=actual+(("phase",1),)
            assert review.tableau(shifted)==review.tableau(expected) and review.state(shifted)!=review.state(expected)
    assert factors["full_replay"]["all_column_control"]==[292,1032,3]
    assert sum(a in replacements or b in replacements for _,a,b in g["moves"])==104


def main():
    expected=json.loads((HERE/"RESULT.json").read_bytes())
    g=frozen("source-projection.json.gz",expected["projection_sha256"])
    factors=frozen("neutral-factors.json.gz",expected["factors_sha256"])
    assert g["complete_word_sha256"] == expected["word_sha256"]
    assert g["complete_layout_sha256"] == expected["layout_sha256"]
    paid,starts,ends,ranks,spaces,internal,helpers,P,T=source_graph(g)
    si,nf,sc,_=single_prices(internal,paid,starts,ends,ranks,spaces)
    sh,hn,hc,hbest=single_prices(helpers,paid,starts,ends,ranks,spaces)
    assert not hn and sc==(79413,3041,78707) and hc==(8793,171,8731)
    assert hbest[1:3]==(1094,6) and Q(hbest[0],UNIT)<Q("-0.00843834771094")
    adj,dc,ac,both,dist=pair_prices(internal,paid,starts,ends,ranks,spaces,si)
    singles=sum(si.values(),Counter())+sum(sh.values(),Counter())
    total=singles+both+dist+Counter(tie=1)
    assert dc=={"worse":28683,"tie":1312} and ac=={"worse":3282715,"tie":1312}
    assert adj==1244 and both==Counter(worse=3114632) and dist==Counter(worse=3080789878,tie=153)
    assert singles==Counter(worse=87420,tie=18)
    assert dict(total)==expected["distinct_states"] and len(nf)==18
    assert finite_control()==5956
    # Even the largest two touched paid stars leave enough real unit jobs for
    # the source's fixed 1008 splits. The extra paid split tariff is constant.
    max_degree=max(sum(paid[i].values()) for i in internal|helpers)
    assert P[1]-2*48*max_degree>=1008
    raw=T.copy()
    raw.subtract(P)
    lo,hi=(Q(x,UNIT) for x in bounds(raw))
    assert list(map(str,(lo,hi)))==expected["raw_margin"]
    assert classify({1: 1})=="gain" and classify({1: -1})=="worse"
    # The signed helper endpoints on chart 1094 contribute to both tariffs.
    old_paid_only=single_delta(1094,6,paid,defaultdict(Counter),defaultdict(Counter),ranks)
    full=single_delta(1094,6,paid,starts,ends,ranks)
    assert dict(+full)!=dict(+old_paid_only) and bounds(full)!=(0,0)
    zlo,zhi=(Q(x,UNIT) for x in tariff(2))
    wlo,whi=5+451*zlo,5+451*zhi
    weighted_lo=whi*lo-5*1008*(2/zlo-1)
    weighted_hi=wlo*hi-5*1008*(2/zhi-1)
    assert Q("-1406.078231652773")<weighted_lo<=weighted_hi<Q("-1406.078231652772")
    assert wlo>0 and hi<0
    neutral_actions(g,factors,nf,paid,spaces)
    print("PASS_STRICT_FRAME_PRICE",dict(total),"raw and two-type deficit at 39/10000",
          "helper 1094 closest", "512 exact columns and 72 signed pairs")


if __name__=="__main__":
    main()
