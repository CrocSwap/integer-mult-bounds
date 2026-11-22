"""Construct a nine-downward-contact 111-port word and verify its complete map."""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
import io
import json
from math import isqrt
from pathlib import Path

COMPRESSED='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'
EXPANDED='b096d6df2a0c4688296b13ab0cfd50fec1c7dec732819c624ddd7a745a144b69'


def load(path):
    data=Path(path).read_bytes();assert sha256(data).hexdigest()==COMPRESSED
    raw=gzip.decompress(data);assert sha256(raw).hexdigest()==EXPANDED
    return json.loads(raw)


def canonical(g):return (json.dumps(g,sort_keys=True,separators=(',',':'))+'\n').encode()


def compressed(raw):
    out=io.BytesIO()
    with gzip.GzipFile(filename='',fileobj=out,mode='wb',mtime=0) as f:f.write(raw)
    return out.getvalue()


def parity(v,owners):
    result=0
    for j in owners:result^=v[j]
    return result


def express(terms,target):
    pivots={}
    for owner,row in terms:
        coeff=1<<owner
        while row:
            p=row.bit_length()-1
            if p not in pivots:pivots[p]=row,coeff;break
            v,c=pivots[p];row^=v;coeff^=c
    answer=0
    while target:
        p=target.bit_length()-1
        if p not in pivots:raise ValueError('native return is missing from the joint live stock')
        v,c=pivots[p];target^=v;answer^=c
    return [j for j in range(answer.bit_length()) if answer>>j&1]


def execute(ch,v,row,n):
    op,owner,*a=row
    if op=='MOVE':assert ch[owner]==a[0];ch[owner]=a[1]
    elif op=='ADD':src,c=a;assert ch[owner]==ch[src]==c;v[owner]^=v[src]
    elif op=='SWAP':s,=a;ch[owner],ch[s]=ch[s],ch[owner];v[owner],v[s]=v[s],v[owner]
    elif op=='INIT':assert owner>=n and owner not in ch;ch[owner],v[owner]=a[0],0
    elif op=='CLEAR':assert owner>=n and ch.pop(owner)==a[0];return v.pop(owner)
    else:raise ValueError(op)
    return None


def replay(g):
    n=g['public'];ch=dict(enumerate(g['start']));v={i:1<<i for i in ch};clears={};peak=n
    for row in g['program']:
        r=execute(ch,v,row,n)
        if r is not None:assert row[1] not in clears;clears[row[1]]=(row[2],r)
        peak=max(peak,len(ch))
    assert ch==dict(enumerate(g['final']))
    assert [v[i] for i in range(n)]==[(1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(n)]
    assert len(clears)==g['owned_fields'] and all(r for c,r in clears.values())
    return v,clears,peak


def reverse(g):
    n=g['public'];ch=dict(enumerate(g['final']));v={i:1<<i for i in ch}
    for op,d,*a in reversed(g['program']):
        if op=='CLEAR':assert d not in ch;ch[d],v[d]=a[0],0
        elif op=='INIT':assert ch.pop(d)==a[0];del v[d]
        elif op=='MOVE':assert ch[d]==a[1];ch[d]=a[0]
        elif op=='ADD':s,c=a;assert ch[d]==ch[s]==c;v[s]^=v[d]
        elif op=='SWAP':s,=a;ch[d],ch[s]=ch[s],ch[d];v[d],v[s]=v[s],v[d]
        else:raise ValueError(op)
    assert ch==dict(enumerate(g['start']))
    assert [v[i] for i in range(n)]==[(1<<i)^((1<<(111+i)) if i<111 else 0) for i in range(n)]


def histograms(g):
    d={int(c):spec['dim'] for c,spec in g['frames'].items()};up=Counter();down=Counter()
    for op,owner,*a in g['program']:
        if op!='MOVE':continue
        delta=d[a[1]]-d[a[0]];assert delta
        (up if delta>0 else down)[abs(delta)]+=1
    return up,down


def build(g,*,top_first=False):
    p=g['program'];n=g['public'];dims={int(c):s['dim'] for c,s in g['frames'].items()};down=[i for i,row in enumerate(p) if row[0]=='MOVE' and dims[row[2]]>dims[row[3]]];assert len(down)==27
    inits={row[1]:i for i,row in enumerate(p) if row[0]=='INIT'};blocks={};missing=set()
    for j in range(0,len(down),3):
        i,m,h=down[j:j+3];a,b,c=p[i][1],p[m][1],p[h][1];start=inits[a];assert p[i][3]==p[m][2] and p[m][3]==p[h][2] and p[h][3]==0 and dims[p[i][2]]==7
        assert sum(r[0]=='MOVE' for r in p[start:h+1])==3 and all(r[0] in ('INIT','ADD','MOVE') and r[1] in (a,b,c) for r in p[start:h+1]);
        for z in (a,b):
            later=[r for r in p[h+1:] if r[1]==z or (r[0] in ('ADD','SWAP') and r[2]==z)]
            assert len(later)==1 and later[0][0]=='CLEAR'
        blocks[start]=(h,a,b,c,(i,m,h));missing.update([a,b])
    ch=dict(enumerate(g['start']));v={i:1<<i for i in ch};new=[];w=[];k=0
    while k<len(p):
        if k in blocks:
            h,a,b,c,clocks=blocks[k];old_ch=ch.copy();old_v=v.copy()
            for row in p[k:h+1]:execute(ch,v,row,n)
            f=v[c];zero=sorted(i for i,t in old_ch.items() if t==0);top=sorted(i for i,t in old_ch.items() if t==1)
            stock=(top+zero) if top_first else (zero+top)
            combo=express([(i,old_v[i]) for i in stock],f);donor=[i for i in combo if old_ch[i]==1];local=[i for i in combo if old_ch[i]==0]
            remote=parity(old_v,donor);assert remote and remote^parity(old_v,local)==f
            replacement=[['INIT',c,1]]+[['ADD',c,i,1] for i in donor]+[['MOVE',c,1,0]]+[['ADD',c,i,0] for i in local]
            for row in replacement:execute(old_ch,old_v,row,n)
            assert old_v[c]==f and old_ch[c]==0 and all(old_ch[j]==t and old_v[j]==v[j] for j,t in ch.items() if j not in (a,b))
            w.append({'old_move_clocks':clocks,'old_grades':[abs(dims[p[i][2]]-dims[p[i][3]]) for i in clocks],'return_owner':c,'removed_owners':[a,b],'chart1_sources':donor,'chart0_sources':local,'original_return_sha256':sha256(f.to_bytes(79,'little')).hexdigest(),'replacement_move_new_clock':len(new)+1+len(donor)})
            new+=replacement;k=h+1;continue
        row=p[k];execute(ch,v,row,n)
        if not (row[0]=='CLEAR' and row[1] in missing):new.append(row)
        k+=1
    changed=dict(g,owned_fields=g['owned_fields']-len(missing),program=new)
    before,cb,p0=replay(g);after,ca,p1=replay(changed);reverse(changed)
    assert before==after and set(cb)-set(ca)==missing and all(cb[o]==ca[o] for o in ca)
    first=g['frames']['1'];zero=g['frames']['0'];identity=[[int(i==j) for j in range(8)] for i in range(8)];assert first=={'A':[],'B':identity,'dim':8} and zero=={'A':identity,'B':[],'dim':0}
    ups,downs=histograms(g);newups,newdowns=histograms(changed);assert ups==newups and newdowns==Counter({8:9});assert sum(ups.values())==2776
    # Mutate the first donor coefficient and re-run the public operator check.
    bad=list(new);clock=w[0]['replacement_move_new_clock'];assert bad[clock-1][0]=='ADD';bad.pop(clock-1)
    try:replay(dict(changed,program=bad))
    except AssertionError:pass
    else:raise AssertionError('a corrupted remote return donor escaped detection')
    report={'schema':'p104-nine-downward-word/1','native_graph_compressed_sha256':COMPRESSED,'native_graph_expanded_sha256':EXPANDED,'new_graph_canonical_sha256':sha256(canonical(changed)).hexdigest(),'new_graph_compressed_sha256':sha256(compressed(canonical(changed))).hexdigest(),'public_basis_rows':n,'retained_identical_typed_dirty_clears':len(ca),'native_dirty_clears':len(cb),'peak_live_native':p0,'peak_live_changed':p1,'native_instructions':len(p),'changed_instructions':len(new),'native_ops':dict(Counter(r[0] for r in p)),'changed_ops':dict(Counter(r[0] for r in new)),'upward_histogram_both':dict(ups),'downward_native_histogram':dict(downs),'downward_changed_histogram':dict(newdowns),'native_sum_of_ranks':sum(r*v for hist in (ups,downs) for r,v in hist.items()),'changed_sum_of_ranks':sum(r*v for hist in (newups,newdowns) for r,v in hist.items()),'returned_scalar_controls':9,'wrong_donor_rejected':True,'chain_witnesses':w}
    return changed,report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('source');parser.add_argument('--write-word',type=Path);parser.add_argument('--top-first',action='store_true');args=parser.parse_args();g,report=build(load(args.source),top_first=args.top_first)
    if args.write_word:args.write_word.write_bytes(compressed(canonical(g)))
    print(json.dumps(report,sort_keys=True,indent=2))
