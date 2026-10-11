"""Exact finite witnesses and endpoint budgets for the final-grid correction.

The defect was identified by GPT-6 Pro. This small checker is independently
authored in Codex. Passing it does not prove the inherited Gaussian tail,
transcendental approximation, tape-complexity or multiplication theorems.
"""
from fractions import Fraction as F
import json

if not __debug__:
    raise RuntimeError('Assertions must be enabled.')
p=101
P=p+12
h=F(1,2**p)
exact=h/2
old_bound=F(2**9,2**P)
nearest=min(abs(exact-k*h) for k in (0,1))
assert nearest==h/2 and old_bound==h/8 and nearest>old_bound
# For every integer k, |k-1/2|>=1/2; the adjacent grid values attain it.

# sqrt(2)<3/2 supplies rational upper budgets for both complex maps.
sqrt_two_upper=F(3,2)
assert sqrt_two_upper**2>2
forward=1+F(1,4)+sqrt_two_upper
correction=3+F(1,4)+sqrt_two_upper
assert forward<3 and correction<5 and 5<F(p,3)
normalized_internal=F(1,16)+sqrt_two_upper*F(1,2**(2*p))
assert normalized_internal<F(1,4)

# Endpoint checks for the written four-step induction: for p>=101,
# 4p<=2^(floor(p/4)-1). Increasing p by four doubles the right side
# while increasing the left side by16, preserving the inequality.
for endpoint in range(101,105):
    assert 4*endpoint<=2**(endpoint//4-1)
assert F(53,20)*p+12<3*p  # p+Gamma+ceil(log2 L_A)+11 upper bound
print(json.dumps({
    'checker_version':'p2-final-grid-1.0',
    'p':p,'P':P,'claimed_error_over_h':str(old_bound/h),
    'unavoidable_error_over_h':str(nearest/h),
    'forward_rational_budget_over_h':str(forward),
    'correction_rational_budget_over_h':str(correction),
    'normalization_budget_below_h_over_4':True,
    'scope':'Exact finite counterexample and rational endpoint budgets; universal proof remains separate.'
},sort_keys=True))
