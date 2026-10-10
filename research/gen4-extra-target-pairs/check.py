#!/usr/bin/env python3
"""Independent columns, new-pair controls and literal invoice bindings."""
import sys
if not __debug__:raise SystemExit('Assertions must be enabled')
sys.dont_write_bytecode=True
import argparse,hashlib,json,struct
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

WORD='c58643033f70544ab1af58fb31da5fa1f4869753895aab6bec9d1bcbb8507dc3'
KAPPA=Q(726214631355537156447271,10**27)
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def word(p):return list(struct.iter_unpack('<6i',p.read_bytes()))
def hist(es):return Counter(e[4]for e in es if e[0]==0 and e[4])+Counter(e[5]for e in es if e[0]==2)

def check(base,out):
    before=base/'final';state=load(base/'restored/249-states.json');n,v=state['n'],state['v']
    assert (n,v)==(19914,1760)
    assert sha(out/'COHORT249-RECORDS.bin')==WORD
    old=word(before/'COHORT249-RECORDS.bin');new=word(out/'COHORT249-RECORDS.bin')
    groups=load(out/'TARGET268-GROUPS.json');previous=load(before/'TARGET268-GROUPS.json')
    assert len(groups)==240 and groups[:220]==previous and len(previous)==220
    extra=groups[220:];members={v+t for g in extra for t in g['targets']};assert len(members)==40
    assert all(len(g['targets'])==2 and len(g['dependent'])==1 and g['close_rank']==21 for g in extra)
    assert load(out/'COHORT249-INITIAL.json')==load(before/'COHORT249-INITIAL.json')
    assert [e for e in old if e[0]in(2,3)]==[e for e in new if e[0]in(2,3)]
    assert [e for e in old if e[0]==1 and e[1]not in members and e[2]not in members]==[e for e in new if e[0]==1 and e[1]not in members and e[2]not in members]
    local=hist(new);delta=local.copy();delta.subtract(hist(old));delta={r:c for r,c in delta.items()if c}
    assert delta=={3:-20,18:-20,21:20}
    assert sum(r*c for r,c in local.items())==422844
    def replay(reverse=False,omit=None):
        cols=[1<<i for i in range(n)]+[0];norms=[1]*n+[0];center=None;largest=1
        indices=range(len(new)-1,-1,-1)if reverse else range(len(new))
        for i in indices:
            op,a,b,c,f,z=new[i]
            if op==1:
                if i==omit:continue
                assert c%2 and a!=b and (b!=n or center is not None)
                cols[a]^=cols[b];norms[a]+=abs(c)*norms[b];largest=max(largest,norms[a])
            elif op==(3 if reverse else 2):
                assert center is None and b==n;center=a;cols[b]=cols[a];norms[b]=norms[a]
            elif op==(2 if reverse else 3):
                assert center==a and b==n and cols[a]==cols[b];center=None;cols[b]=0;norms[b]=0
        assert center is None
        wrong=sum(cols[i]!=((1<<i)^((1<<(i-v))if v<=i<2*v else 0))for i in range(n))
        if omit is None:assert wrong==0
        else:assert wrong>0
        return dict(reverse=reverse,omitted_record=omit,wrong_rows=wrong,row_l1_bound=largest)
    forward=replay();inverse=replay(True)
    controls=[]
    for cat in(34,35):
        at=next(i for i,e in enumerate(new)if e[0]==1 and e[5]==cat and e[1]in members and e[2]in members)
        controls.append(replay(omit=at))
    native=load(out/'GLOBAL.json');assert native['formal_columns_checked']==23434
    assert native['fresh_center_copies']==120 and len(native['negative_controls'])==6
    assert all(c['rejected']for c in native['negative_controls'])
    assert dict(native['local_raw_H'])==local
    assert [forward['row_l1_bound'],inverse['row_l1_bound']]==[int(r['cancellation_free_signed_row_l1_upper'])for r in native['signed_lift_prefix']]
    adds=sum(e[0]==1 for e in new);units=sum(abs(e[3])for e in new if e[0]==1)
    assert adds==native['local_scalar_additions']==sum(e[0]==1 for e in old)+20
    H=Counter({r:120*c for r,c in local.items()});H.update({r:48*v for r in(4,23,46,50)})
    bank=load(out/'BANK-REVIEW.json');oldbank=load(before/'BANK-REVIEW.json')
    assert {k:v for k,v in bank.items()if k!='label'}=={k:v for k,v in oldbank.items()if k!='label'}
    assert bank['normalized_stock']==510316 and bank['literal_stock']==2551580
    assert bank['actual_role_replica_stage_assignments']==9836400
    price=load(out/'FIXED-PRICE.json');profile=price['profile'];invoice=load(out/'FINITE.json')
    assert {int(r):c for r,c in profile['histogram'].items()}==dict(H)
    assert profile['calls']==sum(H.values()) and profile['rank_mass']==sum(r*c for r,c in H.items())
    assert profile['stock']==bank['normalized_stock'] and profile['deficit']==105600
    assert Q(price['kappa'])==KAPPA>Q(load(before/'FIXED-PRICE.json')['kappa'])
    assert len(price['strict_constraints'])==47 and min(map(Q,price['strict_constraints'].values()))>0
    assert price['ordinary_levels']==8 and price['lucas_lehmer_iterations']==125 and price['lucas_lehmer_residue']=='0'
    assert price['adjacent_rejected_at_finite_and_cap']
    assert int(price['finite_coefficient_recomputed'])==int(invoice['full_counted_primitive_coefficient'])
    assert int(invoice['positive_rank_children'])==5*sum(H.values())
    assert int(invoice['global_weighted_additions'])==120*(5*adds+6*v)
    assert int(invoice['global_unit_expanded_additions'])==120*(5*units+6*v)
    assert int(invoice['full_counted_primitive_coefficient'])==185427454637140801
    payload=64*forward['row_l1_bound']**3*inverse['row_l1_bound']**2
    assert payload==int(native['payload_prefix_upper'])==int(invoice['payload_signed_prefix_upper']) and payload<2**104
    result=dict(status='PASS_INDEPENDENT_EXTRA_TARGET_PAIRS_AND_LITERAL_INVOICE',word_sha256=WORD,kappa=str(KAPPA),
        kappa_decimal=price['kappa_decimal'],extra_pairs=20,targets=sorted(t-v for t in members),local_histogram_delta=delta,
        local_additions=adds,local_unit_additions=units,normalized_calls=sum(H.values()),normalized_stock=profile['stock'],
        unchanged_banks=True,forward=forward,inverse=inverse,new_pair_omission_controls=controls,
        primitive_coefficient=invoice['full_counted_primitive_coefficient'],payload_bits=payload.bit_length(),
        scope='Conditional finite construction. All inherited all-size hypotheses remain assumptions.')
    (out/'INDEPENDENT.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS independent 20-pair composition; kappa = '+price['kappa_decimal'],flush=True)
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--base-replay',type=Path,required=True);ap.add_argument('--candidate',type=Path,required=True);a=ap.parse_args()
    check(a.base_replay,a.candidate)
