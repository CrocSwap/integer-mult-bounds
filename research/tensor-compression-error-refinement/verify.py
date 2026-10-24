"""Actual source-extracted compression suffix; no numerical owner replaced."""
import argparse
import ast
from contextlib import ExitStack
from hashlib import sha256
import json
from pathlib import Path
import sys
from unittest.mock import patch
from fractions import Fraction as Q
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from model import need,records,core,axis,recurrence,inward


def sources():
    rows=[r for r in json.loads((HERE/'SOURCES.json').read_text())['files'] if r['usage']=='input']
    for row in rows:
        need(sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'exact source bytes: '+row['path'])
    return len(rows)


def suffix(engine):
    """Extract exact existing statements after chirp and before restoration."""
    source=Path(engine.__file__).read_text()
    tree=ast.parse(source)
    tensor=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Tensor')
    run=next(n for n in tensor.body if isinstance(n,ast.FunctionDef) and n.name=='run')
    groups=[n.body for n in ast.walk(run) if isinstance(n,ast.Try)]
    group=next(body for body in groups if any(isinstance(n,ast.Expr) and ast.unparse(n).startswith('self.call(self.chirp,') for n in body))
    start=next(i for i,n in enumerate(group) if isinstance(n,ast.Expr) and ast.unparse(n).startswith('self.call(self.chirp,'))+2
    end=next(i for i,n in enumerate(group) if isinstance(n,ast.Expr) and ast.unparse(n).startswith('self.boundary(self.current,'))
    selected=group[start:end]
    need(len(selected)==6 and ast.unparse(selected[0])=='self.regroup(plan, rows, False)' and ast.unparse(selected[-1])=='self.natural_padding(plan, rows, True)', 'exact six-statement compression suffix')
    function=ast.parse('def extracted(self, book, plan, rows, catalogue):\n    pass').body[0]
    function.body=selected
    module=ast.fix_missing_locations(ast.Module(body=[function],type_ignores=[]))
    env=dict(vars(engine));exec(compile(module,'<authenticated Tensor.run compression suffix>','exec'),env)
    return env['extracted'],sha256(ast.dump(module,include_attributes=False).encode()).hexdigest()


def physical():
    sys.path.insert(0,str(ROOT/'research/physical-gaussian-tensor'))
    from tensor_sources import opened
    with opened():
        import tensor_engine as engine
        from tensor_catalogue import Catalogue
        from tensor_fixture import prepared_catalogue,finite_chirp,literal_native
        from tensor_router import FullRouter
        from tensor_model import catalogue,compression_page,Cursor
        from tensor_records import bounded_record_io
        from cardinal_counts import Count
        from check_composed import encode
        from check_support import no_decode
        from expansion_check_block import packet_bytes
        from ring_check_words import tape
        from router_metadata import owned
        from compact_counts import append_bits
        from session import initialize_marker,erase_marker,sealed_constructors
        from words import BLANK
        run,code_hash=suffix(engine)
        raw=prepared_catalogue();header,profiles=catalogue(raw)
        need(header['sources']==[7,7] and header['p']==48 and header['P']==80,'retained calibration')
        B=1<<48
        values=[(((19*i+7)%101-50)*(B//128),((31*i+13)%97-48)*(B//128)) for i in range(64)]
        need(all(1000000*(a*a+b*b)<=601**2*B*B for a,b in values),'declared post-chirp disk')
        expected,shape=values,(8,8)
        for i,profile in enumerate(profiles):expected,shape=axis(expected,shape,i,profile)
        need(shape==(7,7),'independent complete source box')
        machine=engine.Tensor(finite_chirp(),FullRouter(literal_native()))
        prepared,payload=tape(raw),tape(encode(values,50))
        core_owner=machine.lines.compression
        original_core=core_owner.run
        core_calls=[]; stages=[]
        def capture(port):
            head=port.head;raw=packet_bytes(port)
            while port.head<head:port.step(1)
            while port.head>head:port.step(-1)
            return raw
        def observe_core(page,source):
            page_raw,source_raw=capture(page),capture(source)
            returned=original_core(page,source)
            raw_output=capture(returned)
            description=compression_page(Cursor(page_raw))
            reference=core(records(source_raw),description)
            need(records(raw_output)==reference,'actual Core equals independent signed staged reference')
            need(capture(page)==page_raw and capture(source)==source_raw and core_owner.closed and not core_owner.pool.live,'Core preserves borrowed pages and closes scratch')
            core_calls.append((sha256(page_raw).hexdigest(),sha256(source_raw).hexdigest(),sha256(raw_output).hexdigest()))
            return returned
        original_lines,original_halo,original_assemble=machine.apply_lines,machine.halo,machine.assemble
        def observed(label,method):
            def call(*args,**kwargs):
                method(*args,**kwargs)
                data=records(capture(machine.current))
                stages.append({'stage':label,'records':len(data),'norm2':max(a*a+b*b for a,b in data),'sha256':sha256(capture(machine.current)).hexdigest()})
            return call
        machine.last_counts=dict(natural_padding=0,gathers=0,halos=0,expansion_axes=0,compression_axes=0,assembled_axes=0,chirps=0)
        book=None
        with owned(Count.literal(1)) as (rows,):
            row_saved=capture(rows.tape)
            for t in machine.pool.tapes:initialize_marker(t)
            machine.closed=False
            try:
                with ExitStack() as stack:
                    stack.enter_context(patch.object(core_owner,'run',observe_core))
                    for name,method in [('apply_lines',original_lines),('halo',original_halo),('assemble',original_assemble)]:
                        stack.enter_context(patch.object(machine,name,observed(name,method)))
                    with bounded_record_io(),sealed_constructors(),machine.scope.installed(),no_decode():
                        book=Catalogue(prepared,machine.pool.acquire);plan=book.plan
                        machine.current,machine.following=machine.pool.acquire(),machine.pool.acquire()
                        append_bits(payload,machine.current);machine.current.rewind()
                        run(machine,book,plan,rows,prepared)
                        actual=capture(machine.current)
                        machine.idle()
                need(actual==encode(expected,50),'complete actual suffix equals independent natural-coordinate reference')
                need(capture(prepared)==raw and capture(payload)==encode(values,50) and capture(rows.tape)==row_saved,'borrowed suffix inputs unchanged')
            finally:
                for t in (machine.current,machine.following):
                    if t is not None:t.clear()
                machine.current=machine.following=None
                if book is not None:book.close()
                machine.pool.empty()
                for t in machine.pool.tapes:erase_marker(t)
                machine.closed=True
                prepared.rewind();payload.rewind();rows.rewind()
        need(not machine.pool.live and all(t.head==1 and all(x==BLANK for x in t.cells) for t in machine.pool.tapes),'suffix owned scratch erased')
        prepared.clear();payload.clear();erase_marker(prepared);erase_marker(payload)
        need([s['stage'] for s in stages]==['halo','halo','apply_lines','apply_lines','assemble','assemble'],'actual all-halos-first stage chronology')
        need(machine.last_counts==dict(natural_padding=2,gathers=2,halos=2,expansion_axes=0,compression_axes=2,assembled_axes=2,chirps=0),'full actual suffix counts')
        transposed=[expected[j*7+i] for i in range(7) for j in range(7)]
        need(transposed!=expected,'wrong final natural layout distinguished')
        # Premature restriction discards original target coordinates; repeated
        # endpoint padding is an explicitly wrong replacement for those halos.
        first,_=axis(values,(8,8),0,profiles[0])
        wrong=[first[i*8+j] if i<7 else (0,0) for i in range(8) for j in range(8)]
        wrong,_=axis(wrong,(8,8),0,profiles[0]);wrong,_=axis(wrong,(7,8),1,profiles[1])
        need(wrong!=expected,'premature restricted-axis reuse distinguished')
        return dict(core_calls=len(core_calls),core_trace_sha256=sha256(json.dumps(core_calls).encode()).hexdigest(),stages=stages,counts=machine.last_counts,output_sha256=sha256(actual).hexdigest(),catalogue_sha256=sha256(raw).hexdigest(),source_suffix_ast_sha256=code_hash,scope='actual extracted post-chirp/pre-restoration suffix; boundary-only finite pages, no production accuracy claim',controls=['transposed final layout','premature restricted-axis reuse'])


def algebra():
    for D in (1,2,3,17,100):
        for p in (101,102,16384):
            delta=Q(2,1<<p);initial=Q(601,1000);error=Q(1,256)
            radius,err=recurrence(initial,error,delta,D)
            weight=Q(1,8**D)
            need(radius==weight*initial+delta*(1-weight)*Q(8,7) and err==weight*error+delta*(1-weight)*Q(8,7),'exact domain/error recurrence')
    # Inward rounding is not Lipschitz: neighboring inputs across a grid jump.
    need(inward(127,7)==0 and inward(128,7)==1
         and abs(inward(128,7)-inward(127,7))>Q(1,128),
         'nonlinear rounded-map Lipschitz inference rejected')
    return {'recurrence_cases':15,'local_delta':'inherited strict <2h; finite reduced-halo output does not certify it'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    result=dict(status='PASS_COMPRESSION_SUFFIX',inputs=sources(),algebra=algebra(),physical=physical())
    p=HERE/'RESULT.json'
    if args.write:p.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(json.dumps(result,sort_keys=True)==json.dumps(json.loads(p.read_text()),sort_keys=True),'typed complete suffix receipt')
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
