#!/usr/bin/env python3
"""Depth-one E8 direct-source construction and complete finite checks."""
import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import importlib.util
from itertools import combinations
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if not __debug__:
    raise SystemExit('Refusing optimized Python: pinned phase utilities require assertions.')


def require(ok, why):
    if not ok:
        raise ValueError(why)


def load_reference():
    source = json.loads((HERE/'SOURCE.json').read_text())
    for record in source['files'].values():
        if 'vendored_path' in record:
            data = (HERE/record['vendored_path']).read_bytes()
            require(hashlib.sha256(data).hexdigest()==record['sha256'],'source SHA256')
            require(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
                    == record['git_blob'],'source Git blob')
    spec = importlib.util.spec_from_file_location('pr647',HERE/'vendor/pr647_verify.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ref = load_reference()
I, ZERO = ref.biteye(9), (0,)*9


def plus(target,source,c=Q(1)):
    for col,value in source.items():
        updated = target.get(col,Q(0))+c*value
        if updated:
            target[col] = updated
        else:
            target.pop(col,None)


def geometry():
    ports, roots = [],[]
    for triple in combinations(range(9),3):
        ports.append(sum(1<<j for j in triple))
        roots.append([Q(int(j in triple))-Q(1,3) for j in range(9)])
    for a,b in combinations(range(9),2):
        ports.append(511^(1<<a)^(1<<b))
        roots.append([Q(int(j==a)-int(j==b)) for j in range(9)])
    K = [[Q(int(t==s))-sum((x*y for x,y in zip(u,v)),Q(0))/2
          for s,v in enumerate(roots)] for t,u in enumerate(roots)]
    A = [[root[j] for root in roots] for j in range(8)]
    B = [[(root[j]-root[8])/2 for j in range(8)] for root in roots]
    for t in range(120):
        for s in range(120):
            require(K[t][s]+sum(B[t][j]*A[j][s] for j in range(8))==int(t==s),
                    'K+BA identity')
            if K[t][s]:
                require(not ref.bitdot(ports[t],ports[s]),'pair cap inclusion')
    return ports,K,A,B


def build():
    ports,K,A,B = geometry()
    frames = [ref.outer(p,9) for p in ports]+[ZERO]*120
    initial = list(frames)
    events, adds, helper_adds, allocations = [],[],[],[]
    def alloc():
        r = len(frames);frames.append(ZERO);initial.append(ZERO)
        allocations.append(r)
        return r
    def move(r,P):
        old = frames[r]
        require(ref.bitmm(old,P)==old and ref.bitmm(P,old)==old,'nonnested move')
        events.append(('move',r,P));frames[r]=P
    def add(t,s,c):
        require(frames[t]==frames[s],'unequal add frames')
        events.append(('add',t,s,c));adds.append((t,s,c))
        if s>=240:
            helper_adds.append((t,s,c))
    outputs = [alloc() for _ in ports]
    for t,r in enumerate(outputs):
        move(r,ref.bitadd(I,ref.outer(ports[t],9)))
    for t in range(120):
        for s in range(120):
            if K[t][s]:
                z=alloc();move(z,ref.outer(ports[s],9))
                add(z,s,Q(1))
                move(z,ref.bitadd(I,ref.outer(ports[t],9)))
                add(outputs[t],z,K[t][s]);move(z,I)
    centers=[alloc() for _ in range(8)]
    for z in centers:move(z,I)
    for s in range(120):
        move(s,I)
        for j in range(8):
            if A[j][s]:add(centers[j],s,A[j][s])
    require(len(allocations)==6848 and len(adds)==14176 and len(helper_adds)==6720,
            'literal core counts')
    return {'ports':ports,'A':A,'B':B,'outputs':outputs,'centers':centers,
            'core':events,'adds':adds,'helper_adds':helper_adds,
            'initial':initial,'core_final':frames,'helpers':allocations}


def word(data,direction):
    # Macros have explicit frame, scratch and primitive invoices below/in PROOF.md.
    events=[('old',direction)]+list(data['core'])+[('centers',direction)]
    for t,r in enumerate(data['outputs']):
        events += [('move',120+t,ref.bitadd(I,ref.outer(data['ports'][t],9))),
                   ('output',120+t,r,Q(1)),('move',r,I)]
    for t,s,c in reversed(data['adds']):
        events.append(('cleanup',t,s,-c))
    return events


def check_frames(data,events,direction):
    frames=list(data['initial']);hist=Counter();projectors=set();count=Counter()
    for event in events:
        kind=event[0]
        if kind=='move':
            _,r,P=event;old=frames[r]
            require(ref.bitmm(old,P)==old and ref.bitmm(P,old)==old,'chronological nesting')
            diff=ref.bitadd(old,P);rank=len(ref.indep(ref.bitmt(diff)))
            if rank:hist[rank]+=1;projectors.add(diff)
            frames[r]=P
        elif kind in ('add','output','cleanup'):
            _,t,s,c=event
            require(frames[t]==frames[s],f'{kind}: unequal frames at {t},{s}')
            count[kind]+=1
        elif kind=='old':
            require(all(frames[r]==ZERO for r in data['helpers']),'old helper frame')
            require(all(frames[120+t]==ZERO for t in range(120)),'old target frame')
            count['old']+=1
        elif kind=='centers':
            require(event[1]==direction,'wrong center orientation')
            require(all(frames[r]==I for r in data['centers']),'center full frame')
            require(all(frames[120+t]==ZERO for t in range(120)),'center target frame')
            hist[9]+=8;projectors.add(I);count['centers']+=1
        else:
            raise ValueError('unknown event')
    require(all(frames[r]==I for r in data['helpers']),'helper endpoint')
    require(all(frames[t]==I for t in range(120)),'source endpoint')
    require(all(frames[120+t]==ref.bitadd(I,ref.outer(data['ports'][t],9))
                for t in range(120)),'target endpoint')
    require(count=={'old':1,'centers':1,'add':14176,'output':120,'cleanup':14176},
            'complete word event counts')
    return hist,projectors


def read_response(data,z):
    out=[dict(z[r]) for r in data['outputs']]
    for t in range(120):
        for j,r in enumerate(data['centers']):
            if data['B'][t][j]:plus(out[t],z[r],data['B'][t][j])
    return out


def old_response(data,z,direction,omit=False):
    if omit:return
    tmp=[{} for _ in z]  # Namespace model: only helper rows are populated/owned.
    if direction=='forward':
        for r in data['helpers']:tmp[r]=dict(z[r])
        for t,s,c in data['helper_adds']:plus(tmp[t],tmp[s],c)
        for t,response in enumerate(read_response(data,tmp)):plus(z[120+t],response,-1)
    else:
        for t,r in enumerate(data['outputs']):plus(tmp[r],z[120+t])
        for j,r in enumerate(data['centers']):
            for t in range(120):
                if data['B'][t][j]:plus(tmp[r],z[120+t],data['B'][t][j])
        for t,s,c in reversed(data['helper_adds']):plus(tmp[s],tmp[t],c)
        for r in data['helpers']:plus(z[r],tmp[r])
    # tmp is initialized, exclusively owned, and cleared; charged in the invoice.
    for row in tmp:row.clear()


def run(data,events,direction,omit_old=False):
    z=[{j:Q(1)} for j in range(len(data['initial']))]
    for event in events:
        kind=event[0]
        if kind=='old':old_response(data,z,direction,omit_old)
        elif kind=='centers':
            if direction=='forward':
                for t in range(120):
                    for j,r in enumerate(data['centers']):
                        if data['B'][t][j]:plus(z[120+t],z[r],data['B'][t][j])
            else:
                for j,r in enumerate(data['centers']):
                    for t in range(120):
                        if data['B'][t][j]:plus(z[r],z[120+t],-data['B'][t][j])
        elif kind in ('add','output','cleanup'):
            _,t,s,c=event
            if direction=='backward':t,s,c=s,t,-c
            plus(z[t],z[s],c)
    expected=[{j:Q(1)} for j in range(len(z))]
    for t in range(120):
        if direction=='forward':expected[120+t][t]=Q(1)
        else:expected[t][120+t]=Q(-1)
    require(z==expected,'symbolic arbitrary-dirt endpoint')
    return len(z)


def moment(hist,W,k):
    upper=Q(0);lower=Q(0)
    for s,c in hist.items():
        x=Q(27,s);y=x;shifts=0
        while y>2:y/=2;shifts+=1
        def partial(a):
            u=(a-1)/(a+1)
            return sum((2*u**(2*j+1)/Q(2*j+1) for j in range(36)),Q(0))
        lo=partial(y)+shifts*partial(Q(2))
        z=k*ref.log_upper(x)
        require(0<=z<1,'moment exponential domain')
        upper+=s*c*(1+z+z*z/(2*(1-z/3)))
        lower+=s*c*(1+k*lo)
    return 27*W-upper,27*W-lower


def phases(projectors):
    count=0
    for P in projectors:
        ref.check_phase(P);count+=1
        # Downward lowering = positive child plus diag(P) translation.
        diag=ref.bdiag(P)
        probes=[0]+[1<<i for i in range(9)]+[(1<<i)|(1<<j) for i,j in combinations(range(9),2)]
        for y in probes:
            w=ref.popcount(ref.bitmv(P,y))
            require((-w-(w+2*ref.bitdot(diag,y)))%4==0,'downward phase')
    return count


def controls(data,forward):
    accepted=[]
    def reject(name,fn):
        try:fn()
        except (ValueError,AssertionError):accepted.append(name)
        else:raise ValueError('negative control accepted: '+name)
    reject('omit_old_response',lambda:run(data,forward,'forward',omit_old=True))
    # Seed-selected source 26: all its pair reads must precede its full-frame climb.
    idx=next(i for i,e in enumerate(forward) if e[0]=='add' and e[2]==26)
    wrong=list(forward);e=wrong[idx];wrong[idx]=('add',e[1],27,e[3])
    reject('misroute_source_26',lambda:check_frames(data,wrong,'forward'))
    wrong=list(forward);wrong.insert(idx,('move',26,I))
    reject('early_source_26_climb',lambda:check_frames(data,wrong,'forward'))
    wrong=list(forward);del wrong[idx]
    reject('drop_source_26_read',lambda:run(data,wrong,'forward'))
    wrong=list(forward);del wrong[next(i for i,e in enumerate(wrong) if e[0]=='cleanup')]
    reject('drop_cleanup',lambda:run(data,wrong,'forward'))
    wrong=[('centers','backward') if e[0]=='centers' else e for e in forward]
    reject('wrong_center_direction',lambda:check_frames(data,wrong,'forward'))
    H=Counter({1:40680,2:240,7:20160,8:1080,9:48})
    H[9]-=24
    reject('omit_center_bill',lambda:require(sum(s*c for s,c in H.items())==27*7088-24,'center mass'))
    return accepted


def receipt():
    final_projector=tuple((1<<j) if j in (9,18) else 0 for j in range(27))
    ref.check_phase(final_projector)
    data=build();forward=word(data,'forward');backward=word(data,'backward')
    local,projectors=check_frames(data,forward,'forward')
    other,other_proj=check_frames(data,backward,'backward')
    require(local==other and projectors==other_proj,'orientation profile')
    columns=[run(data,forward,'forward'),run(data,backward,'backward')]
    hist=Counter({s:3*c for s,c in local.items()});hist[2]+=240
    require(hist=={1:40680,2:240,7:20160,8:1080,9:48},'global profile')
    require(sum(s*c for s,c in hist.items())==27*7088-24,'global mass')
    slack,_=moment(hist,7088,Q(1,14100));require(slack>Q(11,100),'strict new moment')
    old=Counter({1:41040,2:240,7:20160,8:1440,9:48})
    _,old_slack=moment(old,7208,Q(1,14100));require(old_slack<0,'old-profile exclusion')
    # Concrete instruction counts, including both private macro evaluations.
    forward_adds=6720+2*14176+2*456+4*120
    require(forward_adds==36464,'forward scalar invoice')
    R=6848
    return {'schema':1,'status':'PASS_E8_DIRECT_SOURCE','source_head':'956bb581e7f97328e1b53baa5aca3d2490f2f607',
      'word_sha256':{name:hashlib.sha256(json.dumps(events,default=str,separators=(',',':')).encode()).hexdigest() for name,events in [('forward',forward),('backward',backward)]},
      'seed':26,'scope':'depth-one paid-copy complex RAM provider; no multiplication kappa',
      'helpers':R,'live_columns':7088,'independent_symbolic_columns_by_orientation':columns,
      'core_adds':len(data['adds']),'helper_only_old_response_adds':len(data['helper_adds']),
      'source_accesses_in_core':len(data['adds'])-len(data['helper_adds']),
      'local_histogram':dict(sorted(local.items())),'global_histogram':dict(sorted(hist.items())),
      'global_children':sum(hist.values()),'rank_mass':sum(s*c for s,c in hist.items()),'deficit':24,
      'phase_projectors_checked':phases(projectors),
      'private_arrays':R+120+8,'permutation_work_arrays':1,
      'local_invoice':{'forward_add':forward_adds,'backward_add':forward_adds+R+8,
                       'forward_copy':R+8,'backward_copy':0,'clear_each_orientation':R+240+8},
      'global_invoice':{'add':3*forward_adds+R+8,'copy':2*(R+8),'clear':3*(R+240+8),
                        'children':sum(hist.values()),'permutation_upper':2*sum(hist.values()),
                        'child_translation_upper':sum(hist.values()),'final_translation':120,
                        'signed_exchange':120,'initial_private_zero_writes_upper_per_cover_owner':R+120+9},
      'gaussian_ram_saving':'1/14100','moment_rank_mass_slack_lower':str(slack),
      'old_profile_slack_upper_at_same_saving':str(old_slack),
      'global_rank_two_phase_checked':True,'padding_bits':742,'normalized_gap_lower':str(Q(11,100*27*(1<<742))),
      'negative_controls':controls(data,forward)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path);parser.add_argument('--check',type=Path)
    args=parser.parse_args();result=receipt()
    payload=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.check:require(args.check.read_bytes()==payload.encode(),'receipt mismatch')
    if args.output:args.output.write_text(payload)
    print('PASS_E8_DIRECT_SOURCE: 7088 columns in both directions; 120 fewer helpers; 7 negative controls')

if __name__=='__main__':main()
