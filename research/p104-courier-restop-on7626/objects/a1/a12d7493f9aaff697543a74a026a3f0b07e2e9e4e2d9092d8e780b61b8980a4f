#!/usr/bin/env python3
"""Conjoin fresh complete applications under the explicitly bounded common U."""
import argparse,gzip,hashlib,json,sys
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent
SOURCE='c14f365d254598f6a2daa349b47f815d20c649f0439cc36897b531412e19a3de'
CANDIDATE=None
CALLER='255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc'
def need(x,s):
    if not x:raise ValueError(s)
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical_hash(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def gate(g,label):
    need(g['outer']['strict_count']==54 and g['outer']['functional_count']==4,label+' outer count')
    need(F(g['claim'])>0 and F(g['raw_bracket'][0])<F(g['raw_bracket'][1]),label+' bracket')
def signed_resources(checks,word,canonical,label):
    p=checks['ODD-PRECISION.json'];t=checks['ODD-FIXED-TAPE-COUNTS.json'];a=checks['ODD-ADMISSION-PARTIAL.json'];g=checks['ODD-CALLER-EXACT-GRID.json']
    need(p['native_sha256']==t['native_sha256']==a['native_sha256']==canonical,label+' native binding')
    need(p['caller_sha256']==t['caller_sha256']==a['caller_sha256']==g['caller_sha256']==CALLER,label+' caller binding')
    need(t['native_invocations']==17 and t['owned_banks_per_raw_occurrence']==1156,label+' invocation/stock')
    need(p['context_c']==t['context_c'] and 0<p['context_c']<=4096,label+' precision context')
    need(t['actual_ambient']<=t['compiler_ambient_cap']==153 and t['context_bound_bits']<t['H'] and t['Kstar_bits']<t['H'],label+' compiler/tape size')
    need(all(int(x['strict_power_of_two'])<t['H'] for x in p['rounded_caller']['bounds'].values()),label+' rounded caller bound')
    native_scalars=sum(e[0]!='MOVE' for e in word['program'])
    need(t['scalar_macro_inputs']['native']==17*native_scalars,label+' actual scalar occurrences')
    need(t['scalar_services_upper']==32*sum(t['scalar_macro_inputs'].values()),label+' charged scalar services')
    need(t['scalar_steps_coefficient']==t['scalar_services_upper']*2**20,label+' normalized scalar coefficient')
    need(t['elementary_records_per_map_upper']==4*(t['actual_ambient']+1)**2 and t['elementary_records_upper']==t['monomial_map_slots']*t['elementary_records_per_map_upper'],label+' finite map records')
    ordinary=a['ordinary'];need(ordinary['route_items']['owned_lifetime']==4*204 and ordinary['routing']==1000*sum(ordinary['route_items'].values()),label+' charged lifetime routing')
    need(ordinary['raw_upper']==17*(ordinary['scalar_upper']+ordinary['routing'])+ordinary['caller_total'],label+' 17-call ordinary multiplication')
    need(ordinary['conservative_total']==ordinary['raw_upper']+ordinary['per_input_conversion']+ordinary['lambda_second_charge']+ordinary['all_caller_scalar_surcharge']+ordinary['charged_caller_odd_conversions'],label+' complete ordinary charge')
    need(ordinary['conservative_total']<10**9 and a['crossing_probe_rejected'],label+' ordinary/probe')
    gate(a['compiler_outer'],label)
    need(F(t['tested_claim'])==F(a['compiler_outer']['claim']) and F(t['H'])==F(a['compiler_outer']['H']),label+' tape/gate claim and H')
    return {'ordinary':ordinary['conservative_total'],'ordinary_margin':10**9-ordinary['conservative_total'],'lifetime_routing_charge_per_native_call':ordinary['route_items']['owned_lifetime']*1000,'lifetime_routing_charge_in_ordinary':17*ordinary['route_items']['owned_lifetime']*1000,'native_lifetime_pairs_per_raw_occurrence':17*204,'INIT_CLEAR_scalar_services_charged':17*408*32,'precision_context':p['context_c'],'ambient':t['actual_ambient'],'scalar_services':t['scalar_services_upper'],'scalar_steps_coefficient':t['scalar_steps_coefficient'],'map_slots':t['monomial_map_slots'],'elementary_records':t['elementary_records_upper'],'context_bound_bits':t['context_bound_bits'],'H':t['H']}
def main():
    need(not sys.flags.optimize,'resource qualification requires assertions enabled')
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir();w=a.work;root=a.root
    global CANDIDATE
    first_gate=root/'compose7624_completion/run/case';fg=read(first_gate/'RESULT.json')
    need(fg['status']=='PASS_DIFFERENTIAL_ONLY_PROVISIONAL_UNDER_COMMON_U','first gate missing')
    required={'built/candidate-word.json.gz','built/edit-manifest.json','built/status.json','exact/status.json','price/PRICE.json','price/invoice-new.json'}
    need(required<=set(fg['receipt_hashes']),'missing first gate receipts')
    for rel,h in fg['receipt_hashes'].items():
        p=first_gate/rel;need(p.resolve().is_relative_to(first_gate.resolve()) and p.is_file() and not p.is_symlink() and sha(p)==h,'first gate hash '+rel)
    manifest=read(first_gate/'built/edit-manifest.json');CANDIDATE=manifest['candidate_canonical_sha256']
    need(manifest['source_canonical_sha256']==SOURCE and manifest['candidate_gzip_sha256']==sha(first_gate/'built/candidate-word.json.gz'),'manifest bindings')
    npath=w/'producer54/validation_native/NATIVE-RESULT.json';spath=w/'producer54/validation_signed/RESULT.json';n=read(npath);s=read(spath);identity=read(w/'QUALIFICATION-ID.json');ledger=read(w/'CONTACT7624-ADAPTERS.json');u=read(HERE/'COMMON-U.json')
    need(u['status']=='EXPLICIT_UNIMPLEMENTED_SUPPLIER_PREMISE','conditional model declaration')
    tariff=u['finite_same_tariff_assumptions']
    need(tariff['ordinary_source_units_per_lifetime_pair']==4000 and tariff['scalar_services_per_INIT_or_CLEAR']==32 and tariff['scalar_elementary_coefficient_per_service']==2**20 and tariff['precision_context_cap']==4096 and tariff['fixed_banks_signed']==1156,'stated finite tariff differs from checked model')
    need(ledger['common_U_sha256']==sha(HERE/'COMMON-U.json'),'prepared common U hash')
    need(identity['run_id'] and identity['candidate_canonical_sha256']==ledger['candidate_canonical_sha256']==CANDIDATE and identity['source_canonical_sha256']==ledger['source_canonical_sha256']==SOURCE,'identity word bindings')
    need(identity['first_gate_result_sha256']==ledger['first_gate_result_sha256']==sha(first_gate/'RESULT.json'),'fresh gate binding')
    need(ledger['launcher_sha256']==sha(HERE/'application.py')==sha(w/'CONTACT7624-LAUNCHER.py'),'launcher binding')
    need(read(w/'PREPARED.json')['ledger_sha256']==sha(w/'CONTACT7624-ADAPTERS.json'),'prepared ledger binding')
    for name,h in ledger['adapter_source_hashes'].items():need(sha(HERE/name)==h,'adapter source '+name)
    for name,h in ledger['frozen_hashes'].items():need(sha(w/'frozen-composition'/name)==h,'frozen input '+name)
    helper=w/'producer54/validation_signed/w2_adapt.py'
    need(sha(helper)==ledger['source_204_helper_sha256']==ledger['adapted_204_helper_sha256']==ledger['signed']['helper_sha256'],'source 204 helper binding')
    for kind,key in (('native','adapted_runner_sha256'),('signed','adapted_sha256')):
        need(sha(w/f'producer54/validation_{kind}/run.py')==ledger[kind][key],'adapted runner '+kind)
    need(n['status']=='PASS_CONTACT7624_COMPLETE_NATIVE' and s['status']=='PASS_CONTACT7624_COMPLETE_SIGNED_APPLICATION','complete application statuses')
    for name,path in (('native',npath),('signed',spath)):
        r=read(w/(name+'.receipt.json'));need(r['stage']==name and r['exit']==0 and r['run_id']==identity['run_id']==ledger['run_id'],'fresh attempt '+name)
        need(r['candidate_canonical_sha256']==CANDIDATE and r[name+'_result_sha256']==sha(path) and r['adapter_sha256']==sha(w/'CONTACT7624-ADAPTERS.json') and r['launcher_sha256']==sha(HERE/'application.py'),'fresh hash chain '+name)
        if name=='signed':need(r['stale_native_results_rejected']==3 and set(r['stale_native_receipt_bindings_rejected'])=={'run_id','native_result_sha256','adapter_sha256','launcher_sha256'},'freshness controls')
    candidate=json.loads(gzip.decompress((root/'compose7624_completion/run/case/built/candidate-word.json.gz').read_bytes()));source=json.loads(gzip.decompress((root/'inputs/pr7624/research/p104-w2-primal-dual-bypass/data/word.json.gz').read_bytes()))
    need(canonical_hash(candidate)==CANDIDATE and canonical_hash(source)==SOURCE,'actual resource word identities')
    need(n['word_canonical_sha256']==CANDIDATE and n['native']['lifetimes']==n['source_native']['lifetimes']==204 and n['native']['owned_peak']==n['source_native']['owned_peak']==50 and source['owned_fields']==candidate['owned_fields']==68 and not n['native']['bad_inputs'] and not n['source_native']['bad_inputs'],'native allocation')
    for word in (source,candidate):
        need(sum(e[0]=='INIT' for e in word['program'])==sum(e[0]=='CLEAR' for e in word['program'])==204,'actual lifetime count')
    ingredient=n['paired_ordinary'];need(ingredient['candidate']==n['ordinary'],'ingredient paired bill')
    for name,obj in (('source',ingredient['source_7624']),('candidate',ingredient['candidate'])):
        need(obj['conservative_total']<10**9 and obj['route_items']['owned_lifetime']==816,'ingredient lifetime tariff '+name)
        need(obj['routing']==1000*sum(obj['route_items'].values()) and obj['raw_upper']==18*(obj['scalar_upper']+obj['routing'])+obj['caller_total'],'18-call ingredient routing '+name)
        need(obj['conservative_total']==obj['raw_upper']+obj['per_input_conversion']+obj['lambda_second_charge']+obj['extra_B_scalar_surcharge'],'18-call complete ordinary '+name)
    need(n['paired_precision']['candidate']==n['precision'] and n['paired_precision']['source_7624'],'paired ingredient envelopes')
    gate(n['gate'],'candidate ingredient');gate(n['paired_precision']['source_gate'],'source ingredient')
    source_r=s['source_resource'];need(source_r['status']=='DERIVED_FRESH_SOURCE_RESOURCE_ONLY' and source_r['candidate_native_receipt_sha256']==sha(npath),'derived fresh source receipt')
    need(read(w/'producer54/validation_signed/SOURCE-RESOURCE.json')==source_r,'source resource file and signed embedding differ')
    derived=source_r['derived_result'];paired=n['paired_precision']
    need(derived['word_canonical_sha256']==SOURCE and derived['native']==n['source_native'] and derived['invoice']==n['source_invoice'],'fresh derived source inventory/invoice')
    need(derived['precision']==paired['source_7624'] and derived['gate']==paired['source_gate'] and derived['price']==paired['source_price'] and derived['ordinary']==ingredient['source_7624'],'fresh derived source precision/price/ordinary')
    need(source_r['source_18_gate']==paired['source_gate'] and source_r['source_17_gate']==source_r['checks']['ODD-ADMISSION-PARTIAL.json']['compiler_outer'],'source gate context separation')
    need(source_r['source_word_gzip_sha256']==sha(root/'inputs/pr7624/research/p104-w2-primal-dual-bypass/data/word.json.gz') and source_r['caller_sha256']==CALLER,'source resource inputs')
    source_check_names={'ODD-TYPE-B-REPLAY.json','ODD-TYPE-AB-REPLAY.json','ODD-CALLER-EXACT-GRID.json','ODD-PHYSICAL-BINDING.json','ODD-PRECISION.json','ODD-ADMISSION-PARTIAL.json','ODD-FIXED-TAPE-COUNTS.json'}
    need(set(source_r['checks'])==source_check_names and set(source_r['check_sha256'])==source_check_names and len(source_r['logs'])==len({x['check'] for x in source_r['logs']})==7,'seven distinct source checks')
    for row in source_r['logs']:need(sha(w/'producer54/validation_signed'/('SOURCE-'+row['check']+'.log'))==row['sha256'],'source check log')
    for label,checks,np in (('source',source_r['checks'],paired['source_7624']),('candidate',s['checks'],n['precision'])):
        precision=checks['ODD-PRECISION.json'];need(precision['native_grid']==np['word'] and precision['rounded_native']==np['rounded_native'],'paired native grid/envelope '+label)
    source_stats=signed_resources(source_r['checks'],source,SOURCE,'source signed');candidate_stats=signed_resources(s['checks'],candidate,CANDIDATE,'candidate signed')
    need(source_stats['precision_context']==candidate_stats['precision_context'],'same common signed precision context')
    for key in ('context_height','context_mass_bits','context_c'):
        need(source_r['checks']['ODD-PRECISION.json'][key]==s['checks']['ODD-PRECISION.json'][key],'common charged precision '+key)
    need(n['paired_precision']['source_7624']['context_c']==n['precision']['context_c']<=4096,'same common ingredient precision context')
    for label,word_obj,word_file in (('source',source,root/'inputs/pr7624/research/p104-w2-primal-dual-bypass/data/word.json.gz'),('candidate',candidate,first_gate/'built/candidate-word.json.gz')):
        cp=w.parent/'certificates'/('source-certificate.json' if label=='source' else 'certificate.json')
        cc=read(cp);need(cc['summary']['sha256']==sha(word_file) and cc['summary']['clears']==cc['summary']['certified']==len(cc['clears'])==204,'full certificate count/binding '+label)

    need(source_r['source_catalogue_rerun'] is False,'source scope changed')
    matched=s['matched_ordinary'];need(read(w/'producer54/validation_signed/MATCHED-ORDINARY.json')==matched and matched['source_total']==source_stats['ordinary'] and matched['candidate_total']==candidate_stats['ordinary'],'matched complete signed ordinary')
    need(candidate_stats['scalar_services']<=source_stats['scalar_services'],'unexpected new tape scalar demand')
    gate(s['price']['public_claim_gate'],'public candidate claim');gate(source_r['source_17_gate'],'fresh source signed')
    price=read(root/'compose7624_completion/run/case/price/PRICE.json');decl=read(root/'compose7624_completion/run/case/price/invoice-new.json');actual=s['price']['after']
    baseline=s['price']['baseline_7624']
    need({str(k):v for k,v in actual['P'].items()}==decl['paid'] and {str(k):v for k,v in actual['T'].items()}==decl['targets'],'actual complete signed invoice equals directed first gate')
    need({str(k):v for k,v in baseline['P'].items()}==price['source_signed_paid'] and {str(k):v for k,v in actual['P'].items()}==price['candidate_signed_paid'] and baseline['T']==actual['T'] and baseline['S']==actual['S']==1424,'paired complete invoice')
    need(sum(baseline['P'].values())==110060 and sum(actual['P'].values())==110043 and sum(actual['T'].values())==22461,'actual paid and target census')
    need(s['price']['baseline_7624_rejects_claim'] and s['price']['baseline_7624_rejects_raw_upper'],'current comparator directed rejection')
    need(price['status']=='PROVISIONAL_UNDER_COMMON_U' and F(s['price']['public_claim_gate']['claim'])==F(price['claim'])==F(s['price']['first_gate_claim']) and F(s['price']['first_gate_probe'])==F(price['tested']),'public claim mismatch')
    need(F(price['claim'])-F(price['old_published_raw_upper'])==F(price['gain_over_published_old_upper'])>0 and F(price['claim'])<F(price['candidate_fixed_invoice_ceiling']['raw_bracket'][0]),'directed price gain')
    gate(price['outer_gate'],'first gate candidate')
    catalogue=s['catalogue'];need(catalogue and catalogue[0]['catalogue_size']>0,'nonempty signed catalogue')
    cursor=0
    for row in catalogue:
        need(row['catalogue_size']==catalogue[0]['catalogue_size'] and row['slice_start']==cursor and row['slice_stop']>cursor and row['slice_stop']-cursor==row['checked_maps'] and row['word_sha256']==sha(first_gate/'built/candidate-word.json.gz') and row['phase_control_rejected'],'signed catalogue slice')
        cursor=row['slice_stop']
    need(cursor==catalogue[0]['catalogue_size'] and sum(x['main_boundary_pairs'] for x in catalogue)==104,'complete map and binding census')
    checks=s['checks']['ODD-8X9-APPLICATION-CHECKS.json'];need(checks['native_canonical_sha256']==CANDIDATE,'assembled application candidate')
    with localcontext() as ctx:
        ctx.prec=40;claim_decimal=str(Decimal(F(price['claim']).numerator)/Decimal(F(price['claim']).denominator))
    common_h=max(F(source_stats['H']),F(candidate_stats['H']),F(paired['source_gate']['H']),F(n['gate']['H']))
    report={'status':'PASS_CONDITIONAL_COMMON_U_APPLICATION','claim':price['claim'],'claim_decimal':claim_decimal,'gain_over_7624_raw_upper':price['gain_over_published_old_upper'],'source_published_raw_upper':price['old_published_raw_upper'],'ceiling':price['candidate_fixed_invoice_ceiling'],'common_h_lower_bound':str(common_h),'common_h_scope':'h >= max of fresh source and candidate 17-call and 18-call lower thresholds','source_signed':source_stats,'candidate_signed':candidate_stats,'ingredient_ordinary':{k:ingredient[k]['conservative_total'] for k in ('source_7624','candidate')},'same_tariff_common_U_sha256':sha(HERE/'COMMON-U.json'),'source_17_resource_scope':'Fresh seven source resource checks derived from paired fresh native calculations; source catalogue not rerun.','native_result_sha256':sha(npath),'signed_result_sha256':sha(spath),'source_resource_file_sha256':sha(w/'producer54/validation_signed/SOURCE-RESOURCE.json'),'run_id':identity['run_id'],'supplier_premise_discharged':False,'same_original_premise_dominance_established':False,'selected_frontier_changed':False,'limitations':u['limitations']}
    (a.out/'RESOURCE-COMPARISON.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print(json.dumps({'status':report['status'],'claim':report['claim']},sort_keys=True),flush=True)
if __name__=='__main__':main()
