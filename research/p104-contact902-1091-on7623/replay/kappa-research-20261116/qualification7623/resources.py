#!/usr/bin/env python3
"""Conjoin fresh complete applications under the explicitly bounded common U."""
import argparse,gzip,hashlib,json
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent
SOURCE='48e1845e6b24832731705a3ff096b22d2b807428f7d625d06b45adfe3b5a738c'
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
    ordinary=a['ordinary'];need(ordinary['route_items']['owned_lifetime']==4*180 and ordinary['routing']==1000*sum(ordinary['route_items'].values()),label+' charged lifetime routing')
    need(ordinary['conservative_total']<10**9 and a['crossing_probe_rejected'],label+' ordinary/probe')
    gate(a['compiler_outer'],label)
    need(F(t['tested_claim'])==F(a['compiler_outer']['claim']) and F(t['H'])==F(a['compiler_outer']['H']),label+' tape/gate claim and H')
    return {'ordinary':ordinary['conservative_total'],'ordinary_margin':10**9-ordinary['conservative_total'],'lifetime_routing_charge':17*180*4000,'INIT_CLEAR_scalar_services_charged':17*360*32,'precision_context':p['context_c'],'ambient':t['actual_ambient'],'scalar_services':t['scalar_services_upper'],'scalar_steps_coefficient':t['scalar_steps_coefficient'],'map_slots':t['monomial_map_slots'],'elementary_records':t['elementary_records_upper'],'context_bound_bits':t['context_bound_bits'],'H':t['H']}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir();w=a.work;root=a.root
    global CANDIDATE
    first_gate=root/'compose7623/run/case';fg=read(first_gate/'RESULT.json')
    need(fg['status']=='PASS_DIFFERENTIAL_ONLY_PROVISIONAL_UNDER_COMMON_U','first gate missing')
    for rel,h in fg['receipt_hashes'].items():need(sha(first_gate/rel)==h,'first gate hash '+rel)
    CANDIDATE=read(first_gate/'built/edit-manifest.json')['candidate_canonical_sha256']
    npath=w/'producer54/validation_native/NATIVE-RESULT.json';spath=w/'producer54/validation_signed/RESULT.json';n=read(npath);s=read(spath);identity=read(w/'QUALIFICATION-ID.json');ledger=read(w/'CONTACT7623-ADAPTERS.json');u=read(HERE/'COMMON-U.json')
    need(u['status']=='EXPLICIT_UNIMPLEMENTED_SUPPLIER_PREMISE','conditional model declaration')
    tariff=u['finite_same_tariff_assumptions']
    need(tariff['ordinary_source_units_per_lifetime_pair']==4000 and tariff['scalar_services_per_INIT_or_CLEAR']==32 and tariff['scalar_elementary_coefficient_per_service']==2**20 and tariff['precision_context_cap']==4096 and tariff['fixed_banks_signed']==1156,'stated finite tariff differs from checked model')
    need(ledger['common_U_sha256']==sha(HERE/'COMMON-U.json'),'prepared common U hash')
    need(n['status']=='PASS_CONTACT7623_COMPLETE_NATIVE' and s['status']=='PASS_CONTACT7623_COMPLETE_SIGNED_APPLICATION','complete application statuses')
    for name,path in (('native',npath),('signed',spath)):
        r=read(w/(name+'.receipt.json'));need(r['stage']==name and r['exit']==0 and r['run_id']==identity['run_id']==ledger['run_id'],'fresh attempt '+name)
        need(r['candidate_canonical_sha256']==CANDIDATE and r[name+'_result_sha256']==sha(path) and r['adapter_sha256']==sha(w/'CONTACT7623-ADAPTERS.json') and r['launcher_sha256']==sha(HERE/'application.py'),'fresh hash chain '+name)
    candidate=json.loads(gzip.decompress((root/'compose7623/run/case/built/candidate-word.json.gz').read_bytes()));source=json.loads(gzip.decompress((root/'inputs/pr7623/research/p104-loan-snapshot-engine-on7621/data/word.json.gz').read_bytes()))
    need(canonical_hash(candidate)==CANDIDATE and canonical_hash(source)==SOURCE,'actual resource word identities')
    need(n['native']['lifetimes']==n['source_native']['lifetimes']==180 and n['native']['owned_peak']==n['source_native']['owned_peak']==50 and source['owned_fields']==candidate['owned_fields']==68,'native allocation')
    for word in (source,candidate):
        need(sum(e[0]=='INIT' for e in word['program'])==sum(e[0]=='CLEAR' for e in word['program'])==180,'actual lifetime count')
    ingredient=n['paired_ordinary'];need(ingredient['candidate']==n['ordinary'],'ingredient paired bill')
    for name,obj in (('source',ingredient['source_7623']),('candidate',ingredient['candidate'])):
        need(obj['conservative_total']<10**9 and obj['route_items']['owned_lifetime']==720,'ingredient lifetime tariff '+name)
    need(n['paired_precision']['candidate']==n['precision'] and n['paired_precision']['source_7623'],'paired ingredient envelopes')
    gate(n['gate'],'candidate ingredient');gate(n['paired_precision']['source_gate'],'source ingredient')
    source_r=s['source_resource'];need(source_r['status']=='DERIVED_FRESH_SOURCE_RESOURCE_ONLY' and source_r['candidate_native_receipt_sha256']==sha(npath),'derived fresh source receipt')
    need(read(w/'producer54/validation_signed/SOURCE-RESOURCE.json')==source_r,'source resource file and signed embedding differ')
    derived=source_r['derived_result'];paired=n['paired_precision']
    need(derived['word_canonical_sha256']==SOURCE and derived['native']==n['source_native'] and derived['invoice']==n['source_invoice'],'fresh derived source inventory/invoice')
    need(derived['precision']==paired['source_7623'] and derived['gate']==paired['source_gate'] and derived['price']==paired['source_price'] and derived['ordinary']==ingredient['source_7623'],'fresh derived source precision/price/ordinary')
    need(source_r['source_18_gate']==paired['source_gate'] and source_r['source_17_gate']==source_r['checks']['ODD-ADMISSION-PARTIAL.json']['compiler_outer'],'source gate context separation')
    for label,checks,np in (('source',source_r['checks'],paired['source_7623']),('candidate',s['checks'],n['precision'])):
        precision=checks['ODD-PRECISION.json'];need(precision['native_grid']==np['word'] and precision['rounded_native']==np['rounded_native'],'paired native grid/envelope '+label)
    source_stats=signed_resources(source_r['checks'],source,SOURCE,'source signed');candidate_stats=signed_resources(s['checks'],candidate,CANDIDATE,'candidate signed')
    need(source_stats['precision_context']==candidate_stats['precision_context'],'same common signed precision context')
    need(n['paired_precision']['source_7623']['context_c']==n['precision']['context_c']<=4096,'same common ingredient precision context')
    for label,word_obj,word_file in (('source',source,root/'inputs/pr7623/research/p104-loan-snapshot-engine-on7621/data/word.json.gz'),('candidate',candidate,first_gate/'built/candidate-word.json.gz')):
        cp=w.parent/'certificates'/('source-certificate.json' if label=='source' else 'certificate.json')
        cc=read(cp);need(cc['summary']['sha256']==sha(word_file) and cc['summary']['clears']==cc['summary']['certified']==len(cc['clears'])==180,'full certificate count/binding '+label)

    need(source_r['source_catalogue_rerun'] is False,'source scope changed')
    matched=s['matched_ordinary'];need(matched['source_total']==source_stats['ordinary'] and matched['candidate_total']==candidate_stats['ordinary'],'matched complete signed ordinary')
    need(candidate_stats['scalar_services']<=source_stats['scalar_services'],'unexpected new tape scalar demand')
    gate(s['price']['public_claim_gate'],'public candidate claim');gate(source_r['source_17_gate'],'fresh source signed')
    price=read(root/'compose7623/run/case/price/PRICE.json');decl=read(root/'compose7623/run/case/price/invoice-new.json');actual=s['price']['after']
    need({str(k):v for k,v in actual['P'].items()}==decl['paid'] and {str(k):v for k,v in actual['T'].items()}==decl['targets'],'actual complete signed invoice equals directed first gate')
    need(s['price']['baseline_7623_rejects_claim'] and s['price']['baseline_7623_rejects_raw_upper'],'current comparator directed rejection')
    need(F(s['price']['public_claim_gate']['claim'])==F(price['claim']),'public claim mismatch')
    checks=s['checks']['ODD-8X9-APPLICATION-CHECKS.json'];need(checks['native_canonical_sha256']==CANDIDATE,'assembled application candidate')
    report={'status':'PASS_CONDITIONAL_COMMON_U_APPLICATION','claim':price['claim'],'claim_decimal':str(__import__('decimal').Decimal(F(price['claim']).numerator)/__import__('decimal').Decimal(F(price['claim']).denominator)),'gain_over_7623_raw_upper':price['gain_over_published_old_upper'],'ceiling':price['candidate_fixed_invoice_ceiling'],'source_signed':source_stats,'candidate_signed':candidate_stats,'ingredient_ordinary':{k:ingredient[k]['conservative_total'] for k in ('source_7623','candidate')},'same_tariff_common_U_sha256':sha(HERE/'COMMON-U.json'),'source_17_resource_scope':'Fresh seven source resource checks derived from paired fresh native calculations; source catalogue not rerun.','native_result_sha256':sha(npath),'signed_result_sha256':sha(spath),'source_resource_file_sha256':sha(w/'producer54/validation_signed/SOURCE-RESOURCE.json'),'run_id':identity['run_id'],'supplier_premise_discharged':False,'same_original_premise_dominance_established':False,'selected_frontier_changed':False,'limitations':u['limitations']}
    (a.out/'RESOURCE-COMPARISON.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print(json.dumps({'status':report['status'],'claim':report['claim']},sort_keys=True),flush=True)
if __name__=='__main__':main()
