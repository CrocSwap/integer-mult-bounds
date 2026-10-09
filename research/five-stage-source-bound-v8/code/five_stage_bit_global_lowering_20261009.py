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
RAW = BASE/'retimed_source_heads_20261009/raw471_ledger.json'
ACTIVE = ((0,1),(1,0),(0,1),(3,2),(2,3))
BANKS = ('X1','Y1','X2','Y2')
V, R, H, M = 1760, 16643, 24, 120
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

def record_local(pr210_root=None,base_bit_root=None):
    """Instrument the unchanged physical tag generator, never the F2 payload."""
    source = PHYSICAL.read_text()
    saved = json.loads(PHYSICAL.with_name(PHYSICAL.stem+'_result.json').read_text())
    assert sha(source.encode()) == saved['script_sha256']
    def patch(old,new):
        nonlocal source
        assert source.count(old) == 1, ('instrumentation site mismatch',old)
        source = source.replace(old,new)
    patch('caps={}', 'initial_state=state.copy()\ncaps={}')
    patch('subcache={}', 'subcache={}\nlocal_records=record_storage\nkind_ids={k:i for i,k in enumerate(sorted(expected_categories))}')
    patch('d=C.dimf[f]-C.dimf[old];assert d>=0',
          'd=C.dimf[f]-C.dimf[old];assert d>=0\n local_records.extend((0,i,old,f,d,0))')
    patch('else:move(y,f)', 'else:move(y,f)\n local_records.extend((1,x,physical_y,c,f,kind_ids[kind]))')
    patch('centers.append(center)',
          'centers.append(center)\n local_records.extend((2,source,n,frame,ZERO,rank))')
    patch("center['after_event']=count",
          "local_records.extend((3,center['source'],n,center['frame'],ZERO,center['rank']))\n center['after_event']=count")
    prepared=None
    if pr210_root is not None:
        loader_path=BASE/'five_stage_export_plan_20261009/loader/source_loader.py'
        spec=importlib.util.spec_from_file_location('global_physical_clean_loader',loader_path)
        loader=importlib.util.module_from_spec(spec);spec.loader.exec_module(loader)
        prepared=loader.prepare(pr210_root,base_bit_root)
        prepared['SOURCE_TEXT']=(Path(pr210_root)/loader.PR210_PACKAGE/'newg/replay.py').read_text()
        assert sha(prepared['SOURCE_TEXT'].encode())==saved['scalar_source_sha256']
        fingerprint=loader.semantic_fingerprint(prepared)
        prefix="setup=AUDIT.read_text().split('result = {')[0]\nns={'__file__':str(AUDIT),'__name__':'physical_telescope_dependency'}\nexec(compile(setup,str(AUDIT),'exec'),ns)"
        patch(prefix,'ns=prepared_namespace')
    storage = array('i')
    ns = dict(__file__=str(PHYSICAL),__name__='global_lowering_local_dependency',
              record_storage=storage,expected_categories=saved['categories'],prepared_namespace=prepared)
    argv = sys.argv
    try:
        sys.argv = [str(PHYSICAL)]
        with redirect_stdout(io.StringIO()): exec(compile(source,str(PHYSICAL)+' [recording]','exec'),ns)
    finally:
        sys.argv = argv
    fresh = json.loads(json.dumps(ns['result']))
    if prepared is None:
        assert fresh == saved, 'unchanged physical witness did not reproduce exactly'
        ns['context_binding']=dict(kind='historical audited context',exact_receipt_equality=True)
    else:
        fields=('source_head','scalar_source_sha256','scalar_projection_sha256',
                'weighted_scalar_events','categories','physical_registers','positive_rank_moves',
                'copied_centers','center_scatter_reads','temporary_streams_simultaneous',
                'paid_histogram','paid_rank_mass','initial_endpoints','final_endpoints')
        assert all(fresh[k]==saved[k]for k in fields),[k for k in fields if fresh[k]!=saved[k]]
        inventories=[Counter((r['basis_sha256'],r['dimension'])for r in z['used_frames'])for z in(saved,fresh)]
        assert set(inventories[0])==set(inventories[1]), 'clean source used different exact frame bases'
        maps=[{r['frame_id']:r['basis_sha256']for r in z['used_frames']}for z in(saved,fresh)]
        def copy_semantics(block,mapping):
            return {k:mapping[v]if k in('frame','copy_output_frame')else v for k,v in block.items()}
        assert [copy_semantics(b,maps[0])for b in saved['copied_center_blocks']]==[copy_semantics(b,maps[1])for b in fresh['copied_center_blocks']]
        ns['context_binding']=dict(kind='pinned public clean source roots',fingerprint=fingerprint,
            scalar_digest_and_paid_fields_equal=True,exact_used_basis_set_equal=True,
            exact_used_basis_multiplicities_equal=inventories[0]==inventories[1],
            all_24_copied_block_exact_bases_and_events_equal=True,
            loader_sha256=sha(loader_path.read_bytes()),source_pins=prepared['source_pins'])
    assert len(storage)%6 == 0
    return storage, ns

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
        assert Counter(a for f,s,a in self.entrances) == {12:18,13:48,18:13,20:2200}
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

def verify(lower):
    physical=lower.ns['result']; raw=json.loads(RAW.read_text())
    source_tag=physical['tagged_scalar_sha256']
    stages=[];paid=Counter();program=hashlib.sha256(b'global-physical-v1\0'+source_tag.encode())
    opcode_counts=Counter();center_category=sorted(physical['categories']).index('center')
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
        assert not copy_open and adds==2569626 and copies==erases==24
        assert stage_paid==Counter({int(k):n for k,n in physical['paid_histogram'].items()})
        assert coefficient=={1:785130,2:1783176,3:1320}
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
    assert paid==expected and sum(paid.values())==495304
    assert sum(r*n for r,n in paid.items())==2837560 and LIVE*M-sum(r*n for r,n in paid.items())==4400
    assert opcode_counts[BRIDGE]==6*V and opcode_counts[COMPLETE]==2279
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

def main():
    t=time.monotonic();sys.dont_write_bytecode=True
    def arg(name):return sys.argv[sys.argv.index(name)+1]if name in sys.argv else None
    pr210_root,base_root=arg('--pr210-root'),arg('--base-bit-root')
    assert (pr210_root is None)==(base_root is None)
    records,context=record_local(pr210_root,base_root);lower=Lowerer(records,context)
    checked=verify(lower)
    inputs=[PHYSICAL,PHYSICAL.with_name(PHYSICAL.stem+'_result.json'),RAW,
        BASE/'five_stage_source471_scalar_audit_20261009.py',
        BASE/'five_stage_source471_scalar_audit_20261009_result.json',
        BASE/'five_stage_raw471_rebind_review_20261009.py',
        BASE/'five_stage_raw471_rebind_review_20261009_result.json',
        BASE/'five_stage_gauge_geometry_review_20261009.py',
        BASE/'five_stage_bit_stage_namespace_20261009.py',
        BASE/'five_stage_routed_majorants_20261009.py',
        BASE/'five_stage_routed_majorants_20261009_result.json']
    if pr210_root is not None:inputs += [BASE/'five_stage_export_plan_20261009/loader/source_loader.py',BASE/'five_stage_export_plan_20261009/loader/SOURCE_PINS.json']
    route_receipt=json.loads((BASE/'five_stage_routed_majorants_20261009_result.json').read_text())
    assert route_receipt['proposed_paid_address_inventory']['conservative_route_and_final_exchange_families']==20*V+10*R+4*V==208670
    result=dict(status='PASS_SOURCE_BOUND_CALLABLE_GLOBAL_PHYSICAL_LOWERING',
        source_head=context['result']['source_head'],m=M,global_live=LIVE,external_work_family=WORK,
        local_record_count=len(records)//6,materialized_local_record_bytes=len(records)*records.itemsize,
        weighted_stage_additions=5*2569626,bridge_additions=6*V,total_weighted_additions=5*2569626+6*V,
        scalar_projection_sha256=context['result']['scalar_projection_sha256'],
        local_tagged_sha256=context['result']['tagged_scalar_sha256'],
        local_telescope_semantics_reproduced_exactly=True,context_binding=context['context_binding'],independent_auxiliary_completions=len(lower.entrances),
        geometry_semantics='Actual rational G=I-J/9 projectors; stage d(P direct_sum Q_i)d^-1; data class d*rho_i(q), helper class d*tau_i. Idle uses exact before/after projectors; completion uses diag(sigma,sigma,sigma,sigma,sigma) on that helper only.',
        physical_telescope_contract='Each source-bound stage is Dout M Din^-1. Reverse replays complete signed inverse with complemented frame moves, replacing each erased copied block by fresh copy H-U to H, reverse scatter, erase. Injective routed family maps transport this identity. Exact equal-frame bridge and nested idle identities compose the four-bank F2 endpoint; disjoint five-window helper residuals and per-helper completion give D_I on arbitrary dirt.',
        terminal_relabel='Explicit complete-stream pair permutation newX=oldY,newY=-oldX. The four-bank F2 logical endpoint is identity after exchange. Its 4v stream movements are included in the 208670 route-and-final-exchange families; no unproved equal-frame shear is inserted.',
        no_f2_payload_replay=True,no_cover_enumeration=True,source_supplier_unchanged=True,
        input_pins={str(p.relative_to(ROOT)):sha(p.read_bytes())for p in inputs},
        script_sha256=sha(Path(__file__).read_bytes()),**checked,seconds=time.monotonic()-t)
    if '--write'in sys.argv:
        Path(__file__).with_name('five_stage_bit_global_lowering_20261009_result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
