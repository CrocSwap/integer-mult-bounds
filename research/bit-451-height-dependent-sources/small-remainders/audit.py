"""Independent fixed R345 p16 proof; the supervisor enforces one 45 s child."""
from argparse import ArgumentParser
from fractions import Fraction as F
from hashlib import sha256
from math import comb,lcm
from pathlib import Path
from time import monotonic
import json,signal

PINS={
'bit':('round321/benchmark/producer/BIT-451.json','538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749'),
'grid':('round336/independent/receipt.json','69c8f917d6b2676897639eef67e8f15aae1c23a6bfb608dcd38aed236f299818'),
'mean':('round339/independent/receipt.json','41a80ef6b08339dd146791d5a22a7472de8a8ab651b35f25a0282a4ee751295e'),
'sibling':('round341/independent/receipt-with-minimum.json','42aede07a16e538f97e43341a605e7a432fc0e600504cb1a381e1476abaa30fd'),
'logs':('round341/independent/audit.py','b7dd2e5829fa794e89b7cb7813ee45a0b4301feb508019f7b00062ba81f8b166'),
'old':('round344/independent/receipt.json','1fd90f20d38e5368a98deef7efe4bce880f95b6da8078d4aa37e78921173f1ac'),
'signed':('round344/independent/outer-verified.json','0741754b7644e6d61ab4f36f3471e564aa6ec052a3a4245a2d19402aed1983ad'),
'repaired':('round343/primary.json','846c6441860cf5e91cf958a7f4a77e7bdf5befa8c519b82a157142f34535c4e9')}
def must(x,msg):
    if not x:raise ValueError(msg)
def up(x):return F(-(-x*2**130//1),2**130)
def dn(x):return F((x*2**130)//1,2**130)
def diffs(x):
    a=[]
    while x:
        a.append(x[0]); x=[v-u for u,v in zip(x,x[1:])]
    return a

def evaluate(d,o):
    p,h,v,B,beta=16,1804,451,F(6),F(23,20)
    bit,grid,old=d['bit'],d['grid'],d['old']; l=d['logs']['logint']; ex=d['logs']['exp']
    old_claim=F(old['candidate_grid_claim']); signed=d['signed']['signed']
    must(old['uniform_J']==668 and old['p']==17 and old_claim==F(signed['claim']) and signed['checks']['strict_count']==54 and signed['checks']['functional_count']==4,'R344 good signed price')
    must(len(old['small_x_coefficient_ratios'])==18 and all(len(c['rows'])==32 and len(c['tail'])==18 for c in old['cells'].values()),'p17 previous scope')
    bits=bit['native']['targets']
    must(all(bits[str(r)]>0 for r in (2,8,64)) and 64**151*8**299*2==16**451 and 151+299+1==451,'literal retained minimum')
    C=F(bit['separation']['trial']);H=bit['uniform']['H'];q=F(749,1000);eta=F(bit['uniform']['eta'][0])
    D=h**p;N=(h+H)**p; J=0
    while D<<J<=N:J+=1
    must(D<<(J-1)<=N and F(J,H)*(H+h)>2*p and (1+F((134**v).bit_length()-1,h))**p>F(bit['uniform']['ambient_power'][1]),'base or terminal')
    covered=C-F(J,H)-F(1,H*2**44);stock=bit['cover_and_stock'];rho=F(stock['rho']);rate=F(stock['seed'])
    stages=[]
    for _ in range(7):
        ub=covered-rho*(covered-rate);candidate=F(ub*10**24//1-1,10**24)
        must(rate<candidate<ub<covered<rho<1-ub,'stage');rate=candidate;stages.append(str(rate))
    units=rate*10**17//1;cap=F(units,10**17);tick=F(1,10**14);claim=(cap//tick-8)*tick;tested=claim+7*tick
    ceiling=F(bit['raw_crossing'][1])-F(668,H)-7*tick
    o.update(p=p,h=h,uniform_J=J,uniform_loss=str(F(J,H)),cap=f'{units//10**17}.{units%10**17:017d}',candidate_grid_claim=str(claim),candidate_tested=str(tested),absolute_gain=str(claim-old_claim),separation=str(claim-ceiling),old_relaxed_ceiling=str(ceiling),stages=stages)
    if not old_claim<ceiling<claim<tested<cap:return 'retire: full directed price'
    lim=(q/beta)**p;o['limiting_ratio']=str(lim);o['base_capacity']=str(B*eta)
    if lim>=B*eta:return 'retire: frozen limiting comparison'
    def gain(n,m,e):return dn(ex(e*(l(n)[0]-l(m)[1]))[0])
    # All native t-powers use r/exp(delta log r); separate lower and upper.
    t=1-C;eps=F(grid['epsilon_upper']); paid=bit['native']['paid']
    must(eps==F(d['mean']['epsilon_upper']) and sum(paid.values())==107460,'full paid profile/normalization')
    def raw_bounds(r,loss):
        if r==1:return F(1),F(1)
        loglo,loghi=l(r)
        return dn(F(r)/ex(loss*loghi)[1]),up(F(r)/ex(loss*loglo)[0])
    subset_lo=sum(n*raw_bounds(int(r),C)[0] for r,n in paid.items() if int(r)<=5)
    N0=sum(paid.values())
    per_small=up(ex(t*(l(7)[1]-l(5)[0]))[1])
    U=up((N0*per_small/subset_lo)**v)
    low= gain(16,5,v*C);high=F(old['band_gain'])
    mid=dn(gain(16,7,v*C)*(1+(1-U)*(gain(7,5,v*C)-1)))
    b=F(d['sibling']['source_lower']['root'])
    first=dn(b*gain(16,1,v*C/4))
    o.update(small_L=str(low),mid_L=str(mid),high_L_reused=str(high),small_mass_upper=str(U),admitted_five_mass_lower=str(subset_lo),small_x=str(first),root_lower=str(b))
    if min(low,mid,high,first)<=B or U>=1:return 'retire: nonroot/middle small-rank budget or small-x capacity'
    # Each raw item produces at most one short positive remainder; equality at d
    # belongs to the large class; a full slab is never short.
    def slabs(n,cut):
        full,rem=divmod(n,cut);return [cut]*full+([rem] if rem else [])
    example=[slabs(n,9) for n in (1,2,3,8,9,10,18,19,20,21)]
    must(all(max(s)<=9 and sum(r<3 for r in s)<=1 for s in example) and
         [sum(s) for s in example]==[1,2,3,8,9,10,18,19,20,21] and sum(r<3 for r in example[-1])==0,'one positive small remainder with exact endpoints')
    alpha=F(bit['separation']['three_engine_intervals']['source_1']['alpha'][0])
    tlo=sum(n*raw_bounds(int(r),C)[0] for r,n in bits.items())
    w2=F(17,100);num=sum(n*raw_bounds(int(r),C+w2)[1] for r,n in bits.items())
    lams={F(17,50):F(bit['separation']['caps']['lambda']),w2:up(ex(w2*l(16)[1])[1]*num/tlo)}
    shrink={w:up((z/alpha)**v) for w,z in lams.items()}
    must(all(0<z<1 for z in shrink.values()),'two directed root-share decay factors')
    o['half_tilt_lambda_upper']=str(lams[w2]);o['tail_decay']={str(w):str(x) for w,x in shrink.items()}
    # Rebuild all moments from the original 452 chord atoms and full paid uplift.
    weights=[comb(v,i)*749**i*1251**(v-i) for i in range(v+1)]
    mus=[F(1),q]
    for k in range(2,p+1):
        raw=F(sum(val*(2*i)**k for i,val in enumerate(weights)),2000**v*v**k)
        mus.append((min(F(1),raw)+eps)/(1+eps))
    must(mus==list(map(F,d['mean']['moments'][:p+1])),'paid-law prefix')
    Q=lcm(*(s.denominator for s in mus));mu=[int(v*Q) for v in mus]
    M=[7**j for j in range(p+1)]
    kern=[[comb(i,k)*6**k*mu[k] for k in range(i+1)] for i in range(p+1)]
    values=[]
    def value(g):
        nonlocal M
        while len(values)<=g:
            M=[sum(c*M[n-k] for k,c in enumerate(row)) for n,row in enumerate(kern)]
            values.append(F(M[p],6**p*Q**(len(values)+1)))
        return values[g]
    den=lambda g,extra:(F(319,100)+beta*(g+extra))**p
    def coef(g,extra):
        u=diffs([value(i) for i in range(g,g+p+1)]);v=diffs([den(i,extra) for i in range(g,g+p+1)])
        must(min(v)>0,'denominator coefficients')
        return [x/y for x,y in zip(u,v)]
    cells=[(F(3,4),F(5,6)),(F(5,6),F(11,12)),(F(11,12),F(23,24)),(F(23,24),F(1))]
    upper={};bcell={};o['cells']={}
    for lower,u in cells:
        for w in lams:
            z=4*v*w*u;i=z//1
            upper[u,w]=up(2**i*ex((z-i)*l(2)[1])[1]/alpha**v)
        bcell[u]=min(B,dn(b*gain(16,1,v*C*(1-u))))
        o['cells'][str(u)]={'left':str(lower),'root_capacity':str(bcell[u]),'share_prefactors':{str(w):str(upper[u,w]) for w in lams},'rows':{}}
    def shares(g,u):return {w:upper[u,w]*shrink[w]**g for w in lams}
    def capacity(g,u):return dn(eta*(B-(B-bcell[u])*min(1,*shares(g,u).values())))
    def direct(g,cell):
        lower,u=cell;rec=o['cells'][str(u)]['rows'];key=str(g)
        if key in rec:return True
        ratio=value(g)/den(g,lower);c=capacity(g,u);rec[key]=[str(ratio),str(c)]
        if ratio>=c:o['obstruction']={'cell':list(map(str,cell)),'g':g,'ratio':str(ratio),'capacity_lower':str(c),'excess':str(ratio-c),'root_share_upper_by_tilt':{str(w):str(z) for w,z in shares(g,u).items()}}
        return ratio<c
    for cell in reversed(cells):
        if not direct(16,cell):return 'frozen direct bound fails: cell '+str(cell)+' height 16'
    for cell in cells:
        for g in (0,31):
            if not direct(g,cell):return 'frozen direct bound fails: cell '+str(cell)+' height '+str(g)
    left=coef(0,0);o['small_x_coefficient_ratios']=list(map(str,left))
    for j,r in enumerate(left):
        if r>=B*eta:return 'frozen low-x coefficient fails: '+str(j)
    for cell in cells:
        lower,u=cell
        for g in range(32):
            if not direct(g,cell):return 'frozen direct bound fails: cell '+str(cell)+' height '+str(g)
        tail=coef(32,lower);c=capacity(32,u);o['cells'][str(u)].update(tail=list(map(str,tail)),tail_capacity=str(c))
        for j,r in enumerate(tail):
            if r>=c:return 'frozen tail coefficient fails: cell '+str(cell)+' order '+str(j)
    o['negative_control_old_capacity_fails']=lim>4*eta
    must(o['negative_control_old_capacity_fails'],'old capacity must fail')
    return 'PASS independent source and price; signed binding pending'

def main():
    parser=ArgumentParser();parser.add_argument('root',type=Path);parser.add_argument('out',type=Path);a=parser.parse_args()
    signal.alarm(45); start=monotonic();data={};o={'inputs':{p:x for p,x in PINS.values()}}
    for k,(file,pin) in PINS.items():
        raw=(a.root/file).read_bytes();must(sha256(raw).hexdigest()==pin,file)
        if k=='logs':
            obj={'__name__':'pinned_rational_taylor'};exec(compile(raw,'R341/audit.py','exec'),obj);data[k]=obj
        else:data[k]=json.loads(raw)
    o['decision']=evaluate(data,o)
    with a.out.open('x') as stream:json.dump(o,stream,indent=2);stream.write('\n')
    print(o['decision'],o['cap'],o['candidate_grid_claim'],'seconds',monotonic()-start)
if __name__=='__main__':main()
