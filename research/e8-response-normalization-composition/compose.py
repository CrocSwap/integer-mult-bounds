"""Exact fresh normalization/signed-seven supplier interface and portable science.
Raw path-bound receipts remain intact. Only their provenance and elapsed time
are projected out; scientific cross-references are rebound to canonical receipts.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import copy,gzip,importlib.util,json
read=lambda p:json.loads(Path(p).read_bytes())
digest=lambda p:sha256(Path(p).read_bytes()).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()+b'\n'
def semantic(x):return sha256(canonical(x)).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def provenance(x):
 if isinstance(x,dict):
  if 'source_hashes'in x:assert all(digest(p)==h for p,h in x['source_hashes'].items())
  for k,v in x.items():
   if k!='source_hashes':provenance(v)
 elif isinstance(x,list):
  for v in x:provenance(v)
def omit_sources(x):
 if isinstance(x,dict):return{k:omit_sources(v)for k,v in x.items()if k!='source_hashes'}
 if isinstance(x,list):return list(map(omit_sources,x))
 return x

def run(source,full,signed,baseline,bitparent,fusion,out):
 source,full,signed,baseline,bitparent,fusion,out=map(Path,(source,full,signed,baseline,bitparent,fusion,out));out.mkdir(parents=True,exist_ok=True)
 local=read(full/'local/RESULT.json');phase=read(full/'phase/RESIDUALS.json');adm=read(full/'banks/ADMISSION.json');dec=read(full/'banks/INDEPENDENT-ADMISSION.json');bridge=read(full/'banks/BRIDGE.json')
 assert local['status']=='PASS_CHANGED_GAUGE_LOCAL_RAW_DIRTY_SYMBOLIC_BOTH_ORIENTATIONS_FRAMES_LIFETIMES_AND_NEW_PHASES'
 assert phase['status']=='PASS_FRESH_ALL_CANONICAL_ENTRANCES_TWO_SIDED_RESIDUALS'
 assert adm['status']=='PASS_NEW_ARBITRARY_ENTRANCE_TWO_SIDED_BANK_TEMPLATE_FINITE_INVOICE'
 assert dec['status']=='PASS_INDEPENDENT_DECODED_TWO_SIDED_BANKS_SCHEDULE_PROFILE_AND_INVOICE'
 for x in [local,phase,adm,dec,bridge]:provenance(x)
 candidate=digest(full/'reconstruction/candidate.json')
 assert candidate=='a93e9b7336157fc1ee42f75fc787de54c1aef480e293e11c16e9db790115ecbc'
 assert all(x['candidate_sha256']==candidate for x in [local,phase,adm,dec,bridge['certificate']])
 assert(local['all_raw_columns'],local['gauges'],local['entrance_frames'],local['unit_entrance_gates'])==(1021,119,26,240)
 assert local['raw_operator_equals_same_entrance_nonY_baseline']and local['gauged_K_columns_zero']and local['helper_cleanup_subword_equal']
 assert local['new_and_reflected_exact_phase_pairs']==532 and local['sampled_full_symbolic_omission_controls']==3
 assert len(local['entrance_omission_algebraic_controls'])==240
 for orientation in ['forward','backward']:
  assert local['scalar_checks'][orientation]['independent_live_columns']==1021
  mutations=local['local_checks'][orientation]['mutation_controls'];assert len(mutations)==7 and all(x['rejected']for x in mutations)
 assert phase['fresh_frames']==26 and phase['fresh_address_columns']==13312
 tokens=read(full/'INDEPENDENT-TOKENS.json')
 assert tokens['status']=='PASS_WHOLE_EMITTED_RESPONSE_MAIN_CLEANUP_INDEPENDENT_HELPER_TOKENS'and tokens['candidate_sha256']==candidate
 assert tokens['local_programs_uncompressed_sha256']==local['local_programs_uncompressed_sha256']
 assert set(tokens['results'])=={'forward','backward'}and len(tokens['controls_rejected'])==2 and all(c['rejected']for c in tokens['controls_rejected'])
 assert all(r['independent_helper_operator_tokens']==119 and r['independent_live_columns']==1021 for r in tokens['results'].values())
 assert(adm['m'],adm['live'],adm['physical'],adm['banks_per_stage'],adm['deficit'])==(73,14412,15203,748,2496)
 assert adm['rank_mass']==sum(int(k)*v for k,v in adm['profile'].items())==1049580
 assert dec['all_size_claim']is False and dec['stage_bank_products']==6732 and dec['owner_routes']==6248
 template_raw=gzip.decompress((full/'banks/TEMPLATE.json.gz').read_bytes());routes_raw=gzip.decompress((full/'banks/ROUTES.json.gz').read_bytes())
 template=json.loads(template_raw);template_sha=sha256(template_raw).hexdigest();routes_sha=sha256(routes_raw).hexdigest()
 assert template_sha==adm['template_sha256']==dec['template_sha256']==bridge['certificate']['template_sha256']
 assert routes_sha==adm['route_table_sha256']==dec['route_table_sha256']==template['route_table_sha256']
 assert template['local_admission_sha256']==digest(full/'local/RESULT.json')
 assert template['residual_phase_sha256']==digest(full/'phase/RESIDUALS.json')
 assert bridge['certificate']['supplier_admission_sha256']==digest(full/'banks/ADMISSION.json')
 assert bridge['certificate']['independent_decoder_sha256']==digest(full/'banks/INDEPENDENT-ADMISSION.json')
 assert bridge['semantic']==dict(G=dict(base=2,exponent=30000),E=dict(base=2,exponent=100000),B_upper=dict(base=2,exponent=100001),C0=dict(base=2,exponent=210000),C1=1,strict_literal_gap=1,induction_gap_lower=1)
 assert bridge['rows']==dict(coefficient=20161,degree=10**6,suffix_slope=4*10**6,degree_gap='23971789/25')
 bc=bridge['certificate']
 assert bc['new_local_bound']<2**48 and bc['new_logical_bits']<6050 and bc['new_router_bits']<30000
 assert bc['new_literal_bits']<100000 and bc['new_B_bits']<=100001 and bc['new_C0_required_bits']<210000
 assert bc['new_required_row']<20161 and bc['halving_integer_inequality'][0]>bc['halving_integer_inequality'][1]
 # The raw bindings above are mandatory. These four replacements remove only
 # runtime-dependent receipt hashes, retaining every field of their science.
 clocal=omit_sources(local);assert isinstance(clocal.pop('seconds'),(int,float))
 cphase=copy.deepcopy(phase)
 template['local_admission_sha256']=semantic(clocal);template['residual_phase_sha256']=semantic(cphase)
 ctemplate=semantic(template)
 cadm=omit_sources(adm);cadm['template_sha256']=ctemplate
 cdec=omit_sources(dec);cdec['template_sha256']=ctemplate
 cbridge=omit_sources(bridge);cbc=cbridge['certificate'];cbc['template_sha256']=ctemplate
 cbc['supplier_admission_sha256']=semantic(cadm);cbc['independent_decoder_sha256']=semantic(cdec)
 science=dict(independent_helper_tokens=tokens,local=clocal,phase=cphase,admission=cadm,independent_decoder=cdec,bridge=cbridge,
  template_sha256=ctemplate,route_table_uncompressed_sha256=routes_sha,
  projection='Full scientific fields preserved. Delete only source_hashes provenance and local elapsed seconds; rebind template local/phase receipts, admission/decoder template, and bridge admission/decoder hashes to SHA256 of canonical JSON plus LF. Raw source binding is checked before projection and preserved in fresh outputs.')
 write(out/'SCIENCE.json',science)
 outer=load('normalization_source401_outer',source/'code/outer.py');moment=outer.coarse(adm['profile'],adm['m'],adm['live'])
 assert moment['lower']=='1014633208253716030963/1000000000000000000000000';write(out/'COMPLEX-MOMENTS.json',moment)
 supplier=dict(status='PASS_FRESH_NINE_STAGE_COMPLEX_INTERFACE',b=moment['lower'],m=adm['m'],W=adm['live'],physical=adm['physical'],
  profile=adm['profile'],moment=moment,bridge=cbridge,candidate_sha256=candidate,science_sha256=semantic(science),
  scope='Fresh PR401 response-subspace whole-operator two-sided normalization; inherited all-size, correlated-bank, compiler/chart, precision and ordinary-wrapper assumptions remain. This profile replaces, rather than adds gains to, the parent heterogeneous/fusion profile.')
 write(out/'COMPLEX-SUPPLIER.json',supplier)
 priced=read(signed/'composition/baseline/replay/unsplit-bit/kappa-input.json');finite=read(signed/'validation/FINITE.json')
 assert priced['bit_coarse']=='8128527708459/8000000000000000'and finite['coefficient']==56223565818967 and finite['payload_prefix_bits']==71
 result=load('normalization_signed7_assembly',fusion/'assembly.py').run(baseline,bitparent,priced,finite,supplier)
 assert result['binding']=='complex'and result['outer_cutoffs']['common_cutoff']==14*10**30
 assert result['eta']==result['beta']==str(Q(1,10**30))
 assert Q(result['selected_saving'])<Q(moment['lower'])<Q(priced['bit_coarse'])
 assert len(result['finite_cutoffs'])==8 and all(x['charged_coefficient']==56223565818967 for x in result['finite_cutoffs'])
 assert result['kappa']=='1013604771192819386862427/1000000000000000000000000000'
 write(out/'ASSEMBLY.json',result)
 comparison=outer.assemble(moment['lower'],cbridge,priced['bit_coarse']);write(out/'SOURCE401-PARAMETERS.json',comparison)
 validation=dict(status='PASS_FRESH_RESPONSE_NORMALIZATION_AND_SIGNED_SEVEN_STAGE_COMPOSITION',
  candidate_sha256=candidate,ordinary_candidate_sha256='a2a1e957cec4f86fa7447037d757218d72b7f70c67391cc4dfb81ed60c0d00e6',
  kappa=result['kappa'],complex_b=moment['lower'],bit_c=priced['bit_coarse'],source401_parameters_kappa=comparison['kappa'],
  signed_bit_coefficient=finite['coefficient'],signed_bit_prefix_bits=71,outer_common_log2_cutoff=14*10**30,
  preflight=read(full/'reconstruction/PREFLIGHT.json'),science_sha256=semantic(science),
  output_sha256={n:digest(out/n)for n in ['SCIENCE.json','COMPLEX-MOMENTS.json','COMPLEX-SUPPLIER.json','ASSEMBLY.json','SOURCE401-PARAMETERS.json']},
  scope='Finite checked source-template evidence, not a separately emitted global IR or an unconditional theorem. Complete raw and dirty local operators, independent entrance tokens, exact Gaussian phases, full interleaved owners/banks, complete primitive invoices, both moment engines, eight signed-bit continuations and 47 outer inequalities are checked. All-size normalized windows, arbitrary correlated banks, signed-bit charts/compiler, prime/setup/recovery/precision, fixed tapes/restored rows, analytic interfaces and dominating C_full obligations remain conditional.')
 return validation
