"""Independent dense CPU and Cartesian phase oracle; Apache-2.0.
Prepared for CubeJerry with OpenAI assistance. No author CPU/tests execute.
"""
from pathlib import Path
from itertools import product
import hashlib,importlib.util,json,sys
class Rejected(Exception):pass

def load(path):
    spec=importlib.util.spec_from_file_location('phase_subject',path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def gamma(n):
    s=format(n,'b');return '0'*(len(s)-1)+s

def bits(n,w):
    if not -(1<<(w-1))<=n<(1<<(w-1)):raise OverflowError('signed range')
    return format(n%(1<<w),f'0{w}b')

class CPU:
    def __init__(self,header,data,capacity=None):
        self.origin=[31+3*t for t in range(20)];self.head=self.origin.copy()
        size=capacity or max(2048,4*(len(data)+len(header)+100))
        self.rows=[['_']*size for _ in range(20)];self.steps=0
        for t,o in enumerate(self.origin):self.rows[t][o-5:o-1]=list('1|01')
        self.supply(header,data)
    def supply(self,header,data):
        if self.head!=self.origin:raise AssertionError('not retired')
        for t,s in ((0,header),(1,data)):
            o=self.origin[t];self.rows[t][o:]=['_']*(len(self.rows[t])-o)
            self.rows[t][o:o+len(s)]=list(s);self.rows[t][o+len(s)+1:o+len(s)+5]=list('1|01')
        self.before=[r.copy() for r in self.rows]
    def run(self,code):
        pc=0;start=self.steps
        while self.steps-start<25_000_000:
            op,*args=code[pc];pc+=1;self.steps+=1
            if op=='read':
                t,edges=args;s=self.rows[t][self.head[t]]
                if s not in edges:raise Rejected('undefined local branch')
                pc=edges[s]
            elif op=='write':
                t,s=args
                if s not in '_01|':raise AssertionError('alphabet')
                self.rows[t][self.head[t]]=s
            elif op=='move':
                t,d=args
                if d not in (-1,1):raise AssertionError('nonlocal move')
                self.head[t]+=d
                if not 0<=self.head[t]<len(self.rows[t]):raise AssertionError('capacity')
            elif op=='goto':pc=args[0]
            elif op=='halt':return
            else:raise AssertionError('opcode')
        raise AssertionError('CPU budget exhausted, not a successful rejection')
    def check(self,expected):
        desired=[r.copy() for r in self.before];o=self.origin[1];desired[1][o:o+len(expected)]=list(expected)
        if self.rows!=desired:raise AssertionError('payload/header/exterior/cleanup')
        if self.head!=self.origin:raise AssertionError('head return')

def fixture(D,K,rho,P,S,r,w=8,p=4,d=None):
    params=(p,D+3 if d is None else d,r,D,P,S,K,rho+1,w);phases=[]
    for outer in range(P):
        for chunks in product(range(1<<K),repeat=D):
            q=sum((c>>rho)&1 for c in chunks)%4
            for suffix in range(S):phases.extend([q]*r)
    return params,phases,[((j*17)%61-30,(j*29)%59-29) for j in range(len(phases))]

def expected_bits(phases,pairs,w):
    output=''
    for q,(x,y) in zip(phases,pairs):
        for _ in range(q):x,y=-y,x
        output+=bits(x,w)+bits(y,w)
    return output

def exercise(code,params,phases,pairs,alter=None,cpu=None):
    w=params[-1];header=''.join(gamma(x) for x in params);data=''.join(bits(x,w)+bits(y,w) for x,y in pairs)
    try:expected=expected_bits(phases,pairs,w)
    except OverflowError:expected=None
    if alter=='extra':data+='1';expected=None
    if alter=='short':data=data[:-1];expected=None
    if alter=='bad_domain':expected=None
    if cpu is None:cpu=CPU(header,data)
    else:cpu.supply(header,data)
    start=cpu.steps
    try:cpu.run(code)
    except Rejected:
        if expected is not None:raise AssertionError('unexpected literal rejection')
        if cpu.rows[0]!=cpu.before[0] or cpu.rows[1]!=cpu.before[1]:raise AssertionError('public mutation before rejection')
        return cpu,cpu.steps-start,False
    if expected is None:raise AssertionError('missed rejection')
    cpu.check(expected);return cpu,cpu.steps-start,True

def main():
    path=Path(sys.argv[1]).resolve();m=load(path);code,alphabet=m.compile_phase()
    if set(alphabet)!=set('_01|'):raise AssertionError('alphabet')
    cases=steps=accepted=coefficients=0
    shapes=[(1,1,0),(2,2,0),(2,2,1),(3,2,1),(2,3,2),(4,1,0),(1,5,3),(3,1,0)]
    for j,(D,K,rho) in enumerate(shapes):
        params,phases,pairs=fixture(D,K,rho,1+j%2,1+(j//2)%2,1+j%3)
        _,n,ok=exercise(code,params,phases,pairs);steps+=n;cases+=1;accepted+=ok;coefficients+=len(pairs)
    params,phases,baseline=fixture(3,1,0,1,1,1,w=3,p=1)
    for q in range(4):
        position=phases.index(q)
        for component in (0,1):
            pairs=[(0,0)]*len(phases);pair=[0,0];pair[component]=-4;pairs[position]=tuple(pair)
            _,n,ok=exercise(code,params,phases,pairs);steps+=n;cases+=1;accepted+=ok;coefficients+=len(pairs)
    params,phases,pairs=fixture(2,2,1,2,3,2)
    for alteration in ('extra','short'):
        _,n,ok=exercise(code,params,phases,pairs,alteration);steps+=n;cases+=1;accepted+=ok
    for index,value in ((1,1),(7,3),(8,5)):
        invalid=list(params);invalid[index]=value
        _,n,ok=exercise(code,tuple(invalid),phases,[(0,0)]*len(phases),'bad_domain');steps+=n;cases+=1;accepted+=ok
    cpu=None;identities=None
    for shape in [(3,2,1,2,2,3),(1,1,0,1,1,1),(3,2,0,1,2,2)]:
        params,phases,pairs=fixture(*shape)
        if cpu is None:cpu=CPU('', '',capacity=50000);identities=tuple(map(id,cpu.rows))
        cpu,n,ok=exercise(code,params,phases,pairs,cpu=cpu);steps+=n;cases+=1;accepted+=ok;coefficients+=len(pairs)
        if tuple(map(id,cpu.rows))!=identities:raise AssertionError('backing replaced')
    controls=[]
    for name,tape,old,new in [('mask',m.MASK,'1','0'),('commit',m.DATA,'0','1'),('cleanup',m.OUTPUT,'_','1')]:
        mutant=[('write',tape,new) if ins==('write',tape,old) else ins for ins in code]
        if mutant==code:raise AssertionError('empty mutation')
        params,phases,pairs=fixture(3,1,0,1,2,2)
        try:exercise(mutant,params,phases,pairs)
        except (AssertionError,Rejected):controls.append(name)
        else:raise AssertionError('undetected '+name)
    print(json.dumps({'status':'PASS_INDEPENDENT_DENSE_PHASE','cases':cases,'accepted':accepted,'coefficients':coefficients,'transitions':steps,'locations':len(code),'controls':controls,'phase_sha256':hashlib.sha256(path.read_bytes()).hexdigest()},sort_keys=True))
if __name__=='__main__':main()
