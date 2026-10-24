# Negative association of three binary full-guard events

**A dimension-uniform proof with independent exact corroboration. No new kappa.**

For three pairwise orthogonal rank-one idempotents over the binary field, the
three full-guard indicators under one uniformly sampled complete header are
negatively associated in every dimension `m >= 3`. In fact, any two nonconstant
increasing real functions on disjoint, nonempty sets of these indicators have
strictly negative covariance.

This answers Open next question 1 of Nick Petalas's
[PR #4777](https://github.com/CrocSwap/integer-mult-bounds/pull/4777).
The new step is an all-dimension **union-versus-singleton bound** using only the
known marginal and pair formulas and nonnegativity of the triple probability.
Section 4 proves why the checked event types exhaust negative association.
The counting laws and conjunction inequality remain predecessor results.

Prepared for lee-phys with substantial OpenAI Codex assistance. Apache-2.0.
Independent human and proof-kernel review are unclaimed.

## 1. Domain and cited results

Let `m >= 3` and let `U_1,U_2,U_3` be rank-one idempotents on `F_2^m`, with
`U_i U_j = 0` whenever `i != j`. Put `P_i = I-U_i`. Choose `G` uniformly from
the whole group `GL_m(F_2)`. Event `E_i` means that every leading principal
minor of `G P_i G^-1`, of orders 1 through `m-1`, is nonzero. All three events
use the same header `G`.

The three image lines and their common-kernel complement give a simultaneous
basis with `U_i=e_i e_i^T`. Right multiplication of `G` by this fixed change
of basis permutes the complete header domain. Permuting the distinguished
lines likewise preserves that domain, so the event vector is exchangeable.
Write

```text
n=m-1, X=2^m, A=9^n-2*7^n+5^n,
p=Pr(E_i), p2=Pr(E_i and E_j), p3=Pr(E_1 and E_2 and E_3).
```

The following are cited results, not new claims:

```text
p  = 3^n / [(X-1)2^n],                        (#4227)
p2 = A / [(X-1)(X-2)2^(2n)],                  (#4261)
p3 < p*p2 for every m >= 3.                   (#4777)
```

See the retained [marginal proof](../projector-header-density/PROOF.md),
[pair proof](../corankone-pair-header-law/PROOF.md), and
[conjunction proof](../corankone-triple-block-correlation/PROOF.md).
The [triple law from #4275](../corankone-triple-header-law/PROOF.md) supplies
the exact `p3` used by the verifier and the conjunction proof. These source
files are pinned at this package's base in `SOURCES.json`. No predecessor
executable or live source file is imported by `verify.py`.

## 2. A quantitative pair deficit

Set `r=(7/9)^n`, `s=(5/9)^n` and `delta=1-p2/p^2`. The pair formula gives

```text
delta = [(X-1)(2r-s)-1]/(X-2).
```

We have `0<s<r` and `X>2`. Hence

```text
delta > [(X-1)r-1]/(X-2)
      = r/2 + (Xr-2)/[2(X-2)]
      > r/2,
```

since `Xr=2*(14/9)^n>2`. In particular `p2<p^2`. Furthermore,

```text
0 < p = (3/4)^n / (2-2^(-n)) < (3/4)^n < (7/9)^n = r.
```

All denominators are positive. These inequalities hold throughout the stated
domain without a finite cutoff or limiting argument.

## 3. The missing union inequality

The required covariance gap is

```text
Delta = Pr(E_1 or E_2) Pr(E_3) - Pr((E_1 or E_2) and E_3)
      = p(2p-p2) - (2p2-p3)
      = p^2[(2+p)delta-p] + p3.
```

Using `p3>=0`, `delta>r/2` and `r>p` yields the new explicit bound

```text
Delta > p^2[(1+p/2)r-p] >= p^2(r-p) > 0.
```

Thus, for every `m>=3`,

```text
2p2-p3 < p(2p-p2),
Cov(1_(E_1 or E_2),1_E3) < -p^2[(7/9)^(m-1)-p] < 0.
```

No triple closed form or positive triple probability is needed. In particular,
`m=3` is included although `p3=0`. The exact gaps at `m=3,4` are `421/2352`
and `199/2688` respectively.

## 4. Complete negative association

Put `Z_i=1_Ei`. Negative association requires

```text
Cov(f((Z_i)_(i in I)),g((Z_j)_(j in J))) <= 0
```

for disjoint index sets `I,J` and coordinatewise nondecreasing real functions
`f,g`. With three coordinates, nonempty disjoint sets have sizes `1,1` or
`2,1`, up to exchange. A function on one bit is `a+bZ_i` with `b>=0`.
The nonempty proper increasing subsets of a two-bit square are exactly

```text
{11}, {10,11}, {01,11}, {01,10,11}.
```

Their indicators are AND, the first coordinate, the second coordinate, and OR.
Every increasing real function on that square is a constant plus a nonnegative
linear combination of those indicators: if its distinct values are
`t_0<...<t_l`, then

```text
f = t_0 + sum_(j=1)^l (t_j-t_(j-1)) 1_(f>=t_j).
```

Each nontrivial superlevel set is one of the four sets above. Their covariances
with the remaining coordinate are all strictly negative:

```text
AND:          p3-p*p2 < 0                       (cited #4777),
coordinate:   p2-p^2 < 0                        (Section 2),
OR:           2p2-p3-p(2p-p2) < 0                (Section 3).
```

Covariance linearity proves the theorem. If both functions are nonconstant,
at least one coefficient from each is positive, giving strict negativity.
Constant functions or an empty index set give zero. This covers arbitrary
increasing functions, not only intersections of the events. QED.

## 5. A control showing why the new step matters

Negative pair and AND covariances do not suffice for negative association.
Consider the exchangeable three-bit distribution assigning `13/100` to `000`,
`8/100` to each weight-one state, `21/100` to each weight-two state, and zero
to `111`. Then

```text
p=1/2, p2=21/100, p3=0,
p2-p^2=-1/25, p3-p*p2=-21/200,
Cov(OR(Z_1,Z_2),Z_3)=1/40 > 0.
```

This is a control distribution, not a header counterexample. The independent
increasing-event checker rejects it; a pair/AND-only checker would accept it.

## 6. Exact verification and the cited conjunction lemma

`verify.py` uses Python 3.12's standard library, exact integers and rational
numbers, and explicit checks active under `-O`. It imports no external data.

- Complete `GL_3(F_2)` and `GL_4(F_2)` enumeration constructs the conjugated
  requests by matrix multiplication and tests each leading minor by binary
  elimination. All eight atom counts match the cited moments. Group orders
  are 168 and 20,160.
- Independent enumeration of factor increments `y*x^T` gives convolution
  counts on the one-, two-, and three-kernel safe partial-Gram spaces.
  Evaluation of all 64 three-kernel characters recovers #4275's signed
  eigenvalue multiplicities. Walk counts match the formulas through dimension
  25 where their domains are defined.
- All six increasing subsets of a two-bit square are enumerated. Every
  nontrivial block-versus-singleton covariance and the new quantitative bound
  is checked exactly at every `3<=m<=256`.

The verifier also independently checks the finite component and constants of
the *cited* conjunction proof. For clarity, its all-dimension argument is
restated here with #4777's credit. Write

```text
B=27^n-2*21^n+15^n,
T=27^n-6*21^n+6*19^n-6*17^n+16*15^n-18*13^n+9*11^n-2*9^n.
p3/(p*p2) = (T/B)*(X-1)/(X-4).
```

Strict convexity of `t^n` at `9,7,5` gives `B>0`; its formula also gives
`B<27^n`. The inequality `T>=0` follows from its walk-count interpretation.
After the terms of bases 27 and 21, the absolute coefficients of `T` sum to
57 and all bases are at most 19. For `n>=42`, `57*19^42<21^42` and `19/21<1`
therefore give `T<27^n-5*21^n<B-3*21^n`. Dividing by `0<B<27^n` yields
`T/B<1-3*21^n/B<1-3r`. The upper bound is positive
by `3*7^42<9^42`. For `X>=16`, `(X-1)/(X-4)<=1+4/X`, and
`2/2^n<r` for `n>=2`, since `(14/9)^2>2`. Thus the ratio is below
`(1-3r)(1+r)=1-2r-3r^2<1`. The remaining forty dimensions `3<=m<=42`
have strictly positive integer gaps `(X-4)B-(X-1)T`, checked exhaustively.

This is a replay of the existing conjunction proof, not a new theorem about
that comparison. Section 3's new union proof is analytic for all dimensions.
Finite header counts and the extra sampled dimensions are corroboration,
not extrapolation to an infinite domain.

Controls reject the pair/AND-only false positive, identical events, independent
events falsely claimed strictly negatively associated, malformed atom laws, a missing
finite-GL normalization, and a changed triple spectrum.

Reproduce from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/corankone-triple-negative-association --check-only
python3.12 -B scripts/research_package.py --package research/corankone-triple-negative-association
python3.12 -I -B research/corankone-triple-negative-association/verify.py
python3.12 -I -O -B research/corankone-triple-negative-association/verify.py
```

The direct command prints `PASS_CORANKONE_TRIPLE_NEGATIVE_ASSOCIATION` and a
deterministic exact-check summary. It writes no files and needs no Git. The
registered metadata check separately binds historical source provenance.

## Scope, provenance and credit

The theorem requires three orthogonal kernel lines over `F_2` and a complete
uniform `GL` header distribution. Four or more indicators, odd fields,
nonorthogonal kernels, and restricted/nonuniform header collections are not
covered. No header-selection algorithm, physical caller, supplier admission,
or multiplication exponent follows. The selected kappa remains unchanged.

Base: canonical main `4c0a359d88f22f05189d51f48387750b801a45d4`.
`TASK.json` records the explicit mathematical assignment as a changed scope of
`formal-interface-lemma`; there is no Lean claim. `SOURCES.json` pins retained
proofs and orientation metadata as provenance, not runtime inputs. The counting
proofs were read; a new independent proof of every predecessor is not claimed.
The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19141140)
records overlap and progress.

Credit Nick Petalas for #4227, #4261, #4275, #4767, and #4777, including the
explicit open question; Cinna Davis for the BIT request context; source527,
commdata2338 and Jose Manuel for the normalizer/closure lineage; and Chris R /
Clear1nsight for the earlier counting context credited by #4777. No predecessor
executable is copied. New proof and verification: lee-phys with substantial
OpenAI Codex assistance, Apache-2.0. No independent human or proof-kernel
verification is claimed.

## Open next questions

1. Does negative association hold for four orthogonal binary kernel lines?
   Start by listing the increasing events for the `2+2` and `3+1` splits and
   using the known four-event law. These additional event types are not covered
   by the three-variable reduction; an intersection product bound is insufficient.
2. Does the three-event result hold over odd finite fields? Start with the
   three-kernel partial-Gram transfer and exact small-field atom laws before
   conjecturing a sign. The binary safe-state group and pair-deficit estimate
   do not automatically generalize.

Structured first steps and blockers are in `TASK.json`.
