"""Independent dense CPU and direct Gaussian-integer oracle; Apache-2.0.
Prepared for CubeJerry with OpenAI assistance. Never executes the author CPU/tests.
"""
import hashlib, importlib.util, json, sys
from pathlib import Path

def load(path):
    s=importlib.util.spec_from_file_location('reviewed_egress',path)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def gamma(n):
    b=format(n,'b');return '0'*(len(b)-1)+b

def bits(n,w):
    if not -(1<<(w-1))<=n<(1<<(w-1)):raise ValueError('range')
    return format(n%(1<<w),f'0{w}b')

def oracle(pairs,d,D,w):
    a,b=1,0
    for _ in range(D):a,b=a+b,b-a
    den=1<<(d+D);out=''
    for x,y in pairs:
        for z in (a*x-b*y,b*x+a*y):
            q=abs(z)//den;out+=bits(-q if z<0 else q,w)
    return out

class Dense:
    def __init__(self,header,data):
        self.orig=[25+3*i for i in range(18)]
        size=max(1024,4*(len(data)+len(header)+1))
        self.rows=[['_']*size for _ in range(18)]
        self.head=self.orig.copy();self.low=self.orig.copy();self.high=self.orig.copy()
        for i,o in enumerate(self.orig):self.rows[i][o-5:o-1]=list('1|01')
        for i,s in ((0,header),(1,data)):
            o=self.orig[i];self.rows[i][o-1]='|';self.rows[i][o:o+len(s)]=list(s)
        self.before=[r.copy() for r in self.rows];self.steps=0
    def run(self,code,budget=30_000_000):
        pc=0
        while self.steps<budget:
            op,*arg=code[pc];pc+=1;self.steps+=1
            if op=='read':
                t,jumps=arg;s=self.rows[t][self.head[t]]
                if s not in jumps:raise ValueError('literal rejection')
                pc=jumps[s]
            elif op=='write':t,s=arg;self.rows[t][self.head[t]]=s
            elif op=='move':
                t,d=arg
                if d not in (-1,1):raise AssertionError('nonlocal movement')
                self.head[t]+=d;self.low[t]=min(self.low[t],self.head[t]);self.high[t]=max(self.high[t],self.head[t])
                if not 0<=self.head[t]<len(self.rows[t]):raise AssertionError('dense capacity')
            elif op=='goto':pc=arg[0]
            elif op=='halt':return
            else:raise AssertionError('unexpected opcode')
        raise ValueError('CPU budget')
    def check(self,expected,old_length):
        if self.rows[0]!=self.before[0]:raise AssertionError('header mutation')
        data=self.before[1].copy();o=self.orig[1]
        data[o:o+old_length]=['_']*old_length;data[o:o+len(expected)]=list(expected)
        if self.rows[1]!=data:raise AssertionError('output or old tail')
        if self.head!=self.orig:raise AssertionError('head return')
        for i in range(2,18):
            if self.rows[i]!=self.before[i]:raise AssertionError(f'private cleanup {i}')

def exercise(code,p,d,D,w,pairs,huge=False):
    r=(1<<89)+17 if huge else 1
    hdr=''.join(gamma(x) for x in (p,d,r,D,1,1,1,1,w))
    H=p+2*d+4;data=''.join(bits(x,H) for pair in pairs for x in pair)
    try:expected=oracle(pairs,d,D,w)
    except ValueError:expected=None
    cpu=Dense(hdr,data)
    try:cpu.run(code)
    except ValueError:
        if expected is not None:raise
        if cpu.rows[0]!=cpu.before[0] or cpu.rows[1]!=cpu.before[1]:raise AssertionError('failed call mutated public data')
        return cpu.steps
    if expected is None:raise AssertionError('missed range rejection')
    cpu.check(expected,len(data));return cpu.steps

def main():
    path=Path(sys.argv[1]).resolve();m=load(path);code,alphabet=m.compile_egress()
    if set(alphabet)!={'_','|','0','1'}:raise AssertionError('alphabet')
    cases=steps=0
    for D in range(1,9):
        p,d=9,D+1;H=p+2*d+4
        pairs=[(0,0),(1,-1),(-1,1),(13,-29),(-(1<<(H-1)),0)]
        steps+=exercise(code,p,d,D,H+2,pairs);cases+=1
        pairs=[((j*7)%37-18,(j*11)%41-20) for j in range(1<<D)]
        steps+=exercise(code,p,d,D,p+2,pairs);cases+=1
    for p,d,D,w in [(1,1,1,3),(17,1,1,19),(3,6,5,22),(1,40,37,90)]:
        steps+=exercise(code,p,d,D,w,[(3,-5),(-9,17),(0,0)],True);cases+=1
    controls=[]
    for kind in ('commit_bit','output_cleanup','odd_gaussian_row'):
        mutant=list(code)
        if kind=='odd_gaussian_row':
            old=m.numerator_rows;m.numerator_rows=lambda mode:((1,0),(0,1))
            mutant=m.compile_egress()[0];m.numerator_rows=old
        else:
            changes=0
            for at,ins in enumerate(mutant):
                if kind=='commit_bit' and ins==('write',m.DATA,'0'):
                    mutant[at]=('write',m.DATA,'1');changes+=1
                if kind=='output_cleanup' and ins==('write',m.OUTPUT,m.BLANK):
                    mutant[at]=('goto',at+1);changes+=1
            if changes==0:raise AssertionError('empty mutation')
        try:exercise(mutant,4,2,1,12,[(64,-32),(7,13)])
        except (ValueError,AssertionError):controls.append(kind)
        else:raise AssertionError('undetected '+kind)
    print(json.dumps(dict(status='PASS_INDEPENDENT_DENSE_EGRESS',cases=cases,transitions=steps,instructions=len(code),negative_controls=controls,source_sha256=hashlib.sha256(path.read_bytes()).hexdigest()),sort_keys=True))

if __name__=='__main__':main()
