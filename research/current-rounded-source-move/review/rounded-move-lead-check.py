"""Separate exact algebra/width review; never executes a numerical whole MOVE."""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse,json,sys
def need(ok,message):
    if not ok:raise ValueError(message)
def turn(z,k):
    a,b=z;return ((a,b),(-b,a),(-a,-b),(b,-a))[k%4]
def lin(rows,x):return sum(((x&r).bit_count()%2)<<j for j,r in enumerate(rows))
def exponent(rows,alpha,x):
    chosen=[i for i in range(len(rows)) if (x>>i)&1]
    return sum(alpha[i] for i in chosen)+2*sum((rows[i]>>j)&1 for i in chosen for j in chosen if i<j)
def monomial(vector,r):
    result=[(F(0),F(0)) for _ in vector];destinations=set()
    for x,z in enumerate(vector):
        y=lin(r['matrix_rows'],x)^r['offset'];need(y not in destinations,'affine bijection');destinations.add(y)
        result[y]=turn(z,r['phase']+exponent(r['quadratic_rows'],r['linear_Z4'],x))
    return result
def gaussian(vector,q,orientation=1):
    # C_q = (I+X_q)/2 + i*orientation*(I-X_q)/2.
    result=[]
    for x,(a,b) in enumerate(vector):
        c,d=vector[x^q];result.append(((a+c-orientation*(b-d))/2,(b+d+orientation*(a-c))/2))
    return result
def circuit(vector,instructions):
    for inst in instructions:
        tag=inst[0]
        if tag=='C':vector=gaussian(vector,inst[1],inst[2])
        elif tag=='P':
            result=[(F(0),F(0)) for _ in vector]
            for x,z in enumerate(vector):result[lin(inst[1],x)]=z
            vector=result
        elif tag=='D':vector=[turn(z,exponent(inst[1],inst[2],x)) for x,z in enumerate(vector)]
        elif tag=='X':vector=[vector[x^inst[1]] for x in range(len(vector))]
        elif tag=='phase':vector=[turn(z,inst[1]) for z in vector]
        else:raise ValueError(tag)
    return vector
def rounded(vector):
    return [tuple((v+F(1,2)).numerator//(v+F(1,2)).denominator for v in z) for z in vector]
def main(package):
    sys.path.insert(0,str(package));from rounded_move import S
    M=((1,-1,1,1),(1,1,-1,1),(1,1,1,-1),(-1,1,1,1))
    for i in range(4):
        for j in range(4):need(sum(M[i][k]*M[j][k] for k in range(4))==(4 if i==j else 0),'exact Gaussian orthogonality')
    width_cases=expansion_cases=0
    for h in range(2,258):
        for g in range(1,258):
            sigma=(g+2)//2+1;w=h+g+sigma
            need(2*w-4>=2*h+3*g-1,'squared complete-fibre prefix bound')
            need(w-1>h+g-1,'strict entrance signed headroom');width_cases+=1
            if g<=h:need(w+1<=3*(h+1),'conditional coded-volume expansion');expansion_cases+=1
    need(2*(2+4)-4<2*2+3*4-1,'dropping the width margin is detected')
    triple,original,rec=S.catalog.bind_move(S.catalog.catalog()[1][9896])
    need(rec['rank']==1 and triple[1].fields==(236,),'exact selected raw source')
    x=[(F(0),F(0)) for _ in range(512)];x[0]=(F(1),F(0))
    middle=gaussian(monomial(x,rec['right']),1);exact=circuit(x,original.circuit)
    need(monomial(middle,rec['left'])==exact,'all512 exact source outputs')
    good=rounded(exact);early=monomial(rounded(middle),rec['left'])
    need(exact[21]==(F(1,2),F(-1,2)) and good[21]==(1,0) and early[21]==(0,-1),'actual source distinguishes final-only rounding')
    desired=[(F(0),F(0)) for _ in range(512)];desired[0],desired[1]=(F(1),F(1)),(F(1),F(0))
    entrance_inverse=[(F(0),F(0)) for _ in range(512)];r=rec['right']
    for address in range(512):
        image=lin(r['matrix_rows'],address)^r['offset']
        phase=r['phase']+exponent(r['quadratic_rows'],r['linear_Z4'],address)
        entrance_inverse[address]=turn(desired[image],-phase)
    need(all(-2<=v<=1 for pair in entrance_inverse for v in pair),'all public inputs fit h2')
    middle2=gaussian(desired,1);correct2=rounded(circuit(entrance_inverse,original.circuit))
    need(rounded(middle2)[1]==(2,1),'premature positive-only overflow')
    need(all(-2<=v<=1 for pair in correct2 for v in pair),'all final outputs fit h2')
    need(rounded(monomial(middle2,rec['left']))==correct2,'second complete source factorization')
    return dict(status='independent critical algebra and width checks passed',package=str(package),width_cases=width_cases,expansion_cases=expansion_cases,exact_matrix_inner_products=16,source_outputs_per_control=512,source_controls=['wrong rounding placement','premature intermediate overflow'],negative_width_control=True,numerical_whole_MOVE_executed=False,universal_argument='sigma>=(g+1)/2+1 gives 2w-4>=2h+3g-1; unit phases preserve component magnitudes; exact Gaussian stages consume one divisibility bit each; final codec runs after exit.',limitations='Independent model-assisted review, not a proof-kernel certificate. Source/placement/return premises and complete unabsorbed invoice remain explicit.',reviewed_files={n:sha256((package/n).read_bytes()).hexdigest() for n in ('rounded_move.py','rounded_move_sources.py','PROOF.md')})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('package',type=Path);p.add_argument('--output',type=Path);args=p.parse_args();result=main(args.package.resolve())
    if args.output:args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))
