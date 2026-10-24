#!/usr/bin/env python3
"""Root-run independent literal invoice and necessary alpha funding screen.

Apache-2.0. Substantial OpenAI Codex assistance; predecessor credit in HANDOFF.md.
No author price/provider checker is imported or executed.
"""
import argparse
from collections import Counter,defaultdict
from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import resource
import signal
import sys
import time

ROOT=Path(__file__).resolve().parent

def need(test,message):
    if not test:raise ValueError(message)

def hist(d):return Counter({int(k):v for k,v in d.items()})
def cleaned(c):return {r:v for r,v in sorted(c.items()) if v}
def signed(p,t):
    c=Counter(p);c.subtract(t);return cleaned(c)
def difference(a,b):
    c=Counter(a);c.subtract(b);return cleaned(c)

def load_inputs():
    manifest=json.loads((ROOT/'SOURCE-MANIFEST.json').read_text())
    loaded={}
    for row in manifest['inputs']:
        p=ROOT/row['frozen'];data=p.read_bytes()
        need(sha256(data).hexdigest()==row['sha256'],'frozen source hash changed: '+row['frozen'])
        if p.suffix=='.json':loaded[p.name]=json.loads(data)
    return manifest,loaded

def arithmetic():
    path=ROOT/'inputs/independent_powers_frozen.py'
    spec=importlib.util.spec_from_file_location('neutral_independent_powers',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def derive(c,b,source,old,manifest):
    rows={Path(r['frozen']).name:r for r in manifest['inputs']}
    need(c['source_controller_sha256']==rows['old5398-controller.json']['sha256'],'candidate source controller pin')
    need(c['local_backward_sha256']==rows['local-backward.json']['sha256'],'candidate local B pin')
    need(c['controller']==source,'embedded controller differs from source bytes')
    need(c['source_main']==manifest['canonical_base'],'canonical baseline mismatch')
    need(c['runtime_local_directions']=={'backward':18,'forward_macro_calls':0},'all-backward scope')
    need(source['pairs']==16 and source['prefix_pairs']==7 and source['ambient_rank']==145,'fixed source geometry')
    base_p=hist(old['backward_native']['paid']);base_h=hist(old['backward_native']['helpers'])
    need(base_p==Counter({1:2193,2:412,3:510,4:127,5:40}),'source local paid premise changed')
    need(base_h==Counter({4:28,7:7,8:47,9:318}),'source local helper premise changed')
    need(hist(b['native_paid'])==base_p,'neutral local native profile binding')
    need(b['persistent_original_count']==632 and b['owned_entry_count']==17 and b['owned_exit_zero_count']==17,'632/17 ABI')
    need(b['helper_count']==408 and b['total_productive_helper_fields']==408,'408 helper scope')
    native_calls=[e for e in b['operations'] if e['op']=='PROVIDER_5402']
    gaussian=[e for e in b['operations'] if e['op']=='GAUSSIAN']
    need(len(native_calls)==1 and len(gaussian)==8,'local provider/eight Gaussian inventory')
    extra=Counter()
    for e in gaussian:
        need(e.get('paid') is True and e['rank']==8 and e['actual_axes']==list(range(8)),'extra paid canonical H8')
        extra[e['rank']]+=1
    local_paid=base_p+extra
    need(hist(b['complete_paid_local_profile'])==local_paid,'literal extra Gaussians disagree with local summary')
    need(extra==Counter({8:8}) and hist(b['supplementary_paid'])==extra,'local neutral paid delta')
    local_helpers=base_h+Counter({8:8})
    need(hist(b['helper_jobs'])==local_helpers and hist(b['productive_helpers'])==local_helpers,'local helper neutral delta premise')
    local_aliases=b['physical_field_bindings']
    need(len(local_aliases)==649 and set(local_aliases.values())==set(range(649)),'local alias bijection')

    events=c['typed_emission'];source_events=source['physical_events']
    need(len(events)==len(source_events),'one typed emission per source event')
    need([e['source_event_index'] for e in events]==list(range(len(source_events))),'typed order/source indices')
    jobs=c['canonical_helper_jobs'];by_call=defaultdict(list)
    for job in jobs:by_call[job['call_index']].append(job)
    need(len(jobs)==18*408 and set(by_call)==set(range(18)),'helper job census')
    paid=Counter();targets=Counter();old_paid=Counter();old_targets=Counter()
    kinds=Counter();all_helpers=set();all_owned=set();all_queries=[];call_ids=[];components=[]
    for e,src in zip(events,source_events):
        op=e['op'];kinds[op]+=1;kind=src[0]
        if op=='CALL_NEUTRAL_BACKWARD':
            need(kind=='LOCAL' and src[3] is True and [e['stage'],e['pair']]==src[1:3],'LOCAL source event binding')
            need(e['macro_sha256']==c['local_backward_sha256'] and e['macro_file']=='NEUTRAL-BACKWARD-v16c.json','LOCAL macro binding')
            i=e['local_call_index'];call_ids.append(i)
            hs=e['original_independent_helper_fields'];owned=e['owned_fields']
            need(hs==list(range(3584+408*i,3584+408*(i+1))),'helper block allocation')
            need(owned==list(range(10928+17*i,10928+17*(i+1))),'owned block allocation')
            need(e['owned_entry']=='arbitrary' and e['owned_exit']=='all17zero','owned boundary labels')
            need(not(set(hs)&all_helpers) and not(set(owned)&all_owned),'helper/owned blocks reused')
            all_helpers.update(hs);all_owned.update(owned)
            mapping={}
            for name,role in local_aliases.items():
                mapping[name]=(224*e['pair']+role if role<224 else
                               3584+408*i+role-224 if role<632 else 10928+17*i+role-632)
            need(e['physical_field_bindings']==mapping,'LOCAL literal global field map')
            js=by_call[i]
            need(len(js)==408 and {j['global_field'] for j in js}==set(hs),'helper jobs match independent input fields')
            need({j['source_role'] for j in js}==set(range(224,632)),'helper source-role coverage')
            observed=Counter()
            for j in js:
                need(j['independent_productive_input'] is True and j['positive_layout']=='canonicalC_rankbits0..rank-1','canonical productive helper premise')
                need(j['global_field']==3584+408*i+j['source_role']-224,'helper role-to-owner binding')
                observed[j['rank']]+=1
            need(observed==local_helpers,'per-call helper rank inventory')
            paid.update(local_paid);targets.update(observed)
            old_paid.update(base_p);old_targets.update(base_h)
            components.append(dict(source_event_index=e['source_event_index'],kind='LOCAL',call_index=i,paid=cleaned(local_paid),targets=cleaned(observed)))
        elif op=='RETAINED_QUERY_SHEAR112':
            need(kind=='QUERY_SHEAR' and [e['stage'],e['pair'],e['backward']]==src[1:],'QUERY source binding')
            need(e['paid_rank1_calls']==112,'QUERY rank-one charge')
            need(e['source_main_bank']==2*e['pair'] and e['target_main_bank']==2*e['pair']+1,'QUERY bank binding')
            need(e['source_fields']==list(range(112*e['source_main_bank'],112*(e['source_main_bank']+1))),'QUERY source owners')
            need(e['target_fields']==list(range(112*e['target_main_bank'],112*(e['target_main_bank']+1))),'QUERY target owners')
            need(e['owned_snapshot_bank']==list(range(11234,11346)),'QUERY separate snapshot allocation')
            all_queries.append(e['owned_snapshot_bank']);paid[1]+=112;old_paid[1]+=112
            components.append(dict(source_event_index=e['source_event_index'],kind='QUERY',paid={1:112}))
        elif op=='RETAINED_WHOLE_IDLE':
            need(kind=='IDLE' and e['pair']==src[1] and e['stages']==src[2],'IDLE source binding')
            need(e['rank']==8*len(src[2]) and e['paid_calls']==224,'IDLE rank/count binding')
            need(e['fields']==list(range(224*e['pair'],224*(e['pair']+1))),'IDLE main field binding')
            paid[e['rank']]+=224;old_paid[e['rank']]+=224
            components.append(dict(source_event_index=e['source_event_index'],kind='IDLE',paid={e['rank']:224}))
        else:
            need(op=='RETAINED_MAIN_EVENT' and e['event']==src and e['ports']==112,'retained main event changed')
            need(kind not in ('LOCAL','QUERY_SHEAR','IDLE'),'typed recursive charge hidden as main event')
    need(call_ids==list(range(18)),'ordered unique local call indices')
    need(kinds==Counter({'CALL_NEUTRAL_BACKWARD':18,'RETAINED_QUERY_SHEAR112':15,'RETAINED_WHOLE_IDLE':15,'RETAINED_MAIN_EVENT':114}),'complete typed census')
    need(all_helpers==set(range(3584,10928)) and all_owned==set(range(10928,11234)),'global helper and owned disjoint allocation')
    need(not(all_helpers&all_owned) and not(all_helpers&set(range(3584))) and not(all_owned&set(range(11234,11346))),'main/helper/owned/query separation')
    final=Counter()
    for row in source['diagonal']:
        need(len(row)==34 and row[0] in (-1,1) and all(bit in (0,1) for bit in row[1:]),'source final Gaussian term format')
        final[1+8*sum(row[1:])]+=112
    need(sum(final.values())==3584,'all source main final terms charged')
    targets.update(final);old_targets.update(final)
    components.append(dict(kind='SOURCE_GAUSSIAN_FINAL_TERMS',targets=cleaned(final)))
    need(hist(c['paid_profile'])==paid and hist(c['productive_profile'])==targets,'candidate declared histogram differs from literal invoice')
    need(hist(old['arithmetic']['paid'])==old_paid and hist(old['arithmetic']['targets'])==old_targets,'old source result differs from independently derived source invoice')
    need(difference(paid,old_paid)=={8:144} and difference(targets,old_targets)=={8:144},'neutral profile deltas')
    need(signed(paid,targets)==signed(old_paid,old_targets),'all-real-exponent signed histogram neutrality')
    need(sum(paid.values())==64260 and sum(targets.values())==10928,'global paid/productive job census')
    need(sum(r*n for r,n in paid.items())==238990 and sum(r*n for r,n in targets.items())==239742,'global rank masses')
    for key,expected in [('paid_calls',64260),('productive_fields',10928),('paid_rank_mass',238990),('productive_rank_mass',239742),('rank_mass_surplus',752),('main_input_fields',3584),('independent_helper_input_fields',7344),('total_independent_persistent_fields',10928),('local_owned_fields',306),('query_owned_snapshot_fields',112),('macro_level_field_slots_before_recursive_child_scratch',11346)]:
        need(c[key]==expected,'candidate summary field mismatch: '+key)
    controls=[]
    for name,dp,dt in [('double_extra_H8_target_credit',0,144),('omit_additional_paid_H8',-144,0),('omit_additional_H8_target',0,-144)]:
        mp=Counter(paid);mt=Counter(targets);mp[8]+=dp;mt[8]+=dt
        need(signed(mp,mt)!=signed(old_paid,old_targets),'neutrality mutant survived: '+name)
        controls.append(dict(name=name,expected='reject all-exponent neutrality',observed='rejected',extra_signed_paid_minus_target_H8=dp-dt))
    return paid,targets,old_paid,old_targets,dict(typed_counts=dict(kinds),components=components,main_final_terms=cleaned(final),helper_jobs=7344,helper_owners_disjoint=True,neutral_delta={8:144},signed_histogram= signed(paid,targets),negative_controls=controls)

def fraction_interval(lo,hi):
    return dict(lower=str(lo),upper=str(hi))

def ratio_screen(paid,target,a,rho):
    need(target[0]>0,'positive target moment')
    alo=Fraction(paid[0],target[1]);ahi=Fraction(paid[1],target[0])
    rlo=1-ahi;rhi=1-alo
    answer='PASS_NECESSARY_ALPHA' if rlo>rho else ('REJECT_NECESSARY_ALPHA' if rhi<=rho else 'UNRESOLVED_INTERVAL')
    return dict(alpha=fraction_interval(alo,ahi),rho_max=fraction_interval(rlo,rhi),requested_rho=str(rho),decision=answer)

def run():
    started=time.monotonic();manifest,inputs=load_inputs()
    c=inputs['candidate.json'];b=inputs['local-backward.json'];source=inputs['old5398-controller.json'];old=inputs['old5398-result.json']
    p,t,op,ot,binding=derive(c,b,source,old,manifest);a=arithmetic()
    old_arithmetic=old['arithmetic']
    need(Fraction(old_arithmetic['strictification']['reserve'])==Fraction(1,10**12),'source strictification reserve changed')
    need(Fraction(old_arithmetic['outer']['parameters']['r0'])==Fraction(1,7000000000000),'source outer r0 changed')
    need(Fraction(old_arithmetic['kappa'])==Fraction('.00302728823'),'source comparison kappa changed')
    need(Fraction('.00302728823')<Fraction('.003027288235')<Fraction('.003027288245'),'provisional/tested comparison ordering')
    points=[]
    for text,wanted in [('.003027288245','FAVORABLE_RAW_MOMENT'),('.00302728825','REJECT_RAW_MOMENT')]:
        f=a.Powers(Fraction(text));pm=a.moment(p,f);tm=a.moment(t,f);net=a.minus(pm,tm)
        classification='FAVORABLE_RAW_MOMENT' if net[1]<0 else ('REJECT_RAW_MOMENT' if net[0]>0 else 'UNRESOLVED_INTERVAL')
        need(classification==wanted,'requested fixed-point sign does not match expected decision at '+text)
        source_net=a.minus(a.moment(op,f),a.moment(ot,f));need(a.overlap(net,source_net),'source signed moment enclosure consistency')
        strict=ratio_screen(pm,tm,a,Fraction(1,10**12));outer=ratio_screen(pm,tm,a,Fraction(1,7000000000000))
        old_ratio=ratio_screen(a.moment(op,f),a.moment(ot,f),a,Fraction(0))
        points.append(dict(kappa=text,raw_decision=classification,paid_moment=a.packed(pm),target_moment=a.packed(tm),paid_minus_target=a.packed(net),
                           source_paid_minus_target=a.packed(source_net),necessary_source_strictification_alpha=strict,
                           necessary_outer_r0_alpha_screen=outer,old5398_ratio_comparison=old_ratio,
                           compiler_admitted=False,precision_admitted=False,outer_admitted=False))
    return dict(status='PASS_LITERAL_BINDING_AND_TWO_POINT_NECESSARY_SCREEN',binding=binding,paid=cleaned(p),targets=cleaned(t),
                neutrality='Exact symbolic equality at every real exponent; raw-root source certificate may transfer only subject to this literal binding and original proof premises. No new raw-root extraction.',
                reserve_distinction='Neutral equal additions preserve T-P but change P/T. Fresh neutral target denominator used. Outer r0 is not compiler reserve.',
                points=points,source_checkout_HEAD=manifest['old5398_checkout_HEAD'],source_canonical_base=manifest['canonical_base'],
                inherited_raw_root_metadata_only=old_arithmetic['raw_root_interval'],provisional_kappa='.003027288235',comparison_source_kappa='.00302728823',
                remaining_gates=['all649 native/local columns and owned-zero proof','global source/operator composition','all ordinary and precision/movement charges','compiler and outer closure'],
                environment=dict(python=sys.version,elapsed_seconds=time.monotonic()-started,maximum_resident_set_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024));signal.alarm(30)
    try:result=run()
    except Exception as exc:
        result=dict(status='FAIL',exception=type(exc).__name__,message=str(exc))
        with args.receipt.open('x') as out:json.dump(result,out,indent=2);out.write('\n')
        raise
    with args.receipt.open('x') as out:json.dump(result,out,indent=2);out.write('\n')
    print(json.dumps(dict(status=result['status'],points=result['points'],environment=result['environment']),indent=2))

if __name__=='__main__':main()
