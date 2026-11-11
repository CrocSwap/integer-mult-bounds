"""Independently check every BIT label flow/cut and its complete invoice."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as F
from functools import cache
import gzip
from hashlib import sha256
from itertools import pairwise
import json
from pathlib import Path
import runpy
from time import monotonic

PACKAGE = Path(__file__).resolve().parent
WORD = "research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz"
INVOICE = "research/paired-query-only-bit/EFREE-RESULT.json"


def authenticate(path, raw, digest):
    if sha256(raw).hexdigest() != digest:
        raise ValueError(f"changed input {path}")
    return raw


def load_inputs(root):
    manifest = json.loads((PACKAGE / "SOURCES.json").read_bytes())
    pins = {}
    for entry in manifest["files"]:
        if entry["usage"] != "input":
            continue
        path = entry["path"]
        assert path in (WORD, INVOICE) and path not in pins
        pins[path] = entry["sha256"]
    assert set(pins) == {WORD, INVOICE}
    contents = {}
    for path, digest in pins.items():
        raw = (root / path).read_bytes()
        contents[path] = authenticate(path, raw, digest)
        try:
            authenticate(path, raw + b"\n", digest)
        except ValueError:
            continue
        raise AssertionError("mutated source accepted")
    return json.loads(gzip.decompress(contents[WORD])), json.loads(contents[INVOICE])



def incidence(word):
    n=word['public']
    slots=list(range(n))+[None]*word['owned_fields']
    attr=[(f,False,-1) for f in word['start']]
    visits={i:[i] for i in range(n)}
    paid=[]
    for t,(op,i,*a) in enumerate(word['program']):
        if op=='SWAP':
            j=a[0]
            slots[i],slots[j]=slots[j],slots[i]
        elif op=='MOVE':
            paid.append(tuple(a))
        else:
            v=len(attr)
            attr.append((a[-1],True,t))
            if op=='INIT':
                assert slots[i] is None
                slots[i]=n+t
                visits[n+t]=[v]
            else:
                visits[slots[i]].append(v)
                if op=='ADD' and a[0]!=i:
                    visits[slots[a[0]]].append(v)
                if op=='CLEAR':
                    slots[i]=None
    assert all(v is None for v in slots[n:])
    for i,f in enumerate(word['final']):
        visits[slots[i]].append(len(attr))
        attr.append((f,False,len(word['program'])))
    assert len(visits)==n+237
    edges=[edge for seq in visits.values() for edge in pairwise(seq)]
    assert Counter((attr[u][0],attr[v][0]) for u,v in edges if attr[u][0]!=attr[v][0])==Counter(paid)
    return attr,edges,paid


def linrank(rows):
    pivot={}
    for row in rows:
        r=list(row)
        for j in range(len(r)):
            x=r[j]
            if not x:
                continue
            if j in pivot:
                r=[a-x*b for a,b in zip(r,pivot[j],strict=True)]
            else:
                pivot[j]=[a/x for a in r]
                break
    return len(pivot)


def add(cap,u,v,w):
    if u!=v and w:
        cap[u,v]+=w


def certify(caps, flow, side, source, sink, n):
    balance=[0]*n
    used=set()
    for u,v,f in flow:
        if (u,v) in used or not 0<f<=caps.get((u,v),0):
            raise ValueError('forged flow or duplicate arc')
        used.add((u,v))
        balance[u]+=f
        balance[v]-=f
    cut=sum(w for (u,v),w in caps.items() if u in side and v not in side)
    if balance[source]!=cut or balance[sink]!=-cut or any(balance[j] for j in range(n) if j not in (source,sink)):
        raise ValueError('infeasible flow or cut mismatch')
    return cut


def verify(root):
    start = monotonic()
    assert __debug__
    word, invoice = load_inputs(root)
    p = runpy.run_path(str(PACKAGE / "pricing.py"))
    attr,edges,paid=incidence(word)
    assert len(attr)==32581 and len(edges)==62474
    bases={int(f):[tuple(map(F,row)) for row in j['B']] for f,j in word['frames'].items()}
    dims={f:len(b) for f,b in bases.items()}

    @cache
    def rank(f,g):
        if f==g:
            return 0
        if dims[f]==dims[g] or linrank(bases[f]+bases[g])!=max(dims[f],dims[g]):
            return None
        return abs(dims[f]-dims[g])

    scopes={tuple(sorted((f,g),key=dims.__getitem__)) for f,g in paid if rank(f,g)==1}
    assert len(scopes)==897
    native=Counter(rank(f,g) for f,g in paid)
    signed,copies=p['profile'](invoice,native,word,dims)
    assert copies==36
    k=F(p['TARGET'])
    base=p['cost'](signed,k)
    grid=p['SCALE']
    tariffs={r:tuple(int(x*grid) for x in p['power_bounds'](r,k)) for r in range(1,9)}
    tariffs[0]=(0,0)
    old=[rank(attr[u][0],attr[v][0]) for u,v in edges]
    inf=sum(tariffs[r][1] for r in old)+1
    incident=defaultdict(set)
    for i,(u,v) in enumerate(edges):
        for z in (u,v):
            f,m,_=attr[z]
            if m:
                incident[f].add(i)
    payload = gzip.decompress((PACKAGE / 'CUTS.json.gz').read_bytes())
    report = json.loads(payload)
    assert report['vertices'] == len(attr) and report['edges'] == len(edges)
    assert report['physical_sites'] == 0 and len(paid) == 2871
    assert not report['unresolved'] and not report['pruned_edgewise'] and report['scoped_pairs']==897
    assert len(report['exact_cuts'])==897 and {tuple(q['pair']) for q in report['exact_cuts']}==scopes
    assert list(map(F,report['signed_original_net']))==list(base)
    changed_scopes=0
    best=None
    control_ran=False
    for q in report['exact_cuts']:
        a,b=q['pair']
        relevant=incident[a]|incident[b]
        vs=sorted({v for i in relevant for v in edges[i] if attr[v][1] and attr[v][0] in (a,b)})
        assert q['affected_edges']==len(relevant) and q['variables']==len(vs)
        j={v:i for i,v in enumerate(vs)}
        changed={}
        for v,t,f in q['changed_contacts']:
            assert v in j and v not in changed and (t,f)==(attr[v][2],b if attr[v][0]==a else a)
            changed[v]=f
        changed_scopes+=bool(changed)
        caps=defaultdict(int)
        unary=[[0,0] for _ in vs]
        previous,next_=Counter(),Counter()
        for i in relevant:
            u,v=edges[i]
            if u in j and v in j:
                add(caps,j[u],j[v],tariffs[1][0])
                add(caps,j[v],j[u],tariffs[1][0])
            else:
                x,y=(u,v) if u in j else (v,u)
                assert x in j and y not in j
                for c,f in enumerate((a,b)):
                    rr=rank(f,attr[y][0])
                    unary[j[x]][c]+=inf if rr is None else tariffs[rr][0]
            rr=rank(changed.get(u,attr[u][0]),changed.get(v,attr[v][0]))
            assert rr is not None
            previous[old[i]]+=1
            next_[rr]+=1
        source,sink=len(vs),len(vs)+1
        side={source}
        shift=0
        for i,(c0,c1) in enumerate(unary):
            m=min(c0,c1)
            shift+=m
            add(caps,source,i,c1-m)
            add(caps,i,sink,c0-m)
            if changed.get(vs[i],attr[vs[i]][0])==a:
                side.add(i)
        cut=certify(caps,q['flow_certificate'],side,source,sink,len(vs)+2)
        assert cut+shift==sum(n*tariffs[r][0] for r,n in next_.items())
        if not control_ran:
            wrong=[row[:] for row in q['flow_certificate']]
            assert wrong
            wrong[0][2]+=1
            try:
                certify(caps,wrong,side,source,sink,len(vs)+2)
            except ValueError:
                control_ran=True
            assert control_ran
        upper=base[1]+copies*F(sum(n*tariffs[r][1] for r,n in previous.items())-cut-shift,grid)
        assert upper==F(q['directed_whole_upper'])<0
        delta={r:copies*(previous[r]-next_[r]) for r in set(previous)|set(next_) if r}
        assert {str(r):v for r,v in delta.items()}==q['signed_paid_saving_hist']
        assert list(p['cost'](delta,k))==list(map(F,q['signed_saving_interval']))
        best=upper if best is None else max(best,upper)
        assert monotonic()-start<180, 'audit cap'
    return {
        "status": "PASS_INDEPENDENT_897_BIT_FLOW_CUT_CERTIFICATES",
        "scopes": len(scopes),
        "edges": len(edges),
        "changed_optimal_assignments": changed_scopes,
        "best_directed_whole_upper": str(best),
        "signed_original_net": list(map(str, base)),
        "forged_flow_rejected": control_ran,
        "certificate_sha256": sha256(payload).hexdigest(),
    }


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True,
                        help="Root of the clean checkout or standalone source export")
    result = verify(parser.parse_args().root)
    expected = json.loads((PACKAGE / "AUDIT.json").read_bytes())
    assert result == expected
    print(json.dumps(result, sort_keys=True, indent=2))
