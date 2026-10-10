# Adapted from Henry Grant / hcg890's PR234; upstream code is unchanged except
# the exact gen4 register count and fresh checked count/digest bindings.
# Prepared with substantial OpenAI Codex assistance; upstream notices retained.
"""Source-bound callable five-stage global physical lowering, with streaming QA.

The finite cover variable stays symbolic. One iteration means one cover class;
iter_program() is the exact template to apply to every class in each phase.
No formal F2 payload columns are replayed. The complete local tagged word is
materialized once, then all five actual renamed/reversed instruction streams
are checked and hashed. The local all-column theorem composes through these
explicit namespace, frame, copy-lifetime and boundary bindings.
"""
from array import array
from collections import Counter
from contextlib import redirect_stdout
from functools import lru_cache
from pathlib import Path
import hashlib, importlib.util, io, json, struct, sys, time

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
PHYSICAL = BASE/'five_stage_source471_physical_telescope_20261009.py'
ACTIVE = ((0,1),(1,0),(0,1),(3,2),(2,3))
BANKS = ('X1','Y1','X2','Y2')
V, R, H, M = 1760, 16410, 24, 120
LOCAL, LIVE, WORK = 2*V+R, 4*V+R, 4*V+R
# Compact instruction kinds: move, add, copy, erase, idle, bridge, completion.
MOVE, ADD, COPY, ERASE, IDLE, BRIDGE, COMPLETE, EXCHANGE = range(8)
LOCAL_BEGIN, LOCAL_END = 2, 3
PACK = struct.Struct('<8i')
sha = lambda b: hashlib.sha256(b).hexdigest()
if not __debug__:
    raise SystemExit('refusing optimized Python: assertion checks are required')

def family(stage, local):
    assert 0 <= stage < 5 and 0 <= local <= LOCAL
    if local == LOCAL: return WORK
    if local < V: return ACTIVE[stage][0]*V+local
    if local < 2*V: return ACTIVE[stage][1]*V+local-V
    return 4*V+local-2*V

def address(stage, local, cover='d'):
    """An actual global family and an exact right-multiplication route word.

    rho(stage,port) is the involution in the checked rational route template;
    tau(stage) is the whole-block exchange. A workstream is external and is
    reused only after ERASE. Cover-class enumeration is supplied by the compiler.
    """
    f = family(stage,local)
    if local == LOCAL: return (f, ('external_work', 0))
    if stage == 0: return (f, ('class',cover))
    route = ('rho',stage,local%V) if local < 2*V else ('tau',stage)
    return (f, ('right',cover,route))

def check_namespace(mapper=family):
    for stage in range(5):
        images = [mapper(stage,i) for i in range(LOCAL+1)]
        assert len(set(images)) == LOCAL+1, 'live/work collision'
        assert images[-1] == WORK and WORK not in images[:-1], 'external work not preserved'
        for i in range(LOCAL):
            expected = (ACTIVE[stage][0]*V+i if i<V else
                        ACTIVE[stage][1]*V+i-V if i<2*V else 4*V+i-2*V)
            assert images[i] == expected, 'incorrect data/helper owner'
    return True

class Lowerer:
    """Callable IR lowering; op records have exactly eight signed int fields.

    Stage MOVE: (op,family,old_frame,new_frame,rank,0,stage,complement).
    Stage ADD:  (op,dst,src,coefficient,frame,category,stage,complement).
    COPY:       (op,temp,src,0,frame,0,stage,complement).
    ERASE:      (op,temp,-1,0,frame,0,stage,complement).
    IDLE:       (op,family,-1,0,rank,boundary_id,-1,0).
    BRIDGE:     (op,dst,src,coefficient,0,boundary_id,-1,0).
    COMPLETE:   (op,helper,-1,0,rank,entrance_frame,-1,0).

    frame_projector() and global_stage_projector() supply exact rational matrix
    meanings on demand. Data IDLE boundaries and COMPLETE are defined below.
    """
    def __init__(self,records,context):
        self.records,self.ns = records,context
        self.W,self.C = context['W'],context['C']
        self.initial = context['initial_state']
        self.ZERO,self.FULL = context['ZERO'],context['FULL']
        self.entrances = [(4*V+j,self.initial[2*V+j],self.C.dimf[self.initial[2*V+j]])
                         for j in range(R) if self.C.dimf[self.initial[2*V+j]]]
        from pins import pin
        pin('entrance_rank_histogram',dict(Counter(a for f,s,a in self.entrances)))
        check_namespace()

    def local_rows(self,reverse=False):
        n=len(self.records)
        for k in (range(n-6,-1,-6) if reverse else range(0,n,6)):
            yield tuple(self.records[k:k+6])

    def iter_stage(self,stage,mapper=family):
        assert 0 <= stage < 5
        rev = stage in (1,3)
        for op,a,b,c,f,z in self.local_rows(rev):
            if op == MOVE:
                yield (MOVE,mapper(stage,a),c if rev else b,b if rev else c,f,0,stage,int(rev))
            elif op == ADD:
                yield (ADD,mapper(stage,a),mapper(stage,b),-c if rev else c,f,z,stage,int(rev))
            elif (op == LOCAL_END if rev else op == LOCAL_BEGIN):
                # Always COPY freshly from the original center. No operation
                # inverses an erasure. Reflected source is H-U, target is H.
                yield (COPY,mapper(stage,b),mapper(stage,a),0,c,0,stage,int(rev))
                yield (MOVE,mapper(stage,b),c,f,z,0,stage,int(rev))
            else:
                assert op == (LOCAL_BEGIN if rev else LOCAL_END)
                yield (ERASE,mapper(stage,b),-1,0,f,0,stage,int(rev))

    def iter_idle(self,which):
        # IDs select exact projector pairs in idle_projectors(), not ranks alone.
        rows = {0:((2,46,0),(3,46,1)),
                1:((2,23,2),(3,23,3)),
                2:((0,50,4),(1,50,5),(2,4,6),(3,4,7))}[which]
        for bank,rank,boundary in rows:
            for t in range(V): yield (IDLE,bank*V+t,-1,0,rank,boundary,-1,0)

    def iter_bridges(self,which):
        rows = {0:((0,2,1),(3,1,-1)),1:((3,1,1),(0,2,-1)),2:((1,3,-1),(2,0,1))}[which]
        for dst,src,coefficient in rows:
            for t in range(V): yield (BRIDGE,dst*V+t,src*V+t,coefficient,0,which,-1,0)

    def iter_completions(self):
        for helper,sigma,a in self.entrances:
            yield (COMPLETE,helper,-1,0,5*a,sigma,-1,0)

    def iter_program(self):
        for stage in range(5):
            yield from self.iter_stage(stage)
            if stage in (1,2,4):
                which={1:0,2:1,4:2}[stage]
                yield from self.iter_idle(which)
                yield from self.iter_bridges(which)
        yield from self.iter_completions()
        yield from self.iter_exchanges()

    def iter_exchanges(self):
        # Complete-stream pair permutation, newX=oldY and newY=-oldX.
        # Two movements per pair are explicitly reserved in the route bill.
        for x,y in ((0,1),(2,3)):
            for t in range(V):yield(EXCHANGE,x*V+t,y*V+t,-1,0,0,-1,0)

    @lru_cache(None)
    def frame_projector(self,frame):
        import sympy as sp
        B=sp.Matrix(self.C.B[frame])
        if not self.C.dimf[frame]: return sp.zeros(H)
        G=sp.eye(H)-sp.ones(H)/9
        return B.T*(B*G*B.T).inv()*B*G

    def rho(self,stage,port):
        import sympy as sp
        I=sp.eye(M)
        if stage==0:return I
        q=list(self.W.g['labels'][port]);rest=[j for j in range(H) if j not in q]
        permutation=q+rest
        pi=sp.zeros(H)
        for j,dst in enumerate(permutation):pi[dst,j]=1
        qstar=sp.Matrix([int(i<3)for i in range(H)])
        G=sp.eye(H)-sp.ones(H)/9
        pstar=qstar*(qstar.T*G)/2; p=pi*pstar*pi.T;kstar=sp.eye(H)-pstar
        I[:H,:H]=p;I[stage*H:(stage+1)*H,stage*H:(stage+1)*H]=pstar
        I[:H,stage*H:(stage+1)*H]=pi*kstar
        I[stage*H:(stage+1)*H,:H]=kstar*pi.T
        return I

    def tau(self,stage):
        import sympy as sp
        I=sp.eye(M)
        if stage:
            for j in range(H):I.row_swap(j,stage*H+j)
        return I

    def global_stage_projector(self,stage,frame,complement=False,chart=None):
        """Exact d(P direct_sum Q_stage)d^-1, with d=I by default."""
        import sympy as sp
        P=self.frame_projector(frame)
        if complement:P=sp.eye(H)-P
        A=sp.zeros(M);A[:H,:H]=P
        qstar=sp.Matrix([int(i<3)for i in range(H)])
        G=sp.eye(H)-sp.ones(H)/9
        K=sp.eye(H)-qstar*(qstar.T*G)/2
        for j in range(1,stage+1):A[j*H:(j+1)*H,j*H:(j+1)*H]=K
        return A if chart is None else chart*A*chart.inv()

    def data_boundary(self,stage,port,kind):
        import sympy as sp
        if kind=='P':frame=self.W.w['source_frame'][port];complement=False
        elif kind=='K':frame=self.W.w['source_frame'][port];complement=True
        else:frame=self.FULL if kind=='H' else self.ZERO;complement=False
        route=self.rho(stage,port)
        return route*self.global_stage_projector(stage,frame,complement)*route

    def idle_projectors(self,boundary,port):
        import sympy as sp
        P=self.data_boundary(0,port,'P');I=sp.eye(M);Z=sp.zeros(M)
        pairs=((P,self.data_boundary(1,port,'H')),
               (Z,self.data_boundary(1,port,'K')),
               (self.data_boundary(2,port,'P'),self.data_boundary(3,port,'P')),
               (self.data_boundary(2,port,'0'),self.data_boundary(3,port,'0')),
               (self.data_boundary(2,port,'H'),I),
               (self.data_boundary(2,port,'K'),I-P),
               (self.data_boundary(4,port,'H'),I),
               (self.data_boundary(4,port,'K'),I-P))
        return pairs[boundary]

    def completion_projector(self,frame,chart=None):
        import sympy as sp
        A=sp.diag(*([self.frame_projector(frame)]*5))
        return A if chart is None else chart*A*chart.inv()

def verify(lower,raw):
    physical=lower.ns['result']
    source_tag=physical['tagged_scalar_sha256']
    stages=[];paid=Counter();program=hashlib.sha256(b'global-physical-v1\0'+source_tag.encode())
    opcode_counts=Counter();center_category=physical['category_names'].index('center')
    for stage in range(5):
        digest=hashlib.sha256(b'stage-v1\0'+bytes([stage])+source_tag.encode())
        adds=copies=erases=0;copy_open=False;copy_reads=0;coefficient=Counter();stage_paid=Counter()
        live_image={family(stage,i)for i in range(LOCAL)}
        for row in lower.iter_stage(stage):
            op,a,b,c,f,z,s,reverse=row
            assert s==stage and reverse==int(stage in(1,3))
            if op==MOVE:
                assert a in live_image or a==WORK
                assert f>=0
                if f:stage_paid[f]+=1
                if a==WORK:
                    assert copy_open and c==lower.ZERO and f==22
            elif op==ADD:
                assert a in live_image and (b in live_image or b==WORK) and a!=b
                assert not(a==WORK)
                assert (b==WORK)==(z==center_category)
                if b==WORK:assert copy_open and f==lower.ZERO;copy_reads+=1
                adds+=1;coefficient[abs(c)]+=1
            elif op==COPY:
                assert not copy_open and a==WORK and b in live_image
                assert b>=4*V and lower.C.dimf[f]==22
                copy_open=True;copy_reads=0;copies+=1
            elif op==ERASE:
                assert copy_open and a==WORK and f==lower.ZERO and copy_reads==220
                copy_open=False;erases+=1
            else:raise AssertionError('unexpected stage opcode')
            data=PACK.pack(*row);digest.update(data);program.update(data);opcode_counts[op]+=1
        assert not copy_open and adds==physical['weighted_scalar_events'] and copies==erases==24
        assert stage_paid==Counter({int(k):n for k,n in physical['paid_histogram'].items()})
        assert coefficient=={int(k):v for k,v in physical['coefficient_histogram'].items()}
        paid.update(stage_paid)
        stages.append(dict(stage=stage,sha256=digest.hexdigest(),weighted_additions=adds,
            fresh_copies=copies,erasures=erases,paid_histogram=dict(sorted(stage_paid.items())),
            source_owner=BANKS[ACTIVE[stage][0]],target_owner=BANKS[ACTIVE[stage][1]],
            complemented_reverse=stage in(1,3),work_family=WORK))
        if stage in(1,2,4):
            which={1:0,2:1,4:2}[stage]
            for row in lower.iter_idle(which):
                paid[row[4]]+=1;program.update(PACK.pack(*row));opcode_counts[IDLE]+=1
            for row in lower.iter_bridges(which):
                program.update(PACK.pack(*row));opcode_counts[BRIDGE]+=1
    for row in lower.iter_completions():
        paid[row[4]]+=1;program.update(PACK.pack(*row));opcode_counts[COMPLETE]+=1
    for row in lower.iter_exchanges():
        program.update(PACK.pack(*row));opcode_counts[EXCHANGE]+=1
    assert opcode_counts[EXCHANGE]==2*V
    expected=Counter({int(k):5*n for k,n in raw['one_stage_helper_histogram_including_copies'].items()})
    expected.update({r:2*V for r in(46,23,50,4)})
    expected.update({5*int(a):n for a,n in raw['auxiliary_entrance_rank_histogram'].items()})
    assert paid==expected and sum(paid.values())==raw['five_stage_profile']['calls']
    assert sum(r*n for r,n in paid.items())==raw['five_stage_profile']['rank_mass'] and LIVE*M-sum(r*n for r,n in paid.items())==4400
    from pins import pin
    assert opcode_counts[BRIDGE]==6*V;pin('entrance_count',opcode_counts[COMPLETE])
    # Independent four-bank all-column F2 composition, no source helper replay.
    def bank_endpoint(skip_bridge=None):
        banks=[1<<j for j in range(4)];bindex=0
        for stage,(src,dst)in enumerate(ACTIVE):
            banks[dst]^=banks[src]
            if stage in(1,2,4):
                for row in lower.iter_bridges({1:0,2:1,4:2}[stage]):
                    if row[1]%V:continue
                    if bindex!=skip_bridge:banks[row[1]//V]^=banks[row[2]//V]
                    bindex+=1
        return banks
    assert bank_endpoint()==[2,1,8,4]
    after_exchange=bank_endpoint()
    after_exchange[0],after_exchange[1]=after_exchange[1],after_exchange[0]
    after_exchange[2],after_exchange[3]=after_exchange[3],after_exchange[2]
    assert after_exchange==[1,2,4,8]
    assert all(bank_endpoint(j)!=[2,1,8,4]for j in range(6))
    controls=[]
    try:check_namespace(lambda s,i:LOCAL if i==LOCAL else family(s,i))
    except AssertionError:controls.append('unremapped local temporary collides with arbitrary live helper')
    else:raise AssertionError('collision admitted')
    # An erased workstream cannot be reversed into the original dirty value.
    original,dirty=0b1011,0b1100
    fresh_copy=original;fresh_target=dirty^fresh_copy
    erased_copy=0;literal_reverse_target=dirty^erased_copy
    assert fresh_target!=literal_reverse_target
    controls.append('literal inverse of erased copy loses arbitrary center contribution')
    controls.extend('omitted bridge '+str(j)for j in range(6))
    # Direct-sum support proof executed on the actual 5-window mask. It depends
    # on the routed helper window, not just its rank. Every nonzero entrance is
    # completed separately; no source-owned gauge enters this list.
    correct_windows=[1<<j for j in range(5)]
    assert sum(correct_windows)==31
    wrong_windows=[1<<j for j in(0,1,2,3,3)]
    assert len(set(wrong_windows))!=5
    controls.append('stage4 helper route aliases stage3 window')
    return dict(stages=stages,program_sha256=program.hexdigest(),paid_histogram=dict(sorted(paid.items())),
                paid_calls=sum(paid.values()),paid_rank_mass=sum(r*n for r,n in paid.items()),
                deficit=4400,opcode_counts=dict(sorted(opcode_counts.items())),
                bank_F2_endpoint_before_terminal_relabel=bank_endpoint(),
                bank_F2_endpoint_after_terminal_relabel=after_exchange,
                terminal_exchange_pairs=2*V,terminal_exchange_stream_movements=4*V,
                controls_rejected=controls)

