"""Independent whole-tree oracle and actual control mutants."""
from pathlib import Path
import hashlib,json,sys,itertools,types
sys.path.insert(0,str(Path(__file__).resolve().parent))
import machine as impl
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def check(ok,msg):
    if not ok:raise ValueError(msg)
def rejected(fn):
    try:fn()
    except (ValueError,KeyError):return
    raise ValueError('control unexpectedly accepted')
def pins():
    f=HERE/'SOURCES.json'
    for r in json.loads(f.read_text())['files']:
        check(hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'],'source drift '+r['path'])
def fixture(m,b,bits):
    origins=[7,-3,11,4,-5,19,-31,22,-9]
    payload=(bits,'','1'*b,'','','','','','')
    t=[]
    for i,(h,data) in enumerate(zip(origins,payload)):
        cells={h-1:'|',**{h+j:x for j,x in enumerate(data)}}
        if i==impl.PARK:cells.update({h-7:'1',h-5:'|',h-3:'0'})
        t.append(m.Tape(cells,h))
    return t,origins
def bits_at(t,h,n):return ''.join(t.cells.get(h+i,'_') for i in range(n))
def coupled_leaf(Builder):
    # Independent fixed machine: XOR each row with its original first bit.
    # The host oracle below slices rows only outside runtime control.
    a=Builder();a.read(impl.SOURCE,{'0':'loop0','1':'loop1'})
    for first in (0,1):
        tag=str(first);a.mark('loop'+tag)
        a.read(impl.SOURCE,{'0':'zero'+tag,'1':'one'+tag,'_':'end'})
        for bit,name in ((0,'zero'),(1,'one')):
            a.mark(name+tag);a.read(impl.OUTPUT,{'_':name+tag+'empty'});a.mark(name+tag+'empty')
            a.write(impl.OUTPUT,str(bit^first));a.move(impl.SOURCE,1);a.move(impl.OUTPUT,1);a.go('loop'+tag)
    a.mark('end');a.rewind(impl.SOURCE);a.rewind(impl.OUTPUT);a.code.append(('done',))
    a.mark('reject');a.code.append(('reject',));a.mark('quarantine');a.code.append(('reject',))
    return a.finish()
def one(module,b,d,bits,coupled=False):
    _,m,*_=module.load(ROOT);t,h=fixture(m,b,bits);before=[x.snapshot() for x in t]
    engine=module.Machine(ROOT,t)
    if coupled:engine.leaf=coupled_leaf(engine.rows.Builder)
    # No Tape constructor is available after program initialization.
    old=engine.m.Tape.__init__
    def forbidden(*a,**k):raise ValueError('fresh runtime tape')
    engine.m.Tape.__init__=forbidden
    try:r=engine.run()
    finally:engine.m.Tape.__init__=old
    v=len(bits);n=2**d
    expected=(''.join(str(int(c)^int(bits[(i//b)*b])) for i,c in enumerate(bits)) if coupled else ''.join('1' if c=='0' else '0' for c in bits))
    check(bits_at(t[impl.OUTPUT],h[impl.OUTPUT],v)==expected,'independent payload endpoint')
    check(t[impl.OUTPUT].head==h[impl.OUTPUT],'output head')
    for i in (impl.SOURCE,impl.GUIDE,impl.ROLE0,impl.ROLE1,impl.IO,impl.PARK,impl.TEMP,impl.CONT):
        check(t[i].snapshot()==before[i],'complete frame/cleanup')
    check((r['nodes'],r['leaves'])==(2*n-1,n),'complete binary tree')
    check(r['steps']<=100*v*d+264*v+3,'uniform time invoice')
    check(all(x>=h[impl.PARK]-1 for x in t[impl.PARK].visits),'ancestor locality')
    growth=0
    for i,x in enumerate(t):
        touched=set(x.visits+x.writes);growth+=len(touched-set(dict(before[i][1])))
    check(growth<=16*v+32,'retained growth upper bound')
    rejected(lambda:engine.run())
    return r

def main():
    pins();cases=0;receipts=[]
    for b,d in itertools.product((1,2,3,7),range(5)):
        v=b*2**d
        samples=['0'*v,'1'*v,''.join(str((i*i+i//3)%2) for i in range(v))]
        # Complete basis on the first true recursive source; larger shapes
        # have fixed independently generated arbitrary dirty data.
        if b==3 and d==3:samples+=['0'*i+'1'+'0'*(v-i-1) for i in range(v)]
        for coupled in (False,True):
            for bits in samples:r=one(impl,b,d,bits,coupled);cases+=1
            receipts.append({'B':b,'depth':d,'V':v,'coupled_leaf':coupled,**r})
    source=(HERE/'machine.py').read_text();controls=0
    for old,new in [("active=0 if saved==Z else 1","active=1 if saved==Z else 0"),("self.erase(SOURCE)","self.erase(GUIDE)"),("pc=3;q='boundary'","pc=4;q='boundary'")]:
        check(source.count(old)==1,'unique mutant site')
        mod=types.ModuleType('mutant');exec(compile(source.replace(old,new),'<actual-control-mutant>','exec'),mod.__dict__)
        rejected(lambda:one(mod,3,3,'000001010011100101110111'));controls+=1
    _,m,*_=impl.load(ROOT)
    t,h=fixture(m,3,'010101');t[impl.OUTPUT]=t[impl.SOURCE];rejected(lambda:impl.Machine(ROOT,t));controls+=1
    for b,bits in ((3,''),(3,'01'),(3,'010101010')):
        t,h=fixture(m,b,bits);rejected(lambda:impl.Machine(ROOT,t).run());controls+=1
    result={'status':'PASS_FIXED_BANK_RECURSIVE_CALLER','cases':cases,'controls':controls,'ports':9,'receipts':receipts}
    frozen=HERE/'RESULT.json'
    if '--write-result' in sys.argv:frozen.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    check(json.dumps(result,sort_keys=True)==json.dumps(json.loads(frozen.read_text()),sort_keys=True),'typed frozen receipt')
    return result
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,indent=2))
