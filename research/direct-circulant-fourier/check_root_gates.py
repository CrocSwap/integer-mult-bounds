"""Run the rectangular-wire circuit and its fixed-length H-word lowering."""

from fractions import Fraction
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from root_gate_plan import (
    certify_accretivity, compile_padded_root, load_compiler, lower_pair, padded_matrix, paired_layer,
)


def demand(ok, why):
    if not ok:
        raise ValueError(why)


def fixture_column(compiler, r, gauss_turn, bits, direction, copies, rotation):
    """Form the sector-root column for the finite chirp fixtures."""
    phases = compiler.engine.Phases(bits+8, compiler.raw[compiler.generator.ORACLE])
    C, rounded = compiler.exact.C, compiler.exact.rounded
    half = (r+1)//2
    turns = []
    for k in range(r):
        s = (direction*(gauss_turn+Fraction(half*k*k, r)) - rotation + Fraction(1, 2)) % 1
        turns.append((s-Fraction(1, 2))/copies)
    column = []
    for index in range(r):
        value = C()
        for k, s in enumerate(turns):
            a = s+Fraction(k*index, r)
            value += phases.phase(a.denominator, a.numerator)
        dyadic = rounded(value/r, bits)
        column.append((dyadic.re, dyadic.im))
    return column, phases


def word_image(word, x, y):
    x, y = word[0][0]*x, word[0][1]*y
    for a, b in word[1:]:
        x, y = a*(x+y), b*(x-y)
    return x, y


def verify_lowering(compiler, plan, n):
    checked = set()
    for layer in plan:
        for _, gate in paired_layer(layer, n, compiler.exact):
            key = tuple((v.re,v.im) for row in gate for v in row)
            if key in checked:
                continue
            checked.add(key)
            word = lower_pair(gate)
            demand(len(word)==17, "fixed sixteen-H length")
            for j in range(2):
                column = word_image(word,compiler.exact.C(int(j==0)),compiler.exact.C(int(j==1)))
                demand(column == (gate[0][j],gate[1][j]), "lowered pair differs")
    return len(checked)


def test_one(compiler, r, n, gauss_turn, direction, copies):
    bits = 30
    rotation = direction * gauss_turn if copies == 2 else Fraction(0)
    margin = Fraction(1,3*r) if copies == 2 else Fraction(1,4)
    col, phases = fixture_column(compiler,r,gauss_turn,bits+14,direction,copies,rotation)
    _, mat = padded_matrix(compiler,col,n)
    if r != n:
        try:
            compiler.full.admission(mat)
        except ValueError as exc:
            demand(str(exc)=="exact full Toeplitz admission","wrong old admission failure")
        else:
            raise ValueError("non-Toeplitz control passed")
    plan, builder = compile_padded_root(compiler,col,n,bits+12,radius=2*n,margin=margin)
    count = verify_lowering(compiler,plan,n)
    C, Vec, apply = compiler.exact.C, compiler.exact.Vec, compiler.exact.apply
    data = Vec(C(Fraction(i % 5 - 1,8),Fraction((3*i+1)%7-2,8)) for i in range(n))
    x = data
    for _ in range(copies):
        x,_ = apply(plan,x,builder.bound["data_bits"])
    compensation = phases.phase(rotation.denominator, rotation.numerator)
    x = [z * compensation if i < r else z for i,z in enumerate(x)]
    root_lo,_ = compiler.engine.inverse_sqrt_box(r,bits+22)
    half = (r+1)//2
    ref = []
    for i in range(n):
        if i >= r:
            ref.append(data[i])
            continue
        ref.append(root_lo * sum(
            (phases.phase(r,-direction*half*(i-j)**2)*data[j] for j in range(r)),C()))
    err = max((v-w).norm2() for v,w in zip(x,ref))
    demand(err < Fraction(1,1 << (2*bits)), "physical cyclic chirp error")
    if copies == 2:
        uncompensated = [z / compensation if i < r else z for i,z in enumerate(x)]
        demand(max((a-b).norm2() for a,b in zip(uncompensated,ref)) > Fraction(1,100),
               "missing Gauss compensation was invisible")
    return len(plan),sum(map(len,plan)),count


def test_nonunitary(compiler):
    """Square a filter with Fourier multipliers 2, 1/2, 3 and 1/4."""
    C, Vec, apply = compiler.exact.C, compiler.exact.Vec, compiler.exact.apply
    f = Fraction
    column = [(f(23,16),0), (f(-1,4),f(1,16)), (f(17,16),0), (f(-1,4),f(-1,16))]
    n = 8
    root, _ = padded_matrix(compiler, column, n)
    try:
        certify_accretivity(root, f(1,4))
    except ValueError as exc:
        demand("strict accretivity" in str(exc), "wrong boundary rejection")
    else:
        raise ValueError("A root on the exact margin passed")
    plan, builder = compile_padded_root(compiler, column, n, 38, radius=20, margin=f(1,8))
    count = verify_lowering(compiler, plan, n)
    data = Vec(C(f(2-j,8),f(1-2*j,8)) for j in range(n))
    first, _ = apply(plan, data, builder.bound["data_bits"])
    result, _ = apply(plan, first, builder.bound["data_bits"])
    basis = [C(1), C(0,1), C(-1), C(0,-1)]
    multipliers = [4, f(1,4), 9, f(1,16)]
    target = [sum((m*basis[(j*k)%4] for k,m in enumerate(multipliers)), C())/4
              for j in range(4)]
    expected = [sum((target[(k-j)%4]*data[j] for j in range(4)), C()) for k in range(4)]
    expected += list(data[4:])
    demand(max((u-v).norm2() for u,v in zip(result, expected)) < f(1,1 << 60),
           "exact nonunitary spectrum or dirty complement differs")
    return len(plan), sum(map(len,plan)), count


if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parents[2])
    args=parser.parse_args()
    compiler=load_compiler(args.source_root)
    for r,n,turn,sign,copies in [(3,4,Fraction(1,4),1,3),(5,8,Fraction(1,2),-1,2),
                                 (3,8,Fraction(1,4),-1,16)]:
        print("padded chirp",r,n,sign,"copies",copies,"layers, gates, distinct checked H words",
              test_one(compiler,r,n,turn,sign,copies),flush=True)
    print("padded nonunitary square, layers, gates, distinct checked H words",
          test_nonunitary(compiler),flush=True)
    try:
        compile_padded_root(compiler,[(0,0),(1,0)],4,10)
    except ValueError as exc:
        demand("strict accretivity" in str(exc),"wrong spectral rejection")
    else:
        raise ValueError("unrooted cycle with singular leading section passed")
    print("PASS_PADDED_CIRCULANT_PHYSICAL_GATES")
