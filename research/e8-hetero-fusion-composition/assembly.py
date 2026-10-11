"""Exact positive-slack refinement and explicit retained outer cutoff.

The unchanged baseline assembly executes with the single displayed literal
replacement. Numeric cutoff comparisons follow the retained PR34 all-interval
argument in research/copied-fixed/balanced_assembly.py (source SHA recorded
below). They supplement, rather than replace, prime/setup/recovery and the
stage-specific dominating C_full cutoff obligations. OpenAI Codex assistance.
"""
from pathlib import Path
from fractions import Fraction as Q
import hashlib,types
BASELINE_SHA='fe545811e9e858c9ca616d64f3348b797319a51f1dfa8097588ab117bf78e82c'
CUTOFF_SOURCE_SHA='4d27575dcad2b45a281a34054d311409ecd954f373c0c3a62c29bcc843f06a86'
OLD='eta, beta = Q(1,10**24), Q(1,10**9)'
NEW='eta, beta = Q(1,10**30), Q(1,10**30)'
def ceil(q):return -((-q.numerator)//q.denominator)
def run(baseline,parent,priced,finite,supplier):
    path=Path(baseline)/'assembly.py';raw=path.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==BASELINE_SHA
    text=raw.decode();assert text.count(OLD)==1 and NEW not in text
    changed=text.replace(OLD,NEW);module=types.ModuleType('smaller_positive_slack_assembly')
    module.__file__=str(path);exec(compile(changed,str(path),'exec'),module.__dict__)
    result=module.run(parent,priced,finite,supplier)
    assert result['eta']==result['beta']==str(Q(1,10**30))
    p=result['assembly']['parameters'];e,c,r,beta=[Q(p[k])for k in ['epsilon','c','alpha_squared_power','beta']]
    assert e>0 and c>0 and r>0 and beta>0
    ka,km,kb,ks=[ceil(1/x)for x in [r,e*c,1-e,e*beta]]
    C0=2**210000;largest=max(priced['m'],supplier['m']);assert largest==73
    cuts=dict(guard=ceil(Q((2*C0).bit_length())/(1-e)),normalization=ceil(7/(1-e-r)),
        alpha=16*ka*ka+1,compact=64*km*km+1,geometry=ceil(3/(1-e*(1+c))),
        phase_cell=ceil(9/(e-(1-r)/2)),period=128*kb*kb+1,
        stopped_leaf=ks*(4*largest).bit_length(),log_p=25,reservoir=14)
    common=max(cuts.values());assert common==14*10**30
    assert common>=max(2*ka,2*km,2*kb,25)
    checkpoints=[]
    for j in range(6):
        z=common*2**j
        powers=dict(alpha=(z//ka,8*(z+ka)+64),compact=(z//km,32*(z+km)+192),
            period=(z//kb,16*(z+kb)+56),rows=(z//kb,4*10**6*(z+kb+8)),leaf=(z//ks,4*largest))
        assert all(lhs>=rhs.bit_length()for lhs,rhs in powers.values())
        checkpoints.append(dict(log2_input=z,powers={name:dict(exponent=lhs,rhs=rhs,rhs_bits=rhs.bit_length())for name,(lhs,rhs)in powers.items()}))
    result['slack_source']=dict(baseline_sha256=BASELINE_SHA,old_literal=OLD,new_literal=NEW,
        changed_source_sha256=hashlib.sha256(changed.encode()).hexdigest(),
        cutoff_reference='research/copied-fixed/balanced_assembly.py',cutoff_reference_sha256=CUTOFF_SOURCE_SHA)
    result['outer_cutoffs']=dict(cutoff_log2_input=cuts,common_cutoff=common,power_checkpoints=checkpoints,
        all_interval_argument='For [Z,Z+k), bound RHS at Z+k and LHS at floor(Z/k). Successive intervals double LHS; positive affine RHS grows at most linearly, so 2^j >= j+1 proves persistence.',
        additional_eventual_conditions=['BHP prime threshold and distinct-prime packing','Fixed rational basis, eligible common prime and native table setup','Catalogue and descriptor domination, logarithm absorption, exact recovery','A stage-specific C_full dominating counted primitive, wrapper, row and previous ordinary constants'],
        counted_cutoffs_are_not_universal_machine_cutoffs=True,practical_runtime_claim=False)
    assert path.read_bytes()==raw
    return result
