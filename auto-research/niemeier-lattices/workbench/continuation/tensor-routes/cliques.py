import sys,json,time,argparse
from pathlib import Path
import numpy as np
import z3
PACKAGE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PACKAGE / 'code'))
import e8_cubed as e
parser=argparse.ArgumentParser(description='Optional Z3 discovery; not needed for certificate replay.')
parser.add_argument('output_directory',type=Path)
args=parser.parse_args()
p=args.output_directory.resolve()
e.require(not p.is_relative_to(PACKAGE.parents[1]),'Discovery output must be outside the checkout')
p.mkdir(parents=True,exist_ok=False)
r,f=e.e8_shells();adj=(r@r.T)==0
neighbors=[sum(1<<int(j)for j in np.flatnonzero(row))for row in adj]
cliques=[]
def dfs(chosen,candidates):
 if len(chosen)==8:
  cliques.append(chosen);return
 if candidates.bit_count()<8-len(chosen):return
 while candidates:
  bit=candidates&-candidates;candidates^=bit;i=bit.bit_length()-1
  dfs(chosen+[i],candidates&neighbors[i])
dfs([], (1<<120)-1)
print('cliques',len(cliques),flush=True)
pairs=[(i,j)for i in range(120)for j in range(i+1,120)if adj[i,j]]
inc={pair:[]for pair in pairs}
for k,c in enumerate(cliques):
 for ii,i in enumerate(c):
  for j in c[ii+1:]:inc[i,j].append(k)
e.require(len(cliques)==2025 and set(map(len,inc.values()))=={15},'All real orthogonal cliques incidence')
(p/'orthogonal-cliques.json').write_text(json.dumps(cliques))
s=z3.Solver();s.set(timeout=45000)
v=[z3.Bool('c'+str(i))for i in range(len(cliques))]
for memberships in inc.values():s.add(z3.PbEq([(v[k],1)for k in memberships],1))
s.add(v[0])
a=s.check();print('cover',a,flush=True)
out=dict(all_cliques=2025,orthogonal_edges=len(pairs),edge_multiplicity=15,search_timeout_ms=45000,exact_cover_status=str(a))
if a==z3.sat:
 selected=[i for i,b in enumerate(v)if z3.is_true(s.model()[b])]
 e.require(len(selected)==135,'135-clique edge cover')
 selectedset=set(selected)
 e.require(all(len(selectedset.intersection(m))==1 for m in inc.values()),'Exact edge partition')
 out['selected_indices']=selected
 out['root_multiplicities']=sorted(set(sum(i in cliques[k]for k in selected)for i in range(120)))
(p/'ORTHOGONAL-CLIQUE-COVER.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out),flush=True)
