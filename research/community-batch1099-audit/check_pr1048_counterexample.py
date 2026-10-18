"""Exact counterexample to the arbitrary-fixed-exponent root-ordering claim.
Douglas Colkitt with OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q

def require(x):
    if not x: raise ValueError('Counterexample check failed')

# m=8, W=4, A={2:15}, B={1:14,4:4}; both rank masses are 30.
require(15*2 == 14+4*4 == 30)
# At a0=1/2: G_A=15 sqrt(2)<22=G_B.
require(15**2*2 < 22**2)
# At z=47/1000, A's moment numerator is already above 32.
require(4**47 > Q(16,15)**1000)
# Bound t=2^z from above rationally; B's numerator is 14t^3+16t<32.
t=Q(2583,2500)
require(t**1000 > 2**47)
require(14*t**3+16*t < 32)
# Both numerators strictly increase from 30 at zero. Thus root_A<z<root_B,
# although G_A(a0)<G_B(a0). Fixed-a0 ordering does not order their roots.
print('PASS_PR1048_COUNTEREXAMPLE root_A < 47/1000 < root_B but G_A(1/2) < G_B(1/2)')
