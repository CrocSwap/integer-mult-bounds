#!/usr/bin/env python3
"""Complete source transport against independent coordinate and invoice oracles."""
import argparse,hashlib,itertools,json,pathlib,shutil,sys,tempfile
from fractions import Fraction
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from bounds import invoice

def need(ok,why):
    if not ok:raise ValueError(why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def authenticate():
    manifest=json.loads((HERE/'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage']=='input':need(sha((ROOT/row['path']).read_bytes())==row['sha256'],'source hash '+row['path'])
    for row in manifest['retained']:need(sha((HERE/row['path']).read_bytes())==row['sha256'],'retained hash '+row['path'])
    return sum(row['usage']=='input'for row in manifest['files'])
def load_source():
    sys.path.insert(0,str(ROOT/'research/selected-bit-physical-caller'))
    import loader
    projection=tempfile.TemporaryDirectory(prefix='r437-transport-source-')
    for row in json.loads((loader.CALLER/'SOURCES.json').read_text())['files']:
        if row['usage']!='input':continue
        target=pathlib.Path(projection.name)/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
        source=HERE/'retained/selected-result.json'if row['path']=='certificates/selected-result.json'else ROOT/row['path']
        shutil.copyfile(source,target)
    loader.REPOSITORY=pathlib.Path(projection.name);loader.compatibility_controls();loader.activate()
    return projection

def run_case(d,w,O,F,mutation=None):
    from words import Arena,Ring,BLANK
    from records import Tape
    from cardinal_counts import Count
    from low_codes import LowCodes
    from directory import Context
    from routes import compile_route
    from macro_machine import Machine
    from scratch_pool import ScratchPool
    import routes,selection
    q=3;M=q**w;H=q**((w-1)*d*d);b=M.bit_length()+1
    lows=[]
    for flat in itertools.product(range(q),repeat=d*d):
        determinant=flat[0] if d==1 else flat[0]*flat[3]-flat[1]*flat[2]
        if determinant%q:lows.append(tuple(tuple(flat[i*d+j]for j in range(d))for i in range(d)))
    codes=LowCodes(q,d);need(codes.size==len(lows),'independent complete GL count')
    low=tuple(tuple(int(i==j)for j in range(d))for i in range(d))
    chart=tuple(tuple(Fraction(2 if i==0 else 1)if i==j else Fraction(0)for j in range(d))for i in range(d))
    inverse=tuple(tuple(Fraction(1,2)if i==j==0 else Fraction(int(i==j))for j in range(d))for i in range(d))
    target=tuple(tuple((2 if j==0 else 1)*low[i][j]%q for j in range(d))for i in range(d))
    ordinal=lows.index(low);need(codes.rank(low)==ordinal,'independent low ordinal')
    forward=compile_route(low,chart,codes);backward=compile_route(target,inverse,codes)
    arena=Arena(b,256);modulus=arena.input(M);ring=Ring(modulus);context=Context(ring,codes)
    def tape(bits):
        t=Tape()
        for bit in bits:t.append(bit)
        t.rewind();return t
    def body(t):return bytes(t.cells[1:]).rstrip(bytes([BLANK]))
    def actions(t):return t.meter.reads+t.meter.writes+t.meter.moves
    old,fibre=Count.literal(O),Count.literal(F)
    # Old prefixes0/1 deliberately have identical bytes, but remain separate.
    V=O*len(lows)*H*F;period=len(lows)*H*F
    raw=bytes(((i%period)*13^((i%period)>>2)^((i%period)>>5)^0x53)&1 for i in range(V))
    runtime=object.__new__(Machine);runtime.context=context
    runtime.roles={('family',0):tape(raw),('stage',0):tape([1]*(O*H*F)),
                   'old_count':old.tape,'fibre':fibre.tape,'untouched':tape([1,0,1,1,0,0,1])}
    pool=ScratchPool(q*q+128)
    template=(bytes(arena.template.cells),arena.template.head)
    protected={slot:(bytes(arena.words[slot].cells),arena.words[slot].head)for slot in arena.live}
    borrowed={name:(body(runtime.roles[name]),runtime.roles[name].head)for name in ('old_count','fibre','untouched')}
    physical=[*pool.tapes,*runtime.roles.values()];start=sum(map(actions,physical));wordstart=actions(arena)
    original_key=routes.copy_key;original_commit=Machine.commit;original_scatter=selection.scatter
    if mutation=='wrong stable bit':
        def wrong_key(*args,**kwargs):
            bit=original_key(*args,**kwargs)
            return 1-bit if len(args)>3 or kwargs.get('selected')is not None else bit
        routes.copy_key=wrong_key
    if mutation=='lost owner install':
        def lost_commit(self,result,label):result.clear()
        Machine.commit=lost_commit
    if mutation=='missing lease retirement':
        def keep_commit(self,result,label):
            # Literal source commit with its final Lease.clear omitted.
            target=self.tape(label);target.clear()
            from directory import append_tape
            append_tape(result,target);target.rewind()
        Machine.commit=keep_commit
    try:
        with pool.install():
            runtime.dispatch(('gather_route',('stage',0),0,low,forward));pool.empty()
            expected=bytearray(O*H*F);cap=q**(w-1);mapping=[]
            for o in range(O):
                for h,digits in enumerate(itertools.product(range(cap),repeat=d*d)):
                    mapped=[]
                    for i in range(d):
                        for j in range(d):
                            value=((low[i][j]+q*digits[i*d+j])*(2 if j==0 else 1))%M
                            mapped.append((value-target[i][j])//q)
                    index=0
                    for digit in mapped:index=index*cap+digit
                    mapping.append(index)
                    expected[(o*H+index)*F:(o*H+index+1)*F]=raw[((o*len(lows)+ordinal)*H+h)*F:((o*len(lows)+ordinal)*H+h+1)*F]
            need(body(runtime.roles[('stage',0)])==expected,'independent routed high-carry endpoint')
            # Supplied complete stage-map fixture: position-dependent bit flips.
            # Its actions are measured separately and removed from transport.
            stage=runtime.roles[('stage',0)];before=actions(stage);stage.rewind()
            for i in range(O*H*F):stage.write(stage.read()^((i*7^(i>>2)^1)&1));stage.step(1)
            stage.rewind();child_actions=actions(stage)-before
            runtime.dispatch(('route_scatter',('stage',0),0,low,backward));pool.empty()
            final=bytearray(raw)
            for o in range(O):
                for h in range(H):
                    for f in range(F):
                        i=(o*H+mapping[o*H+h])*F+f
                        final[((o*len(lows)+ordinal)*H+h)*F+f]^=(i*7^(i>>2)^1)&1
            need(body(runtime.roles[('family',0)])==final,'complete original-owner scatter and unselected rows')
        need(arena.live==set(protected),'numerical live restoration')
        need((bytes(arena.template.cells),arena.template.head)==template,'numeric template restoration')
        need(all(word.head==1 and all(bit==BLANK for bit in word.cells[1:]) for word in arena.words if word.slot not in protected),'all retired numeric backing erased')
        need(all((bytes(arena.words[s].cells),arena.words[s].head)==v for s,v in protected.items()),'borrowed numeric bytes/heads')
        need(all((body(runtime.roles[n]),runtime.roles[n].head)==v for n,v in borrowed.items()),'borrowed record bytes/heads')
        need(all(t.head==1 for t in physical)and all(not body(t)for t in pool.tapes),'all role heads and pool erasure')
        bill=invoice(q,d,b,O,len(lows),H,F,2,arena.capacity)
        record=sum(map(actions,physical))-start-child_actions;numeric=actions(arena)-wordstart
        backing=sum(len(t.cells)for t in physical)+sum(len(x.cells)for x in [*arena.words,arena.template])
        need(record+numeric<=bill['completed_roundtrip_actions'],'proved complete action bound')
        need(backing<=bill['retained_cells']and pool.peak<=bill['maximum_live_scratch_leases'],'proved complete retained backing/roles')
        return dict(dimension=d,w=w,old_prefixes=O,fibre_bits=F,low_classes=len(lows),highs=H,payload_bits=V,
            record_actions=record,word_actions=numeric,stage_map_actions_excluded=child_actions,
            retained_cells=backing,retained_pool_cells=sum(len(t.cells)for t in pool.tapes),
            pool_capacity=len(pool.tapes),peak_scratch=pool.peak,leases=pool.allocations,
            endpoint_sha256=sha(body(runtime.roles[('family',0)])),invoice=bill)
    finally:
        routes.copy_key=original_key;Machine.commit=original_commit;selection.scatter=original_scatter

def run():
    inputs=authenticate()
    with load_source():
        cases=[run_case(*args)for args in [(1,1,3,2),(1,2,3,2),(1,3,2,3),(2,2,2,3)]]
        rejected=[]
        for label in ['wrong stable bit','lost owner install','missing lease retirement']:
            try:run_case(1,2,3,2,label)
            except ValueError as e:rejected.append(dict(mutation=label,error=str(e)))
            else:raise ValueError('mutation accepted '+label)
    return dict(status='PASS_COMPLETE_TRANSPORT_TARIFF',live_inputs=inputs,cases=cases,rejected=rejected,
        scope='Complete reduced source transport and written fixed-compiled-control cell-action/backing bounds; no original-root or full caller admission.')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    result=run()
    if args.write:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(json.dumps(result,sort_keys=True)==json.dumps(json.loads((HERE/'RESULT.json').read_text()),sort_keys=True),'typed deterministic receipt')
    print(result['status'])
if __name__=='__main__':main()
