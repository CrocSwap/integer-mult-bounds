"""Exercise the actual e264 small signed product with the last-grid profile."""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(sys.argv[1]).resolve()))
from upstream import install
install()
from installations import DYADIC_ENDPOINT as LAST_GRID
from check_product import physical_product
import band_product
seen=[]
def capture(frame,event,arg):
    if event=='call' and frame.f_code is band_product.h_pack.__code__:
        x=frame.f_locals
        assert x['machine'].profile is LAST_GRID
        assert x['make_supplier'].func is band_product.production_supplier
        seen.append((x['rank_log'],x['make_supplier'].args,x['machine'].total))
        sys.setprofile(None)
sys.setprofile(capture)
try:result=physical_product(LAST_GRID)
finally:sys.setprofile(None)
assert seen==[(36000,(36000,10**21),32)]
assert result['product']=='-345550037539' and result['shuttles']==138
assert result['coefficients_prefix']==[11811,10996,4152,868,77]
print('PASS_E264_LAST_GRID_PROFILE_BOUND_SIGNED_CONTROL')
print(json.dumps({'dispatch':seen,'result':result}))
