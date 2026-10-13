#!/usr/bin/env python3
"""Raise eight PR699 interior frames with unchanged scalar word and boundaries.

Apache-2.0. OpenAI Codex research contribution with substantial AI assistance.
The chain accounting follows BlockInvert's promotion constructor; the independent
scalar/frame audit imported by the replay driver shares no builder code.
"""
import argparse, collections, gzip, hashlib, json
from pathlib import Path


def basis(vs):
    p = {}
    for x in vs:
        for k in sorted(p, reverse=True):
            if x >> k & 1: x ^= p[k]
        if x:
            k = x.bit_length()-1
            for j in list(p):
                if p[j] >> k & 1: p[j] ^= x
            p[k] = x
    return tuple(p[k] for k in sorted(p, reverse=True))


def contained(a, b): return basis(tuple(a)+tuple(b)) == basis(b)
def regs(e): return e[1:3] if e[0] == 'add' else e[1:2]


def endpoints(w):
    v, h, R = (w['report'][k] for k in ('v','h','R')); n=2*v+R
    full = basis(1<<k for k in range(h)); start=[()] * n; end=[full] * n
    for i,p in enumerate(w['ports']):
        start[i]=(p,)
        end[v+i]=basis(x for x in range(1,1<<h) if (x&p).bit_count()%2==0)
    for r,f in w['start_extra'].items(): start[int(r)]=basis(f)
    for r,f in w['helper_final'].items(): end[int(r)]=basis(f)
    return start,end


def events(w):
    for sec in ('A','B'):
        for i,e in enumerate(w[sec]): yield sec,i,regs(e),basis(e[-1])
    for i,(j,f) in enumerate(w['early_cleanup']): yield 'T',i,regs(w['cleanup'][j]),basis(f)


def profile(w):
    cur,end = endpoints(w); paid=collections.Counter()
    for sec,i,rs,f in events(w):
        for r in rs:
            assert contained(cur[r],f), ('nonmonotone',sec,i,r)
            d=len(f)-len(cur[r])
            if d: paid[d]+=1
            cur[r]=f
    for r,f in enumerate(end):
        assert contained(cur[r],f), ('nonmonotone final',r)
        d=len(f)-len(cur[r])
        if d: paid[d]+=1
    # The center descents are fixed by the exact ordered center interface.
    v=w['report']['v']; levels={int(r):basis(f) for r,f in w.get('target_levels',{}).items()}
    for q,U in zip(w['centers'],w['center_frames']):
        U=basis(U); served={levels.get(e[1]-v,()) for e in w['cut'] if e[2]==q}
        for T in sorted(served,key=lambda x:-len(x)):
            assert contained(T,U), 'center descents not nested'
            if T!=U: paid[len(U)-len(T)]+=1
            U=T
    return {str(k):c for k,c in sorted(paid.items()) if c}


def width_inventory(w):
    start,end=endpoints(w); v=w['report']['v']
    return {str(k):c for k,c in sorted(collections.Counter(len(end[r])-len(start[r]) for r in range(2*v,len(start))).items())}


def frame_bounds(w, section, index):
    cur,end=endpoints(w); stream=list(events(w)); at=next(j for j,e in enumerate(stream) if e[:2]==(section,index))
    for _,_,rs,f in stream[:at]:
        for r in rs: cur[r]=f
    rs=stream[at][2]; lower=basis(x for r in rs for x in cur[r]); next_frames={r:end[r] for r in rs}
    unseen=set(rs)
    for _,_,qs,f in stream[at+1:]:
        for r in unseen.intersection(qs): next_frames[r]=f
        unseen.difference_update(qs)
        if not unseen: break
    # Every chosen basis vector must lie in every successor frame. Since these
    # are linear spaces, this checks containment in their exact intersection.
    return rs,lower,next_frames


def apply(w, recipe):
    z=json.loads(json.dumps(w)); assert profile(w)==recipe['baseline_profile']==w['report']['local_profile'], 'baseline paid profile'
    records=[]; oldprofile=profile(w)
    for change in recipe['changes']:
        sec,i=change['section'],change['index']; assert sec=='B', 'only interior B gates are changed'
        assert z[sec][i][-1]==change['old'], ('old frame mismatch',sec,i)
        rs,lower,caps=frame_bounds(z,sec,i); old,new=basis(change['old']),basis(change['new'])
        assert contained(old,new) and len(new)>len(old), ('not a strict frame raise',sec,i)
        assert contained(lower,new), ('below operand frame',sec,i)
        assert all(contained(new,f) for f in caps.values()), ('above successor cap',sec,i)
        z[sec][i][-1]=list(new); current=profile(z)
        delta={k:current.get(k,0)-oldprofile.get(k,0) for k in sorted(set(current)|set(oldprofile))}
        delta={k:c for k,c in delta.items() if c}
        assert delta==recipe['expected_step_delta'], ('step profile delta',sec,i,delta)
        records.append(dict(section=sec,index=i,registers=rs,operand_span=list(lower),successor_frames=caps,delta=delta))
        oldprofile=current
    assert oldprofile==recipe['profile'], 'final profile'
    z['report']['local_profile']=oldprofile
    z['report']['local_rank_mass']=sum(int(k)*c for k,c in oldprofile.items())
    assert width_inventory(z)==recipe['expected_width_inventory']==width_inventory(w), 'width changed'
    assert z['report']['local_rank_mass']==w['report']['local_rank_mass'], 'rank mass changed'
    # Restore all permitted edits and require exact equality of every other field.
    check=json.loads(json.dumps(z))
    for change in recipe['changes']: check[change['section']][change['index']][-1]=change['old']
    check['report']=w['report']; assert check==w, 'scalar or boundary field changed'
    return z,records


def main():
    if not __debug__: raise RuntimeError('Assertions are required; do not use Python -O')
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ('input','recipe','out'): ap.add_argument('--'+k,type=Path,required=True)
    a=ap.parse_args(); raw=gzip.decompress(a.input.read_bytes()); recipe=json.loads(a.recipe.read_text())
    assert hashlib.sha256(raw).hexdigest()==recipe['input_sha256'], 'input word pin'
    z,records=apply(json.loads(raw),recipe); data=json.dumps(z,separators=(',',':')).encode()
    assert hashlib.sha256(data).hexdigest()==recipe['output_sha256'], 'output word pin'
    a.out.mkdir(parents=True,exist_ok=False)
    (a.out/'FULL-WORD.json.gz').write_bytes(gzip.compress(data,mtime=0))
    (a.out/'FRAME-CHECKS.json').write_text(json.dumps(dict(status='PASS_EIGHT_EXACT_CAPPED_INTERIOR_FRAME_RAISES',records=records,profile=profile(z),width_inventory=width_inventory(z)),indent=2)+'\n')
    print('PASS_EIGHT_EXACT_CAPPED_INTERIOR_FRAME_RAISES',recipe['output_sha256'],flush=True)


if __name__=='__main__': main()
