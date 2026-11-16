"""Prepare the single signed #7623 composition adapter; no runner execution.

The caller supplies a prepared work tree and the frozen research round root.
Every source replacement is counted exactly once and recorded with content hashes.
Predecessor attribution and checks are retained; this file confers no admission.
"""
from pathlib import Path
from hashlib import sha256
import json

SOURCE_CAN='48e1845e6b24832731705a3ff096b22d2b807428f7d625d06b45adfe3b5a738c'
SOURCE_GZ='97391721ab7d30f8dd84c8d3c29a3c3ed2df2d65ca55e7ff8329bd09877681d2'
BASELINE=SOURCE_CAN
ORIGINAL_BASE='6c46ad38d812ae110392f1c977cc6f02665f8860e98ef1c21cb539ff3779533d'
INVOICE_SHA='5be4724fde8264b8b1b4a565ea2eb1a56339f29528db40728b3fab210c44208d'
SIGNED_ORIGINAL_SHA='c26b0c59b44eaab54a5f275eeffe77f7e5cbb7316b255d7c3ea127b9ce32b997'
HELPER_ORIGINAL_SHA='3bef6eb00eaa454261f53dfca05a7cc0398c4dbe3bd4b76bc4041ba7d275f678'

def adapt(rootwork, roundroot):
    rootwork=Path(rootwork).resolve();roundroot=Path(roundroot).resolve()
    runner=rootwork/'producer54/validation_signed/run.py'
    gate=roundroot/'compose7623/run/case'
    result=json.loads((gate/'RESULT.json').read_bytes())
    if result['status']!='PASS_DIFFERENTIAL_ONLY_PROVISIONAL_UNDER_COMMON_U':raise ValueError('First gate incomplete')
    for rel in ('built/candidate-word.json.gz','built/edit-manifest.json','built/status.json','exact/EXACT.json.gz','exact/status.json','rankone/RANKONE.json','rankone/status.json','physical/PHYSICAL.json','physical/status.json','price/PRICE.json','price/invoice-source-normalized.json','price/invoice-new.json'):
        if sha256((gate/rel).read_bytes()).hexdigest()!=result['receipt_hashes'][rel]:raise ValueError('First gate receipt '+rel)
    manifest=json.loads((gate/'built/edit-manifest.json').read_bytes())
    price=json.loads((gate/'price/PRICE.json').read_bytes())
    if manifest['source_canonical_sha256']!=SOURCE_CAN or manifest['source_gzip_sha256']!=SOURCE_GZ:raise ValueError('Source binding mismatch')
    CANDIDATE=manifest['candidate_canonical_sha256']
    if price['status']!='PROVISIONAL_UNDER_COMMON_U' or price['bindings']['candidate_canonical_sha256']!=CANDIDATE or price['bindings']['original_word_canonical_sha256']!=SOURCE_CAN or price['bindings']['manifest_sha256']!=sha256((gate/'built/edit-manifest.json').read_bytes()).hexdigest() or price['bindings']['old_invoice_sha256']!=INVOICE_SHA:raise ValueError('Price binding mismatch')
    path=gate/'price/PRICE.json'
    invoice=roundroot/'inputs/pr7623/research/p104-loan-snapshot-engine-on7621/data/invoice-new.json'
    if sha256(invoice.read_bytes()).hexdigest()!=INVOICE_SHA:raise ValueError('source invoice pin mismatch')
    helper=rootwork/'producer54/validation_signed/w2_adapt.py'
    helper_raw=helper.read_bytes()
    if sha256(helper_raw).hexdigest()!=HELPER_ORIGINAL_SHA:raise ValueError('Unexpected original signed helper SHA-256')
    helper_old=b'(life, peak, owned_count) == (167, 50, 68)'
    helper_new=b'(life, peak, owned_count) == (180, 50, 68)'
    if helper_raw.count(helper_old)!=1:raise ValueError('Expected one lifetime helper patch')
    helper_adapted=helper_raw.replace(helper_old,helper_new,1)
    helper_adapted_sha=sha256(helper_adapted).hexdigest()
    compile(helper_adapted,str(helper),'exec')
    raw=runner.read_bytes()
    if sha256(raw).hexdigest()!=SIGNED_ORIGINAL_SHA:raise ValueError('Unexpected original signed runner SHA-256')
    crlf=raw.count(b'\r\n')
    if crlf!=136 or raw.count(b'\r')!=136 or raw.count(b'\n')!=136:
        raise ValueError('Unexpected original signed runner line endings')
    normalized=raw.replace(b'\r\n',b'\n')
    text=normalized.decode();changes=[]
    def patch(label,old,new):
        nonlocal text
        count=text.count(old)
        if count!=1:raise ValueError(f'{label}: expected one source occurrence, got {count}')
        text=text.replace(old,new,1)
        changes.append({'label':label,'occurrences':count,'old':old,'new':new})
    patch('round root binding',"OUT=HERE/'RESULT.json'", "OUT=HERE/'RESULT.json'\nROUND_ROOT=Path("+repr(str(roundroot))+")")
    patch('helper hash binding',"adapter=load('producer_adapter',HERE/'w2_adapt.py')", "assert sha256((HERE/'w2_adapt.py').read_bytes()).hexdigest()=="+repr(helper_adapted_sha)+", 'Prepared helper hash mismatch'\nadapter=load('producer_adapter',HERE/'w2_adapt.py')")
    patch('candidate hash',ORIGINAL_BASE,CANDIDATE)
    patch('native status',"PASS_W3_ADAPTED_COMPLETE_NATIVE","PASS_CONTACT7623_COMPLETE_NATIVE")
    patch('native launch receipt',"assert sha256(canonical(new_word)).hexdigest()==new_result['word_canonical_sha256']","""assert sha256(canonical(new_word)).hexdigest()==new_result['word_canonical_sha256']
receipt=read(ROOT/'native.receipt.json')
assert receipt['stage']=='native' and receipt['exit']==0 and isinstance(receipt['run_id'],str) and receipt['run_id']
assert receipt['run_id']==read(ROOT/'QUALIFICATION-ID.json')['run_id'], 'Fresh qualification run ID'
assert receipt['candidate_canonical_sha256']==sha256(canonical(new_word)).hexdigest()
assert receipt['native_result_sha256']==sha256(NATIVE.read_bytes()).hexdigest()
assert receipt['adapter_sha256']==sha256((ROOT/'CONTACT7623-ADAPTERS.json').read_bytes()).hexdigest()
assert receipt['launcher_sha256']==sha256((ROOT/'CONTACT7623-LAUNCHER.py').read_bytes()).hexdigest()
""".rstrip())
    patch('signed 7546 paid delta',"delta=={1: -272, 2: 1224, 3: -2499, 4: 952, 5: 153, 6: 102, 8: 17} and ","")
    patch('signed 7604 paid delta',"  assert {r:after['P'].get(r,0)-peer_invoice['P'].get(r,0)for r in ranks if after['P'].get(r,0)!=peer_invoice['P'].get(r,0)}=={1: -204, 2: 1292, 3: -2516, 4: 935, 5: 136, 6: 102, 8: 17}","  peer_delta={r:after['P'].get(r,0)-peer_invoice['P'].get(r,0)for r in ranks if after['P'].get(r,0)!=peer_invoice['P'].get(r,0)}")
    patch('signed paid count',"sum(after['P'].values())==110145","sum(after['P'].values())==110111")
    old="  candidate_invoice=read(FROZEN/'CANDIDATE-INVOICE.json')\n  assert normal(after['P'])==candidate_invoice['paid'] and normal(after['T'])==candidate_invoice['targets']"
    new="""  # Reconstruct the current #7623 baseline with this actual native inventory
  # and the very same signed caller, not from a projected raw delta.
  baseline_word=read(FROZEN/'7623-WORD.json.gz')
  assert sha256(canonical(baseline_word)).hexdigest()=="""+repr(BASELINE)+"""
  baseline_native=ind.native(baseline_word);assert not baseline_native['bad_inputs']
  baseline_invoice=ind.invoices(baseline_word,C,baseline_native)
  source_invoice_path=FROZEN/'7623-INVOICE.json'
  assert sha256(source_invoice_path.read_bytes()).hexdigest()=="""+repr(INVOICE_SHA)+"""
  source_invoice=read(source_invoice_path)
  assert normal(baseline_invoice['P'])==source_invoice['paid'] and normal(baseline_invoice['T'])==source_invoice['targets'], 'Fresh signed #7623 baseline invoice'
  assert baseline_invoice['S']==1424 and not baseline_invoice['empty_root_credits']
  assert sum(baseline_invoice['P'].values())==110145 and sum(baseline_invoice['T'].values())==22461
  actual_delta={r:after['P'].get(r,0)-baseline_invoice['P'].get(r,0) for r in set(after['P'])|set(baseline_invoice['P']) if after['P'].get(r,0)!=baseline_invoice['P'].get(r,0)}
  expected_delta={1:-51,2:17,4:-17,5:17}
  assert actual_delta==expected_delta and after['T']==baseline_invoice['T'], 'Fresh complete signed #7623 comparison'
  def delta_from_source(prior):
   ranks=set(baseline_invoice['P'])|set(prior['P'])|set(expected_delta)
   return {r:baseline_invoice['P'].get(r,0)-prior['P'].get(r,0)+expected_delta.get(r,0) for r in ranks if baseline_invoice['P'].get(r,0)-prior['P'].get(r,0)+expected_delta.get(r,0)}
  assert delta==delta_from_source(before) and peer_delta==delta_from_source(peer_invoice), 'Derived baseline comparisons'
  candidate_invoice=read(FROZEN/'CANDIDATE-INVOICE.json')
  assert normal(after['P'])==candidate_invoice['paid'] and normal(after['T'])==candidate_invoice['targets']
  gate_path=FROZEN/'CONTACT7623-PRICE.json'
  assert sha256(gate_path.read_bytes()).hexdigest()=="""+repr(sha256(path.read_bytes()).hexdigest())+"""
  first_gate=read(gate_path)
  assert first_gate['status']=='PROVISIONAL_UNDER_COMMON_U' and first_gate['bindings']['candidate_canonical_sha256']=="""+repr(CANDIDATE)+"""
  assert first_gate['bindings']['original_word_canonical_sha256']=="""+repr(BASELINE)+""" and first_gate['bindings']['old_invoice_sha256']=="""+repr(INVOICE_SHA)+"""
  assert sha256((FROZEN/'CANDIDATE-INVOICE.json').read_bytes()).hexdigest()==first_gate['candidate_invoice']['sha256'], 'First-gate candidate invoice bytes'
  first_claim=Q(first_gate['claim']);first_probe=Q(first_gate['tested']);old_upper=Q(first_gate['old_published_raw_upper'])
  assert old_upper==Q('0.0036624027916') and old_upper<first_claim<first_probe
""".rstrip()
    patch('fresh actual baseline and first gate',old,new)
    old="  assert Q(gate['claim'])>=Q('0.00366110261815'),'Conservative public claim is within the proved application'\n  public_claim=Q('0.00366110261815')\n  public_gate=directed.gate(after,public_claim,public_claim+Q(1,10**18),*map(Q,gate['raw_bracket']),Q(gate['BIT_pin']))"
    new="""  assert directed.moment(G.signed(baseline_invoice),old_upper)[1]<0, 'Current #7623 invoice rejects its certified upper bound'
  assert directed.moment(G.signed(baseline_invoice),first_claim)[1]<0, 'Current #7623 rejects candidate claim'
  assert Q(gate['claim'])>=first_claim and first_probe<Q(gate['raw_bracket'][0]), 'First gate claim and probe within fresh signed bracket'
  public_claim=first_claim
  public_gate=directed.gate(after,public_claim,first_probe,*map(Q,gate['raw_bracket']),Q(gate['BIT_pin']))"""
    patch('fresh claim probe and baseline rejection',old,new)
    patch('price receipt baseline',"native_baseline_rejects_new_claim=True,signed_incumbent_rejects_new_claim=True,", "native_baseline_rejects_new_claim=True,signed_incumbent_rejects_new_claim=True,\n    baseline_7623=baseline_invoice,baseline_7623_rejects_claim=True,baseline_7623_rejects_raw_upper=True,\n    first_gate_claim=first_claim,first_gate_probe=first_probe,first_gate_old_upper=old_upper,")
    old="  assert fresh_price['gate']==partial['compiler_outer']"
    new="""  assert fresh_price['gate']==partial['compiler_outer']
  # Same actual caller and same independent ordinary model for both words.
  # Mirror the seven-check partial admission's exact, counted ordinary patches.
  ordinary_code=code[code.index('def ordinary('):code.index('def main(')]
  ordinary_patches=(('calls=18;',"calls=C['stages'];"),
      ("queryroute=sum(p*1000*(2+(e[4]==-1)) for e in qr)","queryroute=sum(p*1000*(2+(e[4]==-1)) for e in qr)\\n  fusedroute=sum(36500*p for e in C['events'] if e[:2]==[ty,'IDLE_ODD'])"),
      ('idle_routes=idleroute,query_routes=queryroute)','idle_routes=idleroute,query_routes=queryroute,fused_routes=fusedroute)'))
  for find,replacement in ordinary_patches:
   assert ordinary_code.count(find)==1, 'Exact ordinary patch count'
   ordinary_code=ordinary_code.replace(find,replacement,1)
  exec(compile(ordinary_code,str(folder/'independent.py'),'exec'),ind.__dict__)
  ordinary_base=normal(ind.ordinary(baseline_word,C,baseline_native))
  ordinary_candidate=normal(ind.ordinary(new_word,C,inventories[1]))
  charged=partial['ordinary'];caller_surcharge=charged['all_caller_scalar_surcharge'];conversions=charged['charged_caller_odd_conversions']
  for key in ('scalar_upper','init_clear_allowance','route_items','routing','caller_items','caller_total','raw_upper','per_input_conversion','lambda_second_charge','odd_divisions','lambda_paid_rank1_would_reduce_S_by'):
   assert ordinary_candidate[key]==charged[key], 'Fresh partial ordinary mismatch '+key
  assert ordinary_candidate['conservative_total']+caller_surcharge+conversions==charged['conservative_total'], 'Fresh complete ordinary bill mismatch'
  matched_base=ordinary_base['conservative_total']+caller_surcharge+conversions
  matched_candidate=charged['conservative_total']
  assert matched_base<10**9 and matched_candidate<10**9, 'Matched ordinary bound'
  matched_ordinary=dict(model='same actual signed caller and independent ordinary model; same caller surcharge and conversion',
    source=ordinary_base,candidate=ordinary_candidate,caller_scalar_surcharge=caller_surcharge,
    caller_odd_conversions=conversions,source_total=matched_base,candidate_total=matched_candidate,
    candidate_partial_ordinary=charged,complete_U_tariff='unknown; separate qualification required')
  (HERE/'MATCHED-ORDINARY.json').write_text(json.dumps(matched_ordinary,sort_keys=True,indent=2)+'\\n')"""
    patch('matched ordinary and fresh partial bill',old,new)
    old="  (HERE/'MATCHED-ORDINARY.json').write_text(json.dumps(matched_ordinary,sort_keys=True,indent=2)+'\\n')"
    new="""  (HERE/'MATCHED-ORDINARY.json').write_text(json.dumps(matched_ordinary,sort_keys=True,indent=2)+'\\n')
  # A separate pristine source replay: the source record below is derived from
  # THIS fresh candidate native run; it is not a fresh standalone native pass.
  assert normal(baseline_native)==new_result['source_native'], 'Fresh source native inventory binding'
  paired=new_result['paired_precision'];paired_ordinary=new_result['paired_ordinary']
  source_signed_gate,source_signed_price=G.exact_price(vendor,archive,before,baseline_invoice,{'gate':previous['gate']})
  source_work=temp/'producer54-source-working';shutil.copytree(parts[7113]/'replay',source_work)
  source_folder=source_work/'supplier7112/short-caller'
  source_word_bytes=(FROZEN/'7623-WORD.json.gz').read_bytes()
  (source_folder.parent/'WORD.json.gz').write_bytes(source_word_bytes)
  source_result=normal(dict(status='DERIVED_FRESH_SOURCE_RESOURCE_ONLY',word_canonical_sha256="""+repr(BASELINE)+""",
      native=new_result['source_native'],invoice=new_result['source_invoice'],
      precision=paired['source_7623'],gate=paired['source_gate'],price=paired['source_price'],
      ordinary=paired_ordinary['source_7623'],candidate_native_result_sha256=sha256(NATIVE.read_bytes()).hexdigest(),
      scope='Derived from fresh candidate-bound native paired source calculations; not a standalone source native pass.'))
  (source_folder.parent/'RESULT.json').write_text(json.dumps(source_result,sort_keys=True,indent=2)+'\\n')
  source_cohort=normal(dict(target=baseline_invoice['T'],paid=baseline_invoice['P'],bracket=source_signed_gate['raw_bracket']))
  source_current=normal(dict(before=before,after=baseline_invoice,gate=source_signed_gate,price=source_signed_price,
      source_native_result_sha256=sha256((source_folder.parent/'RESULT.json').read_bytes()).hexdigest()))
  (source_folder/'COHORT-PRICE.json').write_text(json.dumps(source_cohort,sort_keys=True,indent=2)+'\\n')
  (source_folder/'CURRENT-PRICE.json').write_text(json.dumps(source_current,sort_keys=True,indent=2)+'\\n')
  source_changes=adapter.adapt(source_folder,source_signed_price['claim_decimal'],int(paired['source_7623']['word']['dyadic_height']))
  source_logs=[]
  for name in commands:
   tick=time.time();log_path=HERE/('SOURCE-'+name+'.log')
   with log_path.open('x') as stream:
    subprocess.run([sys.executable,'-B',str(source_folder/name)],cwd=source_folder,stdout=stream,stderr=subprocess.STDOUT,check=True)
   source_logs.append(dict(check=name,seconds=time.time()-tick,sha256=sha256(log_path.read_bytes()).hexdigest()))
  source_names=('ODD-TYPE-B-REPLAY.json','ODD-TYPE-AB-REPLAY.json','ODD-CALLER-EXACT-GRID.json','ODD-PHYSICAL-BINDING.json',
      'ODD-PRECISION.json','ODD-ADMISSION-PARTIAL.json','ODD-FIXED-TAPE-COUNTS.json')
  source_checks={name:read(source_folder/name) for name in source_names}
  source_partial=source_checks['ODD-ADMISSION-PARTIAL.json']
  assert source_partial['invoice']==source_current['after'] and source_partial['compiler_outer']==source_current['gate'], 'Fresh source 17-call invoice and gate'
  assert source_partial['ordinary']['conservative_total']==matched_base, 'Fresh source matched ordinary bill'
  assert (source_folder/'ODD-TYPE-AB-CALLER.json').read_bytes()==(parts[7113]/'expected/ODD-TYPE-AB-CALLER.json').read_bytes(), 'Fresh source caller pin'
  candidate_precision=read(folder/'ODD-PRECISION.json');candidate_tape=read(folder/'ODD-FIXED-TAPE-COUNTS.json')
  precision_keys=('context_height','context_mass_bits','context_c','native_grid','rounded_native','rounded_caller')
  tape_keys=('H','context_c','context_bound_bits','native_invocations','owned_banks_per_raw_occurrence',
      'scalar_macro_inputs','scalar_services_upper','monomial_map_slots','elementary_records_upper','max_scalar_numerator_bits','common_grid')
  paired_resources=dict(precision={key:{'source':source_checks['ODD-PRECISION.json'][key],
      'candidate':candidate_precision[key]} for key in precision_keys},
      tape={key:{'source':source_checks['ODD-FIXED-TAPE-COUNTS.json'][key],
      'candidate':candidate_tape[key]} for key in tape_keys})
  # A ceiling is not a precision proof: absent a charged common context,
  # stop if either independently recomputed signed context differs.
  for key in ('context_height','context_mass_bits','context_c'):
   assert source_checks['ODD-PRECISION.json'][key]==candidate_precision[key], 'Common charged precision required: '+key
  assert Q(candidate_precision['context_c'])<=4096, 'Precision exceeds stated common U domain'
  source_resource=normal(dict(status='DERIVED_FRESH_SOURCE_RESOURCE_ONLY',native_word_sha256="""+repr(BASELINE)+""",
      candidate_native_receipt_sha256=sha256(NATIVE.read_bytes()).hexdigest(),
      source_native_derived_sha256=sha256((source_folder.parent/'RESULT.json').read_bytes()).hexdigest(),
      source_word_gzip_sha256=sha256(source_word_bytes).hexdigest(),
      caller_sha256=sha256((source_folder/'ODD-TYPE-AB-CALLER.json').read_bytes()).hexdigest(),
      source_current_price_sha256=sha256((source_folder/'CURRENT-PRICE.json').read_bytes()).hexdigest(),
      source_cohort_price_sha256=sha256((source_folder/'COHORT-PRICE.json').read_bytes()).hexdigest(),
      source_17_gate_sha256=sha256(canonical(normal(source_signed_gate))).hexdigest(),
      source_18_gate_sha256=sha256(canonical(normal(paired['source_gate']))).hexdigest(),
      check_sha256={name:sha256((source_folder/name).read_bytes()).hexdigest() for name in source_names},
      derived_result=source_result,source_17_gate=source_signed_gate,source_17_price=source_signed_price,
      source_18_gate=paired['source_gate'],source_18_price=paired['source_price'],adapter=source_changes,
      checks=source_checks,logs=source_logs,paired_resource_comparison=paired_resources,source_catalogue_rerun=False,
      common_U_tariff='unknown; separate qualification required'))
  (HERE/'SOURCE-RESOURCE.json').write_text(json.dumps(source_resource,sort_keys=True,indent=2)+'\\n')"""
    patch('fresh source seven-check resource branch',old,new)
    patch('result ordinary comparison',"adapter=changes,catalogue=catalogue,checks=", "adapter=changes,matched_ordinary=matched_ordinary,catalogue=catalogue,checks=")
    patch('result source resource',"adapter=changes,matched_ordinary=matched_ordinary,catalogue=catalogue,checks=", "adapter=changes,matched_ordinary=matched_ordinary,source_resource=source_resource,catalogue=catalogue,checks=")
    patch('signed success marker','PASS_W3_ADAPTED_COMPLETE_SIGNED_APPLICATION','PASS_CONTACT7623_COMPLETE_SIGNED_APPLICATION')
    compile(text,str(runner),'exec')
    helper.write_bytes(helper_adapted)
    runner.write_text(text)
    return {'schema':'compose7623-signed-adapter/v1','runner':str(runner),'original_sha256':sha256(raw).hexdigest(),
            'line_endings':{'original_crlf_count':crlf,'normalized_lf_count':normalized.count(b'\n'),
                            'normalized_sha256':sha256(normalized).hexdigest()},
            'adapted_sha256':sha256(text.encode()).hexdigest(),'candidate_canonical_sha256':CANDIDATE,
            'helper_path':str(helper),'helper_original_sha256':sha256(helper_raw).hexdigest(),
            'helper_adapted_sha256':helper_adapted_sha,
            'helper_patch':{'label':'lifetime_167_to_180','occurrences':1,'old':helper_old.decode(),'new':helper_new.decode()},
            'baseline_canonical_sha256':BASELINE,'baseline_invoice_sha256':INVOICE_SHA,
            'first_gate_price_path':str(path),'first_gate_price_sha256':sha256(path.read_bytes()).hexdigest(),
            'edits':changes,'scope':'counted runner adaptation only; native launcher and receipt binding and complete signed qualification remain required'}
