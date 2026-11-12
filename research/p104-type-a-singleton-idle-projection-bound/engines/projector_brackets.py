"""Exact inverse-projector transport for the one Type A B8 interval."""
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from signal import SIGALRM,alarm,signal

ROOT=Path(__file__).resolve().parent
PINS={
    "inputs/PRICE.json":"fc02b956e172a6128c08a4774efd5c0bc99ad63cf9cf921c8624aa46213e5560",
    "inputs/CALLER.json":"255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
}
HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER="07a76c5e2738882c0cb322278e56f6cae3c9885d"
U,V=1466,1487
I={(i,i):Q(1) for i in range(36)}


def unique(items):
    obj=dict(items)
    if len(obj)!=len(items):
        raise ValueError("duplicate JSON key")
    return obj


def check(path,digest):
    raw=(ROOT/path).read_bytes()
    if sha256(raw).hexdigest()!=digest:
        raise ValueError("changed dependency "+path)
    return loads(raw,object_pairs_hook=unique)


def elementary(i,j,value=1):
    return {(i,j):Q(value)}


def plus(a,b,scale=1):
    return {k:v for k in a.keys()|b.keys() if (v:=a.get(k,0)+scale*b.get(k,0))}


def multiply(a,b):
    out={}
    for (i,k),x in a.items():
        for (j,l),y in b.items():
            if k==j:
                out[i,l]=out.get((i,l),0)+x*y
    return {k:v for k,v in out.items() if v}


def rows(matrix):
    return [[i,j,str(v)] for (i,j),v in sorted(matrix.items())]


def interval(caller):
    assert caller["types"]["A"]["roles"]==36 and caller["types"]["A"]["offset"]==0
    literal=caller["events"][U:V+1]
    assert literal[0]==["A","IDLE_ONE",7,[8]] and literal[-1]==["A","IDLE_ONE",25,[8]]
    inside=literal[1:-1]
    assert len(inside)==V-U-1==20
    assert inside[0]==["A","ADD",7,0,"2"] and inside[-1]==["A","ADD",25,18,"-2"]
    a=elementary(7,0,2)
    z=elementary(25,18,-2)
    w=plus(plus(I,a),z)
    winv=plus(plus(I,a,-1),z,-1)
    assert multiply(w,winv)==multiply(winv,w)==I

    middle=[]
    for i in range(6):
        r=19+i
        triple=inside[1+3*i:4+3*i]
        assert triple==[["A","ADD",r,18,"-2"],["A","IDLE_ONE",r,list(range(2+i,9))],
                        ["A","ADD",r,18,"2"]]
        s=plus(I,elementary(r,18,-2))
        sinv=plus(I,elementary(r,18,2))
        p=multiply(multiply(sinv,elementary(r,r)),s)
        assert p==plus(elementary(r,r),elementary(r,18,-2))
        middle.append(p)
    first=elementary(7,7)
    last=multiply(multiply(winv,elementary(25,25)),w)
    assert last==plus(elementary(25,25),elementary(25,18,-2))
    all_proj=[first,*middle,last]
    assert all(multiply(p,q)=={} for i,p in enumerate(all_proj) for j,q in enumerate(all_proj) if i!=j)
    assert all(not multiply(p,s) and not multiply(s,p) for p in middle for s in (a,z))
    derivative=plus(first,last)
    assert set(i for i,j in derivative)=={7,25}
    minor=derivative[7,7]*derivative[25,25]-derivative.get((7,25),0)*derivative.get((25,7),0)
    assert minor==1
    physical=plus({},derivative,-2)
    assert physical[7,7]*physical[25,25]==4
    return dict(literal=literal,W0_extra=rows(plus(w,I,-1)),W0_inverse_extra=rows(plus(winv,I,-1)),
        middle_projectors=[rows(p) for p in middle],transported_first=rows(first),transported_last=rows(last),
        normalized_derivative_difference=rows(derivative),rank=2,minor=dict(rows=[7,25],columns=[7,25],determinant="1"),
        exact_specialization=dict(q="1",B8="-1",all_other_bodies="1",difference=rows(physical),
                                  minor_determinant="4",rank=2))


def main():
    assert __debug__
    def stop(*_):
        raise TimeoutError("10-second cap")
    signal(SIGALRM,stop)
    alarm(10)
    try:
        price,caller=(check(k,d) for k,d in PINS.items())
        assert (price["head"],price["caller"],price["pair"],price["ports"])==(HEAD,CALLER,[U,V],96)
        assert len(caller["events"])==4783
        result=interval(caller)
        result.update(head=HEAD,caller=CALLER,pins=PINS,scope=dict(clocks=[U,V],interior_events=20,
            one_local_projector=True,unit_operator_identity=True,fixed_other_derivative=True),
            caps=dict(pairs=1,interior_events=21,seconds=10),decision="excluded",unresolved=[])
    finally:
        alarm(0)
    print(dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
