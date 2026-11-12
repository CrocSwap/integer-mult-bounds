"""One global main-terminal stock map, granting all old and virtual clocks."""
from collections import Counter,defaultdict
from fractions import Fraction as Q
from functools import cache
import gzip
from hashlib import sha256
from importlib.util import module_from_spec,spec_from_file_location
import json
from pathlib import Path
import sys
from time import monotonic

PINS={
    "research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz":"51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78",
    "research/paired-query-only-bit/independent/interval_gate.py":"8dc2bc4c64cba3f83c664373984a075f1a14b4d53958084091345c8cab189dec",
    "research/paired-query-only-bit/EFREE-RESULT.json":"a46b6c6040f75184cab5467656811ad988c216e3bc8e44d595a5015b6e49620b",
}


def read(root,key):
    b=(root/key).read_bytes()
    if sha256(b).hexdigest()!=PINS[key]:
        raise ValueError(f"SHA-256 mismatch: {key}")
    return b


def check_time(deadline):
    if monotonic()>=deadline:
        raise TimeoutError("one stock map exceeded budget")


def rref(vectors):
    basis={}
    for x in vectors:
        v=list(x)
        for p,u in sorted(basis.items()):
            if v[p]:
                c=v[p]
                v=[a-c*b for a,b in zip(v,u,strict=True)]
        p=next((i for i,a in enumerate(v) if a),None)
        if p is None:
            continue
        u=[a/v[p] for a in v]
        for j,b in list(basis.items()):
            if b[p]:
                basis[j]=[a-b[p]*z for a,z in zip(b,u,strict=True)]
        basis[p]=u
    return tuple(tuple(basis[p]) for p in sorted(basis))


@cache
def join(a,b):
    return rref(a+b)


def positions(bits):
    out=[]
    while bits:
        p=bits&-bits
        out.append(p.bit_length()-1)
        bits^=p
    return out


def sweep(w,ranks,pivots,deadline,reverse=False):
    n=w["public"]
    frames=(w["final"] if reverse else w["start"])+[None]*w["owned_fields"]
    rows=[1<<i for i in range(n)]+[0]*w["owned_fields"]
    chart=defaultdict(set)
    bank={}
    touches=defaultdict(list)

    def capture(j):
        f=frames[j]
        if f is not None and ranks[f]==7 and rows[j]:
            chart[f].add(rows[j])

    for i in range(len(rows)):
        capture(i)
    events=list(enumerate(w["program"]))
    for i,(op,j,*a) in (reversed(events) if reverse else events):
        if i%1024==0:
            check_time(deadline)
        touched=(j,a[0]) if op in ("ADD","SWAP") else (j,)
        if not reverse:
            for k in touched:
                touches[k].append(i)
        if i in pivots:
            assert op=="MOVE" and a[1]==1 and rows[j]
            bank[i]=rows[j]
        changed=(j,)
        if op=="MOVE":
            old,new=(a[1],a[0]) if reverse else a
            assert frames[j]==old
            frames[j]=new
        elif op=="ADD":
            k,f=a
            assert frames[j]==frames[k]==f
            dest,src=(k,j) if reverse else (j,k)
            rows[dest]^=rows[src]
            changed=(dest,)
        elif op=="SWAP":
            k=a[0]
            rows[j],rows[k]=rows[k],rows[j]
            frames[j],frames[k]=frames[k],frames[j]
            changed=(j,k)
        else:
            assert op in ("INIT","CLEAR")
            active=(op=="CLEAR") if reverse else (op=="INIT")
            assert (frames[j] is None)==active
            assert active or frames[j]==a[0]
            frames[j]=a[0] if active else None
            rows[j]=0
        for k in changed:
            capture(k)
    expected=[1<<j for j in range(n)]+[0]*w["owned_fields"]
    for j in range(111):
        if reverse:
            expected[j]^=1<<(111+j)
        else:
            expected[111+j]^=1<<j
    assert rows==expected and set(bank)==pivots
    assert frames==(w["start"] if reverse else w["final"])+[None]*w["owned_fields"]
    return chart,bank,touches


def row_reduce(rows,mask):
    pivots={}
    kernel=[]
    for v in rows:
        while v&mask:
            bit=(v&mask)&-(v&mask)
            if bit not in pivots:
                pivots[bit]=v
                break
            v^=pivots[bit]
        else:
            if v:
                kernel.append(v)
    return pivots,kernel


def pure(rows,group):
    _,k=row_reduce(rows,~group)
    b,_=row_reduce(k,group)
    return list(b.values())


def nonzero_pair(a,b):
    return any((u&v).bit_count()%2 for u in a for v in b)


def pairing_rank(a,b):
    values=[sum(((x&y).bit_count()%2)<<j for j,y in enumerate(b)) for x in a]
    p,_=row_reduce(values,-1)
    return len(p)


def compulsory(pivot,others,group):
    outside=~group
    pivots,k=row_reduce(others,outside)
    v=pivot
    while v&outside:
        bit=(v&outside)&-(v&outside)
        if bit not in pivots:
            d=bit
            for a,x in sorted(pivots.items(),reverse=True):
                if (x&d).bit_count()%2:
                    d|=a
            assert not d&group and (pivot&d).bit_count()%2
            assert all(not (x&d).bit_count()%2 for x in others)
            return None,d
        v^=pivots[bit]
    b,_=row_reduce(k+[v],group)
    return list(b.values()),None


def control():
    assert compulsory(4,[8],3)==(None,4)
    span,dual=compulsory(5,[4,2],3)
    assert dual is None and pairing_rank([1,2],span)==2
    assert not nonzero_pair([1],[2]) and nonzero_pair([1],[3])


def terminal_ledger(w,ranks):
    """Follow the physical final field backward through literal SWAPs."""
    public=w["public"]
    wanted={i for i,f in enumerate(w["final"]) if f==1}
    active=[i if i in wanted else None for i in range(public)]+[None]*w["owned_fields"]
    result=[]
    for i,(op,j,*a) in reversed(list(enumerate(w["program"]))):
        if op=="SWAP":
            k=a[0]
            active[j],active[k]=active[k],active[j]
        elif op=="MOVE" and active[j] is not None:
            assert a[1]==1
            result.append({"move_event":i,"bank_owner_at_move":j,"final_role":active[j],
                           "before_rank":ranks[a[0]],"paid_rank":8-ranks[a[0]]})
            active[j]=None
        elif op in ("INIT","CLEAR"):
            assert active[j] is None
    assert len(result)==len(wanted)==545 and all(j is None for j in active)
    assert {x["final_role"] for x in result}==wanted
    return result


def normal(space):
    if space is None:
        return None
    pivots=[next(i for i,x in enumerate(row) if x) for row in space]
    free,=set(range(8))-set(pivots)
    result=[Q(0)]*8
    result[free]=Q(1)
    for row,pivot in zip(space,pivots,strict=True):
        result[pivot]=-row[free]
    a=next(x for x in result if x)
    return [str(x/a) for x in result]


def prices(root,invoice,w,ranks,ledger,stock):
    path="research/paired-query-only-bit/independent/interval_gate.py"
    read(root,path)
    spec=spec_from_file_location("price",root/path)
    g=module_from_spec(spec)
    spec.loader.exec_module(g)
    signed=Counter({int(r):v for r,v in invoice["targets"].items()})
    signed.subtract({int(r):v for r,v in invoice["paid"].items()})
    helper=Counter(ranks[w["final"][j]]-ranks[w["start"][j]] for j in range(222,w["public"]))
    assert helper=={2:1,4:25,6:1,8:410}=={int(r):v for r,v in invoice["native_helpers"].items()}
    copies=len(invoice["native_instances"])
    assert copies==36
    major=Counter(x["before_rank"] for x in ledger
                  if x["final_role"]>=222 and w["start"][x["final_role"]]==0)
    assert major=={2:2,4:2,6:138,7:268}
    out={}
    for k in (Q("0.0040075385047236"),Q("0.004008162992724")):
        base=g.moment(signed,k)
        minority=(0,0)
        for r,n in helper.items():
            if r<8:
                minority=g.add(minority,g.smul(g.sub(g.exact(r),g.power(r,k)),copies*n))
        def terminal(a):
            return g.smul(g.add(g.sub(g.power(a+1,k),g.exact(1)),
                                g.sub(g.power(8-a,k),g.power(8,k))),copies)
        own=g.add(base,minority)
        for a,n in major.items():
            if a<7:
                own=g.add(own,g.smul(terminal(a),n))
        one=terminal(6)
        needed=next(n for n in range(23) if g.add(own,g.smul(one,n))[0]>0)
        assert g.add(own,g.smul(one,needed-1))[1]<0
        total=g.add(own,g.smul(one,stock))
        out[str(k)]={"compatible_stock_upper":stock,"needed":needed,
                     "net_upper":g.show(total),"still_negative":total[1]<0,
                     "all_added_setup_and_ordinary_work_granted_free":True}
    return out


def run(root,seconds):
    deadline=monotonic()+seconds
    control()
    w=json.loads(gzip.decompress(read(root,"research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz")))
    invoice=json.loads(read(root,"research/paired-query-only-bit/EFREE-RESULT.json"))
    assert (w["public"],w["owned_fields"],len(w["program"]))==(659,237,34137)
    raw_frames={int(f):v for f,v in w["frames"].items()}
    ranks={f:x["dim"] for f,x in raw_frames.items()}
    frames={f:rref(tuple(map(Q,row)) for row in x["B"]) for f,x in raw_frames.items()}
    assert len(set(frames.values()))==len(frames)==636
    assert all(len(frames[f])==r for f,r in ranks.items()) and ranks[1]==8
    chart={space:f for f,space in frames.items() if ranks[f]==7}
    ledger=terminal_ledger(w,ranks)
    live=[x for x in ledger if x["paid_rank"]>=2]
    source={}
    owner={}
    for x in live:
        i=x["move_event"]
        op,j,a,b=w["program"][i]
        assert op=="MOVE" and (j,b)==(x["bank_owner_at_move"],1)
        assert ranks[a]==x["before_rank"] and i not in source
        source[i]=frames[a]
        owner[i]=j
    main=sorted(x["move_event"] for x in live if x["final_role"]<222)
    assert len(live)==len(source)==185 and len(main)==22
    pre,pi,touch=sweep(w,ranks,set(source),deadline)
    post,si,_=sweep(w,ranks,set(source),deadline,reverse=True)
    group=sum(1<<i for i in range(222,659) if (w["start"][i],w["final"][i])==(0,1))
    assert group.bit_count()==410

    @cache
    def candidates(mid):
        return [i for i,a in source.items() if join(mid,a)==mid]

    reports=[]
    good=set()
    prefix_global=set()
    suffix_global=set()
    literal=abstract=generic=0
    for i in main:
        check_time(deadline)
        a=source[i]
        mids={x for x in chart if join(x,a)==x}
        assert len(mids)==2
        mids.update(x for b in source.values() if len(x:=join(a,b))==7)
        variants=[(m,chart.get(m),candidates(m)) for m in sorted(mids)]
        variants.append((None,None,[j for j,b in source.items() if join(a,b)==a]))
        clocks=touch[owner[i]]
        pos=clocks.index(i)
        window=[clocks[pos-1]+1 if pos else 0,clocks[pos+1] if pos+1<len(clocks) else len(w["program"])]
        bank_rows=[]
        for mid,f,cohort in variants:
            check_time(deadline)
            assert i in cohort
            literal+=f is not None
            abstract+=mid is not None and f is None
            generic+=mid is None
            p=pure(sorted(pre.get(f,set())|{pi[j] for j in cohort}),group)
            others=sorted(post.get(f,set())|{si[j] for j in cohort if j!=i})
            q,dual=compulsory(si[i],others,group)
            useful=q is not None and nonzero_pair(p,q)
            if useful:
                good.add(i)
                prefix_global.update(p)
                suffix_global.update(q)
            bank_rows.append({"literal_chart":f,"midpoint_normal":normal(mid),"midpoint_kind":"generic" if mid is None else "new_join" if f is None else "literal",
                              "virtual_bank_events":sorted(cohort),"prefix_group_rank":len(p),
                              "compulsory_suffix_group_span_rank":None if q is None else len(q),
                              "paired_support":useful,"outside_dual":None if dual is None else positions(dual)})
        reports.append({"event":i,"role":owner[i],"pivot_quiet_window":window,
                        "prefix_input":positions(pi[i]),"suffix_response":positions(si[i]),
                        "variants":bank_rows,"viable":i in good})
    assert literal==44 and generic==22
    pairing=pairing_rank(sorted(prefix_global),sorted(suffix_global))
    upper=min(pairing,len(good))
    return {"status":"EXHAUSTED_ONE_STOCK_MAP","pins":PINS,"seconds_cap":seconds,
            "target_group_origins":410,"main_banks":22,"virtual_public_banks":185,
            "literal_midpoint_classes":literal,"new_rank7_join_classes":abstract,"generic_new_midpoint_classes":generic,
            "tested_bank_maps":len(reports),"bank_maps":reports,"viable_banks":sorted(good),
            "qualifying_local_pairing_rank":pairing,"stock_upper":upper,"price":prices(root,invoice,w,ranks,ledger,upper),
            "pending_maps":0,"new_individual_sites":0,
            "scope":"Fixed literal normalized operations and bank graph with virtual rank-one plus rank-one subdivision. Grant all literal coframe clocks and all 185 compatible virtual pivots, including all rank-seven rational chart classes. Mandatory own paid pivot coefficient and outside cancellation. New charts cannot acquire new literal occupants in this model."}


if __name__=="__main__":
    assert __debug__
    seconds=int(sys.argv[2]) if len(sys.argv)>2 else 480
    assert 0<seconds<=480
    print(json.dumps(run(Path(sys.argv[1]),seconds),sort_keys=True,indent=2))
