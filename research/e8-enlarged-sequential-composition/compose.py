"""Exact enlarged-sequential/signed-nine supplier interface and portable science.
Raw path-bound receipts remain intact. Only their provenance and elapsed time
are projected out; scientific cross-references are rebound to canonical receipts.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import copy,gzip,importlib.util,json,types
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

def run(source,full,signed,bit,geometry,source401,baseline,fusion,out):
 source,full,signed,bit,geometry,source401,baseline,fusion,out=map(Path,(source,full,signed,bit,geometry,source401,baseline,fusion,out));out.mkdir(parents=True,exist_ok=True)
 bitparent=source401/'vendor/bit'
 local=read(full/'local/RESULT.json');phase=read(full/'phase/RESIDUALS.json');adm=read(full/'banks/ADMISSION.json');dec=read(full/'banks/INDEPENDENT-ADMISSION.json');bridge=read(full/'banks/BRIDGE.json')
 assert local['status']=='PASS_CHANGED_GAUGE_LOCAL_RAW_DIRTY_SYMBOLIC_BOTH_ORIENTATIONS_FRAMES_LIFETIMES_AND_NEW_PHASES'
 assert phase['status']=='PASS_FRESH_ALL_CANONICAL_ENTRANCES_TWO_SIDED_RESIDUALS'
 assert adm['status']=='PASS_NEW_ARBITRARY_ENTRANCE_TWO_SIDED_BANK_TEMPLATE_FINITE_INVOICE'
 assert dec['status']=='PASS_INDEPENDENT_DECODED_TWO_SIDED_BANKS_SCHEDULE_PROFILE_AND_INVOICE'
 for x in [local,phase,adm,dec,bridge]:provenance(x)
 candidate=digest(full/'reconstruction/candidate.json')
 assert candidate=='7ff1782ab6fa0b846d7b00f57a034c05cd64b286eb9c3215efb184d5e9511408'
 assert all(x['candidate_sha256']==candidate for x in [local,phase,adm,dec,bridge['certificate']])
 assert(local['all_raw_columns'],local['gauges'],local['entrance_frames'],local['unit_entrance_gates'])==(1021,204,43,535)
 assert local['raw_operator_equals_same_entrance_nonY_baseline']and local['gauged_K_columns_zero']and local['helper_cleanup_subword_equal']
 assert local['new_and_reflected_exact_phase_pairs']==836 and local['sampled_full_symbolic_omission_controls']==3
 assert len(local['entrance_omission_algebraic_controls'])==535
 for orientation in ['forward','backward']:
  assert local['scalar_checks'][orientation]['independent_live_columns']==1021
  mutations=local['local_checks'][orientation]['mutation_controls'];assert len(mutations)==7 and all(x['rejected']for x in mutations)
 assert phase['fresh_frames']==43 and phase['fresh_address_columns']==22016
 tokens=read(full/'INDEPENDENT-TOKENS.json')
 assert tokens['status']=='PASS_WHOLE_EMITTED_RESPONSE_MAIN_CLEANUP_INDEPENDENT_HELPER_TOKENS'and tokens['candidate_sha256']==candidate
 assert tokens['local_programs_uncompressed_sha256']==local['local_programs_uncompressed_sha256']
 assert set(tokens['results'])=={'forward','backward'}and len(tokens['controls_rejected'])==2 and all(c['rejected']for c in tokens['controls_rejected'])
 assert all(r['independent_helper_operator_tokens']==204 and r['independent_live_columns']==1021 for r in tokens['results'].values())
 assert(adm['m'],adm['live'],adm['physical'],adm['banks_per_stage'],adm['deficit'])==(73,57207,57998,2943,9984)
 assert adm['rank_mass']==sum(int(k)*v for k,v in adm['profile'].items())==4166127
 assert dec['all_size_claim']is False and dec['stage_bank_products']==26487 and dec['owner_routes']==24992
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
 domain=read(full/'domain/RECEIPT.json')
 assert domain['status']=='PASS_RATIONAL_AND_LITERAL_COMPILER_DIAGNOSTIC_WITH_UNCHANGED_GXCORE_REJECTION'
 assert domain['candidates']['shared_long_resynth']['candidate_sha256']==candidate
 assert all(x['gxcore']=='REJECTED'and x['gx_fraction_check']=='PASS'for x in domain['candidates'].values())
 assert set(domain['emitted_primitive_replays'])=={'forward','backward'}
 for orientation,data in domain['emitted_primitive_replays'].items():
  assert data['endpoint_restored']and data['private_streams_zero']and data['raw_independent_columns']==1021
  assert data['actual_primitive_prefix_denominator_lcm']==(12 if orientation=='forward'else 24)
  assert data['halves_exactly_paid']==local['bills'][orientation]['totals']['halving_exposure']
  assert data['divides3_exactly_paid']==local['bills'][orientation]['totals']['divisor3_exposure']
 preflight=read(full/'reconstruction/PREFLIGHT.json');assert len(preflight['target_resynthesis_mutation_controls'])==6 and all(c['rejected']for c in preflight['target_resynthesis_mutation_controls'])
 science=dict(scalar_domain=omit_sources(domain),independent_helper_tokens=tokens,local=clocal,phase=cphase,admission=cadm,independent_decoder=cdec,bridge=cbridge,
  template_sha256=ctemplate,route_table_uncompressed_sha256=routes_sha,
  projection='Full scientific fields preserved. Delete only source_hashes provenance and local elapsed seconds; rebind template local/phase receipts, admission/decoder template, and bridge admission/decoder hashes to SHA256 of canonical JSON plus LF. Raw source binding is checked before projection and preserved in fresh outputs.')
 write(out/'SCIENCE.json',science)
 outer=load('normalization_source401_outer',source/'code/outer.py');moment=outer.coarse(adm['profile'],adm['m'],adm['live'])
 assert moment['lower']=='509476902427531203043/500000000000000000000000';write(out/'COMPLEX-MOMENTS.json',moment)
 supplier=dict(status='PASS_FRESH_NINE_STAGE_COMPLEX_INTERFACE',b=moment['lower'],m=adm['m'],W=adm['live'],physical=adm['physical'],
  profile=adm['profile'],moment=moment,bridge=cbridge,candidate_sha256=candidate,science_sha256=semantic(science),
  scope='Fresh PR410 enlarged entrances with original194 relations and all ten PR409 ordered promotions, whole-operator two-sided normalization; inherited all-size, correlated-bank, compiler/chart, precision and ordinary-wrapper assumptions remain. This profile replaces, rather than adds gains to, the parent heterogeneous/fusion profile.')
 write(out/'COMPLEX-SUPPLIER.json',supplier)
 priced=read(bit/'kappa.json');finite=read(signed/'FINITE.json')
 assert priced['bit_coarse']=='255384852701747/250000000000000000'and finite['coefficient']==71903549476531 and finite['payload_prefix_bits']==91
 raw_signed=read(signed/'RECEIPT.json');raw_geometry=read(geometry/'RECEIPT.json')
 assert raw_signed['status']=='PASS_SOURCE_BOUND_R822_NINE_STAGE_SIGNED_WITNESS_COMPLETE_PREFIX_AND_FINITE_BILL'
 assert raw_signed['fresh_native_bit_receipt_sha256']==digest(bit/'BIT-COMPOSITION-RECEIPT.json')
 for name,want in raw_signed['output_sha256'].items():assert digest(signed/name)==want
 assert raw_geometry['status']=='PASS_FRESH_ALL_PORT_DYADIC_NINE_STAGE_UNSPLIT_GEOMETRY'
 assert raw_geometry['geometry_sha256']==digest(geometry/'geometry.json')and raw_geometry['matrix_count']==12360
 assert raw_geometry['depth_inequality']==[5184,5000]and raw_geometry['denominators']==[1,2,4]
 signed_science={k:v for k,v in raw_signed.items()if k not in ['fresh_native_bit_receipt_sha256','signed_witness_replay_sha256']}
 write(out/'SIGNED9-SCIENCE.json',dict(signed=signed_science,finite=finite,geometry=read(geometry/'geometry.json'),geometry_receipt=raw_geometry))
 small_path=fusion/'assembly.py';small_text=small_path.read_text()
 old_hook="changed=text.replace(OLD,NEW);module=types.ModuleType('smaller_positive_slack_assembly')"
 old_shape="assert priced['K']==3 and priced['stages']==7 and m==56 and priced['T']==7"
 new_shape="assert priced['K']==4 and priced['stages']==9 and m==72 and priced['T']==3"
 new_hook="changed=text.replace(OLD,NEW);assert changed.count("+repr(old_shape)+")==1;changed=changed.replace("+repr(old_shape)+","+repr(new_shape)+");module=types.ModuleType('smaller_positive_slack_assembly')"
 assert small_text.count(old_hook)==1;adapted=small_text.replace(old_hook,new_hook)
 asm=types.ModuleType('shared_donor_signed9_assembly');asm.__file__=str(small_path);exec(compile(adapted,str(small_path),'exec'),asm.__dict__)
 write(out/'ASSEMBLY-ADAPTATION.json',dict(source_sha256=digest(small_path),adapted_sha256=sha256(adapted.encode()).hexdigest(),old_assertion=old_shape,new_assertion=new_shape,scope='Only bit supplier shape changes. All arithmetic, moment, finite invoice/cutoff, restored-row and outer assertions are retained.'))
 result=asm.run(baseline,bitparent,priced,finite,supplier)
 assert result['binding']=='complex'and result['outer_cutoffs']['common_cutoff']==14*10**30
 assert result['eta']==result['beta']==str(Q(1,10**30))
 assert Q(result['selected_saving'])<Q(moment['lower'])<Q(priced['bit_coarse'])
 assert len(result['finite_cutoffs'])==8 and all(x['charged_coefficient']==71903549476531 for x in result['finite_cutoffs'])
 assert result['kappa']=='508958297433848428641873/500000000000000000000000000'
 write(out/'ASSEMBLY.json',result)
 comparison=outer.assemble(moment['lower'],cbridge,priced['bit_coarse']);write(out/'SOURCE410-PARAMETERS.json',comparison)
 validation=dict(status='PASS_FRESH_ENLARGED_SEQUENTIAL204_AND_SIGNED_NINE_STAGE_COMPOSITION',
  candidate_sha256=candidate,ordinary_candidate_sha256='a2a1e957cec4f86fa7447037d757218d72b7f70c67391cc4dfb81ed60c0d00e6',
  kappa=result['kappa'],complex_b=moment['lower'],bit_c=priced['bit_coarse'],source410_parameters_kappa=comparison['kappa'],
  signed_bit_coefficient=finite['coefficient'],signed_bit_prefix_bits=91,outer_common_log2_cutoff=14*10**30,
  preflight=read(full/'reconstruction/PREFLIGHT.json'),science_sha256=semantic(science),
  output_sha256={n:digest(out/n)for n in ['SCIENCE.json','SIGNED9-SCIENCE.json','ASSEMBLY-ADAPTATION.json','COMPLEX-MOMENTS.json','COMPLEX-SUPPLIER.json','ASSEMBLY.json','SOURCE410-PARAMETERS.json']},
  scope='Finite checked source-template evidence, not a separately emitted global IR or an unconditional theorem. Complete raw and dirty local operators, independent entrance tokens, exact Gaussian phases, full interleaved owners/banks, complete primitive invoices, both moment engines, eight signed-bit continuations and 47 outer inequalities are checked. The unchanged fixed-sixths gxcore mirror rejects dirty intermediates; no gxcore or Lean-facing acceptance is claimed. Separately emitted paid HALF/divide3 primitives pass exact rational replay; common-grid precision remains conditional. All-size normalized windows, arbitrary correlated banks, signed-bit charts/compiler, prime/setup/recovery/precision, fixed tapes/restored rows, analytic interfaces and dominating C_full obligations remain conditional.')
 return validation
