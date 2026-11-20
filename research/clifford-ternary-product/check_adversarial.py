"""Audit character signs, sector order, literal products and signed-tail templates."""
from collections import Counter
from itertools import product
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from multiply import geometry, multiply_bits
from sectors import high_pairs, recognise_sectors, sector_product, control_sites
from contraction import joint, events
from operand import recognise_sparse
from templates import assemble, admit
from delivery import deliver

rng = Random(0x847459213)
seen = Counter()


def must(value, reason):
    if not value:
        raise AssertionError(reason)


def spread(word, sites):
    return sum(((word >> i) & 1)*3**i for i in range(sites))


def literal(value, length):
    return bytearray((value >> k) & 1 for k in range(length))


def val(bits):
    return sum(int(z) << k for k,z in enumerate(bits))


def low_bits(k, variant=0):
    low = bytearray(3**k)
    size = 1 << k
    rows = [(rng.randrange(size), rng.randrange(2)) for _ in range(rng.randrange(3))]
    w = rng.randrange(size)
    c = rng.randrange(2)
    pairs = [(i,j) for i in range(k) for j in range(i) if rng.randrange(2)]
    for x in range(size):
        keep = all((x&row).bit_count() % 2 == right for row,right in rows)
        q = (c + (w&x).bit_count() + sum(((x>>i)&(x>>j)&1) for i,j in pairs)) % 2
        digit = int(keep)*q
        if variant == 1: digit = 1
        if variant == 2: digit = 0
        low[spread(x,k)] = digit
    return low


def sector_literal(m):
    h = control_sites(m)
    k = m-h
    B = 3**k
    out = bytearray(3**m)
    for pref in range(1 << h):
        start = spread(pref,h)*B
        local = low_bits(k, rng.choices((0,1,2), (9,2,1))[0])
        out[start:start+B] = local
    return out


def rawcheck(a,b,expect=None):
    av,bv = bytes(a),bytes(b)
    ev = {}
    output = multiply_bits(a,b,evidence=ev)
    must(val(output) == val(a)*val(b), ("product",ev,len(a),len(b)))
    must(len(output)==max(1,(val(a)*val(b)).bit_length()), "noncanonical output")
    must(av==bytes(a) and bv==bytes(b), "input tape mutated")
    if expect is not None: must(ev["route"]==expect, ("admission",expect,ev))
    seen[ev["route"]] += 1
    return ev


def high_schedules():
    total=0
    for h in range(8):
        actual = []
        for i in range(3**h):
            pairs=list(high_pairs(i,h))
            must(all(spread(a,h)+spread(b,h)==i for a,b in pairs), "trit index")
            actual.extend(pairs)
        must(set(actual)==set(product(range(1<<h),repeat=2)), "pair coverage")
        must(len(actual)==4**h,"pair loss or duplicate")
        total+=len(actual)
    print("high ordered pairs",total)


def characters():
    count = 0
    for m in range(6):
        for trial in range(6):
            a,b=low_bits(m),low_bits(m)
            A,B=recognise_sparse(a,m),recognise_sparse(b,m)
            for sa,sb in product((False,True),repeat=2):
                def character(chart, flag):
                    if chart.zero: return 0
                    return sum(((-1)**int(flag and chart.value(x))) << spread(x,m)
                               for x in range(1<<m)
                               if all((x&k).bit_count()%2==v for k,v in chart.equations))
                reference=character(A,sa)*character(B,sb)*(-1 if sa != sb else 1)
                head=numer=0
                chart=joint(A,B,sa,sb)
                for event in events(chart,m,sa!=sb):
                    if event==">": head+=1
                    elif event=="<": head-=1
                    else: numer += (1 if event=="+" else -1) << head
                    must(0<=head<=3**m+m,"head excursion")
                must(numer==reference,"individual signed pass")
                must(head==3**m,"DFS did not restore exponent before finishing")
                count+=1
    print("individual character passes",count)


def sectors():
    pairs_total = 0
    for m in range(2,9):
        for trial in range(3 if m<=7 else 2):
            a,b=sector_literal(m),sector_literal(m)
            ac,bc = recognise_sectors(a,m),recognise_sectors(b,m)
            evidence = {}
            out=sector_product(ac,bc,stats=evidence)
            must(val(out)==val(a)*val(b),"sector-direct glue")
            must(evidence["pairs"]==4**control_sites(m),"pair accounting")
            pairs_total+=evidence["pairs"]
            rawcheck(a,b)
        if m>=4:
            # Upper limit of every individual block and mixed-high carry.
            h=control_sites(m)
            a=bytearray(3**m)
            for x in range(1<<m):a[spread(x,m)]=1
            ac=recognise_sectors(a,m)
            must(val(sector_product(ac,ac))==val(a)**2,"maximum low/high carries")
    print("sector-direct pairs",pairs_total)


def templates_and_failures():
    at=0
    for m in range(4,8):
        for trial in range(5):
            n=3**m-rng.randrange(3)
            _,u,c=geometry(n)
            rep=sum(1<<(i*u) for i in range(c))
            pa,pb=(rng.randrange(1,1<<u) for _ in range(2))
            # Real defects leave the free first template word untouched.
            fa=val(sector_literal(m))
            fb=val(sector_literal(m))
            signs=(1-2*(trial&1),1-2*((trial>>1)&1))
            A,B=pa*rep+signs[0]*(fa<<u),pb*rep+signs[1]*(fb<<u)
            if min(A,B)<0 or max(A,B)>=1<<n:continue
            evidence=rawcheck(literal(A,n), literal(B,n))
            must(evidence["route"]!="ordinary","sector plus signed template was missed")
            at+=1
        rawcheck(literal((1<<n)-1,n),literal(0,1))
    late=7
    h=control_sites(late)
    k=late-h
    B=3**k
    bad=bytearray(3**late)
    origin=spread((1<<h)-1,h)*B
    for j in range(1<<k):
        bad[origin+spread(j,k)]=int(j&7 != 7)
    must(recognise_sectors(bad,late) is None,"late nonlinear block accepted")
    rawcheck(bad,bytearray([1]))
    perturbed=sector_literal(late)
    perturbed[(3**h-1)*B]=1
    must(recognise_sectors(perturbed,late) is None,"late invalid high hole accepted")
    try: multiply_bits(bytes([1]), b"\x00"*3000 + b"\x02")
    except ValueError: pass
    else: raise AssertionError("bad byte accepted")
    print("dense template mutations/carry",at)


high_schedules()
characters()
sectors()
templates_and_failures()
print("routes",dict(seen))
print("PASS_INDEPENDENT_COMPLETE_CALLER")
