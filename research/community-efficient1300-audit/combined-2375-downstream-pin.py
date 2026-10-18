import pathlib,subprocess,json,tempfile,hashlib,importlib.util
P=pathlib.Path('/tmp/pr-efficient1300');R=pathlib.Path('/tmp/integer-mult-efficient1100-20261015');head=json.load(open(P/'2375.json'))['headRefOid'];pkg='research/p25-root-pair-bound-seed632639';target='research/complex-frame-pair-decoders/verify.py'
def blob(ref):return subprocess.check_output(['git','show',ref],cwd=R)
manifest=json.loads(blob('HEAD:'+pkg+'/SOURCES.json'));base=manifest['base_commit'];prod=blob(head+':'+target)
with tempfile.TemporaryDirectory(prefix='pr2375-consumer-')as td:
 root=pathlib.Path(td)
 for row in manifest['files']:
  b=blob(row['git_blob']);assert hashlib.sha256(b).hexdigest()==row['sha256'];f=root/row.get('snapshot_path',row['path']);f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
 for name in ('verify.py','SOURCES.json'):
  f=root/pkg/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(blob('HEAD:'+pkg+'/'+name))
 subprocess.run(['git','init','-q',str(root)],check=True)
 obj=(R/subprocess.check_output(['git','rev-parse','--git-path','objects'],cwd=R,text=True).strip()).resolve();(root/'.git/objects/info/alternates').write_text(str(obj)+'\n')
 sp=importlib.util.spec_from_file_location('consumer2375',root/pkg/'verify.py');v=importlib.util.module_from_spec(sp);sp.loader.exec_module(v);v.check_pins()
 (root/target).write_bytes(prod)
 try:v.check_pins()
 except ValueError as e:failure=str(e)
 else:raise RuntimeError('Expected actual source pin failure')
 assert failure=='working input SHA drift: '+target
 out={'number':2375,'head':head,'consumer':pkg+'/verify.py:check_pins','baseline':'PASS complete source check','production_failure':failure,'new_sha256':hashlib.sha256(prod).hexdigest(),'scope':'Actual downstream pin check with unchanged historical inputs. A full census is unnecessary to establish this integration incompatibility. Newly integrated cycle47 also retains a live input pin to the same original model.'};(P/'combined-2375-downstream-pin.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
