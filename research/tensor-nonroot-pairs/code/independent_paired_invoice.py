"""Portable independent literal invoice for paired rational whole-owner bit programs.
Usage: python independent_paired_invoice.py GLOBAL_DIR PROVIDER_DIR ALLOCATION OUTPUT
This replays new emitted rows; it does not rerun unrelated public PRs.
"""
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction as Q
import json,gzip,struct,hashlib,sys

def read(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def jb(z):return json.dumps(z,separators=(',',':')).encode()
def check(folder,provider,allocation,out):
 folder,provider,allocation,out=map(Path,(folder,provider,allocation,out));g=read(folder/'GLOBAL.json');blob=gzip.decompress((folder/'GLOBAL-TEMPLATE.json.gz').read_bytes());t=json.loads(blob);w=read(provider/'word.json');a=read(allocation)
 assert sha(provider/'word.json')==g['word_sha256']==a['source_word_sha256']
 assert sha(allocation)==g['paired_allocation_sha256'];assert t['paired_rational_hosting']==a
 assert hashlib.sha256(blob).hexdigest()==g['template_sha256'];assert g['cover']==t['cover']=='GL'
 assert t['frame_geometry']==dict(lines=w['lines'],frames=w['frames'],initial=w['start'],final=w['final'])
 paired_frames=set(a['registry']);coordinate_frames={w['start'][h]for h in range(240,955)if str(w['start'][h])not in paired_frames}
 isos={z['frame']:z for z in t['residual_isometries']};assert set(isos)==coordinate_frames
 for f,z in isos.items():
  e=z['entrance_rank'];rows=z['orthogonal_rows_numerator'];den=z['denominator'];assert den==2 and len(rows)==8
  supports=[{i for i,x in enumerate(w['lines'][line])if x}for line in w['frames'][f]];axes=sorted(set().union(*supports))if supports else []
  assert len(axes)==e and all({i}in supports for i in axes)
  mat=[[Q(x,den)for x in row]for row in rows];assert all(sum(mat[i][k]*mat[j][k]for k in range(8))==int(i==j)for i in range(8)for j in range(8))
  assert all(sum(mat[k][i]*mat[k][j]for k in range(e))==int(i==j and i in axes)for i in range(8)for j in range(8))
 M,T,R=78,8,715;L=11;DATA=9600
 assert(g['m'],g['replicas'],g['R'],g['live'])==(M,T,R,DATA)
 raw=list(struct.iter_unpack('<6i',(provider/'records/249-records.bin').read_bytes()))
 assert sha(provider/'records/249-records.bin')==g['source_records_sha256']==t['source_record_sha256']
 local={};local_l1={};local_counts={}
 for rev,key in [(False,'forward'),(True,'reverse')]:
  expect=[]
  for op,x,y,c,f,z in (reversed(raw)if rev else raw):
   if op==0:expect.append([0,x,c if rev else y,y if rev else c,f,int(rev)])
   elif op==1:expect.append([1,x,y,-c if rev else c,f,int(rev)])
   elif op==(3 if rev else 2):expect.append([2,x,955,c,f,8,int(rev)])
   else:assert op==(2 if rev else 3);expect.append([3,x,955,c,f,z,int(rev)])
  assert expect==t['local_programs'][key]
  assert hashlib.sha256(jb(expect)).hexdigest()==g['local_checks'][key]['sha256']
  vals=[1<<i for i in range(955)]+[0];norm=[1]*955+[0];peak=1;hist=Counter();cnt=Counter();live=None
  for e in expect:
   typ,x=e[:2];cnt[typ]+=1
   if typ==0:
    if e[4]:hist[e[4]]+=1
   elif typ==1:
    y,c=e[2:4]
    if c%2:vals[x]^=vals[y]
    norm[x]+=abs(c)*norm[y];peak=max(peak,norm[x])
   elif typ==2:
    assert live is None and vals[955]==0;live=x;vals[955]=vals[x];norm[955]=norm[x];hist[e[5]]+=1
   else:
    assert live==x and vals[955]==vals[x];live=None;vals[955]=0;norm[955]=0
  assert live is None
  assert vals[:955]==[(1<<i)^((1<<(i-120))if 120<=i<240 else 0)for i in range(955)]
  assert peak==g['local_checks'][key]['cancellation_free_row_l1'];local[key]=hist;local_l1[key]=peak;local_counts[key]=cnt
 assert local['forward']==local['reverse']
 # Rebuild every pending-family remainder from actual occupied intervals.
 idle={e['idx']:e for e in t['schedule']if e['kind']=='idle'};used=defaultdict(list)
 for s,rep,h,z in a['owners']:
  c=idle[z['window']];assert c['source_level']<s<=c['target_level'];assert a['windows'][str(z['window'])][1]==c['rank']
  if z['kind']=='coordinate-whole':used[z['window'],z['family']].append((z['offset'],z['offset']+z['width']))
 for p in a['pairs']:
  c=idle[p['window']];assert c['source_level']<p['stage']<=c['target_level'];assert p['active_width']==14
  used[p['window'],p['family']].append((p['active_offset'],p['active_offset']+14))
 rem=Counter()
 for i,c in idle.items():
  for rep in range(T):
   for loc in range(240):
    fam=rep*1200+c['pair']*240+loc;ivs=sorted(used.pop((i,fam),[]));assert all(0<=x<y<=c['rank']for x,y in ivs);assert all(y<=xx for(x,y),(xx,yy)in zip(ivs,ivs[1:]));r=c['rank']-sum(y-x for x,y in ivs)
    if r:rem[r]+=1
 assert not used
 paid=Counter({r:n*L*T for r,n in local['forward'].items()});paid.update(rem)
 assert dict(paid)=={int(r):n for r,n in g['profile'].items()}=={int(r):n for r,n in a['profile'].items()}
 assert M*DATA-sum(r*n for r,n in paid.items())==g['deficit']==3264
 # Literal chronological physical-family maximum-norm envelope, with every bridge.
 calls={(c['stage'],c['replica']):c for c in t['calls']};assert len(calls)==L*T
 norms=[1]*DATA+[0];peak=1;digest=hashlib.sha256();events=0;adds=bridges=copies=clears=0
 for step in t['schedule']:
  if step['kind']=='local_cover_sweep':
   for rep in range(T):
    c=calls[step['stage'],rep];owners=c['owners'];assert len(owners)==955;active={f for f,r in owners[:240]};assert len(active)==240
    assert all(f not in active for f,r in owners[240:])
    for e in t['local_programs'][c['orientation']]:
     typ,x=e[:2];row=[typ,owners[x]]
     if typ==0:row.extend(e[2:])
     else:
      y=e[2];row.extend([owners[y]if y<955 else[DATA,['private',0]],*e[3:]]);fx=owners[x][0];fy=owners[y][0]if y<955 else DATA
      if typ==1:norms[fx]+=abs(e[3])*norms[fy];adds+=1
      elif typ==2:norms[DATA]=norms[fx];copies+=1
      else:assert typ==3;norms[DATA]=0;clears+=1
      peak=max(peak,norms[fx],norms[DATA])
     digest.update(jb(row)+b'\n');events+=1
  elif step['kind']=='bridge':
   d,s=step['dst'],step['src']
   for rep in range(T):
    for k in range(120):
     for x,y in[(rep*1200+2*d*120+k,rep*1200+2*s*120+k),(rep*1200+(2*s+1)*120+k,rep*1200+(2*d+1)*120+k)]:
      norms[x]+=norms[y];peak=max(peak,norms[x]);digest.update(jb(['bridge-add',x,y])+b'\n');events+=1;bridges+=1
 assert norms[DATA]==0 and str(peak)==g['global_prefix_bound'];assert peak.bit_length()==g['global_prefix_bits'];assert 64*((peak.bit_length()+63)//64)==g['charged_prefix_bits']
 assert digest.hexdigest()==g['emitted_program_sha256']and events==g['emitted_events']
 # Literal dyadic routing counts, separate from the retained symbolic GL-routing bound.
 route_counts={};route_values=set();factor_values=set()
 for f,z in a['registry'].items():
  G=[[Q(x)for x in row]for row in z['route']];Gi=[[Q(x)for x in row]for row in z['inverse']];assert len(G)==16 and all(len(r)==16 for r in G)
  assert Gi==list(map(list,zip(*G)))
  assert all(sum(G[i][k]*G[j][k]for k in range(16))==int(i==j)for i in range(16)for j in range(16))
  assert z['entrance_basis']==[w['lines'][i]for i in w['frames'][int(f)]]
  A=[r[:]for r in G]
  for op in z['elementary_reduction']:
   if op[0]=='swap':i,j=op[1:];A[i],A[j]=A[j],A[i]
   elif op[0]=='scale':i,q=op[1:];q=Q(q);assert q;factor_values.update((q,1/q));A[i]=[q*x for x in A[i]]
   else:assert op[0]=='add';i,j,q=op[1:];q=Q(q);factor_values.add(q);A[i]=[x+q*y for x,y in zip(A[i],A[j])]
  assert A==[[Q(i==j)for j in range(16)]for i in range(16)]
  route_counts[f]=len(z['elementary_reduction']);route_values.update(x for row in G for x in row)
 # A copy-block interchange uses at most8 swaps. Slot placement <=77 swaps.
 # Port geometry and general scalar owner routing are invoiced separately.
 max_local=max(route_counts.values(),default=0)+8
 assert max_local<=512
 factor_bits=max(max(abs(x.numerator).bit_length(),x.denominator.bit_length())for x in factor_values);assert factor_bits<=5
 row=3*(M*M+1)+9909+252;assert row==28416==g['row_coefficient']
 result=dict(status='PASS_INDEPENDENT_PAIRED_LITERAL_INVOICE',profile=dict(sorted(paid.items())),live=DATA,template_sha256=hashlib.sha256(blob).hexdigest(),physical_prefix_bits=peak.bit_length(),charged_prefix_bits=g['charged_prefix_bits'],hosted_residuals=len(a['owners']),bank_assignments=0,source_word_sha256=sha(provider/'word.json'),allocation_sha256=sha(allocation),emitted_program_sha256=digest.hexdigest(),emitted_events=events,local_additions=adds,bridge_additions=bridges,copy_erase_episodes=copies,clears=clears,local_prefix_row_l1=local_l1,rank_mass=sum(r*n for r,n in paid.items()),deficit=3264,cover='GL',row_coefficient=row,paired_route_one_direction_elementary_max=max(route_counts.values()),paired_route_with_copy_interchange_max=max_local,residual_isometry_allowance=512,route_extra_allowance=5,route_factor_max_bit_length=factor_bits,route_factor_values=sorted(map(str,factor_values)),placement_swap_bound=M-1,complete_pair_route_values=sorted(map(str,route_values)),scope='Independent exact new-source scalar and physical-family L1 invoice plus literal paired address-map factors. Actual physical owner injection is separately source-bound by hosting/audit_actual_pairs.py. Uses the explicitly retained PR490 fixed-GL-routing/all-size compiler interface; it does not turn that conditional interface into a new machine theorem.')
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['complete_pair_route_values','profile']},indent=2))
if __name__=='__main__':check(*sys.argv[1:])
