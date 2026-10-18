#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent late8 review by OpenAI Codex at Mason Hale's direction.

No native generator or audit modules are imported. This is a computational
check and accompanying proof review, not a claim of independent human review.
"""
import argparse,json,gzip,hashlib
from collections import Counter,defaultdict
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
SOURCE_MANIFEST_SHA256='82ffd9af8586c79ea5d67cb2f6b139d022e10b1062b753e6631d6feeb5832357'
SOURCE_CONTENT_SHA256={
    'base':'d7d8052f795eb5a06b065396b81262760efdb7ce65f3750d1725e34be7ecbf64',
    'extra':'a0923735190ec06eacc5cfdee836f675f88a5c6f2a0db52c967feab44fa758ef',
}
CANDIDATE_CONTENT_SHA256={
    'base':'90e864895e372208c5733c761285d01e7d4b81b56d06b3e8f5737a2c2fc1489d',
    'extra':'5a1b4389872bfeafd5b4b35c53e19a7689b01b8fee3b1dcfe085b7ddc6a8d889',
}
def sha(data):return hashlib.sha256(data).hexdigest()
def authenticate_source(package):
    manifest=package/'MANIFEST.json'
    assert sha(manifest.read_bytes())==SOURCE_MANIFEST_SHA256,'source manifest digest'
    items=json.loads(manifest.read_text())
    actual={f.relative_to(package).as_posix() for f in package.rglob('*') if f.is_file() and f!=manifest}
    assert actual==set(items),'source inventory differs from authenticated manifest'
    for name,digest in items.items():
        assert sha((package/name).read_bytes())==digest,('source file digest',name)
    return len(items)
@lru_cache(None)
def span(vs):
    s={0}
    for v in vs:s|={x^v for x in tuple(s)}
    return frozenset(s)
def S(vs):return span(tuple(vs))
def rank(vs):return len(S(vs)).bit_length()-1
def dm(s):return len(s).bit_length()-1
FULL=S([1<<i for i in range(9)])
def im(cols,x):
    a=0
    for i,c in enumerate(cols):
        if x>>i&1:a^=c
    return a
def regs(g):return g[1:3] if g[0]=='add' else g[1:2]
def nt(r):return not 112<=r<224
def load(p):return json.loads(gzip.decompress(p.read_bytes()))
def chronological(w):
    d=defaultdict(list)
    for op,(p,r,*_) in enumerate(w['warps'],1):d[p].append(['warp',r,op])
    b=[]
    for i in range(len(w['B'])+1):
        b+=d[i]
        if i<len(w['B']):b.append(w['B'][i])
    return b

def check_frames(w):
    live=set(range(704))-set(w['removed'])
    cur={r:S([w['ports'][r]]) if r<112 else S(w['start_extra'].get(str(r),[])) for r in live}
    ends={r:FULL for r in live}
    for i,p in enumerate(w['ports']):ends[112+i]=frozenset(x for x in range(512) if (x&p).bit_count()%2==0)
    for r,vs in w['helper_final'].items():ends[int(r)]=S(vs)
    start=cur.copy();counts=Counter();bysection={};sections={}
    def climb(r,vs):
        s=S(vs);assert cur[r]<=s,(r,cur[r],s)
        d=dm(s)-dm(cur[r]);cur[r]=s
        if d:counts[d]+=1
    def warp(r,op,old,new):
        cols=w['warps'][abs(op)-1][2]
        assert len(S(cols))==512
        assert cur[r]==S(old)
        # Check positive-direction map for either sign, without computing inverse.
        a,b=(old,new) if op>0 else (new,old)
        assert frozenset(im(cols,x) for x in S(a))==S(b)
        cur[r]=S(new)
    for g in w['A']:
        if g[0]=='warp':warp(*g[1:])
        else:
            for r in regs(g):climb(r,g[-1])
    bysection['A']=dict(counts);prev=counts.copy()
    lev={int(k):S(v) for k,v in w['target_levels'].items()}
    assert all(cur[112+t]==lev.get(t,S([])) for t in range(112))
    paths=[]
    for r,vs in zip(w['centers'],w['center_frames']):
        s=S(vs);assert cur[r]==s
        targets=[g[1]-112 for g in w['cut'] if g[2]==r]
        frames=sorted({lev.get(t,S([])) for t in targets},key=lambda s:-len(s))
        ds=[]
        for f in frames:
            assert f<=s
            d=dm(s)-dm(f)
            if d:counts[d]+=1;ds.append(d)
            s=f
        paths.append({'center':r,'start_rank':rank(vs),'target_offsets':targets,'reader_lines':[sorted(f-{0}) for f in frames],'paid_degrees':ds})
    bysection['cut']=dict(counts-prev);prev=counts.copy()
    ops=defaultdict(list)
    for op,rec in enumerate(w['warps'],1):ops[rec[0]].append((op,rec))
    for i in range(len(w['B'])+1):
        for op,(_,r,cols,old,new) in ops[i]:warp(r,op,old,new)
        if i<len(w['B']):
            g=w['B'][i]
            for r in regs(g):climb(r,g[-1])
    bysection['B']=dict(counts-prev);prev=counts.copy()
    for g in w['restore']:
        for r in regs(g):climb(r,g[-1])
    bysection['restore']=dict(counts-prev);prev=counts.copy()
    for r in live:climb(r,ends[r])
    bysection['ends']=dict(counts-prev)
    inventory=Counter(dm(ends[r])-dm(start[r]) for r in live if r>=224)
    assert counts==Counter({int(k):v for k,v in w['report']['local_profile'].items()})
    assert inventory==Counter({int(k):v for k,v in w['report']['width_inventory'].items()})
    return {'profile':dict(sorted(counts.items())),'section_profiles':bysection,'inventory':dict(sorted(inventory.items())),'center_paths':paths},start,ends

def check_cleanup(w):
    restored=set(map(int,w['helper_final']))
    cold=lambda r:r+704 if r in restored else r
    forward=w['A'][w['prelude_events']:]+chronological(w)+w['restore']
    expected=[]
    for g in reversed(forward):
        if g[0]=='warp':expected.append(['warp',cold(g[1]),-g[2]])
        elif nt(g[1]):
            if g[0]=='add':expected.append(['add',cold(g[1]),cold(g[2]),-g[3],g[4]])
            else:expected.append(['scale',cold(g[1]),g[3],g[2]])
    assert expected==[g[:-1] for g in w['cleanup']]
    assert all(S(g[-1])==FULL for g in w['cleanup'])
    return len(expected)

def algebra(w):
    # A monomial records its operations oldest-first; appending an inverse
    # cancels the newest symbol. No native/generator/audit modules imported.
    live=set(range(704))-set(w['removed']);cold=set(map(int,w['helper_final']))
    assert not w['initial_corrections']
    program=w['precondition']+w['compensation']+w['A']+w['cut']+chronological(w)+w['restore']
    result={}
    for dual in [False,True]:
        rows={r:{(r,()):F(1)} for r in live}
        rows.update({704+r:{} for r in cold})
        def apply(g):
            op=g[0]
            if op=='add':
                t,s=g[1:3];q=F(g[3],g[4]);assert t!=s
                if dual:t,s,q=s,t,-q
                for term,c in list(rows[s].items()):
                    v=rows[t].get(term,F(0))+q*c
                    if v:rows[t][term]=v
                    else:rows[t].pop(term,None)
            elif op=='scale':
                q=F(g[2],g[3]);q=1/q if dual else q
                rows[g[1]]={term:q*c for term,c in rows[g[1]].items()}
            elif op=='warp':
                d=g[2]
                if not dual and d>50:
                    assert rows[g[1]]=={(g[1],()):F(1)},('new lender not restored',g,rows[g[1]])
                if dual:d=(abs(d)+1000)*(1 if d>0 else -1)
                rows[g[1]]={(r,word[:-1] if word and word[-1]==-d else word+(d,)):c for (r,word),c in rows[g[1]].items()}
            else:raise AssertionError(op)
        for g in program:apply(g)
        if not dual:
            assert all(rows[112+t]=={(112+t,()):F(1),(t,()):F(1)} for t in range(112))
            assert all(rows[r]=={(r,()):F(1)} for r in cold)
            assert all(not any(var in cold-{r} for (var,word) in rows[r]) for r in live)
        for g in w['cleanup']:apply(g)
        for r in live:
            exp={(r,()):F(1)}
            if dual and r<112:exp[(112+r,())]=F(-1)
            if not dual and 112<=r<224:exp[(r-112,())]=F(1)
            assert rows[r]==exp,(dual,r,rows[r])
        assert all(not rows[704+r] for r in cold)
        result['dual' if dual else 'forward']='PASS'
    return result

def main():
    ap=argparse.ArgumentParser(description='Independent exact audit of the late8 local words; standard library only.')
    ap.add_argument('--source2588',type=Path,required=True,help='Pristine authenticated PR2588 package directory')
    ap.add_argument('--words',type=Path,required=True,help='Directory containing eight-alias-base.json.gz and eight-alias-extra.json.gz')
    ap.add_argument('--out',type=Path,required=True,help='Fresh output JSON; existing files are never overwritten')
    args=ap.parse_args()
    if not __debug__:raise RuntimeError('This verifier requires assertions enabled; do not run Python with -O.')
    assert not args.out.exists(),'Output must be a fresh path'
    source_count=authenticate_source(args.source2588)
    base=args.source2588/'new/borrow/words'
    res={}
    for tag in ['base','extra']:
        path=args.words/f'eight-alias-{tag}.json.gz'
        raw=gzip.decompress(path.read_bytes())
        assert sha(raw)==CANDIDATE_CONTENT_SHA256[tag],('candidate content digest',tag)
        oldpath=base/f'BORROW-WORD-43{tag}.json.gz'
        assert sha(gzip.decompress(oldpath.read_bytes()))==SOURCE_CONTENT_SHA256[tag],('source word digest',tag)
        w=load(path);b=load(oldpath)
        report,start,ends=check_frames(w);breport,bstart,bends=check_frames(b)
        report['local_delta']={k:report['profile'].get(k,0)-breport['profile'].get(k,0) for k in set(report['profile'])|set(breport['profile']) if report['profile'].get(k,0)!=breport['profile'].get(k,0)}
        assert report['local_delta']=={1:-4,7:-4,8:4}
        report['baseline_section_profiles']=breport['section_profiles'];report['baseline_center_paths']=breport['center_paths']
        report['cleanup_events']=check_cleanup(w);report['independent_algebra']=algebra(w)
        oldlive=sorted(set(range(224,704))-set(b['removed']));newlive=sorted(set(range(224,704))-set(w['removed']))
        removed=sorted(set(oldlive)-set(newlive));returned=sorted(set(newlive)-set(oldlive))
        assert removed==[680,681,682,684,688,689,690,692]
        assert returned==[596,600,632,633,656,657,658,660]
        m={r:r for r in set(oldlive)&set(newlive)};m.update(zip(removed,returned))
        assert set(m)==set(oldlive) and set(m.values())==set(newlive)
        assert len(m)==len(set(m.values()))==422
        assert all(dm(bends[r])-dm(bstart[r])==dm(ends[m[r]])-dm(start[m[r]]) for r in oldlive)
        # Endpoint classes are preserved per helper, stronger than widths alone.
        assert all(dm(bends[r])==dm(ends[m[r]]) and dm(bstart[r])==dm(start[m[r]]) for r in oldlive)
        got={i:newlive.index(m[r]) for i,r in enumerate(oldlive)}
        handoff=args.words/'HANDOFF.json'
        if handoff.is_file():
            hand=json.loads(handoff.read_text())['providers'][tag]
            assert m=={int(k):v for k,v in hand['origin_mapping'].items()}
            assert got=={int(k):v for k,v in hand['compact_helper_mapping'].items()}
        report['helper_permutation']='PASS_422_bijective_and_endpoint_dimensions_preserved'
        report['helper_origin_changes']={k:v for k,v in m.items() if k!=v}
        report['compact_helper_changes']={k:v for k,v in got.items() if k!=v}
        report['new_word_content_sha256']=sha(raw)
        report['source_word_content_sha256']=SOURCE_CONTENT_SHA256[tag]
        report['new_ops']=[{'op':i,'position':rec[0],'lender':rec[1],'source_rank':rank(rec[3]),'destination_rank':rank(rec[4]),'image_port':im(rec[2],w['ports'][rec[1]])} for i,rec in enumerate(w['warps'],1) if i>50]
        res[tag]=report
    result={'status':'PASS_INDEPENDENT_LATE8_LOCAL_REVIEW','source_manifest_sha256':SOURCE_MANIFEST_SHA256,'authenticated_source_files':source_count,'providers':res,'scope':'Exact local frame and free-operator algebra verification; no independent physical Clifford/phase, owner admission, precision, global invoice, or outer theorem verification.'}
    with args.out.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(result['status'])
    print('Both providers: local delta = 4 H8 - 4 H7 - 4 H1; 422 helper widths and endpoint dimensions preserved.')

if __name__=='__main__':main()
