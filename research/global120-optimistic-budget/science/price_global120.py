#!/usr/bin/env python3
"""One-point global120 optimistic decoder allowance. Apache-2.0.

No primary construction, invoice verifier, native or author price engine import.
All new modes and old-main preservation are optimistic target grants only.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import resource
import signal
import time

ROOT=Path(__file__).resolve().parent
def need(test,message):
    if not test:raise ValueError(message)
def hist(x):return Counter({int(k):v for k,v in x.items()})
def clean(x):return {r:n for r,n in sorted(x.items()) if n}
def add(x,y):return x[0]+y[0],x[1]+y[1]
def neg(x):return -x[1],-x[0]
def sub(x,y):return add(x,neg(y))
def scale(x,k):return (x[0]*k,x[1]*k) if k>=0 else (x[1]*k,x[0]*k)
def overlap(x,y):return x[0]<=y[1] and y[0]<=x[1]
def ceil(x):return -((-x.numerator)//x.denominator)
def pack(x):
    q=10**24;l=x[0].numerator*q//x[0].denominator;h=ceil(x[1]*q)
    def show(n):
        s='-' if n<0 else '';n=abs(n);return s+str(n//q)+'.'+str(n%q).zfill(24)
    return dict(lower=str(x[0]),upper=str(x[1]),decimal_outer_lower=show(l),decimal_outer_upper=show(h))
def quota(x,cost):
    need(cost[0]>0,'positive tariff')
    if x[1]<=0:return dict(guaranteed_maximum=0,possible_maximum=0,exact_integer=True,positive_allowance=False)
    if x[0]<=0:return dict(guaranteed_maximum=0,possible_maximum=max(0,ceil(x[1]/cost[0])-1),exact_integer=False,positive_allowance=False)
    lo=max(0,ceil(x[0]/cost[1])-1);hi=max(0,ceil(x[1]/cost[0])-1)
    need(lo<=hi,'quota ordering')
    return dict(guaranteed_maximum=lo,possible_maximum=hi,exact_integer=(lo==hi),positive_allowance=True)
def load():
    manifest=json.loads((ROOT/'SOURCE-MANIFEST.json').read_text());data={};paths={}
    for row in manifest['entries']:
        p=ROOT/row['frozen'];raw=p.read_bytes()
        need(sha256(raw).hexdigest()==row['sha256'],'source hash drift '+row['source'])
        paths[row['key']]=p
        if p.suffix=='.json':data[row['key']]=json.loads(raw)
    def named(name):
        keys=[r['key'] for r in manifest['entries'] if Path(r['source']).name==name]
        need(len(keys)==1,'unambiguous source '+name)
        return data[keys[0]]
    assessment=json.loads((ROOT/'ASSESSMENT-BINDING.json').read_text())
    assessed=None
    for row in assessment['sources']:
        p=ROOT/row['frozen'];raw=p.read_bytes()
        need(sha256(raw).hexdigest()==row['sha256'],'assessment hash drift')
        if p.name=='assessor-result.json':assessed=json.loads(raw)
    need(assessed is not None and assessed['status']=='PASS_STATIC_GLOBAL120_BASELINE_DELTA_ROLE_AND_EVENT_INTAKE','independent source assessment')
    prop=data['proposal']
    need(assessed['source_ledger_sha256']=='d1b6cdb455a823d4d53b433bb90e54a0b5aa073e4e0041999261d8ec29ff1820','assessor exact ledger binding')
    need(assessed['resource_id']==prop['resource_id'] and assessed['source_bindings_matched']==10,'assessor resource scope')
    return manifest,data,paths,named,assessed
def derive(data,named,assessed):
    g=data['proposal'];root=data['independent_baseline_receipt'];old=named('NEUTRAL-CALLER-v16c.json');controller=named('CONTROLLER.json')
    closure=named('NEUTRAL-CLOSURE-v1.json');literal=named('INVOICE-NEUTRAL-LITERAL.json');whole=named('WHOLECALLER-RESULT-v1.json')
    bp=hist(root['paid']);bt=hist(root['targets'])
    need(root['status']=='PASS_LITERAL_BINDING_AND_TWO_POINT_NECESSARY_SCREEN','independent literal baseline receipt')
    need(bp==hist(old['paid_profile'])==hist(closure['paid'])==hist(literal['histograms']['paid'])==hist(whole['complete_paid_profile'])==hist(g['baseline']['paid']),'actual neutral baseline paid join')
    need(bt==hist(old['productive_profile'])==hist(closure['targets'])==hist(literal['histograms']['productive'])==hist(whole['productive_profile'])==hist(g['baseline']['targets']),'actual neutral baseline target join')
    need(sum(bp.values())==64260 and sum(bt.values())==10928,'reject older64404 baseline')
    need(sum(r*n for r,n in bp.items())==238990 and sum(r*n for r,n in bt.items())==239742,'baseline masses')
    need(controller==old['controller'],'actual controller/candidate binding')
    src=data['independent_baseline_source_manifest'];candidate_row=next(x for x in src['inputs'] if x['frozen']=='inputs/candidate.json')
    need(candidate_row['sha256']=='1f17fda221bc781ca0b2a120916ed500ba84c305a916a65436a5d6c72d116bcf','root baseline candidate pin')
    need(g['resource_id']=='global120-CI-oldH8promoters-direct-endpoint-padding-no-donations-v1','no-donation branch ID')
    roles=g['original_roles'];need(roles['pair2_local_v3_donation_enabled'] is False and roles['pair2_donation_H8_debit']==0 and roles['H9_promotion_enabled'] is False,'no donor/H9 branch mixing')
    need(g['added_mode_IDLES']['local_donated_pair2_H16_reduction_applied'] is False,'no local donor IDLE reduction')
    old_jobs={x['global_field']:x for x in old['canonical_helper_jobs']};promoted=set()
    need(len(roles['pairs'])==16,'sixteen original-role pairs')
    for i,row in enumerate(roles['pairs']):
        b=3584+408*(i+1)
        need(row['pair']==i and row['source_call_index']==i+1 and row['stage']==2*i+1 and row['helper_pool_start']==b,'original role occurrence')
        for kind,offsets in [('h',roles['h_offsets']),('k',roles['k_offsets'])]:
            ids=row[kind+'_original_global_fields'];need(ids==[b+j for j in offsets] and len(ids)==8,'mode ID formula')
            for field in ids:
                need(field in old_jobs and old_jobs[field]['rank']==8 and field not in promoted,'each debited mode was a distinct old H8 target')
                need(old_jobs[field]['call_index']==i+1,'source helper occurrence')
                promoted.add(field)
    need(len(promoted)==256,'256 distinct once-only H8 target debits')
    need(not(promoted&set(range(3584,3992))) and not(promoted&set(range(10520,10928))),'wrapped helper pools untouched')
    events=controller['physical_events'];idles=Counter();histories=[];queries=0;locals_=0
    for index,e in enumerate(events):
        if e[0]=='IDLE':
            rank=8*len(e[2]);idles[rank]+=16
            histories.append(dict(added_jobs=16,event_index=index,pair=e[1],rank=rank,stages=e[2]))
        elif e[0]=='QUERY_SHEAR':queries+=1
        elif e[0]=='LOCAL':locals_+=1
    need(len(histories)==15 and queries==15 and locals_==18 and len(events)==162,'actual event classes')
    need(histories==g['added_mode_IDLES']['history_rows'] and idles==hist(g['added_mode_IDLES']['histogram']),'all fifteen mode IDLE histories')
    need(idles==Counter({16:32,24:32,32:32,40:32,48:32,56:32,64:32,72:16}),'mode IDLE tariff census')
    modes=Counter();qsigns=[]
    for row in controller['diagonal']:
        need(row[0] in (-1,1) and all(x in (0,1) for x in row[1:]),'old full Gaussian row format')
        qsigns.append(row[0]);modes[1+8*sum(row[1:])]+=8
    need(len(qsigns)==32 and qsigns==g['optimistic_target_grant']['central_q_exponents'],'all32 odd-q mode slots')
    need(modes==hist(g['optimistic_target_grant']['mode_histogram']) and sum(modes.values())==256,'unearned mode-target grant')
    pads=g['explicit_mode_endpoint_padding']
    need(pads['endpoint_stages']==[0,32] and pads['after_old_port_wrapper_indices']==[4,107],'both endpoint pad locations')
    need(hist(pads['paid_each'])==Counter({1:8,8:16}) and hist(pads['paid_both'])==Counter({1:16,8:32}),'endpoint pads paid once')
    need(pads['terminal_Gamma_removed_by_padding'] is False,'padding does not solve terminal Gamma')
    proto=named('BALANCED-J-NATIVE-v1.json');need(proto['supplementary_H1_per_direction']==8,'old-h queries retained in declared global branch')
    local_query=16*8;thin_query=queries*8
    dp=Counter({1:local_query+thin_query+16,8:-16*8+32});dp.update(idles)
    dt=Counter(modes);dt[8]-=256
    need(clean(dp)=={r:n for r,n in sorted(hist(g['deltas']['paid']).items()) if n},'paid delta including pads')
    need(clean(dt)=={r:n for r,n in sorted(hist(g['deltas']['targets']).items()) if n},'target delta once-only promotion debit')
    p=Counter(bp);p.update(dp);t=Counter(bt);t.update(dt)
    need(all(n>=0 for n in p.values()) and all(n>=0 for n in t.values()),'nonnegative resulting profiles')
    need(p==hist(g['fixed_optimistic_price_input']['paid']) and t==hist(g['fixed_optimistic_price_input']['targets']),'complete new ledger profiles')
    expected_p=Counter({1:41418,2:7416,3:9180,4:2286,5:720,8:48,16:480,24:480,32:480,40:480,48:480,56:480,64:480,72:240})
    expected_t=Counter({4:504,7:126,8:734,9:5724,17:480,25:480,33:480,41:480,49:480,57:480,65:480,73:240,145:240})
    need(p==expected_p and t==expected_t,'author/root declared fixed input')
    need(sum(p.values())==64668 and sum(t.values())==10928,'new exact counts')
    pm=sum(r*n for r,n in p.items());tm=sum(r*n for r,n in t.items())
    need(pm==248598 and tm==250366 and tm-pm==1768,'padded mass1768, not unpadded2040')
    need(g['all256targets_admitted'] is False and g['optimistic_target_grant']['new_mode_targets_earned']==0 and g['optimistic_target_grant']['old_main_targets_preserved_in_price_relaxation_only'] is True,'unearned target scope')
    need(g['fixed_optimistic_price_input']['further_paid_Gamma_decoder_or_supplier'] is None and g['fixed_optimistic_price_input']['further_lost_productive_targets'] is None,'source future costs remain unknown')
    need(g['chronology']['contact_kind'].startswith('whole120 C_I'),'old C_P operator is not the declared contact')
    return p,t,bp,bt,dict(delta_paid=clean(dp),delta_targets=clean(dt),mode_IDLES=clean(idles),unearned_mode_targets=clean(modes),
        promoted_original_count=256,wrapped_helper_originals_untouched=816,remaining_nonmode_helpers=7088,old_baseline_paid_count=64260,
        endpoint_paid_once={1:16,8:32},no_donation=True,no_C_P_transfer=True,paid_count=64668,target_count=10928,paid_mass=pm,target_mass=tm,surplus=1768,
        assessor_status=assessed['status'],assessor_check_count=assessed['check_count'])
def run():
    start=time.monotonic();manifest,data,paths,named,assessed=load();g=data['proposal'];p,t,bp,bt,binding=derive(data,named,assessed)
    relax=json.loads((ROOT/'RELAXATION.json').read_text());C=F(relax['C']);rho=F(relax['rho'])
    need(C==F('0.00330007') and rho==F(1,10**9),'one authorized fixed point/reserve')
    need(relax['pricing_only_future_paid']=={} and relax['pricing_only_future_lost_targets']=={} and relax['physical_future_paid_unknown'] is True and relax['physical_future_target_losses_unknown'] is True,'optimistic zero-future-cost calculation is not physical zero cost')
    spec=importlib.util.spec_from_file_location('global120_independent_powers',paths['powers']);a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
    engine=a.Powers(C)
    def f(r):
        x=engine(r);return F(x[0],a.Q),F(x[1],a.Q)
    def moment(profile):
        total=(F(0),F(0))
        for r,n in sorted(profile.items()):total=add(total,scale(f(r),n))
        return total
    pm=moment(p);tm=moment(t);raw=sub(tm,pm);budget=sub(scale(tm,1-rho),pm)
    coefficient_budget=(F(0),F(0))
    for r in sorted(p.keys()|t.keys()):coefficient_budget=add(coefficient_budget,scale(f(r),(1-rho)*t[r]-p[r]))
    need(overlap(budget,coefficient_budget),'direct/signed-coefficient interval agreement')
    alpha=(pm[0]/tm[1],pm[1]/tm[0]);rhomax=(1-alpha[1],1-alpha[0])
    decision='POSITIVE_OPTIMISTIC_DECODER_ALLOWANCE' if budget[0]>0 else ('REJECT_OPTIMISTIC_FIXED_INPUT' if budget[1]<=0 else 'UNRESOLVED_INTERVAL')
    quotas=[]
    for r in (1,8,16,24,25,145):
        cost=f(r);loss=scale(cost,1-rho);pq=quota(budget,cost);lq=quota(budget,loss)
        capped=dict(guaranteed_maximum=min(lq['guaranteed_maximum'],t[r]),possible_maximum=min(lq['possible_maximum'],t[r]))
        quotas.append(dict(rank=r,additional_paid_tariff=pack(cost),additional_paid_alone=pq,lost_target_tariff=pack(loss),lost_targets_alone=lq,
            target_count_in_optimistic_input=t[r],inventory_capped_lost_targets_alone=capped,quotas_not_additive=True,physical_cost_or_target_availability_proved=False))
    baseline_p=moment(bp);baseline_t=moment(bt)
    return dict(status='COMPLETE_SINGLE_POINT_OPTIMISTIC_GLOBAL120_SCREEN',decision=decision,resource_id=g['resource_id'],C=str(C),rho=str(rho),
        binding=binding,fixed_paid=clean(p),optimistic_targets=clean(t),paid_moment=pack(pm),optimistic_target_moment=pack(tm),
        raw_rho0_margin_T_minus_P=pack(raw),optimistic_decoder_allowance_B_rho=pack(budget),signed_coefficient_crosscheck=pack(coefficient_budget),
        optimistic_alpha=pack(alpha),optimistic_rho_max=pack(rhomax),quotas=quotas,
        neutral_baseline_same_cached_C=dict(paid_moment=pack(baseline_p),target_moment=pack(baseline_t),raw_margin=pack(sub(baseline_t,baseline_p)),B_rho=pack(sub(scale(baseline_t,1-rho),baseline_p)),
            scope='Actualneutral64260/10928 comparison only. No compiler/geometry transfer or old three-call42.525 allowance.'),
        mixed_constraint='future_paid(C)+(1-rho)*future_lost_targets(C) < B_rho; every quota alone, never additive',
        source_future_paid_and_losses_unknown=True,pricing_zero_future_repair_is_relaxation_only=True,all256_new_modes_unearned=True,old_main_preservation_optimistic=True,
        new_target_credit_admitted=0,complete_physical_caller=False,funded_kappa=None,
        compiler_geometry_or_old43_envelope_transferred=False,higher_moments_not_evaluated=True,
        remaining_gates=g['unknown_ordinary_and_stock'],environment=dict(elapsed_seconds=time.monotonic()-start,maximum_resident_set_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
        scope='A positive optimistic point justifies the next physical decoder-cost step only; no earned targets or kappa claim.')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024));signal.alarm(30)
    try:r=run()
    except Exception as exc:
        with args.receipt.open('x') as out:json.dump(dict(status='FAIL',exception=type(exc).__name__,message=str(exc)),out,indent=2);out.write('\n')
        raise
    with args.receipt.open('x') as out:json.dump(r,out,indent=2);out.write('\n')
    print(json.dumps({k:r[k] for k in ('status','decision','resource_id','C','rho','raw_rho0_margin_T_minus_P','optimistic_decoder_allowance_B_rho','quotas','environment')},indent=2))
if __name__=='__main__':main()
