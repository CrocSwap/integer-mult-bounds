#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Retained independent rational forward/reverse audit of the candidate.

Reuses Hao Yan's independent engine, with predecessor notices retained.
Never interprets COPY as overwrite; forward audit enforces its zero guard.
"""
import collections
import copy
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path

HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

def require(ok, label):
    if not ok: raise AssertionError(label)

def chronology(w):
    return [e for e in w['program'] if e[0] in ('INIT','CLEAR') or (e[0]=='MOVE' and e[4])]

def main():
    b=load('contact_build',HERE/'build.py')
    engine=load('retained_independent',HERE/'retained/pr7605/retained/pr7604/independent.py')
    base=b.source_word(); prior=b.read(HERE/'retained/pr7605/data/word.json.gz')
    candidate=b.read(HERE/'data/word.json.gz')
    require(candidate==b.build_word(), 'literal construction')
    b.validate_invoice(b.read(HERE/'data/invoice-new.json'))
    require(chronology(base)==chronology(candidate), 'ordered owner chronology')
    require([e[:-1] for e in base['program'] if e[0]=='COPY']==[e[:-1] for e in candidate['program'] if e[0]=='COPY'], 'COPY chronology and coefficients')
    old=engine.audit_word(prior,'7605')
    peer=engine.audit_word(base,'7611')
    new=engine.audit_word(candidate,'candidate')
    require(len(new['rows'])==1569 and len(new['erased'])==74, '1569 rows and 74 CLEARs')
    for key in ('rows','chart','grid','owned_moves','lifetimes','peak','erased','helpers','rises'):
        require(new[key]==peer[key], 'candidate vs 7611 '+key)
    require(new['rows']==old['rows'], 'candidate vs 7605 1569 endpoint rows')
    diffs=[i for i,(a,c) in enumerate(zip(old['erased'],new['erased'])) if a!=c]
    require(diffs==[44], 'exact inherited CLEAR difference 44')
    require(old['erased'][44]==(1557,595,{451:Q(-1),902:Q(-3,2),985:Q(-3,2),1495:Q(1)}), '7605 CLEAR 44 row/owner/chart')
    require(new['erased'][44]==(1557,595,{451:Q(-1),1495:Q(1)}), 'candidate CLEAR 44 row/owner/chart')
    changed=sorted(r for r in set(peer['chains'])|set(new['chains']) if peer['chains'].get(r)!=new['chains'].get(r))
    require(changed==[134,329], 'only changed chains')
    for r in changed:
        before,after=peer['chains'][r],new['chains'][r]
        require(before[0][0]==after[0][0] and before[-1][1]==after[-1][1], 'preserved external chart endpoints')
    delta=collections.Counter(new['paid']);delta.subtract(peer['paid'])
    delta={k:v for k,v in delta.items() if v}
    require(delta=={1:-2,2:2,3:-1,4:-1,5:1}, 'native complete paid delta')
    source_invoice=b.read(HERE/'retained/pr7611/data/invoice-new.json')
    new_invoice=b.read(HERE/'data/invoice-new.json')
    require(new_invoice['targets']==source_invoice['targets'], 'complete target invariant')
    for k in set(source_invoice['paid'])|set(new_invoice['paid']):
        require(new_invoice['paid'].get(k,0)-source_invoice['paid'].get(k,0)==17*delta.get(int(k),0), 'whole invoice delta')
    # The fixed full-caller wrapper must reconcile to the independently recounted native word.
    for r in set(map(int,source_invoice['paid']))|set(peer['paid'])|set(new['paid']):
        before=source_invoice['paid'].get(str(r),0)-17*peer['paid'][r]
        after=new_invoice['paid'].get(str(r),0)-17*new['paid'][r]
        require(before==after and before>=0, 'complete caller paid wrapper')
    op=collections.Counter(new['operations']); op.subtract(peer['operations'])
    require({k:v for k,v in op.items() if v}=={'MOVE':-1}, 'event count delta')
    # Controls use the actual candidate and the same independent semantic
    # oracle, never a candidate hash as the reason for rejection.
    def must_reject(label, fn, expected):
        try:
            fn()
        except (ValueError, AssertionError) as exc:
            require(expected in str(exc), label+' failed for an unexpected reason: '+str(exc))
            return
        raise AssertionError(label+' was not rejected')

    control_reports={}
    # Observer controls preserve literal clocks and exercise guard_incidents
    # directly, without authenticating the modified source word.
    for field in (134,329):
        mutated=copy.deepcopy(base['program'])
        mutated[41076]=['ADD',0,field,'1',3]
        must_reject('intervening observer '+str(field),lambda: b.guard_incidents(mutated),str(field)+' incident window')
        control_reports['observer_'+str(field)]='incident guard rejected'

    bad_invoice=copy.deepcopy(b.read(HERE/'data/invoice-new.json'))
    bad_invoice['paid']['2']+=17
    must_reject('tampered 17-call invoice',lambda: b.validate_invoice(bad_invoice),'stored complete candidate invoice')
    control_reports['tampered_17_call_invoice']='same invoice validator rejected'

    def changed_word(old_event,replacement=None):
        w=copy.deepcopy(candidate); program=w['program']
        require(program.count(old_event)==1, 'unique candidate control literal')
        i=program.index(old_event)
        if replacement is None: program.pop(i)
        else: program[i]=replacement
        return w

    candidate_move=['MOVE',134,3,373,False]
    candidate_add=['ADD',134,329,'-1/2',373]
    for label,mutation in (
        ('wrong_rechart_move',changed_word(candidate_move,['MOVE',134,3,618,False])),
        ('missing_rechart_move',changed_word(candidate_move)),
        ('wrong_contact_coframe',changed_word(candidate_add,['ADD',134,329,'-1/2',618])),
    ):
        must_reject(label,lambda:engine.forward_audit(mutation),'ADD/COPY common chart')
        control_reports[label]='retained forward legality rejected'

    # These changes are legal syntactically; only the independently retained
    # reverse row oracle establishes their actual semantic consequence.
    for label,mutation in (
        ('omitted_contact_add',changed_word(candidate_add)),
        ('wrong_contact_coefficient',changed_word(candidate_add,['ADD',134,329,'-1/4',373])),
    ):
        outputs,labels,erased=engine.reverse_outputs(mutation)
        require(labels==[(r,f) for r,f,_ in new['erased']], label+' CLEAR correspondence')
        bad_outputs=[i for i,(x,y) in enumerate(zip(outputs,new['rows'])) if x!=y]
        bad_clears=[i for i,(x,(_,_,y)) in enumerate(zip(erased,new['erased'])) if x!=y]
        require(len(outputs)==1569 and len(erased)==74 and (bad_outputs or bad_clears), label+' must alter an endpoint or erasure')
        control_reports[label]={'endpoint_mismatches':bad_outputs,'clear_mismatches':bad_clears}
    print(json.dumps({'status':'PASS_CANDIDATE_CONTROLS','controls':control_reports},sort_keys=True))
    print(json.dumps({'status':'PASS_INDEPENDENT_CONTACT','base':'7611','endpoint_rows':1569,'clear_rows':74,'candidate_clear_diff_vs_7611':[],'candidate_clear_diff_vs_7605':[44], 'changed_fields':changed,'paid_native_delta':delta,'ordered_owner_and_copy':True},sort_keys=True))

if __name__=='__main__': main()
