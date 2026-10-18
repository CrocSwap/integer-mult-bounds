"""Independent dense and frozen-dispatch checks of the free-prefix claim."""
from pathlib import Path
import importlib.util,random,json,hashlib,math
P=Path(__file__).resolve().parent

def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
s=load('free_symbolic',P/'symbolic.py');c=load('new_core',P/'core.py')
m=load('dense877',P/'vendor/877/matrices.py');v=load('dirty628',P/'vendor/628/dirty.py')

def check():
 words=[]
 for n in range(1,65):
  for sign in [-1,1]:
   generated=list(s.core.word(n,sign));literal=m.vendor_word(v,n,sign)
   c.need(generated==literal,'independent word matches frozen dispatcher')
   c.need(len(literal)==c.resources(n)[1],'complete leaf count')
   words.append(dict(n=n,sign=sign,leaves=len(literal),sha256=hashlib.sha256(json.dumps(literal).encode()).hexdigest()))
 dense=[];rng=random.Random(890877862)
 for n in [1,2,3,5,8,15,16,31,63]:
  factors=[[[rng.randrange(-2,3) for _ in range(2)] for _ in range(2)] for _ in range(n)]
  if n<=8:
   # Enumerate ordered subsets independently, including identity.
   products=[m.identity(2)]
   for f in factors:products+= [m.multiply(f,p) for p in products]
   G=max(1,max(m.norm(p) for p in products))
  else:G=math.prod(max(1,m.norm(f)) for f in factors)
  depth,N,C=c.resources(n)
  for sign in [-1,1]:
   row=m.trace(factors,list(s.core.word(n,sign)),sign,depth+2,C*G)
   dense.append(dict(n=n,sign=sign,subset_bound=G,coefficient_bound=C,**row))
 controls=[]
 def reject(name,action):
  try:action()
  except (ValueError,StopIteration) as err:controls.append(dict(name=name,rejected=str(err)))
  else:raise ValueError('control accepted '+name)
 # Distinctness of factors is a real condition, not a count-degree heuristic.
 bad=s.identity(2);bad[1][0]={(0,0):1}
 reject('repeated_factor_monomial',lambda:s.audit(bad,2))
 bad=s.identity(2);bad[1][0]={(0,1):1}
 reject('unordered_noncommuting_word',lambda:s.audit(bad,2))
 fs=[[[1,2],[0,1]],[[1,0],[3,1]]]
 W=list(s.core.word(2));B=6*max(1,m.norm(m.multiply(fs[1],fs[0])))
 reject('omitted_last_restore',lambda:m.trace(fs,W[:-1],1,3,B))
 reject('wrong_inverse_order',lambda:m.trace(fs,[(a,b,j,-q) for a,b,j,q in W],-1,3,B))
 # A zero full product leaves a nontrivial prefix; full norm alone is insufficient.
 fs=[[[3,0],[0,3]],[[0,0],[0,0]]]
 reject('whole_product_only_bound',lambda:m.trace(fs,W,1,3,1))
 reject('missing_feedback_smallness',lambda:c.execution(2,3,1,10,0))
 row=c.uniform(64,128,20,160)
 for key,value in [('working_bits',row['working_bits']-1),('prefix_exponent',1),('leaf_calls',63),('coefficient_error_exponent',128),('input_bits',True)]:
  bad={**row,key:value};reject('corrupt_'+key,lambda bad=bad:c.check_uniform(bad))
 reject('unsupported_radix',lambda:c.uniform(6,128,20,160))
 saved=m.inverse_step
 try:
  m.inverse_step=m.prefix_step
  reject('incorrect_inverse_prefix_engine',lambda:m.trace([[[1,2],[0,1]],[[1,0],[3,1]]],W,1,3,100))
 finally:m.inverse_step=saved
 # The full kernel can be identity while a nonshared first inverse is arbitrarily large.
 f1=[[16,0],[0,1]];f2=[[0,1],[1,0]]
 c.need(m.multiply(f1,f2)!=m.multiply(f2,f1),'noncommuting witness')
 # Deliberately no full-inverse-to-subset assertion is admitted for these factors.
 return dict(status='PASS',frozen_words=words,dense_prefixes=dense,negative_controls=controls)
