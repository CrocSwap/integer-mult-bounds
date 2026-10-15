"""Independent finite controls for unequal-spacing packed masked shears."""
from itertools import product
from pathlib import Path
import json,random

HERE=Path(__file__).resolve().parent

def digit(x,i,G):return (x>>(i*G))&((1<<G)-1)
def pack(values,G):return sum(v<<(i*G) for i,v in enumerate(values))
def good(u,t,y,targets,G,K):
    B=1<<G
    return all(digit(u,i,G)!=B-1 and digit(t,i,G)!=B-1 and
               2*B<=((y>>(j+1))&((1<<(K-1))-1))<(1<<(K-1))-2*B
               for i,j in enumerate(targets))

def ops(targets,sources,G):
    out=[]
    F=[('y1',1),('t1',1),('y2',1),('t2',-1)]
    return F+[('load',1)]+F+[('load',-1)]

def run(state,targets,sources,G,n,inverse=False):
    u,t,y=state;H=len(targets)*G;mask=(1<<H)-1;ymask=(1<<n)-1
    sequence=ops(targets,sources,G)
    if inverse:sequence=[(tag,-sign) for tag,sign in reversed(sequence)]
    for tag,sign in sequence:
        if tag=='y1':
            y=(y+sign*sum((2*(digit(u,i,G)&1)*digit(t,i,G))<<j for i,j in enumerate(targets)))&ymask
        elif tag=='y2':
            y=(y+sign*sum(((digit(u,i,G)&1)*(1-2*digit(t,i,G)))<<j for i,j in enumerate(targets)))&ymask
        elif tag=='t1':t=(t+sign*sum(((y>>j)&1)<<(i*G) for i,j in enumerate(targets)))&mask
        elif tag=='t2':t=(t+sign*sum((((y>>j)&1)^(digit(u,i,G)&1))<<(i*G) for i,j in enumerate(targets)))&mask
        else:u=(u+sign*sum(((y>>s)&1)<<(i*G) for i,s in enumerate(sources)))&mask
    return u,t,y

def ideal(state,targets,sources):
    u,t,y=state
    return u,t,y^sum(((y>>s)&1)<<j for s,j in zip(sources,targets))

def check_case(targets,sources,G,K,n,states):
    assert len(targets)==len(sources)==len(set(targets))==len(set(sources))
    assert not set(targets)&set(sources)
    assert all(b-a>=K for a,b in zip(sorted(targets),sorted(targets)[1:]))
    assert all(j+K<=n for j in targets)
    count=good_count=bad_count=corrected=0;images=set()
    for state in states:
        count+=1;out=run(state,targets,sources,G,n)
        assert run(out,targets,sources,G,n,True)==state
        assert good(*out,targets,G,K)==good(*state,targets,G,K)
        assert good(*ideal(state,targets,sources),targets,G,K)==good(*state,targets,G,K)
        if good(*state,targets,G,K):
            good_count+=1;assert out==ideal(state,targets,sources)
        else:
            bad_count+=1
            fixed=ideal(run(out,targets,sources,G,n,True),targets,sources)
            assert fixed==ideal(state,targets,sources)
            corrected+=fixed!=out
        images.add(out)
    return dict(targets=targets,sources=sources,G=G,K=K,n=n,states=count,
                good=good_count,bad=bad_count,changed_by_repair=corrected,distinct_images=len(images))

def main():
    small=check_case([0,6],[4,8],1,5,11,
        product(range(4),range(4),range(1<<11)))
    assert small['states']==small['distinct_images']==32768
    rng=random.Random(713)
    targets=[1,10,21];sources=[5,15,25];G=2;K=7;n=29
    arbitrary=[(rng.randrange(64),rng.randrange(64),rng.randrange(1<<n)) for _ in range(2000)]
    for _ in range(2000):
        u=pack([rng.randrange(3) for _ in targets],G);t=pack([rng.randrange(3) for _ in targets],G)
        y=rng.randrange(1<<n)
        for j in targets:
            y&=~(((1<<K)-1)<<j)
            y|=((rng.randrange(8,56)<<1)|rng.randrange(2))<<j
        arbitrary.append((u,t,y))
    large=check_case(targets,sources,G,K,n,arbitrary)
    out=dict(status='PASS_UNEQUAL_SPACING_PACKED_SHEAR_CONTROLS',exhaustive=small,random_and_good=large,
        scope='Exact address permutations and bad-set repair only; asymptotic tape costs are proved in the companion note.')
    (HERE/'SPARSE-SHEAR-CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
