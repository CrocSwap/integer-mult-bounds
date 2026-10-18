"""Fresh T-variable literal candidate owner/event/chart audit; no background work."""
import argparse,collections,copy,gzip,hashlib,importlib.util,json,time
from pathlib import Path
s=importlib.util.spec_from_file_location('owners',Path(__file__).with_name('audit_owner_table.py'));O=importlib.util.module_from_spec(s);s.loader.exec_module(O)
def basis(vs):
 d={}
 for x in vs:
  O.need(type(x) is int and 0<=x<512,'invalid local frame')
  while x:
   p=x.bit_length()-1
   if p in d:x^=d[p]
   else:d[p]=x;break
 return tuple(d[k] for k in sorted(d,reverse=True))

def local_contract(native,inherited=None):
 w=O.read(native/'CANONICAL-WORD.json.gz')
 if inherited is None:
  r=O.read(native/'INDEPENDENT-LOCAL-REPLAY.json')
  O.need(O.sha(native/'CANONICAL-WORD.json.gz')==r['canonical_word_sha256'],'local canonical binding')
  O.need(O.sha(native/'LOCAL-PROGRAMS.json.gz')==r['local_programs_sha256'],'local program binding')
 else:
  r=dict(paid_profiles={o:inherited['paid_profile'] for o in ('forward','backward')},local={o:dict(prefix_bits_upper=inherited['local'][o]['prefix_bits']) for o in ('forward','backward')},scope='old scalar semantic admission inherited; frame profile and width freshly recounted')
 F=[basis(x) for x in w['frames']];now=[F[i] for i in w['start']];paid=collections.Counter()
 def climb(q,to):
  O.need(len(basis(now[q]+to))==len(to),'local nonmonotone frame')
  jump=len(to)-len(now[q]);O.need(jump>=0,'negative local jump')
  if jump:paid[jump]+=1
  now[q]=to
 O.need(not w['target_levels'],'zero target centre interface')
 for sec in ('A','B','tail'):
  if sec=='B':
   O.need(all(not now[q] for q in range(w['v'],2*w['v'])),'target level interface')
   for q,fi in zip(w['centers'],w['center_frames']):O.need(now[q]==F[fi],'centre frame');paid[len(F[fi])]+=1
  for gate in w[sec]:
   O.need(gate[0] in ('add','scale'),'local scalar gate')
   for q in (gate[1:3] if gate[0]=='add' else gate[1:2]):climb(q,F[gate[-1]])
 for q,fi in enumerate(w['final']):climb(q,F[fi])
 O.need(dict(paid)=={int(k):v for k,v in w['local_profile'].items()},'complete local profile recount')
 for orientation in ('forward','backward'):O.need(dict(paid)=={int(k):v for k,v in r['paid_profiles'][orientation].items()},'native local profile binding')
 widths=[len(F[w['final'][q]])-len(F[w['start'][q]]) for q in range(2*w['v'],len(w['start']))]
 O.need(len(widths)==480 and all(0<v<=9 for v in widths),'actual local widths')
 return widths,dict(paid),r


def audit(plan,source_spec,rows,canonical,phases,parent,native=None,variants=None,dispatch=None,inherited_native=None):
 # The source SPEC supplies the inherited local scalar interface. Its old geometry
 # is never relabeled as a proof of a new replica count or owner table.
 S=copy.deepcopy(source_spec);T=plan['T'];nc=9*T
 S['call_order']=plan['order'];S['expected']['rank_mass']=65088*T
 if native is None:
  default_widths=S['providers']['gauge44']['complete_contract']['widths']
  default_profile={int(k):v for k,v in S['providers']['gauge44']['expected_profile'].items()}
  default_receipt=None;scope='local scalar admission inherited from exact source SPEC'
  if inherited_native is not None:
   actual_widths,actual_profile,_=local_contract(inherited_native,inherited=S['providers']['gauge44']['complete_contract'])
   O.need(actual_widths==default_widths and actual_profile==default_profile,'actual inherited-default canonical widths/profile')
   scope='default actual canonical frames/width/profile freshly recounted; unchanged scalar semantics inherited from exact source SPEC'
 else:
  default_widths,default_profile,default_receipt=local_contract(native)
  S['providers']['gauge44']['complete_contract']['widths']=default_widths
  S['providers']['gauge44']['expected_profile']=default_profile
  scope='default actual native words source-bound to fresh receipt; changed width/profile derived exactly'
 wc={};pc={};contracts={};seen=set();variant_counts=collections.Counter()
 for k,d in (variants or {}).items():contracts[k]=local_contract(d)
 for d in (dispatch or []):
  c=tuple(d['call']);k=d['variant'];O.need(c not in seen and plan['order'][d['time']]==list(c),'literal dispatch time');seen.add(c)
  O.need(k in contracts,'missing actual admitted variant')
  vw,vp,_=contracts[k];changed=sorted(i for i,(a,b) in enumerate(zip(default_widths,vw)) if a!=b)
  O.need(sorted(d['helpers'])==changed and len(set(d['helpers']))==len(d['helpers']),'exact dispatched helper-width changes')
  O.need(all(vw[i]==default_widths[i]+1 for i in changed),'literal one-axis widening')
  wc[c],pc[c]=vw,vp;variant_counts[k]+=1
 z=O.verify(rows,plan,S,canonical,phases,widths_by_call=wc,profiles_by_call=pc,parent=parent)
 O.need(z['profile']=={int(k):v for k,v in plan['profile'].items()},'nomination complete profile')
 z.update(status='PASS_FRESH_LITERAL_CANDIDATE_OWNER_TIMELINE_CHARTS',replicas=T,mixed_calls=len(dispatch or []),default_calls=nc-len(dispatch or []),variant_counts=dict(variant_counts),local_admission=scope,geometry='Fresh actual source-event reconstruction, phase-axis capacities, all pending tensor factors and all actual 73-column charts; no inherited changed-map receipt')
 return z,(rows,plan,S,canonical,phases,wc,pc,parent)

def mutations(ctx):
 rows,plan,spec,canon,ph,wc,pc,parent=ctx;tests=[]
 def reject(name,rr=None,pp=None,hh=None,override=None,widths=None):
  try:O.verify(rows if rr is None else rr,plan if pp is None else pp,spec,canon,ph if hh is None else hh,override=override,widths_by_call=wc if widths is None else widths,profiles_by_call=pc,parent=parent)
  except RuntimeError as e:tests.append(dict(name=name,rejected=str(e)));return
  raise RuntimeError('accepted mutation '+name)
 r=rows.copy();r[1]=dict(r[0]);reject('duplicate_role',r)
 r=rows.copy();r[0]=dict(r[0],width=r[0]['width']+1);reject('wrong_actual_width',r)
 r=rows.copy();r[0]=dict(r[0],time=r[0]['time']+1);reject('wrong_call_time',r)
 r=rows.copy();r[0]=dict(r[0],offset=-1);reject('negative_axis_offset',r)
 r=rows.copy();r[1]=dict(r[1]);
 for key in ['owner_replica','child','port','copy','family','offset']:r[1][key]=r[0][key]
 reject('per_call_family_alias',r)
 r=rows.copy();r[0]=dict(r[0],owner_replica=0,child=5,port=rows[0]['port'],copy=rows[0]['port'],family=(2*plan['pairs']['5']+plan['sides']['5'])*112+rows[0]['port'],offset=0);reject('out_of_window',r)
 reject('wrong_73_axis_chart',override={0:O.idle_basis(canon['ports'][rows[0]['port']])[::-1]})
 p=copy.deepcopy(plan);key=next(iter(p['windows']));p['windows'][key][1].append(9*plan['T']-1);reject('tampered_source_event_window',pp=p)
 r=rows.copy();r[0]=dict(r[0],family=896*plan['T']);reject('private_namespace_or_family_identity',r)
 h=copy.deepcopy(ph);h['recipes'][0]['idle_children'][0]['orthogonal_axes'].pop();reject('incorrect_phase_rank',hh=h)
 if wc:reject('forgot_actual_widened_dispatch',widths={})
 return tests

def main():
 a=argparse.ArgumentParser()
 for k in ('plan','spec','owners','canonical','phases','parent','out'):a.add_argument('--'+k,type=Path,required=True)
 a.add_argument('--native',type=Path);a.add_argument('--inherited-native',type=Path);a.add_argument('--dispatch',type=Path);a.add_argument('--variant',action='append',default=[]);a.add_argument('--controls',action='store_true');z=a.parse_args()
 O.need(not z.out.exists(),'fresh output required');t=time.monotonic()
 r,ctx=audit(O.read(z.plan),O.read(z.spec),O.read(z.owners),O.read(z.canonical),O.read(z.phases),O.read(z.parent),native=z.native,variants={int(x.split('=',1)[0]):Path(x.split('=',1)[1]) for x in z.variant},dispatch=O.read(z.dispatch) if z.dispatch else None,inherited_native=z.inherited_native)
 if z.controls:r['negative_controls']=mutations(ctx)
 for label,key in [('SIGMAS','sigmas'),('REMAINDERS','remainders')]:z.out.with_name(z.out.stem+'-'+label+'.json.gz').write_bytes(gzip.compress(json.dumps(r.pop(key),sort_keys=True,separators=(',',':')).encode(),mtime=0))
 r.update(seconds=time.monotonic()-t,inputs={k:O.sha(getattr(z,k)) for k in ('plan','spec','owners','canonical','phases','parent')})
 z.out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
