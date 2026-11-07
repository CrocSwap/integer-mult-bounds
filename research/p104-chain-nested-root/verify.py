"""Cold exact native/caller/physical/price replay of the chain-nested root caller.

DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
Extends the verifier of @CubeJerry (#6805, with substantial OpenAI assistance).
The native word is #6824's and is rebuilt and fully rechecked here.
All retained algorithms and previous mathematical constructions retain credit.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
import time
import context as L
import native as N
from construct import construct,base as construct_base
import lift
import pricing

HERE=Path(__file__).resolve().parent
ORDINARY_UPPER=488177792
sys.path.insert(0,str(HERE/'retained/caller'))

def payload(data):return json.dumps(data,sort_keys=True,separators=(',',':')).encode()
def progress(s):print(s,flush=True)

def chart_pairs(word):
    main=set(word['live'])|{r+112 for r in word['live']}
    return {(e[2],e[3])for e in word['program']if e[0]=='MOVE'}|{(word['initial'][r],word['final'][r])for r in range(word['public'])if r not in main}

def changed_columns(source,candidate,intermediate,edit):
    # Every chart pair named by the split (frames 749/243/127/3) or touched by an edit event
    # or lifted helper endpoint; all columns of each are replayed. Pairs new against the
    # #6805 word are required to be inside this set.
    pairs={(749,243),(243,127),(3,243)}
    for item in edit['edits']:
        pairs|={(e[2],e[3])for e in item['insert']if e[0]=='MOVE'}
    pairs|={(c['to'],candidate['final'][c['role']])for c in edit['initial']}
    N.need((chart_pairs(candidate)-chart_pairs(source))<=pairs and (chart_pairs(candidate)-chart_pairs(intermediate))<=pairs,
           'Every new native chart pair is column-checked')
    C=N.load(HERE/'retained/native/clifford_exact.py','retimed_columns_compiler')
    V=N.load(HERE/'retained/native/native_verify.py','retimed_columns_interpreter')
    columns=0
    for a,b in sorted(pairs):
        ca=C.canonical_frame(9,tuple(candidate['frames'][a]));cb=C.canonical_frame(9,tuple(candidate['frames'][b]))
        recipe,_=C.lower_child(ca.adjoint().then(cb))
        actual=V.recipe(recipe);expected=V.adjoint(V.frame(candidate['frames'][a],9))+V.frame(candidate['frames'][b],9)
        for column in range(512):
            N.need(V.state(actual,column)==V.state(expected,column),'Every changed Gaussian column and phase')
            columns+=1
        wrong=deepcopy(recipe);wrong['left']['phase']=(wrong['left']['phase']+1)%4
        N.need(V.state(V.recipe(wrong),0)!=V.state(expected,0),'Wrong absolute phase is observable')
    return {'chart_pairs':sorted(pairs),'exact_columns':columns,'phase_controls':len(pairs)}

def lift_negative_controls(intermediate,edit):
    """Each mutated edit list must be rejected by the primary applier or the all-input replay."""
    results=[]
    def reject(label,mutant):
        try:
            N.replay(lift.apply(intermediate,mutant))
        except ValueError as error:
            results.append({'mutation':label,'rejected':str(error)[:80]})
        else:
            raise ValueError('lift negative control accepted: '+label)
    inserted=[(i,j)for i,item in enumerate(edit['edits'])for j,e in enumerate(item['insert'])if e[0]=='ADD']
    for i,j in inserted:
        bad=deepcopy(edit);e=bad['edits'][i]['insert'][j]
        e[3]=str(Q(e[3])*2)
        reject('wrong coefficient at edit %d event %d'%(i,j),bad)
    bad=deepcopy(edit);bad['edits'][-1]['insert']=[]
    reject('missing final repair',bad)
    bad=deepcopy(edit)
    for item in bad['edits']:
        for e in item['insert']:
            if e[1]==665:e[1]=664
            if e[0]=='ADD'and e[2]==665:e[2]=664
    reject('aliased lifted helpers',bad)
    bad=deepcopy(edit);bad['edits'][0]['delete'][0][3]='-1/4'
    reject('stale bound source event',bad)
    bad=deepcopy(edit);bad['edits'][5]['insert']=[e for e in bad['edits'][5]['insert']if e[:2]!=['ADD',120]or e[2]!=556]
    reject('missing carrier delivery',bad)
    return results

def caller_negative_controls(word,local,native,physical,candidate,recipes,prior):
    """Every mutation of the new caller must be rejected by the named check."""
    import caller,rows,chain_root as CR,check_root
    results={}
    def reject(label,action):
        try:action()
        except ValueError as error:results[label]=str(error)[:80]
        else:raise ValueError('caller negative control accepted: '+label)
    def both(bad):
        caller.replay(bad);rows.transpose(bad)
    def first(w,op):return next(i for i,e in enumerate(w['events'])if e[0]==op)
    for op in('LOCAL','QUERY','IDLE_ONE','LAMBDA','ADD'):
        bad=deepcopy(word);del bad['events'][first(bad,op)]
        reject('deleted_'+op.lower(),lambda bad=bad:both(bad))
    bad=deepcopy(word);bad['events'][first(bad,'IDLE_ONE')][2].pop()
    reject('shrunk_merged_idle',lambda:both(bad))
    bad2=deepcopy(word);bad2['events'][first(bad2,'IDLE_ONE')][2].append(1)
    reject('grown_merged_idle',lambda:both(bad2))
    bad3=deepcopy(word);bad3['events'][first(bad3,'IDLE_ONE')][1]+=1
    reject('merged_idle_on_wrong_line',lambda:both(bad3))
    bad3b=deepcopy(word);bad3b['events'][first(bad3b,'IDLE_ONE')][1]+=1
    reject('independent_root_audit_wrong_line',lambda:check_root.family(bad3b))
    bad4=deepcopy(word);bad4['events'][first(bad4,'QUERY')][3]=1
    reject('wrong_phase_thin_query',lambda:both(bad4))
    bad5=deepcopy(word);bad5['events'][first(bad5,'LAMBDA')][2]=1
    reject('wrong_phase_lambda',lambda:both(bad5))
    bad6=deepcopy(word);bad6['diagonal'][0][0]=1
    reject('wrong_phase_output_target',lambda:both(bad6))
    bad7=deepcopy(word);e=bad7['events'][first(bad7,'LOCAL')];e[3]=e[2]
    reject('aliased_native_inputs',lambda:prior.physical(bad7,candidate,recipes))
    bad8=deepcopy(word)
    for e in bad8['events']:
        for slot,value in enumerate(e):
            if slot and e[0]in('ADD','SWAP','QUERY')and slot<3 and value==1:e[slot]=0
    def distinct_then_replay(bad):
        for e in bad['events']:
            if e[0]in('ADD','SWAP','QUERY'):N.need(e[1]!=e[2],'Distinct caller source and destination roles')
        both(bad)
    reject('aliased_caller_inputs',lambda:distinct_then_replay(bad8))
    bad9=deepcopy(word);del bad9['events'][first(bad9,'IDLE_ONE')]
    reject('unpaid_idle_in_invoice',lambda:pricing.assemble(local,native,bad9,physical))
    original=CR.thin_vectors
    def corrupt(sL,sR):
        out=original(sL,sR);x,y=out[0];x=x[:];x[0]+=1;return [(x,y)]+out[1:]
    CR.thin_vectors=corrupt
    try:reject('wrong_root_coefficient',lambda:CR.verify_root(*CR.SHAPE))
    finally:CR.thin_vectors=original
    return results

def gate_shape(local,retained):
    """The same family at (4,4,1|1,4,4): exact replay; #6726's invoice minus one cancelling T32/P32 pair."""
    import caller,rows,scalars,chain_root as CR
    root=CR.verify_root(*CR.GATE)
    gate=CR.build(*CR.GATE)
    forward=caller.replay(gate);reverse=rows.transpose(gate);scalars.verify(gate)
    gT,gP,_,_=pricing.literal_invoice(local,gate)
    rT,rP,_,_=pricing.literal_invoice(local,retained)
    extraT,extraP=Counter(rT),Counter(rP);extraT.subtract(gT);extraP.subtract(gP)
    extraT={r:n for r,n in extraT.items()if n};extraP={r:n for r,n in extraP.items()if n}
    N.need(extraT==extraP=={32:208},'Gate histogram is #6726 minus one cancelling pair, so the crossing is identical')
    return gate,{'root':root,'forward':forward,'reverse':reverse,'cancelling_pair':{'rank':32,'per_side':208},
                 'roles':gate['roles'],'events':len(gate['events']),'max_merged_idle_stages':max(len(e[2])for e in gate['events']if e[0]=='IDLE_ONE')}

def allocation(word,candidate):
    main=set(candidate['live'])|{r+112 for r in candidate['live']}
    helpers=sorted(set(range(candidate['public']))-main)
    mains={(role,port)for role in range(word['roles'])for port in candidate['ports']}
    jobs=[]
    for e in word['events']:
        if e[0]=='LOCAL':
            stage=e[1]
            jobs.extend((stage,r,candidate['initial'][r],candidate['final'][r])for r in helpers)
    N.need(len({(s,r)for s,r,a,b in jobs})==len(jobs)==18*564,'Every native helper has a disjoint independent input')
    N.need(len(mains)+len(jobs)==12232,'Complete main and helper field allocation')
    N.need(candidate['owned_fields']==29,'Separately allocated zero workspace')
    return {'caller_main_fields':len(mains),'native_helper_fields':len(jobs),'total_independent_fields':len(mains)+len(jobs),
            'helpers_per_native_call':len(helpers),'helper_boundary_normalizers':2*len(jobs),
            'native_owned_labels_per_call':29,'peak_owned_per_call':14,'sequential_thin_query_scratch':1,
            'allocation_sha256':sha256(payload(jobs)).hexdigest()}

def run():
    started=time.monotonic()
    pins=json.loads((HERE/'retained/SOURCE-PINS.json').read_bytes())
    for pin in pins:
        b=(HERE/pin['local']).read_bytes()
        from hashlib import sha1
        N.need(sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==pin['git_blob'],'Exact retained Git blob '+pin['local'])
        N.need(sha256(b).hexdigest()==pin['sha256'],'Exact retained source bytes '+pin['local'])
    source=N.read(HERE/'retained/native/PR6702-WORD.json.gz')
    N.need(sha256((HERE/'retained/native/PR6702-WORD.json.gz').read_bytes()).hexdigest()=='e8c7a9d54d98a4cfa27e15593016b3908afed303e0f480076ed3f596192e5a4d','Pinned native source')
    witness=N.read(HERE/'WITNESS.json')
    expected=N.read(HERE/'EXPECTED.json')
    N.need(sha256((HERE/'LIFT.json').read_bytes()).hexdigest()==expected['lift_sha256'],'Pinned lift edit list')
    edit=json.loads((HERE/'LIFT.json').read_bytes())
    intermediate=construct_base(source,witness)
    N.need(sha256(payload(intermediate)).hexdigest()==expected['base_native_payload_sha256'],'Rebuilt pending #6805 native word')
    candidate=construct(source,witness)
    N.need(sha256(payload(candidate)).hexdigest()==expected['native_payload_sha256'],'Rebuilt complete native word')
    local=N.replay(candidate)
    progress('PASS exact #6805 reconstruction, lift edit and forward all-input replay')
    lift_controls=lift_negative_controls(intermediate,edit)
    progress('PASS lift negative controls: wrong coefficient, missing repair, aliased helpers, stale bound event')
    native=N.native(candidate)
    progress('PASS every signed native map, absolute phase and boundary normalizer')
    columns=changed_columns(source,candidate,intermediate,edit)
    progress('PASS '+str(columns['exact_columns'])+' explicit changed native Gaussian columns')
    independent=N.load(HERE/'independent/check_native.py','retimed_independent_adjoint')
    with tempfile.TemporaryDirectory(prefix='native-retimed-')as d:
        path=Path(d)/'candidate.json.gz';path.write_bytes(gzip.compress(payload(candidate),mtime=0))
        middle=Path(d)/'intermediate.json.gz';middle.write_bytes(gzip.compress(payload(intermediate),mtime=0))
        audit=independent.run(HERE/'retained/native/PR6702-WORD.json.gz',middle,path,HERE/'WITNESS.json',HERE/'LIFT.json',True)
        sys.path.insert(0,str(HERE/'independent'))
        independent_invoice=N.load(HERE/'independent/check_invoice.py','retimed_independent_invoice')
        invoice_audit=independent_invoice.run(HERE/'retained/caller',HERE/'CALLER.json',HERE/'retained/native/PR6702-WORD.json.gz',path,audit)
        invoice_audit.pop('candidate_sha256',None)
    audit.pop('candidate_sha256',None) # Compression bytes are not mathematical identity.
    audit['split'].pop('candidate_sha256',None)
    progress('PASS independent native adjoint, ownership monitors, lift audit and controls')
    import caller,rows,scalars,retirement,root_check,chain_root as CR
    # Retained #6726 caller: rebuilt and rechecked as the published baseline; it is not priced.
    retained_root=root_check.verify(N.read(HERE/'retained/caller/ROOT.json'))
    retained_base=caller.construct()
    N.need(retained_base==N.read(HERE/'retained/caller/CALLER-UNRETIRED.json'),'Literal unchanged unretired #6726 caller')
    retained_one,retained_word,retained_witnesses=retirement.construct(retained_base)
    N.need(retained_one==N.read(HERE/'retained/caller/CALLER-ONE-RETIRED.json')and retained_word==N.read(HERE/'retained/caller/CONTROLLER.json'),'Both retained #6726 retirements')
    N.need(retained_witnesses==N.read(HERE/'retained/caller/RETIREMENT-WITNESSES.json'),'Retained #6726 construction witnesses')
    retained_call=caller.replay(retained_word)
    independent_caller=N.load(HERE/'retained/caller/independent.py','retimed_independent_caller')
    caller_audit=independent_caller.run()
    progress('PASS retained #6726 caller rebuilt with its independent Laurent-ring replay')
    # New caller: formula root, deterministic constructor, literal binding, both replays and scalars.
    root=CR.verify_root(*CR.SHAPE)
    word=CR.build(*CR.SHAPE)
    N.need(word==N.read(HERE/'CALLER.json'),'Constructor rebuilds the committed literal caller')
    N.need(sha256(payload(word)).hexdigest()==expected['caller_payload_sha256'],'Pinned caller payload')
    N.need(sha256(json.dumps(word['events'],separators=(',',':')).encode()).hexdigest()==expected['caller_event_sha256'],'Pinned caller events')
    call=caller.replay(word)
    reverse=rows.transpose(word)
    caller_scalars=scalars.verify(word)
    N.need(all(Q(e[-1]).denominator==1 for e in word['events']if e[0]in('ADD','SCALE')),'Integral ordinary caller scalars')
    independent_root=N.load(HERE/'independent/check_root.py','chain_independent_root').family(word)
    progress('PASS chain-nested root identity, chain merge, forward and reverse caller replay, scalars, independent root audit')
    gate,gate_receipt=gate_shape(local,retained_word)
    progress('PASS gate shape (4,4,1|1,4,4): replay and histogram equal to #6726 minus a cancelling pair')
    physical_module=N.load(HERE/'retained/runtime/physical.py','retimed_caller_physical')
    physical=physical_module.physical(word,candidate,L)
    fields=allocation(word,candidate)
    progress('PASS all 7488 caller contacts, whole jobs and independent field allocation')
    prior=N.load(HERE/'retained/physical-review/verify.py','retimed_canonical_physical_audit')
    recipes=N.read(HERE/'retained/runtime/DATA-PHASES.json')
    independent_local=prior.native_ledger(candidate)
    independent_physical=prior.physical(word,candidate,recipes)
    N.need(independent_physical['contact_digest']==physical['route_payload_sha256'],'Independent absolute caller contacts and phases')
    independent_fields=prior.allocation(word,candidate,independent_local)
    independent_bill=prior.invoice(word,independent_local,independent_physical,independent_fields)
    records=prior.adapter_inventory(word,candidate,recipes)
    adapters=prior.check_adapter_inventory(records,word,independent_physical)
    full_work=prior.ordinary(word,independent_local,independent_fields,independent_bill,adapters)
    # The retained review prints a fixed growth-bound string for the #6805 rank mass; state the recounted one.
    N.need(full_work['paid_rank_mass']==166812,'Recounted paid rank mass')
    full_work['growth_bound']='2^(10^9 + '+str(full_work['paid_rank_mass'])+'*f), subject to retained physical precision/tape implementation rates'
    canonical_controls={}
    for kind in ['main','idle','query']:
        bad=deepcopy(records);bad[kind].pop()
        canonical_controls['omitted_'+kind+'_adapter']=prior.rejection(lambda bad=bad:prior.check_adapter_inventory(bad,word,independent_physical))
    canonical_controls['omitted_contact_phase']=prior.rejection(lambda:prior.physical(word,candidate,recipes,True))
    canonical_controls['aliased_native_helpers']=prior.rejection(lambda:prior.allocation(word,candidate,independent_local,True))
    progress('PASS independently reconstructed physical contacts and all canonical-job boundary adapters')
    price=pricing.run(local,native,word,physical,L,adapters,gate)
    caller_controls=caller_negative_controls(word,local,native,physical,candidate,recipes,prior)
    progress('PASS caller negative controls')
    prior.compare_invoice(independent_bill,price)
    N.need(full_work['complete_scalar_upper']==price['nonrecursive']['raw_scalar_upper']==invoice_audit['ordinary']['raw_upper']==ORDINARY_UPPER,'Complete independently charged ordinary budget')
    canonical_audit={'adapters':adapters,'ordinary':full_work,'controls':canonical_controls,
                     'physical':{k:v for k,v in independent_physical.items()if k!='idle_records'},
                     'central_normalization':prior.central_normalization()}
    progress('PASS both exact interval engines, strictification, compiler and 54+4 outer inequalities')
    return {'status':'PASS_CHAIN_NESTED_ROOT','base_commit':'7c49fe32c55de02c2c873655c804b16e4c3fef0a',
            'native_payload_sha256':sha256(payload(candidate)).hexdigest(),'local':local,'native':native,'changed_columns':columns,'lift_controls':lift_controls,
            'independent_native':audit,'independent_invoice':invoice_audit,'root':root,'caller':call,'caller_reverse':reverse,'caller_scalars':caller_scalars,'independent_root':independent_root,
            'caller_controls':caller_controls,'gate':gate_receipt,'retained_caller':{'root':retained_root,'replay':retained_call,'independent':caller_audit,
            'largest_merged_idle_stages':max(len(e[2])for e in retained_base['events']if e[0]=='IDLE_ONE')},'merged_idle_stage_sizes':sorted(len(e[2])for e in word['events']if e[0]=='IDLE_ONE'),'physical':physical,
            'allocation':fields,'canonical_adapter_audit':canonical_audit,'price':price,'selected_frontier_changed':False},time.monotonic()-started

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    result,seconds=run();raw=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.write:(HERE/'RESULT.json').write_text(raw)
    else:N.need((HERE/'RESULT.json').read_text()==raw,'Replayed complete receipt equals committed result')
    print(result['status']+' in '+str(round(seconds,2))+' seconds; conditional kappa='+str(pricing.KAPPA))
