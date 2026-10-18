import sys,collections,pickle
sys.path.insert(0,__import__('os').environ['EO_ROOT']+'/cards/B240')
from prof import basis
from scan import *
FULLB=basis([1<<i for i in range(9)])
_c={}
def B(U):
    k=tuple(U)
    if k not in _c:_c[k]=basis(U)
    return _c[k]
def nested(a,b):
    for x in a:
        for y in b:
            if x>>(y.bit_length()-1)&1:x^=y
        if x:return False
    return True
start=[B((p,)) for p in w['ports']]+[()]*(v+480)
for q,U in w.get('start_extra',{}).items():start[int(q)]=B(U)
end=[FULLB]*n
for q,U in w.get('helper_final',{}).items():end[int(q)]=B(U)
for q in range(v,2*v):end[q]=B([x for x in range(1,1<<9) if (x&w['ports'][q-v]).bit_count()%2==0])
FR=lambda e:B(e[-1]) if e[-1] is not None else None
# per-register op timeline of frames (only ops with frames, i.e. A,B,tail,cut?) ; full-frame others
tl=collections.defaultdict(list)  # reg -> [(idx,frame)]
for idx,(tag,e) in enumerate(prog):
    if e[0]=='scale':continue
    f=FR(e) if tag[0] not in 'LPC' else FULLB if tag[0]=='L' else B(())
    if tag[0]=='cut':f=None
    for r in e[1:3]:tl[r].append((idx,f))
import bisect
def cur_at(r,idx):
    L=tl[r];i=bisect.bisect_left(L,(idx,))  # first with index>=idx
    # last op before idx with frame not None
    j=i-1
    while j>=0 and L[j][1] is None:j-=1
    return L[j][1] if j>=0 else start[r]
def next_at(r,idx):
    L=tl[r];i=bisect.bisect_right(L,(idx,B(())))  # entries > idx
    i=bisect.bisect_left(L,(idx+1,))
    while i<len(L) and L[i][1] is None:i+=1
    return L[i][1] if i<len(L) else end[r]
def join(a,b):return B(list(a)+list(b))
def mass(h):return len(end[h])-len(start[h])
if __name__=='__main__':
    rows=[]
    for h in range(224,704):
        if h in centers:continue
        st,r=track(h)
        if st!='ok':continue
        out,nr,nw=r
        bad=0;viol_dim=0;endv=0;tot=0
        for idx,terms in out:
            tag,e=prog[idx];E=FR(e) if tag[0] not in 'LPC' else FULLB
            if tag[0]=='cut' or tag[0]=='P':bad+=1;continue
            x=e[1]
            for rr,c in terms:
                tot+=1
                if rr in centers: pass
                c0=cur_at(rr,idx)
                ok=nested(c0,E)
                nx=next_at(rr,idx)
                ok2=nested(E,nx)
                oke=nested(E,end[rr])
                if not ok:bad+=1;viol_dim+=1
                elif not ok2:bad+=1
                elif not oke:endv+=1
        rows.append((h,mass(h),h in compH,nr,tot,bad,endv))
    rows.sort(key=lambda r:(r[5],-r[1]))
    print('h mass inComp nreads newops bad endv')
    for r in rows[:40]:print(r)
    print(sum(1 for r in rows if r[5]==0),'fully feasible of',len(rows))
