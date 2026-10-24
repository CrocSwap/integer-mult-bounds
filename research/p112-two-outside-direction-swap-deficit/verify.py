"""Source-bound finite controls for the written all-field theorem, stdlib only."""
from pathlib import Path
from fractions import Fraction
from itertools import product,combinations
import hashlib,json,argparse
from core import partition,binary_rank,require
P=Path(__file__).resolve().parent
R=P.parents[1]

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True)
def authenticate():
    for row in json.loads((P/'SOURCES.json').read_text())['files']:
        if row['usage']=='input':
            require(hashlib.sha256((R/row['path']).read_bytes()).hexdigest()==row['sha256'], 'source hash '+row['path'])

def run():
    authenticate()
    d=json.loads((R/'research/p112-single-lift/reference-geometry.json').read_text())
    roots,labels,duals=d['roots'],d['labels'],d['duals'];n=len(roots)
    require(n==112 and len(labels)==len(duals)==n,'geometry size')
    dot=lambda a,b:sum(x*y for x,y in zip(a,b))
    for i in range(n):
        require(dot(roots[i],roots[i])==8,'norm')
        for j in range(n):
            g=dot(roots[i],roots[j]);require(g%4==0,'integer Gram')
            require(i==j or g in (-4,0,4),'distinct root line')
            require(((duals[i]&labels[j]).bit_count()%2)==(1+g//4)%2,'binary pairing')
            require(dot(d['X'][i],d['X'][j])==g//2,'frame binding')
    ids=list(range(6));points=[(1,0),(0,1),(0,1),(1,1),(1,1),(1,0)]
    edges=[(i,j) for i,j in combinations(ids,2) if dot(roots[i],roots[j])==0]
    require(edges==[(0,1),(2,3),(4,5)],'actual edges')
    fs=[(1,0),(0,1),(1,-1),(1,0),(0,1),(1,-1)]
    colors=partition(points,edges,fs)
    for c in (0,1):
        group=[i for i in ids if colors[i]==c]
        require(binary_rank([labels[i] for i in group])==len(group),'independent colored labels')
    ranks=[binary_rank([labels[i] for i in ids if points[i][a]]) for a in (0,1)]
    require(sum(ranks)>=6,'source deficit')
    # Rational rescaling changes neither projective classes nor membership.
    scaled=[tuple(Fraction(z)*Fraction(i+2,i+1)*(-1)**i for z in pt) for i,pt in enumerate(points)]
    require(partition(scaled,edges,fs)==colors,'scaling')
    require(partition([],[],[])==[],'empty')
    require(partition([(0,7)],[],[(0,1)])==[1],'isolated singleton')
    def rejected(pt,ed,f):
        try:partition(pt,ed,f)
        except ValueError:return
        raise ValueError('negative accepted')
    rejected([(0,0)],[],[(1,0)])
    rejected([(1,0),(1,0)],[(0,1)],[(1,0),(1,0)])
    rejected(points,edges,[(0,1)]+fs[1:])
    rejected([(1,0),(0,1),(1,1)],[(0,1),(0,2)],[(1,0),(0,1),(1,0)])
    # Every labeled graph on four vertices and projective assignment over F2/F3.
    census={}
    es=list(combinations(range(4),2))
    for prime in (2,3):
        pts=[(1,a) for a in range(prime)]+[(0,1)];accepted=0
        for pp in product(pts,repeat=4):
            for mask in range(64):
                ee=[e for k,e in enumerate(es) if mask>>k&1];ff=[]
                for i in range(4):
                    near=[b if a==i else a for a,b in ee if i in (a,b)]
                    if near:
                        x,y=pp[near[0]];f=(y,-x)
                    else:f=(1,0) if pp[i][0] else (0,1)
                    if sum(a*b for a,b in zip(f,pp[i]))%prime==0 or any(sum(a*b for a,b in zip(f,pp[j]))%prime for j in near):break
                    ff.append(f)
                else:
                    partition(pp,ee,ff,prime);accepted+=1
        census[str(prime)]=accepted
    return {'status':'PASS_TWO_OUTSIDE_DIRECTION_SWAP_DEFICIT','geometry_pairs':n*n,'census_admissible':census,'fixture':{'indices':ids,'frame_coordinates':[d['X'][i] for i in ids],'labels':[labels[i] for i in ids],'edges':edges,'colors':colors,'support_ranks':ranks},'controls':{'negative':4,'rational_rescaling':True,'empty':True,'isolated_singleton':True},'theorem_scope':'Written all-field separator implication; finite controls do not prove the theorem or complete K1.'}
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--write');a.add_argument('--check');args=a.parse_args();out=run()
    if args.write:Path(args.write).write_text(json.dumps(out,indent=2)+'\n')
    else:
        receipt=Path(args.check) if args.check else P/'RESULT.json'
        require(canonical(json.loads(receipt.read_text()))==canonical(out),'typed complete receipt')
    print(out['status'])
