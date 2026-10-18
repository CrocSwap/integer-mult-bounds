import importlib.util,json
from fractions import Fraction as Q
from pathlib import Path
spec=importlib.util.spec_from_file_location('invoice',str(Path(__file__).with_name('two_root_invoice.py')));p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
def run(word):
 s=[{('r'+str(i),):Q(1)} for i in range(11)]
 for k,f,a,b,sgn in word:
  if k=='S':s[b]={key:val*Q(2)**(f*sgn) for key,val in s[b].items()};continue
  pref=(f,) if k=='F' else ();scale=sgn if k=='F' else f*sgn
  for key,val in list(s[a].items()):
   key=pref+key;s[b][key]=s[b].get(key,0)+scale*val
   if not s[b][key]:del s[b][key]
 return s
expected=[{('r'+str(i),):Q(1)} for i in range(11)]
for i in range(3):
 for j in range(3):
  if p.v.M[i][j]:expected[3+i][tuple(reversed(p.factors['A'+str(i)]))+tuple(reversed(p.factors['B'+str(j)]))+('r'+str(j),)]=Q(p.v.M[i][j])
checks={}
for name,w in p.words.items():
 if run(w)!=expected:raise ValueError('expanded map '+name)
 if run(w+p.inverse(w))!=run([]):raise ValueError('expanded inverse '+name)
 checks[name]={'map':True,'inverse':True,'factor_calls':sum(k=='F' for k,*_ in w),'root_operations':sum(k!='F' for k,*_ in w)}
w=p.words['two_root12'];controls=[]
for idx in [0,len(w)//2,len(w)-1]:
 if run(w[:idx]+w[idx+1:])==expected:raise ValueError('omission missed')
 controls.append(idx)
print('PASS_EXPANDED_TWO_ROOT',checks,'controls',controls)
Path(__file__).with_name('two_root_expanded.json').write_text(json.dumps({'checks':checks,'omission_controls':controls,'formal_inputs':11,'distinct_noncommuting_factors':27},indent=2)+'\n')
