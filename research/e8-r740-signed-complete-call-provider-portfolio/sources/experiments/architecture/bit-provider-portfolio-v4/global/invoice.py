"""Actual heterogeneous signed streams, stage-cut bound and explicitly paid registry."""
from pathlib import Path
from collections import Counter
import json,gzip,struct,hashlib,importlib.util
P=Path(__file__).resolve().parent;ROOT=P.parents[3];BASE=ROOT/'experiments/architecture/whole-owner-pooling-v4/bit60';read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
g=read(P/'GLOBAL.json');t=json.loads(gzip.decompress((P/'GLOBAL-TEMPLATE.json.gz').read_bytes()));reg=read(P/'PROVIDERS.json');local=g['local_checks'];src={pid:Path(z['directory'])for pid,z in reg.items()}
records={pid:{kind:list(struct.iter_unpack('<6i',(s/('signed-records.bin'if kind=='signed'else'records/249-records.bin')).read_bytes()))for kind in ['raw','signed']}for pid,s in src.items()}
spec=importlib.util.spec_from_file_location('old',BASE/'emit.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
# Explicit unbanked full-stage parity endpoint and cancellation-free row norms.
def scan(kind):
 n=9340;temp=n;val=[1<<i for i in range(n)]+[0];norm=[1]*n+[0];peak=1;units=0;stages=[]
 for e in old.recipe():
  if e['kind']=='local':
   s,p,rev=e['stage'],e['pair'],e['reverse'];pid='lazy'if s==5 else'base';opened=False
   def mp(i):return temp if i==980 else((2*p+(1-i//120 if rev else i//120))*120+i%120 if i<240 else 1200+s*740+i-240)
   for op,a,b,c,f,z in reversed(records[pid][kind])if rev else records[pid][kind]:
    if op==0:continue
    x,y=mp(a),mp(b)
    if op==1:
     units+=abs(c);norm[x]+=abs(c)*norm[y];peak=max(peak,norm[x])
     if c&1:val[x]^=val[y]
    elif op==(3 if rev else 2):assert not opened;opened=True;val[temp]=val[x];norm[temp]=norm[x]
    else:assert opened and val[temp]==val[x];opened=False;val[temp]=norm[temp]=0
   assert not opened;stages.append({'stage':s,'provider':pid,'prefix':str(peak)})
  elif e['kind']=='bridge':
   d,s=e['dst'],e['src']
   for a,b in [(2*d,2*s),(2*s+1,2*d+1)]:
    for i in range(120):x,y=a*120+i,b*120+i;val[x]^=val[y];norm[x]+=norm[y];peak=max(peak,norm[x]);units+=1
  else:
   for p in range(5):
    for i in range(120):x,y=2*p*120+i,(2*p+1)*120+i;val[x],val[y]=val[y],val[x];norm[x],norm[y]=norm[y],norm[x]
 assert val==[1<<i for i in range(n)]+[0]
 return {'all9340_columns_restored':True,'prefix':str(peak),'unit_additions_all8':units*8,'stages':stages}
rawscan,signedscan=scan('raw'),scan('signed');prefix=int(g['global_prefix_bound']);assert max(int(rawscan['prefix']),int(signedscan['prefix']))<=prefix<2**192
m,W,physical=78,9600,9609;H={int(k):v for k,v in g['profile'].items()};E=sum(H.values());assert m*W-sum(r*n for r,n in H.items())==3264
J=8*8*11*980+8*9600+2*65120+2*792;high=16*(m*m+1)**2;good=8*m*m+8;compiler=128*(2*m)**3;geo=read(P/'GEOMETRY.json');target=read(P/'TARGET-OPERATOR.json')['extra_route_selector_bound']
selectors=2*11*8*((W-1)+740*m*(geo['max_route_factors']+144+5+(m-1)+m))+target
# In addition to existing +3 whole-pool selectors and dispatch, conservatively
# pay one provider-registry selector per route item and a second dispatch.
registry_selectors=J;dispatch=200000;selectors+=registry_selectors
fixed=dispatch+J*high+J*physical+E*(good+compiler)+16*m**3+792+selectors+1
coef=signedscan['unit_additions_all8']+fixed+prefix;two=(coef+1)**3*(E+1)**3;assert coef<2**192 and two<2**1024
f={'raw_unit_additions':rawscan['unit_additions_all8'],'signed_unit_additions':signedscan['unit_additions_all8'],'charged_prefix':str(prefix),'prefix_bits':prefix.bit_length(),'allowed_prefix_bits':192,'signed_coefficient':str(coef),'coefficient_bits':coef.bit_length(),'signed_three_level_coefficient':str(two),'three_level_bits':two.bit_length(),'charged_three_level_bits':1024,'row_coefficient':19431,'route_items':J,'selector_calls':selectors,'extra_target_route_selector_calls':target,'whole_owner_dispatch':100000,'provider_registry_dispatch':100000,'provider_registry_selector_calls':registry_selectors,'whole_owner_additional_selector_factors':3}
write=lambda p,x:p.write_text(json.dumps(x,indent=2)+'\n');write(P/'local/GLOBAL-BOUND.json',{'status':'PASS_ACTUAL_COMPLETE_CALL_SIGNED_PROVIDER_PORTFOLIO_FINITE_INVOICE','raw':rawscan,'signed':signedscan,'finite':f,'provider_checks':local,'source_inputs':{str(x.resolve()):sha(x)for x in [P/'GLOBAL.json',P/'TARGET-OPERATOR.json',P/'PROVIDERS.json',Path(__file__)]},'scope':'Same conditional full dirty-slot/cover cut and weighted source/target compiler as frozen pooled60. New providers are complete independently signed980/dirt/inverse kernels; record-stream registry authoritative, no grouped-word regeneration. Actual extra registry selector+dispatch paid. All-size C_full/chart/prime/precision/tape/recovery/analytic obligations inherited.'});print(f)
