"""Exact Gaussian phase check for the actual staged entrance/FULL pair."""
from pathlib import Path
import copy,hashlib,json,sys
sys.dont_write_bytecode=True
NATIVE=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(NATIVE))
sys.path.insert(0,str(NATIVE/'vendor/clifford'))
import bw_gauss as B
import clifford_exact as C
import bw_adapters as A
import numpy as np

def mono(rec):
    re,im,exp=B.recipe_matrix(rec,9)
    assert exp==0
    support=(re!=0)|(im!=0)
    assert (support.sum(axis=0)==1).all() and (support.sum(axis=1)==1).all()
    perm=support.argmax(axis=0);phase=np.zeros(512,dtype=np.int64)
    for x,y in enumerate(perm):phase[x]={(1,0):0,(0,1):1,(-1,0):2,(0,-1):3}[int(re[y,x]),int(im[y,x])]
    return perm,phase

def equal(a,b):
    e=max(a[2],b[2])
    return bool(np.array_equal(a[0]<<(e-a[2]),b[0]<<(e-b[2])) and
                np.array_equal(a[1]<<(e-a[2]),b[1]<<(e-b[2])))

def main():
    E=[429,30];U=[256,128,64,32,16,8,4,2,1]
    rec,compiled=C.lower_child(A.S_of(E,U))
    assert rec['rank']==7 and A.wrapped_ok(E,rec,U)
    z=B.apply_mono(B.eye(9),mono(rec['right']),-1)
    z=B.frame(z,E,9,-1)
    z=B.frame(z,U,9,1)
    z=B.apply_mono(z,mono(rec['left']),-1)
    assert equal(z,B.coord(B.eye(9),range(7)))
    old,_=C.lower_child(A.S_of([30],U))
    assert old['rank']==8 and not A.wrapped_ok(E,old,U)
    wrong=copy.deepcopy(rec);wrong['left']['phase']=(wrong['left']['phase']+1)%4
    assert not A.wrapped_ok(E,wrong,U)
    assert not A.wrapped_ok([],rec,U)
    sources={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
             (Path(__file__),Path(A.__file__),NATIVE/'bw_gauss.py',NATIVE/'vendor/clifford/clifford_exact.py')}
    out={'status':'PASS_EXACT_PAIRED_ENTRANCE_FULL_WIDTH7_RESIDUAL','entry':E,'terminal':U,
         'physical_residual':'T_FULL T_span(429,30)^-1','wrapper_identity':'L^-1 T_FULL T_E^-1 R^-1 = C_[7] tensor I_[2]',
         'width':7,'recipe':rec,'all_512_Gaussian_columns_equal_including_global_phase':True,
         'same_order_dual':'inverse transpose of this exact identity; no zero-value assumption',
         'controls':['old_rank8_entry30_recipe_rejected','wrong_global_phase_rejected','omitted_entrance_transform_rejected'],
         'source_hashes':sources,
         'scope':'The one local changed helper residual used by both644 and660. Does not certify full native supplier, chronological owners, prefix precision, or outer bound.'}
    print(json.dumps(out,sort_keys=True),flush=True)

if __name__=='__main__':main()
