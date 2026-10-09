"""Optional numerical discovery tool; not needed for exact verification.

Uses NumPy/SciPy to propose a weighted maximum-cardinality matching. Exact
eligibility, frame geometry and all paid costs are checked by verify.py.
Copyright 2026 Rohan Arun, Apache-2.0; OpenAI Codex assistance.
"""
import argparse,os,sys,math,subprocess,importlib.util,shlex,json
from pathlib import Path
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching,min_weight_full_bipartite_matching
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
def solve(edgepath,saving,h=24):
    edges=[]
    for line in edgepath.read_text().splitlines():
        x,j,e,ru,rv,rt=map(int,line.split())
        d={}
        for r,c in ((h-ru,-1),(rv,-1),(rt-rv,-1),(rt-ru,1)):
            if r:d[r]=d.get(r,0)+c
        assert sum(r*c for r,c in d.items())==-h
        # At fixed cardinality the rank term is constant; expm1 avoids
        # cancellation in the tiny non-linear part of the moment.
        weight=sum(c*r*math.log(r) for r,c in d.items()) if saving==0 else -sum(c*r*math.expm1(-saving*math.log(r))/saving for r,c in d.items())
        edges.append((x,j,e,d,weight))
    donors=sorted({e[0]for e in edges});uses=sorted({e[1]for e in edges})
    di={x:i for i,x in enumerate(donors)};ui={x:i for i,x in enumerate(uses)}
    # Duplicate support edges can arise through both donor inputs. Deduplicate
    # before sparse construction so duplicate costs are never summed.
    unique={(x,j):(x,j,e,d,weight)for x,j,e,d,weight in edges};edges=list(unique.values())
    rr=[di[e[0]]for e in edges];cc=[ui[e[1]]for e in edges];nd,nu=len(di),len(ui)
    card=int((maximum_bipartite_matching(csr_matrix((np.ones(len(edges)),(rr,cc)),shape=(nd,nu)),perm_type='column')>=0).sum())
    scores=np.array([e[4]for e in edges]);offset=float(scores.max())+1
    penalty=float(scores.max()-scores.min()+1)*(nd+1)
    matrix=csr_matrix((list(offset-scores)+[penalty+offset]*nd,(rr+list(range(nd)),cc+[nu+i for i in range(nd)])),shape=(nd,nu+nd))
    rows,cols=min_weight_full_bipartite_matching(matrix)
    chosen=[unique[(donors[i],uses[j])]for i,j in zip(rows,cols)if j<nu]
    assert len(chosen)==card
    assert len({x for x,*_ in chosen})==len(chosen) and len({j for _,j,*_ in chosen})==len(chosen)
    return chosen

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=Path,default=ROOT/'build/weighted-dual-suffix-search');args=parser.parse_args()
    work=args.output_dir.resolve();work.mkdir(parents=True,exist_ok=True)
    spec=importlib.util.spec_from_file_location('dual_producer',ROOT/'research/dual-suffix-centers/producer.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.build(24,work/'producer',24)
    exe=work/'matcher';subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17','-I',str(ROOT/'scripts/partial_swap'),str(HERE/'matcher.cpp'),'-o',str(exe)],check=True)
    env=dict(os.environ,EXPORT_EDGES=str(work/'edges.txt'));env.pop('SELECT_LINKS',None)
    subprocess.run([str(exe),str(work/'producer.bin'),str(work/'producer.labels')],env=env,check=True)
    links=solve(work/'edges.txt',0.000080,24)
    (work/'links.txt').write_text(''.join(f'{x} {j}\n'for x,j,*_ in links))
    import audit
    result=audit.replay(audit.load(work/'producer'),audit.read_links(work/'links.txt'))
    (work/'producer.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Candidate saved; use the exact full-profile certificate before any bound claim.')
if __name__=='__main__':main()
