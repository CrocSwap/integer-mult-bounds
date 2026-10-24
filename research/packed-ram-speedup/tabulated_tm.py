"""Uniform packed-window TM tabulation: exact bounded-word operational model.
Dugongue with substantial OpenAI Codex assistance. Apache-2.0.
No word multiplication/division, no timing oracle and no pre-supplied table.
This is not a Lean certificate or a fully emitted RamStd instruction program.
"""
from collections import defaultdict
from random import Random
import json


def need(ok,msg):
    if not ok: raise ValueError(msg)

class Words:
    def __init__(self,w):
        self.w=w; self.mask=(1<<w)-1; self.mem=defaultdict(int); self.ops=0; self.high=0
    def fit(self,x):
        need(0<=x<=self.mask,'word/address overflow');return x
    def add(self,a,b):self.ops+=1;return self.fit(a+b)
    def sub(self,a,b):self.ops+=1;return max(0,a-b)
    def shl(self,a,b):self.ops+=1;return self.fit(a<<b)
    def shr(self,a,b):self.ops+=1;return a>>b
    def band(self,a,b):self.ops+=1;return a&b
    def bor(self,a,b):self.ops+=1;return a|b
    def bnot(self,a):self.ops+=1;return self.mask^a
    def load(self,a):self.ops+=1;self.fit(a);return self.mem[a]
    def store(self,a,x):self.ops+=1;self.fit(a);self.fit(x);self.mem[a]=x;self.high=max(self.high,a)
    def test(self,a,b):self.ops+=1;return a==b
    def tick(self):self.ops+=1

class Tabulator:
    def __init__(self,k,A,Q,delta,r,w):
        need(k>=1 and A>=2 and Q>=1 and r>=1 and r&(r-1)==0,'machine/epoch contract')
        self.k,self.A,self.Q,self.delta,self.r=k,A,Q,dict(delta),r
        for (state,reads),(nq,writes,moves) in self.delta.items():
            need(0<=state<Q and 0<=nq<Q and len(reads)==len(writes)==len(moves)==k,'fixed transition shape')
            need(all(0<=x<A for x in reads+writes) and all(x in (-1,0,1) for x in moves),'fixed transition symbol/move')
        # Fixed power-of-two fields ensure all scaling is by shifts, not MUL.
        c=1
        while (1<<c)<A:c<<=1
        self.c=c; self.flog=c.bit_length()-1; self.s=max(1,(Q-1).bit_length())
        self.L=2*r+1;self.B=4*r;self.blog=self.B.bit_length()-1
        self.wbits=c*self.L; self.keybits=self.s+k*self.wbits
        self.rowlog=(2*k+2).bit_length();self.rowstride=1<<self.rowlog
        need(w>max(self.keybits+self.rowlog+10,c*self.B+1),'finite-word table contract')
        self.v=Words(w);self.symbol_mask=(1<<c)-1;self.window_mask=(1<<self.wbits)-1
        self.rows=1<<self.keybits
        # Fixed machine-dependent base above the finite register/scratch prefix.
        self.tablebase=max(512,1<<(64*k+127).bit_length())
        self.database=self.tablebase+(self.rows<<self.rowlog)+512
        self.hlog=(2*k-1).bit_length();self.H=1<<self.hlog
        self.setup_ops=0
        self.build()

    def dispatch(self,q,read):
        # M is fixed: each rule test expands to finitely many branch comparisons.
        v=self.v
        for (state,symbols),transition in self.delta.items():
            v.tick()
            if not v.test(q,state):continue
            equal=True
            for a,b in zip(read,symbols):
                if not v.test(a,b):equal=False;break
            if equal:return transition
        return None

    def local(self,q,windows):
        v=self.v;heads=[self.r for _ in range(self.k)];elapsed=0;halt=0
        for _ in range(self.r):
            v.tick();read=[]
            for i in range(self.k):
                shift=v.shl(heads[i],self.flog)
                read.append(v.band(v.shr(windows[i],shift),self.symbol_mask))
            tr=self.dispatch(q,read)
            if tr is None:halt=1;break
            q,symbols,moves=tr
            for i in range(self.k):
                shift=v.shl(heads[i],self.flog);mask=v.shl(self.symbol_mask,shift)
                windows[i]=v.bor(v.band(windows[i],v.bnot(mask)),v.shl(symbols[i],shift))
                heads[i]=v.add(heads[i],1) if moves[i]==1 else v.sub(heads[i],1) if moves[i]==-1 else heads[i]
            elapsed=v.add(elapsed,1)
        return [q,halt,elapsed]+windows+heads

    def build(self):
        v=self.v;before=v.ops
        for key in range(self.rows):
            v.tick();q=v.band(key,(1<<self.s)-1);payload=v.shr(key,self.s);windows=[]
            for _ in range(self.k):
                windows.append(v.band(payload,self.window_mask));payload=v.shr(payload,self.wbits)
            row=self.local(q,windows)
            address=v.add(self.tablebase,v.shl(key,self.rowlog))
            for value in row:v.store(address,value);address=v.add(address,1)
        self.setup_ops=v.ops-before

    def address(self,tape,block):
        v=self.v;return v.add(self.database,v.add(v.shl(block,self.hlog),tape))

    def get_window(self,tape,start,length=None):
        v=self.v;L=self.L if length is None else length
        need(1<=L<=self.B,'packed chunk length')
        mask=v.sub(v.shl(1,v.shl(L,self.flog)),1)
        block=v.shr(start,self.blog);j=v.band(start,self.B-1);shift=v.shl(j,self.flog)
        low=v.shr(v.load(self.address(tape,block)),shift)
        available=v.sub(self.B,j)
        v.tick()
        if available>=L:return v.band(low,mask)
        rest=v.load(self.address(tape,v.add(block,1)))
        remaining=v.sub(L,available);bits=v.shl(remaining,self.flog);restmask=v.sub(v.shl(1,bits),1)
        return v.band(v.bor(low,v.shl(v.band(rest,restmask),v.shl(available,self.flog))),mask)

    def put_window(self,tape,start,window,length=None):
        v=self.v;L=self.L if length is None else length
        need(1<=L<=self.B,'packed chunk length')
        block=v.shr(start,self.blog);j=v.band(start,self.B-1)
        available=v.sub(self.B,j);count=min(available,L);v.tick()
        bits=v.shl(count,self.flog);shift=v.shl(j,self.flog);mask=v.sub(v.shl(1,bits),1)
        addr=self.address(tape,block);clear=v.shl(mask,shift)
        result=v.bor(v.band(v.load(addr),v.bnot(clear)),v.shl(v.band(window,mask),shift));v.store(addr,result)
        v.tick()
        if available>=L:return
        count=v.sub(L,available);bits=v.shl(count,self.flog);mask=v.sub(v.shl(1,bits),1)
        addr=self.address(tape,v.add(block,1));rest=v.shr(window,v.shl(available,self.flog))
        v.store(addr,v.bor(v.band(v.load(addr),v.bnot(mask)),v.band(rest,mask)))

    def get_symbol(self,tape,pos):
        v=self.v;block=v.shr(pos,self.blog);j=v.band(pos,self.B-1)
        return v.band(v.shr(v.load(self.address(tape,block)),v.shl(j,self.flog)),self.symbol_mask)
    def put_symbol(self,tape,pos,value):
        v=self.v;block=v.shr(pos,self.blog);j=v.band(pos,self.B-1);shift=v.shl(j,self.flog)
        mask=v.shl(self.symbol_mask,shift);addr=self.address(tape,block)
        v.store(addr,v.bor(v.band(v.load(addr),v.bnot(mask)),v.shl(value,shift)))

    def macro(self,q,heads):
        v=self.v;before=v.ops;key=q;keyshift=self.s
        for i in range(self.k):
            window=self.get_window(i,v.sub(heads[i],self.r))
            key=v.bor(key,v.shl(window,keyshift));keyshift=v.add(keyshift,self.wbits)
        address=v.add(self.tablebase,v.shl(key,self.rowlog));row=[]
        for _ in range(2*self.k+3):row.append(v.load(address));address=v.add(address,1)
        for i in range(self.k):
            self.put_window(i,v.sub(heads[i],self.r),row[3+i])
            heads[i]=v.sub(v.add(heads[i],row[3+self.k+i]),self.r)
        need(v.ops-before<=250*(self.k+1),'constant-cost macro envelope')
        return row[0],heads,bool(row[1]),row[2],v.ops-before


def reference_step(q,heads,tapes,delta):
    symbols=tuple(tapes[i].get(heads[i],0) for i in range(len(heads)))
    tr=delta.get((q,symbols))
    if tr is None:return None
    nq,writes,moves=tr
    for i in range(len(heads)):tapes[i][heads[i]]=writes[i];heads[i]+=moves[i]
    return nq


def uniform_parameters(n,k,A,Q,d=2,a=8):
    """Fixed-machine polynomial-envelope constants d,a; no execution-time input.
    Target implements integer scaling by fixed constants with repeated addition.
    The power-of-two divisions below are shifts. n is a supplied bit-length header.
    """
    need(n>=0 and k>=1 and A>=2 and Q>=1 and d>=1 and a>=8,'uniform parameter contract')
    lam=(n+2).bit_length()-1;ell=lam+1
    c=1
    while (1<<c)<A:c<<=1
    K=1<<(k-1).bit_length();denominator_log=6+(K.bit_length()-1)+(c.bit_length()-1)
    q=lam>>denominator_log;r=1<<max(0,q.bit_length()-1)
    statebits=max(1,(Q-1).bit_length());rowlog=(2*k+2).bit_length();hlog=(2*k-1).bit_length()
    width=(a+d+statebits+rowlog+hlog+4*k*c+32)*ell
    origin=1<<(a+d*ell)
    keybits=statebits+k*c*(2*r+1)
    return dict(epoch=r,block=4*r,field_bits=c,keybits=keybits,rows=1<<keybits,origin=origin,width=width,lambda_floor=lam)


def run_packed(k,A,Q,delta,inputs,output_tape,output_cap,codec_type,a=8,d=2,word_width=None):
    """All-length model composition for a supplied fixed halting TM.
    inputs maps distinct tape numbers to (r-bit digits, logical length, bit order).
    codec_type is the pinned supplied Codec implementation, not a runtime oracle.
    The run computes r from the total logical length, generates all tables anew,
    and halts only on an actual missing TM transition. The caller must establish
    the fixed polynomial T+n+m envelope; no runtime T/fuel is supplied.
    """
    need(A>=3,'packed binary codec needs blank and two distinct bit symbols')
    n=sum(length for _,length,_ in inputs.values())
    para=uniform_parameters(n,k,A,Q,d,a)
    r=para['epoch'];w=para['width'] if word_width is None else word_width
    need(w>=para['width'],'caller word width below uniform sufficient bound')
    need(0<=output_tape<k and output_cap>=0,'output protocol')
    sim=Tabulator(k,A,Q,delta,r,w);codec=codec_type(r,sim.c,w)
    # Reserve explicit distinct codec banks before data; source lists model those
    # bounded arrays. The generic proof also allocates IO/descriptor banks.
    codec_words=(1<<((r<<sim.flog)+3))+(1<<(r+2))+512
    sim.database=sim.v.add(sim.database,codec_words)
    heads=[para['origin'] for _ in range(k)];q=0;macro_calls=elapsed=0
    setup=sim.v.ops+codec.setup_ops
    before=sim.v.ops+codec.ops
    for tape,(digits,length,order) in inputs.items():
        need(0<=tape<k,'input tape')
        chunks=codec.input_to_tm(digits,length,order)
        for j,chunk in enumerate(chunks):
            count=min(r,length-(j<<codec.rlog))
            pos=sim.v.add(para['origin'],j<<codec.rlog)
            sim.put_window(tape,pos,chunk,count)
    while True:
        q,heads,halt,count,_=sim.macro(q,heads)
        macro_calls+=1;elapsed+=count
        if halt:break
    def coded_output():
        offset=0
        while offset<output_cap:
            count=min(r,output_cap-offset)
            yield sim.get_window(output_tape,sim.v.add(para['origin'],offset),count)
            offset+=r
    result=codec.tm_to_output(coded_output(),output_cap)
    return result,dict(TM_transitions=elapsed,macro_calls=macro_calls,
        generated_table_rows=sim.rows,setup_primitive_operations=setup,
        runtime_primitive_operations=sim.v.ops+codec.ops-before,
        parameter_setup_scope='Additional O(log(n+2)) fixed-loop operations; not an exact emitted instruction count',
        epoch=r,logical_input_bits=n,actual_word_width=w,
        supplied_runtime_fuel=False,all_tables_generated_for_this_input=True,
        scope='Uniform supplied-machine operational model; not emitted RamStd or Lean certificate')


def check():
    rng=Random(20261022);cases=boundaries=transitions=0;max_macro=0;max_setup=0;tables=0
    for k,A,Q,r in [(1,2,2,1),(1,2,2,2),(1,2,2,4),(1,3,2,1),(1,3,2,2),(2,2,2,1),(2,2,2,2)]:
      for sample in range(4):
        delta={}
        import itertools
        for q in range(Q):
          for ss in itertools.product(range(A),repeat=k):
            if rng.randrange(5):delta[q,ss]=(rng.randrange(Q),tuple(rng.randrange(A) for _ in range(k)),tuple(rng.choice([-1,0,1]) for _ in range(k)))
        sim=Tabulator(k,A,Q,delta,r,64);tables+=sim.rows;max_setup=max(max_setup,sim.setup_ops)
        # The actual complete table is built, including unreachable/invalid entries.
        for trial in range(8):
          sim.v.mem={a:v for a,v in sim.v.mem.items() if a<sim.database};sim.v.mem=defaultdict(int,sim.v.mem)
          origin=4096+trial;heads=[origin for _ in range(k)];rh=[0]*k;tapes=[{} for _ in range(k)];q=rq=0
          for i in range(k):
            for z in range(-10,11):
              a=rng.randrange(A);tapes[i][z]=a;sim.put_symbol(i,origin+z,a)
          for macro_index in range(12):
            q,heads,halt,elapsed,ops=sim.macro(q,heads);max_macro=max(max_macro,ops)
            count=0
            while count<r:
              rr=reference_step(rq,rh,tapes,delta)
              if rr is None:break
              rq=rr;count+=1
            terminal=delta.get((rq,tuple(tapes[i].get(rh[i],0) for i in range(k)))) is None
            need(count==elapsed and q==rq,'table state/time')
            need(heads==[origin+h for h in rh],'signed head displacement')
            for i in range(k):
              for z in range(-10-12*r-2,10+12*r+3):need(sim.get_symbol(i,origin+z)==tapes[i].get(z,0),'tape or frame mismatch')
            if halt:need(terminal,'false halt')
            if not halt:need(elapsed==r,'false incomplete macro')
            transitions+=elapsed;boundaries+=1
            if halt:break
          cases+=1
    # Dirty neighboring fields and arbitrary window alignment must be preserved.
    sim=Tabulator(1,2,1,{},4,64);frames=0
    for start in range(128,160):
      for b in range(6,12):sim.v.store(sim.address(0,b),(1<<sim.B)-1)
      before=[sim.get_symbol(0,z) for z in range(96,192)]
      sim.put_window(0,start,0)
      after=[sim.get_symbol(0,z) for z in range(96,192)]
      need(all(v==(0 if start<=z<start+sim.L else before[z-96]) for z,v in zip(range(96,192),after)),'window dirty frame')
      frames+=1
    # Real nonhalting computation cannot halt just because an epoch ended.
    delta={(0,(0,)):(0,(0,),(1,))}
    sim=Tabulator(1,2,1,delta,4,64);q=0;h=[1024]
    for _ in range(30):q,h,halt,e,_=sim.macro(q,h);need(not halt and e==4,'artificial epoch halt')
    need(h==[1144],'nonhalting advance')
    # Corrupt one addressed row and require state/head/tape detection.
    sim=Tabulator(1,2,1,{},2,64);sim.v.store(sim.tablebase,1)
    q,_,_,_,_=sim.macro(0,[1024]);need(q!=0,'mutated table control escaped')
    try:Tabulator(2,2,2,{},2,10)
    except ValueError:pass
    else:raise ValueError('insufficient word width accepted')
    parameter_cases=0
    for k in [1,2,3,8]:
      for A in [2,3,5]:
       for exponent in [0,1,8,64,128,256,512,1024]:
        n=(1<<exponent)-2 if exponent else 0;n=max(0,n)
        para=uniform_parameters(n,k,A,3)
        need(para['origin']>16*((n+2)**2+para['epoch']+n+1),'polynomial origin')
        need(para['width']>para['keybits']+(2*k+2).bit_length()+10,'uniform table width')
        if para['lambda_floor']>=max(64*(1<<(k-1).bit_length())*para['field_bits'],128):
            need(16*para['keybits']<=para['lambda_floor'],'sublinear full-table budget')
        parameter_cases+=1
    return {'uniform_parameter_cases':parameter_cases,'status':'PASS','machine_cases':cases,'macro_boundaries':boundaries,'TM_transitions':transitions,'precomputed_rows':tables,'maximum_macro_word_operations':max_macro,'maximum_setup_word_operations':max_setup,'dirty_window_frames':frames,'nonhalting_macros':30,'mutated_table_detected':True,'undersized_word_rejected':True,'word_mul_or_div':False,'scope':'exact finite operational model; not emitted RamStd code, Lean proof or improved TM kappa'}

if __name__=='__main__':print(json.dumps(check(),indent=2))
