from itertools import product
import json


def lin(cols,v):
    s=0
    for i,c in enumerate(cols):
        if v>>i&1:s^=c
    return s


def rank(vs):
    piv={}
    for v in vs:
        while v:
            k=v.bit_length()-1
            if k in piv:v^=piv[k]
            else:piv[k]=v;break
    return len(piv)


def space(vs):return tuple(sorted({lin(vs,k) for k in range(1<<len(vs))}))


def C(v):return v^1 if v&8 else v


def main():
    gl=[a for a in product(range(1,8),repeat=3) if rank(a)==3]
    hs=[]; stab=[]; base=space((9,16,32)); neighbors=set()
    for a in gl:
        inv=[next(x for x in range(8) if lin(a,x)==1<<i) for i in range(3)]
        it=[sum(((inv[j]>>i)&1)<<j for j in range(3)) for i in range(3)]
        for mask in range(64):
            q=[((mask>>i)&1)<<i for i in range(3)]
            for z,(i,j) in enumerate([(0,1),(0,2),(1,2)],3):
                if mask>>z&1:q[i]^=1<<j;q[j]^=1<<i
            def h(v):
                x=v&7;z=v>>3
                return lin(a,x)|(lin(it,z^lin(q,x))<<3)
            cols=tuple(h(1<<j) for j in range(6))
            hs.append(cols)
            sub=space(tuple(lin(cols,z) for z in (9,16,32)))
            neighbors.add(sub)
            if sub==base:stab.append(cols)
    orbits=[];unseen=set(neighbors)
    while unseen:
        s=next(iter(unseen)); orb={tuple(sorted(lin(h,v) for v in s)) for h in stab}
        if not orb<=neighbors:raise ValueError('stabilizer left neighbor orbit')
        unseen-=orb;orbits.append(len(orb))
    def ev(mask,x):
        out=(mask&7&x).bit_count()%2
        for k,(i,j) in enumerate([(0,1),(0,2),(1,2)],3):out^=((mask>>k)&1)*((x>>i)&1)*((x>>j)&1)
        return out
    quad={sum(ev(m,x)<<(x-1) for x in range(1,8)) for m in range(64)}
    qorb=[];remaining=set(quad)
    while remaining:
        v=next(iter(remaining));orb={sum(((v>>(lin(a,x)-1))&1)<<(x-1) for x in range(1,8)) for a in gl}
        if not orb<=quad:raise ValueError('quadratic function space not closed')
        remaining-=orb;qorb.append(len(orb))
    if (len(gl),len(hs),len(neighbors),len(stab),sorted(orbits),sorted(qorb)) != (168,10752,14,768,[1,1,12],[1,7,7,21,28]):raise ValueError('geometry mismatch')
    print(json.dumps({'status':'PASS_COMPLEX_THREE_AXIS_FINITE_GEOMETRY','GL3_order':len(gl),'H_symplectic_order':len(hs),'rank_one_neighbor_count':len(neighbors),'common_stabilizer_order':len(stab),'stabilizer_neighbor_orbits':sorted(orbits),'quadratic_dual_character_orbits':sorted(qorb),'new_kappa':False},sort_keys=True))

if __name__=='__main__':main()
