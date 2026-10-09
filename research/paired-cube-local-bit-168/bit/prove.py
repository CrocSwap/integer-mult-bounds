#!/usr/bin/env python3
"""PR168-v4 physical bit word with 556 frame overrides and 34 terminal sinks, exact paid moment and positive atom toll.

Checks supplied graph/frame inputs and all formal columns without executing
the foreign producer. The analytic weighted-compiler contracts are retained.
"""
from fractions import Fraction as Q
from pathlib import Path
import contextlib,gzip,json
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


def certify(row):
    p=dict(m=row['m'],W=row['W_per_vertex'],N=row['deficit_per_vertex'],L=0,
        total_rank=row['rank_per_vertex'],maxchild=row['maxchild'],child_multiplicities=row['child_histogram'])
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
    need(row['changed_operation_frames']==2884+556-row['restored_frames'] if 'restored_frames' in row else True,'frame inventory')
    need(row['reused_registers']==1760,'physical aliases retained')
    reference=json.loads((HERE.parent/'references/pr168/bit-physical-profile.json').read_text())
    # The published parent layer (no overrides) must reproduce PR168 v4's physical profile.
    final_frames=word.opframe;final_changed=word.changed_frames;final_end=word.endframe
    word.opframe=list(word.baseline_opframe)
    word.changed_frames=[i for i,(a,b) in enumerate(zip(word.original_opframe,word.opframe)) if a!=b]
    word.endframe={s:word.opframe[xs[-1]] for s,xs in word.role_ops.items()}
    word.exact_frames();parent_row=word.row()
    need(parent_row['changed_operation_frames']==2884 and parent_row['reused_registers']==1760,'PR168-v4 replacement frames and physical aliases')
    for k in ('h','v','m','W_per_vertex','rank_per_vertex','deficit_per_vertex','loss'):
        need(parent_row[k]==reference[k],'independent parent physical profile agrees: '+k)
    need(parent_row['R']==reference['physical_R'],'independent parent physical role count')
    need(parent_row['child_histogram']=={int(k):n for k,n in reference['child_histogram'].items()},'independent complete parent physical histogram')
    word.opframe=final_frames;word.changed_frames=final_changed;word.endframe=final_end
    need(row['child_histogram']=={int(k):n for k,n in json.loads((HERE.parent/'selected/bit/overrides.json').read_text())['child_histogram'].items()},'independent complete overridden physical histogram')
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
    from terminal import prove as prove_terminal
    selection=json.loads((HERE.parent/'selected/bit/sinks.json').read_text())
    with contextlib.redirect_stdout(sys.stderr):terminal=prove_terminal(word,selection)
    terminal.pop('seconds');terminal.pop('maxrss')
    overridden_row=row;row=terminal['profile']
    row['child_histogram']={int(k):n for k,n in row['child_histogram'].items()}
    need(row['terminal_sinks']==34 and terminal['scalar_addition_delta']<=0,'terminal sink count and retained scalar bill')
    need(row['W_per_vertex']==overridden_row['W_per_vertex']-34 and row['R']==overridden_row['R']-34,'terminal removals reduce stock by the sink count')
    coarse=certify(row)
    primes=prime_certificate(word)
    need(primes==json.loads(gzip.decompress((HERE/'prime-witnesses.json.gz').read_bytes())),'source-bound all-frame prime witness reproduction')
    need(primes['total_operation_frames']==row['changed_operation_frames'] and primes['h']==row['h'],'prime witnesses cover changed frames')
    from hashlib import sha256
    prime_summary={k:v for k,v in primes.items() if k!='frame_witnesses'}
    prime_summary['witness_file']='bit/prime-witnesses.json.gz'
    prime_summary['witness_sha256']=sha256((HERE/'prime-witnesses.json.gz').read_bytes()).hexdigest()
    print(json.dumps(js(dict(status='PASS',profile=row,overridden_profile=overridden_row,parent_profile=parent_row,terminal=terminal,formal=formal,coarse=coarse,prime_witnesses=prime_summary,word_controls=controls,
        foreign_producer_replays=0,scope='Complete F2 identity, integer defining decoder, exact physical frame geometry and retained weighted-compiler contracts.')),sort_keys=True))


if __name__=='__main__':main()
