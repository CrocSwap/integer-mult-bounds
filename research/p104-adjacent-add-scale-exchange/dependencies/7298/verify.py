"""Replay the exact adjacent shared-owned ADD census on both native words."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
from hashlib import sha1, sha256
from itertools import pairwise
from pathlib import Path
import gzip
import json
import runpy

HERE=Path(__file__).resolve().parent
BIT='research/paired-query-only-bit/'
PRICING=runpy.run_path(str(HERE/'pricing.py'))


def read(path,pin):
    raw=path.read_bytes()
    if raw.startswith(b'\x1f\x8b') and pin.get('uncompress',False):
        raw=gzip.decompress(raw)
    blob=sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
    if sha256(raw).hexdigest()!=pin['sha256'] or blob!=pin['git_blob']:
        raise ValueError('Changed input: '+path.name)
    return raw


def rank(rows):
    pivots={}
    for x in rows:
        while x and x.bit_length() in pivots:
            x^=pivots[x.bit_length()]
        if x:
            pivots[x.bit_length()]=x
    return len(pivots)


def commutes(a,b,c,d):
    return a!=b and c!=d and a!=d and c!=b


def complex_scan(word,caller,early):
    frames=word['frames']
    n=word['public']
    dims=list(map(len,frames))
    program=word['program']
    assert all(rank(f)==r for f,r in zip(frames,dims,strict=True))

    @cache
    def distance(a,b):
        return 2*rank(frames[a]+frames[b])-dims[a]-dims[b]

    chains={}
    at={}
    scalar=[]
    native=Counter()
    for t,(tag,d,*args) in enumerate(program):
        if tag=='MOVE':
            a,b,owned=args
            r=distance(a,b)
            assert owned==(d>=n) and r==abs(dims[a]-dims[b])>0
            native[r]+=1
            continue
        scalar.append(t)
        if tag=='INIT':
            assert d not in chains
            chains[d]=[]
        for role in {d,args[0]} if tag in ('ADD','COPY') else {d}:
            if role>=n:
                seq=chains[role]
                at[t,role]=seq,len(seq)
                seq.append(t)
        if tag=='CLEAR':
            del chains[d]
    assert not chains and sum(native.values())==6280
    stages=[e[1] for e in caller['events'] if e[0]=='J']
    assert stages==list(range(1,18))
    copies=len(stages)
    paid=Counter({r:copies*v for r,v in native.items()})
    main=set(word['live'])|{x+112 for x in word['live']}|set(word['hosted']['X2']+word['hosted']['Y2'])
    helper=Counter(dims[b]-dims[a] for r,(a,b) in enumerate(zip(word['initial'],word['final'],strict=True)) if r not in main)
    targets=Counter({r:copies*v for r,v in helper.items()})
    for info in caller['types'].values():
        for sign,offset,*bits in info['diagonal']:
            assert (sign,offset,len(bits))==(-1,0,copies)
            targets[1+8*sum(bits)]+=len(info['ports'])
    for e in caller['events']:
        if e[0]=='J':
            continue
        kind,tag,_,*args=e
        if tag=='QUERY':
            paid[1]+=len(caller['types'][kind]['ports'])
        if tag in ('IDLE_ONE','IDLE_ODD'):
            paid[8*len(args[0])+int(tag=='IDLE_ODD')]+=len(caller['types'][kind]['ports'])
    assert dict(paid)=={int(r):v for r,v in early['invoice']['P'].items()}
    assert dict(targets)=={int(r):v for r,v in early['invoice']['T'].items()}
    assert sum(paid.values())==110536 and sum(targets.values())==22461
    net=targets.copy()
    net.subtract(paid)
    assert sum(r*v for r,v in net.items())==1424
    k=Q(early['price']['independent_raw_bracket'][1])
    base=PRICING['cost'](net,k)
    assert base[1]<0
    counts=Counter()
    rows=defaultdict(list)
    for t,u in pairwise(scalar):
        p,q=program[t],program[u]
        if p[0]!=q[0] or p[0]!='ADD':
            continue
        counts['all']+=1
        a,b,f=p[1],p[2],p[-1]
        c,d,g=q[1],q[2],q[-1]
        if f==g:
            continue
        counts['different_charts']+=1
        shared={a,b}&{c,d}
        if not any(role>=n for role in shared):
            continue
        counts['shared_owned']+=1
        if min(shared)<n or not commutes(a,b,c,d):
            counts['excluded']+=1
            continue
        old=[]
        new=[]
        for role in sorted(shared):
            seq,i=at[t,role]
            seq2,j=at[u,role]
            assert seq is seq2 and j==i+1 and i>0 and j+1<len(seq)
            l=program[seq[i-1]][-1]
            r=program[seq[j+1]][-1]
            old.extend([distance(l,f),distance(g,r)])
            new.extend([distance(l,g),distance(f,r)])
        rows[tuple(sorted(old)),tuple(sorted(new))].append([t,u])
    assert counts=={'all':65118,'different_charts':4625,'shared_owned':20,'excluded':14}
    assert {k:len(v) for k,v in rows.items()}=={((0,0),(4,4)):3,((0,1),(1,2)):2,((0,1),(5,6)):1}
    evidence=[]
    for (old,new),events in sorted(rows.items()):
        delta=Counter(r for r in old if r)
        delta.subtract(r for r in new if r)
        complete=base[1]+copies*PRICING['cost'](delta,k)[1]
        assert complete<0
        evidence.append({'old_ranks':old,'new_ranks':new,'events':events,'complete_upper':str(complete)})
    return {'counts':counts,'cases':evidence,'copies':copies,'probe':str(k),'unresolved':0}


def bit_scan(word,invoice):
    n=word['public']
    live=list(range(n))+[None]*word['owned_fields']
    chart=dict(enumerate(word['start']))
    previous=chart.copy()
    scalar=[]
    paid=Counter()
    traced=Counter()
    edges=0

    def contact(owner,frame):
        nonlocal edges
        assert owner is not None and chart[owner]==frame
        old=previous[owner]
        if old!=frame:
            traced[old,frame]+=1
        previous[owner]=frame
        edges+=1

    for tick,(tag,d,*args) in enumerate(word['program']):
        role=live[d]
        if tag=='MOVE':
            a,b=args
            assert chart[role]==a
            chart[role]=b
            paid[a,b]+=1
            continue
        if tag=='SWAP':
            s=args[0]
            live[d],live[s]=live[s],live[d]
        if tag=='INIT':
            assert role is None
            live[d]=n+tick
            chart[live[d]]=previous[live[d]]=args[0]
        if tag=='CLEAR':
            contact(role,args[-1])
            live[d]=None
        if tag=='ADD':
            src,frame=live[args[0]],args[-1]
            for r in {role,src}:
                contact(r,frame)
            scalar.append((tag,role,src,frame))
        else:
            assert tag in ('SWAP','INIT','CLEAR')
            scalar.append((tag,None,None,None))
    for d,f in enumerate(word['final']):
        contact(live[d],f)
    assert all(x is None for x in live[n:]) and edges==62474 and traced==paid
    dims={int(f):len(x['B']) for f,x in word['frames'].items()}
    native=Counter()
    for (a,b),count in paid.items():
        native[abs(dims[a]-dims[b])]+=count
    signed,copies=PRICING['profile'](invoice,native,word,dims)
    all_pairs=[(a,b) for a,b in pairwise(scalar) if a[0]==b[0]=='ADD']
    owned=[(a,b) for a,b in all_pairs if any(r>=n for r in set(a[1:3])&set(b[1:3]))]
    eligible=[(a,b) for a,b in owned if a[-1]!=b[-1]]
    assert len(scalar)-1==31265 and len(all_pairs)==30551 and len(owned)==246 and not eligible
    margin=PRICING['cost'](signed,Q(PRICING['TARGET']))[1]
    assert margin<0
    return {'normalized_neighbors':len(scalar)-1,'add_pairs':len(all_pairs),'shared_owned':len(owned),
            'checked_edges':edges,'eligible':len(eligible),'unresolved':0,'copies':copies,
            'target':PRICING['TARGET'],'target_margin_upper':str(margin),'saving_upper':'0'}


def controls():
    assert commutes(0,2,1,2) and commutes(0,1,0,2)
    assert not commutes(0,1,1,2) and not commutes(0,1,1,0)
    assert not commutes(0,0,1,2)
    assert 2*rank([1,2,1,4])-4==2
    return {'same_source_and_destination_commute':True,'cross_operands_rejected':True,
            'self_add_rejected':True,'nonnested_rank_not_dimension_gap':True}


def unique_keys(entries):
    out={}
    for k,v in entries:
        if k in out:
            raise ValueError('Duplicate manifest key: '+k)
        out[k]=v
    return out


def run(root):
    p=json.loads((HERE/'PROVENANCE.json').read_bytes(),object_pairs_hook=unique_keys)
    c={}
    for k,pin in p['bundled'].items():
        raw=read(HERE/k,pin)
        c[k]=json.loads(gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw)
    rows=json.loads((HERE/'SOURCES.json').read_bytes(),object_pairs_hook=unique_keys)['files']
    pins=unique_keys((row['path'],row) for row in rows)
    bitword=BIT+'retained/inputs/BIT-NATIVE-WORD.json.gz'
    invoice=BIT+'EFREE-RESULT.json'
    return {'status':'PASS_ADJACENT_OWNED_ADD_EXCHANGE_BOUND','controls':controls(),
            'complex':complex_scan(c['inputs/WORD.json.gz'],c['inputs/CALLER.json.gz'],c['inputs/EARLY-RESULT.json.gz']),
            'bit':bit_scan(json.loads(gzip.decompress(read(root/bitword,pins[bitword]))),
                           json.loads(read(root/invoice,pins[invoice])))}


if __name__=='__main__':
    assert __debug__
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path.cwd())
    args=parser.parse_args()
    result=json.dumps(run(args.root),sort_keys=True,indent=2)+'\n'
    frozen=HERE/'RESULT.json'
    if frozen.is_file():
        assert result==frozen.read_text()
    print(result,end='')
