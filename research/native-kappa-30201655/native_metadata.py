"""Paid affine/quadratic address metadata; independent exact finite reference."""
from random import Random
import json


def require(x,m):
    if not x:raise ValueError(m)


def metadata(e,columns,offset,linear,upper):
    require(e>=1 and len(columns)==len(linear)==len(upper)==e,'shape')
    size=1<<e;mask=size-1
    require(0<=offset<size and all(0<=x<size for x in columns+upper),'address bound')
    require(all(0<=x<4 for x in linear),'linear phase bound')
    require(all((upper[j]&((1<<(j+1))-1))==0 for j in range(e)),'upper phase form')
    mu=max(1,e//16);small=1<<mu;lowmask=small-1
    parity=[0]*small;lowbit=[0]*small
    for x in range(1,small):
        parity[x]=parity[x>>1]^(x&1)
        lowbit[x]=0 if x&1 else 1+lowbit[x>>1]
    def par(x):
        result=0
        for _ in range((e+mu-1)//mu):result^=parity[x&lowmask];x>>=mu
        return result
    def first(x):
        for pos in range(0,e,mu):
            chunk=x&lowmask
            if chunk:return pos+lowbit[chunk]
            x>>=mu
        raise ValueError('zero has no least set bit')
    image=[0]*size;phase=[0]*size
    for x in range(1,size):
        j=first(x);y=x-(1<<j)
        image[x]=image[y]^columns[j]
        phase[x]=(phase[y]+linear[j]+2*par(upper[j]&y))&3
    return [x^offset for x in image],phase


def check():
    rng=Random(20261022);cases=points=0
    for e in range(1,13):
        columns=[1<<j for j in range(e)]
        if e>1:
            for _ in range(4*e):
                a,b=rng.sample(range(e),2)
                columns=[x^((1<<a) if x&(1<<b) else 0) for x in columns]
        offset=rng.randrange(1<<e);linear=[rng.randrange(4) for _ in range(e)]
        upper=[sum(rng.randrange(2)<<k for k in range(j+1,e)) for j in range(e)]
        images,phases=metadata(e,columns,offset,linear,upper)
        require(len(set(images))==1<<e,'affine permutation collision')
        for x in range(1<<e):
            image=offset;phase=0
            for j in range(e):
                if (x>>j)&1:
                    image^=columns[j];phase+=linear[j]
                    for k in range(j+1,e):phase+=2*((upper[j]>>k)&1)*((x>>k)&1)
            require(images[x]==image and phases[x]==phase%4,'independent coordinate/phase mismatch')
            points+=1
        cases+=1
    try:metadata(1,[1],0,[0],[1])
    except ValueError:pass
    else:raise ValueError('non-upper phase accepted')
    return {'status':'PASS_EXACT_METADATA','affine_quadratic_maps':cases,'all_input_addresses_checked':points,'invalid_phase_control':True,'scope':'Finite exact semantics; universal paid O(volume) proof is separate.'}

if __name__=='__main__':print(json.dumps(check(),indent=2))
