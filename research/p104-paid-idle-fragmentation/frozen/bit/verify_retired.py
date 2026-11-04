"""Construct and qualify the new independent characteristic-two retirement.

All-width native/compiler/precision/tape/recovery scope remains inherited.
This is a BIT-dependency gain, not a new global complex-limited kappa.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from functools import lru_cache
import gzip,hashlib,importlib.util,json,time

H=Path(__file__).resolve().parent
RAW=Q('.00374999');GAP=Q(1,10**10);ADMITTED=Q('.00374998')
SOURCE_SHA='51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78'
CALLER_SHA='86c4574d47e406e560b3ae2602e52501d4da4bc4c082b4f31b21f6cfef362cc3'

def need(x,s):
 if not x:raise ValueError(s)
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def encode(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return {str(k):encode(v)for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [encode(v)for v in x]
 return x

def construct():
 blob=(H/'retained/bit_mixed_caller/BINARY-MIXED-CALLER.json.gz').read_bytes()
 need(hashlib.sha256(blob).hexdigest()==CALLER_SHA,'Exact source caller')
 w=json.loads(gzip.decompress(blob));old=w['events'];cut=209;role=5;new=w['roles']
 need(new==34 and old[cut]==['QUERY',20,21],'Exact source cut')
 def remap(e):
  e=e[:]
  for j in {'ADD':[1,2],'SWAP':[1,2],'QUERY':[1,2],'LOCAL':[2,3],'IDLE':[1,2],'IDLE_ONE':[1]}[e[0]]:
   if e[j]==role:e[j]=new
  return e
 E=[['ADD',5,20],['ADD',21,5]]
 A=[['SWAP',5,21],['ADD',5,1],['ADD',5,2],['ADD',5,20]]
 w['events']=E+old[:cut+1]+A+[remap(e)for e in list(reversed(A))+old[cut+1:]+list(reversed(E))]
 w['roles']+=1;w['diagonal'][5]={'q':1,'stages':[]};w['diagonal'].append({'q':0,'stages':[10,11]})
 w['retirement']={'source_cut':cut,'pivot':5,'input_direction':[5,21],'output_direction':[5,20],
  'resident_prefix':[21],'resident_suffix':[1,2,20,21],'input_basis':E,'cut_basis':A,
  'old_target_rank':15,'new_target_ranks':[1,14],'new_input':new,'independent_arbitrary_input':True}
 w['schema']='binary-mixed-projector-caller-retirement/1'
 w['scope']='R091 BIT caller with one exact independent GF2 retirement; all original source and recursive paid jobs retained.'
 return w

def forward(w):
 n=w['roles'];width=w['stages']+1;zero=(0,)*width
 rows=[[{zero}if i==j else set()for j in range(n)]for i in range(n)]
 def shift(row,ss=(),q=0):
  out=[]
  for cell in row:
   cc=set()
   for key in cell:
    k=list(key);k[0]^=q
    for s in ss:k[s]+=1
    z=tuple(k)
    if z in cc:cc.remove(z)
    else:cc.add(z)
   out.append(cc)
  return out
 seen=[]
 for e in w['events']:
  op=e[0]
  if op=='ADD':_,a,b=e;rows[a]=[x^y for x,y in zip(rows[a],rows[b])]
  elif op=='SWAP':_,a,b=e;rows[a],rows[b]=rows[b],rows[a]
  elif op in ('LOCAL','QUERY'):
   if op=='LOCAL':_,s,src,dst=e;seen.append(s)
   else:_,dst,src=e
   rows[dst]=[x^y for x,y in zip(rows[dst],shift(rows[src],q=1))]
   if op=='LOCAL':rows[src]=shift(rows[src],[s]);rows[dst]=shift(rows[dst],[s])
  elif op=='IDLE':_,a,b,ss=e;rows[a]=shift(rows[a],ss);rows[b]=shift(rows[b],ss)
  elif op=='IDLE_ONE':_,a,ss=e;rows[a]=shift(rows[a],ss)
  else:raise ValueError(op)
 need(sorted(seen)==list(range(1,width)),'All native stages once')
 for i,d in enumerate(w['diagonal']):
  key=(d['q'],)+tuple(int(s in d['stages'])for s in range(1,width))
  for j in range(n):need(rows[i][j]==({key}if i==j else set()),f'Forward coefficient {i},{j}')
 return n*n

def main():
 started=time.monotonic();w=construct();forward_count=forward(w)
 sourceblob=(H/'retained/root/inputs/BIT-NATIVE-WORD.json.gz').read_bytes()
 need(hashlib.sha256(sourceblob).hexdigest()==SOURCE_SHA,'Exact native source')
 audit=load(H/'retained/root/audit_binary_mixed.py','retired_independent_audit')
 reverse_count=audit.backward(w);p0,t0,source=audit.source_audit(json.loads(gzip.decompress(sourceblob)))
 P=Counter({r:18*c for r,c in p0.items()});T=Counter({r:18*c for r,c in t0.items()})
 for e in w['events']:
  if e[0]=='QUERY':P[1]+=111
  elif e[0]=='IDLE':P[7*len(e[3])]+=222
  elif e[0]=='IDLE_ONE':P[7*len(e[2])]+=111
 for d in w['diagonal']:T[d['q']+7*len(d['stages'])]+=111
 old=json.loads((H/'retained/bit_mixed_caller/BINARY-MIXED-CALLER-RESULT.json').read_text())['invoice']
 need(dict(P)=={int(k):v for k,v in old['paid_profile'].items()},'Every paid job unchanged')
 delta=Counter(T);delta.subtract({int(k):v for k,v in old['productive_profile'].items()})
 need({r:v for r,v in delta.items()if v}=={1:111,14:111,15:-111},'Exact independent target delta')
 need(sum(T.values())==11751 and sum(P.values())==56895,'Complete productive and paid counts')
 need(sum(r*v for r,v in T.items())-sum(r*v for r,v in P.items())==753,'No invented rank mass')
 negative={}
 for label,at in [('missing_input_basis',0),('missing_cut_basis',2+210),('missing_suffix_basis',2+210+4),('missing_output_basis',len(w['events'])-1)]:
  bad=json.loads(json.dumps(w));del bad['events'][at]
  try:audit.backward(bad)
  except ValueError as e:negative[label]=str(e)
  else:raise ValueError('Retirement corruption accepted: '+label)
 for op in ('LOCAL','QUERY','IDLE','IDLE_ONE'):
  bad=json.loads(json.dumps(w));del bad['events'][next(i for i,e in enumerate(bad['events'])if e[0]==op)]
  try:audit.backward(bad)
  except ValueError as e:negative['missing_'+op]=str(e)
  else:raise ValueError('Unpaid job accepted: '+op)
 C=load(H/'retained/root/inputs/credited_trim.py','retired_finite_compiler')
 I=load(H/'retained/root/inputs/independent_interval.py','retired_independent_interval')
 cert=C.certificate(T,P,RAW,768,15,16,Q(1,5),Q(1,5),uniform_gap=GAP,
  label='binary_mixed_independent_retirement',source_status='Literal366-event caller; all1225 forward and reverse coefficients; actual659-input source and rational native frames independently audited; unchanged inherited all-width native theorem')
 @lru_cache(None)
 def power(r,t):
  lo,hi=I.power(r,t);s=10**65
  return Q((lo*s).__floor__(),s),Q(-((-hi*s).__floor__()),s)
 def moment(hist,t):
  lo=hi=Q(0)
  for r,n in hist.items():x,y=power(r,t);lo+=n*x;hi+=n*y
  return lo,hi
 def margin(k,targets=T):
  tt,pp=moment(targets,1-k),moment(P,1-k)
  return tt[0]-pp[1],tt[1]-pp[0]
 low,high=Q('.0037522104751'),Q('.0037522104752')
 need(margin(low)[0]>0 and margin(high)[1]<0,'Independent rational crossing bracket')
 need(margin(RAW)[0]>0,'New tested saving has strict paid margin')
 need(margin(RAW,{int(k):v for k,v in old['productive_profile'].items()})[1]<0,'Old complete caller cannot fund new claim')
 t=1-RAW;tt=moment(T,t);u=Q(1,5)
 ratios=(I.div(moment(P,t),tt),I.div(moment(P,t+u),I.mul(power(15,u),tt)),I.div(I.mul(power(16,u),moment(T,t-u)),tt))
 limits=list(map(Q,cert['rational_upper_limits']))
 for r,bound in zip(ratios,limits):need(0<r[0]<=r[1]<=bound<1,'Second engine finite tail bound')
 aa,gg,ll=limits;norm=1/(1+768*(1-aa))+2*gg**768+ll**768
 need(norm<1,'Discarded targets and all paid splits funded')
 compiler=cert['uniform_compiler'];threshold=compiler['H'];p=compiler['logarithm_power'];e=compiler['integer_test_exponent']
 need(threshold==GAP.denominator*e and(threshold+1)**p<2**e,'Independent uniform integer threshold')
 need(not(GAP.denominator*(e-1)+1)**p<2**(e-1),'Preceding compiler grid rejects')
 ops=Counter(x[0]for x in w['events']);n=111;m=w['roles'];F=18;thin=ops['QUERY'];idles=ops['IDLE']+ops['IDLE_ONE'];h=127
 basis=n*8*(ops['ADD']+3*ops['SWAP']);visible=F*10**7+basis+256*n*(F+thin+m)
 route_per=8*(10*h*h+10*h);route_count=4*(sum(P.values())+sum(T.values()))+8*n*F+8*n*idles;routes=route_per*route_count
 owned=F*source['owned_labels']+2*n*m*len(w['events'])+16*n*(F+thin+m)
 need(visible+routes<10**12 and owned<10**7,'Actual changed ordinary work and storage funded')
 # Keep the admitted atom parameter .00375. No retuned atom is needed.
 previous=Q('.00374457');covered=RAW-2*GAP;atom=Q('.00375');stages=[]
 for admitted in (Q('.00374996'),ADMITTED):
  envelope=(1-atom)*covered+atom*previous
  need(atom>envelope>admitted>previous and atom<1-envelope,'Retained full ordinary-wrapper envelope')
  stages.append(dict(previous=previous,covered=covered,atom=atom,envelope=envelope,admitted=admitted,strict_debit=envelope-admitted));previous=admitted
 blob=gzip.compress(json.dumps(w,separators=(',',':')).encode(),mtime=0);(H/'RETIRED-CALLER.json.gz').write_bytes(blob)
 out=dict(status='PASS_RETIRED_BIT_ORDINARY_00374998',ordinary_admitted=ADMITTED,previous_ordinary=Q('.00374457'),ordinary_gain=ADMITTED-Q('.00374457'),raw_tested=RAW,raw_crossing=[low,high],covered_saving=covered,
  caller_sha256=hashlib.sha256(blob).hexdigest(),native_source_sha256=SOURCE_SHA,forward_coefficients=forward_count,reverse_coefficients=reverse_count,source=source,
  paid=dict(sorted(P.items())),targets=dict(sorted(T.items())),target_delta={1:111,14:111,15:-111},paid_delta={},paid_jobs=sum(P.values()),productive_fields=sum(T.values()),rank_surplus=753,
  independent_moment_intervals={str(k):I.bounds_text(margin(k),28)for k in (RAW,low,high)},finite_admission=cert,independent_finite_ratios=[I.bounds_text(r,28)for r in ratios],independent_normalized_upper=I.bounds_text((norm,norm),28),
  event_counts=dict(ops),ordinary_basis_records=basis,ordinary_visible_records=visible,whole_job_route_count=route_count,whole_job_route_records=routes,ordinary_record_allowance=10**12,owned_bank_bound=owned,
  compiler_constants={'U_raw':f'sum(i=0..767,{sum(T.values())}^(767-i)*{sum(P.values())}^i)','D':f'{sum(T.values())}^768-W','O':f'{owned}*U_raw+D','G':f'1000000000000*U_raw+8*R+2*{sum(T.values())}^768','E':'64*(Z+N+P+G+1)^3','B_constant':'P+E','C0':'32*N*B_constant^2'},
  ordinary_bootstrap=stages,negative_controls=negative,
  assumptions=['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery'],
  scope='Changed, completely priced BIT dependency under the inherited framework. Overall complex-limited kappa remains unchanged. No materialized uniform word or unconditional integer multiplication theorem.',new_global_kappa_claim=False,seconds=time.monotonic()-started)
 (H/'RETIRED-BIT-ADMISSION.json').write_text(json.dumps(encode(out),indent=2)+'\n')
 print(json.dumps(encode({k:out[k]for k in ('status','ordinary_admitted','ordinary_gain','raw_crossing','caller_sha256','productive_fields','paid_jobs','ordinary_visible_records','whole_job_route_records','owned_bank_bound','seconds')}),indent=2))

if __name__=='__main__':main()
