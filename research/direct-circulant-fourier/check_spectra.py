"""Compare certified root endpoints with the supplied symbols over asymmetric fixtures."""
from fractions import Fraction as F
from pathlib import Path
from random import Random
import sys

root = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cartesian_spectrum import cartesian_root
from root_gate_plan import load_compiler
from spectral import polar_root, phase_value


compiler = load_compiler(root)
C = compiler.exact.C
ref = compiler.engine.Phases(220,compiler.raw[compiler.generator.ORACLE])


def audit(column, comp, target, expected):
    n = len(column)
    entries = [C(*z) for z in column]
    l1 = sum(abs(z.re)+abs(z.im) for z in entries)
    fourier_slack = F(1,1 << 220)*l1
    square_slack = (2*l1+fourier_slack)*fourier_slack
    for k,(lam,input_slack) in enumerate(expected):
        z = sum((q*ref.phase(n,-k*j) for j,q in enumerate(entries)),C())
        residual = comp*z*z-lam
        upper = abs(residual.re)+abs(residual.im)+square_slack+input_slack
        if upper > target:
            raise ValueError(("endpoint bound",n,k,float(upper),float(target)))


rng = Random(92051)
cartesian_count = polar_count = 0
for n in range(1,12):
    values = [(F(rng.randrange(-17,18) or 1)*2**(j%4),F(rng.randrange(-25,26), 1+(j*3)%7))
              for j in range(n)]
    values[0] = (F(1,1 << (4+n)),F(-1,1 << (17+n)))
    if n>1:
        values[1] = (F(-3), F(0))
    if n>2:
        values[2] = (F(-6), F(0))
    packet = cartesian_root(compiler,values,24)
    audit(packet.column,C(*packet.compensation),packet.multiplier_error,
          [(C(*z),0) for z in values])
    cartesian_count += n
    for mode in ("generic","grid"):
        turns = [F(j,n) for j in range(n)]
        radii = [F(1,1 << (2+j)) if j%2 else F(2**(2+j)) for j in range(n)]
        packet, phases = polar_root(compiler,radii,turns,22,phase_grid=n if mode=="grid" else None)
        col = [C(*z) for z in packet.column]
        try:
            from root_gate_plan import certify_accretivity
            certify_accretivity(col,packet.accretivity)
        except ValueError:
            print("FAIL: polar root misses its own margin",n,mode,flush=True)
            continue
        # Comp is rational and differs from the true phase by <=2^-220.
        comp = phase_value(ref,packet.rotation)
        keep = F(1,1 << 210) * (max(radii)+1)
        audit(packet.column,comp,F(1,1 << 22),
              [(phase_value(ref,s)*rad,keep) for s,rad in zip(turns,radii)])
        polar_count += n
print("certified Cartesian coordinates",cartesian_count,"polar coordinates",polar_count)
