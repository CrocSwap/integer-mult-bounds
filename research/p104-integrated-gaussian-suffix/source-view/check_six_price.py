"""Second directed audit uses the raw installed calendar and original first/last heights."""
from fractions import Fraction as Q
from math import ceil
from pathlib import Path
import json,sys
root=Path(__file__).resolve().parent
runtime=Path(sys.argv[1]).resolve()
# Load and hash the changed physical calendar before importing the independent
# 192-bit square-root and discrete-optimization implementation.
sys.path.insert(0,str(runtime))
from upstream import install
install()
from grades import LOWER,numerical_recipe
from installations import ENTRY,TERMINAL
from typed_transport import TypedPlan
assert LOWER==1054 and str(runtime) in str(sys.modules['typed_transport'].__file__)
recipe=numerical_recipe(TERMINAL.complex_log)
sys.path.append(str(root))
import certify_frontier as f
from certify_frontier import T,C,dec,powers
target=Q('.003898216827298')
debit=Q(125645,2**20)
edges,psi,weights=f.aggregate(recipe)
upper_fringe=sum(price*(7*(k-r)+T*r*r/(2*k*LOWER)) for r,k,price in weights)/(T*psi)
invoice=f.factor(upper_fringe,263772,LOWER)
assert powers(2,debit)[0]>invoice>powers(2,debit-Q(1,2**20))[1]
f.CLOCK_CAP=318292011
best=f.optimize(debit)
assert Q(best['lower_bookable'])==target==TERMINAL.kappa and best['gaussian_height']==TERMINAL.complex_log
assert tuple(best['ordinary_heights'])==TERMINAL.rank_logs and best['complete_clock']==318291831
hi=Q(best['supremum'])
assert target<hi and hi==C-debit/479787-f.STOP
assert target-f.OLD_UPPER>Q('0.0000000025441059')
assert f.ordinary(TERMINAL.rank_logs)>target+f.STOP
assert len(edges)==51 and len(recipe.typed_cells())==88 and psi>Q('926899828.8291')
print(json.dumps({'independent_interval_bits':192,'finite_factor_upper':dec(invoice,36),
    'debit':str(debit),'upper_slack':dec(powers(2,debit)[0]-invoice,36),
    'next_smaller_debit_denominator':2**20,'next_smaller_fails':True,
    'estimated_fringe_upper':dec(upper_fringe,39),'exact_stop_supremum':str(hi),
    'strict_gain_over_predecessor_upper':str(target-f.OLD_UPPER),'best':best},indent=2))
