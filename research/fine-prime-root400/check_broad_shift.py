"""Independent exact supplement for the broad Gaussian shift identity.
PR1897 highlighted the inherited disabled assertion. This checker is independently
written from the original two exponents; no PR1897 executable is imported.
The identity requires L != 0. This does not establish all-size precision bounds.
"""
import json,sys
from pathlib import Path
import sympy as sp
x,y,b,L,d,s=sp.symbols('x y b L d s')
EK=-b*(x-L*y+d)**2;EG=-b*L*(x-y-s)**2
expanded=-b*((1-L)*x**2-L*(1-L)*y**2+d**2-L*s**2+2*(d+L*s)*x-2*L*(d+s)*y)
def zero(expr):return sp.Poly(sp.expand(sp.cancel(L**2*expr)),x,y,b,L,d,s).is_zero
def require(expr,label):
 if not zero(expr):raise ValueError(label)
require(EK-EG-expanded,'ordered expansion')
actual=(EK-EG).subs(s,-d/L)
shifted=-b*((1-L)*x**2-L*(1-L)*y**2+d**2-d**2/L+2*d*(1-L)*y)
require(actual-shifted,'complete shifted identity')
require(sp.diff(actual,x).subs(x,0),'zero x-linear term')
wrong_constant=-b*((1-L)*x**2-L*(1-L)*y**2+d**2+d**2/L+2*d*(1-L)*y)
wrong_linear=-b*((1-L)*x**2-L*(1-L)*y**2+d**2-d**2/L-2*d*(1-L)*y)
mutations={'wrong_constant_sign':actual-wrong_constant,'wrong_linear_sign':actual-wrong_linear,'wrong_shift_sign':(EK-EG).subs(s,d/L)-shifted,'missing_L_in_gaussian':(EK+b*(x-y+d/L)**2)-shifted}
for name,expr in mutations.items():
 if zero(expr):raise ValueError('mutation accepted: '+name)
out=dict(status='PASS_EXACT_BROAD_SHIFT_SUPPLEMENT',identities=3,rejecting_controls=list(mutations),corrected_bracket='(1-L)*x^2-L*(1-L)*y^2+d^2-d^2/L+2*d*(1-L)*y',inherited_disabled_expression_residual=str(sp.factor(actual-(-b*((1-L)*x**2-L*(1-L)*y**2+d**2+d**2/L-2*d*(1-L)*y)))),scope='Exact polynomial identities after multiplying by nonzero L squared; no new supplier, kappa arithmetic or all-size analytic theorem. Independent supplement to inherited check_gaugefree.py, whose disabled assertion was identified by PR1897.')
Path(sys.argv[1]).write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
