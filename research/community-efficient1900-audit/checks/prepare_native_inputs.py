from pathlib import Path
import json,subprocess,hashlib,importlib.util
P=Path('/tmp/pr-efficient1900');R=Path('/tmp/integer-mult-efficient1100-20261015');spec=importlib.util.spec_from_file_location('package',R/'scripts/research_package.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
objects=Path(subprocess.check_output(['git','rev-parse','--path-format=absolute','--git-common-dir'],cwd=R,text=True).strip())/'objects'
for n in [2874,2877,2882,2888,2902,2905,2907,2912,2916]:
 d=P/'sources'/str(n);pkg=next((d/'research').iterdir());source=json.loads((pkg/'SOURCES.json').read_text());records=[]
 try:
  for row in source['files']:
   if row['usage']!='input':continue
   raw=subprocess.check_output(['git','show','HEAD:'+row['path']],cwd=R,stderr=subprocess.PIPE);assert hashlib.sha256(raw).hexdigest()==row['sha256'],row['path'];f=d/row['path'];f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(raw);records.append(dict(path=row['path'],sha256=row['sha256'],bytes=len(raw)))
  subprocess.run(['git','init','-q'],cwd=d,check=True);(d/'.git/objects/info/alternates').write_text(str(objects)+'\n');m.validate(d,pkg.relative_to(d).as_posix())
  result=dict(status='PASS',number=n,scope='Full registered metadata, Git source SHA/blob/task card pins; every external runtime input exactly matches current main. Vendored exports receive their own source authentication in declared checks.',files=records,validator_sha256=hashlib.sha256((R/'scripts/research_package.py').read_bytes()).hexdigest())
 except Exception as e:result=dict(status='HOLD',number=n,reason=str(e),files=records)
 (P/f'provenance-{n}-metadata.json').write_text(json.dumps(result,indent=2)+'\n');print(n,result['status'],len(records),result.get('reason',''),flush=True)
