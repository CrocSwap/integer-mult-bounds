"""Check the two-dimensional spectral projection on a mixed padded field."""

import argparse
from fractions import Fraction
from pathlib import Path
from random import Random
import sys


def run(source_root):
    sys.path.insert(0, str(source_root/"research/direct-circulant-fourier"))
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from root_gate_plan import load_compiler
    from spectral_filter import SpectralFilter, live_positions
    from tensor_word import Grid, load_routes

    compiler = load_compiler(source_root)
    grid = Grid(106)
    machine = SpectralFilter((3,5), compiler, load_routes(source_root), grid)
    widths = machine.transform.sides
    mask = lambda: (grid.one if k%2 == j%2 else (0,0) for j in range(5) for k in range(3))
    valid = [i for i in range(32) if i % 4 < 3 and i // 4 < 5]
    if valid != [i for i,live in enumerate(live_positions((3,5),widths)) if live]:
        raise ValueError("The original Cartesian block differs")
    if sum(z == grid.one for z in mask()) != 8:
        raise ValueError("The mask must retain eight independent frequencies")

    C = compiler.exact.C
    phases = compiler.engine.Phases(145, compiler.raw[compiler.generator.ORACLE])
    def kernel(r):
        return [2/(r*(C(1)+phases.phase(r,j))) for j in range(r)]
    k3, k5 = kernel(3), kernel(5)
    def reference(data, q):
        i, j = q%4, q//4
        x = C(Fraction(data[q][0],grid.unit), Fraction(data[q][1],grid.unit))
        total = C()
        for p in valid:
            y = C(Fraction(data[p][0],grid.unit), Fraction(data[p][1],grid.unit))
            total += y*k3[(i-p%4)%3]*k5[(j-p//4)%5]
        return (x+total)/2

    zeros = [(0,0)]*32
    for seed in (4019, 7243):
        rng = Random(seed)
        unit = grid.unit // 64
        values = [(rng.randrange(-126,127)*unit, rng.randrange(-125,126)*unit) for _ in zeros]
        if C(*values[0])*C(*values[5]) == C(*values[1])*C(*values[4]):
            raise ValueError("The independent signal needs a nonzero two-axis minor")
        first = machine.apply(values, mask())
        second = machine.apply(first, mask())
        for j in range(32):
            if j not in valid:
                if values[j] == (0,0) or first[j] != values[j] or second[j] != values[j]:
                    raise ValueError("A dirty pad word changed")
                continue
            out = C(Fraction(first[j][0],grid.unit), Fraction(first[j][1],grid.unit))
            again = C(Fraction(second[j][0],grid.unit), Fraction(second[j][1],grid.unit))
            if (out-reference(values,j)).norm2() >= Fraction(1,1 << 88):
                raise ValueError("Projection differs from the geometric-sum kernel")
            if (out-again).norm2() >= Fraction(1,1 << 88):
                raise ValueError("Second projection differs")
        if all(first[j] == values[j] for j in valid) or all(first[j] == (0,0) for j in valid):
            raise ValueError("The nontrivial mask had no observable effect")
    print("projection 3x5 in 4x8, 8 retained modes, 15 independent inputs, 17 exact dirty holes")
    print("two independent fields, two applications per field,", machine.transform.h_calls,
          "simultaneous H calls per transform")
    print("PASS_NONSEPARABLE_SPECTRAL_FILTER")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parents[2])
    run(parser.parse_args().source_root.resolve())
