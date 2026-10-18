"""Frozen kernel whole-nine-axis footprint construction. No compressed family aliases.
The local words and exact two-sided monomial wrapper are separate source-bound
providers. This file constructs their complete physical ownership and paid
active-complement partition, not an uncharged change of provider semantics.
"""
import json,gzip,hashlib,sys
from pathlib import Path
from collections import Counter,defaultdict,deque
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def emit(selpath,basepath,phasepath,kernelpath,auditpath,wrappath,outpath,providerpath):
 sel,base,phase,kernel,ka,wr=map(read,[selpath,basepath,phasepath,kernelpath,auditpath,wrappath])
 providerpath=Path(providerpath);vp=read(providerpath/'NORMALIZED-PROGRAMS.json.gz');vc=read(providerpath/'NORMALIZED-CHECKS.json');vword=read(providerpath/'CANONICAL-WORD.json.gz')
 for ori,prog in vp.items():
  assert hashlib.sha256(canon(prog)).hexdigest()==vc[ori]['sha256']
  assert vc[ori]['all_columns']==800 and vc[ori]['wrapper_helpers']==79
  assert vc[ori]['paid_profile']==ka['local_profile']
 T=sel['replicas'];V,R,H,K,L=120,560,9,5,11;W=1200*T
 assert T==7
 assert ka['canonical_word_sha256']==sha(kernelpath)and ka['all_target_rows_correct']and ka['all_live_source_and_helper_rows_restored']
 widths=[9-len(kernel['frames'][f])for f in kernel['start'][240:]];assert len(widths)==R and Counter(widths)=={9:481,8:79}
 schedule=json.loads(json.dumps(base['execution_schedule']));schedule[-1]['families']=[0,W];schedule[-1]['charged_calls_per_cover']=W
 win={int(i):(p,r,set(ss))for i,(p,r,ss)in base['hosting']['windows'].items()}
 idle={e['idx']:e for e in schedule if e['kind']=='idle'}
 expected_stages=set(range(11));assert{int(s)for s,n in sel['kernel_calls_perstage'].items()if n}==expected_stages
 assert all(n in(0,T)for n in sel['kernel_calls_perstage'].values())
 stagequeue=defaultdict(deque)
 for i,w,s,n in sel['stages']:
  assert s in win[i][2]
  stagequeue[i,w].extend([s]*n)
 helpers={}
 for s in range(L):
  for w in(8,9):helpers[s,w]=deque((rep,h)for rep in range(T)for h in range(R)if (widths[h]if s in expected_stages else 9)==w)
 slots=[];cpnext=Counter();active=defaultdict(set)
 for i,pat,nn in sel['patterns']:
  rr=win[i][1];assert sum(pat)<=rr and 9*len(pat)<=89 and pat.count(8)<=89-rr
  for _ in range(nn):
   cp=cpnext[i];cpnext[i]+=1
   for j,w in enumerate(pat):
    off=sum(pat[:j]);s=stagequeue[i,w].popleft();rep,h=helpers[s,w].popleft()
    slots.append([i,cp,off,9,w,s,rep,h]);active[i,cp].update(range(off,off+w))
 assert all(cpnext[i]==240*T for i in win)and not any(stagequeue.values())and not any(helpers.values())
 host={(s,rep,h):(i,cp,off,fp,w)for i,cp,off,fp,w,s,rep,h in slots};assert len(host)==L*T*R
 profiles={'base':{int(r):n for r,n in sel['local_profile'].items()},'kernel':{int(r):n for r,n in ka['local_profile'].items()}}
 bh={o:hashlib.sha256(canon(program)).hexdigest()for o,program in base['local_programs'].items()}
 calls=[];paid=Counter();spectators=defaultdict(set);physical_slots=[];stage_owner_child={}
 fullbasis={}
 for port,rec in enumerate(phase['recipes']):
  axes=set(a for ch in rec['idle_children']for a in ch['orthogonal_axes']);axes.add(rec['q']);assert len(axes)==89
  axes=sorted(axes);assert all((a&b).bit_count()%2==int(i==j)for i,a in enumerate(axes)for j,b in enumerate(axes));fullbasis[port]=axes
 for e in schedule:
  if e['kind']!='local':continue
  s,p=e['stage'],e['pair'];ori='backward'if e['reverse']else'forward';provider='kernel'if s in expected_stages else'base'
  for rep in range(T):
   owners=[[rep*1200+(2*p+j//V)*V+j%V,[1,s,j%V]]for j in range(240)]
   for h in range(R):
    i,cp,off,fp,w=host[s,rep,h];hr,sp=divmod(cp,240);side,port=divmod(sp,120)
    f=hr*1200+(2*win[i][0]+side)*120+port;ch=idle[i]['phase_children'][side];ax=phase['recipes'][port]['idle_children'][ch]['orthogonal_axes'];spec=None
    assert (s,f)not in stage_owner_child or stage_owner_child[s,f]==i;stage_owner_child[s,f]=i
    if w==8:
     spec=next(a for a in fullbasis[port]if a not in ax and a not in spectators[s,f]);spectators[s,f].add(spec)
    owners.append([f,[5,i,off,fp,w,spec]]);physical_slots.append([i,cp,off,fp,w,s,rep,h,spec])
   calls.append(dict(stage=s,replica=rep,pair=p,orientation=ori,provider=provider,owners=owners,
    local_program_sha256=bh[ori]if provider=='base'else vc[ori]['sha256'],
    local_word_sha256=sha(kernelpath)if provider=='kernel'else None,
    wrapper_sha256=sha(wrappath)if provider=='kernel'else None))
   paid.update(profiles[provider])
 children=[]
 for i,e in sorted(idle.items()):
  for cp in range(240*T):
   rep,sp=divmod(cp,240);side,port=divmod(sp,120);ch=e['phase_children'][side];ph=phase['recipes'][port]['idle_children'][ch]
   complement=[k for k in range(e['rank'])if k not in active[i,cp]];rr=len(complement)
   children.append(dict(idle=i,replica=rep,side=side,port=port,phase_child=ch,rank=rr,
    active_hosted=e['rank']-rr,paid_complement_coordinates=complement,translation_after=ph['translation_after']))
   if rr:paid[rr]+=1
 assert dict(paid)=={int(r):n for r,n in sel['full_profile'].items()}
 sources={k:sha(p)for k,p in zip(['selection','base_template','data_phase','kernel_word','kernel_local_audit','kernel_wrapper'],[selpath,basepath,phasepath,kernelpath,auditpath,wrappath])}
 sources.update(kernel_normalized_programs=sha(providerpath/'NORMALIZED-PROGRAMS.json.gz'),kernel_normalized_checks=sha(providerpath/'NORMALIZED-CHECKS.json'),kernel_canonical_word=sha(providerpath/'CANONICAL-WORD.json.gz'))
 t=dict(provider_programs={'base':base['local_programs'],'kernel':vp},kernel_program_hashes={o:z['sha256']for o,z in vc.items()},provider_checks={'kernel':vc},version='kernel-whole9-borrowed-spectator-v1',m=89,h=9,replicas=T,live=W,stages=L,
  physical=W+R+len(vword['centers'])+2,private_centers=len(vword['centers']),local_profiles=profiles,execution_schedule=schedule,calls=calls,idle_children=children,
  hosting=dict(windows={str(i):[p,r,sorted(ss)]for i,(p,r,ss)in win.items()},slots=physical_slots),
  source_bindings=sources,baseline_program_hashes=bh,kernel_pivot_helpers=[h for h,w in enumerate(widths)if w==8],
  variant_stages=sorted(expected_stages),profile=dict(sorted(paid.items())),rank_mass=sum(r*n for r,n in paid.items()),deficit=408*T,
  route_decoder='kind5: active=child.orthogonal_axes[off:off+w]; footprint=active+[spectator] iff w8; sigma columns=footprint+sorted(full89basis-minusfootprint). Full basis is q plus union of idle orthogonal axes. Conjugate entire normalized helper by sigma, extend identity on remaining80; inherited cover route composes d*sigma^-1.',wrapper_placement='before and after the complete selected local word; full9 pre=R^-1, post=L^-1, same orientation convention as kernel wrapper certificate',
  complement_rule='Every helper occupies all9 physical axes in one family. Rank8 activeblock lies in idlechild; ninth spectator is an actual orthogonal axis outside that child, reused only across complete sequential calls. Paid complement is exactly child minus activeblocks.',
  scope='Exact physical ownership and paid partition. Local scalar/formal-column and two-sided Gaussian monomial certificates are source-bound separate providers; retained all-size/hosting interfaces remain conditional.')
 assert 89*W-t['rank_mass']==t['deficit'];t=json.loads(json.dumps(t));b=canon(t);Path(outpath).write_bytes(gzip.compress(b,mtime=0));return dict(template_sha256=hashlib.sha256(b).hexdigest(),profile=t['profile'],calls=len(calls),whole9_slots=len(slots),variant_calls=sum(c['provider']=='kernel'for c in calls),sources=sources)
if __name__=='__main__':print(json.dumps(emit(*sys.argv[1:]),indent=2))
