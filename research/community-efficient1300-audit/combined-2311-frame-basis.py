import importlib.util,pathlib,json,hashlib
P=pathlib.Path('/tmp/pr-efficient1300');f=P/'sources/2311/research/pr2265-supplier-admission-audit/verify.py';sp=importlib.util.spec_from_file_location('audit2311',f);a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a)
slots={'transport':(2,3),'add':(4,),'scale':(3,),'swap':(3,),'logical_monomial':(3,),'dual_monomial':(3,),'handoff':(2,3),'dual_handoff':(2,3),'copy':(3,),'clear':(2,),'zero_buffer':(2,),'zero_reframe':(2,)}
def rank(vs):
 b={}
 for v in vs:
  assert type(v)is int and 0<=v<512
  while v:
   k=v.bit_length()
   if k in b:v^=b[k]
   else:b[k]=v;break
 return len(b)
n=0;frames=set()
for orientation in ('forward','backward'):
 t=json.loads(a.blob(a.C2260,'local/data/'+orientation+'.json'))
 for e in t['events']:
  for i in slots[e[0]]:n+=1;frames.add(tuple(e[i]))
 for v in t['endpoints'].values():
  frames.update(tuple(v[k])for k in ('initial','final'))
for v in frames:assert rank(v)==len(v),v
out={'status':'PASS','unique_frames':len(frames),'event_frame_occurrences':n,'scope':'Independent binary elimination verifies all declared basis lists are independent nine-bit vectors, supporting raw-list rank differences in the pinned audit; not a native Clifford or all-size implementation check.','script_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'source_head':a.C2260}
(P/'combined-2311-frame-basis.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
