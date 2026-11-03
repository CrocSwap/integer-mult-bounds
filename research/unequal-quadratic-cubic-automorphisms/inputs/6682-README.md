# Exact tensor characters beyond Frobenius truncations

This contribution was produced by Nick Petalas. Apache-2.0.

Scoped written proof with exact finite corroboration. For every finite field
K = F_q of characteristic p, d >= 2, and n >= 2 which is not a power of p,
we determine the exact ordered covariant stabilizer determinant image for
multiplication in

```text
A = K[x_1,...,x_d]/(x_1^n,...,x_d^n).
```

The new step is the monomial tangent restriction. It settles a non-Frobenius
part of the nilpotent-algebra question in [PR5252](https://github.com/CrocSwap/integer-mult-bounds/pull/5252).
[PROOF.md](PROOF.md) gives the quantified argument. This is an algebraic side
result with no new kappa or selected-frontier change.

## Result

Write H_r = {a^r : a in K*}, and put

```text
N = n^d,
E = n^(d-1) n(n-1)/2,
S = n^(d-2) n(n-1)/2,
D = H_E <(-1)^S>.
```

Every algebra automorphism has a monomial tangent matrix, and its determinant
is the determinant of that tangent substitution on all N monomials. Nonlinear
lifts add no determinant character. The exact automorphism determinant image
is D, attained by variable scalings and swaps.

For the multiplication tensor in A* tensor A* tensor A,

```text
Delta = {(u,v,w) : vw in H_N, uw in H_N, uvw in D}.
```

Let m = q-1, g = gcd(m,N), and h = gcd(m,E), adding m/2 to the latter gcd
when q and S are both odd. Three bounded equations define Delta:

```text
(vw)^(m/g) = (uw)^(m/g) = (uvw)^(m/h) = 1.
```

The image has m^3/(g^2 h) elements. The GL orbit splits into exactly g^2 h
orbits under the product SL group. Independent changes of the three bases
preserve these equations. Extracting them uses q,n,d under an explicit orbit
promise; recognition and a transporter are not supplied.

The swap sign is necessary. For K = F3 and n = d = 2, scalar variable changes
have determinant one, but swapping x and y has determinant minus one. The
full covariant image is exactly {(1,1,1),(2,2,2)}. Omitting the swap loses
one of its two elements. For K = F7, n = 2, d = 3, swaps instead have
determinant one, and the automorphism image is the three nonzero squares.

## Evidence and reproduction

The self-contained standard-library verifier constructs literal quotient
rings and substitution matrices. It executes no predecessor scientific code.
Its generated report binds all six package files by SHA256.

- Fifteen contexts, including F4 and F8, supply 138 literal attaining
  automorphisms. Every basis product is checked.
- Two complete generator-image domains visit 729 pairs over F3 at n = 2
  and 65,536 pairs over F2 at n = 3. They accept 72 and 2,048 automorphisms,
  respectively. Every accepted nonlinear map has monomial tangent and the
  same determinant as its linear substitution. These are complete domains
  for those two small algebras, not a general automorphism-count formula.
- The above checks cover 232,714 basis products. Complete small unit domains
  execute 310 multiplication matrices and recover their exact determinant
  images. All 3,243 determinant triples across the fifteen contexts agree
  with both subgroup membership and the three equations.
- A nonlinear autotopism transforms all 64 coefficients of one literal
  multiplication tensor. Using raw input maps or omitting the input
  transposes changes coefficients and rejects. Five invalid checker domains
  reject, and four named semantic discriminators cover the characteristic
  power boundary, swap sign and determinant image.

From the repository root, with CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/nonfrobenius-rectangular-characters/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/nonfrobenius-rectangular-characters/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/nonfrobenius-rectangular-characters
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/nonfrobenius-rectangular-characters --check-source-history
```

Other machines may substitute their CPython 3.12 path. The direct marker is
`PASS_NONFROBENIUS_RECTANGULAR_CHARACTERS no_new_kappa`. Checks write no files
and remain active under optimization. Receipts are emitted to stdout.

The executable is a bounded corroborator. Literal algebra dimension is at
most 36, fields have at most 13 elements, generator-pair enumeration is
capped at 65,536 and unit enumeration at 1,024 elements. All loops are finite
and no recursion or generated code is used. Python allocates managed objects;
these enforced domain bounds replace fixed-memory allocation. The sole small
callback dispatch is the five invalid-domain controls. Every function is
shorter than 60 lines. Warning-strict normal and optimized execution are the
available Python diagnostics; no external static analyzer is required.

## Scope and credit

The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19380662)
records the changed scope of the bit-new-register-model card. The original
physical-mechanism acceptance gate is unclaimed. Base is canonical main
7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority revision 8, selected PR6030.
The selected source-binding positive control passed. SOURCES.json pins the
question and comparison proofs as provenance, with no external runtime input.

Credit Nick Petalas / PR5252 for the nilpotent-algebra question and covariant
normalization precedent; Ali Romman / PR5316 for one-variable truncations and
PR5459 for characteristic-power cutoffs; Armin Pourshafeie / PR5656 and PR5663
for their split and nonsplit product extensions; David Ganz and the retained
tensor-atlas lineage. The present main step derives the different tangent
restriction directly. No predecessor construction, count or scientific replay
is validated here. Recent PR6578 counts Frobenius-family automorphisms; its
formula and family are not extended. Radical filtrations, the binomial
identity, unital isotopy and cyclic-group facts retain classical credit.
Global literature priority is unclaimed.

Live open/account PRs, handoff claims, active Discussions, local reservations,
main README formula/object searches and merged/general-family searches were
checked. The cached broad search covered 626 open PRs, 6,745 Discussion records
and all 8,917 committed local notes at the pinned base. These are overlap
checks, not a novelty certificate; unpublished work and arbitrary historical
code/diffs remain outside them.

Independent human and formal proof-kernel review are unclaimed. Unequal
cutoffs, arbitrary-tensor recognition, chart recovery, coefficient preparation,
native realization, movement, dirty restoration, precision/tape, a complete
paid supplier/caller invoice and the multiplication theorem remain outside
scope. No selected cold replay, Lean or Docker build is needed or run.

## Open next questions

- Determine the tangent restrictions and determinant image for unequal
  non-Frobenius cutoffs. Start with K[x,y]/(x^2,y^3); a complete lift argument
  for those changed relations is missing.
- Recognize this promised equal-cutoff orbit and recover a multiplication
  chart. Start with a unital table and its radical generators; neither a
  certified recognition procedure nor a physical coefficient bill is given.

Structured relevance, first steps and blockers are in TASK.json. Stop here;
no further construction campaign is implied by this side result.
