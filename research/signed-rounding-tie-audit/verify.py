"""Source-bound sign-inside-rounding audit. Apache-2.0."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
from math import gcd,lcm
import json,hashlib,subprocess,importlib.util,types,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,msg):
 if not ok:raise ValueError(msg)
def Q(x,w):
 y=x*(1<<w)+F(1,2);return F(y.numerator//y.denominator,1<<w)
def tie_possible(c,qs,w):
 terms=[x*(1<<w) for x in [c]+list(qs)]
 D=lcm(*(x.denominator for x in terms)); nums=[int(x*D) for x in terms]
 return D%2==0 and (D//2-nums[0])%gcd(D,*nums[1:])==0
def oracle(c,qs,w):
 periods=[(x*(1<<w)).denominator for x in qs]
 return any(Q(-t,w)!=-Q(t,w) for z in product(*(range(d) for d in periods)) for t in [c+sum(q*k for q,k in zip(qs,z))])
def main():
 for p in json.loads((HERE/'SOURCES.json').read_text())['files']:
  raw=subprocess.check_output(['git','cat-file','blob',p['git_blob']],cwd=ROOT)
  need(hashlib.sha256(raw).hexdigest()==p['sha256'],'Git source')
  if p['usage']=='input':need((ROOT/p['path']).read_bytes()==raw,'source drift')
 vals=sorted({F(n,d) for n in range(-6,7) for d in range(1,10)})
 count=ties=0
 for c,q,w in product(vals,vals,range(4)):
  expected=tie_possible(c,[q],w);need(expected==oracle(c,[q],w),'scalar congruence oracle')
  count+=1;ties+=expected
 lattice=0
 for c,a,b in product((F(0),F(1,4),F(1,2),F(2,3)),vals,vals):
  need(tie_possible(c,[a,b],0)==oracle(c,[a,b],0),'two-parameter congruence oracle');lattice+=1
 dirty_path=ROOT/'research/dirty-prefix-precision/vendor/pr628/dirty.py'
 spec=importlib.util.spec_from_file_location('pinned_dirty',dirty_path);d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
 original=dirty_path.read_text()
 old='value=c.rounded(c.mul(multiplier(i),value),bits)\n        j=destination(i);y[j]=c.add(y[j],scaled(value,sign))'
 new='value=c.rounded(scaled(c.mul(multiplier(i),value),sign),bits)\n        j=destination(i);y[j]=c.add(y[j],value)'
 need(original.count(old)==1,'mutation source location')
 mutant=types.ModuleType('sign_inside_mutant');mutant.__file__=str(dirty_path);exec(compile(original.replace(old,new),str(dirty_path)+'#sign-inside','exec'),mutant.__dict__)
 trials=failures=offties=0;witness=None
 for w,k,y0 in product(range(2,7),range(-9,10),(F(-1),F(0),F(2))):
  x0=(F(k,1<<w),F(0));x=[x0];y=[(y0,F(0))]
  args=dict(coefficient=lambda i:(F(0),F(0)),beta=F(1),bits=w,d=1,multiplier=lambda i:(F(1,2),F(0)))
  d.lift(x,y,sign=1,**args);positive=y[:]
  d.lift(x,y,sign=-1,**args);need(x==[x0] and y==[(y0,F(0))],'unchanged source inverse')
  x=[x0];y=positive[:];mutant.lift(x,y,sign=-1,**args)
  should_fail=(k%2!=0)
  need((y!=[(y0,F(0))])==should_fail,'tie mutation specificity')
  need(x==[x0],'source restored even on failure')
  if should_fail:
   need(y[0][0]-y0==F(1,1<<w),'positive half-up residual');failures+=1
   if (w,k,y0)==(4,1,F(0)):witness={'bits':w,'source':'1/16','forward_target':str(positive[0][0]),'wrong_inverse_target':str(y[0][0]),'expected':'0'}
  else:offties+=1
  trials+=1
 need(witness is not None,'explicit witness')
 # Each omitted arithmetic hypothesis has an exact control.
 need(not tie_possible(F(0),[F(1,3)],0),'odd denominator safe')
 need(tie_possible(F(0),[F(1,2)],0),'even denominator unsafe')
 need(not tie_possible(F(1,4),[F(1,2)],0),'affine offset can avoid all ties')
 need(tie_possible(F(1,4),[F(1,4)],0),'reachable offset tie')
 result={'scalar_cases':count,'scalar_tie_domains':ties,'two_parameter_lattices':lattice,'source_leaf_trials':trials,'wrong_inverse_failures':failures,'off_tie_positive_controls':offties,'witness':witness,'controls':4,'criterion':'D even and gcd(D,u1,...,uk) divides D/2-u0, where2^w(c,q)=u/D','scope':'Sign placement at the last rounding of a deterministic increment; same precision. No existing source bug.'}
 if '--write' in sys.argv:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 else:need(json.loads((HERE/'RESULT.json').read_text())==result,'certificate mismatch')
 print('PASS_SIGNED_ROUNDING_TIES scalar='+str(count)+' lattices='+str(lattice)+' source_failures='+str(failures)+'/'+str(trials))
if __name__=='__main__':main()
