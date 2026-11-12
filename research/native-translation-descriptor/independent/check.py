"""Independent dense local CPU and complete descriptor/translation census.
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
    b=format(n,'b'); return '0'*(len(b)-1)+b

def reversal_steps(P,R,B):
    E=P.bit_length()+R.bit_length()+B.bit_length()
    return 53*P*R*B+23*P*R+71*P+54*R+54*B+28*E-30*(P.bit_count()+R.bit_count()+B.bit_count())-8

def unary_binary_steps(n):
    # Sum of successive quotient lengths is 2*n-popcount(n).
    return 19*n-12*n.bit_count()+19*n.bit_length()+7

def gamma_steps(n):
    return 47*n-30*n.bit_count()+33*n.bit_length()-42

def complete_steps(shape):
    f,r,P,S,w=shape; B=2*S*r*w*(1<<(8*f)); R=1<<f
    E=sum(2*x.bit_length()-1 for x in shape)
    return (42+sum(gamma_steps(x) for x in shape)+(5*E+3)
        +(11*f+12)+(16*S*r*w+10*S*r+10*S+7)
        +(47*(B-2*S*r*w)+150*f+4)
        +unary_binary_steps(P)+unary_binary_steps(B)
        +reversal_steps(P,R,B)
        +7*(P.bit_length()+B.bit_length()+2*f+r+S+w+1)+56+42+1)

def check(code, shape, *, cpu=None, bad=None):
    f,r,P,S,w=shape; Q=1<<f; B=2*S*r*w*(1<<(8*f)); V=P*Q*B
    data=''.join('1' if (((i*13+7)^(i>>3)^(i>>9)).bit_count()&1) else '0' for i in range(V))
    fields=[''.join(map(gamma,shape)),data]
    if bad=='short':fields[1]=data[:-1]
    elif bad=='extra':fields[1]+='1'
    elif bad=='header':fields[0]=fields[0][:-1]+'|'
    elif bad=='symbol':fields[1]=data[:V//3]+'|'+data[V//3+1:]
    if cpu is None:cpu=CPU(25,V+sum(shape)+1024)
    cpu.supply(fields)
    try:steps,counts=cpu.run(code)
    except Rejected:
        need(bad is not None,'unexpected rejection')
        need(cpu.rows[:2]==cpu.before[:2],'failure public preservation')
        return cpu,0
    need(bad is None,'missed malformed packet')
    desired=[row[:] for row in cpu.before];o=cpu.origin[1]
    # Flat address complement on only coordinate zero; no stack/chunk oracle.
    for i in range(V):
        source=(i//(Q*B))*(Q*B)+(Q-1-(i//B)%Q)*B+i%B
        desired[1][o+i]=1+int(data[source])
    need(cpu.rows==desired,'exact selected translation and all private/exterior cells')
    need(cpu.head==cpu.origin,'all successful heads')
    need(steps==complete_steps(shape),'independent complete helper census')
    need(counts[1]==[V+1,V,4*V],'retained same-owner DATA census')
    return cpu,steps

def main():
    path=Path(sys.argv[1]).resolve();spec=importlib.util.spec_from_file_location('translation_subject',path)
    source_digest=hashlib.sha256(path.read_bytes()).hexdigest()
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    code,alphabet=m.compile_translation();need(set(alphabet)==set(SYMBOLS),'alphabet')
    cases=steps=0
    for shape in ((1,1,1,1,1),(1,2,1,1,3),(1,1,2,2,2),(1,3,2,1,1),(1,1,1,3,5),(1,2,3,2,4),(2,1,1,1,1)):
        _,n=check(code,shape);cases+=1;steps+=n
    cpu=CPU(25,32000);ids=tuple(map(id,cpu.rows));history=0
    for shape in ((1,2,2,2,3),(1,1,1,1,1),(1,1,3,2,4)):
        cpu,n=check(code,shape,cpu=cpu);cases+=1;steps+=n
        need(tuple(map(id,cpu.rows))==ids,'one retained inventory')
        new=sum(cpu.high[t]-cpu.low[t]+1 for t in range(2,25))
        need(new>=history,'monotone history');history=new
    for bad in ('short','extra','header','symbol'):check(code,(1,1,1,1,2),bad=bad)
    controls=[]
    def detect(broken,label):
        try:check(broken,(1,1,1,1,2))
        except (AssertionError,Rejected):controls.append(label)
        else:raise AssertionError('undetected mutation: '+label)
    broken=list(code)
    for i,ins in enumerate(code):
        if ins[:2]==('write',m.DATA) and ins[2]=='1':broken[i]=('write',m.DATA,'0')
    detect(broken,'corrupted original-owner commit')
    ports=m.REVERSE_PORTS;m.REVERSE_PORTS=(ports[1],ports[0],*ports[2:])
    wrong,_=m.compile_translation();m.REVERSE_PORTS=ports
    detect(wrong,'wrong collapsed prefix/row descriptors')
    broken=[]
    for op,*args in code:
        if op=='goto':args[0]+=1
        elif op=='read':args[1]={s:p+1 for s,p in args[1].items()}
        broken.append((op,*args))
    detect([('goto',1)]+broken,'functionally correct extra instruction')
    need(hashlib.sha256(path.read_bytes()).hexdigest()==source_digest,'source changed during review')
    print(json.dumps({'status':'PASS_INDEPENDENT_TRANSLATION','program_sha256':source_digest,
        'locations':len(code),'complete_cases':cases,'includes_actual_dimension_f2':True,'transitions':steps,
        'malformed_controls':4,'mutations':controls,'private_history_span':history,
        'exact_helper_census':True},sort_keys=True))

if __name__=='__main__':main()
