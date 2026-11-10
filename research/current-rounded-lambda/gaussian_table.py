"""One final rounding of the global Lambda numerator, literal flat ABI.

Ports: original public field, owned translated/staged field, real work,
imaginary work. No public write occurs in STAGE. COMMIT is separate.
"""
from source_binding import need,vendor
B=vendor('lambda_flat_builder','vendor/exact_scalar_tables.py')

def compile_stage(sign,mutant=None):
    need(type(sign)is int and sign in (-1,1),'fixed Lambda orientation')
    b=B.Builder();b.request(('entry',));bad=('reject',)
    def go(k):b.goto(k)
    def br(p,c):b.branch(p,c,bad)
    def mv(p,n=1):
        for _ in range(abs(n)):b.emit('move',p,1 if n>0 else -1)
    def nums(n=1):mv(2,n);mv(3,n)
    def pubs():mv(0);mv(1)
    def pairwrite(zr,zi):b.emit('write',2,zr);b.emit('write',3,zi);nums()
    def realstep(kr,ki,x,y,left,seen):
        vr=x+y+kr;vi=sign*(x-y)+ki;zr,zi=vr&1,vi&1;rr,ii=vr//2,vi//2
        need(abs(rr)<=2 and abs(ii)<=2,'bounded real carries');pairwrite(zr,zi)
        if left is None:pubs();go(('real',rr,ii,x,y,seen))
        elif left>1:go(('real-high',left-1,rr,ii,x,y,seen))
        elif rr==x+y-zr and ii==sign*(x-y)-zi:go(('real-done',seen))
        else:go(bad)
    def imagstep(kr,ki,x,y,nr,ni,left,seen):
        vr=nr+sign*(y-x)+kr;vi=ni+x+y+ki;zr,zi=vr&1,vi&1;rr,ii=vr//2,vi//2
        need(abs(rr)<=3 and abs(ii)<=3,'bounded imaginary carries');pairwrite(zr,zi)
        if left is None:pubs();go(('imag',rr,ii,x,y,seen))
        elif left>1:go(('imag-high',left-1,rr,ii,x,y,seen))
        elif rr==nr+sign*(y-x)-zr and ii==ni+x+y-zi:go(('imag-done',seen))
        else:go(bad)
    while b.pending:
        key=b.pending.popleft();b.mark(key);tag=key[0]
        if tag=='reject':b.emit('reject','Lambda signed range or canonical format')
        elif tag=='entry':br(2,{4:('entry-i',)})
        elif tag=='entry-i':br(3,{4:('markers',)})
        elif tag=='markers':
            b.emit('write',2,5);b.emit('write',3,5);nums();go(('start',False))
        elif tag=='start':
            _,seen=key;c={x:('real',0,0,2,2,seen) for x in (0,1)}
            if seen:c[4]=('end-y',)
            br(0,c)
        elif tag=='end-y':br(1,{4:('halt',)})
        elif tag=='real':
            _,kr,ki,sx,sy,seen=key;c={x:('real-y',kr,ki,x,seen) for x in (0,1)}
            if sx in (0,1):c[2]=('real-end-y',kr,ki,sx,sy,seen)
            br(0,c)
        elif tag=='real-y':
            _,kr,ki,x,seen=key;br(1,{y:('real-bit',kr,ki,x,y,seen) for y in (0,1)})
        elif tag=='real-bit':_,kr,ki,x,y,seen=key;realstep(kr,ki,x,y,None,seen)
        elif tag=='real-end-y':
            _,kr,ki,sx,sy,seen=key;br(1,{2:('real-high',2,kr,ki,sx,sy,seen)})
        elif tag=='real-high':_,left,kr,ki,x,y,seen=key;realstep(kr,ki,x,y,left,seen)
        elif tag=='real-done':
            _,seen=key;b.emit('write',2,2);b.emit('write',3,2);pubs();go(('rewind-both',('imag',0,0,2,2,seen)))
        elif tag=='rewind-both':
            _,nxt=key;nums(-1);br(2,{0:key,1:key,5:('both-ready',nxt)})
        elif tag=='both-ready':_,nxt=key;nums();go(nxt)
        elif tag=='imag':
            _,kr,ki,sx,sy,seen=key;c={x:('imag-y',kr,ki,x,seen) for x in (0,1)}
            if sx in (0,1):c[2]=('imag-end-y',kr,ki,sx,sy,seen)
            br(0,c)
        elif tag=='imag-y':
            _,kr,ki,x,seen=key;br(1,{y:('imag-r',kr,ki,x,y,None,seen) for y in (0,1)})
        elif tag=='imag-end-y':
            _,kr,ki,x,y,seen=key;br(1,{2:('imag-high',2,kr,ki,x,y,seen)})
        elif tag=='imag-high':_,left,kr,ki,x,y,seen=key;go(('imag-r',kr,ki,x,y,left,seen))
        elif tag=='imag-r':
            _,kr,ki,x,y,left,seen=key;br(2,{nr:('imag-i',kr,ki,x,y,nr,left,seen) for nr in (0,1)})
        elif tag=='imag-i':
            _,kr,ki,x,y,nr,left,seen=key;br(3,{ni:('imag-bit',kr,ki,x,y,nr,ni,left,seen) for ni in (0,1)})
        elif tag=='imag-bit':_,kr,ki,x,y,nr,ni,left,seen=key;imagstep(kr,ki,x,y,nr,ni,left,seen)
        elif tag=='imag-done':
            _,seen=key;br(2,{2:('imag-done-i',seen)})
        elif tag=='imag-done-i':_,seen=key;br(3,{2:('back-y',0)})
        elif tag=='back-y':
            _,phase=key;mv(2,-2);go(('back-y-bit',phase))
        elif tag=='back-y-bit':
            _,phase=key;mv(2,-1);br(2,{0:('back-y-move',phase),1:('back-y-move',phase),5:('back-y-stop',phase)})
        elif tag=='back-y-move':_,phase=key;mv(1,-1);go(('back-y-bit',phase))
        elif tag=='back-y-stop':
            _,phase=key;mv(2)
            if phase==0:mv(1,-1);go(('seek-r-end',))
            else:go(('rewind-i',))
        elif tag=='seek-r-end':br(2,{0:('seek-r-step',),1:('seek-r-step',),2:('back-y',1)})
        elif tag=='seek-r-step':mv(2);go(('seek-r-end',))
        elif tag=='rewind-i':mv(3,-1);br(3,{0:key,1:key,5:('i-ready',)})
        elif tag=='i-ready':mv(3);go(('round-first',2,1 if mutant!='tie-down' else 0))
        elif tag=='round-first':
            _,p,k=key;br(p,{n:('round-drop',p,k,n) for n in (0,1)})
        elif tag=='round-drop':
            _,p,k,n=key;mv(p);go(('round-emit',p,(n+k)//2,2))
        elif tag=='round-emit':
            _,p,k,sz=key;c={x:('round-n',p,k) for x in (0,1)}
            if sz in (0,1):c[2]=('round-high',p,k,sz)
            br(1,c)
        elif tag=='round-n':_,p,k=key;br(p,{n:('round-bit',p,k,n) for n in (0,1)})
        elif tag=='round-bit':
            _,p,k,n=key;v=n+k;z=v&1;b.emit('write',1,z);mv(1);mv(p);go(('round-emit',p,v//2,z))
        elif tag=='round-high':_,p,k,sz=key;br(p,{n:('round-high-bit',p,k,n,sz) for n in (0,1)})
        elif tag=='round-high-bit':
            _,p,k,n,sz=key;v=n+k;z=v&1;kk=v//2
            if (z==sz and kk==n-sz) or mutant=='omit-range':mv(p);go(('round-end',p))
            else:go(bad)
        elif tag=='round-end':_,p=key;br(p,{2:('round-next',p)})
        elif tag=='round-next':
            _,p=key;b.emit('write',1,2);mv(1)
            if p==2:go(('round-first',3,1 if mutant!='tie-down' else 0))
            else:mv(0);go(('rewind-both',('clear',)))
        elif tag=='clear':br(2,{0:('clear-one',),1:('clear-one',),2:('clear-one',),4:('clear-back',)})
        elif tag=='clear-one':b.emit('write',2,4);b.emit('write',3,4);nums();go(('clear',))
        elif tag=='clear-back':nums(-1);br(2,{4:key,5:('clear-ready',)})
        elif tag=='clear-ready':nums();go(('start',True))
        elif tag=='halt':b.emit('halt')
        else:raise ValueError(key)
    return b.finish()


def compile_commit():
    b=B.Builder();b.request(('copy',));bad=('reject',)
    while b.pending:
        key=b.pending.popleft();b.mark(key)
        if key[0]=='copy':b.branch(1,{s:('put',s) for s in (0,1,2)}|{4:('end',)},bad)
        elif key[0]=='put':b.emit('write',0,key[1]);b.emit('move',0,1);b.emit('move',1,1);b.goto(('copy',))
        elif key[0]=='end':b.branch(0,{4:('halt',)},bad)
        elif key[0]=='halt':b.emit('halt')
        else:b.emit('reject','Lambda commit requires exact staged extent')
    return b.finish()
COMMIT=compile_commit()
