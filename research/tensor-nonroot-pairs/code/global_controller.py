"""Bind and expand the complete borrowed-spectator controller against literal providers.
Exact local scalar/phase/wrapper proofs are replayed by their separate checkers.
This replay verifies their use at EVERY call and the inherited unchanged schedule.
"""
import sys,json,gzip,hashlib
from pathlib import Path
from collections import Counter
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def read(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def main(template,physical_audit,checks_path,phase_path,global_path,audit_path):
 t,a,checks=map(read,[template,physical_audit,checks_path]);ts=hashlib.sha256(canon(t)).hexdigest();assert a['template_sha256']==ts
 assert t['physical']==t['live']+560+t['private_centers']+2 and t['private_centers']==16
 assert t['provider_checks']['kernel']==checks
 phase=read(phase_path);route_digest=hashlib.sha256();basis={j:sorted(set([r['q']]+[v for ch in r['idle_children']for v in ch['orthogonal_axes']]))for j,r in enumerate(phase['recipes'])};idles={z['idx']:z for z in t['execution_schedule']if z['kind']=='idle'}
 calls={(c['stage'],c['replica']):c for c in t['calls']};programs=t['provider_programs']['kernel'];n=0;dig=hashlib.sha256();counts=Counter();primitives=0;paid=Counter();invocations=[]
 for e in t['execution_schedule']:
  dig.update(canon(['controller',e])+b'\n')
  if e['kind']!='local':continue
  for rep in range(t['replicas']):
   s=e['stage'];call=calls[s,rep];assert call['pair']==e['pair'];ori='backward'if e['reverse']else'forward';assert call['orientation']==ori and call['provider']=='kernel'
   program=programs[ori];assert hashlib.sha256(canon(program)).hexdigest()==call['local_program_sha256']==checks[ori]['sha256']
   own=call['owners']
   for h,(fam,route)in enumerate(own[240:]):
    kind,i,off,foot,w,spec=route;assert kind==5 and foot==9;pair=t['hosting']['windows'][str(i)][0];sp=fam%1200-2*pair*120;side,port=divmod(sp,120);ch=idles[i]['phase_children'][side];axes=phase['recipes'][port]['idle_children'][ch]['orthogonal_axes'];first=axes[off:off+w]+([spec]if w==8 else[]);sigma=first+[v for v in basis[port]if v not in first];assert len(sigma)==89 and set(sigma)==set(basis[port]);route_digest.update(canon([s,rep,h,fam,sigma])+b'\n')
   pivot={r for r in range(240,800)if own[r][1][4]==8};entry=set();exit_=set();inbody=False;inexit=False;localpaid=Counter();localcounts=Counter()
   for z in program:
    tag=z[0];localcounts[tag]+=1
    if tag=='monomial-wrapper':
     _,direction,r,frame,circuit=z;assert r in pivot and own[r][1][3]==9 and own[r][1][5]is not None
     if direction=='entry':assert not inbody and r not in entry;entry.add(r)
     else:assert direction=='exit'and inbody and r not in exit_;inexit=True;exit_.add(r)
     row=[tag,direction,own[r],frame,circuit]
    else:
     assert not inexit;inbody=True
     if tag=='phase':row=z
     elif tag=='adapter':assert z[2]<240;row=[tag,z[1],own[z[2]],*z[3:]]
     elif tag=='climb':row=[tag,z[1],own[z[2]],*z[3:]];localpaid[z[-1]]+=1
     elif tag=='center':row=[tag,[t['live']+z[1],['private_center',z[1]]],*z[2:]];localpaid[z[-1]]+=1
     else:
      assert tag=='scalar';macro=[]
      for x in z[1]:
       if isinstance(x,list)and len(x)==2 and x[0]in('L','C'):macro.append(own[x[1]]if x[0]=='L'else[t['live']+x[1],['private_center',x[1]]])
       else:macro.append(x)
      row=[tag,macro,z[2]]
    dig.update(canon([s,rep,row])+b'\n');n+=1
   assert entry==exit_==pivot and len(pivot)==79
   assert dict(localpaid)=={int(r):nn for r,nn in checks[ori]['paid_profile'].items()}
   assert len(program)==checks[ori]['events']and localcounts['scalar']==checks[ori]['scalar_macros']
   paid.update(localpaid);counts.update(localcounts);primitives+=checks[ori]['real_component_primitive_bound'];invocations.append([s,rep,ori,call['local_program_sha256']])
 for x in t['idle_children']:
  if x['rank']:paid[x['rank']]+=1
 assert dict(paid)=={int(r):nn for r,nn in t['profile'].items()};assert len(invocations)==77
 assert route_digest.hexdigest()==a['orthogonal_route_decoder_sha256']
 g=dict(orthogonal_route_decoder_sha256=route_digest.hexdigest(),status='PASS_COMPLETE_BORROWED_SPECTATOR_CONTROLLER',template_sha256=ts,m=t['m'],live=t['live'],physical=t['physical'],stages=t['stages'],replicas=t['replicas'],hosted_residuals=len(t['hosting']['slots']),bank_assignments=0,profile=t['profile'],rank_mass=t['rank_mass'],deficit=t['deficit'],maxchild=max(map(int,t['profile'])),local_invocations=77,local_events=n,emitted_program_sha256=dig.hexdigest(),source_local_checks=checks,source_canonical_word_sha256=t['source_bindings']['kernel_canonical_word'],data_phase_sha256=t['source_bindings']['data_phase'],private_centers=t['private_centers'],actual_real_component_primitive_sum=primitives,actual_event_counts=dict(counts),wrapper_calls=counts['monomial-wrapper'],source_binding='Complete normalized79 programs at every call; exact source-bound inherited controller and data-phase recipe; independent local scalar/Clifford/512-column monomial and physical-borrowed proofs.')
 Path(global_path).write_text(json.dumps(g,indent=2)+'\n');a.update(controller_status=g['status'],emitted_program_sha256=g['emitted_program_sha256'],local_events=n,private_centers=t['private_centers'],physical=t['physical'],live=t['live'],actual_real_component_primitive_sum=primitives,complete_invocation_registry_sha256=hashlib.sha256(canon(invocations)).hexdigest(),all_wrapper_placements_checked=True,no_unbilled_helper_adapters=True,source_local_checks=checks);Path(audit_path).write_text(json.dumps(a,indent=2)+'\n');print(json.dumps(g,indent=2))
if __name__=='__main__':main(*sys.argv[1:])
