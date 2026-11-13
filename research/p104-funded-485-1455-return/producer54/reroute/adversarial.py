"""Independent exact audit and corruption controls for the 13-event reroute.

Only the frozen source word and emitted candidate are read. No emitter or retained
validator is imported. A complete local row identity is combined with exact
native frame/lifecycle checks and literal prefix witnesses for every mutation.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from hashlib import sha256
import gzip,json
D=Path(__file__).resolve().parent;ROOT=D.parents[1]
base=json.load(gzip.open(ROOT/'inputs/pr7480/WORD.json.gz','rt'))
word=json.load(gzip.open(D/'WORD.json.gz','rt'))
p=base['program'];q=word['program'];n=base['public'];m=n+base['owned_fields']
canon=lambda w:sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert canon(base)=='5044adee019f073f286789ccb688ffca76d42b60518242bb4daea818d33d337a'
assert canon(word)=='64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
lo,hi=33163,33219
splice=[['ADD',212,1455,'1',3],['ADD',1455,976,'1',3],['ADD',485,1455,'-2',3],['ADD',1455,485,'2/3',3],['MOVE',1455,3,721,False],['ADD',824,1455,'-3/2',721],['ADD',824,54,'-1',721],['ADD',1455,54,'1/2',721],['MOVE',1455,721,724,False],['MOVE',485,3,724,False],['ADD',1455,485,'-2/3',724],['ADD',485,1455,'2',724],['MOVE',1455,724,904,False]]
skip={33163,33164,33165,33172,33186,33191,33200,33201,33203,33205}
expected=p[:lo]+splice+[e for i,e in enumerate(p[lo:],lo)if i not in skip]
assert q==expected
assert all(base[k]==word[k]for k in base if k!='program')

def add(a,b,c):
 for j,v in b.items():
  z=a.get(j,Q(0))+c*v
  if z:a[j]=z
  else:a.pop(j,None)

def elementary(rows,e,guards=None,index=None):
 op,r=e[:2]
 if op in('INIT','CLEAR'):rows[r]={}
 elif op=='SCALE':rows[r]={j:v*Q(e[2])for j,v in rows[r].items()}
 elif op in('ADD','COPY'):
  if op=='COPY':
   if guards is not None:guards.append((index,dict(rows[r])))
   rows[r]={}
  add(rows[r],rows[e[2]],Q(e[3]))

def local(events):
 rows=[{i:Q(1)}for i in range(m)]
 for e in events:elementary(rows,e)
 return rows
source_local=p[lo:hi]
changed_local=splice+[e for i,e in enumerate(p[lo:hi],lo)if i not in skip]
a,b=local(source_local),local(changed_local)
assert a==b
new_hi=lo+len(changed_local);assert q[new_hi:]==p[hi:]

# The pair is encoded and decoded by determinant-one rational shears.
E=[[Q(1),Q(-2)],[Q(2,3),Q(-1,3)]]
I=[[Q(-1,3),Q(2)],[Q(-2,3),Q(1)]]
def det2(A):return A[0][0]*A[1][1]-A[0][1]*A[1][0]
assert det2(E)==det2(I)==1
assert [[sum(I[i][k]*E[k][j]for k in range(2))for j in range(2)]for i in range(2)]==[[1,0],[0,1]]
# Scalar affine identity on independent S,D,N,T,A,J at the splice entry.
order=[485,1455,976,54,824,212]
rows=[{i:Q(1)}for i in range(m)]
for e in splice:elementary(rows,e)
assert rows[485]=={485:Q(1),54:Q(1)}
assert rows[1455]=={1455:Q(1),976:Q(1),54:Q(1,2)}
assert rows[824]=={824:Q(1),485:Q(-1),1455:Q(1,2),976:Q(1,2),54:Q(-1)}
assert rows[212]=={212:Q(1),1455:Q(1)}
assert rows[976]=={976:Q(1)} and rows[54]=={54:Q(1)}

# Full word structural guards, including strict public rises and owned descent.
def span(bs):
 s={0}
 for x in bs:
  assert x not in s and 0<x<512
  s|={x^y for y in tuple(s)}
 return s
spaces=list(map(span,base['frames']))
def structural(w):
 f=w['initial']+[None]*w['owned_fields'];paid=Counter();rise=Counter();life=0;live=0;peak=0;owned_contacts=[];copy=[]
 for i,e in enumerate(w['program']):
  op,r=e[:2]
  assert 0<=r<m
  if op in('ADD','COPY','SCALE'):
   c=Q(e[2]if op=='SCALE'else e[3]);assert c and abs(c)+1<2**16
   for v in [c.denominator]+([abs(c.numerator)]if op=='SCALE'else[]):
    for prime in(2,3,5):
     while v%prime==0:v//=prime
    assert v==1
  if op=='INIT':assert r>=n and f[r]is None;f[r]=e[2];life+=1;live+=1;peak=max(peak,live)
  elif op=='CLEAR':assert r>=n and f[r]==e[2];f[r]=None;live-=1
  elif op=='MOVE':
   assert f[r]==e[2],('MOVE_SOURCE',i,e,f[r]);assert e[4]==(r>=n)
   assert spaces[e[2]]<spaces[e[3]]or(r>=n and spaces[e[3]]<spaces[e[2]])
   inc=len(w['frames'][e[3]])-len(w['frames'][e[2]]);paid[abs(inc)]+=1
   if r>=n and inc>0:rise[inc]+=1
   f[r]=e[3]
  else:
   used=e[1:3]if op in('ADD','COPY')else e[1:2]
   assert all(0<=s<m and f[s]==e[-1]for s in used)
   assert op not in('ADD','COPY')or e[1]!=e[2]
   if op=='COPY':copy.append((i,e))
  used=e[1:3]if op in('ADD','COPY')else e[1:2]
  if any(s>=n for s in used):owned_contacts.append(e)
 assert f==w['final']+[None]*w['owned_fields'] and live==0
 return {'paid':paid,'owned_rises':rise,'lifetimes':life,'peak':peak,'owned_contacts':owned_contacts,'copy':copy}
sold=structural(base);snew=structural(word)
assert sold['owned_contacts']==snew['owned_contacts']
assert sold['owned_rises']==snew['owned_rises']
assert sold['lifetimes']==snew['lifetimes']==74 and sold['peak']==snew['peak']==50
paid_delta={r:snew['paid'][r]-sold['paid'][r]for r in set(sold['paid'])|set(snew['paid'])if snew['paid'][r]!=sold['paid'][r]}
assert paid_delta=={1:1,3:-1,4:-1,6:1}

# Native entry rows from a separately implemented exact prefix adjoint.
def prefix(w,cut,roles):
 ad=[{}for _ in range(m)]
 for j,r in enumerate(roles):ad[r][j]=Q(1)
 for e in reversed(w['program'][:cut]):
  op,r=e[:2]
  if op in('INIT','CLEAR'):ad[r]={}
  elif op=='SCALE':ad[r]={j:v*Q(e[2])for j,v in ad[r].items()}
  elif op in('ADD','COPY'):
   add(ad[e[2]],ad[r],Q(e[3]))
   if op=='COPY':ad[r]={}
 assert not any(ad[n:])
 return {r:{i:ad[i][j]for i in range(n)if j in ad[i]}for j,r in enumerate(roles)}
entry=prefix(base,lo,order)
# Check every new scalar product and stored row on the existing common grid.
unit=1125*2**25;local_rows=[{}for _ in range(m)]
for r,row in entry.items():local_rows[r]=dict(row)
grid_checks=[]
for k,e in enumerate(splice):
 if e[0]=='ADD':
  c=Q(e[3]);term={j:c*v for j,v in local_rows[e[2]].items()}
  assert all((v*unit).denominator==1 for v in term.values())
  elementary(local_rows,e)
  assert all((v*unit).denominator==1 for v in local_rows[e[1]].values())
  grid_checks.append({'index':lo+k,'coefficient':str(c),'product_columns':len(term),'stored_columns':len(local_rows[e[1]])})
# Full literal COPY clean destination, not inferred from endpoint equality.
copy_checks=[]
for i,e in snew['copy']:
 row=prefix(word,i,[e[1]])[e[1]];assert not row
 copy_checks.append({'index':i,'event':e,'initial_input_covector':{}})

# Corruption controls. A nonzero native local covector is composed with the
# literal source prefix, then replayed through the whole fixed suffix.
mutations=[]
for name,offset,coefficient,remove in [('wrong_824_coefficient',5,'1/2',False),('omitted_976_read',1,None,True),('omitted_824_T_update',6,None,True)]:
 sp=[e[:]for e in splice]
 if remove:del sp[offset]
 else:sp[offset][3]=coefficient
 mutant_local=local(sp+[e for i,e in enumerate(p[lo:hi],lo)if i not in skip])
 local_errors={}
 for r in range(m):
  d=dict(mutant_local[r]);add(d,a[r],Q(-1))
  if d:local_errors[r]=d
 assert local_errors
 assert set(j for row in local_errors.values()for j in row)<=set(entry)
 actual={}
 for r,row in local_errors.items():
  z={}
  for j,c in row.items():add(z,entry[j],c)
  if z:actual[r]=z
 assert actual
 # A single source column suffices to reject each specific corruption.
 witness=None
 for column in sorted(set(j for row in actual.values()for j in row)):
  state=[row.get(column,Q(0))if(row:=actual.get(r))else Q(0)for r in range(m)];guard_errors=[]
  for k,e in enumerate(p[hi:],hi):
   op,r=e[:2]
   if op in('INIT','CLEAR'):state[r]=Q(0)
   elif op=='SCALE':state[r]*=Q(e[2])
   elif op in('ADD','COPY'):
    if op=='COPY':
     if state[r]:guard_errors.append((k,state[r]))
     state[r]=Q(0)
    state[r]+=Q(e[3])*state[e[2]]
  errors={r:v for r,v in enumerate(state)if v}
  if errors or guard_errors:
   witness={'initial_input_column':column,'initial_value':'1','final_errors':errors,'copy_guard_errors':guard_errors};break
 assert witness
 mutant={**word,'program':p[:lo]+sp+[e for i,e in enumerate(p[lo:],lo)if i not in skip]}
 structural(mutant)
 mutations.append({'name':name,'event_index':lo+offset,'original_event':splice[offset],'replacement':None if remove else sp[offset],'local_errors':local_errors,'source_witness':witness,'structural_guards_still_pass':True})
wrong={**word,'program':[e[:]for e in q]};wrong['program'][lo+8][2]=3
try:structural(wrong)
except AssertionError as ex:wrong_source={'name':'wrong_move_source','event_index':lo+8,'event':wrong['program'][lo+8],'rejected':True,'reason':str(ex)}
else:raise AssertionError('wrong source accepted')
# A dirty COPY destination can preserve the endpoint map if overwritten, so
# it specifically tests the mandatory interior clean-destination obligation.
ci,ce=snew['copy'][0];source_row=prefix(word,ci,[ce[2]])[ce[2]];assert source_row
col=min(source_row)
injected=['ADD',ce[1],ce[2],'1',ce[-1]]
copy_mutant={**word,'program':q[:ci]+[injected]+q[ci:]}
structural(copy_mutant)
mutant_guard=prefix(copy_mutant,ci+1,[ce[1]])[ce[1]]
assert mutant_guard==source_row and mutant_guard[col]!=0
try:
 assert not mutant_guard, 'COPY destination must be zero on every initial input'
except AssertionError as ex:
 guard_rejection=str(ex)
else:raise AssertionError('dirty COPY destination accepted')
dirty_copy={'name':'nonzero_COPY_destination','insert_before':ci,'inserted_event':injected,'initial_input_column':col,'guard_value':mutant_guard[col],'structural_guards_still_pass':True,'rejected_by_clean_destination':True,'reason':guard_rejection}

# Contacts crossed by the retimed reads are explicitly inventoried.
retimings=[]
for original,event in [(33186,['ADD',212,1455,'1',3]),(33191,['ADD',1455,976,'1',3])]:
 participants=set(event[1:3]);contacts=[]
 for i,e in enumerate(p[lo:original],lo):
  used=e[1:3]if e[0]in('ADD','COPY')else e[1:2]
  if participants.intersection(used):contacts.append((i,e))
 retimings.append({'old_index':original,'new_index':lo if original==33186 else lo+1,'event':event,'crossed_operand_contacts':contacts})

def ser(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return {str(k):ser(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [ser(v)for v in x]
 return x
out={'status':'PASS_INDEPENDENT_EXACT_LOCAL_IDENTITY_CLOCKS_GUARDS_AND_MUTATIONS','source_hash':canon(base),'candidate_hash':canon(word),'original_interval':[lo,hi],'candidate_interval':[lo,new_hi],'all_local_rows':m,'local_row_errors':{},'splice_entry_order':order,'splice_exit_rows':{r:rows[r]for r in order},'encoding_matrix':E,'decoding_matrix':I,'encoding_and_decoding_determinants':1,'retimed_reads':retimings,'paid_delta':paid_delta,'productive_delta':{},'added_operations':{'ADD':3},'lifetimes':74,'owned_peak':50,'all_owned_operand_contacts_identical':True,'new_scalar_common_grid_checks':grid_checks,'common_grid':{'odd':1125,'fractional_bits':25,'scope':'Every newly introduced scalar product and stored row. Full-word maxima are independently recomputed by the resource verifier.'},'copy_checks':copy_checks,'mutations':mutations+[wrong_source,dirty_copy],'phase_scope':'The rational coframe identity is exact over the scalar field and is conjugation-natural. Absolute Gaussian chart recipes, rather than projective Pauli labels, must realise every MOVE. The separate physical verifier checks these finite recipes.'}
(D/'ADVERSARIAL.json').write_text(json.dumps(ser(out),indent=2)+'\n');print(json.dumps(ser({k:v for k,v in out.items()if k not in('new_scalar_common_grid_checks','splice_exit_rows','mutations')}),indent=2));print('mutation outcomes',[(r['name'],r.get('source_witness',{}).get('initial_input_column',r.get('initial_input_column')))for r in out['mutations']])
