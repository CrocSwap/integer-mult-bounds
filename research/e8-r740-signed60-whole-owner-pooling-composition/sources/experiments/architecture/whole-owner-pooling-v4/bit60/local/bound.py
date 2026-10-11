"""Fresh R740 exact signed 95-relation kernel signed prefix and conservative counted invoice."""
from pathlib import Path
from hashlib import sha256
import json,struct,gzip,importlib.util
P=Path(__file__).resolve().parent;ROOT=P.parents[4];SRC=ROOT/'experiments/bit-search/pr434/source/research/e8-early-reset-kernel';FRESH=ROOT/'experiments/stage-search/pr441-signed-retime/full';BIT=P;HOST=P.parent;read=lambda p:json.loads(p.read_bytes());sha=lambda p:sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('reset434global',P.parent/'emit.py');G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G);recipe=G.recipe()
g=read(HOST/'GLOBAL.json');geo=read(HOST/'GEOMETRY.json');s=read(P/'RESULT.json');template=json.loads(gzip.decompress((HOST/'GLOBAL-TEMPLATE.json.gz').read_bytes()))
assert g['word_sha256']==sha(P/'word.json.gz')and s['exported_F2_record_sha256']==g['source_records_sha256']==sha(BIT/'records/249-records.bin')
assert g['template_sha256']==sha256(gzip.decompress((HOST/'GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest()
assert [{k:e[k]for k in ['stage','pair','reverse']}for e in recipe if e['kind']=='local']==[{k:e[k]for k in ['stage','pair','reverse']}for e in template['schedule']if e['kind']=='local_cover_sweep']
assert [e for e in recipe if e['kind']=='bridge']==[e for e in template['schedule']if e['kind']=='bridge']
def scan(events):
 v,R,L,K,T=120,740,11,5,8;local=2*v+R;n=2*K*v+L*R;temp=n;values=[1<<i for i in range(n)]+[0];norm=[1]*n+[0];peak=1;stages=[];copies=adds=bridges=0
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
 assert values==[1<<i for i in range(n)]+[0]and copies==99 and bridges==24*v
 return dict(columns_per_replica=n,direct_sum_columns=T*n,stages=stages,prefix=str(peak),bits=peak.bit_length(),unit_additions_per_replica=adds+bridges,all_F2_columns_restored=True)
raw=list(struct.iter_unpack('<6i',(P/'records/249-records.bin').read_bytes()));signed=list(struct.iter_unpack('<6i',(P/'signed-records.bin').read_bytes()));rawscan=scan(raw);signedscan=scan(signed)
rf,rb=[g['local_checks'][k]['cancellation_free_row_l1']for k in('forward','reverse')];sf,sb=s['forward']['max_prefix_row_l1'],s['literal_signed_inverse']['max_prefix_row_l1'];assert(rf,rb,sf,sb)==(1086,19064,1124,27414)
rawprefix=2**24*rf**6*rb**5;signedprefix=2**24*sf**6*sb**5;prefix=max(rawprefix,signedprefix);assert rawprefix==int(g['global_prefix_bound'])and max(int(rawscan['prefix']),int(signedscan['prefix']))<=prefix<2**192
m,W,T,L,R,V,K=78,g['live'],8,11,740,120,5;H={int(k):v for k,v in g['profile'].items()};E=sum(H.values());physical=g['physical'];d=m*m;N=2*m
assert(W,physical,g['bank_assignments']+g['hosted_residuals'])==(9600,9609,65120)and m*W-sum(r*n for r,n in H.items())==3264
localraw=sum(abs(c)for op,a,b,c,f,z in raw if op==1);localsigned=sum(abs(c)for op,a,b,c,f,z in signed if op==1);assert localraw==g['local_additions']==15192 and localsigned-localraw==s['compensation']['unit_additions']-s['compensation']['odd_additions']==1274
J=8*T*L*(2*V+R)+8*(2*K*V*T)+2*(g['bank_assignments']+g['hosted_residuals'])+2*g['copy_erase_episodes'];high=16*(d+1)**2;good=8*m*m+8;compiler=128*N**3;selectors=2*L*T*((W-1)+R*m*(geo['max_route_factors']+144+5+(m-1)+m))
target_selectors=read(P.parent/'TARGET-OPERATOR.json')['extra_route_selector_bound'];selectors+=target_selectors
dispatch=100000
fixed=dispatch+J*high+J*physical+E*(good+compiler)+16*m**3+g['copy_erase_episodes']+selectors+1
rawunit=88*localraw+g['bridge_additions'];signedunit=88*localsigned+g['bridge_additions'];coef=signedunit+fixed+prefix;rawcoef=rawunit+fixed+rawprefix;two=(coef+1)**3*(E+1)**3
assert coef<2**192 and two<2**1024
assert s['integer_kernel']['pivots']==95 and s['integer_kernel']['all_positive_start_responses_zero_over_Z']
assert len(s['controls'])==4 and all(c['rejected'] for c in s['controls'])
source=[P.parent/'TARGET-OPERATOR.json',HOST/'GLOBAL.json',HOST/'GEOMETRY.json',HOST/'GLOBAL-TEMPLATE.json.gz',P/'RESULT.json',P/'signed-records.bin',P/'records/249-records.bin',HOST/'HOSTING-SELECTION.json',P.parent/'ISOMETRIES.json',P.parent/'emit.py',P.parent/'hosting_core.py',Path(__file__),HOST/'HOSTED-SIGMA.json']
r=dict(status='PASS_SIGNED60_WHOLE_REPLICA_POOL_COMPLETE_STAGE_CUT_PREFIX_AND_FINITE_INVOICE',raw=rawscan,signed=signedscan,local_majorants=dict(raw_forward=rf,raw_reverse=rb,signed_forward=sf,signed_reverse=sb),finite=dict(raw_prefix=str(rawprefix),signed_prefix=str(signedprefix),charged_prefix=str(prefix),prefix_bits=prefix.bit_length(),allowed_prefix_bits=192,raw_unit_additions=rawunit,signed_unit_additions=signedunit,extra_unit_per_local=1274,extra_unit_all88=signedunit-rawunit,extra_even_weighted_per_local=400,raw_coefficient=str(rawcoef),signed_coefficient=str(coef),coefficient_bits=coef.bit_length(),signed_three_level_coefficient=str(two),three_level_bits=two.bit_length(),charged_three_level_bits=1024,row_coefficient=19431,route_items=J,selector_calls=selectors,extra_target_route_selector_calls=target_selectors,whole_owner_dispatch=dispatch,whole_owner_additional_selector_factors=3),source_inputs={str(p.resolve()):sha(p)for p in source},scope='Target-prefix relative port routes explicitly add the current counted selector calls using154 elementary factors per new target ADD; generalized current-label target-as-source weighted compiler remains conditional. R740 with 95 positive-entrance pivots, total entrance rank119; every positive-start signed K column vanishes over Z. Exact signed defining J mod2I, source rows and arbitrary helper dirt restored, complete source-bound eleven-stage scalar scan. The signed sidecar is byte-identical to independently admitted signed60. Wholeowner pooling uses onlywholehelper arrays on inactivepairs acrossallreplicas, with three additional selector factors and100000dispatch units paid. Prefix uses audited phase cuts: fullcover dataownership bijective, every complete helper endpoint is addresspermutation D_U independentofactivefreshsource, workzero, and inactivehostpair prevents earlierrep activegrowth feeding laterrep helpers. This retains the explicit universal dirty-slot interface; intermediate replicas need not be independent. Mixed residual bank and global geometry are separately source-bound below. Rational charts, compressed-window/correlated-bank, all-size compiler/precision/tape/prime/recovery/analytic/C_full obligations stay conditional.')
(P/'GLOBAL-BOUND.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n');print(json.dumps(r['finite'],indent=2));print(sha(P/'GLOBAL-BOUND.json'))
