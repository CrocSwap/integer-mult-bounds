import json,pathlib,subprocess,tempfile,tarfile,io
P=pathlib.Path('/tmp/pr-efficient1300');R=pathlib.Path('/tmp/integer-mult-efficient1100-20261015');head=json.load(open(P/'2348.json'))['headRefOid'];PY='/tmp/pr-efficient200-venv/bin/python'
pkg='research/e8-bit-p111-tuned';v510=pkg+'/vendor/pr510/e8-r480-nine-stage';vk=v510+'/vendor/e8-r715-eleven-stage-whole/code';inv='research/r439-abc-hosted-invoice';script=pkg+'/code/adapt9p.py';missing=vk+'/audit_hosted_k.py'
with tempfile.TemporaryDirectory(prefix='pr2348-adapter-')as td:
 root=pathlib.Path(td)/'root';root.mkdir();paths=[vk,v510+'/code',script,inv+'/invoke.py',inv+'/SOURCES.json']
 raw=subprocess.check_output(['git','archive',head,*paths],cwd=R)
 with tarfile.open(fileobj=io.BytesIO(raw))as t:t.extractall(root,filter='data')
 out=pathlib.Path(td)/'out';out.mkdir();parent=out/'parent'
 subprocess.run([PY,'-I','-B',str(root/v510/'code/adapt.py'),str(root/vk),str(parent)],check=True,capture_output=True)
 reads=out/'reads.json'
 subprocess.run([PY,'-I','-B',str(root/inv/'invoke.py'),str(root),str(reads),str(root/script),str(root/vk),str(root/v510/'code'),str(parent/'audit_parent_k.py'),str(out/'a9p')],check=True,capture_output=True)
 consumed=json.load(open(reads));sources=json.load(open(root/inv/'SOURCES.json'));inputs={r['path']for r in sources['files'] if r['usage']=='input'}
 assert missing in consumed and missing not in inputs
 r={'number':2348,'head':head,'replayed':'Exact pinned parent-adapter and instrumented port-adapter, not the full native pipeline','consumed_but_not_input':sorted(set(consumed)-inputs),'offending_source':missing,'usage':next(r['usage']for r in sources['files'] if r['path']==missing),'finding':'The actual port adapter consumes the demoted auditor source. The full verifier later rejects consumed <= declared inputs even if all native stages pass.'}
 (P/'combined-2348-consumed-input.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
