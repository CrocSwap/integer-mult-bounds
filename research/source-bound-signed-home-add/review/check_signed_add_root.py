"""Separate sparse CPU and integer oracle; no author interpreter/checker."""
from pathlib import Path
from types import ModuleType
import copy,hashlib,json,sys
P=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
A=ModuleType('root_checked_signed_add');A.__file__=str(P/'add.py');sys.modules[A.__name__]=A
exec(compile((P/'add.py').read_bytes(),str(P/'add.py'),'exec'),A.__dict__)
def need(ok,why):
 if not ok:raise ValueError(why)
def word(x,w):return format(x%(1<<w),'0'+str(w)+'b')
def gamma(x):
 b=bin(x)[2:];return '0'*(len(b)-1)+b
def cpu(g,initial,stages,unit=False,budget=10000000):
 origins=[-43+11*t for t in range(6)];heads=origins.copy();texts=[initial.get(t,'^') for t in range(6)]
 tapes=[{o+i:c for i,c in enumerate(s)} for o,s in zip(origins,texts)]
 for t,o in enumerate(origins):tapes[t][o-4]='1';tapes[t][o+1000000]='0'
 if unit:
  for t in (A.S,A.T,A.L,A.W,A.B):heads[t]+=1
 low=origins.copy();high=[o+len(s)-1 for o,s in zip(origins,texts)];high[-1]+=200003
 entry=sum(b-a+1 for a,b in zip(low,high));writes=[0]*6;pc=g.start;steps=early=0;returned=rejected=False
 while pc!='HALT':
  if pc==stages['return']:returned=True
  chosen=None
  for rule in g.rules[pc]:
   if all(tapes[t].get(heads[t],'_')==c for t,c in rule.tests):need(chosen is None,'ambiguous rule');chosen=rule
  if chosen is None:rejected=True;break
  for t,c in chosen.writes:
   need(heads[t]!=origins[t] or c=='^','origin guard changed')
   if c=='_':tapes[t].pop(heads[t],None)
   else:tapes[t][heads[t]]=c
   writes[t]+=1
   if t==0:early+=not returned
  for t,d in chosen.moves:
   need(d in (-1,0,1),'nonlocal move');heads[t]+=d;need(heads[t]>=origins[t],'origin crossed')
   low[t]=min(low[t],heads[t]);high[t]=max(high[t],heads[t])
  pc=chosen.target;steps+=1;need(steps<=budget,'bounded separate CPU exhausted')
 for t,o in enumerate(origins):need(tapes[t].get(o)=='^' and tapes[t].get(o-4)=='1' and tapes[t].get(o+1000000)=='0','opaque/origin preservation')
 def read(t,n):return ''.join(tapes[t].get(origins[t]+i,'_') for i in range(n))
 if not rejected:
  need(heads==origins,'successful head return')
  for t in ((0,A.L,A.W,A.B) if unit else range(1,6)):
   o=origins[t];need(set(tapes[t])=={o,o-4,o+1000000},'private retirement')
 return dict(read=read,rejected=rejected,reject_state=pc,writes=writes,early=early,steps=steps,
             entry_head_history=entry,final_head_history=sum(b-a+1 for a,b in zip(low,high)))
def unit_graph(operation):
 g=A.D.Graph();stages={};A.primitive(g,operation,2,'HALT',stages);g.start=stages['component_entry'];g.validate();return g,stages
def complete_case(operation,shape,late=False):
 f,r,p,s,w,cutoff=shape;n=2*r*p*s*(1<<(9*f));m=1<<(w-1)
 values=range(-m,m) if w==6 else (-m,-m+1,-1,0,1,m-2,m-1)
 pairs=[(a,b) for a in values for b in values if -m<=(b-a if operation=='SUB' else b+a)<m]
 xs=[pairs[i%len(pairs)][0] for i in range(n)];ys=[pairs[i%len(pairs)][1] for i in range(n)]
 if late:xs=[1]*(n-1)+[-1 if operation=='SUB' else 1];ys=[0]*(n-1)+[m-1]
 h=''.join(gamma(t) for t in shape);source=h+''.join(word(t,w) for t in xs);target=h+''.join(word(t,w) for t in ys)
 initial='^'+source+'|'+target+'|$';g,stages=A.compile_home(operation);z=cpu(g,{0:initial},stages)
 if late:
  need(z['rejected'] and z['reject_state']==stages['overflow'],'late final overflow')
  need(z['read'](0,len(initial))==initial and z['writes'][0]==0,'HOME unchanged on rejection')
  need(z['writes'][2]>len(target)+w,'substantial private arithmetic before overflow')
 else:
  outputs=[b-a if operation=='SUB' else b+a for a,b in zip(xs,ys)]
  expected='^'+source+'|'+h+''.join(word(t,w) for t in outputs)+'|$'
  need(not z['rejected'] and z['read'](0,len(expected))==expected,'full scientific fields')
  need(z['writes'][0]==2*len(source) and z['early']==0,'post-return scatter only')
 need(z['steps']<=4096*(len(source)+1),'conservative complete two-HOME bound')
 return dict(operation=operation,shape=shape,F=len(source),components=n,late_overflow=late,
             steps=z['steps'],HOME_writes=z['writes'][0],early_HOME_writes=z['early'],
             entry_head_history=z['entry_head_history'],final_head_history=z['final_head_history'])
def main():
 units=[]
 for operation in ('ADD','SUB'):
  g,stages=unit_graph(operation)
  for w in range(2,7):
   m=1<<(w-1);count=failures=0
   for source in range(-m,m):
    for target in range(-m,m):
     initial={A.S:'^'+word(source,w)+'|',A.T:'^'+word(target,w)+'|',A.W:'^'+'1'*w}
     z=cpu(g,initial,stages,unit=True,budget=10000);value=target-source if operation=='SUB' else target+source;fit=-m<=value<m
     need(z['rejected']!=fit,'exact signed overflow classification');need(z['read'](A.S,w+2)==initial[A.S],'unit source preserved')
     if fit:need(z['read'](A.T,w+2)=='^'+word(value,w)+'|','unit exact signed result')
     else:need(z['reject_state']==stages['overflow'],'only final signed overflow')
     count+=1;failures+=not fit
   units.append(dict(operation=operation,w=w,all_signed_pairs=count,overflow_pairs=failures))
 bad,stages=unit_graph('SUB');bad=copy.deepcopy(bad);zero=next(s for s in bad.rules if s.startswith('carry-0.'));edited=0
 for s,rules in list(bad.rules.items()):
  new=[]
  for rule in rules:
   if rule.target.startswith('carry-1.') and rule.moves==((A.S,-1),(A.T,-1),(A.W,-1)):
    rule=A.D.Rule(rule.tests,rule.writes,rule.moves,zero);edited+=1
   new.append(rule)
  bad.rules[s]=new
 need(edited==1,'initial subtraction carry control target')
 mutant=cpu(bad,{A.S:'^000|',A.T:'^000|',A.W:'^111'},stages,unit=True)
 need(not mutant['rejected'] and mutant['read'](A.T,5)!='^000|','missing subtraction +1 detected')
 full=[]
 for operation in ('ADD','SUB'):
  full.append(complete_case(operation,(1,4,1,1,6,1)));full.append(complete_case(operation,(1,2,2,3,5,1<<256)))
  full.append(complete_case(operation,(1,1,1,1,6,1),late=True))
 print(json.dumps({'marker':'PASS_ROOT_SIGNED_HOME_ADD_REVIEW','unit_components':units,'complete_fields':full,
  'negative_control':'missing initial subtraction carry gives a wrong zero-minus-zero result',
  'unit_scope':'exhaustive local component-entry contract only; complete Gamma geometry supplied separately in full-field tests',
  'independence':'separate sparse signed-origin CPU and unbounded integer oracle; no author interpreter/checker imported',
  'history_note':'head-window counters include older blank visits, not complete unknown opaque K_entry',
  'hashes':{n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in ('add.py','inputs/tape_graph.py','inputs/machine.py')}},indent=2))
if __name__=='__main__':main()
