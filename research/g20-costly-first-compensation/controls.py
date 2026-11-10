"""Independent full-state invoice checks on a complete small-word domain."""
from collections import Counter
from itertools import product
import random

def full(records,start,final,owned,distances):
    rows=[1<<i for i in range(len(start))];frames=list(start);bill=[0]*9;histories=[[] for _ in start]
    for event in records:
        op,d=event[:2]
        if op in ('ERASE','INIT'):
            if d not in owned or (op=='INIT' and rows[d]):raise ValueError('owned action')
            rows[d]=0;histories[d].append((event[2],False));frames[d]=event[2]
        elif op=='ADD':
            s,f=event[2:]
            if not rows[s]:continue
            for role in (d,s):
                histories[role].append((f,bool(rows[role])))
                if frames[role]!=f and rows[role]:
                    if frames[role] is None:raise ValueError('uninitialized nonzero')
                    bill[distances[frames[role]][f]]+=1
                frames[role]=f
            rows[d]^=rows[s]
        else:raise ValueError('opcode')
    for r,f in enumerate(final):
        if r in owned:
            if rows[r]:raise ValueError('owned final')
        else:
            histories[r].append((f,bool(rows[r])))
            if frames[r]!=f and rows[r]:bill[distances[frames[r]][f]]+=1
    return bill,rows,histories

def run(primary,trace):
    distance={a:{b:abs(a-b) for b in range(3)} for a in range(3)}
    start=[0,1,2];final=[2,0,None];owned={2}
    alphabet=[('ADD',d,s,f) for d in range(3) for s in range(3) if d!=s for f in (0,2)]+[('ERASE',2,1)]
    counts=Counter();special=None
    from pathlib import Path
    from types import ModuleType
    raw=Path(trace.__file__).read_text()
    mutations={
        'missing_suffix_charge': ('        if hi<len(req):\n            old=old+[req[hi]];changed=changed+[req[hi]]\n',''),
        'missing_third_role_demand': ('        if merge:changed=sorted(old+changed)','        if merge:changed=old'),
        'missing_source_row_toggle': ('source=olds^bval if s==a else olds','source=olds'),
        'zero_destination_charged': ('if nonzero and frame!=target:','if nonzero is not None and frame!=target:'),
    }
    mutant_classes={}
    for name,(before,after) in mutations.items():
        if raw.count(before)!=1:raise ValueError('mutant binding '+name)
        module=ModuleType(name);exec(compile(raw.replace(before,after),name,'exec'),module.__dict__)
        mutant_classes[name]=module.Trace
    detected=set()
    from bisect import bisect_left,bisect_right
    class AuditTrace(trace.Trace):
        def _replace(self,r,left,right,changed,bill,merge=False):
            req=self.requests[r];lo=bisect_left(self.keys[r],left);hi=bisect_right(self.keys[r],right)
            middle=sorted(req[lo:hi]+changed) if merge else changed
            self.changed[r]=req[:lo]+middle+req[hi:]
            return super()._replace(r,left,right,changed,bill,merge)
        def delta(self,candidate):
            self.changed=list(self.requests)
            return super().delta(candidate)
    def movements(requests,frame):
        result=[]
        for target,paid in requests:
            if target!=frame:result.append((frame,target,bool(paid)))
            frame=target
        return result
    def check(word):
        nonlocal special
        records=list(word)+[('ERASE',2,None)]
        tr=AuditTrace(records,start,final,owned,distance)
        base,rows,_=full(records,start,final,owned,distance)
        if tr.base!=base or tr.endpoint!=rows:raise ValueError('base independent mismatch')
        counts['words']+=1
        for candidate in primary.candidates(records):
            changed=primary.rewrite(records,candidate)
            bill,endpoint,actual_history=full(changed,start,final,owned,distance)
            if endpoint!=rows:raise ValueError('A2 endpoint')
            expected=[a-b for a,b in zip(bill,base)]
            if expected!=tr.delta(candidate):raise ValueError(('trace mismatch',records,candidate,expected,tr.delta(candidate)))
            for role in range(len(start)):
                predicted=[(entry[2],entry[3]) for entry in tr.changed[role]]
                if movements(predicted,start[role])!=movements(actual_history[role],start[role]):raise ValueError('per-role complete history')
            for name in mutant_classes.keys()-detected:
                try:
                    mt=mutant_classes[name](records,start,final,owned,distance)
                    mutant=mt.delta(candidate)
                except ValueError:
                    detected.add(name)
                else:
                    if mutant!=expected:detected.add(name)
            counts['intervals']+=1
            counts['zero_contacts']+=not candidate[4]
            left,right,a,b,_=candidate
            for k in range(left+1,right):
                e=records[k]
                if e[0]=='ADD' and e[2]==a and tr.values[k][1] and tr.values[k][1]==tr.row(b,k):counts['changed_source_becomes_zero']+=1
                if e[0]=='ADD' and e[2]==a and not tr.values[k][1] and tr.row(b,k):
                    counts['third_role_extra_demand']+=1
                    special=(records,candidate)
    for length in range(5):
        for word in product(alphabet,repeat=length):check(word)
    exhaustive=dict(counts)
    rng=random.Random(12)
    for _ in range(2000):check([rng.choice(alphabet) for _ in range(20)])
    if not counts['changed_source_becomes_zero']:raise ValueError('changed zero-source case uncovered')
    if not counts['third_role_extra_demand']:raise ValueError('zero-source side-demand uncovered')
    # The complete small domain covers multiple physical frames, zero sources,
    # zero destinations, owned barriers and final returns, without sampling.
    # The longer deterministic generated cases broaden interaction coverage.
    if detected!=set(mutations):raise ValueError('undetected invoice mutants '+str(set(mutations)-detected))
    return {'exhaustive_short_words':exhaustive,'combined':dict(counts),'rejected_mutations':sorted(detected)}
