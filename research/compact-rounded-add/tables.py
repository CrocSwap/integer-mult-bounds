"""Bit-constant numerator and total rounded ADD as literal flat tables.

Construction-time integers only. Runtime rows are the retained six-opcode ABI.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction
from source_binding import need, vendor
B=vendor('compact_exact_builder','vendor/exact_scalar_tables.py')


def compile_compact(coefficient, *, mutant=None):
    q=Fraction(coefficient);a,den=q.numerator,q.denominator
    L=max(abs(a).bit_length(),den.bit_length());K=L+2
    d,o=0,den
    while o%2==0:d+=1;o//=2
    need(o<=125,'fixed current odd-divisor domain, not arbitrary logarithmic divisor')
    c=den//2
    if mutant=='tie-down':c=max(0,c-1)
    sign=-1 if a<0 else 1
    coeff=[((den>>j)&1,sign*((abs(a)>>j)&1)) for j in range(L-1,-1,-1)]
    if mutant=='lost-negative':coeff=[(x,abs(y)) for x,y in coeff]
    if mutant=='lost-leading':coeff[0]=(0,0)
    b=B.Builder();b.request(('entry',));maxcarry=0
    reject=('reject',)
    def go(k):b.goto(k)
    def branch(port,cases):b.branch(port,cases,reject)
    def move(port,n):
        for _ in range(abs(n)):b.emit('move',port,1 if n>0 else -1)
    def publics():move(0,1);move(1,1)
    def reset(nextkey):go(('reset',K,nextkey))
    def rewind(nextkey):go(('rewind',nextkey))
    def hstep(i,k,sx,sy,x,y,n,remaining,parity):
        nonlocal maxcarry
        beta,alpha=coeff[i];v=2*n+beta*x+alpha*y+k;z=v&1;kk=v//2
        need(abs(kk)<=4,'closed Horner carry');maxcarry=max(maxcarry,abs(kk))
        b.emit('write',2,z);move(2,1)
        if remaining is None:
            publics();go(('hscan',i,kk,x,y,parity))
        elif remaining>1:go(('hhigh',i,remaining-1,kk,sx,sy,parity))
        elif kk==2*n+beta*sx+alpha*sy-z:
            go(('hfinish',i,parity))
        else:go(reject)
    def qdigit(n,k):
        v=n+k;z=v&1;kk=(v-o*z)//2
        need(-o<=kk<=0,'closed quotient carry');return z,kk
    while b.pending:
        key=b.pending.popleft();b.mark(key);tag=key[0]
        if tag=='reject':b.emit('reject','compact rounded ADD format/range')
        elif tag=='entry':branch(2,{4:('entry-o',)})
        elif tag=='entry-o':branch(3,{4:('begin',)})
        elif tag=='begin':
            b.emit('write',2,5);move(2,1);go(('start',0,False))
        elif tag=='start':
            _,parity,seen=key;cases={x:('record',parity) for x in (0,1)}
            if seen and parity==0:cases[4]=('source-end',)
            branch(0,cases)
        elif tag=='source-end':branch(1,{4:('global-back',)})
        elif tag=='record':
            _,parity=key;b.emit('write',2,6);move(2,1);go(('init',parity))
        elif tag=='init':
            _,parity=key;branch(0,{0:('init-y',parity),1:('init-y',parity),2:('init-end',parity)})
        elif tag=='init-y':
            _,parity=key;branch(1,{0:('init-zero',parity),1:('init-zero',parity)})
        elif tag=='init-zero':
            _,parity=key;b.emit('write',2,0);move(2,1);publics();go(('init',parity))
        elif tag=='init-end':
            _,parity=key;branch(1,{2:('init-high',parity)})
        elif tag=='init-high':
            _,parity=key
            for _ in range(K):b.emit('write',2,0);move(2,1)
            b.emit('write',2,2);reset(('hscan',0,0,2,2,parity))
        elif tag=='reset':
            _,left,nxt=key
            if left:move(2,-1);go(('reset',left-1,nxt))
            else:go(('reset-back',nxt))
        elif tag=='reset-back':
            _,nxt=key;move(2,-1);branch(2,{0:('reset-public',nxt),1:('reset-public',nxt),6:('reset-ready',nxt)})
        elif tag=='reset-public':
            _,nxt=key;move(0,-1);move(1,-1);go(('reset-back',nxt))
        elif tag=='reset-ready':
            _,nxt=key;move(2,1);go(nxt)
        elif tag=='hscan':
            _,i,k,sx,sy,parity=key;cases={x:('hy',i,k,x,parity) for x in (0,1)}
            if sx in (0,1):cases[2]=('hend-y',i,k,sx,sy,parity)
            branch(0,cases)
        elif tag=='hy':
            _,i,k,x,parity=key;branch(1,{y:('hn',i,k,x,y,parity) for y in (0,1)})
        elif tag=='hn':
            _,i,k,x,y,parity=key;branch(2,{n:('hdigit',i,k,x,y,n,parity) for n in (0,1)})
        elif tag=='hdigit':
            _,i,k,x,y,n,parity=key;hstep(i,k,x,y,x,y,n,None,parity)
        elif tag=='hend-y':
            _,i,k,sx,sy,parity=key;branch(1,{2:('hhigh',i,K,k,sx,sy,parity)})
        elif tag=='hhigh':
            _,i,left,k,sx,sy,parity=key;branch(2,{n:('hhigh-digit',i,left,k,sx,sy,n,parity) for n in (0,1)})
        elif tag=='hhigh-digit':
            _,i,left,k,sx,sy,n,parity=key;hstep(i,k,sx,sy,sx,sy,n,left,parity)
        elif tag=='hfinish':
            _,i,parity=key
            nxt=('hscan',i+1,0,2,2,parity) if i+1<L else ('offset',0,0,2,2,parity)
            branch(2,{2:('hreset',nxt)})
        elif tag=='hreset':_,nxt=key;reset(nxt)
        elif tag=='offset':
            _,j,k,sn,sz,parity=key
            cases={n:('offset-digit',j,k,n,parity) for n in (0,1)}
            if j==L and sn in (0,1) and k==sn-sz:cases[2]=('offset-done',parity)
            branch(2,cases)
        elif tag=='offset-digit':
            _,j,k,n,parity=key;v=n+((c>>j)&1 if j<L else 0)+k;z=v&1
            b.emit('write',2,z);move(2,1);go(('offset',min(j+1,L),v//2,n,z,parity))
        elif tag=='offset-done':
            _,parity=key;nxt=('residue',0,1%o,2,parity) if o>1 else ('drop',d,0,parity)
            rewind(nxt)
        elif tag=='rewind':
            _,nxt=key;move(2,-1);branch(2,{0:key,1:key,6:('rewind-ready',nxt)})
        elif tag=='rewind-ready':_,nxt=key;move(2,1);go(nxt)
        elif tag=='residue':
            _,rho,power,sn,parity=key
            cases={n:('res-digit',(rho+n*power)%o,(2*power)%o,n,parity) for n in (0,1)}
            if sn in (0,1):
                r=(rho-(0 if mutant=='unsigned-residue' else sn)*power)%o
                cases[2]=('res-done',r,parity)
            branch(2,cases)
        elif tag=='res-digit':
            _,rho,power,sn,parity=key;move(2,1);go(('residue',rho,power,sn,parity))
        elif tag=='res-done':_,r,parity=key;rewind(('drop',d,-r,parity))
        elif tag=='drop':
            _,left,k,parity=key
            if left:branch(2,{n:('drop-digit',left,k,n,parity) for n in (0,1)})
            else:go(('emit',k,2,parity))
        elif tag=='drop-digit':
            _,left,k,n,parity=key;z,kk=qdigit(n,k);move(2,1);go(('drop',left-1,kk,parity))
        elif tag=='emit':
            _,k,sz,parity=key;cases={x:('emit-y',k,parity) for x in (0,1)}
            if sz in (0,1):cases[2]=('emit-end',k,sz,parity)
            branch(0,cases)
        elif tag=='emit-y':
            _,k,parity=key;branch(1,{y:('emit-n',k,parity) for y in (0,1)})
        elif tag=='emit-n':
            _,k,parity=key;branch(2,{n:('emit-digit',k,n,parity) for n in (0,1)})
        elif tag=='emit-digit':
            _,k,n,parity=key;z,kk=qdigit(n,k);b.emit('write',3,z);move(3,1);move(2,1);publics();go(('emit',kk,z,parity))
        elif tag=='emit-end':
            _,k,sz,parity=key;branch(1,{2:('high',K-d,k,sz,parity)})
        elif tag=='high':
            _,left,k,sz,parity=key;branch(2,{n:('high-digit',left,k,n,sz,parity) for n in (0,1)})
        elif tag=='high-digit':
            _,left,k,n,sz,parity=key;z,kk=qdigit(n,k)
            if z!=sz and mutant!='omit-high':go(reject)
            else:
                move(2,1)
                if left>1:go(('high',left-1,kk,sz,parity))
                elif kk==n-o*sz or mutant=='omit-high':go(('quotient-end',parity))
                else:go(reject)
        elif tag=='quotient-end':
            _,parity=key;branch(2,{2:('next',parity)})
        elif tag=='next':
            _,parity=key;b.emit('write',3,2);move(3,1);move(2,1);publics();go(('start',1-parity,True))
        elif tag=='global-back':
            move(2,-1);branch(2,{2:('global-delimiter',),5:('install',)})
        elif tag=='global-delimiter':
            move(0,-1);move(1,-1);move(3,-1);move(2,-K);go(('global-bits',))
        elif tag=='global-bits':
            move(2,-1);branch(2,{0:('global-public',),1:('global-public',),6:('global-back',)})
        elif tag=='global-public':
            move(0,-1);move(1,-1);move(3,-1);go(('global-bits',))
        elif tag=='install':branch(3,{s:('install-symbol',s) for s in (0,1,2)}|{4:('install-end',)})
        elif tag=='install-symbol':
            _,s=key;b.emit('write',0,s);move(0,1);move(3,1);go(('install',))
        elif tag=='install-end':branch(0,{4:('halt',)})
        elif tag=='halt':b.emit('halt')
        else:raise ValueError(('unknown state',key))
    table=b.finish()
    receipt=dict(coefficient=str(q),numerator=a,denominator=den,coefficient_bits=L,extra_width=K,
                 denominator_twos=d,odd_divisor=o,rows=len(table),states=len(b.labels),max_horner_carry=maxcarry,
                 port_order=['target','source','numerator-work','output-work'],mutant=mutant)
    return table,receipt


def cost_bound(receipt,extent,records,old_backing=0,contexts=0):
    U=1+extent+(receipt['extra_width']+1)*records
    return 512*(receipt['coefficient_bits']+8)*U+7*old_backing+16*contexts
