"""Record inherited inputs only after comparison with the pinned Git source."""
from hashlib import sha1,sha256
import json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
HEAD='f626db5c3a3d781d8f7695038776c621651f75e1'
PATHS=[
'research/joint-helper-lattice/native_joint.py','research/joint-helper-lattice/PATCH.json','research/joint-helper-lattice/NATIVE.json.gz',
'research/fresh-helper-boundary/native.py','research/fresh-helper-boundary/CHANGES.json','research/missing-join-frame/PATCH.json',
'research/kappa-rebuild/complex/full-identity-certificates/THREE-base-FULL-IDENTITY-CANONICAL.json.gz',
'research/kappa-rebuild/complex/full-identity-certificates/THREE-base-FULL-IDENTITY-NATIVE.json.gz',
'research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py','research/kappa-rebuild/complex/native_extensions.py',
'research/kappa-rebuild/complex/rebuild_native.py','research/kappa-rebuild/complex/power_two_balance.py',
'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py',
'research/kappa-function-composition/complex/prune_native.py','research/native-warp-extraction-boundary/operators.py',
'research/native-warp-extraction-boundary/algebra.py','research/higher-moment-strictification/verify.py',
'research/transported-warp-frames/PROOF.md']


def main():
    files=[]
    for path in PATHS:
        data=(ROOT/path).read_bytes();blob=sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        expected=subprocess.check_output(['git','rev-parse',HEAD+':'+path],cwd=ROOT,text=True).strip()
        if blob!=expected:raise ValueError('Inherited bytes differ from pinned Git source: '+path)
        files.append({'path':path,'git_blob':blob,'sha256':sha256(data).hexdigest(),'usage':'input' if not path.endswith('PROOF.md') else 'proof_attribution'})
    (HERE/'SOURCES.json').write_text(json.dumps({'base_commit':HEAD,'schema_version':1,'files':files},indent=2,sort_keys=True)+'\n')
    print('PASS_PINNED_GIT_SOURCE_INPUTS',len(files))


if __name__=='__main__':main()
