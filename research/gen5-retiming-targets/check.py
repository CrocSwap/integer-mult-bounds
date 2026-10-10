#!/usr/bin/env python3
"""Independent gen5 composition, arbitrary-column and literal-cost checks."""
import sys
if not __debug__:raise SystemExit('Assertions must be enabled')
sys.dont_write_bytecode=True
import argparse,hashlib,json,struct
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
WORD='7afb22d4d11c0d558644ae18c9227180300fd242c819ae227e94e891decc5d60'
KAPPA=Q(744118535019311029483079,10**27)

def load(p):return json.loads(p.read_text())
def word(p):return list(struct.iter_unpack('<6i',p.read_bytes()))
def hist(es):return Counter(e[4]for e in es if e[0]==0 and e[4])+Counter(e[5]for e in es if e[0]==2)
def delta(a,b):
    h=hist(a);h.subtract(hist(b));return {r:c for r,c in h.items()if c}

def main(root):
    b=root/'base';r=root/'retimed';d=root/'candidate';st=load(b/'249-states.json');n,v=st['n'],st['v'];assert(n,v)==(19406,1760)
    old=word(b/'249-records.bin');mid=word(r/'COHORT249-RECORDS.bin');new=word(d/'COHORT249-RECORDS.bin')
    assert hashlib.sha256((d/'COHORT249-RECORDS.bin').read_bytes()).hexdigest()==WORD
    project=lambda es:[(e[0],e[1],e[2],e[3],e[5])for e in es if e[0]]
    assert project(old)==project(mid)
    assert delta(mid,old)=={1:-1760,2:880,20:-880,21:1760,22:-880}
    assert delta(new,mid)=={1:-221,17:-1,18:-7,2:-8,20:-212,21:220}
    rt=load(r/'RETIMING279.json');assert rt['selected_gates']==rt['undersized_frame_controls_rejected']==880
    assert rt['checked_source_indices']==1760 and not rt['rejected'] and rt['identical_scalar_and_copy_projection']
    groups=load(d/'TARGET268-GROUPS.json');assert len(groups)==220 and all(len(g['targets'])==4 and len(g['dependent'])==1 for g in groups)
    members={v+t for g in groups for t in g['targets']};assert len(members)==880
    assert load(d/'COHORT249-INITIAL.json')==st['initial']==load(r/'COHORT249-INITIAL.json')
    assert load(d/'COHORT249-SELECTION.json')==[]
    assert [e for e in mid if e[0]in(2,3)]==[e for e in new if e[0]in(2,3)]
    assert [e for e in mid if e[0]==1 and e[1]not in members and e[2]not in members]==[e for e in new if e[0]==1 and e[1]not in members and e[2]not in members]
    def replay(reverse=False,omit=None):
        cols=[1<<i for i in range(n)]+[0];norms=[1]*n+[0];center=None;largest=1
        for i in(range(len(new)-1,-1,-1)if reverse else range(len(new))):
            op,a,bb,c,f,z=new[i]
            if op==1:
                if i==omit:continue
                assert c%2 and a!=bb and(bb!=n or center is not None)
                cols[a]^=cols[bb];norms[a]+=abs(c)*norms[bb];largest=max(largest,norms[a])
            elif op==(3 if reverse else 2):
                assert center is None and bb==n;center=a;cols[bb]=cols[a];norms[bb]=norms[a]
            elif op==(2 if reverse else 3):
                assert center==a and bb==n and cols[a]==cols[bb];center=None;cols[bb]=0;norms[bb]=0
        assert center is None
        wrong=sum(cols[i]!=((1<<i)^((1<<(i-v))if v<=i<2*v else 0))for i in range(n))
        assert(wrong==0 if omit is None else wrong>0)
        return dict(reverse=reverse,omitted_record=omit,wrong_rows=wrong,row_l1_bound=largest)
    fw=replay();inv=replay(True);controls=[]
    for cat in(34,35):
        at=next(i for i in range(len(new)-1,-1,-1)if new[i][0]==1 and new[i][5]==cat)
        controls.append(replay(omit=at))
    h=hist(new);assert sum(r*c for r,c in h.items())==411356
    g=load(d/'GLOBAL.json');assert g['formal_columns_checked']==22926 and g['fresh_center_copies']==120
    assert len(g['negative_controls'])==6 and all(c['rejected']for c in g['negative_controls'])
    assert dict(g['local_raw_H'])==h
    assert[fw['row_l1_bound'],inv['row_l1_bound']]==[46393,2303032]==[int(x['cancellation_free_signed_row_l1_upper'])for x in g['signed_lift_prefix']]
    adds=sum(e[0]==1 for e in new);units=sum(abs(e[3])for e in new if e[0]==1)
    assert adds==574392==g['local_scalar_additions']==sum(e[0]==1 for e in old)-440
    bank=load(d/'BANK-REVIEW.json');fs=load(b/'frames.json')['frames'];ranks=Counter()
    initial_rank=0
    for s in range(2*v,n):
        f=st['initial'][str(s)];end=st['final'][str(s)];di=fs[str(f)]['dim'];df=fs[str(end)]['dim'];assert df==24
        ranks[df-di]+=1;initial_rank+=di
    assert ranks=={3:354,4:2182,6:16,7:2,24:13332} and initial_rank==51396
    slots=Counter();nb=0
    for p in bank['bank_patterns']:
        assert sum(p['widths'])==120 and p['count']>0
        for rank in p['widths']:slots[rank]+=p['count']
        nb+=p['count']
    assert slots=={r:120*c for r,c in ranks.items()} and nb==bank['banks_per_stage']==329868
    assert bank['actual_role_replica_stage_assignments']==5*sum(slots.values())==9531600
    assert bank['literal_stock']==844800+5*nb==2494140 and bank['normalized_stock']==498828
    assert bank['new_exact_charts']==411 and bank['max_new_chart_factors']==318 and bank['normalizer_factor_ceiling']==983
    assert bank['new_entrance_rank']==bank['endpoint_rank_deficit']==0
    price=load(d/'FIXED-PRICE.json');p=price['profile'];invoice=load(d/'FINITE.json')
    H=Counter({r:120*c for r,c in h.items()});H.update({r:48*v for r in(4,23,46,50)})
    assert {int(r):c for r,c in p['histogram'].items()}==dict(H)
    assert p['calls']==sum(H.values())==11305080 and p['rank_mass']==sum(r*c for r,c in H.items())
    assert p['stock']==498828 and p['deficit']==105600
    assert Q(price['kappa'])==KAPPA>Q(load(root/'pr285/verification.json')['kappa'])
    assert len(price['strict_constraints'])==47 and min(map(Q,price['strict_constraints'].values()))>0
    assert price['ordinary_levels']==8 and price['lucas_lehmer_iterations']==125 and price['lucas_lehmer_residue']=='0' and price['adjacent_rejected_at_finite_and_cap']
    assert int(invoice['full_counted_primitive_coefficient'])==int(price['finite_coefficient_recomputed'])==180164370784684201
    m=120;N=240;stock=bank['literal_stock'];E=5*sum(H.values());routes=120*(24*v+10*(n-2*v))
    selector=1200*((stock-1)+(n-2*v)*120*983)
    coefficient=120*(5*units+6*v)+routes*16*(m*m+1)**2+routes*(stock+24)+E*(8*m*m+8)+E*128*N**3+16*m**3+120*120+E+selector+1
    assert selector==bank['selector_charge']==2251688038800
    assert coefficient==int(invoice['full_counted_primitive_coefficient'])

    assert int(invoice['positive_rank_children'])==5*sum(H.values())
    assert int(invoice['global_weighted_additions'])==120*(5*adds+6*v)
    assert int(invoice['global_unit_expanded_additions'])==120*(5*units+6*v)
    payload=64*fw['row_l1_bound']**3*inv['row_l1_bound']**2
    assert payload==int(g['payload_prefix_upper'])==int(invoice['payload_signed_prefix_upper']) and payload<2**104
    result=dict(status='PASS_INDEPENDENT_GEN5_COMPOSITION_AND_LITERAL_INVOICE',word_sha256=WORD,kappa=str(KAPPA),kappa_decimal=price['kappa_decimal'],retimed_gates=880,target_groups=220,local_additions=adds,normalized_calls=sum(H.values()),forward=fw,inverse=inv,target_omission_controls=controls,bank_assignments=9531600,primitive_coefficient=invoice['full_counted_primitive_coefficient'],payload_bits=payload.bit_length(),scope='Conditional finite construction. All inherited all-size hypotheses remain assumptions.')
    (d/'INDEPENDENT.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS independent gen5 composition; kappa = '+price['kappa_decimal'])

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--replay',type=Path,required=True);a=ap.parse_args();main(a.replay)
