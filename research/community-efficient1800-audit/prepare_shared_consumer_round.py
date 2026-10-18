from pathlib import Path
import json,subprocess,tarfile,hashlib,shutil
P=Path('/tmp/pr-efficient1800');R=Path('/tmp/integer-mult-efficient1100-20261015');D=P/'shared-frame-consumers';assert not D.exists();shutil.copytree(P/'combined-1861-1922-v3',D,ignore=shutil.ignore_patterns('__pycache__'))
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();pkgs=['cube-xor-replay','disjoint-tensor-frame-unions','ternary-frame-cleared-cache','quadratic-affine-performance','quadratic-affine-packed']
p=subprocess.Popen(['git','archive',head,*['research/'+p for p in pkgs]],cwd=R,stdout=subprocess.PIPE)
with tarfile.open(fileobj=p.stdout,mode='r|') as t:t.extractall(D,filter='data')
assert p.wait()==0
sha=lambda b:hashlib.sha256(b).hexdigest()
def blob(rel):return subprocess.check_output(['git','show',head+':'+rel],cwd=R)
# Supply exact missing source inputs, without overwriting reviewed candidate helpers/certificates.
for pkg in pkgs:
 f=D/'research'/pkg/'SOURCES.json'
 if not f.exists():continue
 m=json.loads(f.read_text());fs=m.get('files',{})
 paths=list(fs) if isinstance(fs,dict) else [x['path'] for x in fs]
 for rel in paths:
  f=D/rel
  if not f.exists():f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(blob(rel))
binary=sha((D/'scripts/binary_phase_frames.py').read_bytes());joint=sha((D/'scripts/audit_joint_frames.py').read_bytes())
f=D/'research/disjoint-tensor-frame-unions/verify.py';s=f.read_text();anchor='        require(restored == base, f"{rel}: changed fields beyond reviewed source pins")';assert anchor in s
new='''        binary = "scripts/binary_phase_frames.py"
        if restored["source_sha256"].get(binary) != base["source_sha256"].get(binary):
            expected = "BINARYHASH"
            require(binary in base["source_sha256"] and
                    restored["source_sha256"].get(binary) == expected,
                    f"{rel}: unreviewed binary-frame companion pin")
            require(sha256((ROOT / binary).read_bytes()).hexdigest() == expected,
                    "binary-frame companion source drift")
            restored["source_sha256"][binary] = base["source_sha256"][binary]
'''.replace('BINARYHASH',binary)
f.write_text(s.replace(anchor,new+anchor))
f=D/'research/disjoint-tensor-frame-unions/VERIFY.json';m=json.loads(f.read_text());m['commands'][0]['checks']+=' Exact reviewed binary_phase_frames companion pin is checked against live bytes; all original payload equality and other pins remain enforced.';f.write_text(json.dumps(m,indent=2)+'\n')
f=D/'tests/test_combined_frame_source_pins.py';s=f.read_text();anchor='            m.check_certificate_pin_discipline()\n            c = Path(t)';assert anchor in s
s=s.replace(anchor,'''            binary = 'scripts/binary_phase_frames.py'
            binary_file = Path(t) / binary
            binary_file.write_bytes((ROOT / binary).read_bytes())
            m.check_certificate_pin_discipline()
            binary_cert = Path(t) / 'certificates/disjoint-tensor-compression.json'
            binary_original = binary_cert.read_bytes()
            bad_binary = json.loads(binary_original)
            bad_binary['source_sha256'][binary] = '0' * 64
            binary_cert.write_text(json.dumps(bad_binary))
            with self.assertRaises(ValueError): m.check_certificate_pin_discipline()
            binary_cert.write_bytes(binary_original)
            binary_file.write_bytes(b'unknown binary helper')
            with self.assertRaises(ValueError): m.check_certificate_pin_discipline()
            binary_file.write_bytes((ROOT / binary).read_bytes())
            c = Path(t)''');f.write_text(s)
# Extend the cube's explicit compatibility overlay, not its frozen scientific manifest.
f=D/'research/cube-xor-replay/COMPATIBILITY.json';m=json.loads(f.read_text());original=json.loads((D/'research/cube-xor-replay/SOURCES.json').read_text())['files']['scripts/audit_joint_frames.py'];data=(D/'scripts/audit_joint_frames.py').read_bytes()
m['files']['scripts/audit_joint_frames.py']=dict(original=original,current=dict(git_blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest(),sha256=joint))
m['extension']=dict(review_baseline=head,pr=1922,author_head=json.loads((P/'1922.json').read_text())['headRefOid'],scope='Maintainer repaired exact rational product, checked in complete normal/optimized supplier replay; cube replay requires complete regression separately.')
m['scope']='Three previously reviewed transitive imports plus explicitly reviewed exact rational-product successor. Original core, row schedule, fixtures and scientific source manifest stay frozen.'
f.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
f2=D/'research/cube-xor-replay/replay.py';s=f2.read_text().replace('a5f102c0b90783698d2912fed9ddeb3a6987fd414fb7c7adffbe638cd98bde7a',sha(f.read_bytes()));a='COMPATIBILITY_PATHS = frozenset(("scripts/audit_fused_block.py",';assert a in s;s=s.replace(a,'COMPATIBILITY_PATHS = frozenset(("scripts/audit_joint_frames.py", "scripts/audit_fused_block.py",');s=s.replace('Only these three transitive','Only these four reviewed').replace('imports use explicitly reviewed current-main bytes','dependencies use explicitly reviewed successor bytes');f2.write_text(s)
# The PR1076 historical replay restores the exact original joint helper.
f=D/'research/quadratic-affine-performance/HISTORICAL-PACKED.json';m=json.loads(f.read_text());m['accepted_live']['scripts/audit_joint_frames.py']=[joint];f.write_text(json.dumps(m,indent=2)+'\n')
(P/'provenance-shared-consumer-round.json').write_text(json.dumps(dict(base=head,binary_sha256=binary,joint_sha256=joint,scope='Candidate consumer integration only; three explicit compatibility changes, original scientific manifests preserved. Not yet admitted.'),indent=2)+'\n')
print('Prepared',D)
