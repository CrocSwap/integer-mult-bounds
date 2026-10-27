"""Independent exact shifted broad Gaussian exponent identity; no producer imports."""
import sys,json,hashlib
from pathlib import Path
import sympy as sp

def require(ok,why):
 if not ok:raise ValueError(why)

def ident(expr):return sp.cancel(sp.expand(expr))==0
x,y,b,L,d=sp.symbols('x y b L d', nonzero=True)
s=-d/L
# Input mathematical statement: original exponent difference of broad kernel and shifted Gaussian.
raw=-b*(x-L*y+d)**2+b*L*(x-y-s)**2
correct=-b*((1-L)*x**2-L*(1-L)*y**2+d**2-d**2/L+2*d*(1-L)*y)
require(ident(raw-correct),'correct shifted identity')
controls={
 'inherited_plus_constant':-b*((1-L)*x**2-L*(1-L)*y**2+d**2+d**2/L+2*d*(1-L)*y),
 'wrong_y_linear_sign':-b*((1-L)*x**2-L*(1-L)*y**2+d**2-d**2/L-2*d*(1-L)*y),
 'unremoved_x_linear':correct-2*b*d*x,
 'wrong_y_quadratic_sign':-b*((1-L)*x**2+L*(1-L)*y**2+d**2-d**2/L+2*d*(1-L)*y),
}
rejected={}
for n,bad in controls.items():
 residual=sp.cancel(sp.expand(raw-bad))
 require(residual!=0,'control not rejected '+n)
 witness=residual.subs({x:sp.Rational(2),y:sp.Rational(3),b:sp.Rational(5),L:sp.Rational(2,3),d:sp.Rational(7,5)})
 require(witness!=0,'control witness vanishes '+n)
 rejected[n]={'symbolic_residual':str(residual),'exact_witness_residual':str(witness)}
# Independently prove desired shift removes x-linear coefficient, retains y-linear coefficient.
require(ident(sp.diff(raw,x).subs({x:0,y:0})),'x-linear cancellation')
require(ident(sp.diff(raw,y).subs({x:0,y:0})+2*b*d*(1-L)),'y-linear coefficient')
report={'status':'PASS_EXACT_BROAD_SHIFT_CORRECTION','sympy_version':sp.__version__,'python_optimization':sys.flags.optimize,'correct_formula':str(correct),'proof':'Exact rational-function equality under L!=0; mathematical intended Gaussian regime additionally b>0,L>0. No numerical stability claim.','original_constant':'d^2 + d^2/L (vacuous or True assertion)','correct_constant':'d^2 - d^2/L','checks':3,'controls':rejected,'producer_imports':False,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
print(json.dumps(report,indent=2))
