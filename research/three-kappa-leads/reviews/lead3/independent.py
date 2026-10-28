from pathlib import Path
from fractions import Fraction as F
import tarfile,gzip,json,hashlib,subprocess
R=Path('/Users/temp/.codex/worktrees/three-kappa-leads/integer-mult-bounds')
sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
with tarfile.open(R/'research/community-frontier1094-audit/selected-replay.tar.gz') as tf:
 def get(n):return json.loads(gzip.decompress(tf.extractfile('candidate/strict/global/base/split-centres/'+n).read()))
 events=get('LOCAL-PROGRAMS.json.gz')['forward']
 data=json.loads(tf.extractfile('candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json').read())
labels=[r['q'] for r in sorted(data['recipes'],key=lambda r:r['port'])]
candidate=json.loads((R/'research/five-plane-port-p112-seed1f7fdfe4/CANDIDATE.json').read_text())['candidate']
blocks=candidate['blocks'];assert sorted(sum(blocks,[]))==list(range(112))
deltas=[]
for b in blocks:
 d=0
 for p in b:d^=labels[p]
 deltas.append(d)
assert deltas[:2]==[98,70]
assert events[13062]==['scalar',['add',['L',112],['C',0],1,4],0]
assert events[13074]==['scalar',['clear',['C',0]],0]
assert events[13076]==['scalar',['copy',['C',1],['L',224]],415]
def X(v,d):return [v[i^d] for i in range(512)]
def add(d,h):return [a+b/4 for a,b in zip(d,h)]
# Independent dense vectors: all source basis vectors; arbitrary dense dirty targets.
dirty=[F((i*17)%31-15,7) for i in range(512)]
for a in range(512):
 h=[F(0)]*512;h[a]=F(1)
 shifted=h[:]
 first=None
 for delta in deltas:
  shifted=X(shifted,delta)
  if first is None:first=add(dirty,shifted)
 assert shifted==h and first!=add(dirty,h)
 assert X(add(X(dirty,98),X(h,98)),98)==add(dirty,h)
# Target-only basis directions are restored by matched translation for zero source;
# together with source directions this checks the full 1024-dimensional block map.
for a in range(512):
 d=[F(0)]*512;d[a]=F(1);z=[F(0)]*512
 assert X(add(X(d,98),X(z,98)),98)==d
# Exact dense source with several values and dirty output detects omission of target pretranslation.
h=[F((i*11)%23-11,13) for i in range(512)]
assert X(add(dirty,X(h,98)),98)!=add(dirty,h)
assert X(add(X(dirty,98),X(h,98)),98)==add(dirty,h)
report={'reviewed_head':sha,'source_basis_dirty_dense_cases':512,'target_basis_cases':512,'all23_final_scratch_restores':True,'first_consumer_fails':True,'matched_translation_restoration_passes':True,'target_posttranslation_only_fails':True,'deltas':deltas,'first_event':events[13062],'scope':'conditional unchanged ZERO consumer splice, not native five-plane route'}
Path('/tmp/three-kappa-astra-lead3/RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
