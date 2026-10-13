"""Independent exact small-operator controls for PR36 copied center schedule.
No imports of PR36 code. Fractions represent Gaussian dyadics exactly.
"""
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha256
import json

ZERO=(Q(0),Q(0));ONE=(Q(1),Q(0));I=(Q(0),Q(1))
def add(a,b):return a[0]+b[0],a[1]+b[1]
def neg(a):return -a[0],-a[1]
def mul(a,b):return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def scale(v,c):return [mul(c,x) for x in v]
def plus(v,w):return [add(x,y) for x,y in zip(v,w)]
def translate(v,mask):return [v[i^mask] for i in range(len(v))]
def phase_line(v,mask,inverse=False):
    # C_u = (1+i)/2 I + (1-i)/2 X_u; C_u^2=X_u.
    sign=-1 if inverse else 1
    a,b=(Q(1,2),Q(sign,2)),(Q(1,2),Q(-sign,2))
    return plus(scale(v,a),scale(translate(v,mask),b))
def complex_frame(v,selected,inverse=False):
    for bit in selected:v=phase_line(v,1<<bit,inverse)
    return v

def bit_frame(v,selected,inverse=False):
    n=(len(v).bit_length()-1)//2
    output=[]
    for address in range(len(v)):
        other=address
        for bit in selected:
            if ((address>>bit)^(address>>(bit+n)))&1:
                other^=(1<<bit)|(1<<(bit+n))
        output.append(v[other])
    return output

def change(v,start,end,frame):return frame(frame(v,start,True),end)
def basis(n,j):return [ONE if i==j else ZERO for i in range(n)]
def dirty(n):return [(Q(i%5-2,4),Q(i%7-3,8)) for i in range(n)]
def assert_same(a,b,label):
    if a!=b:raise AssertionError(label)

def schedule_checks(frame,n):
    D0=(0,);DU=(0,1,2);D1=(0,1,2,3);DV=(0,3)
    # Center w is arbitrary: test every basis vector and a dirty Gaussian vector.
    # Targets start dirty too. Scatters include multiple reads with dyadic signs.
    total=0
    for w in [basis(n,j) for j in range(n)]+[dirty(n)]:
        for reverse in (False,True):
            start,read,end=(D0,D1,DV) if reverse else (DU,D0,D1)
            original=frame(w,start)
            read_old=change(original,start,read,frame)
            final_old=change(read_old,read,end,frame)
            if reverse:
                final_new=change(original,start,end,frame)
                read_new=change(list(final_new),end,read,frame)
            else:
                read_new=change(list(original),start,read,frame)
                final_new=change(original,start,end,frame)
            assert_same(read_new,read_old,'transformed copy read')
            assert_same(final_new,final_old,'original cleanup frame')
            for coefficient in ((Q(1),Q(0)),(Q(-3,4),Q(1,2))):
                target=dirty(n)
                assert_same(plus(target,scale(read_new,coefficient)),
                            plus(target,scale(read_old,coefficient)),'dirty scatter target')
            # Any subsequent linear inverse mixer sees the SAME full vector.
            aux=frame(dirty(n),end)
            assert_same(plus(final_new,scale(aux,(Q(-2),Q(0)))),
                        plus(final_old,scale(aux,(Q(-2),Q(0)))),'cleanup incidence')
            total+=1
    return total

def diagonal(v,mask):return [neg(x) if (i&mask).bit_count()%2 else x for i,x in enumerate(v)]

def phase_endpoint_checks():
    n=16;U=7;full=(0,1,2,3)
    def F(v):return complex_frame(v,full)
    def T(v,inverse=False):return phase_line(v,U,inverse)
    def E(v):return F(T(v,True))
    count=0
    vectors=[(basis(n,j),dirty(n)) for j in range(n)]
    vectors += [(dirty(n),basis(n,j)) for j in range(n)]
    for x,y in vectors:
        # Pre diagonal on x is paid; y has no preconditioning.
        xin=diagonal(x,U)
        A=scale(F(y),(-Q(1),Q(0)))
        B=plus(F(T(T(xin,True),True)),E(y))
        retained=list(A)
        B=plus(B,T(list(A),True)) # one paid inverse rank-one child
        assert_same(A,retained,'retained phase output')
        # weight(U)=3; i^3=-i. PR36 has weight9 giving i instead.
        B=scale(diagonal(B,U),(Q(0),-Q(1)))
        A=scale(A,(-Q(1),Q(0)))
        assert_same(A,F(y),'phase first full output')
        assert_same(B,F(x),'phase corrected full output')
        count+=1
    # Literal weight-nine identity with a dirty vector, avoiding a large full matrix.
    x=dirty(512);U=511
    left=complex_frame(translate(diagonal(x,U),U),range(9))
    left=scale(diagonal(left,U),I)
    assert_same(left,complex_frame(x,range(9)),'literal weight-nine phase identity')
    return count+1

def main():
    result=dict(status='exact local operator controls; general schedule proof remains explicit',
        bit_center_cases=schedule_checks(bit_frame,256),
        phase_center_cases=schedule_checks(complex_frame,16),
        phase_endpoint_cases=phase_endpoint_checks(),
        assumptions=['designated output-use has no intervening producer consumer',
          'scatter reads do not modify the source center',
          'copy/transform/read/discard is charged at original role volume',
          'one simultaneous valid frame family and retained residual compiler'],
        rank_replacement='(r,h) becomes paid copy r plus original h-r; saved rank r',
        endpoint_corrections='N rank-one endpoint copies remain separate and charged')
    output=Path(__file__).with_suffix('.json')
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
