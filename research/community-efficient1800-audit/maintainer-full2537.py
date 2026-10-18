"""Complete original PR2537 --all audit, bounding only disposable memo tables.

Original frame predicates and all main() assertions remain unchanged. Each
sorted move is checked once per original check_moves invocation; clearing
Exact._basis/_null only recomputes deterministic bases/annihilators. All kernel
calls compare the new result with the original Fraction result in audit mode.
"""
import sys
if sys.flags.optimize:
    raise RuntimeError('Assertions must remain enabled')
from pathlib import Path
import os,json,hashlib,importlib.util,time
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'research/recycled-bit-integration'))
import verify as V
assert Path(V.__file__).resolve()==ROOT/'research/recycled-bit-integration/verify.py'
assert hashlib.sha256(Path(V.__file__).read_bytes()).hexdigest()=='e8da17f2b9a06d33c38cd3fea515fc9f5b1cf04ab6d5de0ed8451c65bbb85a8a'
os.environ['VERIFY_JOBS']='1'
original_install=V.install_null_kernel
original_check=V.check_moves
counts={'null':0,'primitive':0}
coverage=[]
def install(folder,mode=None):
    assert original_install(folder,'audit')=='audit'
    import linalg,check_lifted
    null=linalg.null_exact;prim=V.frames147.prim
    def checked_null(A,k):
        counts['null']+=1
        return null(A,k)
    def checked_prim(row):
        counts['primitive']+=1
        return prim(row)
    linalg.null_exact=check_lifted.null_exact=checked_null
    V.frames147.prim=checked_prim
    return 'audit (both original kernels on every call; serial bounded memo tables)'
def bounded_check(exact,moves,nondegenerate=False):
    ordered=sorted(moves,key=lambda m:(str(m[2]),str(m[1]),str(m[0])))
    failed=[];checked=0
    for offset in range(0,len(ordered),512):
        exact._basis.clear();exact._null.clear()
        part=ordered[offset:offset+512]
        failed.extend(original_check(exact,part,nondegenerate=nondegenerate))
        checked+=len(part)
        if offset%25600==0:
            print('FULL2537 checked',checked,'/',len(ordered),'nondegenerate',nondegenerate,counts,flush=True)
    exact._basis.clear();exact._null.clear()
    assert checked==len(ordered)
    coverage.append(dict(moves=checked,nondegenerate=nondegenerate,failures=len(failed)))
    return failed
V.install_null_kernel=install
V.check_moves=bounded_check
sys.argv=['verify.py','--all']
V.main()
assert coverage==[dict(moves=4878,nondegenerate=True,failures=0),dict(moves=202190,nondegenerate=False,failures=0)],coverage
assert counts['null']>0 and counts['primitive']>0
print('PASS_FULL2537',json.dumps(dict(coverage=coverage,kernel_equality_calls=counts,memo_chunk_size=512)),flush=True)
