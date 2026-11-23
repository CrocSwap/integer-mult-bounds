"""Drive signed multiplication, caller dispatch, and both stage seams through this runtime."""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import runpy,sys

root=Path(__file__).parent.resolve()
runtime=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(runtime))
from upstream import install
install()
from installations import ENTRY,TERMINAL,activation
from ordinary_carrier import stage_for_width_log
from staged_carriers import entrance_logs
from band_product import prepare_native,production_supplier
from grades import LOWER
assert LOWER==1054
assert TERMINAL.rank_logs==(8192,118919,524288)
assert TERMINAL.kappa==Q('.003898226579820971') and TERMINAL.complex_log==499284
assert activation(TERMINAL)==1151157
if sys.argv[2]=='product':
    from io import BytesIO
    from band_product import multiply,multiply_tapes
    from check_product import physical_product
    inputs=[(0,0),(-1,0),(-1,-1),(-741503,466013),(2**129-17,-(2**73)+3),(-(2**4096+9),2**41-1)]
    for a,b in inputs:assert multiply(a,b)==a*b
    for tier in (ENTRY,TERMINAL):
        left=BytesIO(b'abc'+(741503).to_bytes(6,'little')+b'finish')
        right=BytesIO(b'xyz'+(466013).to_bytes(5,'little')+b'end');out=BytesIO()
        left.seek(3);right.seek(3)
        sign,size=multiply_tapes(left,6,right,5,out,left_negative=True,profile=tier)
        assert (sign,size,int.from_bytes(out.getvalue(),'little'))==(True,5,345550037539)
        assert left.tell()==right.tell()==3
        recipe=production_supplier(tier.complex_log,tier.positive_stop_denominator).recipe
        assert recipe.rank_log==tier.complex_log and recipe.ambient==306 and len(recipe.cells)==51
    witness=physical_product(ENTRY)
    assert witness['product']=='-345550037539' and witness['coefficients_prefix']==[11811,10996,4152,868,77]
    print('PASS_SIGNED_PRODUCTS_AND_DIRTY_RESTORE',len(inputs),witness)
else:
    helper=runpy.run_path(str(root/'check_stage_seam.py'))
    cuts=tuple(entrance_logs(TERMINAL.rank_logs))
    assert cuts==(8290,127273,651625)
    for i,c in enumerate(cuts,1):
        assert [stage_for_width_log(c+d,3,TERMINAL.rank_logs) for d in (-1,0,1)]==[i-1,i,i]
    origins=prepare_native(TERMINAL)
    assert all(r.level_floor==18960 for r in origins[:-1])
    census=helper['verify_stage']
    direct=[census(TERMINAL,cuts,2,150000),census(TERMINAL,cuts,3,680000)]
    compiled=[census(TERMINAL,cuts,2,1200000),census(TERMINAL,cuts,3,4500000)]
    assert all(x['direct'] for x in direct) and not any(x['direct'] for x in compiled)
    tapes=[helper['verify_tape'](1,[0,1],[2,1]),helper['verify_tape'](2,[1,7],[3,1])]
    print('PASS_STAGES_AND_WRONG_SIGN',cuts,direct,compiled,tapes)
