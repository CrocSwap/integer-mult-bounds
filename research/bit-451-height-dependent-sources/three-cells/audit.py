"""Independent fixed R344 p17 proof; the supervisor enforces one 45 s child."""
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
'old':('round342/independent/receipt.json','f91280ef454af5d74559788e7f63fd442d8778937c52575160be2718354defcd'),
'signed':('round342/independent/outer-verified.json','148a6315592977093c90de293ca3a904da5cf8dd2fa7840d3a23538d1a87857b'),
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
    p,h,v,B,w,beta=17,1804,451,F(4),F(17,50),F(23,20)
    bit,grid,old=d['bit'],d['grid'],d['old']; l=d['logs']['logint']; ex=d['logs']['exp']
    old_claim=F(old['candidate_grid_claim']);good=d['repaired']; signed=d['signed']['signed']
    must(good['decision']=='PRIMARY_AND_INDEPENDENT_SIGNED_REPLAY_MATCH' and old['uniform_J']==708 and F(good['price']['claim'])==old_claim==F(signed['claim']) and signed['checks']['strict_count']==54 and signed['checks']['functional_count']==4,'R343 exact good signed control')
    must(old['left_ratios']==good['small_x']['newton_ratios'] and old['tail_ratios']==good['large_x_tail']['newton_ratios'],'previous complete coefficients')
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
    ceiling=F(bit['raw_crossing'][1])-F(708,H)-7*tick
    o.update(p=p,h=h,uniform_J=J,uniform_loss=str(F(J,H)),cap=f'{units//10**17}.{units%10**17:017d}',candidate_grid_claim=str(claim),candidate_tested=str(tested),absolute_gain=str(claim-old_claim),separation=str(claim-ceiling),old_relaxed_ceiling=str(ceiling),stages=stages)
    if not old_claim<ceiling<claim<tested<cap:return 'retire: full directed price'
    lim=(q/beta)**p;o['limiting_ratio']=str(lim);o['base_capacity']=str(B*eta)
    if lim>=B*eta:return 'retire: frozen limiting comparison'
    def gain(n,m,e):return dn(ex(e*(l(n)[0]-l(m)[1]))[0])
    pre= gain(16,7,v*C); bandgain=gain(4,1,v*C)
    distance=min(F(grid['mean_lower'])-F(3,5),F(4,5)-F(grid['mean_upper']))
    eps=F(grid['epsilon_upper']);var=F(grid['tensor_variance_upper']);fraction=(1-var/distance**2)/(1+eps)
    must(11**3>=4**5 and 11**4<=7**5 and distance>0 and eps==F(d['mean']['epsilon_upper']),'raw band or exact epsilon')
    b=F(d['sibling']['source_lower']['root'])
    all_band=dn(1+fraction*(bandgain-1));first=dn(b*gain(16,1,v*C/6))
    o.update(small_L=str(pre),band_fraction=str(fraction),band_gain=str(all_band),small_x=str(first),root_lower=str(b))
    if min(pre,all_band,first)<=B or fraction<=0:return 'retire: nonroot or small-x source multiplier'
    alpha=F(bit['separation']['three_engine_intervals']['source_1']['alpha'][0]);lam=F(bit['separation']['caps']['lambda'])
    shrink=up((lam/alpha)**v);must(0<shrink<1,'root decay')
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
    cells=[(F(5,6),F(11,12)),(F(11,12),F(1))]
    upper={};bcell={};o['cells']={}
    for lower,u in cells:
        z=4*v*w*u;i=z//1
        upper[u]=up(2**i*ex((z-i)*l(2)[1])[1]/alpha**v)
        bcell[u]=min(B,dn(b*gain(16,1,v*C*(1-u))))
        o['cells'][str(u)]={'left':str(lower),'root_capacity':str(bcell[u]),'share_prefactor':str(upper[u]),'rows':{}}
    def capacity(g,u):return dn(eta*(B-(B-bcell[u])*min(1,upper[u]*shrink**g)))
    def direct(g,cell):
        lower,u=cell;rec=o['cells'][str(u)]['rows'];key=str(g)
        if key in rec:return True
        ratio=value(g)/den(g,lower);c=capacity(g,u);rec[key]=[str(ratio),str(c)]
        return ratio<c
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
    o['negative_control_old_capacity_fails']=lim>F(5,2)*eta
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
