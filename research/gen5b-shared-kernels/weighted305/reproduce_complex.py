"""Independently authored complex-certificate dimension path and moment audit.

Only inert primary JSON is consumed. This is not a scalar map or Lean replay.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as F
import hashlib,gzip,json
import reproduce_pr305 as base

def profile():
    pins=base.read('inputs/complex/source-pins.json')['certificate']
    packed=(base.SOURCE/pins['path']).read_bytes();raw=gzip.decompress(packed)
    assert hashlib.sha256(packed).hexdigest()==pins['compressed_sha256']
    assert hashlib.sha256(raw).hexdigest()==pins['uncompressed_sha256']
    c=json.loads(raw)
    h,v,R=c['h'],c['v'],c['R'];assert(h,v,R)==(22,1320,9412)
    frames=c['frames'];dims=list(map(len,frames));current=c['start'][:]
    assert len(current)==len(c['final'])==2*v+R
    assert frames[0]==[] and dims[1]==h
    for frame in frames:
        pivots=[x.bit_length()-1 for x in frame]
        assert pivots==sorted(set(pivots),reverse=True)
        assert all(type(x)is int and 0<x<1<<h for x in frame)
    checked=set();byrole={label:Counter() for label in ('x','y','s','c')}
    byphase={label:Counter() for label in ('A','copy','B','final')}
    def visit(reg,after,phase):
        before=current[reg]
        if before==after:return
        assert dims[after]>dims[before]
        pair=(before,after)
        if pair not in checked:
            for vector in frames[before]:
                remainder=vector
                for basis in frames[after]:
                    if remainder&(1<<(basis.bit_length()-1)):remainder^=basis
                assert remainder==0
            checked.add(pair)
        rank=dims[after]-dims[before]
        label='x' if reg<v else 'y' if reg<2*v else 's'
        byrole[label][rank]+=1;byphase[phase][rank]+=1;current[reg]=after
    for phase in ('A','B'):
        for row in c[phase]:
            kind,frame,pivot,terms=row[:4]
            assert kind in ('in','out')
            registers=[pivot]+[term[0] for term in terms]
            if kind=='out':registers+=row[4]
            assert len(registers)==len(set(registers))
            for reg in registers:
                assert 0<=reg<len(current)
                visit(reg,frame,phase)
        if phase=='A':
            for _,reg,frame in c['ret']:
                assert current[reg]==frame and dims[frame]==20
                byrole['c'][dims[frame]]+=1;byphase['copy'][dims[frame]]+=1
    for reg,frame in enumerate(c['final']):visit(reg,frame,'final')
    assert current==c['final']
    for role,hist in byrole.items():assert base.clean(hist)==dict(base.histogram(c['blocks'][role]))
    invocation=Counter()
    for hist in byrole.values():invocation.update(hist)
    assert base.mass(invocation)==c['N']==R*h+2*v*(h-1)+c['cst']
    H=Counter({rank:5*n for rank,n in invocation.items()})
    for rank in (2*h-2,h-1,2*h+2,4):H[rank]+=2*v
    m=5*h;W=4*v+R
    assert(sum(H.values()),base.mass(H),m*W-base.mass(H),max(H))==(358975,1613040,3080,46)
    return H,dict(invocation_histogram=base.clean(invocation),invocation_calls=sum(invocation.values()),
        invocation_rank_mass=base.mass(invocation),role_histograms={r:base.clean(x) for r,x in byrole.items()},
        phase_histograms={r:base.clean(x) for r,x in byphase.items()},tested_nested_frame_pairs=len(checked),
        five_stage_histogram=base.clean(H),m=m,W=W,calls=sum(H.values()),rank_mass=base.mass(H),deficit=m*W-base.mass(H),
        certificate_sha256=pins['compressed_sha256'],scope='Dimension path and binary frame containment census only; no complex scalar identity, inherited geometry theorem, or physical assembly replay.')

def run():
    base.verify_sources()
    H,receipt=profile();root=base.bracket(H,receipt['m'],receipt['W'],bad=False)
    b=F(754736418878859,10**18)
    assert root['lower']==b
    receipt.update(status='PASS_INDEPENDENT_COMPLEX_DECLARED_PROFILE_MOMENT',root_bracket=root,
        chosen_coarse=b,moment_at_chosen_coarse=base.moment(H,110,14692,b,bad=False))
    return receipt

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    report=run()
    (base.HERE/'complex-receipt.json').write_text(json.dumps(base.ae.serial(report),indent=2)+'\n')
    print(json.dumps(base.ae.serial(dict(calls=report['calls'],rank_mass=report['rank_mass'],
        root_bracket=[report['root_bracket'][k] for k in ('lower','upper')],
        residuals=[base.ex.dec(report['root_bracket']['lower_moment'][1]-1),base.ex.dec(report['root_bracket']['upper_moment'][0]-1)])),indent=2))
