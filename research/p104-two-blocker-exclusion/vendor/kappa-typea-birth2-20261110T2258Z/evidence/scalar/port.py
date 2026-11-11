"""Rebase the adjacent one-blocker scalar commutator screen onto exact #7131."""
from collections import Counter
from fractions import Fraction as Q
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
WORD = '9557c4682056ab7cc7cda89aa73865bef0e3948cc10b3c3061b0a944af05b96a'
RESULT = 'e4ae0c1cfa809cd780a6e22ce32528e7ca4b4e57f90abf91ad0bde97d30446ab'
CALLER = '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc'
BASE = ROOT/'kappa-chronology-pivot-20261110T1021Z/evidence/corrected_contacts.py'
GRAPH = ROOT/'kappa-interior-20261110T0823Z/evidence/closure.py'
PRICE = ROOT/'kappa-coupled-boundaries-20261110T0908Z/replay/research/shared-wire-stop-fusion/audit_price.py'


def read(path, pin, compressed=False):
    payload=path.read_bytes()
    if compressed:
        payload=gzip.decompress(payload)
    assert sha256(payload).hexdigest()==pin
    return json.loads(payload)


def module(name, path):
    spec=spec_from_file_location(name,path)
    result=module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def count_invoice(word, caller, graph):
    spaces=[graph.span(f) for f in word['frames']]
    dim=[len(f) for f in word['frames']]
    public=word['public']
    paid,owned_paid,targets=Counter(),Counter(),Counter()
    charts=word['initial']+[None]*word['owned_fields']
    for e in word['program']:
        op,r=e[:2]
        if op=='MOVE':
            a,b,private=e[2:]
            assert charts[r]==a and private==(r>=public)
            assert spaces[a]<spaces[b] or private and spaces[b]<spaces[a]
            (owned_paid if private else paid)[abs(dim[b]-dim[a])]+=1
            charts[r]=b
        elif op=='INIT':
            assert r>=public and charts[r] is None
            charts[r]=e[2]
        elif op=='CLEAR':
            assert r>=public and charts[r]==e[2]
            charts[r]=None
        else:
            assert all(charts[s]==e[-1] for s in (e[1:3] if op in ('ADD','COPY') else e[1:2]))
    assert charts==word['final']+[None]*word['owned_fields']
    main=set(word['live'])|{r+112 for r in word['live']}|set(word['hosted']['X2'])|set(word['hosted']['Y2'])
    for r,(a,b) in enumerate(zip(word['initial'],word['final'])):
        if r not in main:
            assert spaces[a]<spaces[b]
            targets[dim[b]-dim[a]]+=1
    p,t=Counter(),Counter()
    stages=0
    for e in caller['events']:
        if e[0]=='J':
            stages+=1
            p.update(paid)
            p.update(owned_paid)
            t.update(targets)
        elif e[1]=='QUERY':
            p[1]+=len(caller['types'][e[0]]['ports'])
        elif e[1] in ('IDLE_ONE','IDLE_ODD'):
            p[8*len(e[3])+(e[1]=='IDLE_ODD')]+=len(caller['types'][e[0]]['ports'])
    assert stages==17
    for data in caller['types'].values():
        for row in data['diagonal']:
            t[row[0]%2+8*sum(row[2:])]+=len(data['ports'])
    return p,t,dict(native_public_P=paid,native_owned_P=owned_paid,native_T=targets,
        public=public,owned=word['owned_fields'],program_events=len(word['program']),native_copies=stages)


def run(word_path, result_path, caller_path, journal_path, cap, mode="adjacent"):
    word=read(word_path,WORD,True)
    source=read(result_path,RESULT)
    caller=read(caller_path,CALLER)
    graph=module('current_graph',GRAPH)
    engine=module('current_directed',PRICE)
    old=module('retained_adjacent_blocker',BASE)
    p,t,controls=count_invoice(word,caller,graph)
    for actual,name in ((p,'P'),(t,'T')):
        assert dict(actual)=={int(k):v for k,v in source['price']['after'][name].items()}
    signed=t.copy();signed.subtract(p)
    assert sum(r*n for r,n in signed.items())==1424
    lo,hi=map(Q,source['price']['gate']['raw_bracket'])
    assert engine.raw_margin(signed,lo)[0]>0>engine.raw_margin(signed,hi)[1]
    old.WORD_SHA=WORD
    old.BRACKET=(str(lo),str(hi))
    propagate=old.propagate
    join=propagate.__globals__['join']

    def reject_disjoint(low,high,equalities,ordered_paid):
        if any(not join(low[a],low[b])<=high[a]&high[b] for a,b in equalities):
            return None
        return propagate(low,high,equalities,ordered_paid)

    old.propagate=reject_disjoint
    with journal_path.open('x') as journal:
        receipt=old.screen(word,graph,engine,journal,free_correction=mode=="free",cap=cap,
                           owned_blocker=mode=="owned",gauss=mode=="gauss")
    return dict(source_word_sha256=WORD,source_result_sha256=RESULT,source_caller_sha256=CALLER,
        source_price_bracket=[str(lo),str(hi)],full_paid=p,full_target=t,source_literal=controls,
        replay_sources={p.name:sha256(p.read_bytes()).hexdigest() for p in (BASE,GRAPH,PRICE)},
        tested_placement_cap=cap,**receipt)


if __name__=='__main__':
    options=sys.argv[5:]
    mode=next((x[2:] for x in options if x.startswith('--')), 'adjacent')
    cap=next((int(x) for x in options if not x.startswith('--')), None)
    assert mode in ('adjacent','free','owned','gauss')
    print(json.dumps(run(*map(Path,sys.argv[1:5]),cap,mode),indent=2,sort_keys=True))
