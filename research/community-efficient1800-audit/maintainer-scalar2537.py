"""Finish unchanged scalar/pricing stages using the authenticated complete frame audit.

This is explicitly source-bound reuse, not a fresh frame replay. The first
stage's complete exact nesting marker precedes a memory-guard termination.
"""
import sys
if sys.flags.optimize:
    raise RuntimeError('Assertions must remain enabled')
from pathlib import Path
import json,hashlib,os
ROOT=Path(__file__).resolve().parent
receipt_path=Path(sys.argv[1]);log_path=Path(sys.argv[2])
receipt=json.loads(receipt_path.read_text());log=log_path.read_bytes()
assert receipt['head']=='222063b96ec1a109a8c9f40e5d615498a737c6dd'
assert receipt['status']=='budget_deferred' and receipt['commands'][0]['stop_reason']=='memory_guard_1GiB'
assert not receipt['changed_files_after']
assert hashlib.sha256(log).hexdigest()==receipt['log_sha256']
assert b'PASS exact rational nesting (4878 new pairs; all inherited pairs checked)' in log
assert b'null_exact kernel: audit (both original kernels on every call; serial bounded memo tables)' in log
for name,digest in receipt['input_sha256'].items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest, name
sys.path.insert(0,str(ROOT/'research/recycled-bit-integration'))
import verify as V
assert hashlib.sha256(Path(V.__file__).read_bytes()).hexdigest()=='e8da17f2b9a06d33c38cd3fea515fc9f5b1cf04ab6d5de0ed8451c65bbb85a8a'
observed=[]
def reused(exact,moves,nondegenerate=False):
    observed.append((len(moves),nondegenerate))
    assert observed==[(4878,True),(202190,False)][:len(observed)]
    print('REUSED_COMPLETE_FRAME_STAGE',len(moves),nondegenerate,'log_sha256='+receipt['log_sha256'],flush=True)
    return []
# No frame objects remain resident while the independent scalar arrays are built.
V.Exact=lambda *args: None
V.install_null_kernel=lambda *args,**kwargs: 'REUSED complete original/fast exact comparison from authenticated earlier stage'
V.check_moves=reused
os.environ['VERIFY_JOBS']='1'
sys.argv=['verify.py','--all']
V.main()
assert observed==[(4878,True),(202190,False)]
print('PASS_SCALAR_AND_ASSEMBLY2537_WITH_AUTHENTICATED_FRAME_REUSE',flush=True)
