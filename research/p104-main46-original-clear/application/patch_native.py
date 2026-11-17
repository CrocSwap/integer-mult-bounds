#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Adapt only #7605's native verifier to the pinned main-46 transplant."""

import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path

CANDIDATE = "aa83ede3e5833d43606d711068619db0dc28cbcd858dd11e8e89da6d09883916"
BASELINE_NATIVE = "0ada1e2e7de8887e6ebbd16cda3c8b9738d71873857657ff4fa6e180653cf888"
BASELINE_GZIP = "37358c493d18ebc6be386aebb4c17529b38883674731f7009ef4e96a5313467d"
BASELINE_CANONICAL = "e20f3f9240ac3f5fa4bbd7ab9b5550d660886901bb209f335409c329ac45d9cd"
PEER_EDITS = "a49e9962e32d13fd91cd8715d888bb1f4305003e63dd25485aa413905e00b8d9"

OLD_REBUILD = "        need(new==dict(peer,program=emitted),'Exact timed helper757 word and unchanged metadata')"
NEW_REBUILD = f'''        baseline_path=ROOT/'frozen-composition/7605-WORD.json.gz'
        need(sha256(baseline_path.read_bytes()).hexdigest()=='{BASELINE_GZIP}','Exact #7605 compressed word')
        baseline=read(baseline_path)
        need(baseline==dict(peer,program=emitted),'Rebuilt exact timed helper757 baseline from #7604')
        need(sha256(canonical(baseline)).hexdigest()=='{BASELINE_CANONICAL}','Exact #7605 canonical word')
        tape=baseline['program']
        plan_path=ROOT/'frozen-composition/7610-EDITS.json'
        need(sha256(plan_path.read_bytes()).hexdigest()=='{PEER_EDITS}','Exact public #7610 edit list')
        plan=read(plan_path)
        need(len(tape)==76636==plan['base_events']+5 and not plan['append'],'Five-event shift and no appended operations')
        deletes={{clock+5:event for clock,event in plan['delete']}}
        inserts={{clock+5 if clock else 0:events for clock,events in plan['insert_before']}}
        need(sorted(deletes)==[45372,45373,45375,47958] and sorted(inserts)==[0,45377,47958],'Exact unique translated #7610 clocks')
        need(all(tape[i]==event for i,event in deletes.items()),'Exact deleted #7605 operations')
        need(tape[45376:45379]==[['MOVE',818,914,245,False],['ADD',818,1456,'1',245],['ADD',818,588,'1',245]],'Carrier and first outward reads')
        need(tape[47959]==['ADD',1019,46,'1',127],'Main 46 return before first chart-127 use')
        baseline_tagged=list(enumerate(tape))
        candidate_tagged=[]
        for i,event in baseline_tagged:
            candidate_tagged.extend((-(16*i+j+1),added) for j,added in enumerate(inserts.get(i,[])))
            if i not in deletes:
                candidate_tagged.append((i,event))
        need(new==dict(baseline,program=[event for _,event in candidate_tagged]),'Exact main-46 transplant with unchanged metadata')'''

OLD_INVENTORY = """        oldN,peerN,N=map(I.native,(old,peer,new))
        need(all(N[k]==peerN[k]for k in('public','helpers','rises','owned_peak','lifetimes','bad_inputs')),'Fixed complete #7604 ownership and target contract')
        need(delta(N['paid'],peerN['paid'])=={1:-2,2:1},'Exact additional helper757 native saving')"""
NEW_INVENTORY = f"""        oldN,peerN,baselineN,N=map(I.native,(old,peer,baseline,new))
        baseline_native_path=ROOT/'frozen-composition/7605-NATIVE.json'
        need(sha256(baseline_native_path.read_bytes()).hexdigest()=='{BASELINE_NATIVE}','Exact #7605 native receipt')
        baseline_receipt=read(baseline_native_path)
        need(normalized(baselineN)==baseline_receipt['native'] and baseline_receipt['word_canonical_sha256']=='{BASELINE_CANONICAL}','Independently reconstructed #7605 native inventory')
        fixed=('public','helpers','rises','owned_peak','lifetimes','bad_inputs')
        need(all(baselineN[k]==peerN[k] for k in fixed),'Fixed complete #7604 ownership and target contract')
        need(delta(baselineN['paid'],peerN['paid'])=={{1:-2,2:1}},'Exact inherited helper757 native saving')
        need(all(N[k]==baselineN[k] for k in fixed),'Fixed exact #7605 ownership and target contract')
        need(delta(N['paid'],baselineN['paid'])=={{1:-2,2:1}},'Exact main-46 native saving')"""

CHART_SET_OLD = """    need({(3,618),(716,807),(327,907),(618,913),(729,808),(3,603)}<=affected,'Every token-settled, two-contraction, helper315 and helper757 direct pair')
    report=[]"""
CHART_SET_NEW = """    need({(3,618),(716,807),(327,907),(618,913),(729,808),(3,603),(914,245),(245,127),(914,127)}<=affected,'All inherited and main-46 changed-route pairs')
    main46_maps={}
    main46_ranks={(914,245):1,(245,127):1,(914,127):2}
    report=[]"""

CHART_CONTROL_OLD = """        bad=deepcopy(recipe);bad['left']['phase']=(bad['left']['phase']+1)%4"""
CHART_CONTROL_NEW = """        if (a,b) in main46_ranks:
            need(recipe['rank']==main46_ranks[a,b],'Exact main-46 pair rank')
            main46_maps[a,b]=actual
        bad=deepcopy(recipe);bad['left']['phase']=(bad['left']['phase']+1)%4"""

CHART_RETURN_OLD = """    return {'all_affected_pairs':report,'changed_public_fields':changed,'wrong_phase_rejected':True}"""
CHART_RETURN_NEW = """    via=main46_maps[914,245]+main46_maps[245,127]
    direct=main46_maps[914,127]
    for x,y in ((via,direct),(interpreter.adjoint(via),interpreter.adjoint(direct))):
        interpreter.equal(x,y,'Exact main-46 composed signed action and absolute phase')
        for column in range(512):
            need(interpreter.state(x,column)==interpreter.state(y,column),'Exact main-46 composed Gaussian column')
    return {'all_affected_pairs':report,'changed_public_fields':changed,'wrong_phase_rejected':True,
            'main46_composed_columns':512,'main46_composed_adjoint_columns':512}"""

FORWARD_OLD = """        ("        bad=deepcopy(new);i=bad['program'].index(['MOVE',485,3,724,False]);bad['program'][i][2]=721", """
FORWARD_NEW = '''        ("        forward,grid=audit.replay(new,list(enumerate(new['program'])),set())", """        baseline_forward,baseline_grid=audit.replay(baseline,baseline_tagged,set())
        forward,grid=audit.replay(new,candidate_tagged,set())
        need(forward==baseline_forward,'Exact #7605 endpoints, versions, all CLEAR rows, COPY rows and owned events')
        need(len(forward[0])==1569 and len(forward[2])==74,'All rows and CLEARs checked')
        need(delta(grid['opcodes'],baseline_grid['opcodes'])=={'ADD':11,'MOVE':-1},'Full native scalar and MOVE counts')"""),
        ("        bad=deepcopy(new);i=bad['program'].index(['MOVE',485,3,724,False]);bad['program'][i][2]=721", '''

FAULT_OLD = """        controls['missing_helper757_paid_move']=rejects(lambda:I.native(bad))
        bad=deepcopy(new);i=bad['program'].index(['MOVE',485,3,724,False]);bad['program'][i][2]=721"""
FAULT_NEW = """        controls['missing_helper757_paid_move']=rejects(lambda:I.native(bad))
        direct=['MOVE',46,914,127,False]
        need(new['program'].count(direct)==1,'Unique literal main-46 direct MOVE')
        bad=deepcopy(new);bad['program'].remove(direct)
        controls['missing_main46_paid_move']=rejects(lambda:I.native(bad))
        bad=deepcopy(new);bad['program'][bad['program'].index(direct)][2]=245
        controls['wrong_main46_move_source']=rejects(lambda:I.native(bad))
        correction=['ADD',588,818,'1',245]
        i=45385
        need(new['program'][i:i+3]==[correction,['ADD',1456,818,'-1',245],['ADD',818,1456,'1',245]],'Exact coframe correction before first outward read')
        bad=deepcopy(new);del bad['program'][i]
        bad_tagged=candidate_tagged[:i]+candidate_tagged[i+1:]
        def replay_missing_correction():
            bad_forward,_=audit.replay(bad,bad_tagged,set())
            need(bad_forward==baseline_forward,'Removed correction changes the exact old rows')
        controls['missing_main46_coframe_correction']=rejects(replay_missing_correction)
        bad=deepcopy(new);i=bad['program'].index(['MOVE',485,3,724,False]);bad['program'][i][2]=721"""

CHANGES = (
    (CHART_SET_OLD, CHART_SET_NEW),
    (CHART_CONTROL_OLD, CHART_CONTROL_NEW),
    (CHART_RETURN_OLD, CHART_RETURN_NEW),
    ("    expected = digest(canonical(word))\n    patches = [\n        (\"EXPECTED=", f"    expected = digest(canonical(word))\n    if expected != '{CANDIDATE}':\n        raise ValueError('Exact main-46 candidate canonical hash')\n    patches = [\n        (\"EXPECTED="),
    (OLD_REBUILD, NEW_REBUILD),
    (OLD_INVENTORY, NEW_INVENTORY),
    ("\"=={1:-7,2:-5,4:1,6:1,7:1}\"", "\"=={1:-9,2:-4,4:1,6:1,7:1}\""),
    ("\"len(old['program'])+164\"", "\"len(old['program'])+174\""),
    (FORWARD_OLD, FORWARD_NEW),
    (FAULT_OLD, FAULT_NEW),
)


def patch_native_application(source):
    """Return the adapted source and exact patch receipt."""
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
    hash_text = lambda text: sha256(text.encode()).hexdigest()
    return adapted, {"scope": "CHARTS and native_adapter only",
                     "source_sha256": hash_text(source), "adapted_sha256": hash_text(adapted),
                     "candidate_sha256": CANDIDATE, "edits": changes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("application", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    source = args.application.read_text()
    adapted, receipt = patch_native_application(source)
    with args.output.open("x") as out:
        out.write(adapted)
    with args.receipt.open("x") as out:
        json.dump(receipt, out, indent=2)
        out.write("\n")


if __name__ == "__main__":
    main()
