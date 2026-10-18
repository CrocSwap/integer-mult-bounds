"""Independent stdlib replay of whole-family footprint ownership and paid axes.
No import of the emitter or native optimizer. The whole9 packing is not the
invalid direct-sum replacement of a single helper by two smaller families.
"""
import json,gzip,hashlib,sys,copy
from pathlib import Path
from collections import Counter
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def audit(t,phase,base,ka,source,variant_programs,variant_checks):
 V,R,T,K,L,H=120,560,7,5,11,9;W=8400
 assert(t['m'],t['h'],t['replicas'],t['live'],t['stages'])==(89,H,T,W,L)
 assert t['private_centers']==ka['private_centers']and t['physical']==W+R+ka['private_centers']+2
 assert t['source_bindings']==source
 assert t['variant_stages']==list(range(11))
 assert t['provider_programs']=={'base':base['local_programs'],'kernel':variant_programs}
 assert t['provider_checks']=={'kernel':variant_checks}
 assert t['kernel_program_hashes']=={o:hashlib.sha256(canon(p)).hexdigest()for o,p in variant_programs.items()}
 for ori,pp in variant_programs.items():
  assert t['kernel_program_hashes'][ori]==variant_checks[ori]['sha256']
  hh=Counter(z[-1]for z in pp if z[0]in('climb','center'))
  assert dict(hh)=={int(r):n for r,n in ka['local_profile'].items()}
  wrap=[z for z in pp if z[0]=='monomial-wrapper'];assert len(wrap)==158
 assert t['baseline_program_hashes']=={o:hashlib.sha256(canon(p)).hexdigest()for o,p in base['local_programs'].items()}
 widths=ka['widths'];pivot=[h for h,w in enumerate(widths)if w==8]
 assert t['kernel_pivot_helpers']==pivot and len(pivot)==79
 expected_profiles={'base':{'1':1912,'2':784,'3':168,'4':224,'5':392,'8':24},'kernel':ka['local_profile']}
 assert t['local_profiles']==expected_profiles
 expected_schedule=copy.deepcopy(base['execution_schedule']);expected_schedule[-1]['families']=[0,W];expected_schedule[-1]['charged_calls_per_cover']=W
 assert t['execution_schedule']==expected_schedule
 last={};local_positions=[];win={};idle={};stage_info={}
 for pos,e in enumerate(t['execution_schedule']):
  if e['kind']=='local':
   s=e['stage'];assert s not in stage_info;stage_info[s]=e;last[e['pair']]=pos;local_positions.append((pos,s,e['pair']))
  elif e['kind']=='bridge':last[e['dst']]=pos;last[e['src']]=pos
  elif e['kind']=='idle':
   i,pair=e['idx'],e['pair'];assert i not in idle;idle[i]=e;lo=last.get(pair,-1)
   ss={s for pp,s,p in local_positions if lo<pp<pos and p!=pair}
   if ss and e['rank']:win[i]=(pair,e['rank'],ss)
 assert set(stage_info)==set(range(L))
 assert t['hosting']['windows']=={str(i):[p,r,sorted(ss)]for i,(p,r,ss)in win.items()}
 correction=t['execution_schedule'][-1]
 assert correction['kind']=='translate_every_live_family'and correction['families']==[0,W]and correction['charged_calls_per_cover']==W
 fullbasis={}
 for port,rec in enumerate(phase['recipes']):
  bb=sorted(set([rec['q']]+[a for ch in rec['idle_children']for a in ch['orthogonal_axes']]));assert len(bb)==89
  assert all((a&b).bit_count()%2==int(i==j)for i,a in enumerate(bb)for j,b in enumerate(bb));fullbasis[port]=set(bb)
 route_digest=hashlib.sha256()
 actual_calls={};occupied=set();active_occupied=set();used={};used_axes={};Hpaid=Counter();derivedslots=[];foreign=0;variant=0;active8=0;foot9=0
 for call in t['calls']:
  s,rep,p=call['stage'],call['replica'],call['pair'];assert s in stage_info and 0<=rep<T and(s,rep)not in actual_calls;actual_calls[s,rep]=call
  e=stage_info[s];assert p==e['pair']and p==((s+1)//2-1 if s else 0)
  ori='backward'if e['reverse']else'forward';assert call['orientation']==ori
  provider='kernel'if s in range(11)else'base';assert call['provider']==provider
  if provider=='base':assert call['local_program_sha256']==t['baseline_program_hashes'][ori]and call['local_word_sha256']is None and call['wrapper_sha256']is None
  else:assert call['local_program_sha256']==t['kernel_program_hashes'][ori] and call['local_word_sha256']==source['kernel_word']and call['wrapper_sha256']==source['kernel_wrapper'];variant+=1
  Hpaid.update({int(r):n for r,n in expected_profiles[provider].items()});own=call['owners'];assert len(own)==800
  for j in range(240):assert own[j]==[rep*1200+(2*p+j//120)*120+j%120,[1,s,j%120]]
  for h,(f,route)in enumerate(own[240:]):
   assert len(route)==6 and route[0]==5
   _,i,off,foot,w,spec=route;assert foot==9 and w==(widths[h]if provider=='kernel'else 9)and i in win
   pair,rr,ss=win[i];assert s in ss and pair!=p and 0<=off and off+w<=rr
   hr,within=divmod(f,1200);sideport=within-2*pair*120;assert 0<=hr<T and 0<=sideport<240
   side,port=divmod(sideport,120);ch=idle[i]['phase_children'][side];axes=phase['recipes'][port]['idle_children'][ch]['orthogonal_axes'];assert len(axes)==rr and len(set(axes))==rr
   af=axes[off:off+w]
   assert len(af)==w
   if w==8:
    assert spec in fullbasis[port]and isinstance(spec,int)and spec.bit_count()%2==1 and all((spec&a).bit_count()%2==0 for a in axes)and spec not in axes
    footprint=af+[spec]
   else:assert spec is None;footprint=af
   assert len(footprint)==9
   sigma=footprint+sorted(fullbasis[port]-set(footprint));assert len(sigma)==89 and len(set(sigma))==89
   route_digest.update(canon([s,rep,h,f,sigma])+b'\n')
   for a in footprint:assert(s,f,a)not in occupied;occupied.add((s,f,a))
   for a in af:assert(f,a)not in active_occupied;active_occupied.add((f,a))
   key=(i,hr,side,port);used.setdefault(key,set()).update(range(off,off+w));used_axes.setdefault(key,set()).update(axes[off:off+w])
   derivedslots.append([i,hr*240+side*120+port,off,9,w,s,rep,h,spec]);foreign+=hr!=rep;active8+=w==8;foot9+=1
 assert len(actual_calls)==77 and variant==77 and active8==6083 and foot9==43120 and len(occupied)==43120*9
 assert sorted(t['hosting']['slots'])==sorted(derivedslots)
 childkeys=set();inactive_paid=0
 for x in t['idle_children']:
  i,rep,side,port=x['idle'],x['replica'],x['side'],x['port'];key=(i,rep,side,port);assert key not in childkeys;childkeys.add(key)
  assert i in idle and 0<=rep<T and 0<=side<2 and 0<=port<120
  e=idle[i];ch=e['phase_children'][side];ph=phase['recipes'][port]['idle_children'][ch];assert x['phase_child']==ch and x['translation_after']==ph['translation_after']
  active=used.get(key,set());comp=[q for q in range(e['rank'])if q not in active]
  assert x['paid_complement_coordinates']==comp and x['rank']==len(comp)and x['active_hosted']==len(active)
  assert len(set(comp))==len(comp)and not(set(comp)&active)and set(comp)|active==set(range(e['rank']))
  if len(comp):Hpaid[len(comp)]+=1
 assert len(childkeys)==len(idle)*T*240
 assert dict(Hpaid)=={int(r):n for r,n in t['profile'].items()}
 mass=sum(r*n for r,n in Hpaid.items());assert mass==t['rank_mass']==744744 and 89*W-mass==t['deficit']==2856
 return dict(status='PASS_INDEPENDENT_WHOLE9_FOOTPRINT_ACTIVE_COMPLEMENT',profile=dict(sorted(Hpaid.items())),rank_mass=mass,deficit=2856,local_calls=77,kernel_calls=77,whole9_slots=foot9,active8_slots=active8,globally_disjoint_active_axes=len(active_occupied),whole_footprint_axis_cells=len(occupied),foreign_replica_slots=foreign,split_helpers=0,orthogonal_route_decoder_sha256=route_digest.hexdigest(),scope='Physical route and paid complement replay; separate source-bound complete local and Gaussian monomial audits establish the local provider/wrapper.')
def main():
 template,selection,basepath,phasepath,kernelpath,auditpath,wrappath,out,providerpath=map(Path,sys.argv[1:]);t,base,phase,ka=map(read,[template,basepath,phasepath,auditpath])
 sources={k:sha(p)for k,p in zip(['selection','base_template','data_phase','kernel_word','kernel_local_audit','kernel_wrapper'],[selection,basepath,phasepath,kernelpath,auditpath,wrappath])}
 sources.update(kernel_normalized_programs=sha(providerpath/'NORMALIZED-PROGRAMS.json.gz'),kernel_normalized_checks=sha(providerpath/'NORMALIZED-CHECKS.json'),kernel_canonical_word=sha(providerpath/'CANONICAL-WORD.json.gz'))
 vp,vc=read(providerpath/'NORMALIZED-PROGRAMS.json.gz'),read(providerpath/'NORMALIZED-CHECKS.json')
 assert ka['canonical_word_sha256']==sha(kernelpath)
 kw=read(kernelpath);ka['private_centers']=len(kw['centers']);ka['widths']=[9-len(kw['frames'][f])for f in kw['start'][240:]]
 got=audit(t,phase,base,ka,sources,vp,vc);mut={}
 def test(name,fn):
  q=copy.deepcopy(t);fn(q)
  try:audit(q,phase,base,ka,sources,vp,vc)
  except(AssertionError,KeyError,IndexError,TypeError):mut[name]='REJECTED'
  else:raise AssertionError('vacuous mutation '+name)
 ic=next(i for i,c in enumerate(t['calls'])if c['provider']=='kernel');h=t['kernel_pivot_helpers'][0]+240
 test('compressed footprint8',lambda q:q['calls'][ic]['owners'][h][1].__setitem__(3,8))
 test('charged active rank9 instead8',lambda q:q['calls'][ic]['owners'][h][1].__setitem__(4,9))
 test('wrong complete provider',lambda q:q['calls'][ic].__setitem__('provider','base'))
 test('wrong provider word hash',lambda q:q['calls'][ic].__setitem__('local_word_sha256','0'*64))
 test('wrong monomial wrapper hash',lambda q:q['calls'][ic].__setitem__('wrapper_sha256','0'*64))
 test('wrong forward reverse orientation',lambda q:q['calls'][ic].__setitem__('orientation','backward'))
 test('whole helper overlaps another',lambda q:q['calls'][ic]['owners'].__setitem__(h,copy.deepcopy(q['calls'][ic]['owners'][h+1])))
 test('active data family alias',lambda q:q['calls'][ic]['owners'][h].__setitem__(0,q['calls'][ic]['owners'][0][0]))
 test('off family footprint',lambda q:q['calls'][ic]['owners'][h][1].__setitem__(2,100))
 test('dropped helper',lambda q:q['calls'][ic]['owners'].pop())
 test('dropped invocation',lambda q:q['calls'].pop())
 test('dropped physical slot ledger',lambda q:q['hosting']['slots'].pop())
 ix=next(i for i,x in enumerate(t['idle_children'])if x['rank']>0 and x['active_hosted']>0)
 test('omitted paid complement coordinate',lambda q:q['idle_children'][ix]['paid_complement_coordinates'].pop())
 test('forged complement rank',lambda q:q['idle_children'][ix].__setitem__('rank',t['idle_children'][ix]['rank']+1))
 test('dropped idle complement',lambda q:q['idle_children'].pop())
 test('dropped mandatory final translation',lambda q:q['execution_schedule'].pop())
 test('corrupted actual normalized program',lambda q:q['provider_programs']['kernel']['forward'].pop())
 test('corrupted invocation program hash',lambda q:q['calls'][ic].__setitem__('local_program_sha256','0'*64))
 test('changed inherited controller',lambda q:q['execution_schedule'][1].__setitem__('pair',4))
 test('borrowed spectator aliases active direction',lambda q:q['calls'][ic]['owners'][h][1].__setitem__(5,1))
 test('understated physical workspace',lambda q:q.__setitem__('physical',q['physical']-1))
 test('forged paid profile',lambda q:q['profile'].__setitem__('8',q['profile']['8']-1))
 got.update(template_sha256=hashlib.sha256(canon(t)).hexdigest(),source_bindings=sources,mutations_rejected=mut)
 out.write_text(json.dumps(got,indent=2)+'\n');print(json.dumps(got,indent=2))
if __name__=='__main__':main()
