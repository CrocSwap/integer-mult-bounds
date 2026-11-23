"""Observe real #8042 packet boundaries without replacing its payload operations."""
from array import array
from collections import Counter
from contextlib import contextmanager, ExitStack
from fractions import Fraction
from functools import wraps
from hashlib import sha256
from io import BytesIO
from itertools import product
from math import prod
from pathlib import Path
import argparse
import inspect
import json
import sys
from textwrap import dedent
from types import FunctionType


def need(ok, reason):
    if not ok:
        raise AssertionError(reason)


def peek(tape, start=0, end=None):
    at=tape.tell();tape.seek(start)
    data=tape.read() if end is None else tape.read(end-start)
    tape.seek(at)
    return data


def aliases(old,new):
    changed=[]
    for mod in tuple(sys.modules.values()):
        if mod is None or not hasattr(mod,'__dict__'):
            continue
        for name,value in tuple(vars(mod).items()):
            if value is old:
                setattr(mod,name,new);changed.append((mod,name))
    return changed


class Audit:
    def __init__(self):
        self.work=[];self.work_peak=0;self.edges=[];self.packet=None
        self.packets=[];self.routes=[];self.pipelines=[];self.restores=[]
        self.prior_calls=0;self.baseline=None;self.rejected=[]
        self.weighted_depth=0;self.max_weighted_depth=0

    def bind(self):
        import growing_binary,streaming_routes,five_exchange,same_order_body
        original=streaming_routes.work_tapes
        @contextmanager
        def observed_work(count):
            with original(count) as files:
                token=(id(files),count);self.work.append(token)
                self.work_peak=max(self.work_peak,sum(n for _,n in self.work))
                try:yield files
                finally:need(self.work.pop()==token,'non-LIFO temporary scope')
        self.restores.append((original,aliases(original,observed_work)))

        original_weighted=same_order_body.SameOrderBody.weighted
        @wraps(original_weighted)
        def weighted(core,source,target,**shape):
            need(not self.work,'transient scratch crosses same-stage call')
            v=shape['available']*shape['older']*core.atom**(2*shape['atoms'])*shape['gap']*shape['suffix']
            p=self.packet;a=core.arena
            tops=(a.pending.top,a.answers.top)
            if p is not None:
                need(tops==p['tops'],'same-stage sibling changed pending/answer markers')
                need(v==p['length'],'high or spectator volume lost')
            pages={str(k):[(q.base,q.size) for q in h.frames] for k,h in a.heads.items() if h.frames}
            self.weighted_depth+=1
            self.max_weighted_depth=max(self.max_weighted_depth,self.weighted_depth)
            self.edges.append({'packet':None if p is None else p['ordinal'],'volume':v,
                               'atoms':shape['atoms'],'weighted_depth':self.weighted_depth,
                               'tops':tops,'pages':pages,'work_files':0})
            try:ans=original_weighted(core,source,target,**shape)
            finally:self.weighted_depth-=1
            need((a.pending.top,a.answers.top)==tops,'child failed stack-marker return')
            return ans
        self.restore_weighted=(same_order_body.SameOrderBody,original_weighted)
        same_order_body.SameOrderBody.weighted=weighted

        original_packet=five_exchange.same_order_line
        @wraps(original_packet)
        def packet(core,source,target,**shape):
            need(self.packet is None,'unexpected covered nesting in bounded fixture')
            v=shape['unused']*shape['heights']*shape['older']*core.atom**(2*core.n*shape['f'])*shape['gap']*shape['suffix']
            a=core.arena;tops=(a.pending.top,a.answers.top)
            p0,a0,total=self.baseline
            need(tops[0]-p0+tops[1]-a0+v==total,'pending + answer + packet conservation')
            saved=(peek(a.pending.head.file,0,tops[0]),peek(a.answers.head.file,0,tops[1]))
            rec={'ordinal':len(self.packets),'length':v,'tops':tops,'highs':shape['heights'],'first_edge':len(self.edges)}
            self.packet=rec
            try:ans=original_packet(core,source,target,**shape)
            finally:self.packet=None
            rec['calls']=len(self.edges)-rec['first_edge']
            need(rec['calls'] in (1,3,5),'wrong odd same-stage itinerary')
            need(saved==(peek(a.pending.head.file,0,tops[0]),peek(a.answers.head.file,0,tops[1])),'suspended packet prefix changed')
            need((a.pending.top,a.answers.top)==tops,'packet changed parent markers')
            self.packets.append(rec)
            return ans
        self.restores.append((original_packet,aliases(original_packet,packet)))

        original_route=streaming_routes.type_route
        @wraps(original_route)
        def route(source,target,rows,types,suffix_bytes,**kw):
            si,ti=source.tell(),target.tell()
            ans=original_route(source,target,rows,types,suffix_bytes,**kw)
            volume=rows*types*suffix_bytes
            need(source.tell()-si==target.tell()-ti==volume,'incomplete full-cohort traversal')
            self.routes.append({'inverse':bool(kw.get('inverse',False)),'volume':volume,'source_span':[si,source.tell()],'target_span':[ti,target.tell()]})
            return ans
        self.restores.append((original_route,aliases(original_route,route)))

        original_pipe=growing_binary.pipe
        @wraps(original_pipe)
        def pipe(arena,kind,source,target,volume,schedule):
            self.pipelines.append((kind,volume))
            return original_pipe(arena,kind,source,target,volume,schedule)
        self.restores.append((original_pipe,aliases(original_pipe,pipe)))

    def previous(self,source,target,digits,prefix,gap,suffix):
        from streaming_routes import cold_swap_tape
        self.prior_calls+=1
        return cold_swap_tape(source,target,digits,prefix,gap,suffix)

    def unbind(self):
        cls,fn=self.restore_weighted;cls.weighted=fn
        for old,changed in reversed(self.restores):
            for mod,name in changed:setattr(mod,name,old)


def inverse2(a,q):
    (x,y),(z,w)=a;d=pow((x*w-y*z)%q,-1,q)
    return ((d*w%q,-d*y%q),(-d*z%q,d*x%q))


def native_factors(word,q):
    a=[[Fraction(1),Fraction(0)],[Fraction(0),Fraction(1)]]
    for op,i,*rest in word:
        if op=='add':
            j,c=rest;a[i]=[x+c*y for x,y in zip(a[i],a[j])]
        elif op=='scale':
            c,=rest;a[i]=[c*x for x in a[i]]
        else:
            j,=rest;a[i],a[j]=a[j],a[i]
    a=[[x.numerator*pow(x.denominator,-1,q)%q for x in row] for row in a]
    b=inverse2(a,q)
    return a[1],(b[0][1],b[1][1])


def oracle(raw,dims,maps,mod,weight):
    out=bytearray(len(raw))
    strides=[prod(dims[i+1:]) for i in range(len(dims))]
    for index,coords in enumerate(product(*(range(d) for d in dims))):
        ext,lo,hi,old,h0,h1,g,t0,t1=coords
        u,v=maps[lo,hi];a,b=weight(old,0),weight(old,1)
        delta=(v[0]*(t0-pow(a,-1,mod)*h0)+v[1]*(t1-pow(b,-1,mod)*h1))%mod
        image=(ext,lo,hi,old,(h0+a*u[0]*delta)%mod,(h1+b*u[1]*delta)%mod,g,(t0-u[0]*delta)%mod,(t1-u[1]*delta)%mod)
        dest=sum(x*s for x,s in zip(image,strides))
        out[4*dest:4*dest+4]=raw[4*index:4*index+4]
    return bytes(out)


def run_case(label,layout,direct,older,gap,unused):
    from binary_receiver import Receiver
    from factored_frames import Frame
    from quotient_route import canonical_lows,representative
    import direct_body,module_atoms,quotient_route
    audit=Audit();audit.bind()
    try:
        core=Receiver(2,layout,previous=audit.previous,direct=direct)
        mod,atom=core.modulus,core.atom
        word=(('add',0,1,Fraction(1)),('add',1,0,Fraction(1,2)),('scale',0,Fraction(-1)))
        frame=Frame(2,word,(1,));u,v=native_factors(word,mod)
        lows=[(1,0,0,1)] if direct else list(canonical_lows(2))
        highs=1 if direct else core.high
        dims=(unused,len(lows),highs,older,atom,atom,gap,atom,atom)
        data=array('I',range(1,prod(dims)+1))
        need(data.itemsize==4,'32-bit opaque records are required')
        if sys.byteorder!='little':data.byteswap()
        raw=data.tobytes();cohort=len(raw)
        left=b'left-external-guard';right=b'right-external-guard'
        source=BytesIO(left+raw+right);source.seek(len(left))
        target=BytesIO(left+bytes(cohort)+right);target.seek(len(left))
        maps={}
        for lo,low in enumerate(lows):
            for hi in range(highs):
                a=((1,0),(0,1)) if direct else representative(low,hi,2,core.digits)
                b=inverse2(a,mod)
                pu=tuple(sum(a[i][j]*u[j] for j in range(2))%mod for i in range(2))
                pv=tuple(sum(v[i]*b[i][j] for i in range(2))%mod for j in range(2))
                need(sum(x*y for x,y in zip(pu,pv))%mod==1,'oracle pairing failed')
                maps[lo,hi]=pu,pv
        def weight(old,j):return (2,5)[(old+j)%2]%mod
        with core.storage() as arena, ExitStack() as held:
            parents=[]
            for kind in ('chart-line','chart-packet','exposed-leaf','weighted','matcher','direct-coordinate'):
                for i,page in enumerate(held.enter_context(arena.frames(kind,2))):
                    value=(kind+str(i)+'/dirty-parent/').encode()
                    page.write(value);parents.append((page,value))
            pg=b'pending-parent-not-owned-by-child';ag=b'answer-parent-not-owned-by-child'
            pt=BytesIO(pg);pt.seek(len(pg));arena.pending.push_reverse(pt,len(pg))
            arena.answers.append(BytesIO(ag),len(ag))
            p0,a0=arena.pending.top,arena.answers.top
            audit.baseline=p0,a0,cohort
            core.serve_line(source,target,frame,1,unused,older,gap,4,weight)
            need((arena.pending.top,arena.answers.top)==(p0,a0),'external markers not restored')
            need(peek(arena.pending.head.file,0,p0)==pg[::-1],'pending ancestor changed')
            need(peek(arena.answers.head.file,0,a0)==ag,'answer ancestor changed')
            for page,value in parents:need(peek(page)==value,'named ancestor page changed')
            for key,head in arena.heads.items():
                live=head.frames[-1].base+head.frames[-1].size if head.frames else 0
                if key==('pending',0):live=p0
                if key==('answers',0):live=a0
                need(peek(head.file,live,head.peak)==bytes(head.peak-live),'dirty historical child tail survived')
            restored=BytesIO();arena.pending.pop_forward(restored,p0)
            need(restored.getvalue()==pg,'pending ancestor final return failed')
            restored=BytesIO();arena.answers.take_answers(0,restored)
            need(restored.getvalue()==ag,'answer ancestor final return failed')
            with arena.frames('chart-line',1):
                try:parents[0][0].write(b'!')
                except ValueError:audit.rejected.append('write through suspended parent')
                else:raise AssertionError('illegal outer write admitted')
            peaks={str(k):h.peak for k,h in arena.heads.items()}
        need(source.tell()==target.tell()==len(left)+cohort,'external head at wrong boundary')
        need(source.getvalue()==left+raw+right,'source payload changed')
        expected=oracle(raw,dims,maps,mod,weight)
        need(target.getvalue()==left+expected+right,'independent full-record oracle mismatch')
        if direct:
            need(len(audit.edges)==1,'direct route used multiple same-stage calls')
            need(sum(k=='matcher' for k,_ in audit.pipelines)==2,'one nonidentity basis route missing')
        else:
            need(len(audit.packets)==len(lows),'missing low packet')
            need([r['inverse'] for r in audit.routes]==[False,True],'missing full-cohort entrance/exit')
        from same_order_body import SameOrderBody
        audit.work.append(('forbidden',1))
        try:
            SameOrderBody.weighted(core,BytesIO(),BytesIO(),atoms=1,available=1,older=1,gap=1,suffix=1)
        except AssertionError as e:
            need('transient scratch' in str(e),'unexpected mutation rejection')
            audit.rejected.append('transient scratch across same-stage call')
        else:raise AssertionError('forbidden temporary lifetime survived')
        finally:audit.work.pop()
        result={'case':label,'records':prod(dims),'bytes':cohort,'highs_per_low':highs,
                'same_stage_calls':len(audit.edges),'max_nested_weighted_depth':audit.max_weighted_depth,
                'itineraries':dict(Counter(p['calls'] for p in audit.packets)),
                'earlier_stage_calls':audit.prior_calls,'peak_transient_files':audit.work_peak,
                'source_counts':core.last_storage,'physical_head_peaks':peaks,
                'routes':audit.routes,'packets':audit.packets,'edges':audit.edges,
                'mutations_rejected':audit.rejected,'output_sha256':sha256(expected).hexdigest()}
        print(label,prod(dims),'records',len(audit.edges),'same-stage calls',flush=True)
        return result
    finally:audit.unbind()


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--runtime',type=Path,required=True)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--full-high',action='store_true')
    cli.add_argument('--mutation',choices=('missing-inverse','lost-highs','lost-marker','dirty-tail','live-scratch'))
    args=cli.parse_args()
    sys.path.insert(0,str(args.runtime.resolve()))
    from upstream import install
    install()
    if args.mutation:
        control(args.mutation,args.output)
        return
    results=[run_case('direct-nonidentity',(1,2,0,0),True,2,2,2),
             run_case('covered-dirty-spectators',(1,1,0,0),False,2,2,2)]
    if args.full_high:
        results.append(run_case('covered-all-true-highs',(1,2,0,0),False,1,1,1))
    args.output.write_text(json.dumps({'status':'passed','cases':results},indent=2)+'\n')
    print('PASS_RETIMED_PACKET_STORAGE_AUDIT')


def control(name,output):
    import five_exchange,receiver,stack_tapes
    # Each mutation changes one actual pinned operation in memory. The source
    # checkout and retained predecessor bytes remain unchanged.
    if name=='missing-inverse':
        owner,attr=five_exchange,'direct_line'
        old,new='yield move(inverse_word(frame.word))','yield move(())'
        expected='independent full-record oracle mismatch';case=('control-direct',(1,2,0,0),True,2,2,2)
    elif name=='lost-highs':
        owner,attr=receiver.Receiver,'serve_line'
        old,new='heights=self.high,','heights=1,'
        expected='pending + answer + packet conservation';case=('control-highs',(1,2,0,0),False,1,1,1)
    elif name=='lost-marker':
        owner,attr=receiver.Receiver,'serve_line'
        old,new='answers.take_answers(after, completed)','answers.take_answers(0, completed)'
        expected='external markers not restored';case=('control-marker',(1,1,0,0),False,2,2,2)
    elif name=='dirty-tail':
        owner,attr=stack_tapes.Page,'release'
        old,new='write_zeros(self, self.size)','pass  # deliberately omit physical erasure'
        expected='dirty historical child tail survived';case=('control-tail',(1,2,0,0),True,2,2,2)
    else:
        owner,attr=five_exchange,'same_order_line'
        old='with core.storage() as arena:'
        new='with core.storage() as arena, __import__("streaming_routes").work_tapes(1) as illegal:'
        expected='transient scratch crosses same-stage call';case=('control-scratch',(1,1,0,0),False,2,2,2)
    original=getattr(owner,attr);source=dedent(inspect.getsource(original))
    need(source.count(old)==1,'mutation has no unique source site')
    modified=source.replace(old,new)
    if name=='live-scratch':
        modified=modified.replace('        pipe(arena,','        illegal[0].write(b"dirty")\n        pipe(arena,')
    namespace=dict(original.__globals__)
    exec(compile(modified,'<negative-control:'+name+'>','exec'),namespace)
    created=namespace[original.__name__]
    replacement=FunctionType(created.__code__,original.__globals__,created.__name__,created.__defaults__,created.__closure__)
    replacement.__kwdefaults__=created.__kwdefaults__
    changed=aliases(original,replacement);setattr(owner,attr,replacement)
    try:
        try:run_case(*case)
        except AssertionError as error:
            need(expected in str(error),'mutation rejected for an unexpected reason: '+str(error))
            output.write_text(json.dumps({'status':'rejected','mutation':name,'reason':str(error)},indent=2)+'\n')
            print('PASS_NEGATIVE_CONTROL',name,str(error),flush=True)
        else:raise AssertionError('source mutation was not detected: '+name)
    finally:
        setattr(owner,attr,original)
        for module,key in changed:setattr(module,key,original)


if __name__=='__main__':main()
