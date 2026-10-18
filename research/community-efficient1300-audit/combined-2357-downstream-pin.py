import pathlib,subprocess,json,tarfile,io,tempfile,hashlib,importlib.util
P=pathlib.Path('/tmp/pr-efficient1300');R=pathlib.Path('/tmp/integer-mult-efficient1100-20261015');head=json.load(open(P/'2357.json'))['headRefOid'];pkg='research/complex-ck-target-forest';source='research/complex-k492-owner-repair/code/hpe_audit_local.py'
def blob(path):return subprocess.check_output(['git','show',head+':'+path],cwd=R)
manifest=json.loads(blob(pkg+'/SOURCES.json'))
with tempfile.TemporaryDirectory(prefix='pr2357-consumer-')as td:
 root=pathlib.Path(td);paths=[pkg+'/verify.py',pkg+'/SOURCES.json',*manifest['files']]
 raw=subprocess.check_output(['git','archive',head,*paths],cwd=R)
 with tarfile.open(fileobj=io.BytesIO(raw))as t:t.extractall(root,filter='data')
 spec=importlib.util.spec_from_file_location('pr2357_consumer',root/pkg/'verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
 try:v.check_sources()
 except ValueError as e:failure=str(e)
 else:raise RuntimeError('Expected actual stale input rejection')
 assert failure=='source pin: '+source
 production=(root/source).read_bytes();baseline=subprocess.check_output(['git','show','0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2:'+source],cwd=R);(root/source).write_bytes(baseline)
 v.check_sources()
 result={'number':2357,'head':head,'consumer':pkg+'/verify.py:check_sources','new_source_failure':failure,'original_source_positive_control':'PASS complete source check including bound geometry/programs','expected_sha256':manifest['files'][source]['sha256'],'new_sha256':hashlib.sha256(production).hexdigest(),'scope':'Exact downstream source check, not a full target-forest circuit replay. Additional live-bound consumers need a coordinated migration.'}
 (P/'combined-2357-downstream-pin.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
