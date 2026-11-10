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
RAW=Q('.00376670');GAP=Q(1,10**10);ADMITTED=Q('.00376669')
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
 native=(H.parent/'two-fragment/CONTROLLER.json').read_bytes()
 need(hashlib.sha256(native).hexdigest()=='543b8728e659561b95e127dad7bd7534645996d7d2c61602bb5d89c89a73944c','Frozen integral source caller')
 c=json.loads(native);events=[]
 for e in c['events']:
  op=e[0]
  if op=='LAMBDA':continue
  if op in('SCALE','ADD'):
   value=Q(e[-1]);need(value.denominator==1,'Integral coefficients before reduction')
   if op=='SCALE':need(abs(value)==1,'Integral unimodular scaling');continue
   if int(value)%2:events.append(e[:-1])
  elif op=='QUERY':need(e[-1]in(-1,1),'Central involution query');events.append(e[:-1])
  elif op in('SWAP','LOCAL','IDLE','IDLE_ONE'):events.append(e)
  else:raise ValueError('Integral transfer opcode')
 return{'schema':'binary-two-paid-fragments/1','roles':c['roles'],'stages':c['stages'],'events':events,'diagonal':[{'q':d[0]%2,'stages':[s for s,x in enumerate(d[1:])if x]}for d in c['diagonal']]}

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
 old=json.loads((H/'RETIRED-BIT-ADMISSION.json').read_text())
 need(Q(old['ordinary_admitted'])==Q('.00374998'),'Previous qualified BIT ordinary result')
 expectedT=Counter({r:18*n for r,n in t0.items()});expectedP=Counter({r:18*n for r,n in p0.items()})
 for size,count in {2:8,4:4}.items():expectedT[7*size+1]+=222*count;expectedP[7*size]+=222*count
 expectedT.update({127:111,64:222,36:222,8:222,28:222,1:111})
 expectedP.update({1:1665,35:222,28:222,7:222})
 need(T==expectedT and P==expectedP,'Independent actual-source tree and root formula invoice')
 need((w['roles'],w['stages'],len(w['events']))==(34,18,356),'Complete reduced caller census')
 need((sum(T.values()),sum(P.values()))==(11640,56673),'Every productive input and paid request counted')
 need(sum(r*v for r,v in T.items())-sum(r*v for r,v in P.items())==753,'No invented rank mass')
 negative={}
 for label,at in [('missing_input_basis',0),('missing_first_handoff',next(i for i,e in enumerate(w['events'])if e==['SWAP',2,6])),('missing_second_handoff',next(i for i,e in enumerate(w['events'])if e==['SWAP',2,4])),('missing_output_basis',len(w['events'])-1)]:
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
  label='binary_two_paid_fragments',source_status='Literal356-event integral-reduction caller; all1156 forward and reverse coefficients; actual659-input source and rational native frames independently audited; unchanged inherited all-width native theorem')
 @lru_cache(None)
 def power(r,t):
  lo,hi=I.power(r,t);s=10**65
  return Q((lo*s).__floor__(),s),Q(-((-hi*s).__floor__()),s)
 def moment(hist,t):
  lo=hi=Q(0)
  for r,n in hist.items():x,y=power(r,t);lo+=n*x;hi+=n*y
  return lo,hi
 def margin(k,targets=T,paid=P):
  tt,pp=moment(targets,1-k),moment(paid,1-k)
  return tt[0]-pp[1],tt[1]-pp[0]
 low,high=Q('.0037667234775'),Q('.0037667234776')
 need(margin(low)[0]>0 and margin(high)[1]<0,'Independent rational crossing bracket')
 need(margin(RAW)[0]>0,'New tested saving has strict paid margin')
 need(margin(RAW,{int(k):v for k,v in old['targets'].items()},{int(k):v for k,v in old['paid'].items()})[1]<0,'Old complete caller cannot fund new claim')
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
 # The covered saving now exceeds the old atom. Retune it to .004,
 # checking the full retained wrapper envelope and stock conditions below.
 previous=Q('.00374998');covered=RAW-2*GAP;atom=Q('.004');stages=[]
 for admitted in (Q('.00376663'),ADMITTED):
  envelope=(1-atom)*covered+atom*previous
  need(atom>envelope>admitted>previous and atom<1-envelope,'Retained full ordinary-wrapper envelope')
  stages.append(dict(previous=previous,covered=covered,atom=atom,envelope=envelope,admitted=admitted,strict_debit=envelope-admitted));previous=admitted
 blob=gzip.compress(json.dumps(w,separators=(',',':')).encode(),mtime=0);(H/'FRAGMENT-CALLER.json.gz').write_bytes(blob)
 out=dict(status='PASS_TWO_FRAGMENTS_BIT_ORDINARY_00376669',ordinary_admitted=ADMITTED,previous_ordinary=Q('.00374998'),ordinary_gain=ADMITTED-Q('.00374998'),raw_tested=RAW,raw_crossing=[low,high],covered_saving=covered,
  caller_sha256=hashlib.sha256(blob).hexdigest(),native_source_sha256=SOURCE_SHA,forward_coefficients=forward_count,reverse_coefficients=reverse_count,source=source,
  paid=dict(sorted(P.items())),targets=dict(sorted(T.items())),invoice_comparison='Full new invoice independently counted; predecessor cannot fund new claim; integral source and BIT native source both hash-bound',paid_jobs=sum(P.values()),productive_fields=sum(T.values()),rank_surplus=753,
  independent_moment_intervals={str(k):I.bounds_text(margin(k),28)for k in (RAW,low,high)},finite_admission=cert,independent_finite_ratios=[I.bounds_text(r,28)for r in ratios],independent_normalized_upper=I.bounds_text((norm,norm),28),
  event_counts=dict(ops),ordinary_basis_records=basis,ordinary_visible_records=visible,whole_job_route_count=route_count,whole_job_route_records=routes,ordinary_record_allowance=10**12,owned_bank_bound=owned,
  compiler_constants={'U_raw':f'sum(i=0..767,{sum(T.values())}^(767-i)*{sum(P.values())}^i)','D':f'{sum(T.values())}^768-W','O':f'{owned}*U_raw+D','G':f'1000000000000*U_raw+8*R+2*{sum(T.values())}^768','E':'64*(Z+N+P+G+1)^3','B_constant':'P+E','C0':'32*N*B_constant^2'},
  ordinary_bootstrap=stages,negative_controls=negative,
  assumptions=['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery'],
  scope='Changed, completely priced BIT dependency under the inherited framework. Overall complex-limited kappa remains unchanged. No materialized uniform word or unconditional integer multiplication theorem.',new_global_kappa_claim=False,seconds=time.monotonic()-started)
 (H/'FRAGMENT-BIT-ADMISSION.json').write_text(json.dumps(encode(out),indent=2)+'\n')
 print(json.dumps(encode({k:out[k]for k in ('status','ordinary_admitted','ordinary_gain','raw_crossing','caller_sha256','productive_fields','paid_jobs','ordinary_visible_records','whole_job_route_records','owned_bank_bound','seconds')}),indent=2))

if __name__=='__main__':main()
