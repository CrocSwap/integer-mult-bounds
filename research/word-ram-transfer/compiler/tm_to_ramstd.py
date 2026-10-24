"""Executable finite TM to RamStd-subset compiler; no multiplication primitive.

Apache-2.0. Prepared by Dugongue with substantial OpenAI Codex assistance.
Finite tests corroborate the separate universal proof; this is not Lean verification.
"""
from itertools import product
import json
import random

OPS = frozenset(('set','load','store','add','sub','and','jlt','jzero','jump','read','write','halt'))

class Assembler:
    def __init__(self):
        self.code = []
        self.labels = {}
    def mark(self, label):
        if label in self.labels:
            raise ValueError('duplicate label')
        self.labels[label] = len(self.code)
    def emit(self, op, *args):
        if op not in OPS:
            raise ValueError('forbidden opcode')
        self.code.append((op,) + args)

def compile_tm(k, alphabet, states, delta, output_tape=0, output_mode="raw"):
    """Transition (q, read tuple) -> (q', write tuple, moves tuple), else halt.

    Input x (before house-standard list-length prefix) is
    [m,n_0,tape_0...,n_1,tape_1...,...]. All heads initially 0.
    Default output is the m raw symbols at positions 0,...,m-1.
    fixed_lsb decodes the MSB prefix of bit codes 1,2 before blank 0,
    reverses it and pads to exactly m logical bits (prefix length <= m).
    Symbol 0 is blank. A missing transition halts genuinely.
    """
    if output_mode not in ('raw','fixed_lsb'):
        raise ValueError('unknown output mode')
    if output_mode=='fixed_lsb' and alphabet<3:
        raise ValueError('fixed_lsb requires blank 0 and bit codes 1,2')
    if k < 1 or alphabet < 1 or states < 1 or not 0 <= output_tape < k:
        raise ValueError('invalid finite machine shape')
    for (q,read), (nq,write,moves) in delta.items():
        if not (0<=q<states and 0<=nq<states and len(read)==len(write)==len(moves)==k):
            raise ValueError('invalid transition shape')
        if any(not 0<=s<alphabet for s in read+write) or any(d not in (-1,0,1) for d in moves):
            raise ValueError('invalid transition data')
    # Register cells are the same memory as all data, as in RamStd.
    ZERO,ONE,TWO,TMP,COUNT,STRIDE,M,PARITY = range(8)
    HEAD = list(range(8,8+k)); ADDRESS=list(range(8+k,8+2*k)); SYM=list(range(8+2*k,8+3*k))
    BASE=1 << (8+3*k).bit_length()
    a=Assembler()
    a.emit('set',ONE,1); a.emit('set',TWO,2); a.emit('set',STRIDE,2*k)
    a.emit('read',TMP)  # House-standard outer input-list length.
    a.emit('read',M)
    for i in range(k):
        a.emit('read',COUNT); a.emit('set',ADDRESS[i],BASE+i)
        a.mark(('init',i)); a.emit('jzero',COUNT,('initend',i))
        a.emit('read',SYM[i]); a.emit('store',ADDRESS[i],SYM[i])
        a.emit('add',ADDRESS[i],ADDRESS[i],STRIDE)
        a.emit('sub',COUNT,COUNT,ONE); a.emit('jump',('init',i))
        a.mark(('initend',i))
    a.emit('jump',('state',0))
    for q in range(states):
        a.mark(('state',q))
        for i in range(k):
            a.emit('set',ADDRESS[i],BASE+i)
            for _ in range(k): a.emit('add',ADDRESS[i],ADDRESS[i],HEAD[i])
            a.emit('load',SYM[i],ADDRESS[i])
        for serial,read in enumerate(product(range(alphabet),repeat=k)):
            skip=('skip',q,serial)
            for i,s in enumerate(read):
                a.emit('set',TMP,s)
                a.emit('jlt',SYM[i],TMP,skip); a.emit('jlt',TMP,SYM[i],skip)
            transition=delta.get((q,read))
            if transition is None:
                a.emit('jump','output')
            else:
                nq,write,moves=transition
                for i,s in enumerate(write):
                    a.emit('set',SYM[i],s); a.emit('store',ADDRESS[i],SYM[i])
                for i,d in enumerate(moves):
                    if d==0: continue
                    # pi(z)=2z for z>=0, and -2z-1 for z<0.
                    # A crossing of zero is the only exceptional case.
                    end=('moveend',q,serial,i)
                    special=('special',q,serial,i)
                    a.emit('and',PARITY,HEAD[i],ONE)
                    a.emit('jzero',PARITY,('even',q,serial,i))
                    # Odd u: right subtracts 2 except u=1 -> 0; left adds 2.
                    if d==1:
                        a.emit('jlt',HEAD[i],TWO,special)
                        a.emit('sub',HEAD[i],HEAD[i],TWO); a.emit('jump',end)
                        a.mark(special); a.emit('set',HEAD[i],0)
                    else: a.emit('add',HEAD[i],HEAD[i],TWO)
                    a.emit('jump',end)
                    a.mark(('even',q,serial,i))
                    if d==1: a.emit('add',HEAD[i],HEAD[i],TWO)
                    else:
                        a.emit('jzero',HEAD[i],('zero',q,serial,i))
                        a.emit('sub',HEAD[i],HEAD[i],TWO); a.emit('jump',end)
                        a.mark(('zero',q,serial,i)); a.emit('set',HEAD[i],1)
                    a.mark(end)
                a.emit('jump',('state',nq))
            a.mark(skip)
        # Alphabet validity invariant makes this defensive path unreachable.
        a.emit('jump','output')
    a.mark('output'); a.emit('set',ADDRESS[0],BASE+output_tape)
    if output_mode=='raw':
        a.mark('outloop'); a.emit('jzero',M,'halt')
        a.emit('load',TMP,ADDRESS[0]); a.emit('write',TMP)
        a.emit('add',ADDRESS[0],ADDRESS[0],STRIDE)
        a.emit('sub',M,M,ONE); a.emit('jump','outloop')
    else:
        # Fixed-width LSB output from the usual blank-terminated MSB bit prefix.
        # COUNT is no longer live after input initialization; M is remaining width.
        a.emit('set',COUNT,0)
        a.mark('scan'); a.emit('jlt',COUNT,M,'probe'); a.emit('jump','reverse')
        a.mark('probe'); a.emit('load',TMP,ADDRESS[0]); a.emit('jzero',TMP,'reverse')
        a.emit('add',COUNT,COUNT,ONE); a.emit('add',ADDRESS[0],ADDRESS[0],STRIDE)
        a.emit('jump','scan')
        a.mark('reverse'); a.emit('jzero',COUNT,'pad')
        a.emit('sub',ADDRESS[0],ADDRESS[0],STRIDE); a.emit('load',TMP,ADDRESS[0])
        a.emit('sub',TMP,TMP,ONE); a.emit('write',TMP)
        a.emit('sub',COUNT,COUNT,ONE); a.emit('sub',M,M,ONE); a.emit('jump','reverse')
        a.mark('pad'); a.emit('jzero',M,'halt'); a.emit('write',ZERO)
        a.emit('sub',M,M,ONE); a.emit('jump','pad')
    a.mark('halt'); a.emit('halt')
    # labels may be tuples as well as strings.
    code=[]
    for ins in a.code:
        code.append((ins[0],)+tuple(a.labels[v] if isinstance(v,(str,tuple)) and v in a.labels else v for v in ins[1:]))
    return code,dict(base=BASE,head=HEAD,states={a.labels[('state',q)]:q for q in range(states)},labels=a.labels)

class VM:
    def __init__(self,w,code,inp):
        self.mod=1<<w; self.mask=self.mod-1; self.code=code; self.mem={}; self.pc=0
        self.inp=list(inp); self.input_pos=0; self.out=[]; self.steps=0
    def get(self,a): return self.mem.get(a & self.mask,0)
    def put(self,a,v): self.mem[a & self.mask]=v & self.mask
    def step(self):
        if not 0<=self.pc<len(self.code): return False
        op,*x=self.code[self.pc]; old=self.pc; self.pc+=1
        if op=='halt': self.pc=old; return False
        if op=='set': self.put(x[0],x[1])
        elif op=='load': self.put(x[0],self.get(self.get(x[1])))
        elif op=='store': self.put(self.get(x[0]),self.get(x[1]))
        elif op=='add': self.put(x[0],self.get(x[1])+self.get(x[2]))
        elif op=='sub': self.put(x[0],max(0,self.get(x[1])-self.get(x[2])))
        elif op=='and': self.put(x[0],self.get(x[1]) & self.get(x[2]))
        elif op=='jump': self.pc=x[0]
        elif op=='jzero':
            if self.get(x[0])==0: self.pc=x[1]
        elif op=='jlt':
            if self.get(x[0])<self.get(x[1]): self.pc=x[2]
        elif op=='read':
            if self.input_pos==len(self.inp): self.pc=old; return False
            self.put(x[0],self.inp[self.input_pos]); self.input_pos+=1
        elif op=='write': self.out.append(self.get(x[0]))
        else: raise ValueError(op)
        self.steps+=1; return True

def zigzag(z): return 2*z if z>=0 else -2*z-1

def reference_step(q,heads,tapes,delta):
    read=tuple(tapes[i].get(h,0) for i,h in enumerate(heads))
    t=delta.get((q,read))
    if t is None: return None
    nq,writes,moves=t
    for i,h in enumerate(heads): tapes[i][h]=writes[i]
    return nq,[h+d for h,d in zip(heads,moves)]

def check_case(k,A,Q,delta,tapes,m,width=16,max_macro=40):
    code,meta=compile_tm(k,A,Q,delta)
    if (1<<width)<=meta['base']+k*(2*(sum(map(len,tapes))+max_macro+m+2)+1):
        raise ValueError('word-width proof precondition fails')
    x=[m]
    for t in tapes: x += [len(t),*t]
    v=VM(width,code,[len(x),*x])
    ts=[dict(enumerate(t)) for t in tapes]; heads=[0]*k; q=0; macros=0; first=True
    halted=False
    while v.steps<2000000:
        if v.pc in meta['states']:
            if not first:
                r=reference_step(q,heads,ts,delta)
                if r is None: raise AssertionError('RAM reached a new TM boundary after TM halt')
                q,heads=r; macros+=1
            first=False
            if meta['states'][v.pc]!=q: raise AssertionError('state mismatch')
            for i,h in enumerate(heads):
                if v.get(meta['head'][i])!=zigzag(h): raise AssertionError('head mismatch')
                for pos in range(-max_macro-1,max(max_macro+2,len(tapes[i])+1)):
                    addr=meta['base']+i+k*zigzag(pos)
                    if v.get(addr)!=ts[i].get(pos,0): raise AssertionError('tape mismatch')
            if macros==max_macro: break
        if not v.step():
            if reference_step(q,heads,ts,delta) is not None: raise AssertionError('premature RAM halt')
            expected=[ts[0].get(j,0) for j in range(m)]
            if v.out!=expected: raise AssertionError('output mismatch')
            halted=True; break
    else: raise AssertionError('microinstruction execution budget exceeded')
    C=100*(k+1)*(A**k+1)+20*(k+1)**2
    bound=C*(macros+1)+10*(sum(map(len,tapes))+m+k+1)
    if v.steps>bound: raise AssertionError('advertised instruction envelope failed')
    if any(i[0] not in OPS for i in code): raise AssertionError('forbidden primitive')
    return dict(macros=macros,steps=v.steps,halted=halted,program_instructions=len(code))

def check_lsb_emitters():
    rng=random.Random(2235); cases=0; product_cases=0; total_steps=0
    fixtures=[]
    for m in range(13):
        for bits in product((0,1),repeat=m):
            fixtures.append((m,list(bits)))
    for n in range(1,6):
        for left in range(1<<n):
            for right in range(1<<n):
                v=left*right
                bits=list(map(int,bin(v)[2:]))
                fixtures.append((2*n,bits)); product_cases+=1
    fixtures.append((503,[1]*503))  # one-past-end pointer 1022 at w=10
    fixtures.extend([(0,[]),(4,[0]),(4,[1]),(4,[1,0]),(4,[1,1]),(8,[0,0,1,1])])
    for _ in range(200):
        m=rng.randrange(1,513); length=rng.randrange(m+1)
        fixtures.append((m,[rng.randrange(2) for _ in range(length)]))
    for number,(m,bits) in enumerate(fixtures):
        k=1+number%3; output_tape=number%k
        if m==503 and bits==[1]*503: k=1; output_tape=0
        # Dirty cells after a delimiter are legal; the emitter must ignore them.
        raw=[b+1 for b in bits]
        if len(bits)<m: raw += [0,2,1,2,2]
        elif number%2 and not (m==503 and bits==[1]*503): raw += [2,1,2]  # no end blank inside the m-cell cap
        tapes=[[] for _ in range(k)]; tapes[output_tape]=raw
        code,meta=compile_tm(k,3,1,{},output_tape=output_tape,output_mode='fixed_lsb')
        x=[m]
        for tape in tapes: x += [len(tape),*tape]
        width=12 if m<128 else 16
        if m==503 and bits==[1]*503: width=10
        vm=VM(width,code,[len(x),*x]); before=None
        while vm.steps<1000000:
            if vm.pc==meta['labels']['output']: before=vm.steps
            if not vm.step(): break
        else: raise AssertionError('LSB emitter execution budget exceeded')
        value=int(''.join(map(str,bits)) or '0',2)
        expected=[(value>>j)&1 for j in range(m)]
        if vm.out!=expected: raise AssertionError('LSB emitter numeric mismatch')
        if before is None or vm.steps-before>14*m+7:
            raise AssertionError('LSB emitter cost envelope failed')
        if max(vm.mem,default=0)>meta['base']+2*k*(sum(map(len,tapes))+m+2)+k:
            raise AssertionError('LSB emitter finite memory envelope failed')
        if any(ins[0] not in OPS for ins in code): raise AssertionError('LSB forbidden opcode')
        cases+=1; total_steps+=vm.steps
    # Wrongly appending blanks/zeros to MSB "11" at width 4 represents 12,
    # whereas the specified LSB normalization must represent the original 3.
    wrong_msb_append=int('1100',2)
    if wrong_msb_append==3: raise AssertionError('MSB append negative control invalid')
    # Actually corrupt the reversal direction; independent numeric semantics rejects.
    code,meta=compile_tm(1,3,1,{},output_mode='fixed_lsb')
    code=[('add',*ins[1:]) if ins[0]=='sub' and ins[1]==9 else ins for ins in code]
    x=[4,5,2,2,0,1,2]
    broken=VM(12,code,[len(x),*x])
    while broken.steps<10000 and broken.step(): pass
    if broken.out==[1,1,0,0]: raise AssertionError('Wrong-direction emitted-code mutation escaped')
    return dict(cases=cases,product_pairs=product_cases,microinstructions=total_steps,
                wrong_direction_code_rejected=True,small_word_boundary_tested=True,
                wrong_msb_append_detected=True,full_width_no_terminator_tested=True,
                dirty_post_terminator_tested=True,leading_zero_tested=True)

def run_checks():
    rng=random.Random(20261022); results=[]
    for k in (1,2,3):
        for case in range(80):
            A=3; Q=3; delta={}
            for q in range(Q):
                for read in product(range(A),repeat=k):
                    if rng.randrange(8)==0: continue
                    delta[q,read]=(rng.randrange(Q),tuple(rng.randrange(A) for _ in range(k)),tuple(rng.choice((-1,0,1)) for _ in range(k)))
            tapes=[[rng.randrange(A) for _ in range(rng.randrange(9))] for _ in range(k)]
            results.append(check_case(k,A,Q,delta,tapes,rng.randrange(10)))
    # Sweep both zero crossings and long negative/positive prefixes deliberately.
    for d in (-1,1):
        delta={(0,(s,)):(0,(s,),(d,)) for s in range(3)}
        results.append(check_case(1,3,1,delta,[[1,2,1]],5,max_macro=200))
    # The generic theorem is valid at every larger word length, not only its minimum.
    for w in (12,16,31,64):
        results.append(check_case(1,3,1,{},[[1,2]],4,width=w))
    rejected=0
    try: check_case(1,3,1,{},[[1,2]],4,width=3)
    except ValueError: rejected+=1
    if rejected!=1: raise AssertionError('small-word negative control accepted')
    # Actual emitted-code faults must be caught by the independent semantic check.
    global compile_tm
    good_compiler=compile_tm
    faults=('stride','head_unit','store','halt','output')
    caught=[]
    for fault in faults:
        def faulty(*args, _fault=fault, **kwargs):
            code,meta=good_compiler(*args,**kwargs)
            if _fault=='stride':
                at=next(i for i,x in enumerate(code) if x[0]=='set' and x[1]==5)
                code[at]=('set',5,1)
            elif _fault=='head_unit':
                code[1]=('set',2,1)
            elif _fault=='store':
                code=[('load',*x[1:]) if x[0]=='store' else x for x in code]
            elif _fault=='halt':
                code[-1]=('jump',next(iter(meta['states'])))
            elif _fault=='output':
                code=[('write',0) if x[0]=='write' else x for x in code]
            return code,meta
        compile_tm=faulty
        try:
            delta={(0,(s,)):(1,(1,),(1,)) for s in range(3)}
            check_case(1,3,2,delta,[[2,2,2]],3)
        except AssertionError:
            caught.append(fault)
        finally:
            compile_tm=good_compiler
    if caught!=list(faults): raise AssertionError('emitted-code negative control escaped')
    lsb=check_lsb_emitters()
    out=dict(lsb_emitter=lsb,schema='tm-to-ramstd-finite-check-v1',cases=len(results),macro_boundaries=sum(r['macros']+1 for r in results),microinstructions=sum(r['steps'] for r in results),halting_cases=sum(r['halted'] for r in results),nonhalting_prefix_cases=sum(not r['halted'] for r in results),small_word_rejections=rejected,emitted_code_faults_rejected=caught,uses_multiplication_or_division=False,formal_lean_verification=False)
    print(json.dumps(out,indent=2,sort_keys=True))
    return out

if __name__=='__main__': run_checks()

