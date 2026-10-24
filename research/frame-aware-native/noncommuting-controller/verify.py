"""Literal p16 free-associative operator replay. Apache-2.0; OpenAI assistance."""
from fractions import Fraction as Q
from pathlib import Path
import json,hashlib
P=Path(__file__).parent
SOURCE_SHA256='1f5d6aa267e4e66048818714b5d3b5eae17a58abe91d15deeaa34574f7391a5f'

def need(ok,message):
 if not ok:raise ValueError(message)

def plus(a,b,c=1):
 out=dict(a)
 for key,v in b.items():
  out[key]=out.get(key,0)+c*v
  if not out[key]:del out[key]
 return out

def left_word(a,q,word,c=1):
 return {(k[0]+q,tuple(word)+k[1]):v*c for k,v in a.items()}

def literal(events,n,wrong_query=False,wrong_idle=False):
 M=[[{(0,()):Q(1)}if i==j else {}for j in range(n)]for i in range(n)]
 q_control=False;idle_control=False
 for ev in events:
  op=ev[0]
  if op in ['LOCAL','QUERY_SHEAR']:
   _,stage,pair,reverse=ev
   if wrong_query and op=='QUERY_SHEAR'and not q_control:reverse=not reverse;q_control=True
   x,y=2*pair,2*pair+1
   if reverse:x,y=y,x
   M[y]=[plus(u,left_word(v,1 if reverse else -1,(),-1 if reverse else 1))for u,v in zip(M[y],M[x])]
   if op=='LOCAL':
    for role in [x,y]:M[role]=[left_word(u,0,(stage,))for u in M[role]]
  elif op=='IDLE':
   _,pair,selected=ev;word=tuple(reversed(selected))
   if wrong_idle and len(word)>=2 and not idle_control:word=word[::-1];idle_control=True
   for role in [2*pair,2*pair+1]:M[role]=[left_word(u,0,word)for u in M[role]]
  elif op=='ADD':
   _,dst,src,*c=ev;M[dst]=[plus(u,v,c[0]if c else 1)for u,v in zip(M[dst],M[src])]
  elif op=='SIGNED_SWAP':
   _,a,b=ev;M[a],M[b]=M[b],[left_word(u,0,(),-1)for u in M[a]]
  else:raise ValueError('Unknown event')
 return M

def transform(M,L,R):
 n=len(M);T=[[{}for _ in range(n)]for _ in range(n)]
 for i,row in enumerate(L):
  for k,c in enumerate(row):
   c=Q(c)
   if c:
    for j,v in enumerate(M[k]):T[i][j]=plus(T[i][j],v,c)
 out=[[{}for _ in range(n)]for _ in range(n)]
 for k,row in enumerate(R):
  for j,c in enumerate(row):
   c=Q(c)
   if c:
    for i in range(n):out[i][j]=plus(out[i][j],T[i][k],c)
 return out

def check(M,certificate):
 n=len(M);want=certificate['diagonal']
 for i in range(n):
  for j in range(n):
   expected={(want[i][0],tuple(want[i][1])):Q(1)}if i==j else {}
   need(M[i][j]==expected,'Free-word endpoint at row '+str(i)+' column '+str(j))

def scalar_boundary(A):
 n=len(A);A=[[Q(x)for x in row]for row in A];work=[row[:]for row in A];ops=[]
 def dyadic(q):return q.denominator&(q.denominator-1)==0
 for j in range(n):
  k=next((i for i in range(j,n)if work[i][j]),None);need(k is not None,'Invertible scalar boundary')
  if k!=j:work[j],work[k]=work[k],work[j];ops.append(('swap',j,k))
  if work[j][j]!=1:
   q=1/work[j][j];need(dyadic(q)and dyadic(1/q),'Reversible dyadic boundary scale')
   work[j]=[q*x for x in work[j]];ops.append(('scale',j,q))
  for i in range(n):
   if i!=j and work[i][j]:
    q=-work[i][j];need(dyadic(q),'Dyadic scalar boundary ADD')
    work[i]=[x+q*y for x,y in zip(work[i],work[j])];ops.append(('add',i,j,q))
 replay=[[Q(i==j)for j in range(n)]for i in range(n)]
 for op in reversed(ops):
  if op[0]=='swap':_,a,b=op;replay[a],replay[b]=replay[b],replay[a]
  elif op[0]=='scale':_,a,q=op;replay[a]=[x/q for x in replay[a]]
  else:_,a,b,q=op;replay[a]=[x-q*y for x,y in zip(replay[a],replay[b])]
 need(replay==A,'Synthesized scalar boundary replay')
 return len(ops)

def run():
 need(hashlib.sha256((P/'CONTROLLER.json').read_bytes()).hexdigest()==SOURCE_SHA256,'Pinned #4470 source bytes')
 source=json.loads((P/'CONTROLLER.json').read_text());certificate=json.loads((P/'FREE-CERTIFICATE.json').read_text());n=32
 events=source['physical_events']
 need(len(events)==154,'154 source events')
 thick={0,32,*range(1,32,2)}
 full=[e[1]for e in events if e[0]=='LOCAL'];thin=[e[1]for e in events if e[0]=='QUERY_SHEAR']
 need(len(full)==18 and set(full)==thick,'Exactly the 18 declared thick stages')
 need(len(thin)==15 and set(thin)==set(range(33))-thick,'Exactly the 15 remaining query-only stages')
 need(all(e[1]in thick for e in events if e[0]=='LOCAL'),'Stage allowlist')
 need(all(set(e[2])<=thick for e in events if e[0]=='IDLE'),'Idle stage allowlist')
 need(len(certificate['diagonal'])==32,'32 declared diagonal entries')
 need(sum(q==-1 for q,w in certificate['diagonal'])==16 and sum(q==1 for q,w in certificate['diagonal'])==16,'Balanced central exponents')
 need(all(set(w)<=thick for q,w in certificate['diagonal']),'Diagonal stage allowlist')
 check(transform(literal(events,n),certificate['left'],certificate['right']),certificate)
 boundary_operations={k:scalar_boundary(certificate[k])for k in ['left','right']}
 controls={}
 for name,kw in [('wrong_query',{'wrong_query':True}),('reordered_idle',{'wrong_idle':True})]:
  try:check(transform(literal(source['physical_events'],n,**kw),certificate['left'],certificate['right']),certificate)
  except ValueError:controls[name]=True
  else:raise ValueError('Control not rejected: '+name)
 global_word=max((w for q,w in certificate['diagonal']),key=len)
 nonempty=[w for w in certificate['paid_idle']if w]
 need(len(nonempty)==15,'15 nonempty paid idle words')
 need(nonempty==[list(reversed(e[2]))for e in events if e[0]=='IDLE'],'Certificate idle words match literal chronology')
 from collections import Counter
 expected=Counter((q,tuple(w))for w in nonempty+[global_word]for q in [-1,1])
 need(Counter((q,tuple(w))for q,w in certificate['diagonal'])==expected,'Each paid idle and the global word occur once with each central exponent')
 need(len(global_word)==18 and set(global_word)==thick,'Longest word contains every thick stage exactly once')
 need(all(any(global_word[i:i+len(w)]==w for i in range(len(global_word)))for w in nonempty),'Every idle is contiguous')
 result={'status':'PASS_NONCOMMUTATIVE_STAGE_P16_IDENTITY','dimension':n,'stage_operator_assumptions':'D_s arbitrary endomorphisms; Q invertible and commuting with all D_s; no D_s-D_t commutation used','coefficient_domain':'rational free associative algebra in D_s with central invertible Q','controls':controls,'scalar_boundary_operations':boundary_operations,'global_word':global_word,'paid_idle_words_contiguous':True,'new_kappa':False,'inputs':{f:hashlib.sha256((P/f).read_bytes()).hexdigest()for f in ['CONTROLLER.json','FREE-CERTIFICATE.json']}}
 print(json.dumps(result,indent=2))
if __name__=='__main__':run()
