#!/usr/bin/env python3
"""Independent endpoint census, word magnitudes and literal invoice binding."""
import sys
if not __debug__:raise SystemExit('Assertions must be enabled')
sys.dont_write_bytecode=True
import argparse,hashlib,json,struct
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
WORD='8cfe069d7714b332d44f9ede431f4a902834963dac974436590cbec33ccb27f6'
KAPPA=Q(745272866677869825771952,10**27)
def load(p):return json.loads(p.read_text())
def word(p):return list(struct.iter_unpack('<6i',p.read_bytes()))
def hist(es):return Counter(e[4]for e in es if e[0]==0 and e[4])+Counter(e[5]for e in es if e[0]==2)
def main(root):
    b=root/'base';d=root/'candidate';coords=root/'coordinates';st=load(coords/'249-states.json');n,v=st['n'],st['v'];assert(n,v)==(19406,1760)
    old=word(b/'COHORT249-RECORDS.bin');new=word(d/'COHORT249-RECORDS.bin')
    assert hashlib.sha256((d/'COHORT249-RECORDS.bin').read_bytes()).hexdigest()==WORD
    h=hist(new);change=h.copy();change.subtract(hist(old));assert {r:c for r,c in change.items()if c}=={1:1320,2:-880}
    assert sum(r*c for r,c in h.items())==409894==sum(r*c for r,c in hist(old).items())-440
    audit=load(d/'INDEPENDENT.json');assert audit['word_sha256']==WORD and audit['exact_signed_commutation']['moved_gates']==440
    assert [(x['reverse'],x['omit_restoration'],x['wrong_rows'])for x in audit['checks']]==[(False,False,0),(False,True,440),(True,False,0),(True,True,440)]
    cleanup=load(d/'CLEANUP.json');assert cleanup['helpers_retired']==440 and not cleanup['rejected'] and cleanup['new_records']==len(new)==661380
    assert load(d/'COHORT249-INITIAL.json')==load(b/'COHORT249-INITIAL.json')
    assert [e for e in old if e[0]in(2,3)]==[e for e in new if e[0]in(2,3)]
    adds=sum(e[0]==1 for e in new);units=sum(abs(e[3])for e in new if e[0]==1)
    assert adds==565050==sum(e[0]==1 for e in old)
    g=load(d/'GLOBAL.json');assert g['formal_columns_checked']==22926 and g['fresh_center_copies']==120
    assert len(g['negative_controls'])==6 and all(c['rejected']for c in g['negative_controls'])
    assert dict(g['local_raw_H'])==h
    l1=[]
    for reverse in (False,True):
        norms=[1]*n+[0];largest=1;center=None
        for op,a,bb,c,f,z in (reversed(new)if reverse else new):
            if op==1:
                assert 0<=a<n and 0<=bb<=n and (bb!=n or center is not None)
                norms[a]+=abs(c)*norms[bb];largest=max(largest,norms[a])
            elif op==(3 if reverse else 2):
                assert center is None and bb==n;center=a;norms[bb]=norms[a]
            elif op==(2 if reverse else 3):
                assert center==a and bb==n;center=None;norms[bb]=0
        assert center is None;l1.append(largest)
    assert l1==[67127,2360408]==[int(x['cancellation_free_signed_row_l1_upper'])for x in g['signed_lift_prefix']]
    bank=load(d/'BANK-REVIEW.json');fs=load(coords/'frames.json')['frames'];fs.update(load(d/'COHORT249-FRAMES.json'))
    initial=load(d/'COHORT249-INITIAL.json');final=load(d/'COHORT249-FINAL.json');ranks=Counter();base_ranks=Counter();entrance=endpoint=changed=0
    assert final==load(d/'249-states.json')['final']
    destinations={str(e['helper'])for e in cleanup['edits']}
    for s in range(n):
        key=str(s)
        if key not in destinations:assert final[key]==st['final'][key]
        else:assert fs[str(final[key])]['dim']==23
        if s<2*v:continue
        di=fs[str(initial[key])]['dim'];df=fs[str(final[key])]['dim'];original=fs[str(st['initial'][key])]['dim']
        assert di>=original;ranks[df-di]+=1;base_ranks[df-original]+=1
        entrance+=di-original;endpoint+=24-df;changed+=di!=original
    assert base_ranks=={3:794,4:1742,6:16,7:2,24:13332}
    assert (entrance,endpoint,changed)==(1022,440,450)==(bank['new_entrance_rank'],bank['endpoint_rank_deficit'],bank['new_gauged_roles'])
    assert {int(r):c for r,c in bank['residual_families'].items()}==dict(ranks)
    slots=Counter();nb=0
    for p in bank['bank_patterns']:
        assert sum(p['widths'])==120 and p['count']>0
        for rank in p['widths']:slots[rank]+=p['count']
        nb+=p['count']
    assert slots=={r:120*c for r,c in ranks.items()} and nb==bank['banks_per_stage']==328406
    assert bank['actual_role_replica_stage_assignments']==5*sum(slots.values())==9531600
    assert bank['literal_stock']==844800+5*nb==2486830 and bank['normalized_stock']==497366
    assert bank['new_exact_charts']==985 and bank['max_new_chart_factors']==318 and bank['normalizer_factor_ceiling']==983
    price=load(d/'FIXED-PRICE.json');p=price['profile'];invoice=load(d/'FINITE.json')
    H=Counter({r:120*c for r,c in h.items()});H.update({r:48*v for r in(4,23,46,50)})
    assert {int(r):c for r,c in p['histogram'].items()}==dict(H)
    assert p['calls']==sum(H.values())==11449320 and p['rank_mass']==sum(r*c for r,c in H.items())==59578320
    assert p['stock']==497366 and p['deficit']==105600
    assert Q(price['kappa'])==KAPPA>Q(load(root/'pr290/verification.json')['kappa'])
    assert len(price['strict_constraints'])==47 and min(map(Q,price['strict_constraints'].values()))>0
    assert price['ordinary_levels']==8 and price['lucas_lehmer_iterations']==125 and price['lucas_lehmer_residue']=='0'
    assert price['adjacent_rejected_at_finite_and_cap']==[['margin2'],['margin2']]
    m=120;N=240;stock=bank['literal_stock'];E=5*sum(H.values());routes=120*(24*v+10*(n-2*v))
    selector=1200*((stock-1)+(n-2*v)*120*983)
    coefficient=120*(5*units+6*v)+routes*16*(m*m+1)**2+routes*(stock+24)+E*(8*m*m+8)+E*128*N**3+16*m**3+120*120+E+selector+1
    assert selector==bank['selector_charge']==2251679266800
    assert coefficient==int(invoice['full_counted_primitive_coefficient'])==int(price['finite_coefficient_recomputed'])==181440420660517801
    assert int(invoice['positive_rank_children'])==E
    assert int(invoice['global_weighted_additions'])==120*(5*adds+6*v)==340297200
    assert int(invoice['global_unit_expanded_additions'])==120*(5*units+6*v)==342409200
    assert {int(r):int(c)for r,c in invoice['literal_histogram'].items()}=={r:5*c for r,c in H.items()}
    payload=64*l1[0]**3*l1[1]**2
    assert payload==int(g['payload_prefix_upper'])==int(invoice['payload_signed_prefix_upper']) and payload.bit_length()==97 and payload<2**104
    result=dict(status='PASS_INDEPENDENT_ENDPOINTS_AND_LITERAL_INVOICE',word_sha256=WORD,kappa=str(KAPPA),kappa_decimal=price['kappa_decimal'],early_restorations=440,local_additions=adds,normalized_calls=sum(H.values()),signed_row_l1=l1,bank_assignments=9531600,primitive_coefficient=str(coefficient),payload_bits=97,scope='Conditional finite construction. All inherited all-size hypotheses remain assumptions.')
    (d/'INVOICE-AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS independent endpoints and literal invoice; kappa = '+price['kappa_decimal'])
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--replay',type=Path,required=True);main(ap.parse_args().replay)
