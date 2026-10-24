# Native recipes for the new centre-deleted core

This lane checks the native operators for both PR3133 provider words.
The words are the byte-equal copies in PR3148. It uses the new frame and
warp data. It does not use the earlier T74 frame data.

Fresh generation passed for both providers. Each run checked 1130 frames,
3036 directed child edges, 224 endpoint adapters, 180 signed physical warp
classes, 72 logical warp operators, and 56 residual wrapper classes. The
residual classes include 32 proper terminal pairs, of which 24 are cold.
Each source run rejected 25 wrapper mutations and 13 warp mutations.

The fresh child and residual recipe files have the same hashes as the
authenticated PR3133 native receipt. Both literal dual runs also passed:
each checked all 180 signed classes on all 512 columns. In each provider,
172 literal dual recipes differ from the forward recipes. All literal
dual recipes have rank zero. Thus the choice of logical warp orientation
does affect the phase tables, but it does not add native children.

The independent interpreter review is a separate calculation. The scalar
map, stock, controller, precision, and complete kappa calculation are also
separate checks. `RESULT.json` gives the generation result; `FREEZE.json`
pins its inputs, scripts, proofs, and outputs.

## Exact operator test

For a binary subspace U, let T_U be the canonical Clifford frame in the
pinned source. A child from U to V must implement T_V T_U^{-1}. The
generator derives its recipe from this product. It checks the full Pauli
table and the exact Gaussian dyadic image of the zero basis vector. These
two checks include the global phase.

To see this, let A and B be unitary operators with the same action on all
Pauli generators. Then B^{-1} A commutes with every X and Z generator. An
operator that commutes with every Z generator is diagonal in the standard
basis. If it also commutes with every X generator, all diagonal entries
are equal. Thus A is a scalar multiple of B. Equality on the zero basis
vector fixes that scalar as one. The argument applies to each generated
Clifford product. It also proves equality of all positive tensor powers.

Each child recipe has the form L C_[r] R, with R applied first. The
serialized L and R are monomial Clifford operators. For a nested frame
change, the checked r is the difference of the frame dimensions. The
physical warp product is T_V K_G^{sign} T_U^{-1}. Its checked r is zero.
The separate Gaussian matrix implementation checks every one of its 512
columns.

A helper that enters at E and leaves at V has residual T_V T_E^{-1}.
The recipes include the proper terminal subspaces of the new words. They
also include the cold pairs with E equal to zero. The exact wrapper test
checks R^{-1}, then the residual, then L^{-1}; the result is C_[r]. It does
not replace a proper terminal frame by FULL.

## Literal dual warps

The backward scalar proof uses the inverse transpose of each logical
warp. For a unitary warp K this is the entrywise conjugate of K. The
source emitter stores the same signed warp labels for both orientations.
The orientation must therefore select a physical implementation.

There are two valid routes. The free-operator proof can establish the
endpoint identity for an arbitrary consistent choice of invertible warp
generators. The physical implementation can then use the forward K in
both orientations. Alternatively, the literal dual implementation can
use conjugate(K) in the backward orientation. This lane supplies exact
recipes for the second route as well.

The literal dual route has a general rank-zero closure property. Let K
be a monomial Clifford operator whose nonzero entries are fourth roots of
unity. Every source K_G has this property. In a standard basis, K is an affine
permutation with a phase of the form

    i^(c + alpha.x + 2 q(x)),

where q is a binary quadratic form. Conjugation changes this phase by
2(c + alpha.x) modulo 4. The quadratic term vanishes. After the affine
permutation, this phase is a signed Z Pauli. Thus

    conjugate(K) K^{-1} = P

for a Pauli P. Suppose the accepted physical warp is

    W = T_V K T_U^{-1}

and W is monomial. Then its literal dual counterpart is

    T_V conjugate(K) T_U^{-1} = (T_V P T_V^{-1}) W.

A Clifford frame maps a Pauli to a Pauli. A Pauli is monomial. Hence the
literal dual counterpart is monomial and needs no native child. Apply the
same argument to K^{-1} for a negative signed occurrence. This proof does
not require U and V to be FULL, or require the Pauli to be diagonal after
frame conjugation.

`generate_dual_warps.py` also checks this conclusion directly for each
signed class of each new provider. It uses the physical product
T_V conjugate(K_G)^{sign} T_U^{-1}. A separate Gaussian matrix calculation
compares all 512 columns. A wrong global phase must fail.

## Source and credit

The core comes from
[PR3133](https://github.com/CrocSwap/integer-mult-bounds/pull/3133), at
commit `51eb9c4ee9e4722010d308aa3309e039d3940cc2`. The byte-equal provider
words are in
[PR3148](https://github.com/CrocSwap/integer-mult-bounds/pull/3148), at
commit `f2927a4b8afcf0701a6b945e14f30de1d94f5176`:

- [Base word](https://github.com/CrocSwap/integer-mult-bounds/blob/f2927a4b8afcf0701a6b945e14f30de1d94f5176/research/coupled-carrier-cap740/words/base.json.gz).
- [Extra word](https://github.com/CrocSwap/integer-mult-bounds/blob/f2927a4b8afcf0701a6b945e14f30de1d94f5176/research/coupled-carrier-cap740/words/extra.json.gz).

The unchanged recipe sources come from
[PR2588](https://github.com/CrocSwap/integer-mult-bounds/pull/2588), at
commit `8cd9dc88e24f062e2ca2fa7f4844a3d3319381fb`:

- [Phase compiler](https://github.com/CrocSwap/integer-mult-bounds/blob/8cd9dc88e24f062e2ca2fa7f4844a3d3319381fb/research/gmx-t74-borrow43-handoff/new/code/borrow/bw_phases.py).
- [Residual wrappers](https://github.com/CrocSwap/integer-mult-bounds/blob/8cd9dc88e24f062e2ca2fa7f4844a3d3319381fb/research/gmx-t74-borrow43-handoff/new/code/borrow/bw_adapters.py).
- [Gaussian matrix implementation](https://github.com/CrocSwap/integer-mult-bounds/blob/8cd9dc88e24f062e2ca2fa7f4844a3d3319381fb/research/gmx-t74-borrow43-handoff/new/code/borrow/bw_gauss.py).
- [Serialized warp checker](https://github.com/CrocSwap/integer-mult-bounds/blob/8cd9dc88e24f062e2ca2fa7f4844a3d3319381fb/research/gmx-t74-borrow43-handoff/new/code/borrow/bw_check_recipes.py).
- [Exact Clifford implementation](https://github.com/CrocSwap/integer-mult-bounds/blob/8cd9dc88e24f062e2ca2fa7f4844a3d3319381fb/research/gmx-t74-borrow43-handoff/new/code/borrow/vendor/clifford/clifford_exact.py).

The source files retain their original author and AI-assistance notices.
The wrapper source credits the PR458 construction. The warp source credits
Cinna Davis and PR2226. OpenAI Codex assisted this lane's driver, literal
dual calculation, proof, and local checks. The independent review is a
separate agent calculation. It is not a maintainer review.

## Reproduction

Use one process and the workspace Python that has NumPy:

    work/verification-venv/bin/python -I -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/generate_recipes.py
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 work/verification-venv/bin/python -I -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/generate_dual_warps.py
    python3 -I -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/freeze_results.py

The first command checks every source and input pin before generation.
It runs the wrapper, phase, and serialized warp checks for each provider.
The second command checks the source and first-stage output pins before
it generates the literal dual recipes. The scripts write results only
inside this lane. No PR, push, or publication commit is part of this work.
