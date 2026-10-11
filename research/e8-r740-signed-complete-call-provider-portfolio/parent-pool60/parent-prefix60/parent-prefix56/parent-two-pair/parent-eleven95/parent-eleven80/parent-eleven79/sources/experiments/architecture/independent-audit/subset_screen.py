"""Independent product row rank and second-engine necessary screens."""
from pathlib import Path
from fractions import Fraction as Q
from itertools import product
from collections import Counter
import json,importlib.util,hashlib
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent;D=ROOT/'experiments/architecture/k5-subset-screen'
E=ROOT/'experiments/bit-search/pr433/source/research/split-centres-global/vendor/engines/base_two_moment.py'
spec=importlib.util.spec_from_file_location('subset_second',E);M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
def rank(rows):
    b={}
    for x in rows:
        while x:
            p=x.bit_length()-1
            if p in b:x^=b[p]
            else:b[p]=x;break
    return len(b)
def main():
    productchecks=[]
    for q in range(2,9):
        ports=list(product(range(q),repeat=5));v=q**5;constant=(1<<v)-1
        axes=[[sum((y[i]==j)<<k for k,y in enumerate(ports)) for j in range(q)] for i in range(5)]
        base=constant
        for i in range(5):base^=axes[i][0]
        generators=[base]+[axes[i][j]^axes[i][0] for i in range(5) for j in range(1,q)]
        c=rank(generators);expected=5*(q-1) if q%2 else 5*q-8;assert c==expected
        d=1+5*(q-1)+10*(q-1)**2
        eig=[q**3*(3*q*q-15*q+20),q**3*(8-3*q),2*q**3];assert all(eig)
        productchecks.append(dict(q=q,central_rank=c,feature_rank=d,feature_Gram_eigenvalues=eig))
    source=D/'RESULT.json';r=json.loads(source.read_text());checks=[]
    for row in r['rows']:
        d,v,L=row['d'],row['v'],Q(row['L']);m=5*d;H=Counter({d-1:10*v})
        for rk in [2*d-2,d-1,2*d+2,4]:H[rk]+=2*v
        mass=sum(rk*n for rk,n in H.items());deficit=4*v-5*L
        for rate,claim in row['probes'].items():
            lo,hi=M.moment(m,1,list(H.items()),Q(rate));ul=m*lo-mass;uh=m*hi-mass
            assert (ul>deficit)==claim['excluded'] and (ul>4*v)==claim['data_only_excluded']
            old=list(map(Q,claim['uplift_per_port']));assert max(ul/v,old[0])<=min(uh/v,old[1])
        checks.append(row['tag'])
    out=dict(status='PASS_INDEPENDENT_PRODUCT_CENTRAL_RANK_LABEL_NONDEGENERACY_AND_SECOND_ENGINE_SCREENS',
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),product_rank_checks=productchecks,prospective_profiles_checked=len(checks),
        leverage_argument='Degree<=2 tensor feature rowspace invariant under transitive coordinate permutations; Euclidean projection diagonal d/v. For restricted support S, eigenvalues of P_SS lie[0,1], giving rational support rank>=trace=|S|d/v.',
        minimum_support_argument='For nonconstant binary function on one q-axis absolute bias<=1-2/q; independent coordinate biases multiply, so any nonzero additive response support>=v/q. Constant nonzero response supports allv.',
        scope='Fixed central rowspace basis and fixedfive-stage data itinerary, including generous freeprep/restoration. No outside-rowspace overcomplete kernel, targetmixing, changedstages or sharedbank architecture obstruction.')
    (P/'SUBSET-SCREEN.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
if __name__=='__main__':main()
