"""Deterministic exact witnesses; normal execution writes no files."""
import json
from pathlib import Path
from linear import (Q,identity,transpose,multiply,inverse,rank_factor,nullspace,
                    require,outer,add,scale,dot)


def dual_word(length, thin, positions, bases=None):
    """Full pairs are consecutive; thin order is the order in the input list."""
    require(len(thin)==len(positions),'thin positions length')
    require(positions==sorted(positions),'thin positions chronological')
    require(all(0<=v<=length for v in positions),'thin positions range')
    bases=bases or [identity(2) for _ in range(length)]
    ps=[];qs=[];full=[];thin_indices=[]
    for gap in range(length+1):
        for j,pos in enumerate(positions):
            if pos==gap:
                q,p=thin[j];thin_indices.append(len(qs));qs.append(list(map(Q,q)));ps.append(list(map(Q,p)))
        if gap<length:
            b=bases[gap];bi=inverse(b);start=len(qs);full.append([start,start+1])
            qs.extend(transpose(b));ps.extend(bi)
    n_units=len(qs)
    gram=[[Q((i>j)-(i<j))*dot(ps[i],qs[j]) for j in range(n_units)] for i in range(n_units)]
    x,y=rank_factor(gram)
    return {'n':len(x),'N':n_units,'X':transpose(x),'Y':y,'full':full,
            'thin':thin_indices,'dual_p':ps,'dual_q':qs}


def scalar_chain_sites(g,h):
    n=g+h+1;out=[]
    def vector(entries):
        v=[Q(0)]*n
        for j,c in entries:v[j]+=Q(c)
        return v
    for i in range(g):
        x=vector([(0,1),(1+i,1)]+[(1+j,2) for j in range(i)])
        y=vector([(0,1),(1+i,-1)])
        out.append((x,y,set(range(i+2))))
    for i in range(h):
        x=vector([(0,-1),(1+g+i,1)]+[(1+g+j,2) for j in range(i+1,h)])
        y=vector([(0,1),(1+g+i,1)])
        out.append((x,y,{0,*range(1+g+i,n)}))
    return out


def coupled_chain(g,h):
    """Four-thin dual closure, gauged to the inherited full chain operators."""
    length=g+h;require(length%2==0 and g>0 and h>0,'positive even total length')
    thin=[([1,0],[1,0]),([1,1],[Q(1,2),Q(1,2)])]*2
    root=dual_word(length,thin,[g]*4)
    x=transpose(root['X']);y=root['Y'];full=[u for block in root['full'] for u in block]
    a_cols=[root['X'][u] for u in full]+nullspace([y[u] for u in full])
    n0=length+1;n=2*n0
    require(len(a_cols)==n,'full span plus common-kernel basis')
    def embed(v,ch):return [Q(0)]*(ch*n0)+list(v)+[Q(0)]*((1-ch)*n0)
    sites=scalar_chain_sites(g,h);b_cols=[]
    for xx,yy,mask in sites:b_cols.extend([embed(xx,0),embed(xx,1)])
    kernel=[Q(1)]*(g+1)+[Q(-1)]*h
    b_cols.extend([embed(kernel,0),embed(kernel,1)])
    gauge=multiply(transpose(b_cols),inverse(transpose(a_cols)))
    root['X']=transpose(multiply(gauge,x));root['Y']=multiply(y,inverse(gauge))
    root['stages']=[];root['shape']=[g,h]
    for i,(xx,yy,mask) in enumerate(sites):
        a,b=root['full'][i]
        require(root['X'][a]==embed(xx,0) and root['X'][b]==embed(xx,1),'full column gauge')
        require(root['Y'][a]==embed(yy,0) and root['Y'][b]==embed(yy,1),'full row gauge')
        root['stages'].append({'units':[a,b],'mask':sorted(mask|{n0+j for j in mask})})
    return root


def jsonable(value):
    if isinstance(value,Q):return str(value)
    if isinstance(value,list):return [jsonable(x) for x in value]
    if isinstance(value,dict):return {k:jsonable(v) for k,v in value.items()}
    return value


def parse_root(root):
    root=dict(root)
    for key in ('X','Y','dual_p','dual_q'):
        root[key]=[[Q(x) for x in row] for row in root[key]]
    return root


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    for g in (1,9):
        root=jsonable(coupled_chain(g,g))
        path=args.output/('root-%d.json'%root['n'])
        path.write_text(json.dumps(root,sort_keys=True,separators=(',',':'))+'\n')
        print(path.name)
