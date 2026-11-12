"""Independent dense CPU and selected XOR/popcount phase oracle; Apache-2.0.
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
        self.origin=[31+3*t for t in range(23)];self.head=self.origin.copy()
        size=capacity or max(2048,4*(len(data)+len(header)+100))
        self.rows=[['_']*size for _ in range(23)];self.steps=0
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

def expected_bits(phases,pairs,w):
    output=''
    for q,(x,y) in zip(phases,pairs):
        for _ in range(q):x,y=-y,x
        output+=bits(x,w)+bits(y,w)
    return output


def require(ok,message):
    if not ok:raise AssertionError(message)

def phase(f,address):
    a=[0]*9
    for j in range(8,-1,-1):address,a[j]=divmod(address,1<<f)
    require(address==0,'coordinate range')
    parity=a[0]^a[1]^a[2]^a[3]^a[5]^a[6]
    return (f-parity.bit_count()+2*a[7].bit_count())%4

def exercise(code,params,pairs=None,alter=None,cpu=None):
    f,r,P,S,w=params;Q=1<<(9*f);count=300 if alter=='prefix' else P*Q*S*r
    phases=[phase(f,(j//(S*r))%Q) for j in range(count)]
    if pairs is None:
        lim=min(12,(1<<(w-1))-1)
        pairs=[((7*j)%(2*lim+1)-lim,(11*j)%(2*lim+1)-lim) for j in range(count)]
    header=''.join(gamma(n) for n in params)
    data=''.join(bits(x,w)+bits(y,w) for x,y in pairs)
    try:expected=expected_bits(phases,pairs,w)
    except OverflowError:expected=None
    if alter=='extra':data+='1';expected=None
    if alter=='short':data=data[:-1];expected=None
    if cpu is None:cpu=CPU(header,data)
    else:cpu.supply(header,data)
    start=cpu.steps
    try:cpu.run(code)
    except Rejected:
        require(expected is None or alter=='prefix','unexpected literal rejection')
        require(cpu.rows[0]==cpu.before[0] and cpu.rows[1]==cpu.before[1],'public rejection mutation')
        if alter=='prefix':
            o=cpu.origin[2]
            require(cpu.rows[2][o:o+len(expected)]==list(expected),'incomplete f>1 staged prefix arithmetic')
            require(cpu.head[2]==o+len(expected),'staged prefix length')
        return cpu,cpu.steps-start,False,count
    require(expected is not None and alter!='prefix','missed range/cardinality guard')
    cpu.check(expected)
    return cpu,cpu.steps-start,True,count

def main():
    path=Path(sys.argv[1]).resolve();m=load(path);code,alphabet=m.compile_phase()
    require(set(alphabet)==set('_01|'),'alphabet')
    require(m.SELECTED_LINEAR==(3,3,3,3,0,3,3,2,0),'linear source pin')
    require(m.SELECTED_ROWS==(111,111,111,111,0,111,111,0,0),'quadratic source pin')
    require(m.SELECTED_CONSTANT==1,'absolute phase source pin')
    cases=steps=accepted=coefficients=0
    cpu=CPU('','',capacity=100000);identities=tuple(map(id,cpu.rows))
    for params in [(1,2,2,2,5),(1,1,1,1,3),(1,2,1,3,6)]:
        cpu,n,ok,count=exercise(code,params,cpu=cpu)
        cases+=1;steps+=n;accepted+=ok;coefficients+=count
        require(tuple(map(id,cpu.rows))==identities,'retained tape identities')
    phases=[phase(1,a) for a in range(512)]
    for q in range(4):
        where=phases.index(q)
        for component in (0,1):
            pairs=[(0,0)]*512;xy=[0,0];xy[component]=-2;pairs[where]=tuple(xy)
            _,n,ok,count=exercise(code,(1,1,1,1,2),pairs)
            cases+=1;steps+=n;accepted+=ok;coefficients+=count
    for alter in ('extra','short'):
        _,n,ok,count=exercise(code,(1,1,1,1,4),alter=alter)
        cases+=1;steps+=n;accepted+=ok
    prefixes=[]
    for f in (2,3,4):
        _,n,ok,count=exercise(code,(f,1,1,1,5),alter='prefix')
        cases+=1;steps+=n
        prefixes.append({'f':f,'staged_coefficients':count,'complete_packet':False})
    variants=[
        ('omit absolute tensor phase',m.compile_phase(constant=0)[0]),
        ('omit quadratic cross terms',m.compile_phase(rows=tuple((1<<i) if x&1 else 0 for i,x in enumerate(m.SELECTED_LINEAR)))[0]),
        ('wrong original-owner commit',[('write',1,'1') if x==('write',1,'0') else x for x in code]),
    ]
    controls=[]
    for name,mutant in variants:
        require(mutant!=code,'effective mutation')
        try:exercise(mutant,(1,1,1,1,5))
        except AssertionError:controls.append(name)
        else:raise AssertionError('undetected '+name)
    print(json.dumps({'status':'PASS_INDEPENDENT_NATIVE_PHASE','cases':cases,'accepted':accepted,'full_fixture_coefficients':coefficients,'transitions':steps,'locations':len(code),'tapes':23,'controls':controls,'incomplete_prefixes':prefixes,'phase_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'limitations':'All-f theorem rests on proof; f=2,3,4 checks are deliberately incomplete packets, with verified staged prefixes.'},sort_keys=True))
if __name__=='__main__':main()
