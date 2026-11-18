#!/usr/bin/env python3
import argparse, collections, datetime, gzip, hashlib, json, os, resource, signal, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from exact import Interpreter, diff
BASE=CAND=BI=CI=None
INVOICE_PINS=['7d54c1ec036d4c096526dd95e06892ca99210812d51a503b22f6d78243330ca9','fa0c37a9e67d0a82850c4fcfd5cbdb3bd88e1f8db329176e5669da6c7788f6a2']
PINS=['6c52b2fba7c20343a50cb92ed4b997aa9921c78f212ac6428d13fff2bcd014cf','450c7e544efb5258c4b8b4858b49cbd7482d14f206cdda1a71833fc73343ac66']
def sha(b): return hashlib.sha256(b).hexdigest()
def load(p,pin):
 b=gzip.decompress(p.read_bytes()); assert sha(b)==pin; return json.loads(b)
def roles(e): return e[1:3] if e[0] in ('ADD','COPY') else e[1:2]
def watched(e,n): return any(r>=n for r in roles(e)) or e[0]=='COPY'
def observe(a,e): return a.snapshot(sorted(set(roles(e))))
def run(w):
 a=Interpreter(w); observations=[]; erasures=[]
 for i,e in enumerate(w['program']):
  watch=watched(e,a.n)
  if watch: before=observe(a,e)
  if e[0]=='CLEAR': erasures.append((e[1],e[2],a.rows[e[1]].copy()))
  a.step(i)
  if watch: observations.append((e,before,observe(a,e)))
 a.end();return a,observations,erasures
def compare(base,cand):
 a,ao,ae=run(base); b,bo,be=run(cand)
 assert len(ao)==len(bo)==630, ('observation count',len(ao),len(bo))
 assert len(ae)==len(be)==74, ('erasure count',len(ae),len(be))
 for i,(x,y) in enumerate(zip(ao,bo)):
  if x!=y: raise ValueError('protected observation mismatch index %d event %s / %s'%(i,x[0],y[0]))
 for i,(x,y) in enumerate(zip(ae,be)):
  if x!=y: raise ValueError('erasure mismatch index %d role/chart %s / %s'%(i,x[:2],y[:2]))
 for r in range(a.n):
  if a.rows[r]!=b.rows[r]:raise ValueError('public row %d: %s'%(r,diff(a.rows[r],b.rows[r])))
 assert a.peak==b.peak
 return {'protected_events':len(ao),'compared_before_after':2*len(ao),'ordered_erasures':len(ae),'all_arbitrary_public_input_columns':a.n,'public_outputs':a.n,'source_peak':a.peak,'candidate_peak':b.peak,'copy_count':sum(e[0]=='COPY' for e,_,_ in ao)}
def census(w):
 n=w['public'];dim=list(map(len,w['frames']));main=set(w['live']);main|={r+112 for r in w['live']};main|=set(w['hosted']['X2'])|set(w['hosted']['Y2'])
 return collections.Counter(abs(dim[e[3]]-dim[e[2]]) for e in w['program'] if e[0]=='MOVE'),collections.Counter(dim[w['final'][r]]-dim[w['initial'][r]] for r in range(n) if r not in main)
def fmt(c):return {str(k):v for k,v in sorted(c.items()) if v}
def delta(a,b):
 c=collections.Counter(b);c.subtract(a);return fmt(c)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 global BASE,CAND,BI,CI
 if not __debug__: raise SystemExit('optimized Python is unsupported')
 parser=argparse.ArgumentParser(description='Independent exact comparator on explicit frozen inputs')
 for name in ('base','candidate','base-invoice','candidate-invoice','output'): parser.add_argument('--'+name,required=True,type=Path)
 args=parser.parse_args();BASE,CAND,BI,CI=args.base,args.candidate,args.base_invoice,args.candidate_invoice
 if args.output.exists(): raise SystemExit('output already exists; use a new path')
 os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,)*2);resource.setrlimit(resource.RLIMIT_CPU,(570,570));signal.alarm(600)
 started=now();t=time.monotonic(); result={'started_utc':started,'base_word':PINS[0],'candidate_word':PINS[1]}
 try:
  base=load(BASE,PINS[0]);cand=load(CAND,PINS[1]);assert sha(BI.read_bytes())==INVOICE_PINS[0] and sha(CI.read_bytes())==INVOICE_PINS[1], 'invoice pins';assert {k:v for k,v in base.items() if k!='program'}=={k:v for k,v in cand.items() if k!='program'}
  result.update(compare(base,cand))
  # Identify a candidate-specific public ADD from literal sequence diff, not constructor annotations.
  aa=[tuple(e) for e in base['program']];bb=[tuple(e) for e in cand['program']]; extra=collections.Counter(bb)-collections.Counter(aa)
  inserted=[j for j,e in enumerate(bb) if extra[e]>0 and e[0]=='ADD' and all(r<cand['public'] for r in roles(e))]
  assert inserted, 'no changed public ADD for actual mutation'
  mutant=dict(cand);mutant['program']=list(cand['program']);j=inserted[0]; event=list(mutant['program'][j]);old=event[3];event[3]=str(-__import__('fractions').Fraction(old));mutant['program'][j]=event
  try: compare(base,mutant)
  except Exception as e: result['actual_sign_mutation']={'clock':j,'original':bb[j],'mutated':event,'rejected':True,'error':str(e)}
  else:raise AssertionError('actual sign mutation accepted')
  bp,bt=census(base);cp,ct=census(cand);bi=json.loads(BI.read_text());ci=json.loads(CI.read_text());oldp=collections.Counter({int(k):v for k,v in bi['paid'].items()});oldt=collections.Counter({int(k):v for k,v in bi['targets'].items()});residp=oldp.copy();residp.subtract({k:17*v for k,v in bp.items()});residt=oldt.copy();residt.subtract({k:17*v for k,v in bt.items()}); assert all(v>=0 for v in residp.values()) and all(v>=0 for v in residt.values());newp=collections.Counter({k:17*v for k,v in cp.items()});newp.update(residp);newt=collections.Counter({k:17*v for k,v in ct.items()});newt.update(residt);assert fmt(newp)==ci['paid'] and fmt(newt)==ci['targets']
  result.update(native_paid_delta=delta(bp,cp),native_target_delta=delta(bt,ct),signed17_paid_delta=delta(oldp,newp),signed17_target_delta=delta(oldt,newt),invoice_candidate_match=True,status='PASS_INDEPENDENT_EXACT')
 except BaseException as e:
  result.update(status='FAILED_OR_INTERRUPTED',error_type=type(e).__name__,error=str(e))
 finally:
  result.update(ended_utc=now(),elapsed_seconds=time.monotonic()-t,base_compressed_sha256=sha(BASE.read_bytes()),candidate_compressed_sha256=sha(CAND.read_bytes()),post_base_raw_sha256=sha(gzip.decompress(BASE.read_bytes())),post_candidate_raw_sha256=sha(gzip.decompress(CAND.read_bytes())),scope='Exact Q rows for all public input columns; ideal-zero owned INIT, inherited supplier reset; chart and liveness checks; unchanged protected event ordered identity. No native/signed physical application, provider admission, independent price engine, covariance, precision, or goal admission.')
  with args.output.open('x') as out: json.dump(result,out,indent=2,sort_keys=True);out.write('\n')
 print(json.dumps(result,sort_keys=True));return 0 if result['status']=='PASS_INDEPENDENT_EXACT' else 1
if __name__=='__main__':sys.exit(main())
