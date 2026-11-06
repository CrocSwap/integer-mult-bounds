"""Exact held-row census and reverse response construction for triple recoding.
Jerry Chen / @CubeJerry, substantial OpenAI Codex assistance. Apache-2.0.
Native word #6702; predecessor carrier method #6765/#6767.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import gzip, json
HERE=Path(__file__).resolve().parent
WORD_SHA='e8c7a9d54d98a4cfa27e15593016b3908afed303e0f480076ed3f596192e5a4d'
def need(condition,message):
 if not condition:raise ValueError(message)
def scalar(value):
 value=Fraction(value)
 need(value.denominator&(value.denominator-1)==0,'Dyadic scalar')
 return value
def add(dest,source,scale=1):
 for key,value in source.items():
  z=dest.get(key,Fraction(0))+scale*value
  if z:dest[key]=z
  else:dest.pop(key,None)
def freeze(vector):return tuple(sorted(vector.items()))
def load_word():
 raw=(HERE/'inputs/PR6702-WORD.json.gz').read_bytes()
 need(sha256(raw).hexdigest()==WORD_SHA,'Pinned native word')
 return json.loads(gzip.decompress(raw))
def census(word):
 program,n=word['program'],word['public'];N=n+word['owned_fields']
 writes,reads=defaultdict(list),defaultdict(list)
 for i,entry in enumerate(program):
  writes[entry[1]].append(i)
  if entry[0]in('ADD','COPY'):reads[entry[2]].append(i)
 main=set(word['live'])|{r+112 for r in word['live']};intervals=[]
 for role in range(n):
  if role in main:continue
  moves=[i for i in writes[role]if program[i][0]=='MOVE']
  for first,last in zip(moves,moves[1:]):
   middle=[i for i in writes[role]if first<i<last]
   if any(program[i][0]!='SCALE'for i in middle):continue
   exports=[i for i in reads[role]if first<i<last]
   if not exports:continue
   need(all(program[i][0]=='ADD'for i in exports),'ADD-only exports')
   previous=[i for i in writes[role]if i<first and program[i][0]!='SCALE'];following=[i for i in writes[role]if i>last and program[i][0]!='SCALE']
   intervals.append(dict(role=role,first=first,last=last,lo=previous[-1]+1 if previous else 0,hi=following[0]if following else len(program),exports=exports))
 at=defaultdict(list)
 for interval in intervals:at[interval['first']].append(interval)
 rows=[{r:Fraction(1)}if r<n else{}for r in range(N)];groups=defaultdict(list);copies=0
 for i,entry in enumerate(program):
  for interval in at[i]:
   row=rows[interval['role']];need(bool(row),'Nonzero rational source row')
   factor=row[min(row)];rowkey=tuple((r,v/factor)for r,v in sorted(row.items()))
   interval['normalization']=str(factor);interval['rowkey']=tuple((r,str(v))for r,v in rowkey);groups[rowkey].append(interval)
  operation,role=entry[:2]
  if operation in('INIT','CLEAR'):rows[role]={}
  elif operation=='SCALE':
   factor=Fraction(entry[2]);need(scalar(factor)!=0,'Nonzero SCALE');need(abs(factor.numerator)&(abs(factor.numerator)-1)==0,'SCALE dyadic inverse')
   rows[role]={r:v*factor for r,v in rows[role].items()}
  elif operation in('ADD','COPY'):
   need(role!=entry[2],'No self ADD/COPY')
   if operation=='COPY':need(not rows[role],'Exact COPY-zero premise');copies+=1
   factor=Fraction(entry[3]);scalar(factor)
   for r,value in rows[entry[2]].items():
    value=rows[role].get(r,Fraction(0))+factor*value
    if value:rows[role][r]=value
    else:rows[role].pop(r,None)
 expected=[{r:Fraction(1)}if r<n else{}for r in range(N)]
 for r in word['live']:expected[r+112][r]=Fraction(1)
 need(rows==expected,'All-input exact native endpoint');triples=[]
 for rowkey,members in groups.items():
  if len(members)!=3:continue
  members=sorted(members,key=lambda x:x['first']);need(len({c['role']for c in members})==1,'Single helper per triple')
  need(all(a['last']==b['first']for a,b in zip(members,members[1:])),'Consecutive triple chain')
  role,first,last=members[0]['role'],members[0]['first'],members[-1]['last']
  need(all(program[z][0]in('SCALE','MOVE')for z in writes[role]if first<z<last),'No source feedback')
  lo,hi=members[0]['lo'],members[-1]['hi'];move_indices=[c['first']for c in members]+[last]
  frames=[program[first][2]]+[program[z][3]for z in move_indices];need(len(set(frames))==5,'Distinct chain frames')
  ranks=[len(word['frames'][program[z][3]])-len(word['frames'][program[z][2]])for z in move_indices]
  need(all(r>0 for r in ranks),'Positive paid transport ranks');exports=sorted(z for c in members for z in c['exports'])
  need(exports==[z for z in reads[role]if first<z<last],'All internal exports removed exactly once')
  triples.append(dict(role=role,first=first,last=last,lo=lo,hi=hi,lower=max([lo]+[z+1 for z in reads[role]if lo<=z<first]),upper=min([hi]+[z for z in reads[role]if last<z<hi]),moves=move_indices,frames=frames,ranks_before=ranks,exports=exports,members=members))
 summary=dict(intervals=len(intervals),classes=len(groups),class_sizes=dict(sorted(Counter(len(c)for c in groups.values()).items())),triples=len(triples),copy_zero_checks=copies,public_inputs=n,endpoint_rows=N)
 return intervals,groups,triples,writes,reads,summary
def suffix(word):
 program,n=word['program'],word['public'];N=n+word['owned_fields']
 columns=[{r:1}if r<n and word['final'][r]!=127 else{}for r in range(N)]
 frames=word['final'][:]+[None]*word['owned_fields'];ends=[len(program)]*N;residences=[];after={}
 def save(role,low,high):
  if low<=high and frames[role]is not None:residences.append((role,low,high,frames[role],freeze(columns[role])))
 monitor=n
 for i in range(len(program)-1,-1,-1):
  entry=program[i];operation,role=entry[:2];touched={role}
  if operation in('ADD','COPY'):touched.add(entry[2])
  for r in touched:save(r,i+1,ends[r]);ends[r]=i
  after[i]=columns[role].copy()
  if operation=='MOVE':frames[role]=entry[2]
  elif operation=='SCALE':
   factor=scalar(entry[2]);columns[role]={r:v*factor for r,v in columns[role].items()}
  elif operation in('ADD','COPY'):
   add(columns[entry[2]],columns[role],scalar(entry[3]))
   if operation=='COPY':columns[role][monitor]=1;monitor+=1
  elif operation in('INIT','CLEAR'):columns[role]={};frames[role]=None if operation=='INIT'else entry[2]
  else:raise ValueError(operation)
 for r in range(N):save(r,0,ends[r])
 return residences,after,monitor-n
def target(word,triple,writes,after):
 result={}
 for z in triple['exports']:
  factor=scalar(word['program'][z][3])
  for i in writes[triple['role']]:
   if triple['first']<i<z and word['program'][i][0]=='SCALE':factor=factor*scalar(word['program'][i][2])
  add(result,after[z],factor)
 return result
def topology_nodes(triple,residences,keep):
 frames=[triple['frames'][k]for k in keep];nodes=[]
 for role,low,high,frame,response in residences:
  if role==triple['role']or not response or frame not in frames:continue
  low,high=max(low,triple['lo']),min(high,triple['hi'])
  if low<=high:nodes.append((low,high,frames.index(frame),response))
 return nodes
def columns_at(nodes,cuts,frame_count):
 return[dict(v)for v in sorted({v for low,high,k,v in nodes if(k==0 or high>=cuts[k-1])and(k==frame_count-1 or low<=cuts[k])})]
def span(columns,target_vector):
 basis={}
 for col in columns:
  row=dict(col)
  while row:
   p=min(row)
   if p not in basis:
    factor=Fraction(1)/row[p];basis[p]={k:v*factor for k,v in row.items()};break
   add(row,basis[p],-row[p])
 remainder=target_vector.copy()
 while remainder:
  p=min(remainder)
  if p not in basis:return False,len(basis)
  add(remainder,basis[p],-remainder[p])
 return True,len(basis)
def proper_keeps():
 for count in range(3):
  for inside in combinations((1,2,3),count):yield(0,*inside,4)

def dual(columns,target_vector):
 """Exact rational analogue of #6765's independently checked dual solver."""
 basis={}
 for column in reversed(columns):
  row=dict(column)
  for pivot in sorted(basis,reverse=True):
   if pivot in row:add(row,basis[pivot],-row[pivot])
  if row:
   pivot=max(row);factor=Fraction(1)/row[pivot]
   basis[pivot]={k:v*factor for k,v in row.items()}
 residual=target_vector.copy()
 for pivot in sorted(basis,reverse=True):
  if pivot in residual:add(residual,basis[pivot],-residual[pivot])
 if not residual:return None
 witness={max(residual):Fraction(1)}
 for pivot in sorted(basis):
  z=sum(witness.get(k,0)*v for k,v in basis[pivot].items())
  if z:
   value=witness.get(pivot,0)-z
   if value:witness[pivot]=value
   else:witness.pop(pivot,None)
 factor=sum(witness.get(k,0)*v for k,v in target_vector.items())
 need(factor!=0,'Nonzero separating value')
 witness={k:v/factor for k,v in witness.items()}
 need(dual_ok(witness,columns,target_vector),'Every exact dual dot product')
 return witness

def dual_ok(witness,columns,target_vector):
 return all(sum(witness.get(k,0)*v for k,v in col.items())==0 for col in columns)and sum(witness.get(k,0)*v for k,v in target_vector.items())==1

def vector_json(vector):return[[k,str(v)]for k,v in sorted(vector.items())]
def digest(value):return sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def census_digest(intervals):
 return digest(sorted(intervals,key=lambda c:(c['role'],c['first'],c['last'])))
def residence_digest(residences):
 return digest(sorted((r,l,h,f,vector_json(dict(v)))for r,l,h,f,v in residences))
