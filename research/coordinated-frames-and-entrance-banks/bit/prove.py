#!/usr/bin/env python3
"""Frozen PR179 physical bit word, completed entrance banks and exact paid moment.

Checks supplied graph/frame inputs and all formal columns without executing
the foreign producer. The analytic weighted-compiler contracts are retained.
"""
from fractions import Fraction as Q
from pathlib import Path
import gzip,json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE.parent/'arithmetic'))
sys.dont_write_bytecode=True
from word import Candidate,need
from interval_moment import moment,log_interval,exp_interval
from prime_witnesses import certificate as prime_certificate


def js(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):js(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [js(v) for v in x]
    return x


def paid_moment(p,a,details=False):
    raw=moment(p,a,details);m,w=p['m'],p['W']
    count=sum(p['child_multiplicities'].values());bad=Q(1,10**16);fallback=32*m*m
    ll,lu=log_interval(Q(m));el,eu=exp_interval(a*ll,a*lu)
    weight=bad*Q(fallback*count,w*m)
    return dict(saving=a,lower=raw['lower']+weight*el,upper=raw['upper']+weight*eu,
        strict_gap_lower=1-raw['upper']-weight*eu,raw=raw,fallback_lower=weight*el,
        fallback_upper=weight*eu,edge_count=count,fallback_children_per_edge=fallback,
        bad_fraction=bad)



def bank_projectors():
    """Literal address maps on every F2 and integer basis column of two banks."""
    checks=[]
    for width,count in ((4,18),(24,3)):
        owner=[j//width for j in range(72)]
        need([owner.count(s) for s in range(count)]==[width]*count,'actual full bank partition')
        projectors=[[int(owner[j]==s) for j in range(72)] for s in range(count)]
        need(all(sum(P[j] for P in projectors)==1 for j in range(72)),'sum of actual projectors is identity')
        need(all(P[j]*P[j]==P[j] for P in projectors for j in range(72)),'idempotent bank projectors')
        need(all(P[j]*T[j]==0 for s,P in enumerate(projectors) for t,T in enumerate(projectors) if s!=t for j in range(72)),'pairwise disjoint bank projectors')
        def run(column,ring,indices):
            x=[0]*72;y=[0]*72
            (x if column<72 else y)[column%72]=1
            for s in indices:
                P=projectors[s]
                x,y=([a-P[j]*a+P[j]*b for j,(a,b) in enumerate(zip(x,y))],
                     [b-P[j]*b+P[j]*a for j,(a,b) in enumerate(zip(x,y))])
                if ring:x=[a%ring for a in x];y=[a%ring for a in y]
            return x+y
        controls={}
        for ring in (2,0):
            for column in range(144):
                expected=[0]*144;expected[(column+72)%144]=1
                need(run(column,ring,range(count))==expected,'completed bank full dirty swap formal column')
                need(run(column,ring,list(range(count))+list(reversed(range(count))))==[int(j==column) for j in range(144)],'completed bank inverse restores arbitrary contents')
            for tag,indices in (('omit_block',list(range(count-1))),('repeat_block',list(range(count))+[count-1])):
                column=72-width;expected=[0]*144;expected[column+72]=1
                need(run(column,ring,indices)!=expected,'adverse bank control rejected: '+tag)
                controls[str(ring)+':'+tag]=True
        checks.append(dict(width=width,blocks=count,ambient=72,rings=[2,0],formal_columns=288,
            inverse_columns=288,projectors_idempotent=True,projectors_disjoint=True,sum_is_identity=True,
            controls_rejected=controls,endpoint='partialSwap(P)(x,y)=(x-Px+Py,y-Py+Px)'))
    return checks


def packed_row(word,row):
    """Bank WHOLE physical chains; a paired recipient is an internal splice."""
    need((row['h'],row['m'],row['v'],row['reused_registers'])==(24,72,1760,1760),'retained bit dimensions and aliases')
    starts={s:z['dim'] for s,z in word.gauge.items() if s not in word.donor}
    need(len(starts)==row['selected_roles'] and row['selected_rank_histogram']=={20:2200},'actual surviving physical entrances')
    need(set(starts.values())=={20} and len(starts)==2200,'rank20 entrance gauges only')
    need(all(b in word.donor and word.gauge[b]['dim']==21 for b in word.donor),'rank21 recipients are splices, not separate bank roles')
    gauges=len(starts);rest=row['R']-gauges
    need(rest==15828,'every remaining physical role charged')
    H=dict(row['child_histogram'])
    need(H.pop(60,None)==gauges,'remove exactly one rank60 entrance exterior per surviving gauge')
    W=Q(2*word.v)+3*(Q(gauges,18)+Q(rest,3))
    mass=sum(r*n for r,n in H.items())
    need(W==Q(59144,3) and mass==1417520 and 72*W-mass==1936,'complete packed bank telescoping inventory')
    need(max(H)==22 and all(0<r<72 and n>0 for r,n in H.items()),'proper paid bank children')
    need(9*gauges%18==0 and 9*rest%3==0,'stage-private integer bank realization')
    need(3*(9*gauges//18+9*rest//3)+2*9*word.v==9*W,'nine-copy literal stock agrees')
    packed=dict(row,W_per_vertex=W,rank_per_vertex=mass,deficit_per_vertex=1936,child_histogram=H,maxchild=22,
        physical_roles_before_banks=row['R'],bank_roles_per_vertex=W-2*word.v,
        bank=dict(entrance_rank=20,entrance_gauges=gauges,undeferred_physical_roles=rest,
            selected_blocks=18,selected_width=4,undeferred_blocks=3,undeferred_width=24,
            stages=3,physical_chains_spliced=True,physical_replica_count=9,moment_normalization_scale=3,selected_banks_per_stage=1100,undeferred_banks_per_stage=47484),
        bank_projector_checks=bank_projectors())
    expected=json.loads((HERE/'banks.json').read_text())
    ep=expected['profile']
    need(Q(ep['W_per_vertex'])==W and ep['rank_per_vertex']==mass and ep['deficit_per_vertex']==1936,'stored packed dimensions')
    need({int(r):n for r,n in ep['child_multiplicities'].items()}==H,'stored entire packed histogram')
    need(expected['bank']==dict(entrance_rank=20,entrance_gauges=gauges,undeferred_physical_roles=rest),'stored actual bank role classes')
    return packed


def independent_bank_moment(row,coarse):
    from base_two_moment import moment as alternate_moment
    W=int(3*row['W_per_vertex']);H=[(r,3*n) for r,n in row['child_histogram'].items()]
    count=sum(n for r,n in H);fallback=32*72**2*count
    _,upper=alternate_moment(72,W,H,coarse['coarse_saving'])
    _,bad_upper=alternate_moment(72,W,[(1,fallback)],coarse['coarse_saving'])
    gap=1-upper-Q(1,10**16)*bad_upper
    need(gap>0,'independent base-two paid moment contracts')
    next_saving=coarse['coarse_saving']+Q(1,coarse['coarse_grid'])
    lower,_=alternate_moment(72,W,H,next_saving)
    bad_lower,_=alternate_moment(72,W,[(1,fallback)],next_saving)
    need(lower+Q(1,10**16)*bad_lower>1,'independent base-two adjacent paid moment exclusion')
    return gap


def certify(row):
    p=dict(m=row['m'],W=row['W_per_vertex'],N=row['deficit_per_vertex'],L=0,
        total_rank=row['rank_per_vertex'],maxchild=row['maxchild'],child_multiplicities=row['child_histogram'])
    # Scale three clears the normalized moment fractions; the stage-private physical realization uses nine copies.
    p=dict(p,W=int(3*Q(p['W'])),N=3*p['N'],total_rank=3*p['total_rank'],
        child_multiplicities={r:3*n for r,n in p['child_multiplicities'].items()})
    grid=10**18;lo=0;hi=grid//100
    need(paid_moment(p,Q(lo,grid))['upper']<1,'zero-saving rank contraction')
    need(paid_moment(p,Q(hi,grid))['lower']>1,'upper bracket')
    while hi-lo>1:
        mid=(lo+hi)//2;r=paid_moment(p,Q(mid,grid))
        if r['upper']<1:lo=mid
        elif r['lower']>1:hi=mid
        else:raise ValueError('increase moment precision')
    coarse=Q(lo,grid);accepted=paid_moment(p,coarse,True);rejected=paid_moment(p,Q(hi,grid),True)
    need(accepted['upper']<1<rejected['lower'],'adjacent grid paid-moment proof')
    old=Q(384599,10**10);threshold=coarse/(1+coarse-old);atomgrid=10**24
    floor=(threshold*atomgrid).numerator//(threshold*atomgrid).denominator
    atom=Q(floor+1,atomgrid);actual=(1-atom)*coarse+atom*old
    need(actual<atom<1-actual,'paid atom and row adapter toll')
    need(Q(2*p['m']**3,2**80)<Q(1,10**16),'fixed prime rare-class bound')
    need(Q(p['total_rank'])+accepted['bad_fraction']*accepted['fallback_children_per_edge']*accepted['edge_count']<p['W']*p['m'],'contaminated mass contracts')
    previous=atom-Q(1,atomgrid)
    need(previous<=(1-previous)*coarse+previous*old,'previous atom grid does not pay strict toll')
    return dict(coarse_saving=coarse,accepted=accepted,rejected=rejected,coarse_grid=grid,
        atom_beta=atom,old_atom_saving=old,ordinary_saving=actual,atom_threshold=threshold,
        atom_grid=atomgrid,atom_lower_gap=atom-actual,atom_upper_gap=1-actual-atom,
        controls=dict(next_coarse_grid_rejected=True,previous_atom_grid_rejected=True),
        scope='Adjacent coarse exclusion for this fixed worst-case bad-class envelope and least atom on the stated grid; no true bad-fraction or global optimality claim.')


def main():
    need(not sys.flags.optimize,'assertions enabled')
    word=Candidate();word.exact_frames();row=word.row()
    need(row['changed_operation_frames']==2884 and row['reused_registers']==1760,'selected PR168-v4 replacement frames and physical aliases')
    reference=json.loads((HERE.parent/'references/pr168/bit-physical-profile.json').read_text())
    for k in ('h','v','m','W_per_vertex','rank_per_vertex','deficit_per_vertex','loss'):
        need(row[k]==reference[k],'independent physical profile agrees: '+k)
    need(row['R']==reference['physical_R'],'independent physical role count')
    need(row['child_histogram']=={int(k):n for k,n in reference['child_histogram'].items()},'independent complete physical histogram')
    formal=[word.formal(r) for r in (2,0)]
    controls=[]
    for tamper in ('omit_compensation','missing_partner','stale'):
        try:word.formal(2,tamper)
        except ValueError:controls.append(tamper)
        else:raise ValueError('Adverse word control accepted: '+tamper)
    i=word.changed_frames[0];old=word.opframe[i];word.opframe[i]=word.register([])
    try:word.exact_frames()
    except ValueError:controls.append('zero_operation_frame')
    else:raise ValueError('Zero frame accepted')
    word.opframe[i]=old
    packed=packed_row(word,row)
    coarse=certify(packed)
    independent_gap=independent_bank_moment(packed,coarse)
    expected=json.loads((HERE/'banks.json').read_text())
    need(coarse['coarse_saving']==Q(expected['coarse']) and coarse['atom_beta']==Q(expected['atom']) and coarse['ordinary_saving']==Q(expected['effective']),'stored exact paid bank savings')
    primes=prime_certificate(word)
    need(primes==json.loads(gzip.decompress((HERE/'prime-witnesses.json.gz').read_bytes())),'source-bound all-frame prime witness reproduction')
    need(primes['total_operation_frames']==row['changed_operation_frames'] and primes['h']==row['h'],'prime witnesses cover changed frames')
    from hashlib import sha256
    prime_summary={k:v for k,v in primes.items() if k!='frame_witnesses'}
    prime_summary['witness_file']='bit/prime-witnesses.json.gz'
    prime_summary['witness_sha256']=sha256((HERE/'prime-witnesses.json.gz').read_bytes()).hexdigest()
    print(json.dumps(js(dict(status='PASS',profile=packed,inherited_profile=row,formal=formal,coarse=coarse,prime_witnesses=prime_summary,word_controls=controls,independent_moment_gap=independent_gap,
        foreign_producer_replays=0,scope='Complete F2 identity and integer decoder on every source, target and dirty column; exact spliced physical frames; completed18x4/3x24 bank projectors; independent paid moments and atom toll. The inherited weighted compiler, bank routing, stage cover and all-size recovery contracts remain conditional.')),sort_keys=True))


if __name__=='__main__':main()
