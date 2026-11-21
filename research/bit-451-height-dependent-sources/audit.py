"""Independent R342 height-dependent source check. No builder imports or outcomes."""
from argparse import ArgumentParser
from fractions import Fraction as F
from hashlib import sha256
from math import comb,lcm
from pathlib import Path
from time import monotonic
import json,signal

PINS={'bit':'538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749','grid':'69c8f917d6b2676897639eef67e8f15aae1c23a6bfb608dcd38aed236f299818','mean':'41a80ef6b08339dd146791d5a22a7472de8a8ab651b35f25a0282a4ee751295e','old':'42aede07a16e538f97e43341a605e7a432fc0e600504cb1a381e1476abaa30fd','closure':'b7dd2e5829fa794e89b7cb7813ee45a0b4301feb508019f7b00062ba81f8b166'}
def must(x,why):
    if not x:raise ValueError(why)
def up(x):
    return F(-(-x*2**150//1),2**150)
def down(x):
    return F(x*2**120//1,2**120)
def diffs(x):
    result=[]
    while x:
        result.append(x[0]);x=[b-a for a,b in zip(x,x[1:])]
    return result
def fnval(mus):
    p=len(mus)-1
    d=lcm(*(v.denominator for v in mus))
    integral=[int(v*d) for v in mus]
    kernel=[[comb(n,k)*6**k*integral[k] for k in range(n+1)] for n in range(p+1)]
    acc=[7**k for k in range(p+1)];res=[]
    for g in range(51):
        acc=[sum(c*acc[n-k] for k,c in enumerate(row)) for n,row in enumerate(kernel)]
        res.append(F(acc[p],6**p*d**(g+1)))
    return res

def verify(BIT,grid,mean,old,logs,o):
    p=18;v=451;h=1804;B=F(5,2);q=F(749,1000);beta=F(23,20);shift=F(7,8)
    C=F(BIT['separation']['trial']);eta=F(BIT['uniform']['eta'][0])
    H=BIT['uniform']['H']; J=0;d=h**p;n=(H+h)**p
    while d<<J<=n:J+=1
    must((d<<(J-1))<=n<(d<<J) and F(J,H)*(h+H)>2*p,'terminal')
    must(F(h+(134**v).bit_length()-1,h)**p>F(BIT['uniform']['ambient_power'][1]),'base')
    source=BIT['cover_and_stock'];rate=F(source['seed']);rho=F(source['rho'])
    covered=C-F(J,H)-F(1,H*2**44);st=[]
    for _ in range(7):
        lim=covered-rho*(covered-rate)
        step=F(lim*10**24//1-1,10**24);must(rate<step<lim<covered<rho<1-lim,'stage')
        rate=step;st.append(str(rate))
    tick=F(1,10**14);units=rate*10**17//1;cap=F(units,10**17)
    claim=(cap//tick-8)*tick;tested=claim+7*tick;oldc=F(old['candidate_grid_claim'])
    ceiling=F(BIT['raw_crossing'][1])-F(old['uniform_loss'])-7*tick
    o.update(p=p,h=h,uniform_J=J,uniform_loss=str(F(J,H)),cap=f'{units//10**17}.{units%10**17:017d}',candidate_grid_claim=str(claim),candidate_tested=str(tested),old_relaxed_ceiling=str(ceiling),separation=str(claim-ceiling),absolute_gain=str(claim-oldc),stages=st)
    must(old['uniform_J']==747 and old['attained_target_floor']['two_adic_exponent']==1804,'old complete')
    if not oldc<ceiling<claim<tested<cap:return 'full price fails'
    if (q/beta)**p>=B*eta:return 'limit guard fails'
    ell=logs['logint'];ex=logs['exp']
    def lowpower(n,d,e):
        return down(ex(e*(ell(n)[0]-ell(d)[1]))[0])
    near=lowpower(16,9,v*C); bandgain=lowpower(4,1,v*C)
    dist=min(F(grid['mean_lower'])-F(3,5),F(9,10)-F(grid['mean_upper']))
    eps=F(grid['epsilon_upper']); var=F(grid['tensor_variance_upper'])
    must(11**3>=4**5 and 11**9<=9**10 and dist>0 and eps==F(mean['epsilon_upper']),'paid band')
    fraction=(1-var/dist**2)/(1+eps)
    nonroot=down(1+fraction*(bandgain-1))
    b=min(B,F(old['source_lower']['root']))
    initial=down(b*lowpower(16,1,v*C/8))
    o.update(smallL_guard=str(near),band_fraction=str(fraction),band_guard=str(nonroot),small_x_guard=str(initial),
             multiplier=str(B),root_lower=str(b))
    if min(near,nonroot,initial)<=B:return 'nonroot or small-x guard fails'
    al=F(BIT['separation']['three_engine_intervals']['source_1']['alpha'][0])
    lam=F(BIT['separation']['caps']['lambda']); w=F(17,50)
    must(0<lam<al<1,'root tail contraction')
    # k0^w=2^(4*v*w); factor out the integer exponent before small Taylor.
    z=4*v*w;integer=z//1
    start=up((2**integer)*ex((z-integer)*ell(2)[1])[1] / al**v)
    shrink=up((lam/al)**v)
    must(0<shrink<1,'outward root-share proxy decreasing')
    def capacity(g):
        return down(eta*(B-(B-b)*min(1,start*shrink**g)))
    mu=list(map(F,mean['moments'][:p+1]));values=fnval(mu)
    den=lambda g,extra:(F(319,100)+beta*(g+extra))**p
    def coeffs(g,extra):
        u=diffs(values[g:g+p+1]);v=diffs([den(i,extra) for i in range(g,g+p+1)])
        must(min(v)>0,'Newton denominator positive')
        return [x/y for x,y in zip(u,v)]
    left=coeffs(0,0);o['left_ratios']=list(map(str,left))
    for j,r in enumerate(left):
        if r>=B*eta:return 'first-region sufficient coefficient fails at j='+str(j)
    o['finite']=[];o['u0_upper']=str(start);o['ug_multiplier_upper']=str(shrink)
    for g in range(32):
        r=values[g]/den(g,shift); c=capacity(g)
        o['finite'].append({'g':g,'ratio':str(r),'capacity_lower':str(c)})
        if r>=c:return 'upper-x sufficient finite comparison fails at G='+str(g)
    tail=coeffs(32,shift);o['tail_ratios']=list(map(str,tail));o['tail_capacity_lower']=str(capacity(32))
    for j,r in enumerate(tail):
        if r>=capacity(32):return 'translated sufficient coefficient fails at j='+str(j)
    o['positive_control_no_x_slack_fails']=max(values[g]/den(g,0)-capacity(g) for g in range(32))>0
    return 'PASS component; independent signed application required'

def main():
    parser=ArgumentParser()
    for x in [*PINS,'out']:parser.add_argument('--'+x,type=Path,required=True)
    a=parser.parse_args();signal.alarm(60);start=monotonic()
    data={}
    for k,d in PINS.items():
        raw=getattr(a,k).read_bytes();must(sha256(raw).hexdigest()==d,k)
        if k=='closure':
            mod={'__name__':'pinned_previous_rational_implementation'};exec(compile(raw,'R341-independent.py','exec'),mod)
        else:data[k]=json.loads(raw)
    o={'pins':PINS};o['decision']=verify(data['bit'],data['grid'],data['mean'],data['old'],mod,o)
    with a.out.open('x') as out:json.dump(o,out,indent=2);out.write('\n')
    print(o['decision'],o['cap'],o['candidate_grid_claim'],'seconds',monotonic()-start)
if __name__=='__main__':main()
