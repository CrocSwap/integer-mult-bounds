#!/usr/bin/env python3
"""Immutable alpha-renaming join only; root executes, no physics rerun."""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import argparse,copy,json
HERE=Path(__file__).resolve().parent
def need(x,s):
    if not x:raise ValueError(s)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def check(d,plan,b):
    w=d['controller'];events=w['physical_events'];em=d['typed_emission'];need(len(em)==len(events),'one typed emission per sourcephysicalevent')
    need(d['source_controller_sha256']==plan['bindings']['controller_sha256']and d['local_backward_sha256']==plan['bindings']['B_sha256'],'actualglobalpacket source/localjoin')
    need(d['main_input_fields']==3584 and d['total_independent_persistent_fields']==10928 and d['local_owned_fields']==306 and d['query_owned_snapshot_fields']==112 and d['macro_level_field_slots_before_recursive_child_scratch']==11346,'actualraw418owned allocator')
    helper_ranks={(r['event_index'],o):r['rank']for r in plan['helper_targets']for o in r['owners']};calls=[];owners=set();helperjobs=[]
    for i,(e,t)in enumerate(zip(events,em)):
        need(t['source_event_index']==i,'actualchronology event index')
        if e[0]=='LOCAL':
            n=len(calls);_,stage,pair,back=e;loc=plan['locals'][n];need(back and loc['event_index']==i and loc['stage']==stage and loc['pair']==pair,'sameLOCALstage/entrybindings')
            need(t['op']=='CALL_NEUTRAL_BACKWARD'and t['local_call_index']==n and t['stage']==stage and t['pair']==pair and t['macro_sha256']==plan['bindings']['B_sha256'],'actualBword perLOCAL')
            bind={}
            for f,r in b['physical_field_bindings'].items():
                bind[f]=224*pair+r if r<224 else 3584+408*n+r-224 if r<632 else 10928+17*n+r-632
            need(t['physical_field_bindings']==bind and len(set(bind.values()))==649,'all649actualfieldIDs agreewithplanalpha-renaming')
            need(t['original_independent_helper_fields']==list(range(3584+408*n,3584+408*(n+1)))and t['owned_fields']==list(range(10928+17*n,10928+17*(n+1))),'all408persistent/17owned disjoint actualrouting')
            for r in range(224,632):
                fid=3584+408*n+r-224;need(fid not in owners,'persistenthelpercollision');owners.add(fid)
                helperjobs.append({'call_index':n,'global_field':fid,'independent_productive_input':True,'positive_layout':'canonicalC_rankbits0..rank-1','rank':helper_ranks[i,r],'source_role':r})
            need(t['owned_entry']=='arbitrary'and t['owned_exit']=='all17zero','actualarbitraryownedentry/zeroreturn')
            calls.append(i)
        elif e[0]=='QUERY_SHEAR':
            _,stage,pair,back=e;src=2*pair+int(back);dst=2*pair+int(not back)
            need(t['op']=='RETAINED_QUERY_SHEAR112'and t['stage']==stage and t['pair']==pair and t['backward']==back,'actualquery orientation')
            need(t['source_main_bank']==src and t['target_main_bank']==dst and t['source_fields']==list(range(src*112,(src+1)*112))and t['target_fields']==list(range(dst*112,(dst+1)*112)),'actualquerysource/targetportbindings')
            need(t['owned_snapshot_bank']==list(range(11234,11346))and t['paid_rank1_calls']==112,'samesharedquery112ownedbank')
        elif e[0]=='IDLE':
            need(t['op']=='RETAINED_WHOLE_IDLE'and t['pair']==e[1]and t['stages']==e[2]and t['rank']==8*len(e[2])and t['fields']==list(range(224*e[1],224*(e[1]+1)))and t['paid_calls']==224,'actualwholeIDLE224binding')
        else:need(t['op']=='RETAINED_MAIN_EVENT'and t['event']==e and t['ports']==112,'literalmain event retained')
    need(d['canonical_helper_jobs']==helperjobs and owners==set(range(3584,10928))and len(calls)==18,'actual7344helperjobs allrank/ownerbindings')
    need(d['runtime_local_directions']=={'backward':18,'forward_macro_calls':0},'noextraFwrapperdoublecount')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    pp=HERE/'WHOLECALLER-PLAN-v1.json';rp=HERE/'WHOLECALLER-RESULT-v1.json';dp=HERE.parent/'caller/NEUTRAL-CALLER-v16c.json';bp=HERE.parent/'caller/NEUTRAL-BACKWARD-v16c.json';plan=json.loads(pp.read_text());result=json.loads(rp.read_text());d=json.loads(dp.read_text());b=json.loads(bp.read_text())
    need(result['plan_sha256']==sha(pp)and result['status']=='PASS_EXACT_WHOLECALLER_AND_ALL10928_CANONICAL_TARGET_ROUTES','acceptedcompleteplanreceipt')
    ctrl=HERE.parents[2]/'swarm-next-gain-sol-high-20261024/repository/research/kappa-backward-controller-20261023/CONTROLLER.json';need(d['controller']==json.loads(ctrl.read_text()),'globalpacket embeds exactsourcecontroller')
    check(d,plan,b);controls=[]
    for label,change in [('wrongmainport',lambda z:next(e for e in z['typed_emission']if e['op']=='CALL_NEUTRAL_BACKWARD')['physical_field_bindings'].__setitem__('x0',1)),('reusedhelperowner',lambda z:next(e for e in z['typed_emission']if e['op']=='CALL_NEUTRAL_BACKWARD')['original_independent_helper_fields'].__setitem__(0,0)),('queryownedoverlap',lambda z:next(e for e in z['typed_emission']if e['op']=='RETAINED_QUERY_SHEAR112')['owned_snapshot_bank'].__setitem__(0,10928))]:
        bad=copy.deepcopy(d);change(bad)
        try:check(bad,plan,b)
        except(ValueError,KeyError)as ex:controls.append({'name':label,'rejected':True,'reason':str(ex)});continue
        raise ValueError('bindingmutantaccepted '+label)
    out={'schema':'independent-neutral-caller-alpha-binding/v1','status':'PASS_ACTUAL_GLOBAL649_FIELD_ALPHA_RENAMING_AND418_OWNED','global_packet_sha256':sha(dp),'canonical_route_plan_sha256':sha(pp),'wholecaller_receipt_sha256':sha(rp),'checker_sha256':sha(Path(__file__)),'actual_fields':11346,'persistent_targets':10928,'private_fields':418,'source_controller_sha256':sha(ctrl),'controls':controls,'authoritative_execution':'The immutableglobalpacket supplies concreteintegerIDs/controller/Bcalls; WHOLECALLER-PLAN-v1 supplies the finalcommon145axisembedding, actualglobaltarget/IDLEroutewords and RIGHTeventsLEFTnormalization order. Read them jointly. Earlierglobalpacketgenericphysical_kernel prose doesnot overrideexplicitplanrecipes.','funding_admitted':False}
    need(not a.output.exists(),'freshbindingreceipt');a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,sort_keys=True))
if __name__=='__main__':main()
