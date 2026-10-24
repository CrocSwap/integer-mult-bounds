#!/usr/bin/env python3
"""Bounded exact corroboration; universal scope belongs to PROOF.md."""
import sys,json,hashlib,copy,time,ast
from pathlib import Path
from itertools import combinations,product
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import algebra as a

def check(ok,message):
 if not ok:raise RuntimeError(message)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def equal(x,y):check(canonical(x)==canonical(y),'complete typed receipt mismatch')
def authenticate():
 manifest=json.loads((HERE/'SOURCES.json').read_text())
 for row in manifest['files']:
  if row['usage']!='input':continue
  p=ROOT/row['path'];raw=p.read_bytes();check(not p.is_symlink(),'regular input')
  check(hashlib.sha256(raw).hexdigest()==row['sha256'],'source SHA256')
  check(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'source Git blob')
 tree=ast.parse((ROOT/'research/dn-bipartite-basis-floor/verify.py').read_text())
 fixture=next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='first_fixture')
 check(ast.literal_eval(fixture.body[0].value)==[(0,1),(0,2),(0,4),(1,2),(2,3),(3,4)],'actual predecessor D5 fixture')
 return manifest

def rejects(fn):
 try:fn()
 except (ValueError,RuntimeError):return
 raise RuntimeError('mutation accepted')
def cheap(expected):
 mutant=copy.deepcopy(expected);mutant['first_D5'][0]['total']=float(mutant['first_D5'][0]['total'])
 rejects(lambda:equal(expected,mutant))
 rejects(lambda:a.shear(3,0,0,1))
 rejects(lambda:a.roots(3,[(0,1),(0,1)]))
 rejects(lambda:a.roots(3,[(1,0)]))
 rejects(lambda:a.fitting(a.roots(2,[(0,1)]),[0,2]))

def run():
 stats={'small_factorizations':0,'common_pairing_bills':0,'independent_span_bills':0,'forced_minor_checks':0,'GL2_blocks':0}
 n=3;all_edges=list(combinations(range(n),2));shears=[(i,j) for i in range(n) for j in range(n) if i!=j]
 parameters=[F(-1),F(0),F(1)]
 for mask in range(1,8):
  edges=[e for k,e in enumerate(all_edges) if mask>>k&1];r=a.roots(n,edges);pairs=list(a.all_pairings(r))
  for (i,j),(k,l),t,s in product(shears,shears,parameters,parameters):
   r,p,q,supports=a.factors(n,edges,i,j,k,l,t,s);stats['small_factorizations']+=1
   lower,witness=a.degree_certificate(n,edges,supports);check(lower>=2*len(edges),'complete degree certificate')
   g=a.gram(r)
   for minor in witness:
    check(all(g[x][y]!=0 for x in minor for y in minor),'forced identity locations')
    stats['forced_minor_checks']+=1
   for B in pairs:
    costs=a.bill(B,supports);check(sum(costs)>=2*len(edges),'common pairing floor');stats['common_pairing_bills']+=1
    # Independent span oracle on every fourth factorization, all its pairings.
    if stats['small_factorizations']%4==0:
     check(costs==a.bill(B,supports,a.rank_by_span),'independent rank oracle');stats['independent_span_bills']+=1
 # Arbitrary two-coordinate GL2 lemma, including diagonal/antidiagonal cases.
 edges=[(0,1),(0,2),(1,2)];r=a.roots(3,edges)
 for u,v,w,z in product((-1,0,1),repeat=4):
  delta=u*z-v*w
  if not delta:continue
  m=a.eye(3);m[0][:2]=[F(u),F(v)];m[1][:2]=[F(w),F(z)]
  inv=a.eye(3);inv[0][:2]=[F(z,delta),F(-v,delta)];inv[1][:2]=[F(-w,delta),F(u,delta)]
  p=a.multiply(r,m);q=a.multiply(r,a.transpose(inv));check(a.multiply(p,a.transpose(q))==a.gram(r),'GL2 exact Gram')
  supports=[([i for i in range(6) if p[i][j]],[i for i in range(6) if q[i][j]]) for j in range(3)]
  check(a.degree_certificate(3,edges,supports)[0]>=6,'GL2 degree certificates');stats['GL2_blocks']+=1
 # Actual predecessor D5 graph; every matrix entry, one complete common B invoice.
 edges=[(0,1),(0,2),(0,4),(1,2),(2,3),(3,4)];fixtures=[]
 for c,d,t,s,expected in [(1,2,F(1),F(1),[3,3,3,2,2]),(1,0,F(1),F(1),[4,4,3,2,2]),(1,0,F(1),F(-1),[2,3,3,2,2]),(1,0,F(1),F(-1,2),[4,4,3,2,2])]:
  r,p,q,supports=a.factors(5,edges,0,1,c,d,t,s);B=a.edge_pairing(edges);a.fitting(r,B)
  costs=a.bill(B,supports);check(costs==expected,'actual D5 common invoice');check(a.degree_certificate(5,edges,supports)[0]>=12,'D5 certificate')
  fixtures.append({'shears':[0,1,c,d,str(t),str(s)],'prices':costs,'total':sum(costs),'gram_entries':144})
 # Three-coordinate two-shear cancellation boundaries beyond {-1,0,1}.
 for t,s in [(F(1,2),F(-2)),(F(2),F(-1,2)),(F(-3,2),F(2,3)),(F(7,3),F(-5,2))]:
  for (i,j),(k,l) in product(shears,repeat=2):
   _,_,_,supports=a.factors(3,[(0,1),(0,2),(1,2)],i,j,k,l,t,s)
   check(a.degree_certificate(3,[(0,1),(0,2),(1,2)],supports)[0]>=6,'rational cancellation boundary')
 # Semantic mutants: wrong inverse order/cross term and false coordinate anchoring.
 M=a.multiply(a.shear(3,0,1,1),a.shear(3,1,2,1));wrong=a.multiply(a.shear(3,0,1,-1),a.shear(3,1,2,-1))
 check(a.multiply(M,wrong)!=a.eye(3),'wrong inverse order rejected')
 r,p,q,supports=a.factors(3,[(0,1),(0,2),(1,2)],0,1,1,2,1,1)
 check([row[1] for row in p]!=[row[1] for row in r] and [row[1] for row in q]!=[row[1] for row in r],'middle coordinate-anchor mutant rejected')
 rejects(lambda:check(sum(a.bill(a.edge_pairing([(0,1),(0,2),(1,2)]),supports,lambda rows:0))>=6,'rank-zero implementation mutant rejected'))
 # A forbidden directed pairing bit is an actual rejected input.
 B=a.edge_pairing([(0,1),(0,2),(1,2)]);B[0]|=1<<2
 rejects(lambda:a.fitting(r,B))
 # Empty graph and isolated-coordinate behavior.
 check(a.factors(3,[],0,1,1,2,1,1)[3]==[([],[])]*3,'empty graph')
 return {'status':'PASS_DN_TWO_SHEAR_FLOOR','statistics':stats,'first_D5':fixtures,'rational_boundary_cases':144,'mutants':['wrong inverse order','false middle coordinate anchor','rank zero','forbidden fitting entry','typed float substitution','invalid shear/graph'],'scope':'Universal written paired-graph theorem; bounded exact controls, no fixed-nonzero-basis optimum or physical supplier.'}

def main():
 authenticate();expected=None
 if '--emit' not in sys.argv:
  expected=json.loads((HERE/'RESULT.json').read_text());cheap(expected)
 if '--check-only' in sys.argv:print('PASS_PINS_AND_TYPED_CONTROLS');return
 start=time.monotonic();observed=run();observed['local_sha256']={name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in ('PROOF.md','algebra.py','verify.py','README.md','SOURCES.json','TASK.json','VERIFY.json')}
 if expected is not None:equal(observed,expected)
 print(json.dumps(observed,indent=2));print('elapsed_seconds='+str(time.monotonic()-start),file=sys.stderr)
if __name__=='__main__':main()
