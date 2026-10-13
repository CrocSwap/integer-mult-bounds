"""Price every nested-donor nominee with exact whole-family pattern counts and two moments."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import sys,json,math,types,hashlib
r=Path.cwd();out=r/'r715-nested-donor-pricing';assert not out.exists();out.mkdir()
sys.path[:0]=[str(r/'source454-review/e8-r740-replica32/code'),str(r/'complex447-search'),str(r/'source450-review/code'),str(r/'source443-review/code/engines')]
import e8core as E,hosting_core as HC,moment as M,base_two_moment as M2
HK=types.ModuleType('tight');HK.__file__=str(r/'source450-review/code/hosting_k.py');exec(Path(HK.__file__).read_text().replace('options=dict(time_limit=time_limit, disp=False)','options=dict(time_limit=time_limit,mip_rel_gap=1e-11,disp=False)'),HK.__dict__)
ref=json.loads((r/'r715-factor-replica84-strong-RESULT.json').read_text());c=float(Q(ref['bit_lower']));HK.cost=lambda k,m:k*math.expm1(c*math.log(m/k))/c if k else 0
ns={};text=(r/'screen_whole454_complex.py').read_text();exec(('def schedule(K):'+text.split('def schedule(K):',1)[1].split('\nfor L,T in',1)[0]).replace('rank=8*','rank=7*'),ns)
K=5;T=json.loads((r/'pr472-delivery-publication/research/r715-factor-replica84/CONFIG.json').read_text())['replicas'];m=78;stages=11;copies=240*T;W=copies*K;sc=ns['schedule'](K);win={i:x for i,x in HC.windows(sc).items() if x[1] and x[2]};L=None;cache={};records=[]
for trial in range(20):
 source=r/'r715-nested-donor-reselection'/('trial-'+str(trial));dest=out/('trial-'+str(trial));dest.mkdir();word=json.loads((source/'WORD.json').read_text());record=json.loads((source/'RESULT.json').read_text());assert hashlib.sha256((source/'WORD.json').read_bytes()).hexdigest()==record['word_sha256']
 if L is None:L=E.Lat(word['lines'])
 assert [tuple(x) for x in word['lines']]==L.lines
 masks=E.to_masks(word,L);dims=[L.dim(x) for x in masks];audit=E.replay(word,L=L,masks=masks,span_mode='z');assert not audit['viol'];assert dict(audit['H'])=={int(k):n for k,n in record['profile'].items()}
 widths=[8-dims[f] for f in word['start'][240:]];counts=Counter(widths);key=tuple(sorted(counts.items()));avail={(s,w):n*T for s in range(stages) for w,n in counts.items()}
 try:
  if key not in cache:
   y,z,_=HK.solve(win,copies,avail,m,host_all=True,maxk=max(x[1] for x in win.values())//min(widths),time_limit=120)
   for i in win:
    assert sum(n for (ii,pat),n in y.items() if ii==i)==copies
    for w in counts:assert sum(n*pat.count(w) for (ii,pat),n in y.items() if ii==i)==sum(n for (ii,ww,s),n in z.items() if ii==i and ww==w)
   for (s,w),n in avail.items():assert sum(k for (i,ww,ss),k in z.items() if ss==s and ww==w)==n
   assert all(isinstance(n,int) and n>=0 for n in list(y.values())+list(z.values()))
   idle=Counter()
   for (i,pat),n in y.items():
    rank=win[i][1]-sum(pat);assert rank>=0
    if rank:idle[rank]+=n
   for e in sc:
    if e['kind']=='idle' and e['idx'] not in win and e['rank']:idle[e['rank']]+=copies
   cache[key]=y,z,idle
  y,z,idle=cache[key];P=Counter({k:n*stages*T for k,n in audit['H'].items()});P.update(idle);assert m*W-sum(k*n for k,n in P.items())==408*T
  cert=M.certify(P,m,W,True);lo,hi=Q(cert['lower']),Q(cert['upper'])
  for x,below in [(lo,True),(hi,False)]:
   a,b=M2.moment(m,W,list(P.items()),x);d,e=M2.moment(m,W,[(1,32*m*m*sum(P.values()))],x);assert b+e/10**16<1 if below else a+d/10**16>1
  result=dict(trial=trial,status='PASS_EXACT_LOCAL_PATTERN_COUNTS_AND_TWO_MOMENTS_GLOBAL_PENDING',word_sha256=record['word_sha256'],replicas=T,bit_lower=str(lo),profile=dict(sorted(P.items())),projected_kappa=float(lo/(1+lo)),beats_current=lo>Q(ref['bit_lower']),multi_entrance_donors=record['multi_entrance_donors'])
  HC.save_selection(dest/'SELECTION.json','bit',y,z,0)
 except Exception as ex:result=dict(trial=trial,status='FAILED_PRICING',error=repr(ex))
 records.append(result);(dest/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(out/'LEDGER.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(result),flush=True)
(out/'COMPLETE.json').write_text(json.dumps(dict(status='FINISHED',trials=len(records),inventories=len(cache),gains=[x['trial'] for x in records if x.get('beats_current')],failures=[x['trial'] for x in records if x['status']=='FAILED_PRICING']),indent=2)+'\n')
