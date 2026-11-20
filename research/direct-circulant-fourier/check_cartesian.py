"""Check the physical filter against independent four-point Gaussian arithmetic."""

import argparse
from fractions import Fraction
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cartesian_spectrum import cartesian_root
from root_gate_plan import compile_padded_root, load_compiler


def check(compiler):
    C, Vec, apply = compiler.exact.C, compiler.exact.Vec, compiler.exact.apply
    f = Fraction
    symbols = [(1, 0), (-1, 0), (-2, 0), (f(3,5), f(4,5))]
    root = cartesian_root(compiler, symbols, 32)
    correction = C(*root.compensation)
    if correction.norm2() != 1 or correction.re == 0 or correction.im == 0:
        raise ValueError("Expected a nontrivial exact rational unit correction")
    if root.multiplier_error > f(1, 1 << 32):
        raise ValueError("Private coefficient precision differs")
    plan, builder = compile_padded_root(compiler, root.column, 8, 42, radius=12,
                                        margin=root.margin)
    data = Vec(C(f(4-j,16),f(2*j-3,16)) for j in range(8))
    x, _ = apply(plan, data, builder.bound["data_bits"])
    x, _ = apply(plan, x, builder.bound["data_bits"])
    result = [v * correction if j < 4 else v for j,v in enumerate(x)]

    basis = [C(1), C(0,1), C(-1), C(0,-1)]
    values = [C(*z) for z in symbols]
    spectrum = [sum((data[j]*basis[(-j*k) % 4] for j in range(4)), C()) for k in range(4)]
    expected = [sum((values[k]*spectrum[k]*basis[(j*k) % 4] for k in range(4)), C())/4
                for j in range(4)] + list(data[4:])
    if max((a-b).norm2() for a,b in zip(result,expected)) >= f(1,1 << 60):
        raise ValueError("The two physical roots differ from the stated filter")
    if max((a-b).norm2() for a,b in zip(x,expected)) <= f(1,100):
        raise ValueError("A missing branch correction was invisible")
    if min(z.norm2() for z in data[4:]) == 0:
        raise ValueError("The complement control needs dirty wires")

    for symbols in [[], [(1,0),(0,0)]]:
        try:
            cartesian_root(compiler, symbols, 8)
        except ValueError:
            pass
        else:
            raise ValueError("An invalid spectrum passed")
    for value in [(f(1,1 << 32), f(-1,1 << 40)), (-3,0)]:
        one = cartesian_root(compiler, [value], 26)
        z = C(*one.column[0])
        error = C(*one.compensation) * z*z - C(*value)
        if error.norm2() > one.multiplier_error**2:
            raise ValueError("One-coordinate absolute error differs")
    print("Cartesian spectrum 4 of 8, exact nonreal unit correction,",
          len(plan), "layers,", sum(map(len,plan)), "gates")
    print("PASS_CARTESIAN_SYMBOL_GATES")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parents[2])
    check(load_compiler(parser.parse_args().source_root))
