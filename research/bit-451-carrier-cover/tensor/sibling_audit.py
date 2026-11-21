"""R341: exact rational source complement and paid-recipient audit, CPython 3.12."""
from argparse import ArgumentParser
from fractions import Fraction as F
from functools import cache
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import signal
from time import monotonic

PINS={'bit':'538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749','old':'41a80ef6b08339dd146791d5a22a7472de8a8ab651b35f25a0282a4ee751295e',
      'flow':'4cb32f6b8e388ecf6ed41b5bbdeeb4539cb40c8424f194974afea58f7e0921e8','tensor':'d8bed723957dcd30cc6462562b8e9d5ee33a36891c73916a986459969895993e',
      'producer':'85e4a9a88411e1d763e5d6360b1093f8987c267be853c42322aa5e812dc13698','ambient':'95cc9e31bc030ec94b04decddcca2d28ee98cfec0ca7803b54666b2b76a5c9ab',
      'tree':'750782f6d1cc0a9fff8a768899f3f4c62a7efdf0696d8b5a5d640b1836f5ab72'}
def require(x,msg):
    if not x: raise ValueError(msg)

def blob(path,key):
    b=path.read_bytes()
    require(sha256(b).hexdigest()==PINS[key],key)
    return b

def ln_series(z):
    x=z; v=F(0)
    for i in range(36):
        v+=2*x/(2*i+1)
        x*=z*z
    return v,v+2*x/(73*(1-z*z))

@cache
def logint(n):
    k=n.bit_length()-1
    a,b=ln_series(F(1,3))
    c,d=ln_series(F(n-2**k,n+2**k))
    return F((k*a+c)*2**80//1,2**80),F(-(-(k*b+d)*2**80//1),2**80)

def exp(x):
    require(0<=x<10,'Taylor range')
    s=F(1); v=F(1)
    for k in range(1,46):
        v=v*x/k;s+=v
    return s,s+v*x/46/(1-x/47)

def tally(hist,delta):
    one=sum(int(r)*n for r,n in hist.items())
    high=F(0)
    for r,n in hist.items():
        v=int(r)/exp(delta*logint(int(r))[0])[0]
        high+=n*F(-(-v*2**70//1),2**70)
    return one,high

def controls():
    # For an explicit source DAG, count child target slots against the literal
    # rank-matched parent demand separately for each occurrence (incl aliases).
    ranks=[1,1,1,4,6];target=[(10,2),(12,1)];signals=[]
    for L in map(F,[3,4,6,9,10,12]):
        declared=[(i,k,w) for i,r in enumerate(ranks) for k,w in target if r<=L<k]
        independent=[]
        for i,r in enumerate(ranks):
            if r>L: continue
            for k,w in target:
                supplied=w if k<=L else 0
                if w-supplied: independent.append((i,k,w-supplied))
        require(declared==independent,'exact target/sibling multiplicity')
        signals.append(sum(w for _,_,w in independent))
    require(signals==[9,12,15,15,5,0],'cut boundary rank fixture')
    require(len(set(ranks))!=len(ranks),'duplicate labels matter')
    return signals

def arithmetic(bit,old,base):
    v,h,p=451,1804,19
    require((old['p'],old['uniform_J'],old['h'])==(20,786,h),'predecessor control')
    C=F(bit['separation']['trial']);eps=F(old['epsilon_upper'])
    require(C==F('.003879928046148') and F(old['mean'])==F(749,1000),'slope')
    s=bit['separation'];loss=F(s['discarded_target_upper'][1]);alpha=F(s['three_engine_intervals']['source_1']['alpha'][0])
    require(0<F(s['paid_uplift_upper'][1])<eps*alpha**v,'positive full paid excess')
    prod,pt=tally(bit['native']['targets'],C);mass,qt=tally(bit['native']['paid'],C)
    require(mass==291360 and sum(bit['native']['paid'].values())==107460 and sum(bit['native']['targets'].values())==20706,'full native labels')
    root=(F(prod,pt)**v)/exp(v*C*logint(16)[1])[1]-loss
    partial=exp(v*C*(logint(16)[0]-logint(11)[1]))[0]
    full=(F(mass,qt)**v)/(1+eps)
    floor=lambda x:F(x*10**18//1,10**18)
    bounds=dict(root=str(floor(root)),partial=str(floor(partial)),full=str(floor(full)))
    multiplier=F(8,5)
    require(min(map(F,bounds.values()))>multiplier,'all three source cases')
    q=F(749,1000);prob=q/2
    weights=[comb(v,i)*749**i*1251**(v-i) for i in range(v+1)]
    require(sum(weights)==2000**v and prob==F(749,2000),'atom law')
    mus=[F(1),q]
    for k in range(2,p+1):
        m=F(sum(w*(2*i)**k for i,w in enumerate(weights)),2000**v*v**k)
        mus.append((min(1,m)+eps)/(1+eps))
    require(mus==list(map(F,old['moments'][:p+1])),'independent paid-moment reconstruction')
    coeff=base['ratios'](mus,p)
    l,u=map(F,bit['uniform']['eta'])
    require(len(coeff)==20 and max(coeff)<multiplier*l and coeff[-1]==(q/F(23,20))**p,'all-height contraction')
    require(max(coeff)>u,'negative: removing source gain breaks capacity')
    positive=base['ratios'](list(map(F,old['moments'])),20)
    require(positive==list(map(F,old['coefficients'])) and max(positive)<l,'known-good independent p20')
    require((1+F((134**v).bit_length()-1,h))**p>F(bit['uniform']['ambient_power'][1]),'unmodified base')
    H=bit['uniform']['H']; high=(h+H)**p;den=h**p;J=0
    while (den<<J)<=high:J+=1
    require(den<<(J-1)<=high and F(J,H)*(H+h)>2*p,'terminal and adjacent control')
    cover=C-F(J,H)-F(1,H*2**44);stock=bit['cover_and_stock'];rho=F(stock['rho'])
    require(F(stock['bad_surcharge_upper'])<F(1,2**45),'cover')
    rate=F(stock['seed']); stages=[]
    for _ in range(7):
        upper=cover-rho*(cover-rate); nxt=F((upper*10**24)//1-1,10**24)
        require(rate<nxt<upper<cover<rho<1-upper,'ordinary stage')
        stages.append(str(nxt));rate=nxt
    units=rate*10**17//1;cap=F(units,10**17);tick=F(1,10**14)
    claim=(cap//tick-8)*tick;tested=claim+7*tick
    ceiling=F(bit['raw_crossing'][1])-F(786,H)-7*tick
    prior=F(old['candidate_grid_claim'])
    require(prior<ceiling<claim<tested<cap,'strict full comparison')
    return dict(p=p,h=h,source_lower=bounds,capacity_multiplier=str(multiplier),eta_lower=str(l),
                effective_capacity_lower=str(l*multiplier),coefficients=list(map(str,coeff)),peak_index=coeff.index(max(coeff)),
                positive_control_p=20,negative_control_unmodified_capacity=True,edge_control_counts=controls(),
                uniform_J=J,uniform_loss=str(F(J,H)),stages=stages,cap=f'{units//10**17}.{units%10**17:017d}',
                candidate_grid_claim=str(claim),candidate_tested=str(tested),old_relaxed_ceiling=str(ceiling),
                separation=str(claim-ceiling),absolute_gain=str(claim-prior),exact_percent=str(100*(claim-prior)/prior))

def main():
    parser=ArgumentParser(description=__doc__)
    for arg in ('bit','old','flow','producer','ambient','tensor','tree','out'):
        parser.add_argument('--'+arg,type=Path,required=True)
    parser.add_argument('--outer',type=Path)
    parser.add_argument('--bind-receipt',type=Path)
    a=parser.parse_args();start=monotonic();signal.alarm(60)
    b={key:blob(getattr(a,key),key) for key in PINS}
    bit,old=map(json.loads,[b['bit'],b['old']])
    base={'__name__':'immutable_tensor'};exec(compile(b['tensor'],'tensor/audit.py','exec'),base)
    if a.bind_receipt:
        result=json.loads(a.bind_receipt.read_bytes())
        require(result['pins']==PINS and a.outer,'component pin inventory and outer required')
    else:
        result=arithmetic(bit,old,base);result['pins']=PINS;print('component_seconds',monotonic()-start)
    tuple_counts={2:1,8:299,64:151}
    minimum=1
    for k,count in tuple_counts.items():
        require(bit['native']['targets'].get(str(k),0)>0,'attained floor uses a present target')
        minimum*=k**count
    require(sum(tuple_counts.values())==451 and minimum==16**451,'attained minimum for root maximality')
    result['attained_target_floor']={'tuple_counts':{str(k):v for k,v in tuple_counts.items()},'two_adic_exponent':1804}
    if a.outer:
        base['bind'](result,a.outer)
        rec=json.loads((a.outer/'receipt.json').read_bytes()); k='adapter/binary/FINITE.json'
        f=base['source'](a.outer/k,rec['output_sha256'][k])
        require(f['word_sha256']==bit['native']['candidate_canonical_sha256'] and f['ordinary_admitted']==rec['cap']==result['cap'],'actual signed supplier')
        require({'low_cap_rejected','extra_rank_1_charge_rejected'}.issubset(rec['controls']),'signed negative controls')
        result['outer_binding']={'output_sha256':rec['output_sha256'],'controls':rec['controls']}
    with a.out.open('x') as out:json.dump(result,out,indent=2);out.write('\n')
    print('PASS',result['source_lower'],result['cap'],result['candidate_grid_claim'],result['absolute_gain'])
if __name__=='__main__':main()
