"""Fresh compressed R822 supplier: literal signed cost and both exact engines."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
from collections import Counter
import importlib.util,json,gzip,struct,sys
assert __debug__;sys.dont_write_bytecode=True
assert len(sys.argv)==3;P=Path(sys.argv[1]).resolve();OUT=P/'full';SRC=Path(sys.argv[2]).resolve();read=lambda p:json.loads(p.read_bytes());sha=lambda p:sha256(p.read_bytes()).hexdigest()
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
G=load(P/'global_word.py','new_global');recipe=G.recipe();g=read(OUT/'GLOBAL.json');a=read(OUT/'AUDIT.json');geo=read(OUT/'GEOMETRY.json');s=read(P/'RESULT.json');blob=gzip.decompress((OUT/'GLOBAL-TEMPLATE.json.gz').read_bytes());template=read(OUT/'GLOBAL.json')
assert sha256(blob).hexdigest()==g['template_sha256']==a['template_sha256']
assert g['source_records_sha256']==s['exported_F2_record_sha256']==sha(P/'records/249-records.bin')
assert g['R']==822 and g['replicas']==8 and g['m']==64 and g['live']==15078
raw=list(struct.iter_unpack('<6i',(P/'records/249-records.bin').read_bytes()));signed=list(struct.iter_unpack('<6i',(P/'signed-records.bin').read_bytes()))
assert s['compensation']==dict(weighted_additions=8811,odd_additions=8699,even_additions=112,unit_additions=8963,maximum_coefficient=5)
def scan(events):
 v,R,L,K,T=120,822,9,4,8;local=2*v+R;n=2*K*v+L*R;temp=n;values=[1<<i for i in range(n)]+[0];norm=[1]*n+[0];peak=1;stages=[];copies=adds=bridges=0
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
cf=s['forward']['max_prefix_row_l1'];cb=s['literal_signed_inverse']['max_prefix_row_l1'];assert(cf,cb)==(742,7500)
prefix=(1<<18)*max(cf,g['local_checks']['forward']['cancellation_free_row_l1'])**5*max(cb,g['local_checks']['reverse']['cancellation_free_row_l1'])**4
assert prefix==int(g['global_prefix_bound']) and max(int(rawscan['prefix']),int(signedscan['prefix']))<=prefix<1<<192
localraw=sum(abs(c)for op,a,b,c,f,z in raw if op==1);localsigned=sum(abs(c)for op,a,b,c,f,z in signed if op==1);assert(localraw,localsigned)==(14689,14953)
H={int(k):n for k,n in g['profile'].items()};m=64;W=g['live'];E=sum(H.values());mass=sum(r*n for r,n in H.items());assert m*W-mass==2496
moment=load(SRC/'code/pricing/moment.py','m64_moment');other=load(SRC/'code/pricing/base_two_moment.py','m64_other')
root=moment.certify(H,m,W,True);grid=Q(1,10**24);c=Q(int(Q(root['lower'])*10**24),10**24)
bm=moment.moment(H,m,W,c,True);nm=moment.moment(H,m,W,c+grid,True);assert bm[1]<1<nm[0]
fallback=32*m*m*E
_,up=other.moment(m,W,list(H.items()),c);_,bad=other.moment(m,W,[(1,fallback)],c);lo,_=other.moment(m,W,list(H.items()),c+grid);lobad,_=other.moment(m,W,[(1,fallback)],c+grid)
assert up+Q(1,10**16)*bad<1<lo+Q(1,10**16)*lobad
assert 2*max(H)**2<m*m and bm[1]**2<1 and not 2*max(H)<m
T,L,R,V,K=8,9,822,120,4;physical=g['physical'];d=m*m;N=2*m;unit=L*T*localsigned+g['bridge_additions'];originalunit=L*T*localraw+g['bridge_additions'];assert unit-originalunit==72*264==19008
J=8*T*L*(2*V+R)+8*(2*K*V*T)+2*g['bank_assignments']+2*g['copy_erase_episodes'];high=16*(d+1)**2;good=8*m*m+8;compiler=128*N**3;selectors=2*L*T*((W-1)+R*m*(geo['max_route_factors']+(m-1)+m))
coefficient=unit+J*high+J*physical+E*(good+compiler)+16*m**3+g['copy_erase_episodes']+selectors+prefix+1;original=coefficient-19008;two=(coefficient+1)**2*(E+1)**2
assert coefficient<1<<192 and two<1<<512 and two<1<<30000
row=2*(m*m+1)+9909+252;assert row==18355<20161 and geo['route_denominators']==[1,2,4] and geo['bad_prime_factors']==[2]
r=dict(status='PASS_COMPRESSED_R822_SIGNED_SUPPLIER_FINITE_AND_TWO_MOMENTS',bit_coarse=str(c),bit_coarse_decimal=str(float(c)),m=m,W=W,physical=physical,histogram=H,deficit=2496,paid_calls=E,rank_mass=mass,halving_depth=2,row_coefficient=row,bit_moment_interval=list(map(str,bm)),independent_bit_moment_interval=[str(up+Q(1,10**16)*bad)],next_grid_rejected=True,two_rational_engines=True,raw_prefix_scan=rawscan,signed_prefix_scan=signedscan,finite=dict(raw_unit_additions=originalunit,signed_unit_additions=unit,extra_even_weighted_per_local=112,extra_unit_per_local=264,extra_global_unit=19008,route_items=J,selector_calls=selectors,raw_coefficient=str(original),coefficient=str(coefficient),coefficient_bits=coefficient.bit_length(),two_level_coefficient=str(two),two_level_bits=two.bit_length(),charged_finite_bits=512,prefix_majorant=str(prefix),prefix_bits=prefix.bit_length(),charged_payload_bits=192),inputs={str(p.relative_to(P)):sha(p)for p in [P/'ADAPTATION.json',P/'RESULT.json',P/'signed-records.bin',OUT/'GLOBAL.json',OUT/'GEOMETRY.json',OUT/'AUDIT.json',OUT/'GLOBAL-TEMPLATE.json.gz']},scope='Fresh compressed m64/T8 whole residual packing and source-template scalar replay. The signed defining source J mod2=I restores arbitrary local dirt; parity equals the emitted F2 program. Added even compensation is charged. Common-grid reflected chart/conditional all-size compiler, correlated-bank lifting, prime/tape/precision/recovery/analytic interface and dominating C_full remain inherited obligations; counted cutoff is not universal machine cutoff.')
(OUT/'SUPPLIER.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n');print('PASS',r['bit_coarse'],r['bit_coarse_decimal']);print('finite',coefficient,'two_level_bits',two.bit_length())
