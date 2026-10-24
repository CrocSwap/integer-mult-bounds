"""Independent endpoints, ownership and mutation controls; no oracle feeds execution."""
from pathlib import Path
from hashlib import sha256,sha1
from contextlib import contextmanager
import argparse,ast,inspect,json,sys,textwrap,types,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import elementary as e
from raw import Raw

def need(ok,message):
    if not ok:raise ValueError(message)

def same_receipt(a,b):
    return json.dumps(a,sort_keys=True,separators=(',',':'),allow_nan=False)==json.dumps(b,sort_keys=True,separators=(',',':'),allow_nan=False)

def body(tape):return bytes(tape.cells[1:]).rstrip(bytes([e.BLANK]))
def descriptor(n):
    t=e.Tape()
    for b in reversed(bin(n)[2:]):t.append(int(b))
    t.append(e.RIGHT);t.rewind();return t

def payload(bits):
    t=e.Tape()
    for b in bits:t.append(b)
    t.rewind();return t

def target(i,w,a,g,s):
    i,k=divmod(i,s);i,y=divmod(i,1<<w);i,j=divmod(i,g);i,x=divmod(i,1<<w)
    return ((((i*(1<<w)+y)*g+j)*(1<<w)+x)*s+k)

def expected(bits,w,a,g,s):
    out=bytearray(len(bits))
    for i,b in enumerate(bits):out[target(i,w,a,g,s)]=b
    return bytes(out)

def case(w,a,g,s,bits=None,engine=None):
    n=a*4**w*g*s
    if bits is None:bits=bytes(((i*13)^(i>>3)^0x53)&1 for i in range(n))
    data=payload(bits);ds=tuple(descriptor(x) for x in (w,a,g,s));ports=(data,*ds)
    before=[bytes(t.cells) for t in ports]
    own=engine is None
    if own:engine=e.Elementary()
    out=engine.run(data,*ds)
    need(body(out)==expected(bits,w,a,g,s),'exact interchange')
    need([bytes(t.cells) for t in ports]==before,'borrowed bytes')
    need(all(t.head==1 for t in (*ports,out)),'all returned heads')
    need(engine.bank.peak<=13,'proved live bound')
    out.clear()
    if own:
        engine.close();need(all(all(b==e.BLANK for b in t.cells) for t in (*engine.bank.tapes,engine.output)),'owned erasure')
    return dict(width=w,spectators=[a,g,s],bits=n,peak=engine.bank.peak)

@contextmanager
def traffic():
    totals=dict(read=0,write=0,step=0);original={n:getattr(e.Tape,n) for n in totals}
    def counted(name,fn):
        def call(self,*args):totals[name]+=1;return fn(self,*args)
        return call
    for n,fn in original.items():setattr(e.Tape,n,counted(n,fn))
    try:yield totals
    finally:
        for n,fn in original.items():setattr(e.Tape,n,fn)

def controls():
    rows=[case(*v) for v in ((0,2,3,2),(1,2,3,2),(2,2,3,1),(3,1,2,1),(4,1,1,1),(5,1,1,1))]
    columns=0
    for fixture in ((1,2,2,1),(2,1,1,1)):
        w,a,g,s=fixture;n=a*4**w*g*s
        for i in range(n):
            bits=bytes(int(j==i) for j in range(n));case(*fixture,bits=bits);columns+=1
    engine=e.Elementary()
    for fixture in ((2,1,3,2),(0,1,2,2),(3,1,1,1)):case(*fixture,engine=engine)
    engine.close()
    need(all(all(b==e.BLANK for b in t.cells) for t in (*engine.bank.tapes,engine.output)),'reused owner disposal')
    rejected=[]
    def reject(label,fn):
        try:fn()
        except ValueError:rejected.append(label)
        else:raise ValueError('control escaped '+label)
    old=e.bitstream.digit_swap
    source=textwrap.dedent(inspect.getsource(old)).replace('buckets[b][a]','buckets[a][b]')
    ns={};exec(compile(source,'<wrong-bucket-control>','exec'),e.bitstream.__dict__,ns)
    e.bitstream.digit_swap=types.FunctionType(ns['digit_swap'].__code__,e.bitstream.__dict__)
    try:reject('wrong_bucket_transpose',lambda:case(2,1,2,1,bits=bytes(int(i==1) for i in range(32))))
    finally:e.bitstream.digit_swap=old
    old=e.Elementary.run
    source=textwrap.dedent(inspect.getsource(old)).replace('pre.multiply_small(2);','None;')
    ns={};exec(compile(source,'<missing-prefix-control>','exec'),e.__dict__,ns)
    e.Elementary.run=ns['run']
    try:reject('missing_next_prefix_update',lambda:case(2,1,2,1,bits=bytes(int(i==1) for i in range(32))))
    finally:e.Elementary.run=old
    old=e.Lease.clear
    def uncleared(self):
        self.bank.live[self.slot]=None;self.active=False
    e.Lease.clear=uncleared
    try:reject('missing_lease_erase',lambda:case(2,1,2,1,bits=bytes(int(i==1) for i in range(32))))
    finally:e.Lease.clear=old
    engine=e.Elementary();data=payload(bytes(16));ds=[descriptor(v) for v in (2,1,1,1)]
    reject('external_alias',lambda:engine.run(data,ds[0],ds[0],ds[2],ds[3]))
    with engine.bank.installed():reject('runtime_tape_allocation',e.Tape)
    engine.close()
    # The current selected record and all selected/native classes are irrelevant
    # to this actual import graph, not silently accepted by a patched guard.
    forbidden={'loader','source','ordinary','macro_machine','macro_binding','topology','catalogue'}
    need(not forbidden.intersection(sys.modules),'no selected dependency')
    from rotation import Runner,compile_rotation,Fiber
    def fiber_case(wrong=False,stale=False):
        bits=bytes(((i*7)^(i>>2))&1 for i in range(48));data=payload(bits)
        rom=payload(bytes(int(x) for x in '00000000001000101000100000000000'))
        runner=Runner(e.Physical);node=compile_rotation('u_plus')[10]
        if stale:node=Fiber(node.zero,node.one,0)
        if wrong:node=Fiber(node.zero,node.zero,node.rom_address)
        out=runner.run(data,rom,(node,))
        need(body(out)==bits[-12:]+bits[:-12],'actual ROM orientation')
        need(rom.head==data.head==out.head==1,'fiber heads')
        need(all(b==e.BLANK for t in (runner.left,runner.right) for b in t.cells[1:]),'fiber scratch')
    fiber_case();reject('wrong_ROM_cut',lambda:fiber_case(wrong=True));reject('stale_ROM_address',lambda:fiber_case(stale=True))
    for label,value in (('boolean_receipt_integer',True),('float_receipt_integer',1.0)):
        changed=dict(rows[1]);changed['width']=value
        reject(label,lambda:need(same_receipt(rows[1],changed),'typed receipt mismatch'))
    from unittest.mock import patch
    original_read=Path.read_bytes
    damaged=ROOT/'research/unconditional-batched-crt/check_batched_crt.py'
    def altered(path):
        data=original_read(path)
        return data+b'\n' if path==damaged else data
    with patch.object(Path,'read_bytes',altered):reject('damaged_source_bytes',authenticate)
    return dict(cases=rows,independent_columns=columns,rejected=rejected,reused_calls=3,private_role_capacity=16,proved_peak=13)

def load(path):
    m=types.ModuleType(path.stem);m.__file__=str(path);exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m

def bound(w,a,g,s):
    v=a*4**w*g*s;d=w+sum(n.bit_length() for n in (w,a,g,s))+4
    return 2**20*(w+1)*(v+1)*(d+1)**2

def actual(dump_path=None):
    crt=load(ROOT/'research/unconditional-batched-crt/check_batched_crt.py')
    rows=[crt.benes(crt.rotation(8,5,a))[2][1] for a in (0,2,4,0)];rombits=tuple(b for row in rows for b in row)
    labels=[(x^((x>>12)*1237))&4095 for x in range(16384)]
    bits=bytes(int(b) for v in labels for b in f'{v:012b}')
    expected_labels=[None]*16384
    for x,value in enumerate(labels):
        u,t,y,back=x>>12,(x>>10)&3,(x>>2)&255,x&3
        a,b,c=crt.compact(u,t,y,lambda z:(rombits[z&31],),positions=(2,),ybits=8)
        expected_labels[(((a*4+b)*256+c)*4)+back]=value
    want=bytes(int(b) for v in expected_labels for b in f'{v:012b}')
    data,rom=payload(bits),payload(rombits);rom_before=bytes(rom.cells)
    start=time.monotonic()
    with traffic() as bill:
        caller=Raw();returned=caller.run(data,rom)
        need(returned is data and body(data)==want,'actual complete rawS endpoint')
        need(bytes(rom.cells)==rom_before and rom.head==1 and data.head==1,'ROM and heads')
        need(caller.calls==12 and caller.runner.rom_reads==8192,'all twelve shuttles and current-ROM calls')
        private=(*caller.engine.bank.tapes,caller.engine.output,*caller.u,*caller.t,caller.runner.left,caller.runner.right,caller.runner.output)
        need(len({id(t) for t in (*private,data,rom)})==30,'disjoint complete physical inventory')
        caller.close()
        need(all(all(b==e.BLANK for b in t.cells) and t.head==1 for t in private),'all28 private roles erased/returned')
    limit=12*max(bound(2,1,1024,12),bound(2,4,256,12))+2**16*(196608+1)
    need(sum(bill.values())+caller.engine.bank.control+caller.runner.control<=limit,'conservative source bound')
    # Cross-task artifact is observational only; not a repair-input conversion.
    result=dict(status='PASS_STANDALONE_COMPLETE_RAW',geometry=[2,2,8,2],payload_bits=len(want),physical_private_roles=28,
        ordinary_calls=caller.calls,rom_reads=caller.runner.rom_reads,peak_scratch=caller.engine.bank.peak,
        tape_actions=bill,allocator_control=caller.engine.bank.control,rotation_control=caller.runner.control,
        conservative_source_bound=limit,input_sha256=sha256(bits).hexdigest(),raw_sha256=sha256(body(data)).hexdigest(),
        rom=''.join(map(str,rombits)))
    if dump_path is not None:Path(dump_path).write_bytes(body(data))
    return result,time.monotonic()-start

def authenticate():
    result={}
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage']!='input':continue
        b=(ROOT/row['path']).read_bytes();need(sha256(b).hexdigest()==row['sha256'],'source SHA '+row['path'])
        need(sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['git_blob'],'source Git blob')
        result[row['path']]=row['sha256']
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--light',action='store_true');ap.add_argument('--write-result',action='store_true');ap.add_argument('--dump-raw');args=ap.parse_args()
    sources=authenticate();checks=controls()
    if args.light:print(json.dumps(checks,indent=2));print('PASS_STANDALONE_LIGHT');return
    out,seconds=actual(args.dump_raw);result=dict(status='PASS_STANDALONE_ELEMENTARY_AND_RAW',controls=checks,actual=out,sources=sources,
        code_hashes={n:sha256((HERE/n).read_bytes()).hexdigest() for n in ('elementary.py','raw.py','rotation.py')})
    if args.write_result:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:need(same_receipt(json.loads((HERE/'RESULT.json').read_text()),result),'exact typed frozen receipt')
    print(json.dumps(dict(status=result['status'],seconds=seconds,actual=out),indent=2))
if __name__=='__main__':main()
