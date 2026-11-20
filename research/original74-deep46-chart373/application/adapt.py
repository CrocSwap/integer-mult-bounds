# SPDX-License-Identifier: Apache-2.0
"""Counted adapters for the original-74 #7657 application and retained #7643 contact test."""
BASE = "450c7e544efb5258c4b8b4858b49cbd7482d14f206cdda1a71833fc73343ac66"
OLD_CLAIM = "0.0036524238117"
CLAIM = "0.0036527403111"
FEE = {1:-2, 2:2, 3:-1, 4:-1, 5:1}
NATIVE = 'PASS_CONTACT_ON_7657_NATIVE'
SIGNED = 'PASS_CONTACT_ON_7657_SIGNED'
COMPLETE = 'PASS_CONTACT_ON_7657_FINAL'


def replace(text, edits, ledger):
    for old,new in edits:
        assert text.count(old)==1, ('Expected exactly one source anchor',old)
        text=text.replace(old,new)
        ledger.append(dict(before=old,after=new,occurrences=1))
    compile(text,'<adapted application>', 'exec')
    return text


def native(text,word_sha,contact_source,ledger):
    # Import the exact prior signed Gaussian compositions from #7643 by two unique anchors.
    composition=contact_source[contact_source.index('    contact_compositions={}'):contact_source.index("    return {'all_affected_pairs':report")]
    capture=contact_source[contact_source.index('        if (a,b) in contact_ranks:'):contact_source.index('        bad=deepcopy(recipe)')]
    return replace(text,[
        (f"EXPECTED='{BASE}'",f"EXPECTED='{word_sha}'"),
        ("PATCHES=[]","contact=load('contact_word_7657', ROOT/'contact_word.py')\nPATCHES=[]"),
        ("    affected={pair for i in changed for pair in old_routes[i]+new_routes[i]}", """    affected={pair for i in changed for pair in old_routes[i]+new_routes[i]}
    prior=read(ROOT/'frozen-composition/7657-WORD.json.gz')
    prior_routes=routes(prior)
    direct_changed=[role for role in prior_routes if prior_routes[role]!=new_routes[role]]
    need(direct_changed==[134,329],'Exactly the two immediate predecessor itineraries changed')
    affected |= {pair for role in direct_changed for pair in prior_routes[role]+new_routes[role]}"""),
        ("    triples,_=support.chart_contract(base,word)", """
    triples,_=support.chart_contract(base,prior)
    contact_ranks={(3,373):2,(3,618):3,(373,618):1,(373,733):2,(373,913):5,(618,733):1,(618,913):4}
    need(set(contact_ranks)<=affected,'Every old and new contact pair derived from literal routes')
    contact_maps={}"""),
        ("        bad=deepcopy(recipe)",capture+"        bad=deepcopy(recipe)"),
        ("    return {'composed_1062':composed",composition+"    return {'contact_compositions':contact_compositions,'composed_1062':composed"),
        ("        need(new==dict(baseline,program=[e for _,e in tagged]),'Exact frozen edit on original #7605')", f"""        prior=read(ROOT/'frozen-composition/7657-WORD.json.gz')
        need(prior==dict(baseline,program=[e for _,e in tagged]),'Rebuilt exact #7657 joint from #7605 and #7611')
        need(sha256(canonical(prior)).hexdigest()=='{BASE}','Authenticated #7657 canonical word')
        local=contact.splice(prior,read(ROOT/'frozen-composition/CONTACT.json'))
        need(new==dict(prior,program=[e for _,e in local]),'Exactly the five translated #7643 events on #7657')
        tagged=[(tagged[i][0],e) for i,e in local]"""),
        ("support.chart_contract(baseline,new)","support.chart_contract(baseline,prior)"),
        ("        need(delta(N['paid'],baselineN['paid'])==expected_delta,'Measured paid difference from #7605')",
         f"""        priorN=I.native(prior)
        need(normalized(priorN)==read(ROOT/'frozen-composition/7657-NATIVE.json')['native'],'Fresh full #7657 native inventory')
        need(delta(priorN['paid'],baselineN['paid'])==expected_delta,'Measured #7657 paid difference from #7605')
        need(all(N[k]==priorN[k] for k in ('public','helpers','rises','owned_peak','lifetimes','bad_inputs')) and delta(N['paid'],priorN['paid'])=={FEE!r},'Fixed #7657 contract and actual contact fee')"""),
        ("len(new['program'])==76673","len(prior['program'])==76673 and len(new['program'])==76672"),
        ("        forward_receipt=forward_endpoint(new,forward[0])","""        courier_versions=contact.courier_versions(prior,new,local,audit)
        fresh,second_grid,prior_forward,prior_owned=support.inspect_owned_contacts(prior,new,local,audit)
        need(fresh[0]==forward[0] and second_grid==grid,'Same exact candidate under both sets of clock tags')
        forward_receipt=forward_endpoint(new,forward[0])"""),
        ("        controls=support.negatives(new,tagged,base_forward,protected,audit,I.native,rejects,triples)",
         """        controls=support.negatives(new,tagged,base_forward,protected,audit,I.native,rejects,triples)
        controls.update(contact.faults(new,local,prior_forward,prior_owned,audit,I.native,rejects))"""),
        ("native=N,original_7605_operand_clocks", "native=N,courier_operand_versions=courier_versions,original_7657_operand_clocks=len(prior_owned),original_7657_clear_rows=len(prior_forward[2]),original_7605_operand_clocks"),
        ("PASS_CHART1062_COMPLETE_NATIVE",NATIVE),
    ],ledger)


def signed(text,word_sha,old_fee,ledger):
    import ast
    anchor,=[line for line in text.splitlines() if line.startswith("  assert diff(after['P'],binvoice['P'])==")]
    assert ast.literal_eval(anchor.split('==',1)[1])==old_fee
    return replace(text,[
        (BASE,word_sha),("PASS_CHART1062_COMPLETE_NATIVE",NATIVE),("PASS_CHART1062_COMPLETE_SIGNED_APPLICATION",SIGNED),
        (anchor,
         f"""  w45=read(FROZEN/'7657-WORD.json.gz')
  assert sha256(canonical(w45)).hexdigest()=='{BASE}'
  n45=ind.native(w45)
  assert normal(n45)==read(FROZEN/'7657-NATIVE.json')['native'] and not n45['bad_inputs']
  bill45=ind.invoices(w45,C,n45)
  assert normal(bill45)==read(FROZEN/'7657-SIGNED.json')['price']['after']
  assert diff(bill45['P'],binvoice['P'])=={old_fee!r}
  assert diff(after['P'],bill45['P'])=={repr({r:17*n for r,n in FEE.items()})}
  assert bill45['T']==after['T'] and bill45['S']==1424 and not bill45['empty_root_credits']"""),
        ("sum(after['P'].values())==110281","sum(bill45['P'].values())==110281 and sum(after['P'].values())==110264"),
        ("public_claim=Q('"+OLD_CLAIM+"')","public_claim=Q('"+CLAIM+"')"),
        ("  public_gate=directed.gate(", """  for label in ('7645','7657'):
   peer_final=read(FROZEN/(label+'-FINAL.json'))
   peer_signed=read(FROZEN/(label+'-SIGNED.json'))
   assert peer_final['candidate_canonical_sha256']==peer_signed['price']['new_native'] and peer_signed['caller_sha256']==sha256((parts[7113]/'expected/ODD-TYPE-AB-CALLER.json').read_bytes()).hexdigest()
   assert peer_final['assumptions']==['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery'] and peer_signed['assumptions']==peer_final['assumptions']
   peer_bill=peer_signed['price']['after']
   account={k:({int(r):v for r,v in value.items()} if k in ('P','T') else value) for k,value in peer_bill.items()}
   assert account['T']==after['T'] and account['S']==1424 and not account['empty_root_credits']
   assert Q(peer_final['raw_crossing'][1])<public_claim and directed.moment(G.signed(account),public_claim)[1]<0
  public_gate=directed.gate("""),
    ],ledger)


def final(text,ledger):
    return replace(text,[
        ("== 110281","== 110264"),("paid_calls=110281","paid_calls=110264"),
        ("Q('"+OLD_CLAIM+"')", "Q('"+CLAIM+"')") if text.count("Q('"+OLD_CLAIM+"')")==1 else
        ("assert Q(price['public_claim_gate']['claim']) == Q('"+OLD_CLAIM+"')","assert Q(price['public_claim_gate']['claim']) == Q('"+CLAIM+"')"),
        ("assert Q(price['public_claim_gate']['tested']) == Q('"+OLD_CLAIM+"')","assert Q(price['public_claim_gate']['tested']) == Q('"+CLAIM+"')"),
        ("return dict(status='PASS_CHART1062_FINAL_APPLICATION', claim='"+OLD_CLAIM+"',",f"""immediate=read(root/'frozen-composition/7657-FINAL.json')
    nearest=read(root/'frozen-composition/7645-FINAL.json')
    assert native['original_7657_clear_rows']==74 and native['original_7657_operand_clocks']==435
    assert all(native['controls'][name] for name in ('missing_contact_add','wrong_contact_chart','missing_contact_return','wrong_contact_sign'))
    assert native['courier_operand_versions']>0 and len(native['charts']['composed_1062'])==5
    assert len(native['charts']['contact_compositions'])==3
    assert all(item['columns']==item['adjoint_columns']==512 and item['absolute_phase_verified'] for item in native['charts']['contact_compositions'].values())
    assert ordinary==read(root/'DERIVATION.json')['ordinary']
    return dict(status='{COMPLETE}', claim='{CLAIM}', predecessor_7657=immediate['candidate_canonical_sha256'],
                original_7657_raw=immediate['raw_crossing'],peer_7645_raw=nearest['raw_crossing'],
                ordinary_change_over_7657=ordinary-immediate['ordinary_bound'],
                tape_change_over_7657={{k:tape[k]-immediate['tape'][k] for k in fields}},
                complete_paid_delta_over_7657={repr({r:17*n for r,n in FEE.items()})},"""),
        ("complete_paid_delta=", "prior_7657_complete_paid_delta_over_7605="),
    ],ledger)
