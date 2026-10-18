"""Independent exact mixed-call owner, actual windows and 73-axis chart check.
Standard-library only; frozen local semantic admission remains explicit.
"""
import argparse,collections,hashlib,importlib.util,json,time
from pathlib import Path
spec=importlib.util.spec_from_file_location('owner_core',Path(__file__).with_name('audit_owner_table.py'))
O=importlib.util.module_from_spec(spec);spec.loader.exec_module(O)

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

def run(package,owners,dispatch,old_native,new_native,canonical,phases,parent,variants=None):
 P=O.read(package/'data/PLAN.json');S=O.read(package/'data/SPEC.json');rows=O.read(owners);D=O.read(dispatch)
 ow,op,oldr=local_contract(old_native,S['providers']['gauge44']['complete_contract'])
 O.need(ow==S['providers']['gauge44']['complete_contract']['widths'],'actual old widths contract')
 O.need(op=={int(k):v for k,v in S['providers']['gauge44']['expected_profile'].items()},'actual old local profile')
 group_order=[[411,413,414,415],[379,381,382,383],[387,389,390,391],[395,397,398,399],[403,405,406,407]]
 contracts={};dirs=dict(variants or {});dirs.setdefault(1,new_native)
 selected={d.get('variant',1) for d in D}
 O.need(selected<=set(dirs),'missing actual native variant')
 for k in sorted(selected):
  O.need(type(k) is int and 1<=k<=5,'invalid variant')
  nw,np,nr=local_contract(dirs[k]);expected=sum(group_order[:k],[])
  O.need(sorted(i for i,(a,b) in enumerate(zip(ow,nw)) if a!=b)==sorted(expected),'exact changed helpers')
  O.need(all(nw[i]==ow[i]+1 for i in expected),'exact widened helpers')
  delta=collections.Counter(np);delta.subtract(op)
  O.need({j:v for j,v in delta.items() if v}=={1:-8*k,2:8*k,3:4*k,4:-4*k},'exact joint demotion local delta')
  O.need(sum(op.values())==sum(np.values()),'same local child count')
  contracts[k]=(nw,np,nr)
 wc={};pc={};seen=set();variant_counts=collections.Counter()
 for d in D:
  c=tuple(d['call']);O.need(c not in seen and P['order'][d['time']]==list(c),'literal dispatch time');seen.add(c);k=d.get('variant',1)
  O.need(d['helpers']==sum(group_order[:k],[]),'literal changed helpers')
  wc[c],pc[c],_=contracts[k];variant_counts[k]+=1
 result=O.verify(rows,P,S,O.read(canonical),O.read(phases),widths_by_call=wc,profiles_by_call=pc,parent=O.read(parent))
 result['mixed_calls']=len(D);result['default_calls']=144-len(D)
 result['source_event_windows']='fresh reconstruction from source_schedule and actual phase-axis ranks'
 result['local_contracts']='fresh complete frame profiles and widths on both canonical words; changed-word scalar receipt freshly bound; unchanged old scalar admission inherited'
 result['variant_counts']=dict(sorted(variant_counts.items()))
 result['local_prefix_bits']={o:max([oldr['local'][o]['prefix_bits_upper']]+[z[2]['local'][o]['prefix_bits_upper'] for z in contracts.values()]) for o in ('forward','backward')}
 result['local_contract_count']=1+len(contracts)
 return result,(rows,P,S,O.read(canonical),O.read(phases),wc,pc,O.read(parent))

def negative_controls(context):
 import copy
 rows,plan,spec,canon,ph,wc,pc,parent=context
 tests=[]
 def reject(name,r=None,p=None,h=None,override=None,widths=None):
  try:O.verify(rows if r is None else r,plan if p is None else p,spec,canon,ph if h is None else h,override=override,widths_by_call=wc if widths is None else widths,profiles_by_call=pc,parent=parent)
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
 p=copy.deepcopy(plan);p['windows'][next(iter(p['windows']))][1].append(143);reject('tampered_source_event_window',p=p)
 r=rows.copy();r[0]=dict(r[0],family=14336);reject('private_namespace_or_family_identity',r)
 reject('forgot_widened_dispatch',widths={})
 h=copy.deepcopy(ph);h['recipes'][0]['idle_children'][0]['orthogonal_axes'].pop();reject('incorrect_phase_rank',h=h)
 return tests

def main():
 a=argparse.ArgumentParser()
 for k in ('package','owners','dispatch','old-native','new-native','canonical','phases','parent','out'):a.add_argument('--'+k,type=Path,required=True)
 a.add_argument('--controls',action='store_true');a.add_argument('--variant',action='append',default=[],help='K=actual-native-directory')
 z=a.parse_args();O.need(not z.out.exists(),'fresh output required');t=time.monotonic();variants={int(x.split('=',1)[0]):Path(x.split('=',1)[1]) for x in z.variant}
 result,context=run(z.package,z.owners,z.dispatch,z.old_native,z.new_native,z.canonical,z.phases,z.parent,variants=variants)
 if z.controls:result['negative_controls']=negative_controls(context)
 charts=result.pop('sigmas');remainders=result.pop('remainders')
 import gzip
 for suffix,data in [('SIGMAS',charts),('REMAINDERS',remainders)]:z.out.with_name(z.out.stem+'-'+suffix+'.json.gz').write_bytes(gzip.compress(json.dumps(data,sort_keys=True,separators=(',',':')).encode(),mtime=0))
 result.update(status='PASS_ACTUAL_MIXED_OWNER_WINDOWS_CHARTS_PROFILE',seconds=time.monotonic()-t,inputs={str(p):O.sha(p) for p in [z.package/'data/PLAN.json',z.package/'data/SPEC.json',z.owners,z.dispatch,z.canonical,z.phases,z.parent,z.old_native/'CANONICAL-WORD.json.gz',z.new_native/'CANONICAL-WORD.json.gz']})
 z.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({k:v for k,v in result.items() if k!='inputs'},indent=2))
if __name__=='__main__':main()
