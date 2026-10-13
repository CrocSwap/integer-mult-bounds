from pathlib import Path
import importlib.util,json,gzip,copy
root=Path(__file__).resolve().parents[2]; spec=importlib.util.spec_from_file_location('audit806',root/'research/pr695-digest-audit/verify.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
import tempfile,tarfile
_tmp=tempfile.TemporaryDirectory();base=Path(_tmp.name).resolve()
with tarfile.open(Path(__file__).with_name('pr806-historical-inputs.tar.gz')) as archive:
 for member in archive:
  dest=(base/member.name).resolve()
  if not member.isfile() or not dest.is_relative_to(base):raise ValueError('Invalid fixture member')
  dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(archive.extractfile(member).read())
mixed=base/'mixed-global'
names=['hosted/GLOBAL-TEMPLATE.json.gz','hosted/HOSTED.json','PLAN.json','audit/ASYNC-AUDIT.json','audit/OWNERS-AND-PROFILE.json','audit/PREFIX-AND-INVOICE.json']+[f'base/providers/{p}/{n}' for p in m.PROVIDERS for n in m.TIMED]
original={n:(mixed/n).read_bytes() for n in names};original['ASSEMBLY.json']=(base/'ASSEMBLY.json').read_bytes()
committed={n:b for n,b in original.items() if n=='ASSEMBLY.json' or n.startswith(('hosted/HOSTED','audit/'))}
def generate(semantic_change=False):
 local=copy.deepcopy(original);table={}
 for p in m.PROVIDERS:
  for n in m.TIMED:
   key=f'base/providers/{p}/{n}';obj=json.loads(local[key]);obj['seconds']+=0.125
   if semantic_change and n=='SCALAR-FRAME-AUDIT.json':obj['unverified_non_timing_change']=True
   new=(json.dumps(obj,indent=2)+'\n').encode();table[m.digest(local[key])]=m.digest(new);local[key]=new
 local['PLAN.json']=m.substitute(local['PLAN.json'],table)
 raw=gzip.decompress(local['hosted/GLOBAL-TEMPLATE.json.gz']);template=json.loads(raw)
 template['async_schedule']['source_plan_sha256']=m.digest(local['PLAN.json'].replace(b'\r\n',b'\n'))
 new=json.dumps(template,sort_keys=True,separators=(',',':')).encode();table[m.digest(raw)]=m.digest(new);local['hosted/GLOBAL-TEMPLATE.json.gz']=gzip.compress(new,mtime=0)
 for name in ['audit/ASYNC-AUDIT.json','audit/OWNERS-AND-PROFILE.json','hosted/HOSTED.json']:
  new=m.substitute(local[name],table);table[m.digest(local[name])]=m.digest(new);local[name]=new
 name='audit/PREFIX-AND-INVOICE.json';obj=json.loads(m.substitute(local[name],table))
 for p in m.PROVIDERS:obj['providers'][p]['artifacts']=dict(reversed(list(obj['providers'][p]['artifacts'].items())))
 new=(json.dumps(obj,indent=2)+'\n').encode();table[m.digest(local[name])]=m.digest(new);local[name]=new
 local['ASSEMBLY.json']=m.substitute(local['ASSEMBLY.json'],table)
 return local
local=generate();report=m.explain(local,committed);report['rejection_controls']=m.controls(local,committed)
report['test_kind']='Controlled recomputation from the historical raw replay; not a fresh construction or reproduction of unavailable CI payloads'
report['semantic_change_control_accepted']=m.explain(generate(True),committed)['status'].startswith('PASS')
report['finding']='Whole-file hash substitution is not proof that only timing changed. Non-timing SCALAR-FRAME-AUDIT mutations can pass if their digest is propagated consistently.'
print(json.dumps(report,indent=2))
