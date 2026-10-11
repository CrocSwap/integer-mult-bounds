"""Pinned PR402 design constructor with an explicit exact histogram callback.
The two target/donor witnesses are frozen; no search runs during reconstruction.
Prepared with OpenAI Codex assistance; source redesign remains credited to PR402.
"""
from pathlib import Path
from hashlib import sha256,sha1
import copy,importlib.util,json,types
HERE=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_bytes())
digest=lambda p:sha256(Path(p).read_bytes()).hexdigest()
def apply(source404,input_path,output):
 source404,input_path,output=map(Path,(source404,input_path,output));assert not output.exists()
 pins=read(HERE/'pr402-source.json')
 for name,pin in pins['files'].items():
  raw=(HERE/name).read_bytes();assert sha256(raw).hexdigest()==pin['sha256']
  assert sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob']
 assert digest(HERE/'designs.json')==pins['designs_sha256']
 assert digest(input_path)=='feb95ec8f4068337b066b6208a60752199015fddedd2992bd7f76ba35ea3f0c5'
 s=importlib.util.spec_from_file_location('shared404_frames',source404/'frames/reconstruct.py');math=importlib.util.module_from_spec(s);s.loader.exec_module(math)
 text=(HERE/'pr402-redesign.py').read_text();old='from cxkernel import rehist';assert text.count(old)==1
 changed=text.replace(old,'rehist = _audited_rehist')
 def rehist(c):math.rehist_and_audit(c);return c
 module=types.ModuleType('pinned402_design');module.__file__=str(HERE/'pr402-redesign.py');module._audited_rehist=rehist
 exec(compile(changed,str(HERE/'pr402-redesign.py'),'exec'),module.__dict__)
 c=read(input_path);d=module.build(c,module.from_json(read(HERE/'designs.json')))
 assert math.replay(c)==math.replay(d)
 assert all(c[k]==d[k]for k in c if k not in ['B','blocks','N'])and c['N']==d['N']
 trans=math.rehist_and_audit(d);blob=json.dumps(d,sort_keys=True,separators=(',',':')).encode()
 assert sha256(blob).hexdigest()=='3ced59a749d2e61e6a540e423af7bcd1abfef602606f883de99fb83faa61022c'
 output.mkdir(parents=True);(output/'candidate.json').write_bytes(blob)
 expected=math.replay(d);controls=[]
 for target in [177,220]:
  for kind,frame,source,coefficient in [('omit_setup',0,221,-1),('omit_restore',892,221,1),('flip_delivery',892,801,-1)]:
   bad=copy.deepcopy(d);hits=[i for i,g in enumerate(bad['B'])if g[0]=='in'and g[1]==frame and g[2]==target and len(g[3])==1 and g[3][0][0]==source and g[3][0][1]==coefficient];assert len(hits)==1
   if kind.startswith('omit'):bad['B'].pop(hits[0])
   else:bad['B'][hits[0]][3][0][1]*=-1
   changed_map=math.replay(bad);assert changed_map!=expected
   controls.append(dict(target=target,mutation=kind,rejected=True,changed_rows=sum(a!=b for a,b in zip(changed_map,expected))))
 a=math.histogram(c);b=math.histogram(d)
 receipt=dict(status='PASS_PINNED_PR402_TWO_TARGET_RESYNTHESIS_WITH_EXACT_404_AUDIT',source_sha256=digest(input_path),candidate_sha256=sha256(blob).hexdigest(),source402_commit=pins['commit'],
  redesign_native_sha256=digest(HERE/'pr402-redesign.py'),redesign_adapted_sha256=sha256(changed.encode()).hexdigest(),
  literal_substitution=dict(old=old,new='rehist = _audited_rehist',count=1),designs_sha256=digest(HERE/'designs.json'),
  targets=[177,220],donor=221,mutation_controls=controls,all_raw_columns=1021,nested_transitions=trans,histogram_delta={r:b[r]-a[r]for r in a.keys()|b.keys()if b[r]!=a[r]},
  scope='Exact source-bound constructor and full rational raw operator. Strong dirty scalar, Gaussian phase, owners/banks, invoices, signed-bit and outer admission remain separate mandatory checks; inherited conditional obligations remain.')
 (output/'RECEIPT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');return receipt
