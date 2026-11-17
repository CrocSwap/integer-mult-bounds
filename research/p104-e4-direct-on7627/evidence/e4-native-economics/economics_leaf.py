# SPDX-License-Identifier: Apache-2.0
"""Candidate-bound 18-call native ingredient invoice and precision leaf.

No work is performed at import. Invoke only within the authenticated source
context and an independently approved, bounded controller. This is not the
17-call signed application, physical qualification or a kappa admission.
"""
import copy, hashlib, importlib.util, json, sys
from fractions import Fraction as Q
from types import ModuleType

SOURCE='b80b6e74bff87c8d8160c5e121dac7c68df0827a7061847b896075417a346238'
CANDIDATE='1ea66c263faa51da704d7aae944f3371400afaf5df8a56904ab96319f6554e0e'
RANK9='e71097ca81a082afd7c647324a6c94cb357aeb1084693a095a0f3e0b45a9b11a'
def need(ok,msg):
    if not ok: raise ValueError(msg)
def normalize(x): return json.loads(json.dumps(x,default=str))
def word_hash(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def adapt(path, helper_count, odd, frac, name):
    raw=path.read_bytes();need(hashlib.sha256(raw).hexdigest()==RANK9,'rank9 source hash')
    need(type(helper_count) is int and helper_count==1101,'helper census')
    need(type(odd) is int and odd>0 and odd%2==1 and type(frac) is int and 0<=frac<=256,'grid parameters')
    src=raw.decode(); changes=[]
    pairs=[('== 1080','== '+str(helper_count)),
           ('fresh_arbitrary_helpers=18 * 1080','fresh_arbitrary_helpers=18 * '+str(helper_count)),
           ('grid.word_run(word), grid.caller_run(caller)',f'grid.word_run(word, scale={odd}, frac={frac}), grid.caller_run(caller)'),
           ("    exec(compile(src, str(env_path), 'exec'), env.__dict__)",
            '    assert src.count("(life, peak, owned_count) == (54, 43, 51)") == 1\n    src=src.replace("(life, peak, owned_count) == (54, 43, 51)","(life, peak, owned_count) == (204, 50, 68)")\n    exec(compile(src, str(env_path), \'exec\'), env.__dict__)')]
    for old,new in pairs:
        need(src.count(old)==1,'unique adaptation anchor '+old)
        src=src.replace(old,new);changes.append({'before':old,'after':new,'occurrences':1})
    obj=ModuleType(name);obj.__file__=str(path);sys.modules[name]=obj;exec(compile(src,str(path),'exec'),obj.__dict__)
    return obj,{'source_sha256':RANK9,'adapted_sha256':hashlib.sha256(src.encode()).hexdigest(),'edits':changes}
def delta(after,before):
    return {str(k):after.get(k,0)-before.get(k,0) for k in sorted(set(after)|set(before)) if after.get(k,0)!=before.get(k,0)}
def surcharge(caller):
    total=0
    for e in caller['events']:
        if e[0]=='B' and e[1] in ('ADD','SCALE'):
            q=Q(e[4] if e[1]=='ADD' else e[3]);a,d=abs(q.numerator),q.denominator
            total+=4*(a.bit_length()+d.bit_length()+1+(a.bit_count() if e[1]=='ADD' else 0))
    return total*len(caller['types']['B']['ports'])
def adjusted(unadjusted,routes,extra):
    b=copy.deepcopy(unadjusted);diff=routes-b['caller_items']['B']['fused_routes']
    b['caller_items']['B']['fused_routes']=routes
    for k in ('caller_total','raw_upper','conservative_total'):b[k]+=diff
    b['extra_B_scalar_surcharge']=extra;b['conservative_total']+=extra
    b['margin_to_billion']=10**9-b['conservative_total']
    need(b['margin_to_billion']>0,'ordinary strict billion bound')
    return b

def run(vendor,archive,rank9,bundle,old,new,before,after,grids,prior):
    need(__debug__,'assertions required in retained code')
    need(word_hash(old)==SOURCE and word_hash(new)==CANDIDATE,'literal word hashes')
    need(prior['status']=='PASS_SWARM30_COMPLETE_NATIVE' and prior['word_canonical_sha256']==SOURCE,'prior identity')
    need(normalize(before)==prior['native'] and not before['bad_inputs'] and not after['bad_inputs'],'fresh native source binding')
    for k in ('public','helpers','rises','owned_peak','lifetimes'):
        need(before[k]==after[k],'native shared contract '+k)
    need(before['lifetimes']==204 and before['owned_peak']==50 and old['owned_fields']==new['owned_fields']==68,'ownership counts')
    need(delta(after['paid'],before['paid'])=={'2':-1,'3':-1,'5':1},'actual E4 native profile')
    need(normalize(grids['source']['grid'])==prior['grid'] and normalize(grids['source']['derived_grid'])==prior['derived_grid'],'source grid prior agreement')
    sys.path.insert(0,str(rank9))
    modules={}; records={}
    for label in ('source','candidate'):
        g=grids[label]['derived_grid'];modules[label],records[label]=adapt(rank9/'candidate_gate.py',sum(before['helpers'].values()),g['odd_scale'],g['fractional_bits'],'e4_economics_rank9_'+label)
    G=load('e4_economics_gate',bundle/'gate.py')
    caller_path=rank9/'dyadic/CALLER.json';raw=caller_path.read_bytes();need(hashlib.sha256(raw).hexdigest()==G.CALLER,'authenticated 18-call ingredient caller');caller=json.loads(raw)
    I=modules['source'].independent(vendor)
    symbolic=I.caller(caller);need(not symbolic['bad_outputs'] and normalize(symbolic)==prior['caller'],'fresh ingredient caller')
    src_invoice=I.invoices(old,caller,before);new_invoice=I.invoices(new,caller,after)
    need(normalize(src_invoice)==prior['invoice'],'fresh source 18-call invoice')
    need(normalize(src_invoice['T'])==normalize(new_invoice['T']) and src_invoice['S']==new_invoice['S']==1520,'18-call target and rank surplus')
    need(delta(new_invoice['P'],src_invoice['P'])=={'2':-18,'3':-18,'5':18},'18-call paid delta')
    need(src_invoice['empty_root_credits']==new_invoice['empty_root_credits']==0,'no empty-root credit')
    old_raw=I.ordinary(old,caller,before);new_raw=I.ordinary(new,caller,after)
    routes=prior['ordinary']['caller_items']['B']['fused_routes'];extra=surcharge(caller)
    bindings=prior['signed_routes']['bindings']
    need(len(bindings)==16 and 1000*sum(len(row['caller_fields'])*row['ordinary_elementary_units'] for row in bindings)==routes,'historical physical route inventory and tariff')
    need(extra==prior['ordinary']['extra_B_scalar_surcharge'],'caller scalar surcharge')
    old_bill=adjusted(old_raw,routes,extra);new_bill=adjusted(new_raw,routes,extra)
    need(normalize(old_bill)==prior['ordinary'],'source complete 18-call ordinary reproduction')
    # Recompute the source's own gate, not its earlier comparison with #7624.
    interval=load('e4_economics_source_interval',vendor/'interval_gate.py')
    independent_price=load('e4_economics_source_directed',archive/'audit_price.py')
    historical=prior['gate']; lo,hi=map(Q,historical['raw_bracket'])
    claim,tested=map(Q,(historical['claim'],historical['tested']))
    source_gate=interval.gate(src_invoice,claim,tested,lo,hi,historical['BIT_pin'])
    need(normalize(source_gate)==historical,'fresh source gate reproduces prior record')
    hist=G.signed(src_invoice)
    diagnostic,(ind_lo,ind_hi),(ind_lower,ind_upper)=independent_price.crossing(hist)
    need(lo<=ind_lo<ind_hi<=hi,'independent source crossing within prior bracket')
    need(interval.moment(hist,lo)[0]>0 and interval.moment(hist,hi)[1]<0,'source interval endpoint signs')
    for k in (lo,hi,tested):
        a,b=independent_price.raw_margin(hist,k)
        need((a>0 if k in (lo,tested) else b<0),'independent source endpoint sign')
    source_price={'diagnostic_crossing':diagnostic,'raw_bracket':[str(lo),str(hi)],
       'independent_raw_bracket':[str(ind_lo),str(ind_hi)],
       'interval_margin_at_bracket':[interval.show(interval.moment(hist,lo)),interval.show(interval.moment(hist,hi))],
       'independent_margin_at_bracket':[[str(x) for x in independent_price.raw_margin(hist,k)] for k in (lo,hi)],
       'independent_crossing_margins':[[str(x) for x in m] for m in (ind_lower,ind_upper)],
       'comparison_scope':'Fresh source invoice and crossing; historical comparison to #7624 not reconstructed here.'}
    prior_bracket=prior['price']['independent_raw_bracket']
    need([Q(x) for x in prior_bracket]==[ind_lo,ind_hi],'source independent bracket reproduces prior record')
    gate,price=G.exact_price(vendor,archive,src_invoice,new_invoice,prior)
    manifest=json.loads((vendor/'INDEPENDENT-SOURCES.json').read_bytes())
    binding=load('e4_economics_bit_binding',archive/'verify.py');binding.bit_binding(I,manifest)
    old_precision=modules['source'].precision(vendor,old,caller,source_gate,manifest)
    need(normalize(old_precision)==prior['precision'],'fresh source precision reproduction')
    new_precision=modules['candidate'].precision(vendor,new,caller,gate,manifest)
    for label,precision in [('source',old_precision),('candidate',new_precision)]:
        derived=grids[label]['derived_grid']; wg=precision['word']
        need(wg['odd_scale_lcm']==derived['odd_scale'] and wg['dyadic_height']==derived['fractional_bits'] and wg['maximum_scaled_mass']==derived['scaled_maximum_mass'],'independent precision grid match '+label)
    common=max(old_precision['context_c'],new_precision['context_c']);need(common<=4096,'common context cap')
    return normalize({'schema':'e4-native-economics-leaf/v1','status':'PASS_E4_18_CALL_INGREDIENT_ECONOMICS_ONLY',
      'source_canonical_sha256':SOURCE,'candidate_canonical_sha256':CANDIDATE,'caller_sha256':G.CALLER,'calls':18,
      'expected_route_charge':{'source':routes,'candidate':routes,'basis':'recounted 16 authenticated historical caller bindings; fresh physical comparison required'},
      'source_invoice':src_invoice,'candidate_invoice':new_invoice,'source_ordinary':old_bill,'candidate_ordinary':new_bill,
      'source_precision':old_precision,'candidate_precision':new_precision,'common_context_c':common,
      'source_gate':source_gate,'source_price':source_price,'candidate_gate':gate,'candidate_price':price,'adapters':records,'limitations':['18-call ingredient branch only; not signed 17-call price, physical qualification or kappa admission.', 'Common U remains an explicit unimplemented supplier premise for both actual 204-lifetime histories.', 'Route adjustment inherits prior receipt and requires fresh candidate physical route qualification.']})
