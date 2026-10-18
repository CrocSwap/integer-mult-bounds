"""Semantic D contract for the inherited interleaved scalar interface."""
import argparse,copy,gzip,hashlib,importlib.util,json,sys
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(HERE))
import independent
BASE='c0e3631dc24e3c24a861f7d3d79e0608481cccec'
PATHS=('research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz',
 'research/r439-bsection-stars-seed01/candidate.json.gz',
 'research/e8-bit-p111-tuned/code/xcheck_p.py',
 'research/e8-bit-carrier-skeleton/README.md')

def need(b,s):
 if not b:raise ValueError(s)
def pairs(x):
 d={}
 for k,v in x:need(k not in d,'duplicate JSON key');d[k]=v
 return d
def read(b):return json.loads(b,object_pairs_hook=pairs,parse_constant=lambda s:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(x):return sha(enc(x).encode())
def source():
 p=read((HERE/'SOURCES.json').read_bytes());need(set(p)=={'base','files'} and p['base']==BASE and set(p['files'])==set(PATHS),'exact source inventory')
 for f in PATHS:need(sha((ROOT/f).read_bytes())==p['files'][f],'source pin '+f)
 words=[read(gzip.decompress((ROOT/f).read_bytes())) for f in PATHS[:2]]
 need((words[0]['v'],words[0]['R'])==(111,439),'selected bit shape')
 spec=importlib.util.spec_from_file_location('pinned_checker',ROOT/PATHS[2]);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 return words,mod

def drows(gates,n):
 rows=[1<<j for j in range(n)]
 for _,d,ss in gates:
  for s in ss:rows[d]^=rows[s]
 return rows

def semantic(w):
 v,R=w['v'],w['R'];n=2*v+R
 zero=next(i for i,f in enumerate(w['frames']) if not f)
 need(all(w['start'][r]==zero for r in range(v,n)),'D entry frame')
 for f,d,ss in w['D']:
  need(f==zero,'D must use zero frame')
  need(v<=d<n and ss and all(v<=s<n for s in ss) and len(set([d]+ss))==len(ss)+1,'D operands must be distinct Y/H registers')
  need(not(d>=2*v and any(s<2*v for s in ss)),'retained H1 target feedback')
 rows=drows(w['D'],n);N=[];hmask=((1<<R)-1)<<(2*v)
 for r in range(n):
  delta=rows[r]^(1<<r)
  if v<=r<2*v:
   need(delta&~hmask==0,'D target boundary is not helper-only shear');N.append(delta>>(2*v))
  else:need(delta==0,'D helper/source not restored')
 return N

def check_k(actual,expected):
 need(actual==expected,'semantic K mismatch')

def stream(w):
 out=[('add',d,s) for sec in ('D','A') for _,d,ss in w[sec] for s in ss]
 tmp=2*w['v']+w['R']
 for j,h in enumerate(w['ret']):
  out.append(('copy',tmp,h))
  out.extend(('add',w['v']+t,tmp) for t,ss in enumerate(w['scatter']) if j in ss)
  out.append(('erase',tmp,h))
 out.extend(('add',d,s) for sec in ('B','C') for _,d,ss in w[sec] for s in ss)
 return out

def literal(w,reverse=False):
 n=2*w['v']+w['R'];rows=[1<<i for i in range(n)]+[0];ops=stream(w)
 for k,d,s in (reversed(ops) if reverse else ops):
  if reverse:k={'copy':'erase','erase':'copy'}.get(k,k)
  if k=='add':rows[d]^=rows[s]
  elif k=='copy':need(rows[d]==0,'live copy temporary');rows[d]=rows[s]
  else:need(rows[d]==rows[s],'changed copy before erasure');rows[d]=0
 need(rows[-1]==0,'copy temporary remains')
 return rows[:-1]

def bill(w,W):
 paths=[[f] for f in w['start']]
 for sec in 'DABC':
  for f,d,ss in w[sec]:
   for r in [d]+ss:
    if paths[r][-1]!=f:
     need(W.nested(paths[r][-1],f) and W.fdim[paths[r][-1]]<W.fdim[f],'frame climb');paths[r].append(f)
 for r,f in enumerate(w['final']):
  if paths[r][-1]!=f:need(W.nested(paths[r][-1],f) and W.fdim[paths[r][-1]]<W.fdim[f],'final frame climb');paths[r].append(f)
 profile=Counter(W.fdim[b]-W.fdim[a] for p in paths for a,b in zip(p,p[1:]))
 copy_ranks=[t['rank'] for t in W.totals()];profile.update(copy_ranks)
 peaks=[];ops=stream(w)
 for reverse in (False,True):
  vals=[1]*(2*w['v']+w['R'])+[0];peak=1
  for k,d,s in (reversed(ops) if reverse else ops):
   if reverse:k={'copy':'erase','erase':'copy'}.get(k,k)
   vals[d]=vals[d]+vals[s] if k=='add' else (vals[s] if k=='copy' else 0);peak=max(peak,vals[d])
  peaks.append(peak)
 F,B=peaks;local=64*F**3*B**2;nine=(1<<18)*F**5*B**4
 need(local<1<<104 and nine<1<<192,'positive precision guard')
 return {'profile':{str(k):v for k,v in sorted(profile.items())},'rank_mass':sum(k*v for k,v in profile.items()),'copy_ranks':copy_ranks,
  'ADDS':sum(k=='add' for k,_,_ in ops),'D_ADDS':sum(len(ss) for _,_,ss in w['D']),'COPY':len(copy_ranks),'ERASE':len(copy_ranks),
  'F':F,'B':B,'local_integer':local,'nine_stage_integer':nine,'local_bits':local.bit_length(),'nine_stage_bits':nine.bit_length(),'frame_paths_sha256':digest(paths)}

def controls(w,N):
 v,R=w['v'],w['R'];n=2*v+R;zero=next(i for i,f in enumerate(w['frames']) if not f);out=[]
 def reject(name,bad,part):
  try:semantic(bad)
  except ValueError as e:need(part in str(e),'wrong rejection');out.append(name)
  else:raise ValueError('accepted '+name)
 # Endpoint-neutral forbidden changes still violate the retained contract.
 b=copy.deepcopy(w);b['D']=[[zero,2*v,[v]]]*2+b['D'];reject('target feedback despite neutral endpoint',b,'H1')
 b=copy.deepcopy(w);b['D']=[[zero,v,[0]]]*2+b['D'];reject('source access despite neutral endpoint',b,'Y/H')
 b=copy.deepcopy(w);b['D'][0][0]=next(i for i,f in enumerate(w['frames']) if f);reject('nonzero frame',b,'zero frame')
 b=copy.deepcopy(w);b['D'].append([zero,2*v,[2*v+1]]);reject('unrestored helper',b,'not restored')
 b=copy.deepcopy(w);b['D'].append([zero,v,[v+1]]);reject('target mixing at boundary',b,'helper-only')
 b=copy.deepcopy(w);b['D'].append([zero,v,[2*v]])
 try:check_k(semantic(b),N)
 except ValueError:out.append('wrong K rejected')
 else:raise ValueError('wrong semantic compensation accepted')
 need(all((a^c)&((1<<(2*v))-1)==0 for a,c in zip(drows(w['D'],n),drows(b['D'],n))),'wrong K clean-helper counterexample')
 # A restored helper conjugation is a valid new syntactic-H2 violation.
 fixture={'v':1,'R':2,'frames':[[]],'start':[0]*4,'D':[[0,2,[3]],[0,1,[2]],[0,2,[3]]]}
 need(semantic(fixture)==[3]==independent.inspect(fixture['D'],1,2),'positive restored sharing')
 out.append('positive restored helper circuit accepted')
 return out

def compute():
 (old,w),mod=source();need(all(w[k]==old[k] for k in old if k not in ('B','C','D')),'frozen nonedited fields')
 W0,lab0,flow0,hyp0,con0,_=mod.check(old);W,lab,flow,hyp,con,_=mod.check(w)
 need(all(hyp0.values()) and all(con0.values()),'original interface baseline')
 need([k for k,v in hyp.items() if not v]==['H2_D_frame0_targets_from_helpers'] and [k for k,v in con.items() if not v]==['K_equals_D'],'inherited rejection pattern')
 N=semantic(w);need(N==independent.inspect(w['D'],w['v'],w['R']),'independent complete D columns')
 need(N==semantic(old),'same selected compensation map')
 # Proof-only chronological bridge: leave the candidate continuation literal,
 # but use the original target-only D to invoke every old interface condition.
 bridge=copy.deepcopy(w);bridge['D']=copy.deepcopy(old['D'])
 _,_,_,bridge_hyp,bridge_con,_=mod.check(bridge)
 need(all(bridge_hyp.values()) and all(bridge_con.values()),'proof-only original-D interface bridge')
 need(semantic(bridge)==N,'proof-only D boundary equality')
 raw,_,_=W.replay(sections=('A','scatter','B'),frames_on=False)
 check_k(N,[raw[w['v']+t]>>(2*w['v']) for t in range(w['v'])])
 n=W.n;want=[(1<<r)^(1<<(r-w['v'])) if w['v']<=r<2*w['v'] else 1<<r for r in range(n)]
 need(literal(w)==want==literal(w,True),'complete literal forward/reverse endpoint')
 baseline=bill(old,W0);candidate=bill(w,W)
 for key in ('profile','rank_mass','copy_ranks','COPY','ERASE','frame_paths_sha256'):need(baseline[key]==candidate[key],'unchanged paid interface '+key)
 cs=controls(w,N)
 return {'base':BASE,'seed':10,'candidate':'PR1062 11500-ADD candidate','columns':n,'independent_D_columns':n,
  'candidate_under_unmodified_checker_hypotheses':hyp,'candidate_under_unmodified_checker_conclusions':con,
  'proof_only_original_D_bridge':{'hypotheses':bridge_hyp,'conclusions':bridge_con,
   'same_zero_frame_D_boundary':True,'continuation_unchanged':True,'virtual_D_cost_not_charged':True},
  'semantic_H2':True,'semantic_K_equals_D':True,'other_inherited_hypotheses_retained':True,'semantic_N_hex':[hex(x) for x in N],
  'baseline':baseline,'candidate_bill':candidate,'controls':cs,
  'scope':'Proved replacement scalar-interface contract for zero-frame D; no selected/native/hosting admission',
  'native_executed':False,'new_kappa':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();r=compute()
 if a.write:(HERE/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n')
 else:need(enc(r)==enc(read((HERE/'RESULT.json').read_bytes())),'typed canonical result mismatch')
 print('PASS_SEMANTIC_D_CONTRACT columns='+str(r['columns'])+' ADDs='+str(r['candidate_bill']['ADDS'])+' controls='+str(len(r['controls']))+' no_new_kappa')
if __name__=='__main__':main()
