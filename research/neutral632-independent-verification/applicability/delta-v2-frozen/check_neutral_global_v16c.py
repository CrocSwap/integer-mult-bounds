#!/usr/bin/env python3
"""Root-run global composition after independent all649-column B/F acceptance.
Fresh32bankLaurentreplay; actual10928originaldirection allocation and helper census.
Native source and local phase/circuit proofs are reused only at their exact pins.
"""
import argparse,hashlib,json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent;BASE=HERE.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(x,s):
    if not x:raise ValueError(s)
def main(output):
    gp=HERE/'NEUTRAL-CALLER-v16c.json';g=json.loads(gp.read_text())
    bp=HERE/'NEUTRAL-BACKWARD-v16c.json';fp=HERE/'NEUTRAL-FORWARD-v16c.json';b=json.loads(bp.read_text())
    receipt=json.loads((HERE.parent/'challenge/NEUTRAL-LOCAL-RESULT-v16c.json').read_text())
    need(receipt['status']=='PASS_COMPLETE_LOCAL_STANDARD_B_AND_F_WITH408POSITIVE_HELPERS','independent local B/F gate')
    need(receipt['packet_sha256']=={'backward':sha(bp),'forward':sha(fp)},'exact accepted local packet bytes')
    need(all(receipt['results'][k]['independent_original_columns']==632 and receipt['results'][k]['arbitrary_owned_columns']==17 and receipt['results'][k]['owned_zero_outputs']==17 and receipt['results'][k]['positive_helpers']==408 for k in('B','F')),'all649 local contract before global reuse')
    need(all(c['rejected']for c in receipt['controls'])and len(receipt['controls'])>=11,'all actual local controls')
    source=BASE/g['source_controller_path'];s=json.loads(source.read_text())
    need(sha(source)=='60cc512b39cdb9ea2c2ac6c6634c8d3f9627d96ace08ffa659a9d9472444122b','retained exact all18B5398 controller')
    need(g['controller']==s and g['source_controller_sha256']==sha(source),'unchanged complete source events/boundaries')
    need(g['local_backward_sha256']==sha(bp)and g['runtime_local_directions']=={'backward':18,'forward_macro_calls':0},'no F doublecount')
    zero=(0,)*34
    def plus(a,b,c=F(1)):
        out=dict(a)
        for key,value in b.items():
            z=out.get(key,F(0))+c*value
            if z:out[key]=z
            elif key in out:del out[key]
        return out
    def shift(row,term,sign=1):return [{tuple(x+y for x,y in zip(key,term)):sign*c for key,c in cell.items()}for cell in row]
    rows=[[{zero:F(x)}if F(x)else{}for x in row]for row in s['boundaries']['right']]
    for e in s['physical_events']:
        op=e[0]
        if op in('LOCAL','QUERY_SHEAR'):
            _,stage,pair,back=e;x,y=2*pair,2*pair+1
            if back:x,y=y,x
            term=(1 if back else-1,)+(0,)*33
            rows[y]=[plus(dst,src,F(-1 if back else 1))for dst,src in zip(rows[y],shift(rows[x],term))]
            if op=='LOCAL':
                need(back is True,'every full runtime supplier is B')
                term=(0,)+tuple(int(k==stage)for k in range(33));rows[x]=shift(rows[x],term);rows[y]=shift(rows[y],term)
        elif op=='IDLE':
            term=(0,)+tuple(int(k in e[2])for k in range(33));rows[2*e[1]]=shift(rows[2*e[1]],term);rows[2*e[1]+1]=shift(rows[2*e[1]+1],term)
        elif op=='Q_POWER':
            need(e[2]in(-2,2),'only inherited even powers');rows[e[1]]=shift(rows[e[1]],(e[2],)+(0,)*33)
        elif op=='ADD':rows[e[1]]=[plus(x,y,F(e[3]))for x,y in zip(rows[e[1]],rows[e[2]])]
        elif op in('SIGNED_SWAP','SWAP'):
            x,y=e[1:];rows[x],rows[y]=rows[y],shift(rows[x],zero,-1 if op=='SIGNED_SWAP'else 1)
        else:raise ValueError(e)
    result=[[{}for _ in range(32)]for _ in range(32)]
    for i,weights in enumerate(s['boundaries']['left']):
        for k,c in enumerate(weights):
            if F(c):
                for j in range(32):result[i][j]=plus(result[i][j],rows[k][j],F(c))
    expected=[[{tuple(s['diagonal'][i]):F(1)}if i==j else{}for j in range(32)]for i in range(32)]
    need(result==expected,'all1024 complete global main coefficients')
    local_calls=[t for t in g['typed_emission']if t['op']=='CALL_NEUTRAL_BACKWARD']
    need(len(local_calls)==18,'eighteen runtime B invocations')
    fresh_helpers=set();fresh_owned=set()
    for call in local_calls:
        q=call['local_call_index'];pair=call['pair'];mapping=call['physical_field_bindings'];start=3584+q*408
        wanted={}
        for name,role in b['physical_field_bindings'].items():
            wanted[name]=2*pair*112+role if role<112 else(2*pair+1)*112+role-112 if role<224 else start+role-224 if role<632 else 10928+17*q+role-632
        need(mapping==wanted and len(set(mapping.values()))==649,'all649 exact role bindings per call')
        need(call['macro_sha256']==sha(bp),'no replaced local macro')
        helpers=set(call['original_independent_helper_fields']);owned=set(call['owned_fields'])
        need(helpers==set(range(start,start+408))and not helpers&fresh_helpers,'fresh independent408 percall')
        need(owned==set(range(10928+17*q,10928+17*(q+1)))and not owned&fresh_owned,'separate17owned percall')
        fresh_helpers|=helpers;fresh_owned|=owned
    need(fresh_helpers==set(range(3584,10928))and fresh_owned==set(range(10928,11234)),'complete persistent/helper/private allocation')
    jobs=g['canonical_helper_jobs'];need(len(jobs)==7344 and len({j['global_field']for j in jobs})==7344,'no duplicated helper credit')
    helpers=Counter(j['rank']for j in jobs)
    need(helpers==Counter({4:504,7:126,8:990,9:5724}),'all408positive helpers percall including144 newH8')
    query=[t for t in g['typed_emission']if t['op']=='RETAINED_QUERY_SHEAR112']
    need(len(query)==15 and all(t['owned_snapshot_bank']==list(range(11234,11346))for t in query),'112 privatequeryfields sequential reuse')
    need(not(fresh_helpers|fresh_owned|set(range(3584)))&set(range(11234,11346)),'query snapshots cannot borrow original/private-full fields')
    P=Counter();T=Counter(helpers)
    for _call in local_calls:P.update({int(k):v for k,v in b['complete_paid_local_profile'].items()})
    for e in s['physical_events']:
        if e[0]=='QUERY_SHEAR':P[1]+=112
        elif e[0]=='IDLE':P[8*len(e[2])]+=224
    for t in s['diagonal']:T[1+8*sum(t[1:])]+=112
    need(P==Counter({int(k):v for k,v in g['paid_profile'].items()})and T==Counter({int(k):v for k,v in g['productive_profile'].items()}),'full literal invoice matches global typed binder')
    need((sum(P.values()),sum(T.values()),sum(r*n for r,n in P.items()),sum(r*n for r,n in T.items()))==(64260,10928,238990,239742),'exact counts/rank masses')
    out={'status':'PASS_NEUTRAL_COMPLETE_GLOBAL_COMPOSITION_AND_ALLOCATION','caller_sha256':sha(gp),'local_packet_sha256':receipt['packet_sha256'],
      'scalar_boundary_execution':'RIGHT_program thenphysical_events thenLEFT_program','main_bank_coefficients_checked':1024,'main_independent_fields':3584,
      'fresh_independent_positive_helper_fields':7344,'total_independent_original_fields':10928,'full_local_owned_fields_zero':306,
      'shared_query_owned_fields':112,'macro_private_total':418,'macro_total_fields':11346,
      'paid_calls':64260,'productive_fields':10928,'paid_rank_mass':238990,'productive_rank_mass':239742,'surplus':752,
      'neutral_delta':{'paid_H8':144,'productive_H8':144},
      'positive_Gaussian_main_normalizer_gate':'RawdiagonalQexponents areNOTscalar signs. Actual145axisinput/outputpermutation and nativecentralX-normalizer packet is a separatelybound physical/layout gate; do notturnthisLaurentPASSintofinalcanonicalGaussiancreditwithoutit.',
      'proof_reuse':'Globalmainblocklaw inherited from old5398 only AFTER exactunrestrictedall649 local standard224B wasindependentlyaccepted. Actual400helperaliases/rootphasecomponent bound separately.',
      'complete_scientific_admission':False,'gain_admitted':False,'checker_sha256':sha(Path(__file__))}
    output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,sort_keys=True))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=HERE/'NEUTRAL-GLOBAL-COMPOSITION-v16c.json');main(p.parse_args().output)
