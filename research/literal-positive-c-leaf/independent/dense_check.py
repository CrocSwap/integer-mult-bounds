"""Independent dense local CPU and direct tensor-polynomial C oracle.
Prepared for CubeJerry with OpenAI assistance. Apache-2.0.
The author interpreter, tests and expected-output routine are not used.
"""
from pathlib import Path
import hashlib, importlib.util, json, sys

def need(x, message):
    if not x: raise AssertionError(message)

class Rejected(Exception): pass

SYMBOLS = '_01|'

class CPU:
    def __init__(self, tapes, capacity):
        self.origin = [19+2*t for t in range(tapes)]
        self.head = self.origin.copy()
        self.rows = [bytearray(capacity) for _ in range(tapes)]
        for t,o in enumerate(self.origin):
            self.rows[t][o-6:o-2] = bytes((2,1,3,2))
            self.rows[t][-5:-1] = bytes((1,2,3,1))
        self.low = self.origin.copy(); self.high = self.origin.copy()

    def supply(self, fields):
        need(self.head==self.origin, 'clean successful reuse')
        for t,word in enumerate(fields):
            row=self.rows[t]; o=self.origin[t]
            row[o:-6]=bytes(len(row)-6-o)
            row[o:o+len(word)] = bytes(SYMBOLS.index(c) for c in word)
            row[o+len(word)+1:o+len(word)+5] = bytes((1,2,3,1))
        self.before = [r[:] for r in self.rows]

    def run(self, code, limit=120_000_000):
        compiled=[]; nt=len(self.rows)
        for ins in code:
            op,*args=ins
            if op=='read':
                t,branches=args; need(0<=t<nt,'tape range')
                dest=[-1]*4
                for c,p in branches.items():
                    need(c in SYMBOLS and type(p) is int and 0<=p<len(code),'local branch')
                    dest[SYMBOLS.index(c)]=p
                compiled.append((0,t,dest))
            elif op=='write':
                t,c=args; need(0<=t<nt and c in SYMBOLS,'local write')
                compiled.append((1,t,SYMBOLS.index(c)))
            elif op=='move':
                t,d=args; need(0<=t<nt and d in (-1,1),'unit move')
                compiled.append((2,t,d))
            elif op=='goto':
                need(0<=args[0]<len(code),'fixed goto');compiled.append((3,args[0],0))
            elif op=='halt': compiled.append((4,0,0))
            else: raise AssertionError('nonlocal instruction')
        rows=self.rows; h=self.head; lo=self.low; hi=self.high
        pc=steps=0; counts=[[0,0,0] for _ in rows]
        while steps<limit:
            op,t,v=compiled[pc]; pc+=1; steps+=1
            if op==0:
                counts[t][0]+=1;pc=v[rows[t][h[t]]]
                if pc<0: raise Rejected('undefined branch')
            elif op==1: counts[t][1]+=1;rows[t][h[t]]=v
            elif op==2:
                counts[t][2]+=1;h[t]+=v
                need(0<=h[t]<len(rows[t]),'observer capacity')
                if h[t]<lo[t]:lo[t]=h[t]
                if h[t]>hi[t]:hi[t]=h[t]
            elif op==3:pc=t
            else:return steps,counts
        raise AssertionError('bounded observer budget exhausted')

def gamma(n):
    b=format(n,'b');return '0'*(len(b)-1)+b

def mul(a,b):return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])

def weight(k,h):
    z=(1,0)
    for _ in range(k-h):z=mul(z,(1,1))
    for _ in range(h):z=mul(z,(1,-1))
    return z

def oracle(values, shape, dimension):
    """Each partial tensor is recomputed directly from the original values.
    No butterfly recurrence or signed carry implementation is reused.
    """
    f,r,P,S,w,cutoff=shape
    if f>cutoff or w<2:return None
    Q=1<<f; tail=(1<<((dimension-1)*f))*S*r; bound=1<<(w-1)
    for k in range(1,f+1):
        q=1<<k;weights=[weight(k,h) for h in range(k+1)];result=[]
        for p in range(P):
            for a in range(Q):
                high=(a//q)*q
                for t in range(tail):
                    re=im=0
                    for b in range(q):
                        z=mul(weights[((a%q)^b).bit_count()],values[(p*Q+high+b)*tail+t])
                        re+=z[0];im+=z[1]
                    if re%q or im%q:return None
                    z=(re//q,im//q)
                    if any(not -bound<=x<bound for x in z):return None
                    result.append(z)
    return result

def field(values,w):
    return ''.join(format(x%(1<<w),'0'+str(w)+'b') for pair in values for x in pair)

def fixture(shape,dimension,kind='scaled'):
    f,r,P,S,w,cutoff=shape;N=P*(1<<(dimension*f))*S*r
    if kind=='scaled':
        return [(((((i*17)^(i>>3))%3)-1)*(1<<f),((((i*7+1)^(i>>2))%3)-1)*(1<<f)) for i in range(N)]
    if kind=='odd':return [(1,0)]+[(0,0)]*(N-1)
    return [(0,0)]*N

def check(code,shape,dimension,values=None,*,bad=None,cpu=None):
    f,r,P,S,w,cutoff=shape
    if values is None:values=fixture(shape,dimension)
    expected=oracle(values,shape,dimension)
    header=''.join(map(gamma,shape));data=field(values,w);V=len(data)
    fields=[header,data]
    if bad=='short':fields[1]=data[:-1]
    elif bad=='extra':fields[1]+='1'
    elif bad=='header':fields[0]='|'+header[1:]
    elif bad=='symbol':fields[1]=data[:V//3]+'|'+data[V//3+1:]
    if cpu is None:cpu=CPU(29,V+len(header)+sum(shape[:5])+2048)
    cpu.supply(fields)
    try:steps,counts=cpu.run(code)
    except Rejected:
        need(expected is None or bad is not None,'unexpected exact C rejection')
        need(cpu.rows[:2]==cpu.before[:2],'failed call preserves both public tapes')
        return cpu,0,False
    need(expected is not None and bad is None,'missed parity/range/header/cardinality rejection')
    desired=[row[:] for row in cpu.before];o=cpu.origin[1]
    desired[1][o:o+V]=bytes(1+int(c) for c in field(expected,w))
    need(cpu.rows==desired,'direct tensor values, complete private retirement, opaque cells')
    need(cpu.head==cpu.origin,'all successful heads return')
    need(counts[1]==[V+1,V,4*V],'one input clone and same-owner final commit')
    need(counts[0][1]==0,'header is read-only')
    return cpu,steps,True

def main():
    path=Path(sys.argv[1]).resolve();digest=hashlib.sha256(path.read_bytes()).hexdigest()
    spec=importlib.util.spec_from_file_location('positive_c_subject',path);m=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=m;spec.loader.exec_module(m)
    actual,alphabet=m.compile_leaf();need(set(alphabet)==set(SYMBOLS),'alphabet')
    successes=rejections=steps=actual_cases=fixtures=0
    for shape in ((1,1,1,1,5,1),(1,2,1,1,5,3),(1,1,2,2,5,1),(1,1,1,1,5,1<<2048)):
        _,n,ok=check(actual,shape,9);successes+=ok;rejections+=not ok;steps+=n;actual_cases+=1
    for shape,kind in (((1,1,1,1,2,1),'odd'),((2,1,1,1,2,1),'zero'),((2,1,1,1,2,2),'odd')):
        _,n,ok=check(actual,shape,9,fixture(shape,9,kind));successes+=ok;rejections+=not ok;steps+=n;actual_cases+=1
    for bad in ('short','extra','header','symbol'):
        check(actual,(1,1,1,1,5,1),9,bad=bad);rejections+=1
    # Separate fixed-dimension construction fixtures: explicitly not the m=9 table.
    for dimension in (1,2):
        m.NATIVE_DIMENSION=dimension;code,_=m.compile_leaf()
        for f in (1,2,3,4):
            shape=(f,1,1,1,f+4,f)
            _,n,ok=check(code,shape,dimension);successes+=ok;rejections+=not ok;steps+=n;fixtures+=1
    m.NATIVE_DIMENSION=1;small,_=m.compile_leaf()
    # Exhaust every signed width-two pair. Direct matrix oracle decides parity/range.
    for a in range(-2,2):
        for b in range(-2,2):
            for c in range(-2,2):
                for d in range(-2,2):
                    _,n,ok=check(small,(1,1,1,1,2,1),1,[(a,b),(c,d)])
                    successes+=ok;rejections+=not ok;steps+=n;fixtures+=1
    cpu=CPU(29,24000);ids=tuple(map(id,cpu.rows));hist=0
    for shape in ((3,1,2,2,7,3),(1,1,1,1,5,1),(4,2,2,1,8,5)):
        cpu,n,ok=check(small,shape,1,cpu=cpu);need(ok,'reuse fixture acceptance')
        successes+=1;fixtures+=1;steps+=n
        need(tuple(map(id,cpu.rows))==ids,'one retained inventory')
        h=sum(cpu.high[t]-cpu.low[t]+1 for t in range(2,29));need(h>=hist,'retained history');hist=h
    controls=[]
    def detect(broken,shape,values,label):
        try:check(broken,shape,1,values)
        except (AssertionError,Rejected):controls.append(label)
        else:raise AssertionError('undetected mutation '+label)
    original_rows=m.ROWS;m.ROWS=(original_rows[2],original_rows[3],original_rows[0],original_rows[1])
    wrong,_=m.compile_leaf();m.ROWS=original_rows
    detect(wrong,(1,1,1,1,5,1),[(2,0),(0,0)],'wrong conjugate kernel')
    broken=list(small);changed=0
    for i,ins in enumerate(small):
        if ins[:2]==('read',m.NUM) and set(ins[2])=={'0','1'} and ins[2]['1']==len(small)-1:
            broken[i]=('read',m.NUM,{'0':ins[2]['0'],'1':ins[2]['0']});changed+=1
    need(changed==4,'four exact divisibility gates')
    detect(broken,(1,1,1,1,3,1),[(1,0),(0,0)],'rounding an odd numerator')
    broken=list(small);changed=0
    for i,ins in enumerate(small):
        if ins[:2]==('read',m.NUM) and len(ins[2])==1 and next(iter(ins[2])) in ('0','1'):
            dest=next(iter(ins[2].values()));broken[i]=('read',m.NUM,{'0':dest,'1':dest});changed+=1
    need(changed==8,'eight signed fit branches')
    detect(broken,(1,1,1,1,2,1),[(-2,-2),(-2,0)],'truncating signed overflow')
    broken=list(small)
    for i,ins in enumerate(small):
        if ins[:2]==('write',m.DATA) and ins[2]=='1':broken[i]=('write',m.DATA,'0')
    detect(broken,(1,1,1,1,5,1),[(2,0),(0,0)],'corrupt original-owner installation')
    need(hashlib.sha256(path.read_bytes()).hexdigest()==digest,'source changed during review')
    print(json.dumps({'status':'PASS_INDEPENDENT_POSITIVE_C','program_sha256':digest,'locations':len(actual),
        'actual_dimension_cases':actual_cases,'actual_f2_complete_success':False,
        'smaller_dimension_fixtures':fixtures,'successes':successes,'rejections':rejections,
        'successful_transitions':steps,'private_history_span':hist,'large_cutoff_bits':2049,
        'mutations':controls},sort_keys=True))

if __name__=='__main__':main()

