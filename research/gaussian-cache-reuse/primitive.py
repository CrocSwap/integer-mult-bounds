"""Literal owned-cache primitives with exact dyadic-complex column checks.

Classical copy/transport sharing; repository Clifford implementation retained
unchanged and authenticated by the caller. Apache-2.0; Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from geometry import need, distance, span, fanout_program, dual_program, tariffs

ZERO=(Q(0),Q(0));ONE=(Q(1),Q(0))


def add(a,b):
    return a[0]+b[0],a[1]+b[1]


def mul(a,b):
    return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]


def conjugate(ce,op):
    out=ce.ident(op.n)
    for e in op.circuit:
        if e[0]=='P':part=ce.perm(op.n,e[1])
        elif e[0]=='D':part=ce.diag(op.n,e[1],tuple(-a%4 for a in e[2]))
        elif e[0]=='C':part=ce.cgate(op.n,e[1],-e[2])
        elif e[0]=='X':part=ce.xgate(op.n,e[1])
        elif e[0]=='phase':part=ce.Op(op.n,ce.identity(op.n),[('phase',-e[1]%4)])
        else:raise ValueError('Unrecognized exact circuit primitive')
        out=out.then(part)
    return out


def matrix(op):
    cols=[]
    for j in range(1<<op.n):
        vec,den=op.zero_state(j)
        cols.append([(Q(a,1<<den),Q(b,1<<den)) for a,b in vec])
    return [list(row) for row in zip(*cols)]


def mv(a,x):
    return [sum_pairs(mul(v,w) for v,w in zip(row,x)) for row in a]


def sum_pairs(values):
    z=ZERO
    for v in values:z=add(z,v)
    return z


def proportion(snapshot,current):
    """Exact logical operator rows, not owner names or frame labels."""
    if not snapshot:return Q(0) if not current else None
    k=next(iter(snapshot));q=current.get(k,Q(0))/snapshot[k]
    return q if {k:v*q for k,v in snapshot.items() if v*q}==current else None


def run(ce,spaces):
    n=3;frames=[ce.canonical_frame(n,list_basis(s)) for s in spaces]
    edge_checks=0;non_nested=0
    for i,a in enumerate(spaces):
      for j,b in enumerate(spaces):
        op=frames[i].adjoint().then(frames[j]);recipe,compiled=ce.lower_child(op)
        need(recipe['rank']==distance(a,b),'Actual Clifford edge grade, including nonnested frames')
        need(compiled.tab==op.tab and matrix(compiled)==matrix(op),'All-column normal form and absolute phase')
        edge_checks+=1;non_nested+=int(not(a<=b or b<=a))
    roles=['X','Y1','Y2','Z','W'];size=1<<n
    forward=fanout_program();backward=dual_program()

    @lru_cache(None)
    def transition(kind,a,b):
        op=ce.canonical_frame(n,list(a)).adjoint().then(ce.canonical_frame(n,list(b)))
        return matrix(conjugate(ce,op) if kind=='DUAL_MOVE' else op)

    def execute(program,column,wrong_phase=False,changed_source=False,supplied=None):
        state={r:[ZERO]*size for r in roles} if supplied is None else {r:v[:] for r,v in supplied.items()}
        if supplied is None:state[roles[column//size]][column%size]=ONE
        mutated=False
        for e in program:
            kind,r=e[:2]
            if kind=='CLEAR':state[r]=[ZERO]*size
            elif kind=='COPY':state[r]=state[e[2]][:]
            elif kind=='ADD':
                state[r]=[add(x,(e[3]*y[0],e[3]*y[1])) for x,y in zip(state[r],state[e[2]])]
                if changed_source and r=='Y1':
                    state['X']=[(2*x,2*y) for x,y in state['X']]
            else:
                a,b=tuple(e[2]),tuple(e[3])
                if wrong_phase and not mutated:
                    kind='DUAL_MOVE' if kind=='MOVE' else 'MOVE';mutated=True
                state[r]=mv(transition(kind,a,b),state[r])
        return state

    a1=matrix(ce.canonical_frame(n,[1,2]));a2=matrix(ce.canonical_frame(n,[1,4]))
    transpose=lambda a:[list(row) for row in zip(*a)]
    def expected(column,back=False,source_changed=False):
        initial={r:[ZERO]*size for r in roles};initial[roles[column//size]][column%size]=ONE
        out={r:initial[r][:] for r in roles}
        out['Z']=out['W']=[ZERO]*size
        if back:
            delta1=mv(transpose(a1),initial['Y1']);delta2=mv(transpose(a2),initial['Y2'])
            out['X']=[(x[0]-y[0]-z[0],x[1]-y[1]-z[1]) for x,y,z in zip(initial['X'],delta1,delta2)]
        else:
            out['Y1']=[add(x,y) for x,y in zip(initial['Y1'],mv(a1,initial['X']))]
            source=[(2*x,2*y) for x,y in initial['X']] if source_changed else initial['X']
            if source_changed:out['X']=source
            out['Y2']=[add(x,y) for x,y in zip(initial['Y2'],mv(a2,source))]
        return out
    for column in range(len(roles)*size):
        need(execute(forward,column)==expected(column),'Forward: all arbitrary persistent and owned entry columns')
        need(execute(backward,column)==expected(column,True),'Raw inverse transpose: all arbitrary columns')
    need(any(execute(forward,j,True)!=expected(j) for j in range(size)),'Wrong forward phase rejected')
    need(any(execute(backward,j,True)!=expected(j,True) for j in range(size,3*size)),'Wrong raw-dual orientation rejected')
    need(any(execute(forward,j,changed_source=True)!=expected(j,source_changed=True) for j in range(size)),
         'Reusing a stale snapshot after a source change is rejected')
    row={('X',()):Q(1)};changed={('X',()):Q(1),('Y',()):Q(1)}
    need(proportion(row,changed) is None,'Changed source expression invalidates cache')
    restored=dict(changed);restored.pop(('Y',()))
    need(proportion(row,restored)==1,'A restored source is safe despite intervening writes')
    need(proportion(row,{('X',()):Q(3,2)})==Q(3,2),'Specified scalar change can be absorbed in the ADD coefficient')
    # Derived variant for an actual already-paid observation. Its correlation
    # with X is an explicit caller precondition, never independent input credit.
    existing=[['CLEAR','W']]+forward[4:-1]
    for column in range(len(roles)*size):
        initial={r:[ZERO]*size for r in roles};initial[roles[column//size]][column%size]=ONE
        wanted={r:v[:] for r,v in initial.items()};wanted['W']=[ZERO]*size
        for r,frame in [('Y1',(1,2)),('Y2',(1,4))]:
            delta=mv(transition('MOVE',(1,),frame),initial['Z'])
            wanted[r]=[add(x,y) for x,y in zip(initial[r],delta)]
        need(execute(existing,column)==wanted,'Existing observation: every independent column; cache returned unchanged')
    line=matrix(ce.canonical_frame(n,[1]))
    for j in range(size):
        supplied={r:[ZERO]*size for r in roles};supplied['X'][j]=ONE
        supplied['Z']=mv(line,supplied['X'])
        actual=execute(existing,0,supplied=supplied);wanted=expected(j)
        need(all(actual[r]==wanted[r] for r in ('X','Y1','Y2','W')) and actual['Z']==supplied['Z'],
             'Caller-proved observation Z=C_line X gives the intended target updates')
    existing_tariff=tariffs(existing);existing_tariff['owned_fields']=1
    existing_tariff['borrowed_observation_fields']=1
    return {'exact_frame_pairs':edge_checks,'non_nested_pairs':non_nested,
            'address_dimension':3,'addresses_per_field':size,'independent_original_fields':3,
            'arbitrary_owned_entry_fields_cleared':2,'all_input_columns_per_orientation':len(roles)*size,
            'forward':tariffs(forward),'raw_inverse_transpose':tariffs(backward),
            'existing_paid_observation_variant':{'tariff':existing_tariff,'all_input_columns':len(roles)*size,
                'precondition':'Z=C_line X for the exact required logical snapshot; caller supplies and already pays that observation. Z is returned unchanged. Its creation, retention and eventual cleanup remain caller costs.'},
            'negative_controls':['wrong forward phase','wrong dual orientation','stale snapshot'],
            'lifetime_controls':['restored source','specified proportional source'],
            'primitive_scope':'Exact finite module plus written block/tensor lift; no installed selected-caller improvement.'}


def list_basis(s):
    from geometry import basis
    return basis(s)
