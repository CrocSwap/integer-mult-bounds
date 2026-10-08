#!/usr/bin/env python3
"""Assemble already verified balanced/split axes and exact conditional arithmetic.

No network search occurs here. This uses the pinned inherited rational enclosure
and balanced-assembly checker. Its transfer assumptions remain explicit.
"""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
from fractions import Fraction as Q
from copy import deepcopy
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
from verify_balanced_split import assemble,PIN

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--upstream',type=Path,required=True);p.add_argument('--verification',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--frontier',type=Path)
    a=p.parse_args();root=a.upstream.resolve()
    assert subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()==PIN
    sys.path.insert(0,str(root/'scripts/experiments'))
    from split_pair_compose import check_sources
    from split_pair_arithmetic import refine,audit
    import binary_frame_math as arithmetic
    check_sources();axes=[];inputs={}
    for h in (23,25):
        path=a.verification/f'comparison-{h}.json';d=json.loads(path.read_text())
        profile=a.verification/f'balanced-split-{h}.bin.profiles.json'
        assert d['source_pin']==PIN and digest(profile)==d['profile_sha256']
        assert digest(a.verification/f'balanced-split-{h}.bin')==d['binary_sha256']
        assert json.loads(profile.read_text())==d['profile']
        assert d['replay']['roles']==d['profile']['R'] and d['replay']['rank_mass']==d['profile']['rank_sum']
        axes.append(d['profile']);inputs[str(h)]=dict(comparison_sha256=digest(path),profile_sha256=digest(profile),word_sha256=d['word_sha256'])
    assert sorted(f['h'] for f in axes)==[23,25], 'Need exactly one profile per axis'
    profile=assemble(axes);rows=profile['child_multiplicities'];m=profile['m'];W=profile['W']
    public_path=root/'research/round6-pr71/parameter-certificate.json';public=json.loads(public_path.read_text())
    old_a=Q(public['bit_saving']);at_old=refine.exact_moment(m,W,rows,old_a)
    denominator=10**18;low=1;high=10**14
    assert refine.exact_moment(m,W,rows,Q(low,denominator))['upper']<1
    assert refine.exact_moment(m,W,rows,Q(high,denominator))['lower']>1
    steps=0
    while low+1<high:
        middle=(low+high)//2;x=refine.exact_moment(m,W,rows,Q(middle,denominator));steps+=1
        if x['upper']<1:low=middle
        elif x['lower']>1:high=middle
        else:raise ArithmeticError('Need sharper directed enclosure')
    saving=Q(low,denominator);accepted=refine.exact_moment(m,W,rows,saving);rejected=refine.exact_moment(m,W,rows,Q(high,denominator))
    independent=audit.independent_moment(arithmetic.js(profile),saving,arithmetic.js(accepted['terms']))
    independent_rejected=audit.independent_moment(arithmetic.js(profile),Q(high,denominator),arithmetic.js(rejected['terms']))
    assert accepted['upper']<1<rejected['lower'] and independent[1]<1<independent_rejected[0]
    bridge=deepcopy(public['finite_bridge']);bridge['bit']['W']=W;bridge['bit']['wire_bits']=W.bit_length()
    coefficient=sum(bridge[axis]['halving_degree']*bridge[axis]['wire_bits'] for axis in ('bit','complex'))
    bridge['rows']['coefficient']=coefficient
    bridge['rows']['degree_gap']=Q(bridge['rows']['degree'])-Q(51,25)*coefficient
    assert bridge['rows']['degree_gap']>0
    preferred=refine.assemble(bridge,saving,Q(1,10**18),denominator)
    frontier=None
    if a.frontier:
        f=json.loads(a.frontier.read_text());target=Q(f['bit_saving']);fm=refine.exact_moment(m,W,rows,target)
        frontier=dict(source_sha256=digest(a.frontier),reported_kappa=Q(f['kappa']),reported_bit_saving=target,
            candidate_moment_at_frontier=fm,kappa_difference=preferred['kappa']-Q(f['kappa']),
            candidate_exceeds_frontier_kappa=preferred['kappa']>Q(f['kappa']))
    result=dict(status='PASS combined finite profile, exact moment and conditional balanced assembly',scope='This combines already verified finite words and inherited fixed data/exterior/copy facts. Physical all-size compiler and transfer contracts remain hypotheses; no new full-machine Lean theorem.',source_pin=PIN,inputs=inputs,checker_sha256=digest(Path(__file__)),
        prior_public_sha256=digest(public_path),profile=profile,bit_saving=saving,excluded_next_bit_saving=Q(high,denominator),denominator=denominator,binary_search_steps=steps,
        accepted_moment=accepted,rejected_moment=rejected,independent_enclosures=dict(accepted=independent,rejected=independent_rejected),moment_at_pr73=at_old,
        finite_bridge=bridge,backoff=Q(1,10**18),preferred=preferred,kappa=preferred['kappa'],prior_kappa=Q(public['kappa']),kappa_gain=preferred['kappa']-Q(public['kappa']),frontier_comparison=frontier)
    a.output.write_text(json.dumps(arithmetic.js(result),indent=2)+'\n')
    print(json.dumps(dict(status='PASS',W=W,roles=[x['R'] for x in axes],bit_saving=str(saving),kappa=str(preferred['kappa']),kappa_gain_vs73=str(result['kappa_gain']),exceeds76=None if frontier is None else frontier['candidate_exceeds_frontier_kappa'])),flush=True)
if __name__=='__main__':main()
