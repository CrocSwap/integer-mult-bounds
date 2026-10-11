"""Exact paid two-sided adapters for the fourteen isotropic helper entrances.
Each wrapped residual is a coordinate C child; no orthogonal-conjugacy claim.
Chafreaky with OpenAI Codex; uses inherited Gaussian compiler. Apache-2.0.
Usage: adapters.py LOCAL_SPLIT_CENTRES_DIR
"""
import gzip,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
from clifford_exact import canonical_frame,lower_child,monomial,diag,perm,xgate,Op,identity,fourier
out=Path(sys.argv[1]);ld=lambda p:json.loads(gzip.decompress(p.read_bytes())) if p.suffix=='.gz' else json.loads(p.read_text())
word=ld(out/'CANONICAL-WORD.json.gz');raw=ld(out/'LOCAL-PROGRAMS.json.gz');n=word['h'];v=word['v'];R=word['R'];full=tuple(1<<i for i in range(n))
canonical=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def decode(r):return diag(n,tuple(r['quadratic_rows']),tuple(r['linear_Z4'])).then(perm(n,tuple(r['matrix_rows']))).then(xgate(n,r['offset'])).then(Op(n,identity(n),[('phase',r['phase'])]))
recipes={}
for f in sorted(set(word['start'][2*v:])):
 E=word['frames'][f];S=canonical_frame(n,E).adjoint().then(canonical_frame(n,full));w=n-len(E)
 if not E:
  assert S.tab==fourier(n).tab and S.zero_state()==fourier(n).zero_state();recipes[str(f)]=dict(rank=n,pre=None,post=None,identity_adapters=True);continue
 rec,compiled=lower_child(S);assert rec['rank']==w and compiled.tab==S.tab and compiled.zero_state()==S.zero_state()
 left,right=decode(rec['left']),decode(rec['right']);pre,prec=monomial(right.adjoint());post,postc=monomial(left.adjoint())
 target=fourier(n,range(w));wrapped=pre.then(S).then(post)
 assert wrapped.tab==target.tab and wrapped.zero_state()==target.zero_state()
 recipes[str(f)]=dict(rank=w,pre=prec,post=postc,identity_adapters=False)
helpers=[r for r in range(2*v,2*v+R) if word['start'][r]];assert len(helpers)==79 and len(recipes)==15
programs={}
for orientation,events in raw.items():
 body=[];removed=[]
 for e in events:
  if e[0]=='adapter' and e[2]>=2*v:
   assert e[1] in ('old_to_new','new_to_old') and e[3]==(word['start'] if e[1]=='old_to_new' else word['final'])[e[2]];removed.append(e)
  else:body.append(e)
 assert len(removed)==2*R
 # Both scalar orientations leave helpers unchanged; both residuals are S,
 # not inverses. Wrappers surround the ENTIRE invocation including cleanup.
 pre=[['residual_adapter','pre',r,word['start'][r]] for r in helpers]
 post=[['residual_adapter','post',r,word['start'][r]] for r in helpers]
 programs[orientation]=pre+body+post
(out/'RESIDUAL-ADAPTERS.json').write_text(json.dumps(dict(h=n,recipes=recipes,helper_entry_gate='none: initial frame is the interpretation of arbitrary helper data',factorization='S=L C_w R; pre=R^-1; post=L^-1; same residual in both scalar orientations'),indent=2)+'\n')
(out/'ADAPTED-PROGRAMS.json.gz').write_bytes(gzip.compress(canonical(programs),mtime=0))
print('PASS constructed 14 exact nontrivial two-sided adapters, 79 wrapped helpers in each orientation')
