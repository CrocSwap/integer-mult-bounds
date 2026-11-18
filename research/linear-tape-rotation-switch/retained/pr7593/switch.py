"""Literal fixed-tape canonical padded-rotation switch predicate.

Prepared for @CubeJerry with OpenAI assistance. Apache-2.0.
The mathematical formulas and child closure are Nick Petalas's #7504.
Python loops below expand fixed graph macros only, never runtime data.
"""
from hashlib import sha256
import json

B,L,E=2,3,4
SYMBOLS=(0,1,B,L,E)
H_IN,S_IN,A_IN,J_IN,X_IN,OUT=range(6)
COUNT,WIDTH,S,A,J,X,LAST,TEMP=range(6,14)
PRIVATE=tuple(range(6,14)); NUMBERS=(S,A,J,X,LAST,TEMP)
TAPES=14

class Builder:
    def __init__(self): self.code=[]; self.labels={}; self.counter=0
    def fresh(self,prefix='q'):
        self.counter+=1; return prefix+'_'+str(self.counter)
    def mark(self,label):
        if label in self.labels: raise ValueError('duplicate label '+label)
        self.labels[label]=len(self.code)
    def op(self,*instruction): self.code.append(instruction)
    def read(self,tape,branches):
        self.op('R',tape,{s:branches.get(s,'reject') for s in SYMBOLS})
    def jump(self,label): self.op('J',label)
    def finish(self):
        out=[]
        for ins in self.code:
            if ins[0]=='R': out.append(('R',ins[1],{s:self.labels[t] for s,t in ins[2].items()}))
            elif ins[0]=='J': out.append(('J',self.labels[ins[1]]))
            else: out.append(ins)
        return tuple(out)

    def rewind(self,t):
        loop=self.fresh('rewind'); back=self.fresh('back'); done=self.fresh('home')
        self.op('M',t,-1); self.mark(loop)
        self.read(t,{0:back,1:back,B:back,E:back,L:done})
        self.mark(back); self.op('M',t,-1); self.jump(loop)
        self.mark(done); self.op('M',t,1)

    def zero_test(self,t,yes,no):
        loop=self.fresh('zero'); adv=self.fresh('zadv'); z=self.fresh('iszero'); nz=self.fresh('nonzero')
        self.mark(loop); self.read(t,{0:adv,1:nz,E:z})
        self.mark(adv); self.op('M',t,1); self.jump(loop)
        self.mark(z); self.rewind(t); self.jump(yes)
        self.mark(nz); self.rewind(t); self.jump(no)

    def decrement(self,t):
        loop=self.fresh('dec'); zero=self.fresh('borrow'); one=self.fresh('borrow_done')
        self.mark(loop); self.read(t,{0:zero,1:one})
        self.mark(zero); self.op('W',t,1); self.op('M',t,1); self.jump(loop)
        self.mark(one); self.op('W',t,0); self.rewind(t)

    def increment(self,t):
        loop=self.fresh('inc'); one=self.fresh('carry'); zero=self.fresh('carry_done')
        self.mark(loop); self.read(t,{0:zero,1:one})
        self.mark(one); self.op('W',t,0); self.op('M',t,1); self.jump(loop)
        self.mark(zero); self.op('W',t,1); self.rewind(t)

    def zero_word(self,t):
        loop=self.fresh('clear_number'); bit=self.fresh('digit'); done=self.fresh('number_zero')
        self.mark(loop); self.read(t,{0:bit,1:bit,E:done})
        self.mark(bit); self.op('W',t,0); self.op('M',t,1); self.jump(loop)
        self.mark(done); self.rewind(t)

    def copy_word(self,source,target):
        loop=self.fresh('copy'); z=self.fresh('copy0'); o=self.fresh('copy1'); done=self.fresh('copied')
        self.mark(loop); self.read(source,{0:z,1:o,E:done})
        for bit,label in ((0,z),(1,o)):
            self.mark(label); self.op('W',target,bit)
            self.op('M',source,1); self.op('M',target,1); self.jump(loop)
        self.mark(done); self.rewind(source); self.rewind(target)

    def shift_right(self,t):
        loop=self.fresh('half'); z=self.fresh('half0'); o=self.fresh('half1'); done=self.fresh('half_done')
        self.op('M',t,1); self.mark(loop); self.read(t,{0:z,1:o,E:done})
        for bit,label in ((0,z),(1,o)):
            self.mark(label); self.op('M',t,-1); self.op('W',t,bit)
            self.op('M',t,1); self.op('M',t,1); self.jump(loop)
        self.mark(done); self.op('M',t,-1); self.op('W',t,0); self.op('M',t,1); self.rewind(t)

    def shift_left(self,t):
        loops=[self.fresh('double0'),self.fresh('double1')]; done=self.fresh('double_done')
        self.jump(loops[0])
        for carry in (0,1):
            self.mark(loops[carry]); writes=[self.fresh('double_digit'),self.fresh('double_digit')]
            self.read(t,{0:writes[0],1:writes[1],E:done if carry==0 else 'reject'})
            for old in (0,1):
                self.mark(writes[old]); self.op('W',t,carry); self.op('M',t,1); self.jump(loops[old])
        self.mark(done); self.rewind(t)

    def compare(self,t,u,lt,eq,gt,skip=0):
        loops=[self.fresh('cmp_lt'),self.fresh('cmp_eq'),self.fresh('cmp_gt')]
        for _ in range(skip): self.op('M',t,1); self.op('M',u,1)
        self.jump(loops[1])
        for state in range(3):
            t0=self.fresh('cmp_t0'); t1=self.fresh('cmp_t1'); end=self.fresh('cmp_end')
            pairs={(a,b):self.fresh('cmp_pair') for a in (0,1) for b in (0,1)}
            done=self.fresh('cmp_done')
            self.mark(loops[state]); self.read(t,{0:t0,1:t1,E:end})
            self.mark(t0); self.read(u,{0:pairs[0,0],1:pairs[0,1]})
            self.mark(t1); self.read(u,{0:pairs[1,0],1:pairs[1,1]})
            for (a,b),label in pairs.items():
                self.mark(label); self.op('M',t,1); self.op('M',u,1)
                self.jump(loops[state if a==b else (0 if a<b else 2)])
            self.mark(end); self.read(u,{E:done})
            self.mark(done); self.rewind(t); self.rewind(u); self.jump((lt,eq,gt)[state])

    def cleanup(self,outcome):
        for t in range(6): self.rewind(t)
        for t in PRIVATE:
            self.rewind(t)
            loop=self.fresh('retire'); bit=self.fresh('erase'); done=self.fresh('retired')
            self.mark(loop); self.read(t,{0:bit,1:bit,E:bit,B:done})
            self.mark(bit); self.op('W',t,B); self.op('M',t,1); self.jump(loop)
            self.mark(done); self.rewind(t)
            self.op('M',t,-1); self.op('W',t,B); self.op('M',t,1)
        self.op('H',outcome)


def compile_query(mutation=None):
    """Emit one fixed finite table; mutation is a test-only constructor switch."""
    if mutation not in (None,'swap_child','drop_branch_carry','drop_padded_first'):
        raise ValueError('unknown fixed mutation')
    b=Builder()
    for t in PRIVATE:
        b.op('M',t,-1); b.op('W',t,L); b.op('M',t,1)
    out_blank=b.fresh('out_blank'); out_end=b.fresh('out_end')
    b.read(OUT,{B:out_blank}); b.mark(out_blank); b.op('M',OUT,1)
    b.read(OUT,{B:out_end}); b.mark(out_end); b.op('M',OUT,-1)
    # Copy canonical positive height. Last digit must be1; no host decode.
    h0=b.fresh('height_last0'); h1=b.fresh('height_last1')
    put0=b.fresh('height0'); put1=b.fresh('height1'); copied=b.fresh('height_copied')
    b.read(H_IN,{0:put0,1:put1})
    for bit,put,after in ((0,put0,h0),(1,put1,h1)):
        b.mark(put); b.op('W',COUNT,bit); b.op('M',COUNT,1); b.op('M',H_IN,1); b.jump(after)
    b.mark(h0); b.read(H_IN,{0:put0,1:put1})
    b.mark(h1); b.read(H_IN,{0:put0,1:put1,B:copied})
    b.mark(copied); b.op('W',COUNT,E); b.rewind(COUNT); b.rewind(H_IN)
    # WIDTH holds h+1 unary ones. COUNT keeps fixed original binary length.
    b.op('W',WIDTH,1); b.op('M',WIDTH,1)
    count_loop=b.fresh('height_countdown'); append=b.fresh('width_append'); width_done=b.fresh('width_done')
    b.mark(count_loop); b.zero_test(COUNT,width_done,append)
    b.mark(append); b.op('W',WIDTH,1); b.op('M',WIDTH,1); b.decrement(COUNT); b.jump(count_loop)
    b.mark(width_done); b.op('W',WIDTH,E); b.rewind(WIDTH)
    init=b.fresh('init_numbers'); init_bit=b.fresh('init_bit'); init_done=b.fresh('init_done')
    b.mark(init); b.read(WIDTH,{1:init_bit,E:init_done})
    b.mark(init_bit)
    for t in NUMBERS: b.op('W',t,0); b.op('M',t,1)
    b.op('M',WIDTH,1); b.jump(init)
    b.mark(init_done)
    for t in NUMBERS: b.op('W',t,E); b.rewind(t)
    b.rewind(WIDTH)
    # Exactly h+1 bits for each supplied unsigned field; blank frontier.
    for source,target in ((S_IN,S),(A_IN,A),(J_IN,J),(X_IN,X)):
        loop=b.fresh('read_field'); bit=b.fresh('field_digit'); end=b.fresh('field_end'); done=b.fresh('field_done')
        p0=b.fresh('field0'); p1=b.fresh('field1')
        b.mark(loop); b.read(WIDTH,{1:bit,E:end})
        b.mark(bit); b.read(source,{0:p0,1:p1})
        for v,label in ((0,p0),(1,p1)):
            b.mark(label); b.op('W',target,v); b.op('M',target,1); b.op('M',source,1); b.op('M',WIDTH,1); b.jump(loop)
        b.mark(end); b.read(source,{B:done})
        b.mark(done); b.rewind(source); b.rewind(target); b.rewind(WIDTH)
    # LAST=2h-2, copied from the preserved height and operated on tape.
    loop=b.fresh('copy_height'); p0=b.fresh('h_to_last0'); p1=b.fresh('h_to_last1'); done=b.fresh('last_height')
    b.mark(loop); b.read(H_IN,{0:p0,1:p1,B:done})
    for v,label in ((0,p0),(1,p1)):
        b.mark(label); b.op('W',LAST,v); b.op('M',LAST,1); b.op('M',H_IN,1); b.jump(loop)
    b.mark(done); b.rewind(H_IN); b.rewind(LAST); b.shift_left(LAST); b.decrement(LAST); b.decrement(LAST)
    # TEMP=2^h: the high bit of the h+1-bit private word.
    loop=b.fresh('limit'); adv=b.fresh('limit_advance'); done=b.fresh('limit_done')
    b.mark(loop); b.read(TEMP,{0:adv,E:done})
    b.mark(adv); b.op('M',TEMP,1); b.jump(loop)
    b.mark(done); b.op('M',TEMP,-1); b.op('W',TEMP,1); b.rewind(TEMP)
    nonzero=b.fresh('modulus_nonzero'); bounded=b.fresh('modulus_bounded')
    a_ok=b.fresh('offset_ok'); x_ok=b.fresh('address_ok'); domain=b.fresh('domain_ok')
    b.zero_test(S,'reject',nonzero); b.mark(nonzero)
    b.compare(S,TEMP,bounded,bounded,'reject'); b.mark(bounded)
    b.compare(A,S,a_ok,'reject','reject'); b.mark(a_ok)
    b.compare(X,TEMP,x_ok,'reject','reject'); b.mark(x_ok)
    b.compare(J,LAST,domain,domain,'reject'); b.mark(domain)
    b.mark('query_loop')
    b.jump('query_body'); b.mark('query_body')
    active=b.fresh('nonidentity'); not_leaf=b.fresh('nonleaf'); row_test=b.fresh('row_test')
    b.zero_test(A,'answer0',active); b.mark(active)
    b.zero_test(LAST,'answer1',not_leaf); b.mark(not_leaf)
    b.zero_test(J,'first_row',row_test); b.mark(row_test)
    b.compare(J,LAST,'interior','last_row','reject')
    b.mark('first_row'); sodd=b.fresh('first_sodd'); bothodd=b.fresh('first_bothodd')
    b.read(S,{0:'answer0',1:sodd}); b.mark(sodd); b.read(A,{0:'answer0',1:bothodd}); b.mark(bothodd)
    if mutation=='drop_padded_first': b.jump('answer0')
    else: b.compare(X,S,'answer0','answer1','answer0',skip=1)
    b.mark('last_row'); seven=b.fresh('last_seven'); sodd=b.fresh('last_sodd'); ae=b.fresh('last_ae'); ao=b.fresh('last_ao'); evenodd=b.fresh('last_evenodd')
    b.read(S,{0:seven,1:sodd})
    b.mark(seven); b.read(A,{0:'answer0',1:evenodd}); b.mark(evenodd); b.compare(X,S,'answer1','answer0','answer0')
    b.mark(sodd); b.read(A,{0:ae,1:ao})
    b.mark(ae); b.compare(X,A,'answer1','answer0','answer0')
    b.mark(ao); inside=b.fresh('last_inside'); b.compare(X,S,inside,inside,'answer0'); b.mark(inside)
    b.copy_word(A,TEMP); b.decrement(TEMP); b.compare(X,TEMP,'answer0','answer1','answer1')
    b.mark('interior')
    # Three parity bits are finite control, not numeric host registers.
    sr=[b.fresh('s_parity'),b.fresh('s_parity')]; b.read(S,{0:sr[0],1:sr[1]})
    for sd in (0,1):
        b.mark(sr[sd]); ar=[b.fresh('a_parity'),b.fresh('a_parity')]; b.read(A,{0:ar[0],1:ar[1]})
        for ad in (0,1):
            b.mark(ar[ad]); xr=[b.fresh('x_parity'),b.fresh('x_parity')]; b.read(X,{0:xr[0],1:xr[1]})
            for xd in (0,1):
                b.mark(xr[xd]); branch=1-xd if mutation=='swap_child' else xd
                b.shift_right(S); b.shift_right(A)
                if sd and branch==ad: b.increment(S)
                if branch and ad and mutation!='drop_branch_carry': b.increment(A)
                b.jump('child_reduce')
    b.mark('child_reduce'); less=b.fresh('child_lt'); equal=b.fresh('child_equal')
    b.compare(A,S,less,equal,'reject'); b.mark(equal); b.zero_word(A); b.jump(less)
    b.mark(less); b.decrement(J); b.decrement(LAST); b.decrement(LAST); b.shift_right(X); b.jump('query_loop')
    b.mark('answer0'); b.op('W',OUT,0); b.jump('success')
    b.mark('answer1'); b.op('W',OUT,1); b.jump('success')
    b.mark('success'); b.cleanup('DONE')
    b.mark('reject'); b.cleanup('REJECT')
    return b.finish(),dict(b.labels)

def digest(code):
    return sha256(json.dumps(code,separators=(',',':'),sort_keys=True).encode()).hexdigest()
