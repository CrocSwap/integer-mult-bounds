"""Complete source-template-bound PR433 signed/unsigned scalar prefix and bill."""
from pathlib import Path
from hashlib import sha256
import importlib.util,json,struct,gzip
assert __debug__
import sys
if not __debug__:raise RuntimeError('Assertions required')
assert len(sys.argv)==5
SRC,NATIVE,N386,FRESH_GEO=map(lambda x:Path(x).resolve(),sys.argv[1:])
P=Path(__file__).resolve().parent;BIT=NATIVE/'bit426-source-centres';read=lambda p:json.loads(p.read_bytes());sha=lambda p:sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('native433global',SRC/'code/bit_global.py');G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G);recipe=G.recipe()
g=read(BIT/'global/GLOBAL.json');geo=read(FRESH_GEO);audit=read(BIT/'global/AUDIT.json');signed_result=read(P/'RESULT.json');t=json.loads(gzip.decompress((BIT/'global/GLOBAL-TEMPLATE.json.gz').read_bytes()))
assert g['template_sha256']==audit['template_sha256']==sha256(gzip.decompress((BIT/'global/GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest()
assert [{k:e[k]for k in ['stage','pair','reverse']}for e in recipe if e['kind']=='local']==[{k:e[k]for k in ['stage','pair','reverse']}for e in t['schedule']if e['kind']=='local_cover_sweep']
assert [e for e in recipe if e['kind']=='bridge']==[e for e in t['schedule']if e['kind']=='bridge']
assert sha(P/'records/249-records.bin')==g['source_records_sha256']==signed_result['exported_F2_record_sha256']
raw=list(struct.iter_unpack('<6i',(P/'records/249-records.bin').read_bytes()));signed=list(struct.iter_unpack('<6i',(P/'signed-records.bin').read_bytes()))
def scan(events):
 v,R,L,K,T=120,758,9,4,8;local=2*v+R;n=2*K*v+L*R;temp=n;values=[1<<i for i in range(n)]+[0];norm=[1]*n+[0];peak=1;stages=[];copies=adds=bridges=0
 for stage in recipe:
  if stage['kind']=='local':
   s,p,rev=stage['stage'],stage['pair'],stage['reverse'];opened=None
   def mapper(r):
    if r==local:return temp
    if r<2*v:return (2*p+(1-r//v if rev else r//v))*v+r%v
    return 2*K*v+s*R+r-2*v
   for op,a,b,c,f,z in reversed(events)if rev else events:
    if op==0:continue
    x,y=mapper(a),mapper(b)
    if op==1:
     assert x!=y and x!=temp and x!=opened
     if y==temp:assert opened is not None
     norm[x]+=abs(c)*norm[y];peak=max(peak,norm[x]);adds+=abs(c)
     if c&1:values[x]^=values[y]
    elif op==(3 if rev else 2):
     assert opened is None and b==local and norm[temp]==0 and values[temp]==0;opened=x;values[temp]=values[x];norm[temp]=norm[x];copies+=1
    else:
     assert op==(2 if rev else 3)and opened==x and values[temp]==values[x];values[temp]=norm[temp]=0;opened=None
   assert opened is None and all(values[2*K*v+s*R+r]==1<<(2*K*v+s*R+r)for r in range(R))
   stages.append(dict(stage=s,reverse=rev,max_prefix_row_l1=str(peak)))
  elif stage['kind']=='bridge':
   d,s,c=stage['dst'],stage['src'],stage['coefficient'];assert abs(c)==1
   for side,sign in [(0,c),(1,-c)]:
    dst,src=((2*d)*v,(2*s)*v)if side==0 else((2*s+1)*v,(2*d+1)*v)
    for i in range(v):values[dst+i]^=values[src+i];norm[dst+i]+=abs(sign)*norm[src+i];peak=max(peak,norm[dst+i]);bridges+=1
  else:
   assert stage['kind']=='exchange'
   for p in range(K):
    for i in range(v):x,y=2*p*v+i,(2*p+1)*v+i;values[x],values[y]=values[y],values[x];norm[x],norm[y]=norm[y],norm[x]
 assert values==[1<<i for i in range(n)]+[0]and copies==81 and bridges==18*v
 return dict(columns_per_replica=n,direct_sum_columns=T*n,stages=stages,prefix=str(peak),bits=peak.bit_length(),unit_additions_per_replica=adds+bridges,all_F2_columns_restored=True)
rawscan=scan(raw);signedscan=scan(signed)
rf=g['local_checks']['forward']['cancellation_free_row_l1'];rb=g['local_checks']['reverse']['cancellation_free_row_l1'];sf=signed_result['forward']['max_prefix_row_l1'];sb=signed_result['literal_signed_inverse']['max_prefix_row_l1'];assert(rf,rb,sf,sb)==(3885147,15348208,3885147,15348968)
rawprefix=(1<<18)*rf**5*rb**4;signedprefix=(1<<18)*sf**5*sb**4;assert rawprefix==int(g['global_prefix_bound']);prefix=max(rawprefix,signedprefix);assert max(int(rawscan['prefix']),int(signedscan['prefix']))<=prefix<1<<256
localraw=sum(abs(c)for op,a,b,c,f,z in raw if op==1);localsigned=sum(abs(c)for op,a,b,c,f,z in signed if op==1);assert(localraw,localsigned)==(14510,15196)
H={int(k):v for k,v in g['profile'].items()};m,W,T,L,R,V,K=64,14502,8,9,758,120,4;E=sum(H.values());physical=g['physical'];d=m*m;N=2*m
assert m*W-sum(r*n for r,n in H.items())==2496 and 2*max(H)**2<m*m and g['bank_assignments']==54576 and g['independent_unbanked_scalar_columns']==7782
J=8*T*L*(2*V+R)+8*(2*K*V*T)+2*g['bank_assignments']+2*g['copy_erase_episodes'];high=16*(d+1)**2;good=8*m*m+8;compiler=128*N**3;selectors=2*L*T*((W-1)+R*m*(geo['max_route_factors']+(m-1)+m))
fixed=J*high+J*physical+E*(good+compiler)+16*m**3+g['copy_erase_episodes']+selectors+1
rawunit=72*localraw+g['bridge_additions'];signedunit=72*localsigned+g['bridge_additions'];assert signedunit-rawunit==49392
rawcoef=rawunit+fixed+rawprefix;coef=signedunit+fixed+prefix;rawtwo=(rawcoef+1)**2*(E+1)**2;two=(coef+1)**2*(E+1)**2;assert coef<1<<256 and two<1<<512
row=2*(m*m+1)+9909+252;assert row==18355<20161
source_inputs={}
for namespace,root,names in [
 ('source',SRC,['MANIFEST.json','code/bit_construct.py','code/bit_global.py','code/bit_audit.py','code/combined.py']),
 ('native',NATIVE,['bit426-source-centres/bit-source-centres.json','bit426-source-centres/bit-source-centres-receipt.json','bit426-source-centres/global/GLOBAL.json','bit426-source-centres/global/GLOBAL-TEMPLATE.json.gz','bit426-source-centres/global/GEOMETRY.json','bit426-source-centres/global/AUDIT.json','BIT-PRICE.json']),
 ('signed',P,['RESULT.json','ADAPTATION.json','signed-records.bin','global_bound.py','geometry/GEOMETRY.json']),
 ('geometry-source',N386,['MANIFEST.json','geometry.py'])]:
 for name in names:source_inputs[namespace+'/'+name]=sha(root/name)

r=dict(status='PASS_PR433_SIGNED_SOURCE_COMPLETE_PREFIX_AND_COMPENSATED_FINITE_INVOICE',bit_coarse=read(NATIVE/'BIT-PRICE.json')['lower'],raw=rawscan,signed=signedscan,local_majorants=dict(raw_forward=rf,raw_reverse=rb,signed_forward=sf,signed_reverse=sb),finite=dict(raw_prefix=str(rawprefix),signed_prefix=str(signedprefix),charged_prefix=str(prefix),prefix_bits=prefix.bit_length(),allowed_prefix_bits=256,raw_unit_additions=rawunit,signed_unit_additions=signedunit,extra_unit_per_local=686,extra_unit_all72=49392,extra_even_weighted_per_local=245,raw_coefficient=str(rawcoef),signed_coefficient=str(coef),coefficient_bits=coef.bit_length(),raw_two_level_coefficient=str(rawtwo),signed_two_level_coefficient=str(two),two_level_bits=two.bit_length(),charged_two_level_bits=512,row_coefficient=row,route_items=J,selector_calls=selectors),source_inputs=source_inputs,scope='Signed defining J mod2I with arbitrary dirt restored, including literal negative inverse of559source-basis shears. The original unsigned source parity word is not an integeridentity certificate. Complete recipe scalar replay matched to native emittedtemplate; reflected rational charts/wholecorrelatedbank and all-size compiler/precision/tape/prime/recovery/analytic/C_full obligations remain conditional. Increased exactprefixand49392unitcharge preserve256/512allowances; native433 originally inherited global geometry; this supplement freshly reruns the unchanged PR386 geometry with only the explicit candidate filename and R758 dimension assertions adapted, compares all mathematical fields, and binds that fresh receipt here.')
(P/'GLOBAL-BOUND.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items()if k not in ['source_inputs','raw','signed']},indent=2))
