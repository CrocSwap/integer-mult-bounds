# ADDITIVE ad2: rung ceilings (#7113 caller, X=112) for S values valid on t >= t_lo (S(t_lo), monotone); rg1 = our lane code.
import sys, io, contextlib
sys.path.insert(0, '<research-tree>/cards/WILD/UNIMODEL/runggen')
with contextlib.redirect_stdout(io.StringIO()):
    import rg1
from rg1 import add, ceiling, fm, nat, C7113, D
for lab, S in (('ls5 S(.01)=865.58 [as quoted]', '865.58'), ('ls5 S(.0075)=865.058', '865.058'),
               ('S_fix(.0075)=799.010 (Y2 free edge)', '799.010')):
    mx = ceiling(add((1, C7113), (-1, nat(112, D(S), False))))
    ad = ceiling(add((1, C7113), (-1, nat(112, D(S), True))))
    print(f'{lab}: max form {fm(mx)} | +HS additive {fm(ad)}')
print('control X112+HS only:', fm(ceiling(add((1, C7113), (-1, nat(112, 0))))))
