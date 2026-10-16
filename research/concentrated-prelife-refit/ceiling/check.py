"""Exact fixed-inventory ceiling for the actual B1149 frame-refit profile.
Apache-2.0; retained PR2679 packing model and PR2733 rational helper credits.
Prepared with substantial OpenAI Codex assistance; no human review claimed.
"""
if not __debug__:raise RuntimeError('Assertions are required; run without -O')
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from math import prod
import json,gzip,importlib.util,time,hashlib,heapq,argparse
HERE=Path(__file__).resolve().parent
rd=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PUBLISHED_ARTIFACTS='4a99b88d4c05de1819314739ff95ec119e05ddbbcdb603557dee3e6aa9346710'
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main(package,parent,out):
 start=time.process_time();assert not out.exists() and not out.resolve().is_relative_to(package.resolve());out.mkdir(parents=True)
 manifest=parent/'ARTIFACTS.json';assert sha(manifest)==PUBLISHED_ARTIFACTS;pins=rd(manifest)
 rels=['independent.py','composition_algebra.py','CLAIM.json','independent-inputs/GLOBAL-TEMPLATE.json.gz']
 for n in rels:assert sha(parent/n)==pins[n],n
 files=[Path(__file__),manifest,*[parent/n for n in rels],package/'expected/PROVIDERS.json',package/'expected/PROFILE.json',*[package/f'expected/words/{tag}.json.gz'for tag in ['base','extra']]];snap={str(p):sha(p)for p in files}
 bounds=module('published_rational_bounds',parent/'independent.py');frames=module('published_frame_interpreter',parent/'composition_algebra.py');pv=rd(package/'expected/PROVIDERS.json');assert pv['gauge44']==pv['extra']
 for tag,pid in [('base','gauge44'),('extra','extra')]:
  word=rd(package/f'expected/words/{tag}.json.gz');report,starts,ends=frames.check_frames(word);live=sorted(set(range(224,704))-set(word['removed']));widthvec=[frames.dm(ends[q])-frames.dm(starts[q])for q in live];assert widthvec==pv[pid]['widths'];assert report['profile']=={int(k):v for k,v in pv[pid]['actual_paid_profile'].items()}
 claim=rd(parent/'CLAIM.json');H={int(k):v for k,v in rd(package/'expected/PROFILE.json').items()};old={int(k):v for k,v in claim['global_profile'].items()};paid={int(k):v for k,v in pv['gauge44']['actual_paid_profile'].items()};oldpaid={int(k):v for k,v in claim['local_profile'].items()};computed=Counter(old)
 for k in set(paid)|set(oldpaid):computed[k]+=666*(paid.get(k,0)-oldpaid.get(k,0))
 assert dict(computed)==H and sum(k*v for k,v in H.items())==4816512
 a=F('0.0017162556782302');candidate=F('0.001716255678230180199082');candidate_upper=candidate+F(1,10**24);cl,cu=bounds.moment(H,candidate);ul,uu=bounds.moment(H,candidate_upper);assert cu<1<ul
 W=[4,5,7,8,9];widths=Counter(pv['gauge44']['widths']);N=[666*widths[w]for w in W];source=rd(parent/'independent-inputs/GLOBAL-TEMPLATE.json.gz');B=Counter()
 for c in source['idle_children']:B[c['rank']]+=2*c['replicas']
 assert dict(B)=={8:49728,16:33152,32:33152,48:33152};assert len(pv['gauge44']['widths'])==415;caps=sorted(B)
 def patterns(cap,i=0):
  if i==len(W):yield ();return
  for k in range(cap//W[i]+1):
   for rest in patterns(cap-k*W[i],i+1):yield(k,)+rest
 P=[(c,p)for c in caps for p in patterns(c)];idle=lambda c,p:c-sum(w*k for w,k in zip(W,p));den=1<<256
 def down(q):return F(q.numerator*den//q.denominator,den)
 phi={0:F(0)}
 for z in range(1,max(caps)+1):phi[z]=down(bounds.cost(z,a)[0]/66304)
 # Exact proposed dual multipliers; feasibility is recomputed for every pattern.
 pi=list(map(F,['-233525924253327/281474976710656000000', '-292109400819631/281474976710656000000', '-6525621680749133/4503599627370496000000', '-1862889328641663/1125899906842624000000', '-8377492948384171/4503599627370496000000']));dot=lambda p:sum(k*q for k,q in zip(p,pi));y={c:min(phi[idle(cc,p)]-dot(p)for cc,p in P if cc==c)for c in caps}
 # A triangular integer lattice basis; validate full rank, every generator, index, and complete quotient.
 Z=[(8,(0,0,0,1,0)),(16,(0,0,0,2,0)),(16,(0,0,1,0,1)),(32,(0,0,0,0,3)),(32,(0,0,0,4,0)),(32,(0,0,1,2,1)),(32,(0,0,2,0,2)),(32,(0,1,0,0,3)),(32,(1,0,0,0,3)),(48,(0,0,0,0,0)),(48,(0,0,0,0,5))]
 vec=lambda c,p:tuple([int(c==cc)for cc in caps]+list(p));rows=[list(vec(c,p))for c,p in Z];basis=[]
 for j in range(9):
  nz=[r for r in rows if r[j]];rows=[r for r in rows if not r[j]]
  while len(nz)>1:
   nz.sort(key=lambda r:abs(r[j]));pivot=nz[0];next_=[pivot]
   for row in nz[1:]:
    q=row[j]//pivot[j];row=[x-q*z for x,z in zip(row,pivot)];(next_ if row[j]else rows).append(row)
   nz=next_
  assert nz;row=nz[0];row=[-x for x in row]if row[j]<0 else row;basis.append(row)
 assert all(not any(r)for r in rows);index=prod(basis[j][j]for j in range(9));assert index==20
 def red(v):
  v=list(v)
  for j,row in enumerate(basis):q=v[j]//row[j];v=[x-q*z for x,z in zip(v,row)]
  return tuple(v)
 zero=(0,)*9;assert all(red(vec(c,p))==zero for c,p in Z);best={}
 for c,p in P:
  rc=phi[idle(c,p)]-dot(p)-y[c];assert rc>=0;g=red(vec(c,p))
  if g!=zero and(g not in best or rc<best[g]):best[g]=rc
 dist={zero:F(0)};queue=[(F(0),zero)]
 while queue:
  d,g=heapq.heappop(queue)
  if d!=dist[g]:continue
  for h,v in best.items():
   z=red([x+y for x,y in zip(g,h)]);cand=d+v
   if z not in dist or cand<dist[z]:dist[z]=cand;heapq.heappush(queue,(cand,z))
 assert len(dist)==index;target=red([B[c]for c in caps]+N);lb=sum(B[c]*y[c]for c in caps)+sum(n*q for n,q in zip(N,pi))+dist[target];paidlb=sum(666*n*bounds.cost(r,a)[0]/66304 for r,n in paid.items());total=down(lb+paidlb);assert total>1
 baseline=F(claim['kappa']);gap=a-candidate;ratio=(candidate-baseline)/(a-baseline);assert 0<ratio<1
 assert all(sha(Path(p))==h for p,h in snap.items())
 result={'status':'PASS_EXACT_RATIONAL_REFIT_INVENTORY_CEILING','source2733':'2761b52b17590b8cf94f2e410004a8252d5592dc','published_artifacts_sha256':PUBLISHED_ARTIFACTS,'source_bindings':snap,'endpoint_upper':str(a),'moment_lower':str(total),'moment_margin':str(total-1),'moment_margin_float':float(total-1),'candidate_native_bracket':[str(candidate),str(candidate_upper)],'candidate_lower_moment_upper':str(cu),'candidate_upper_moment_lower':str(ul),'baseline_PR2733_headline':str(baseline),'remaining_endpoint_gap_upper':str(gap),'fraction_baseline_to_ceiling_gain_realized_lower':str(ratio),'bins':dict(B),'per_call_width_counts':dict(widths),'paid_per_call':paid,'global_profile':H,'calls':666,'patterns':len(P),'lattice_index':index,'quotient_states':len(dist),'integrality_correction':str(dist[target]),'pi_exact':[str(q)for q in pi],'y_exact':{str(c):str(v)for c,v in y.items()},'CPU_seconds':time.process_time()-start,'scope':'Fixed actual415-helper width inventory, actual refit paid profile,666calls and fixed source bin multiset; all windows/families relaxed. Native complex root ceiling; conservative cost is no lower. Not a global optimum or a bound on changed words,inventory,bins or call counts. Candidate moment bracket is not native/global/outer admission.'}
 (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['status','patterns','lattice_index','moment_margin_float','CPU_seconds']}))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);ap.add_argument('--package',type=Path,default=HERE.parent);ap.add_argument('--parent',type=Path,default=HERE.parent.parent/'concentrated-prelife-composition');a=ap.parse_args();main(a.package.resolve(),a.parent.resolve(),a.work.resolve())
