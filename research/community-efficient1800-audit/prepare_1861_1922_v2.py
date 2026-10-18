from pathlib import Path
import json,subprocess,tarfile,hashlib,shutil
P=Path('/tmp/pr-efficient1800');R=Path('/tmp/integer-mult-efficient1100-20261015');D=P/'combined-1861-1922-v2';old=P/'combined-1861-1922';assert not D.exists();D.mkdir()
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
proc=subprocess.Popen(['git','archive',head,'scripts','tests','certificates','upstream','docs/research/parity-side.md','docs/research/positive-side-core.md','docs/research/rank-product-core.md'],cwd=R,stdout=subprocess.PIPE)
with tarfile.open(fileobj=proc.stdout,mode='r|') as t:t.extractall(D,filter='data')
assert proc.wait()==0
for n,pkg,helper,test in [(1861,'parity-side-basis-cache','binary_phase_frames.py','test_parity_side_basis_cache.py'),(1922,'joint-frames-cleared-product','audit_joint_frames.py','test_joint_frames_cleared_product.py')]:
 shutil.copytree(old/'research'/pkg,D/'research'/pkg)
 for rel in ['scripts/'+helper,'tests/'+test]:shutil.copy2(old/rel,D/rel)
subprocess.run(['git','init','-q',str(D)],check=True);obj=(R/subprocess.check_output(['git','rev-parse','--git-path','objects'],cwd=R,text=True).strip()).resolve();(D/'.git/objects/info/alternates').write_text(str(obj)+'\n');(D/'.git/HEAD').write_text(head+'\n')
sha=lambda b:hashlib.sha256(b).hexdigest()
for n,pkg,helper,certs in [(1861,'parity-side-basis-cache','binary_phase_frames.py',['parity-side','disjoint-tensor-compression','dyadic-central-factor']),(1922,'joint-frames-cleared-product','audit_joint_frames.py',['rank-product-core'])]:
 binding={}
 for name in certs:
  rel='certificates/'+name+'.json';f=D/rel;raw=f.read_bytes();binding[rel]=sha(raw);d=json.loads(raw)
  original=d['source_sha256']['scripts/'+helper];new=sha((D/'scripts'/helper).read_bytes())
  # Text-only pin replacement preserves current companion pins and all other bytes.
  assert raw.count(original.encode())==1
  f.write_bytes(raw.replace(original.encode(),new.encode()))
 f=D/'research'/pkg/'verify.py';s=f.read_text();anchor='PINNED_CERTS = (';i=s.index(anchor)
 s=s[:i]+'INTEGRATION_BASE_COMMIT = '+repr(head)+'\nINTEGRATION_CERT_SHA256 = '+repr(binding)+'\n'+s[i:]
 a='''        require(restored == base, f"{rel}: changed fields beyond the '''+('binary_phase_frames' if n==1861 else 'audit_joint_frames')+''' pin")'''
 b='''        integration_raw = subprocess.check_output(["git", "show", f"{INTEGRATION_BASE_COMMIT}:{rel}"], cwd=ROOT)
        require(sha256(integration_raw).hexdigest() == INTEGRATION_CERT_SHA256[rel], f"{rel}: integration snapshot changed")
        integration = json.loads(integration_raw)
        require(restored == integration, f"{rel}: changed fields beyond the reviewed current source pin")
        require({k:v for k,v in base.items() if k != "source_sha256"} ==
                {k:v for k,v in integration.items() if k != "source_sha256"},
                f"{rel}: mathematical payload differs from author baseline")'''
 assert a in s;s=s.replace(a,b);f.write_text(s)
 f=D/'research'/pkg/'README.md';f.write_text(f.read_text()+'''\nThe integration preserves the newer main-branch companion source pins. The\nchecker authenticates both the original author baseline and the exact reviewed\nintegration commit, requires identical mathematical payloads, and permits only\nthis PR's helper pin to differ from that current snapshot. Historical timing\nreceipts and original baseline files remain unchanged.\n''')
(P/'provenance-1861-1922-v2.json').write_text(json.dumps(dict(base=head,scope='Current scripts/tests/certificates plus reviewed candidate API and nonvacuity fixes; preserve companion pins and authenticate both historical and integration baselines.'),indent=2)+'\n')
print('Prepared v2',head)
