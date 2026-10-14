"""Independent finite table replay of charged unmarked-buffer lifecycle.

This is supporting operational evidence, not the universal Lean proof.
The predecessor table is bundled as controller_controls, with its credits.
"""
from itertools import product
from hashlib import sha256
from pathlib import Path
import importlib.util
import sys
import json
_spec=importlib.util.spec_from_file_location('_clean_boundary_predecessor',Path(__file__).with_name('controller_controls.py'))
old=importlib.util.module_from_spec(_spec)
sys.modules[_spec.name]=old
_spec.loader.exec_module(old)

MARK = tuple(('marker',q) for q in range(3))
CHILD = tuple(('caller',q) for q in old.STATES)
STATES = tuple((stage,payload) for stage in range(3) for payload in MARK+CHILD)
ENTRY = ((0,MARK[0]),(1,('caller',(0,'move',old.COPY))),(2,MARK[0]))

def transition(state,scanned):
    stage,(kind,payload)=state
    result=None
    if stage in (0,2) and kind=='marker':
        value=old.SEP if stage==0 else old.BLANK
        if payload==0:
            result=('marker',1),old.actions(scanned,{i:(scanned[i],-1) for i in (0,1,2,4)})
        elif payload==1:
            result=('marker',2),old.actions(scanned,{i:(value,1) for i in (0,1,2,4)})
    elif stage==1 and kind=='caller':
        action=old.transition(payload,scanned)
        if action is not None:
            target,commands=action
            result=('caller',target),commands
    if result is not None:
        target,commands=result
        return (stage,target),commands
    if stage<2:
        return ENTRY[stage+1],old.actions(scanned,{})
    return None

def check_case(x,y,h,past,table=transition):
    machine,backgrounds,expected=old.initial_machine(x,y,h,past)
    for i in (0,1,2,4):
        machine.tapes[i].write(-1,old.BLANK)
        expected[i].pop(-1)
    machine.state=ENTRY[0]
    time=0
    while True:
        scanned=tuple(t.read(p) for t,p in zip(machine.tapes,machine.heads))
        action=table(machine.state,scanned)
        if action is None: break
        state,commands=action
        old.require(state in STATES,'control escaped finite states')
        for i,(symbol,offset) in enumerate(commands):
            old.require(symbol in range(4) and offset in (-1,0,1),'nonlocal action')
            machine.tapes[i].write(machine.heads[i],symbol)
        machine.heads=[p+cmd[1] for p,cmd in zip(machine.heads,commands)]
        machine.state=state
        time+=1
        old.require(time<=6*len(x)+5*len(y)+25,'failed to terminate')
    old.require(time==6*len(x)+5*len(y)+24,'marker or handoff invoice mismatch')
    old.require(machine.state==(2,('marker',2)),'terminal state mismatch')
    old.require(machine.heads==[0,0,0,h,0],'head restoration mismatch')
    for i,tape in enumerate(machine.tapes):
        old.require(tape.background is backgrounds[i] and tape.changes==expected[i],
                    'whole cell function mismatch')
    return time

def run_tests():
    digest=sha256(); entries=0
    for q,r in product(STATES,old.SCANS):
        a=transition(q,r)
        if a is not None:
            target,commands=a
            old.require(target in STATES and len(commands)==5,'bad finite table')
            old.require(all(s in range(4) and d in (-1,0,1) for s,d in commands),'nonlocal table')
        digest.update(json.dumps([q,r,a],separators=(',',':')).encode()+b'\n')
        entries+=1
    cases=0
    patterns=(lambda p: old.BLANK,lambda p:old.SEP,lambda p:(p*p+3*p+7)%4)
    for x,y,h,past in product(old.all_words(3),old.all_words(3),(-7,-1,0,6),patterns):
        check_case(x,y,h,past);cases+=1
    for lx,ly in ((0,23),(17,0),(5,31),(29,2)):
        check_case(tuple(i%3==0 for i in range(lx)),tuple(i%2==0 for i in range(ly)),-37,patterns[2]);cases+=1
    def broken(q,r):
        action=transition(q,r)
        if q==(2,('marker',1)) and action is not None:
            target,commands=action
            commands=tuple((old.SEP,d) if i in (0,1,2,4) else (s,d) for i,(s,d) in enumerate(commands))
            return target,commands
        return action
    try:check_case((False,True),(True,),-3,patterns[2],broken)
    except RuntimeError: rejected=True
    else:raise RuntimeError('corrupted marker-removal table accepted')
    return dict(status='PASS_LITERAL_CLEAN_BOUNDARY_CONTROLS',states=len(STATES),tapes=5,
                alphabet=4,table_entries=entries,table_sha256=digest.hexdigest(),cases=cases,
                cost='6|x|+5|y|+24',corrupted_removal_rejected=rejected)

if __name__=='__main__': print(json.dumps(run_tests(),sort_keys=True))
