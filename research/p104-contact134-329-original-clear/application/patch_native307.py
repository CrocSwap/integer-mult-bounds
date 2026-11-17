#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Patch only the native application and chart proof after the R304 adapter."""

import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path

NEW_SHA = "dcd797e45b6d4b74411a8a73a9b6e8247bb2ea8744924332b0dd43db3e219f02"
OLD_SHA = "aa83ede3e5833d43606d711068619db0dc28cbcd858dd11e8e89da6d09883916"
BASE_NATIVE = "49372e31656269fcf0d62db2d02739f9163dc5b2406f406cc701a873afb5b220"
CONTACT = "512dbbc3c5133b07400b720f55753e976aca48020e91b2d0086345802de1bc14"

OLD_REBUILD = "        need(new==dict(baseline,program=[event for _,event in candidate_tagged]),'Exact main-46 transplant with unchanged metadata')"
NEW_REBUILD = f'''        incumbent_tagged=candidate_tagged
        incumbent_path=ROOT/'frozen-composition/7642-WORD.json.gz'
        incumbent=read(incumbent_path)
        need(incumbent==dict(baseline,program=[event for _,event in incumbent_tagged]),'Exact preserved main-46 transplant')
        need(sha256(canonical(incumbent)).hexdigest()=='{OLD_SHA}','Exact #7642 canonical word')
        contact_path=ROOT/'frozen-composition/7612-CONTACT.json'
        need(sha256(contact_path.read_bytes()).hexdigest()=='{CONTACT}','Exact #7612 port receipt')
        plan=read(contact_path)
        need(plan['incumbent_word_sha256']=='{OLD_SHA}' and plan['peer_head']=='e814828ee5b869c9468282d57ba28c364b07d130','Exact signed contact sources')
        original={{int(clock):event for clock,event in plan['old_events'].items()}}
        edits={{int(clock):event for clock,event in plan['proposed_events'].items()}}
        need(original=={{41049:['MOVE',134,3,618,False],41050:['MOVE',329,373,618,False],
                         41051:['ADD',134,329,'-1/2',618],41142:['MOVE',329,618,733,False],
                         42086:['MOVE',134,618,913,False]}},'Exact five original contact events')
        need(edits=={{41049:['MOVE',134,3,373,False],41050:None,
                      41051:['ADD',134,329,'-1/2',373],41142:['MOVE',329,373,733,False],
                      42086:['MOVE',134,373,913,False]}},'Exact one-ADD rechart and paid return changes')
        need(all(incumbent_tagged[i][1]==event for i,event in original.items()),'Literal #7642 clock and operand matches')
        roles=lambda event: set(event[1:3] if event[0] in ('ADD','COPY') else event[1:2])
        tape=incumbent['program']
        need([i for i in range(41049,42087) if 134 in roles(tape[i])]==[41049,41051,42086]
             and [i for i in range(41050,41143) if 329 in roles(tape[i])]==[41050,41051,41142],'No intervening observations of either recharted role')
        candidate_tagged=[(tag,edits.get(clock,event)) for clock,(tag,event) in enumerate(incumbent_tagged)
                          if edits.get(clock,event) is not None]
        need(new==dict(incumbent,program=[event for _,event in candidate_tagged]),'Exact literal contact word with unchanged metadata')'''

OLD_INVENTORY = """        need(all(N[k]==baselineN[k] for k in fixed),'Fixed exact #7605 ownership and target contract')
        need(delta(N['paid'],baselineN['paid'])=={1:-2,2:1},'Exact main-46 native saving')"""
NEW_INVENTORY = f"""        incumbent_native_path=ROOT/'frozen-composition/7642-NATIVE.json'
        need(sha256(incumbent_native_path.read_bytes()).hexdigest()=='{BASE_NATIVE}','Exact #7642 native receipt')
        incumbent_receipt=read(incumbent_native_path)
        need(normalized(incumbentN)==incumbent_receipt['native'] and incumbent_receipt['word_canonical_sha256']=='{OLD_SHA}','Freshly reconstructed #7642 native inventory')
        need(all(incumbentN[k]==baselineN[k] and N[k]==incumbentN[k] for k in fixed),'Exact preserved ownership and target contracts')
        need(delta(incumbentN['paid'],baselineN['paid'])=={{1:-2,2:1}},'Inherited main-46 native saving')
        need(delta(N['paid'],incumbentN['paid'])=={{1:-2,2:2,3:-1,4:-1,5:1}},'Exact contact native saving')"""

OLD_FORWARD = """        need(forward==baseline_forward,'Exact #7605 endpoints, versions, all CLEAR rows, COPY rows and owned events')
        need(len(forward[0])==1569 and len(forward[2])==74,'All rows and CLEARs checked')
        need(delta(grid['opcodes'],baseline_grid['opcodes'])=={'ADD':11,'MOVE':-1},'Full native scalar and MOVE counts')"""
NEW_FORWARD = """        incumbent_forward,incumbent_grid=audit.replay(incumbent,incumbent_tagged,set())
        need(forward==incumbent_forward==baseline_forward,'Exact #7642 and #7605 endpoints, versions, all CLEAR rows, COPY rows and owned events')
        need(len(forward[0])==1569 and len(forward[2])==74,'All rows and CLEARs checked')
        need(delta(incumbent_grid['opcodes'],baseline_grid['opcodes'])=={'ADD':11,'MOVE':-1},'Inherited main-46 complete opcode counts')
        need(delta(grid['opcodes'],incumbent_grid['opcodes'])=={'MOVE':-1},'Exact contact opcode counts and unchanged scalar counts')"""

OLD_PHASE = """    need({(3,618),(716,807),(327,907),(618,913),(729,808),(3,603),(914,245),(245,127),(914,127)}<=affected,'All inherited and main-46 changed-route pairs')
    main46_maps={}
    main46_ranks={(914,245):1,(245,127):1,(914,127):2}"""
NEW_PHASE = """    contact_ranks={(3,373):2,(3,618):3,(373,618):1,(373,733):2,(373,913):5,(618,733):1,(618,913):4}
    contact_maps={}
    incumbent_chart_path=ROOT/'frozen-composition/7642-WORD.json.gz'
    incumbent_chart_word=read(incumbent_chart_path)
    need(sha256(canonical(incumbent_chart_word)).hexdigest()=='aa83ede3e5833d43606d711068619db0dc28cbcd858dd11e8e89da6d09883916','Exact #7642 phase comparator')
    for role in (134,329):
        old_role_pairs=[tuple(e[2:4]) for e in incumbent_chart_word['program'] if e[0]=='MOVE' and e[1]==role]
        affected |= set(old_role_pairs+new_routes[role])
    need(set(contact_ranks)<=affected,'Every old and new contact chart pair')
    need({(3,618),(716,807),(327,907),(618,913),(729,808),(3,603),(914,245),(245,127),(914,127)}<=affected,'All inherited and main-46 changed-route pairs')
    main46_maps={}
    main46_ranks={(914,245):1,(245,127):1,(914,127):2}"""
OLD_RANKS = """        bad=deepcopy(recipe);bad['left']['phase']=(bad['left']['phase']+1)%4"""
NEW_RANKS = """        if (a,b) in contact_ranks:
            need(recipe['rank']==contact_ranks[a,b],'Exact contact rank')
            contact_maps[a,b]=actual
        bad=deepcopy(recipe);bad['left']['phase']=(bad['left']['phase']+1)%4"""
OLD_PHASE_END = """    return {'all_affected_pairs':report,'changed_public_fields':changed,'wrong_phase_rejected':True,
            'main46_composed_columns':512,'main46_composed_adjoint_columns':512}"""
NEW_PHASE_END = """    contact_compositions={}
    for label,left,right in (
        ('134_retained',contact_maps[3,618]+contact_maps[618,913],contact_maps[3,373]+contact_maps[373,913]),
        ('329_contribution_to_134',contact_maps[373,618]+contact_maps[618,913],contact_maps[373,913]),
        ('329_retained',contact_maps[373,618]+contact_maps[618,733],contact_maps[373,733]),
    ):
        for x,y in ((left,right),(interpreter.adjoint(left),interpreter.adjoint(right))):
            interpreter.equal(x,y,label+' exact signed Pauli action and phase')
            for column in range(512):
                need(interpreter.state(x,column)==interpreter.state(y,column),label+' exact Gaussian column')
        contact_compositions[label]={'columns':512,'adjoint_columns':512,'absolute_phase_verified':True}
    return {'all_affected_pairs':report,'changed_public_fields':changed,'wrong_phase_rejected':True,
            'main46_composed_columns':512,'main46_composed_adjoint_columns':512,
            'contact_compositions':contact_compositions}"""

OLD_CONTROL = """        controls['missing_main46_coframe_correction']=rejects(replay_missing_correction)
        bad=deepcopy(new);i=bad['program'].index(['MOVE',485,3,724,False]);bad['program'][i][2]=721"""
NEW_CONTROL = """        controls['missing_main46_coframe_correction']=rejects(replay_missing_correction)
        return_move=['MOVE',329,373,733,False]
        need(new['program'][41141]==return_move and new['program'].count(return_move)==1,'Unique literal role329 return')
        bad=deepcopy(new);bad['program'].remove(return_move)
        controls['missing_contact_paid_return']=rejects(lambda:I.native(bad))
        contact_index=41050
        need(new['program'][contact_index]==['ADD',134,329,'-1/2',373],'Literal recharted signed ADD')
        bad=deepcopy(new);bad['program'][contact_index][-1]=618
        controls['wrong_contact_chart']=rejects(lambda:I.native(bad))
        bad=deepcopy(new);del bad['program'][contact_index]
        bad_contact=candidate_tagged[:contact_index]+candidate_tagged[contact_index+1:]
        def replay_missing_contact():
            bad_forward,_=audit.replay(bad,bad_contact,set())
            need(bad_forward==incumbent_forward,'Omitted contact changes exact output or retirement')
        controls['missing_contact_add']=rejects(replay_missing_contact)
        bad=deepcopy(new);i=bad['program'].index(['MOVE',485,3,724,False]);bad['program'][i][2]=721"""

CHANGES = (
    (f"if expected != '{OLD_SHA}'", f"if expected != '{NEW_SHA}'"),
    ("raise ValueError('Exact main-46 candidate canonical hash')", "raise ValueError('Exact contact-rechart candidate canonical hash')"),
    (OLD_REBUILD, NEW_REBUILD),
    ("oldN,peerN,baselineN,N=map(I.native,(old,peer,baseline,new))", "oldN,peerN,baselineN,incumbentN,N=map(I.native,(old,peer,baseline,incumbent,new))"),
    (OLD_INVENTORY, NEW_INVENTORY),
    ("\"=={1:-9,2:-4,4:1,6:1,7:1}\"", "\"=={1:-11,2:-2,3:-1,5:1,6:1,7:1}\""),
    ("\"len(old['program'])+174\"", "\"len(old['program'])+173\""),
    (OLD_FORWARD, NEW_FORWARD),
    (OLD_PHASE, NEW_PHASE),
    (OLD_RANKS, NEW_RANKS),
    (OLD_PHASE_END, NEW_PHASE_END),
    ("        i=45385", "        i=45384"),
    (OLD_CONTROL, NEW_CONTROL),
)


def patch_stage(source):
    """Return adapted application source and path-independent patch receipt."""
    start = source.index("CHARTS = ")
    stop = source.index("def signed_adapter(", start)
    native = source[start:stop]
    changes = []
    for before, after in CHANGES:
        if native.count(before) != 1:
            raise ValueError(f"Expected one native patch location: {before[:96]!r}")
        native = native.replace(before, after)
        changes.append({"before": before, "after": after, "occurrences": 1})
    adapted = source[:start] + native + source[stop:]
    ast.parse(adapted)
    digest = lambda value: sha256(value.encode()).hexdigest()
    return adapted, {"scope": "CHARTS and native_adapter only",
                     "source_sha256": digest(source), "adapted_sha256": digest(adapted),
                     "candidate_sha256": NEW_SHA, "edits": changes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("application", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    adapted, receipt = patch_stage(args.application.read_text())
    with args.output.open("x") as out:
        out.write(adapted)
    with args.receipt.open("x") as out:
        json.dump(receipt, out, indent=2)
        out.write("\n")


if __name__ == "__main__":
    main()
