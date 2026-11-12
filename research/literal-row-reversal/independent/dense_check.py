"""Independent local CPU, address formula and exact reversal census.
Prepared for CubeJerry with OpenAI assistance. Apache-2.0.
No author interpreter, checker or expected-output routine is used.
"""
from pathlib import Path
import hashlib, importlib.util, itertools, json, sys

def need(value, message):
    if not value: raise AssertionError(message)

class Rejected(Exception): pass

class CPU:
    def __init__(self, capacity):
        self.origin = [19+2*t for t in range(13)]
        self.head = self.origin.copy()
        self.rows = [['_']*capacity for _ in range(13)]
        for t,o in enumerate(self.origin): self.rows[t][o-6:o-2] = list('10|1')
        self.low = self.origin.copy(); self.high = self.origin.copy()
    def supply(self, fields):
        need(self.head == self.origin, 'retired heads before reuse')
        for t,text in enumerate(fields):
            o = self.origin[t]
            self.rows[t][o:] = ['_']*(len(self.rows[t])-o)
            self.rows[t][o:o+len(text)] = list(text)
            self.rows[t][o+len(text)+1:o+len(text)+5] = list('01|0')
        self.before = [r.copy() for r in self.rows]
    def run(self, code):
        pc = steps = 0; counts = [[0,0,0] for _ in range(13)]
        while steps < 5_000_000:
            op,*args = code[pc]; pc += 1; steps += 1
            if op in ('read','write','move'):
                t = args[0]; need(type(t) is int and 0<=t<13, 'fixed tape set')
                counts[t][('read','write','move').index(op)] += 1
                self.low[t] = min(self.low[t],self.head[t]); self.high[t] = max(self.high[t],self.head[t])
            if op == 'read':
                symbol = self.rows[t][self.head[t]]
                if symbol not in args[1]: raise Rejected('undefined local branch')
                pc = args[1][symbol]
            elif op == 'write':
                need(args[1] in '_01|','four-symbol alphabet'); self.rows[t][self.head[t]] = args[1]
            elif op == 'move':
                need(args[1] in (-1,1),'unit movement'); self.head[t] += args[1]
                need(0<=self.head[t]<len(self.rows[t]),'test capacity')
                self.low[t] = min(self.low[t],self.head[t]); self.high[t] = max(self.high[t],self.head[t])
            elif op == 'goto': pc = args[0]
            elif op == 'halt': return steps,counts
            else: raise AssertionError('unapproved instruction')
        raise AssertionError('test budget exhausted')

def total(P,R,B):
    """Derived from helper costs and loop invariants, not a fit."""
    E = P.bit_length()+R.bit_length()+B.bit_length()
    pop = P.bit_count()+R.bit_count()+B.bit_count()
    return 53*P*R*B+23*P*R+71*P+54*R+54*B+28*E-30*pop-8

def check(code,shape,data=None,mutation=None,cpu=None,count_check=True):
    P,R,B = shape; V = P*R*B
    if data is None:
        data = ''.join(str(((i*i+3*i+7)^(i>>2)^(i>>5)).bit_count()%2) for i in range(V))
    output = ''.join(data[(i//(R*B))*R*B+(R-1-(i//B)%R)*B+i%B] for i in range(V))
    fields = [format(x,'b') for x in shape]+[data]
    if mutation == 'short': fields[3] = data[:-1]
    if mutation == 'extra': fields[3] += '1'
    if mutation == 'leading_zero': fields[0] = '0'+fields[0]
    if mutation == 'zero': fields[1] = '0'
    if mutation == 'symbol': fields[2] += '|'
    if cpu is None: cpu = CPU(max(512,3*(V+sum(shape)+50)))
    cpu.supply(fields)
    try: steps,counts = cpu.run(code)
    except Rejected:
        need(mutation is not None,'unexpected rejection')
        need(cpu.rows[:4] == cpu.before[:4],'public precommit rejection'); return cpu,0
    need(mutation is None,'missed descriptor/cardinality rejection')
    desired = [r.copy() for r in cpu.before]; o = cpu.origin[3]
    desired[3][o:o+V] = list(output)
    need(cpu.rows == desired,'complete records, prefix isolation, exterior, cleanup')
    need(cpu.head == cpu.origin,'all heads restored')
    if count_check:
        need(steps == total(*shape),'exact independently derived transition census')
        need(counts[3] == [V+1,V,4*V],'public DATA read/write/move census')
        for t in range(3):
            ell = shape[t].bit_length()
            need(counts[t] == [ell+1,0,2*ell],'descriptor read/return census')
    return cpu,steps

def main():
    path = Path(sys.argv[1]).resolve()
    spec = importlib.util.spec_from_file_location('reversal_subject',path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    code,alphabet = m.compile_reverse(); need(set(alphabet)==set('_01|'),'alphabet')
    cases = steps = exhaustive = 0
    for shape in itertools.product((1,2,4),(1,2,3,7,16),(1,2,5,17,33)):
        _,n = check(code,shape); cases += 1; steps += n
    for shape in ((1,2,3),(2,2,2),(1,3,2)):
        for word in itertools.product('01',repeat=shape[0]*shape[1]*shape[2]):
            _,n = check(code,shape,''.join(word)); cases += 1; exhaustive += 1; steps += n
    cpu = CPU(10000); identities = tuple(map(id,cpu.rows)); last_history = 0
    for shape in ((3,17,13),(1,1,1),(2,9,21)):
        cpu,n = check(code,shape,cpu=cpu); cases += 1; steps += n
        need(tuple(map(id,cpu.rows))==identities,'stable backing identity')
        history = sum(cpu.high[t]-cpu.low[t]+1 for t in range(4,13))
        need(history>=last_history,'historical backing cannot shrink'); last_history=history
    for mutation in ('short','extra','leading_zero','zero','symbol'):
        check(code,(2,3,5),mutation=mutation)
    controls=[]; broken=list(code)
    for i,ins in enumerate(code):
        if ins[:2]==('write',m.RECORD) and ins[2] in ('0','1'):
            need(code[i+1]==('move',m.RECORD,1),'staging mutation seam')
            broken[i]=('write',m.OUTPUT,ins[2]); broken[i+1]=('move',m.OUTPUT,1)
    try: check(broken,(2,3,5))
    except AssertionError: controls.append('omit internal-bit order restoration')
    else: raise AssertionError('record mutation survived')
    # A harmless extra entry jump preserves every value but breaks exact T.
    shifted=[('goto',1)]
    for op,*args in code:
        if op=='goto': args[0]+=1
        if op=='read': args[1]={k:v+1 for k,v in args[1].items()}
        shifted.append((op,*args))
    check(shifted,(2,3,5),count_check=False)
    try: check(shifted,(2,3,5))
    except AssertionError: controls.append('functionally correct extra instruction')
    else: raise AssertionError('cost mutation survived')
    broken=[('write',m.DATA,'1') if x==('write',m.DATA,'0') else x for x in code]
    try: check(broken,(2,3,5))
    except AssertionError: controls.append('corrupt public installation')
    else: raise AssertionError('installation mutation survived')
    print(json.dumps({'status':'PASS_INDEPENDENT_LITERAL_REVERSAL','cases':cases,
        'exhaustive_binary_inputs':exhaustive,'transitions':steps,'locations':len(code),
        'controls':controls,'rejection_controls':5,'retained_private_span':last_history,
        'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'exact_cost':'53PRB+23PR+71P+54R+54B+28E-30sum(popcount)-8'},sort_keys=True))

if __name__=='__main__': main()
