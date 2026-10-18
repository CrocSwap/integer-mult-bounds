# Three identical rational targets still need nine calls with arbitrary dirty workspace

**Written extension of a retained computer-assisted theorem. No new kappa or
supplier admission.** In the formal abelian rank-one call model below, three
copies of any invertible rational 3-by-3 target require exactly nine paid
calls, even with any finite number of arbitrary dirty registers that must be
restored. The rational paid frames are unrestricted: no finite alphabet,
numerator bound or denominator bound is imposed.

This removes the finite-alphabet restriction from the three-identical-target
case of [PR1604](https://github.com/CrocSwap/integer-mult-bounds/pull/1604).
It does not extend the retained theorem to three *different* targets with
dirty workspace. The positive construction search must therefore change
another premise, such as the number of active targets or the address model.

## Exact statement and model

Use the group algebra over F2 of the additive group of rational 3-by-3
matrices. Its formal symbols satisfy `[A][B] = [A+B]`. A paid factor is

```text
D_N([A]) = I + ([A] - 1) N,
rank_Q(A) = 1,
N in M_R(F2), rank_F2(N) = 1, N^2 = N.
```

For every finite `R >= 3`, invertible `T in M_3(Q)`, and rank-three
idempotent `P in M_R(F2)`, the minimum number of factors for

```text
product_j D_Nj([Aj]) = I + ([T] - 1) P
```

is **nine**. In a binary basis adapted to P, this endpoint has three
diagonal copies of `[T]` and `R-3` identity entries. Those additional roles
have arbitrary initial contents and are restored exactly. Equality means
equality of every formal coefficient, not equality after one finite
specialization. Free scalar GL changes are represented by conjugating the
projectors; arbitrary free address maps between calls are outside the model.

## Proof and predecessor boundary

[PROOF.md](PROOF.md) supplies the written argument. It uses two named
published inputs, with source pins recorded in [SOURCES.json](SOURCES.json):

- Ali Romman's [PR468](https://github.com/CrocSwap/integer-mult-bounds/pull/468),
  retained in [bit-three-register-lower-bound](../bit-three-register-lower-bound/README.md),
  excludes eight calls on exactly three scalar registers. Common rational
  left multiplication reduces an identical invertible target T to I3.
- woklerx's [PR1456](https://github.com/CrocSwap/integer-mult-bounds/pull/1456)
  at `83b6ad2ace819a96128131a3600ee914a66dd0dd` bounds the sum of target
  ranks when the paid frames have at most one rational relation. Its
  statement explicitly permits arbitrary register count and zero targets
  on restored dirty roles. Together with the low-frame-span argument, it
  proves that two active copies of T still need six calls with arbitrary
  dirty workspace.

David Govea’s [PR720](https://github.com/CrocSwap/integer-mult-bounds/pull/720),
at `a942c0ae1b463710ca535c1fba1b07b6431b5a86`, removes target triangularity
for exactly three registers. It does not admit extra dirty registers and is
not a dependency of this identical-target extension.

The new reduction applies the augmentation ideal to the actual finitely
generated subgroup H of paid frames. It does not reduce rational matrix
entries modulo two or use the augmentation of the divisible ambient group.
For a hypothetical eight-call word with rational frame span d, it gives
`dim span(N_j) <= 8-d` when `T = 0 in H/2H`; otherwise P is in that scalar
span and its dimension is at most `9-d`.

Low frame spans `d <= 4` are excluded by an explicitly restated extension
of the predecessor's projection argument. For `d >= 5`, only scalar spans
of dimension at most four remain. A scalar span of dimension at most three
restricts to the three-dimensional image of P. In dimension four, P is the
sum of three mutually orthogonal rank-one projectors. The fourth projector
then gives either a three-register quotient or an invariant split into one
active target and two active targets with dirty workspace. The disjoint
call requirements are respectively nine or `3+6`.

Nine calls attain the bound: write T as its three rank-one column matrices,
and apply all three on each active coordinate role. A binary change of
basis gives the construction for every rank-three P.

## Evidence and reproduction

The new proof is a written theorem relying on the two named inputs. The
package's finite checks corroborate its new algebraic reductions and the
nine-call construction; they are not an enumeration of rational frames or
a machine-checked proof of the universal statement.

```sh
python3.12 -B scripts/research_package.py --package research/bit-identical-three-targets-dirty
python3 -I -O -B research/bit-identical-three-targets-dirty/verify.py
python3 -I -O -B research/bit-identical-three-targets-dirty/independent.py
```

The primary checker classifies all 120 binary rank-one idempotents on
four coordinates: 56 active-image cases, 28 common-dirty-kernel cases,
24 invariant-line cases and 12 invariant-hyperplane cases. It checks
28 rank-three projector decompositions, 489 rank-one span members with
multiplicity and 144 induced call partitions. Forbidden rank-one
nilpotent and rank-two paid-projector controls reject.

The separate checker enumerates all 65,536 binary 4-by-4 matrices and
reproduces those cases, counts and decompositions without importing the
primary implementation. It also replays the full formal nine-call word
at register counts 3, 4 and 7 for a nondiagonal integer target with
determinant 25, including scalar conjugations that mix active and dirty
coordinates. All three omitted-call controls reject, as does a corrupted
case-count fixture. The certificate records the complete finite cases;
verification requires no network fetch.

Consult the checker output and registered replay receipt for execution
details. This package does not rerun PR468's 21,317,520-order
computer-assisted theorem, the selected supplier's cold replay, native
physical admission, or a Lean proof. Separate proof review and separate
finite implementations were performed by AI agents, not independent human
reviewers. [TASK.json](TASK.json) records the research scope.

For the proposed three-target dimension-three kernel, even the ideal
overhead-free normalized moment is

```text
9 * (1/3)^(1-a) / 3 = 3^a.
```

It cannot be below one for positive a. Extra restoration, routing or
precision costs cannot rescue this particular route. This is a statement
about the declared kernel model, not a lower bound for integer
multiplication or for other supplier contracts.

## Open next questions

- **Four identical targets in eleven calls.** A four-target construction
  would escape the three-target theorem and has favorable ideal moment
  `(11/12) * 3^a`. A first bounded step is an exact formal search with
  four active roles and a specified scalar alphabet containing at least
  two noncoordinate projectors, followed by a full paid invoice for
  any witness. The three-target argument fails at a
  precise point: four active coordinates can have `a_i b_i = 1` for every
  i while `a dot b = 0`, so it no longer forces an invariant coordinate
  line or complementary hyperplane. No eleven-call construction or
  physical admission is asserted here.
- **Different three-dimensional targets with dirty workspace.** The
  augmentation identity has several target exponent classes instead of
  one tensor `t tensor P`. A first step is to derive the corresponding
  scalar-span restriction. The present identical-target reduction does
  not establish that case.

## Credit and license

Ali Romman's PR468 supplies the retained three-register theorem and the
projection/rank tools. Its model and flag-method lineage is credited to
eumemic's [PR288](https://github.com/CrocSwap/integer-mult-bounds/pull/288)
and huxint's [PR203](https://github.com/CrocSwap/integer-mult-bounds/pull/203).
woklerx's PR1456 supplies the arbitrary-register one-relation theorem.
Tuafo's PR1604, head `c5f5bef84f6648d5573f801c283e01a333ea5f89`, is the
preceding finite dyadic ternary-frame result and remains separately
credited; its finite census is not reused as an unrestricted-rational
proof. Prepared for Tuafo with substantial OpenAI Codex assistance,
including GPT-6 Astra at maximum reasoning for derivation, independent
implementation and proof review. New material is Apache-2.0.
