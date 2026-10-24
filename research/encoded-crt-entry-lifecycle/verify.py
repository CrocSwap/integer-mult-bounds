"""Observer-only fixtures for the authenticated complete numerical entry.
JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse,hashlib,json,math,sys,types
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def need(ok,msg):
    if not ok:raise ValueError(msg)
def load(name,path):
    m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m
    exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m
def modules():
    for row in json.loads((P/'SOURCES.json').read_text())['files']:
        if row['usage']!='input':continue
        raw=(ROOT/row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest()==row['sha256'],'source SHA256 drift')
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'source Git blob drift')
    src=ROOT/'research/r437-preparation-composition/predecessor4025/source'
    return (load('words',src/'words.py'),load('records',src/'records.py'),load('current',ROOT/'research/encoded-current-crt/producer.py'),load('entry',P/'entry.py'),load('reference',ROOT/'research/unconditional-batched-crt/check_batched_crt.py'))
def digits(x):return [int(b) for b in reversed(bin(x)[2:])]
def port(w,e,values):
    t=e.Port(w)
    for v in values:t.append(v)
    t.rewind();return t
def stream(w,r,e,rows,width=None):
    body=[]
    for row in rows:
        body.append(r.ROOT)
        for v in row:
            bits=digits(v);body.extend(bits if width is None else bits+[0]*(width-len(bits)));body.append(r.WORD_END)
        body.append(r.RECORD_END)
    return port(w,e,body+[w.RIGHT])
def value(word):return sum(v<<i for i,v in enumerate(word.cells[1:-1]))
def observe(out,width,w,r):
    b=out['stream'].cells;at=1;rows=[]
    while b[at]!=w.RIGHT:
        need(b[at]==r.ROOT,'output tag');at+=1;row=[]
        for _ in range(2):
            bits=b[at:at+width];need(len(bits)==width and all(v in (0,1) for v in bits),'output bits')
            row.append(sum(v<<i for i,v in enumerate(bits)));at+=width;need(b[at]==r.WORD_END,'word delimiter');at+=1
        need(b[at]==r.RECORD_END,'record delimiter');at+=1;rows.append(row)
    need(all(v==w.BLANK for v in b[at+1:]),'output tail')
    return [value(out['lower']),value(out['product']),rows,out['left_valid']]
def expected(ref,left,right):
    valid=all(y<q for q,y in left);lower=ref.decode_group([y for q,y in left],[q for q,y in left]) if valid else 0
    product=math.prod(q for q,y in left);prefix=product;rows=[]
    for q,x in right:
        offset=lower*pow(prefix,-1,q)%q
        rows.append([offset,(x+offset)%q if x<q else x]);prefix*=q
    return [lower,product,rows,valid]
def snapshot(ports):return [(bytes(t.cells),t.head) for t in ports]
def traffic(ports):return {k:sum(getattr(t.meter,k) for t in ports) for k in ('reads','writes','moves')}
def event_hooks(w,events):
    zero,free=w.Arena.zero,w.Arena.free
    def z(a):
        out=zero(a);events.append(['alloc',out.slot]);return out
    def f(a,word):
        events.append(['free',word.slot]);return free(a,word)
    w.Arena.zero=z;w.Arena.free=f
    return zero,free
def reference_events(w,r,p,e,width,left,right,a):
    l=stream(w,r,e,left,width);rr=stream(w,r,e,right,width);events=[];old=event_hooks(w,events)
    try:
        out=p.produce(a,l,rr,w,r);a.free_many(out['lower'],out['product']);out['stream'].clear()
    finally:w.Arena.zero,w.Arena.free=old
    return events

def case(mod,width,invocations,fault=None):
    w,r,p,e,ref=mod;guide=port(w,e,[w.ONE]*width)
    dirty=[port(w,e,digits(i)+[0]*(width-len(digits(i)))+[w.RIGHT]) for i in range(8)]
    for i,t in enumerate(dirty):
        for _ in range(i%3):t.step(1)
    owned_inputs=[guide,*dirty];before=snapshot(owned_inputs);base=traffic(owned_inputs)
    old=w.Word.__init__,w.Arena.__init__
    def forbidden(*a,**k):raise ValueError('host bulk constructor forbidden')
    w.Word.__init__=w.Arena.__init__=forbidden
    try:ctx=e.Entry(w,r,guide,dirty)
    finally:w.Word.__init__,w.Arena.__init__=old
    need(len(ctx.owned)==60 and all(len(t.cells)==width+2 for t in ctx.owned[:57]),'exact initialized physical inventory')
    results=[];events=[];all_streams=[];stream_base={k:0 for k in base}
    reference_arena=w.Arena(width,64)
    for i in range(8):reference_arena.literal(i)
    for left,right in invocations:
        l=stream(w,r,e,left);rr=stream(w,r,e,right);all_streams.extend([l,rr]);saved=snapshot([l,rr]);tb=traffic([l,rr])
        for k in base:stream_base[k]+=tb[k]
        local=[];hooks=event_hooks(w,local)
        producer=p if fault is None else types.SimpleNamespace(produce=lambda *a:p.produce(*a,fault=fault))
        try:
            out=ctx.invoke(producer,l,rr);actual=observe(out,width,w,r)
            need(actual==expected(ref,left,right),'actual source endpoint');ctx.consume(out)
        finally:w.Arena.zero,w.Arena.free=hooks
        need(local==reference_events(w,r,p,e,width,left,right,reference_arena),'exact lazy/eager allocation-event correspondence')
        events.extend(local);need(snapshot([l,rr])==saved,'borrowed descriptor exact bytes/heads')
        need(ctx.arena.live==set(range(8)),'protected inventory after consume')
        results.append(dict(left=left,right=right,endpoint=actual,allocation_events=len(local)))
    ctx.close();need(snapshot(owned_inputs)==before,'borrowed guide/dirty exact bytes/heads')
    need(all(t.head==1 and all(v==w.BLANK for v in t.cells) for t in ctx.owned),'complete private retirement')
    retained=sum(len(t.cells) for t in ctx.owned);bound=57*(width+2)+3*(width-2)*(2*width+4)+6
    need(retained<=bound,'whole retained backing')
    observed=traffic(owned_inputs+all_streams+ctx.owned)
    for k in observed:observed[k]-=base[k]+stream_base[k]
    numerical={k:getattr(ctx.arena.meter,k) for k in observed}
    need(sum(observed.values())+sum(numerical.values())<=len(invocations)*(2**20*(width+2)**4+2**16*(width+2)**2),'complete tariff')
    return dict(width=width,calls=results,retained_cells=retained,retained_bound=bound,port_traffic=observed,numerical_traffic=numerical,events_sha256=hashlib.sha256(json.dumps(events).encode()).hexdigest())
def rejects(fn,label):
    try:fn()
    except (ValueError,TypeError):return label
    raise ValueError('control accepted '+label)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write-result',action='store_true');args=ap.parse_args();mod=modules();w,r,p,e,ref=mod
    cases=[case(mod,4,[([(2,1)],[(3,2)])])]
    for width in (10,16,24):cases.append(case(mod,width,[([(5,1),(7,5)],[(13,9)]), ([(5,1),(7,5)],[(13,15)])]))
    cases.append(case(mod,16,[([(5,1),(7,5)],[(13,9),(17,7)]), ([(5,5),(7,5)],[(13,9)]), ([(3,1)],[(5,2),(7,6)])]))
    controls=[]
    for fault in ('treat_current_as_original','omit_right_prefix','rotate_padding'):
        controls.append(rejects(lambda:case(mod,16,[([(5,1),(7,5)],[(13,15),(17,7)])],fault),fault))
    controls.append(rejects(lambda:case(mod,9,[([(5,1),(7,5)],[(13,9)])]),'insufficient product margin'))
    for n in (0,1,2,3,4,9):
        g=port(w,e,[w.ONE]*n);old=snapshot([g]);need((e.Extent(g,w)>=4)==(n>=4),'encoded guard');need(snapshot([g])==old,'guard head restore')
    controls.append(rejects(lambda:int(e.Extent(port(w,e,[1]*4),w)),'host decode'))
    controls.append(rejects(lambda:e.Extent(port(w,e,[1]*4),w)>=5,'unaudited width comparison'))
    result=dict(status='PASS_ENCODED_CRT_ENTRY_LIFECYCLE',cases=cases,controls=controls,owned_ports=60,source_guard_cases=6,entry_sha256=hashlib.sha256((P/'entry.py').read_bytes()).hexdigest())
    encoded=json.dumps(result,sort_keys=True)
    if args.write_result:(P/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(encoded==json.dumps(json.loads((P/'RESULT.json').read_text()),sort_keys=True),'typed complete receipt mismatch')
    print(json.dumps(dict(status=result['status'],cases=len(cases),controls=len(controls))))
if __name__=='__main__':main()
