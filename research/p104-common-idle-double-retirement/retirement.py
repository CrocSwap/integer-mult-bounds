"""Exact ordinary two-sided retirement on the changed eight-field caller.

The dual-pair method is inherited from PR5599/PR6545. The new prefix and
its explicit rational pairs are source-specific and independently checked.
"""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
G=[['SCALE',4,'-1'],['ADD',21,4,'1'],['ADD',4,20,'1']]
J=[['SWAP',4,21],['ADD',4,1,'1'],['ADD',4,20,'-1'],
   ['ADD',0,4,'2'],['ADD',2,4,'-2'],['ADD',20,4,'2']]
def inverse(events):
 out=deepcopy(list(reversed(events)))
 for e in out:
  if e[0]=='ADD':e[-1]=str(-Q(e[-1]))
  elif e[0]=='SCALE':e[-1]=str(1/Q(e[-1]))
  elif e[0]=='LAMBDA':e[-1]=-e[-1]
  elif e[0]!='SWAP':raise ValueError('ordinary basis only')
 return out
def construct(source):
 w=deepcopy(source);cut=353;pivot=4;fresh=w['roles'];group=[4,20,21]
 if w['events'][cut]!=['LAMBDA',20,1]:raise ValueError('exact new cut')
 if len({tuple(w['diagonal'][r][1:])for r in group})!=1:raise ValueError('equal complete targets')
 normalized=w['events']+[['LAMBDA',r,1]for r in group]
 slots={'ADD':(1,2),'SWAP':(1,2),'SCALE':(1,),'LAMBDA':(1,),'Q_POWER':(1,),
        'QUERY':(1,2),'LOCAL':(2,3),'IDLE':(1,2),'IDLE_ONE':(1,)}
 def rename(e):
  e=deepcopy(e)
  for j in slots[e[0]]:
   if e[j]==pivot:e[j]=fresh
  return e
 w['events']=inverse(G)+normalized[:cut+1]+J
 handoff=len(w['events'])-1
 w['events'] += [rename(e)for e in inverse(J)+normalized[cut+1:]+G]
 w['events'] += [['LAMBDA',r,-1]for r in group]
 w['roles']+=1
 w['diagonal'][pivot]=[-1]+[0]*(w['stages']+1)
 w['diagonal'].append([0,*source['diagonal'][pivot][1:]])
 return w,{'cut_after':cut,'handoff_after':handoff,'pivot':pivot,'fresh':fresh,'group':group,
           'boundary':G,'middle':J,
           'a':{'1':'1','20':'-1','21':'1'},'b':{'0':'-2','2':'2','20':'-2','21':'-1'},
           'c':{'20':'1','4':'-1'},'d':{'4':'-1','21':'-1'}}
if __name__=='__main__':
 w,p=construct(json.loads((HERE/'CONTROLLER-UNRETIRED.json').read_text()))
 (HERE/'CONTROLLER.json').write_text(json.dumps(w,indent=2)+'\n');(HERE/'WITNESS.json').write_text(json.dumps(p,indent=2)+'\n')
 print(json.dumps({'fields':w['roles'],'events':len(w['events']),'fresh':p['fresh'],'cut':p['cut_after']}))
