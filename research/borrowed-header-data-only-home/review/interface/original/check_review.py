"""Read-only independent sparse-Graph review of B's frozen adapter."""
from pathlib import Path
from hashlib import sha256
import atexit,copy,importlib.util,json,random,sys,tempfile,time
HERE=Path(__file__).resolve().parent
SUBJECT=Path('/workspace/scratch/92c9920affc2/worker-b/research/borrowed-header-data-home')
cache=tempfile.TemporaryDirectory(prefix='borrow-review-');atexit.register(cache.cleanup)
sys.dont_write_bytecode=True;sys.pycache_prefix=str(Path(cache.name)/'absent')


def need(ok,label):
    if not ok:raise ValueError(label)


need(sha256((SUBJECT/'FREEZE.json').read_bytes()).hexdigest()=='0f3f4bae39a8f630c56799912c41f2babecf0493531e043d6a6e0cb21ef717a7','subject freeze')
freeze=json.loads((SUBJECT/'FREEZE.json').read_text())
for pin in freeze['files']:
    raw=(SUBJECT/pin['path']).read_bytes();need(len(raw)==pin['bytes'] and sha256(raw).hexdigest()==pin['sha256'],'frozen subject bytes')
spec=importlib.util.spec_from_file_location('review_borrowed_adapter',SUBJECT/'adapter.py')
A=importlib.util.module_from_spec(spec);sys.modules[spec.name]=A;spec.loader.exec_module(A)


class Capture:
    def __init__(self):self.rules={};self.count=0
    def state(self,name):
        n=self.count;self.count+=1;self.rules[n]=[];return n
    def add(self,state,target,tests=(),writes=(),moves=()):
        self.rules[state].append((target,tuple(tests),tuple(writes),tuple(moves)))


def relocation():
    checked=0
    for rank in range(1,10):
        code=A.core(rank)
        for header in (3,34):
            capture=Capture();need(A.embed(capture,code,-1,header)==0,'embedded start')
            for pc,(op,*args) in enumerate(code):
                port=lambda t:header if t==0 else 3+t
                nxt=pc+1 if pc+1<len(code) else -1
                if op=='read':expected=[(dst,((port(args[0]),s),),(),()) for s,dst in args[1].items()]
                elif op=='write':expected=[(nxt,(),((port(args[0]),args[1]),),())]
                elif op=='move':expected=[(nxt,(),(),((port(args[0]),args[1]),))]
                elif op=='goto':expected=[(args[0],(),(),())]
                elif op=='halt':expected=[(-1,(),(),())]
                else:raise ValueError('unknown source opcode')
                need(capture.rules[pc]==expected,'direct-PC injection mismatch')
                need(not any(t==header for _,_,wr,_ in expected for t,_ in wr),'native header write')
                checked+=1
    return checked


class Rejected(ValueError):pass


class Sparse:
    def __init__(self,g,payloads,headers):
        reachable=set();pending=[g.start]
        while pending:
            name=pending.pop()
            if name in reachable or name=='HALT':continue
            reachable.add(name);pending.extend(r.target for r in g.rules[name])
        self.reachable_header_writes=sum(t in headers for name in reachable for r in g.rules[name] for t,_ in r.writes)
        self.unreachable_header_writes=sum(t in headers for name,rows in g.rules.items() if name not in reachable
                                           for r in rows for t,_ in r.writes)
        need(self.reachable_header_writes==0,'reachable borrowed-header write')
        need(self.unreachable_header_writes>0,'reservation-entry boundary control')
        self.names=list(g.rules);self.loc={n:i for i,n in enumerate(self.names)};self.loc['HALT']=-1
        self.rows=[[(self.loc[r.target],r.tests,r.writes,r.moves) for r in g.rules[n]] for n in self.names]
        self.pc=self.loc[g.start];self.origins=[19*t-401 for t in range(35)];self.heads=self.origins.copy()
        self.tapes=[{o:'^',o-7:'1',o+1000000:'0'} for o in self.origins]
        for t,text in [(0,'^'+payloads[0]+'|'+payloads[1]+'|$')]+[(t,'^'+h+'|$101') for t,h in headers.items()]:
            self.tapes[t].update({self.origins[t]+i:s for i,s in enumerate(text)})
        self.low=self.origins.copy();self.high=self.origins.copy();self.high[33]+=10*len(payloads[0])
        self.writes=[0]*35;self.steps=0
    def run(self,stop=None):
        target=None if stop is None else self.loc[stop]
        while self.pc!=-1 and self.pc!=target:
            matches=[]
            for rule in self.rows[self.pc]:
                if all(self.tapes[t].get(self.heads[t],'_')==s for t,s in rule[1]):matches.append(rule)
            if not matches:raise Rejected('no matching local-symbol rule')
            need(len(matches)==1,'nondeterministic Graph')
            nxt,_,writes,moves=matches[0]
            for t,s in writes:
                if s=='_':self.tapes[t].pop(self.heads[t],None)
                else:self.tapes[t][self.heads[t]]=s
                self.writes[t]+=1
            for t,d in moves:
                need(d in (-1,0,1),'nonunit Graph movement');self.heads[t]+=d
                self.low[t]=min(self.low[t],self.heads[t]);self.high[t]=max(self.high[t],self.heads[t])
            self.pc=nxt;self.steps+=1
            need(self.steps<100000000,'review execution cap')
    def fields(self):
        o=self.origins[0];t=self.tapes[0];pos=o+1;out=[]
        for _ in range(2):
            bits=[]
            while t.get(pos) in ('0','1'):bits.append(t[pos]);pos+=1
            need(t.get(pos)=='|','HOME delimiter');pos+=1;out.append(''.join(bits))
        need(t.get(pos)=='$','HOME endpoint');return tuple(out)


def gamma(n):
    b=bin(n)[2:];return '0'*(len(b)-1)+b
def header(shape):return ''.join(gamma(x) for x in shape)
def encode(values):return ''.join(format(x%64,'06b') for z in values for x in z)
def operator(values):
    out=list(values)
    for mask in (256,128):
        for i in range(512):
            if i&mask:continue
            a,b=out[i];c,d=out[i|mask];rows=(a-b+c+d,a+b-c+d,a+b+c-d,-a+b+c+d)
            need(all(x%2==0 for x in rows),'oracle exact halves')
            out[i],out[i|mask]=(rows[0]//2,rows[1]//2),(rows[2]//2,rows[3]//2)
    return out


def physical():
    rng=random.Random(8032026);values=[(4*rng.randrange(-1,2),4*rng.randrange(-1,2)) for _ in range(512)]
    data=encode(values);parked=''.join(str(rng.randrange(2)) for _ in data);v=len(data)
    hs={3:header((1,1,1,1,6,2)),34:header((1,1,1,1,6,1<<(v+5)))}
    need(len(hs[34])>v,'genuinely E larger than DATA')
    graph,stages=A.compile_home(2,header_tapes=(3,34,3));cpu=Sparse(graph,(parked,data),hs)
    before=copy.deepcopy(cpu.tapes);old_high=cpu.high.copy();answers=[];snapshot=None
    for event in range(3):
        old_data=data;values=operator(values);data=encode(values);answers.append(data)
        cpu.run(stages[event]['core_return'])
        need(cpu.fields()==(parked,old_data),'HOME wrote before native return')
        need(cpu.heads[3 if event!=1 else 34]==cpu.origins[3 if event!=1 else 34]+1,'borrowed origin+1')
        need(all(cpu.heads[t]==cpu.origins[t]+2 for t in range(4,34)),'native origin+2')
        if event==0:snapshot=copy.deepcopy(cpu)
        cpu.run(stages[event]['primitive_return'])
        need(cpu.fields()==(parked,old_data),'HOME wrote during private install')
        need(all(cpu.tapes[t]==before[t] for t in range(4,34)),'native private retirement')
        need(cpu.heads==cpu.origins,'all heads before scatter')
        cpu.run(None if event==2 else stages[event+1]['adapter_entry'])
        need(cpu.fields()==(parked,data),'exact rank2 DATA-only scatter')
        need(all(a>=b for a,b in zip(cpu.high,old_high)),'historical backing reduced')
        old_high=cpu.high.copy()
    need(cpu.writes[0]==3*v and cpu.writes[3]==cpu.writes[34]==0,'public write counts')
    need(cpu.heads==cpu.origins,'final heads')
    need(all(cpu.tapes[t]==before[t] for t in range(1,35)),'final private/header/exterior equality')
    rejected=[]
    for kind in ('short','long'):
        bad=copy.deepcopy(snapshot);end=bad.origins[4]+2+v
        if kind=='short':bad.tapes[4].pop(end-1)
        else:bad.tapes[4][end]='1'
        try:bad.run()
        except Rejected:pass
        else:raise ValueError('returned extent mismatch accepted')
        need(bad.writes[0]==0,'mismatch HOME write')
        need(bad.tapes[0]==snapshot.tapes[0] and bad.tapes[3]==snapshot.tapes[3] and bad.tapes[34]==snapshot.tapes[34],
             'mismatch public bytes changed')
        rejected.append(kind)
    return {'rank':2,'V':v,'header_lengths':[len(hs[3]),len(hs[34])],
            'header_sequence':[3,34,3],'steps':cpu.steps,'HOME_writes':cpu.writes[0],
            'header_writes':[cpu.writes[3],cpu.writes[34]],'returned_extent_faults':rejected,
            'reachable_header_writes':cpu.reachable_header_writes,
            'unreachable_header_writes':cpu.unreachable_header_writes,
            'signed_origins':True,'final_output_sha256':sha256(data.encode()).hexdigest()}


if __name__=='__main__':
    started=time.monotonic();count=relocation();packet=physical()
    result={'marker':'PASS_INDEPENDENT_BORROWED_HEADER_DATA_REVIEW','embedded_instructions_checked':count,
            'packet':packet,'subject_freeze_sha256':sha256((SUBJECT/'FREEZE.json').read_bytes()).hexdigest(),
            'elapsed_seconds':round(time.monotonic()-started,3)}
    (HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,sort_keys=True))
