# SPDX-License-Identifier: Apache-2.0
"""Extend the frozen #7643 native, signed, and final checkers to the two #7644 routes."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTACT = "dcd797e45b6d4b74411a8a73a9b6e8247bb2ea8744924332b0dd43db3e219f02"
MAIN46 = "aa83ede3e5833d43606d711068619db0dc28cbcd858dd11e8e89da6d09883916"
NATIVE = "PASS_COMBINED_COMPLETE_NATIVE"
SIGNED = "PASS_COMBINED_COMPLETE_SIGNED_APPLICATION"


def patches(text, pairs):
    for original, replacement in pairs:
        if text.count(original) != 1:
            raise ValueError(f"Expected exactly one occurrence of {original!r}")
        text = text.replace(original, replacement)
    compile(text, "<exactly adapted source>", "exec")
    return text


def native(candidate_sha):
    source = (HERE / "source/7643-native.py").read_text()
    return patches(source, [
        (f"EXPECTED='{CONTACT}'", f"EXPECTED='{candidate_sha}'"),
        ("PATCHES=[]", "support=load('chart1062_support', ROOT/'word_checks.py')\nPATCHES=[]"),
        ("routes=lambda w:{i:[tuple(e[2:4])for e in w['program']if e[0]=='MOVE'and e[1]==i]for i in range(w['public'])}",
         "routes=lambda w:dict(enumerate(support.routes(w)))"),
        ("    report=[]", """    contact=read(ROOT/'frozen-composition/7643-WORD.json.gz')
    triples,fee=support.chart_contract(contact,word)
    need(set(triples)=={(740,1062,1071),(401,1062,922)} and fee=={1:-1,2:-2,5:1},'Exactly both #7644 bypasses')
    affected |= {pair for a,b,c in triples for pair in ((a,b),(b,c),(a,c))}
    maps={}
    report=[]"""),
        ("        actual=interpreter.recipe(recipe)", "        actual=interpreter.recipe(recipe)\n        maps[a,b]=actual"),
        ("    return {'all_affected_pairs':report", "    composed=support.physical(interpreter,maps,triples)\n    return {'composed_1062':composed,'all_affected_pairs':report"),
        ("        need(new==dict(incumbent,program=[event for _,event in candidate_tagged]),'Exact literal contact word with unchanged metadata')",
         f"""        contact=read(ROOT/'frozen-composition/7643-WORD.json.gz')
        need(contact==dict(incumbent,program=[event for _,event in candidate_tagged]),'Rebuild #7643 contact word from #7642')
        need(sha256(canonical(contact)).hexdigest()=='{CONTACT}','Exact #7643 word')
        contact_tagged=candidate_tagged
        local_tags=support.reconstruct(contact,read(ROOT/'frozen-composition/EDITS.json'))
        need(new==dict(contact,program=[e for _,e in local_tags]),'Exact chart-1062 splice on #7643')
        candidate_tagged=[(contact_tagged[t][0] if t>=0 else -2000000+t,e) for t,e in local_tags]
        remap={{t:i for i,(t,e) in enumerate(local_tags) if t>=0}}
        triples,fee=support.chart_contract(contact,new)"""),
        ("oldN,peerN,baselineN,incumbentN,N=map(I.native,(old,peer,baseline,incumbent,new))",
         "oldN,peerN,baselineN,incumbentN,contactN,N=map(I.native,(old,peer,baseline,incumbent,contact,new))"),
        ("need(delta(N['paid'],incumbentN['paid'])=={1:-2,2:2,3:-1,4:-1,5:1},'Exact contact native saving')",
         """need(delta(contactN['paid'],incumbentN['paid'])=={1:-2,2:2,3:-1,4:-1,5:1},'Exact contact native saving')
        need(normalized(contactN)==read(ROOT/'frozen-composition/7643-NATIVE.json')['native'],'Exact prior native inventory')
        need(all(N[k]==contactN[k] for k in fixed) and delta(N['paid'],contactN['paid'])==fee,'Fixed contracts and both bypasses')"""),
        ("=={1:-11,2:-2,3:-1,5:1,6:1,7:1}", "=={1:-12,2:-4,3:-1,5:2,6:1,7:1}"),
        ("len(old['program'])+173", "len(old['program'])+188"),
        ("        incumbent_forward,incumbent_grid=audit.replay(incumbent,incumbent_tagged,set())", """        incumbent_forward,incumbent_grid=audit.replay(incumbent,incumbent_tagged,set())
        checked_forward,checked_grid,contact_forward,protected=support.inspect_owned_contacts(contact,new,local_tags,audit)
        need(checked_grid==grid and checked_forward[0]==forward[0], 'Same literal candidate under both clock maps')"""),
        ("delta(grid['opcodes'],incumbent_grid['opcodes'])=={'MOVE':-1}", "delta(grid['opcodes'],incumbent_grid['opcodes'])=={'ADD':17,'MOVE':-3}"),
        ("        controls={}", "        controls=support.negatives(new,local_tags,contact_forward,protected,audit,I.native,rejects,triples)"),
        ("        i=45384", "        i=remap[45384]"),
        ("new['program'][41141]", "new['program'][remap[41141]]"),
        ("        contact_index=41050", "        contact_index=remap[41050]"),
        ("native=N,forward=forward_receipt", "native=N,protected_clocks=len(protected),ordered_erasures=len(contact_forward[2]),forward=forward_receipt"),
        ("PASS_CONTACT134_329_COMPLETE_NATIVE", NATIVE),
    ])


def signed(candidate_sha, claim):
    source=(HERE/"source/7643-signed.py").read_text()
    return patches(source, [
        (f"sha256(canonical(new_word)).hexdigest()=='{CONTACT}'",f"sha256(canonical(new_word)).hexdigest()=='{candidate_sha}'"),
        ("FROZEN/'7642-WORD.json.gz'","FROZEN/'7643-WORD.json.gz'"),
        ("FROZEN/'7642-NATIVE.json'","FROZEN/'7643-NATIVE.json'"),
        ("FROZEN/'7642-SIGNED.json'","FROZEN/'7643-SIGNED.json'"),
        ("Pinned literal 134/329 contact word","Pinned literal combined word"),
        (MAIN46,CONTACT),
        ("0.003650666180757","0.003650982374396"),
        ("{1:-34,2:34,3:-17,4:-17,5:17}","{1:-17,2:-34,5:17}"),
        ("==110332","==110298"),
        ("Q(gate['claim'])>=Q('0.00365098237428')",f"Q(gate['claim'])>=Q('{claim}')"),
        ("public_claim=Q('0.00365098237428')",f"public_claim=Q('{claim}')"),
        ("  public_gate=directed.gate(", """  other=read(FROZEN/'7644-INVOICE.json')
  benchmark=dict(before,T={int(r):v for r,v in other['targets'].items()},P={int(r):v for r,v in other['paid'].items()})
  assert public_claim>Q(read(FROZEN/'7644-FINAL.json')['raw_crossing'][1])
  assert directed.moment(G.signed(benchmark),public_claim)[1]<0,'The full #7644 invoice rejects the candidate claim'
  public_gate=directed.gate("""),
        ("Whole reconstructed #7642 invoice","Whole reconstructed #7643 invoice"),
        ("Strictly higher than #7642 raw crossing","Strictly higher than #7643 raw crossing"),
        ("Exact #7642 invoice rejects","Exact #7643 invoice rejects"),
        ("source_head='d7f82810689ed2cd649ec9aaaf3b1485b585c82e'","source_head='694667c8c129508d78b53a6a51690d4c284d0549'"),
        ("component_head='e814828ee5b869c9468282d57ba28c364b07d130'","component_head='32cfa1d20d3e4587dc601e69ccac1cd24a239e5c'"),
        ("PASS_CONTACT134_329_COMPLETE_NATIVE",NATIVE),
        ("PASS_CONTACT134_329_COMPLETE_SIGNED_APPLICATION",SIGNED),
    ])


def final():
    source=(HERE/"source/7643-final.py").read_text()
    return patches(source,[
        ("read(HERE / 'data/7642-FINAL.json')","read(root / 'frozen-composition/7643-FINAL.json')"),
        ("read(HERE / 'data/word.json.gz')","read(root / 'frozen-composition/CANDIDATE-WORD.json.gz')"),
        ("read(HERE / 'data/invoice-new.json')","read(root / 'frozen-composition/CANDIDATE-INVOICE.json')"),
        ("== 110332 and","== 110298 and"),
        ("== 782668204 < 10**9","== read(root/'PREPARED.json')['ordinary'] < 10**9"),
        ("    assert native['charts']['wrong_phase_rejected']", """    assert native['charts']['wrong_phase_rejected']
    assert native['ordered_erasures']==74 and native['protected_clocks']>0
    assert len(native['charts']['composed_1062'])==2
    for record in native['charts']['composed_1062']:
        assert record['forward_columns']==record['adjoint_columns']==512
    assert len(native['charts']['contact_compositions'])==3
    assert all(entry['columns']==entry['adjoint_columns']==512 and entry['absolute_phase_verified'] for entry in native['charts']['contact_compositions'].values())
    assert all(native['controls'][key] for key in ('missing_contact_add','missing_contact_paid_return','wrong_contact_chart','removed_role185_compensation','missing_role_82_direct_move','missing_role_185_direct_move'))"""),
        ("PASS_CONTACT134_329_FINAL_APPLICATION","PASS_COMBINED_FINAL_APPLICATION"),
        ("paid_calls=110332","paid_calls=110298"),
        ("ordinary_change_over_7642","ordinary_change_over_7643"),
        ("tape_change_over_7642","tape_change_over_7643"),
    ])
