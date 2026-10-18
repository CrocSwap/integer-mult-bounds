import pathlib,json,sys,subprocess,tempfile,hashlib
P=pathlib.Path('/tmp/pr-efficient1800');root=P/'sources/1926';pkg=root/'research/unittest-receipt-comparison';R='/tmp/integer-mult-efficient1100-20261015';sys.path.insert(0,str(pkg));import adapter
pins=json.loads((pkg/'SOURCES.json').read_text());bindings=[]
for r in pins['files']:
 raw=subprocess.check_output(['git','show',pins['base_commit']+':'+r['path']],cwd=R);assert hashlib.sha256(raw).hexdigest()==r['sha256'];assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==r['git_blob'];bindings.append(r)
assert adapter.check_sources(root)
with tempfile.TemporaryDirectory() as tmp:
 current=pathlib.Path(tmp)
 for name in adapter.INPUTS:
  f=current/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(subprocess.check_output(['git','show','HEAD:'+name],cwd=R))
 try:adapter.check_sources(current)
 except ValueError as e:assert str(e)=='source drift: scripts/run_isolated_tests.py';failure=str(e)
 else:raise AssertionError('current runner unexpectedly admitted')
print('PASS_RECEIPT_SOURCE_PROBE original_inputs=pass current_main='+failure)
(P/'finding-1926-source-drift.json').write_text(json.dumps(dict(number=1926,head=json.loads((P/'1926.json').read_text())['headRefOid'],main=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),bindings=bindings,original_positive_control=True,current_main_rejected=failure,scope='Source-binding compatibility failure, not a defect in the byte comparator; complete execution and historical-source migration remain required.'),indent=2)+'\n')
