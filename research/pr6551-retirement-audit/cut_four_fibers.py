"""Independent exact cut and complete endpoint checks in all four fibers of q^4 - 1.

No source or lead replay routines are imported. Gaussian rational arithmetic and
formal commuting stage monomials are implemented here. Apache-2.0; prepared for
DLamdata with substantial OpenAI Codex assistance.
"""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import json
import sys
import hashlib

Z = (F(0), F(0))
O = (F(1), F(0))
I = (F(0), F(1))
MON = (0,)*19


def need(ok, label):
    if not ok:
        raise ValueError(label)


def plus(a, b):
    return a[0]+b[0], a[1]+b[1]


def times(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def power(a, n):
    out=O
    for _ in range(n%4):
        out=times(out,a)
    return out


def add_poly(a, b, scalar=O):
    result=dict(a)
    for mon, value in b.items():
        value=plus(result.get(mon,Z),times(value,scalar))
        if value==Z:
            result.pop(mon,None)
        else:
            result[mon]=value
    return result


def scale(a, b):
    return {mon:times(value,b) for mon,value in a.items() if times(value,b)!=Z}


def stage(a, labels):
    labels=set(labels)
    return {tuple(x+int(i in labels) for i,x in enumerate(mon)):value for mon,value in a.items()}


def replay_vector(events, q, reverse=False, target=4):
    state=[{} for _ in range(35)]
    state[target]={MON:O}
    for e in (reversed(events) if reverse else events):
        op=e[0]
        if op in ('SCALE','Q_POWER','LAMBDA'):
            r=e[1]
            if op=='SCALE':
                c=(F(e[2]),F(0))
            elif op=='Q_POWER':
                c=power(q,e[2])
            else:
                c=plus((F(1,2),F(e[2],2)), times((F(1,2),F(-e[2],2)),power(q,2)))
            state[r]=scale(state[r],c)
        elif op=='SWAP':
            a,b=e[1:]
            state[a],state[b]=state[b],state[a]
        elif op in ('ADD','QUERY'):
            dst,src=e[1:3]
            c=(F(e[3]),F(0)) if op=='ADD' else power(q,e[3])
            if reverse:
                src,dst=dst,src
            state[dst]=add_poly(state[dst],state[src],c)
        elif op=='LOCAL':
            j,src,dst=e[1:]
            if reverse:
                state[src]=stage(state[src], [j])
                state[dst]=stage(state[dst], [j])
                state[src]=add_poly(state[src],state[dst],power(q,-1))
            else:
                state[dst]=add_poly(state[dst],state[src],power(q,-1))
                state[src]=stage(state[src],[j])
                state[dst]=stage(state[dst],[j])
        elif op in ('IDLE','IDLE_ONE'):
            roles,labels=(e[1:3],e[3]) if op=='IDLE' else ([e[1]],e[2])
            for r in roles:
                state[r]=stage(state[r],labels)
        else:
            raise ValueError('unknown opcode '+op)
    return state


def slots(e):
    return {'ADD':(1,2),'SWAP':(1,2),'SCALE':(1,),'LAMBDA':(1,),
            'Q_POWER':(1,),'QUERY':(1,2),'LOCAL':(2,3),'IDLE':(1,2),'IDLE_ONE':(1,)}[e[0]]


def audit(word):
    events=word['events']
    need(word['roles']==35 and word['stages']==18,'dimensions')
    prefix=events[:345]
    need(prefix[-1]==['ADD',4,21,'1'],'cut marker')
    need(all(e[i]!=34 for e in prefix for i in slots(e)),'fresh input used before handoff')
    need(all(e[i]!=4 for e in events[345:-3] for i in slots(e)), 'retired input reused after handoff')
    need(events[-3:]==[['LAMBDA',4,-1],['LAMBDA',20,-1],['LAMBDA',21,-1]],'final normalization')
    totals=[]
    for q in [O,(-F(1),F(0)),I,(F(0),-F(1))]:
        lam=plus((F(1,2),F(1,2)),times((F(1,2),-F(1,2)),power(q,2)))
        s=times(lam,power(q,-1))
        expected=[{} for _ in range(35)]
        expected[4]={MON:s}
        for reverse in [False,True]:
            got=replay_vector(prefix,q,reverse)
            need(got==expected,'pivot column' if not reverse else 'pivot row')
        totals.append({'q':[str(v) for v in q], 'pivot_scalar':[str(v) for v in s], 'row_coefficients':35,'column_coefficients':35})
    return totals


def reject(label,word):
    try:
        audit(word)
    except ValueError as exc:
        return {'control':label,'rejected_by':str(exc)}
    raise ValueError('accepted mutant: '+label)


class EndpointMismatch(ValueError):
    """A scientific endpoint disagreement, distinct from input validation."""
    def __init__(self, witness):
        super().__init__('full formal endpoint mismatch')
        self.witness = witness


def encode_poly(value):
    return [[list(mon), [str(c[0]), str(c[1])]] for mon,c in sorted(value.items())]


def full_endpoint(word):
    """Replay every output row backward, keeping all stage powers formal."""
    need(word['roles']==35 and word['stages']==18,'endpoint dimensions')
    diagonal=word['diagonal']
    need(len(diagonal)==35,'endpoint target count')
    for d in diagonal:
        need(len(d)==20 and all(type(x) is int for x in d),'endpoint integer signature')
        need(d[1]==0 and all(x>=0 for x in d[1:]),'endpoint formal stage signature')
    fibers=[]
    for q in [O,(-F(1),F(0)),I,(F(0),-F(1))]:
        for output in range(35):
            got=replay_vector(word['events'],q,reverse=True,target=output)
            d=diagonal[output]
            expected=[{} for _ in range(35)]
            expected[output]={tuple(d[1:]):power(q,d[0])}
            if got!=expected:
                coordinate=next(i for i in range(35) if got[i]!=expected[i])
                raise EndpointMismatch({'q':[str(x) for x in q],
                    'output':output,'input':coordinate,
                    'actual':encode_poly(got[coordinate]),
                    'expected':encode_poly(expected[coordinate])})
        fibers.append({'q':[str(x) for x in q], 'output_rows':35,
                       'coefficient_positions':35*35})
    return {'fibers':fibers,'events':len(word['events']),
            'coefficient_positions_per_fiber':35*35,
            'total_coefficient_positions':4*35*35,
            'formal_stage_variables':list(range(1,19)),
            'stage_zero_retained_and_zero_in_target':True}


def endpoint_reject(label,word):
    # Require an actual transfer disagreement; a schema or cut failure is not
    # accepted as evidence that the independent suffix calculation detected it.
    try:
        full_endpoint(word)
    except EndpointMismatch as exc:
        return {'control':label,'rejected_by':'full formal endpoint mismatch',
                'witness':exc.witness}
    raise ValueError('accepted endpoint mutant: '+label)


def shared_region(a,b):
    old,new=a['events'],b['events']
    prefix=0
    while prefix<min(len(old),len(new)) and old[prefix]==new[prefix]:
        prefix+=1
    suffix=0
    while suffix<min(len(old),len(new))-prefix and old[-suffix-1]==new[-suffix-1]:
        suffix+=1
    need(prefix==358 and suffix==67,'exact maximal shared event regions')
    return {'common_prefix_events':prefix,'common_suffix_events':suffix,
            'changed_old_half_open':[prefix,len(old)-suffix],
            'changed_new_half_open':[prefix,len(new)-suffix],
            'changed_diagonal_roles':[i for i,(x,y) in enumerate(zip(a['diagonal'],b['diagonal'])) if x!=y]}


def main():
    need(len(sys.argv)==3,'expected old and new controller paths')
    old,new=map(Path,sys.argv[1:3])
    a=json.loads(old.read_text());b=json.loads(new.read_text())
    need(a['events'][:345]==b['events'][:345],'literal prefix unchanged')
    results={'old':audit(a),'new':audit(b),
             'old_full_endpoint':full_endpoint(a),'new_full_endpoint':full_endpoint(b),
             'shared_regions':shared_region(a,b)}
    controls=[]
    bad=deepcopy(b);bad['events'][340][-1]='-1'
    controls.append(reject('changed_middle_add_sign',bad))
    bad=deepcopy(b);bad['events'][0][-1]='1'
    controls.append(reject('changed_input_basis_sign',bad))
    bad=deepcopy(b);bad['events'][0][2]=34
    controls.append(reject('fresh_input_read_before_handoff',bad))
    bad=deepcopy(b);bad['events'].insert(345,['ADD',0,4,'1'])
    controls.append(reject('retired_input_reused_after_handoff',bad))
    # A true external cancellation keeps the prefix operator identical.
    positive=deepcopy(b);positive['events'][5:5]=[['ADD',1,2,'1'],['ADD',1,2,'-1']]
    for q in [O,(-F(1),F(0)),I,(F(0),-F(1))]:
        for rev in [False,True]:
            need(replay_vector(positive['events'][:347],q,rev)==replay_vector(b['events'][:345],q,rev),'cancelling ADD pair')
    # An arbitrary dirty-input suffix change with exact inverse remains valid;
    # the endpoint checker must not reject every changed suffix by identity pin.
    positive_suffix=deepcopy(b)
    positive_suffix['events'][372:372]=[['ADD',3,34,'1/2'],['ADD',3,34,'-1/2']]
    suffix_positive=full_endpoint(positive_suffix)
    need(b['events'][363]==['ADD',1,22,1],'event363 ADD control input')
    need(b['events'][358]==['IDLE',20,21,[10,11,12,13,14]],'event358 IDLE control input')
    need(b['events'][371]==['LOCAL',10,0,1],'event371 LOCAL control input')
    need(b['diagonal'][34][12]==1,'fresh target contains D11')
    mutations=[]
    bad=deepcopy(b);bad['events'][363][-1]=-bad['events'][363][-1]
    mutations.append(('suffix_event363_add_sign',bad))
    bad=deepcopy(b);bad['events'][358][-1].remove(11)
    mutations.append(('suffix_event358_idle_remove_D11',bad))
    bad=deepcopy(b);bad['events'][371][2],bad['events'][371][3]=bad['events'][371][3],bad['events'][371][2]
    mutations.append(('suffix_event371_local_swap_source_destination',bad))
    bad=deepcopy(b);bad['diagonal'][34][12]=0
    mutations.append(('fresh_diagonal_remove_D11',bad))
    endpoint_controls=[]
    for label,bad in mutations:
        need(bad['events'][:345]==b['events'][:345],'mutant preserves literal cut prefix')
        audit(bad)  # Existing cut/lifetime checks pass; only full endpoint fails.
        rejection=endpoint_reject(label,bad)
        rejection['existing_cut_checks_pass']=True
        endpoint_controls.append(rejection)
    results.update(status='PASS_FOUR_FIBER_RETIREMENT_CUT_AND_ENDPOINTS',
        literal_shared_events=345,raw_shared_prefix_events=329,
        controls=controls,endpoint_controls=endpoint_controls,
        positive_control='cancelling ADD pair at cut input',
        endpoint_positive_control={'description':'inverse half-ADD pair on arbitrary fresh input in changed suffix',
                                   'events':suffix_positive['events'],
                                   'total_coefficient_positions':suffix_positive['total_coefficient_positions']},
        input_sha256={'old':hashlib.sha256(old.read_bytes()).hexdigest(),
                      'new':hashlib.sha256(new.read_bytes()).hexdigest()})
    print(json.dumps(results,indent=2,sort_keys=True))

if __name__=='__main__':main()
