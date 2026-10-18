# Finite semantic binding of all cold hyperplane terminals

**All 511 cases pass. No new Lean theorem, supplier or κ.**

The retained [HPE proof note](../hyperplane-end-lean/PROOF.md), section 7,
records a local check of the zero-entrance factorization on all 511 hyperplanes
of `F₂⁹`, but says that checking script was not shipped. This package makes
that finite source-side premise independently reproducible. It checks the
actual canonical-frame circuit and serialized child wrappers against a separate
exact kernel, with global phase and the wrapped chart's spectator retained.
The original local finding keeps its credit; this is a new audit, not priority
for the factorization itself.

## Formal boundary and concrete object

The generic `HyperplaneEnd.exact_cold` in
[Multi.lean](../hyperplane-end-lean/HyperplaneEnd/Multi.lean) assumes:

```text
T_E^-1 = identity,
T_U v = L (C tensor identity) (R v).
```

It then obtains the corresponding factorization of `T_U T_E^-1`.
`cold_hyperplane_width` states that entrance rank zero and terminal rank eight
give width eight and one spectator. These remain conditional Lean statements;
this Python audit does **not** instantiate them with proof terms or run Lean.

For each nonzero 9-bit normal a=1,...,511, the checker enumerates
`U_a={x : parity(a & x)=0}`. Each set has 256 elements. Independent span
enumeration constructs an ordered eight-vector basis and confirms its span
equals U_a. All 511 sets are distinct. This covers every hyperplane of `F₂⁹`,
because a nonzero binary functional has no nontrivial scalar multiples.
The independently constructed ordered basis is also compared with the
producer's nullspace convention; its output is a comparison subject, not
the span oracle. Arbitrary reordered representations are not separately audited.

The pinned producer's `canonical_frame(9, ())` has an empty circuit, hence
the empty entrance and its inverse are identity. For every U_a, its
`canonical_frame(9, basis)` and `lower_child` produce a rank-eight child and
serialized monomials L,R. The checked equation is

```text
L^-1 T_U R^-1 = C_[8] tensor I_2
```

on the full 512-dimensional complex space. The tensor convention is
`x -> (x mod 256, floor(x/256))`. The spectator is **bit 8 in this wrapped
chart**, not necessarily a fixed physical coordinate before the wrappers.
This is not `Exact.lean`'s three C7/two-spectator instances.

Composition convention matters: source `then` applies the left circuit first.
Thus `rmon.then(C8).then(lmon)` is `L C8 R`; the audit executes R⁻¹,
then T_U, then L⁻¹. With the source variable K, the canonical construction
`K.adjoint().then(C8).then(K)` is `K C8 K⁻¹`. The inverse ordering in a
Multi.lean explanatory comment is reconciled by renaming K to its inverse;
the abstract `exact_cold` statement is unaffected. Frozen sources are unchanged.

## Independent acceptance and faithful packed input

The source constructors supply candidates only. They internally use tableau
and zero-state checks, but those checks are **not** the audit's acceptance
oracle. The independent evaluator does not call their state-vector executor,
tableau comparison, source inverse routine or source verifier.

It interprets each literal P/D/X/C/global-phase gate with Gaussian integer
pairs, retaining a common denominator rather than performing data-dependent
cancellation. Serialized inverse monomials are evaluated pointwise: for
`M e_x = i^phi(x) e_(Gx xor b)`,

```text
(M^-1 v)_x = i^(-phi(x)) v_(Gx xor b).
```

Every permutation is independently checked as a 512-element bijection;
quadratic symmetry, phase parity, translations and gate domains are validated.

The reference is a closed-form kernel, not another execution of the C gates.
For x,y with the same spectator bit, its unnormalized matrix entry is

```text
16 * (-i)^popcount(x xor y),   common denominator 256.
```

Cross-spectator entries are zero. This follows from eight factors of
`(1+i)I+(1-i)X`: `(1+i)^8=16` and `(1-i)/(1+i)=-i`.

The check uses one **encoded basis sum**, `v_x=B^x`, with B=2^18. This is not
a claim that equality on an ordinary single input determines an operator.
The encoding is faithful for these explicitly bounded integer matrices:

1. Each basis-column numerator starts with component bound one. An unnormalized
   C gate sums four signed real/imaginary components, enlarging that bound by
   at most four. Monomial permutations and i-phases preserve it. Eight C gates
   give bound `4^8=65536` for each numerator matrix component.
2. The reference has component bound 16. Both sides have denominator 2^8, so
   each component of their difference has integer digits bounded by
   `D=65536+16=65552 < B-1`.
3. If a row has a highest nonzero difference digit d_j, then its leading
   magnitude is at least B^j. All lower digits together have magnitude at most
   `D*(B^j-1)/(B-1) < B^j`. They cannot cancel it.
4. Equality of every real and imaginary packed output therefore forces every
   matrix difference entry to vanish, including implicit zeros. Every supported
   gate is complex-linear, so equality of the basis columns extends to all
   complex vectors. No real-linear/conjugating operation is admitted.

The primary checker verifies the radix guard and the eight-C denominator.
All 511 comparisons cover **261,632 complex-linear input columns and
133,955,584 matrix entries logically**, without materializing those matrices
or executing each column separately. [RESULT.json](RESULT.json) stores source
pins, coverage, bounds and the deterministic digest of per-normal records.
Hashes compact the receipt; actual acceptance compares the exact packed
Gaussian integers after the bound checks.

## Controls and reproduction

For the normal-1 case, five circuit mutations must reject: left global phase,
right spectator translation, reversed C direction, C on the spectator, and
omission of one C gate. The first four fail operator equality; omission fails
the declared denominator/width contract. An additional radix-2 alias
`2 - 1*2 = 0` demonstrates why a bound is necessary, and the unsafe radix is
explicitly rejected. The CLI tests run the smallest/mixed normals 1 and 511
and independently require rejection of omitted-case and unsafe-radix receipts.
They also reject integer/float and integer/Boolean aliases: receipt comparison
uses a type-preserving canonical JSON representation, not Python's coercive
decoded-value equality.

Python 3.10+ and the standard library, from the repository root:

```sh
python3 -I -O -B research/cold-hyperplane-semantic-binding/verify.py
python3 -I -O -B research/cold-hyperplane-semantic-binding/test_verify.py
python3 scripts/research_package.py --package research/cold-hyperplane-semantic-binding --check-only
python3.12 -B scripts/research_package.py --package research/cold-hyperplane-semantic-binding
```

Expected primary output:

```text
PASS_COLD_HYPERPLANE_SEMANTIC_BINDING hyperplanes=511 columns=261632 entries=133955584 controls=5 global_phase spectator_preserved no_new_kappa
```

`--probe` runs only the two named smallest/mixed cases and never claims full
coverage. Default replay is read-only; `--write` regenerates the receipt after
the complete source and semantic checks. No dependency installation is needed.

## Assignment, overlap and limitations

Base `d78fe4bbb6f6b769e39586f8bb3ba8c31a31fd3a`; assigned
`independent-verification`, OS nonce `3b261ab51d51856a178fbaca68514f8a`;
chosen card `formal-interface-lemma`, scope key `e3ffea67887eeb4c396c`.
[TASK.json](TASK.json) records the refined object, pre-computation card,
source history and stop rule. The prescribed baseline binding check passed.
Both first probes and the complete domain passed; no pivot was used.

The entry survey and immediate concrete-object overlap check distinguished
the [three non-cold-pair audit](../hpe-lean-semantic-binding/README.md) from
this family, and the retained cold14 packages' fourteen rank-four endpoints
from these 511 rank-eight endpoints. No matching all-511 cold binding was
found; this is not proof of novelty. No directly fitting open handoff was
found, so the assigned theorem-to-certificate binding method was retained.
Claim: https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18917564.

This supplies external finite evidence for hE/hU in the stated operator model,
not a numeric-mask-to-Lean adapter or proof term. It does not check any actual
emitted helper's unit row/zero column, multi-tail chronology, recipes, disjoint
footprints, whole-call hosting, precision/tape, all-size or analytic obligations.
Wrapper execution and all physical charges remain inherited and unrepriced.
No new moment, a<D/E improvement, cold supplier, selected-record change, full
cold replay or multiplication theorem is claimed.

## Open next questions

Can the generic cold factorization be instantiated in Lean from an explicit
full-rank basis instead of external finite checks? A useful first step is one
normal-1 frame in a `C256 tensor C2` model, with the actual ordered canonical
monomial chart and composition convention. This would reduce a conditional
source-to-formal gap without changing a budget. The blocker is a missing
numeric-mask/Frame adapter and generic canonical-frame semantic theorem;
this package neither supplies those nor runs a Lean build. Structured fields
are in [TASK.json](TASK.json).

## Credit and license

Jeremy Kothe / jeremykothe2 supplied the HPE formalization
https://github.com/CrocSwap/integer-mult-bounds/pull/593; DreamingOfClouds
supplied the generic multi-gate/cold specialization
https://github.com/CrocSwap/integer-mult-bounds/pull/599 and retained
Lemma A/G/compiler lineage. The independent non-cold semantic audit by
commdata2338 https://github.com/CrocSwap/integer-mult-bounds/pull/1415 is
credited and not reused as an oracle. icekylinx's direct-delivery package
retains the compiler and its predecessor notices; the original cold14
source-side checks keep their credit. No predecessor files are copied or edited.

Prepared by Aaron Wang / navinor, **with help from chatgpt**, including
separate read-only AI mathematical/code review. No independent human or Lean
kernel review is claimed. New work is Apache-2.0.
