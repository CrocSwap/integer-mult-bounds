# Unavoidable scalar primes in uniform resonant image recovery

For the frozen resonant channel of [PR #4797](https://github.com/CrocSwap/integer-mult-bounds/pull/4797),
exact uniform recovery of its **canonical orthogonal input projection** needs
the odd scalar primes **3, 5 and 7**, and these primes suffice. This is a
statement about a precisely defined coefficient ring and uniform linear
program, not a physical lower bound for division or a complete supplier.

Dugongue's [PR #4885](https://github.com/CrocSwap/integer-mult-bounds/pull/4885)
already proves the all-width rank, support projectors and explicit polynomial
pseudoinverse. Those results are credited predecessors, not new claims here.
The new result shows that the odd denominators cannot all be removed by a
different finite uniform monomial-linear decoder with the same orthogonal
output contract. It distinguishes an actual arithmetic obligation from a
possibly inconvenient choice of inverse polynomial.

Canonical claim: [Discussion #1166, comment 19138314](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19138314).
Base: `b91956876e5b4122fd89179f1b57557ff8378f15`, priority revision 7.

## Exact contract and theorem

Let `A` be the 256 actual three-bit monomial words with rational coefficients
`±1/16` in the source `TARGET.json`. A word `g=(p,s)` acts by
`g e_j = i^s(j) e_p(j)`. Every actual central phase is retained. For positive
width `f`, evaluation is

```
A_f = sum_g a_g g^(tensor f).
```

Coefficients occur once, outside tensor powers. For a set `S` of odd rational
primes define `R_S = Z[i,1/2,{1/p : p in S}]`. In particular `S=empty` is the
Gaussian dyadic ring. Let `P_f` be the orthogonal projection onto `im A_f*`,
the canonical accessible input subspace. The desired output from observation
`z=A_f y`, for every arbitrary `y in C^(8^f)`, is exactly `P_f y`.

**Theorem.** There is a fixed finite monomial-linear decoder with scalar
coefficients in `R_S`, valid at **every positive even width** `f=2,4,6,...`,
if and only if `{3,5,7}` is contained in `S`.

“Fixed finite” means a finite straight-line algebraic program independent of
`f`: its scalar coefficients and its base monomial words are fixed. A lifted
base word may of course be executed by an address loop over `8^f` entries.
The program may copy registers, add them, multiply by scalars in `R_S`, and
apply lifted monomials. It can use any fixed finite number of zero registers
or independent arbitrary dirty inputs, with the declared dirty returns.
Its designated output must be `P_f y` for all those independent inputs.

Let `H` be the group of all fourth-root monomial three-bit base matrices.
For necessity we grant this entire group, a larger alphabet than the actual
affine/phase engine. Sufficiency
uses the actual words of `A` and their products/adjoints, already certified
free in #4797. No inversion of an arbitrary register operator is a free
instruction. This theorem is not about arbitrary oblique representatives,
width-dependent scalar constants/circuit families, approximate output,
nonlinear bit arithmetic, or a decoder given extra correlated paid responses.
It determines scalar availability, not the number or runtime of divisions.

## Source-bound projector certificate

Write `C=A* A/16`. The authenticated #4885 checker reconstructs the exact
integer group algebra on 21,504 actual monomials. Its degree-18 polynomial is
`p(t)=t q(t)`, with

```
q(0) = -40131624960 = -2^19 * 3^7 * 5 * 7,
C q(C) = 0.
```

This integer identity, not a finite tensor-width sample or modular guess,
is replayed here. `C_f` is Hermitian positive semidefinite. Therefore

```
P = I - q(C)/q(0)
```

evaluates to `P_f` at every positive width: it is zero on the zero eigenspace
and one on each nonzero eigenspace. We use that source-bound polynomial to
compute exact coefficients; the rank formula itself need not be rerun.

### The correct quotient for even widths

For every even width, `[g]` and `[-g]` have the same evaluation. Define
`bar H = H/{I,-I}`. The projector coefficient of an even class is the **sum**
of the two signed-word coefficients, not a choice of one representative.
The checker normalizes a word by subtracting either 0 or 2 from every phase
exponent, so its first phase exponent lies in `{0,1}`. The central class of
`iI` remains different from identity: at width `2k` it evaluates to `(-1)^k I`.

The full source projector has 21,056 nonzero word coefficients. Its even
quotient has 10,528 nonzero classes and minimal integer coefficient-clearing
denominator

```
3870720 = 2^12 * 3^3 * 5 * 7.
```

One explicit class simultaneously witnesses all three odd primes:

```
permutation = (0,1,3,2,4,5,7,6)
phase_i     = (0,0,1,3,0,0,3,1)
coefficient = 1243/3870720.
```

The numerator is coprime to the denominator. Each separate signed word has
half this coefficient. `verify.py` recomputes all exact rational coefficients,
the entire denominator histogram and this witness from the pinned source
annihilator. The denominator is measured in the correct all-even quotient,
not in one concrete matrix or in the unreduced inverse polynomial.

### Why all-even evaluation is faithful

Take finitely many distinct classes represented by nonzero matrices `g_j`.
The tensors `u_j=g_j tensor g_j` are nonzero and pairwise distinct. Indeed,
`g tensor g=h tensor h` implies `h=alpha g` and `alpha^2=1`, hence precisely
`h=±g`. To see the proportionality directly, apply a nonzero coordinate of
`g` to the first factor of the equality; then substitute the proportionality
back into the equality.

Choose a complex linear functional `ell` on the matrix-tensor space for
which all numbers `alpha_j=ell(u_j)` are distinct and nonzero. Such a choice
avoids a finite union of proper hyperplanes. If
`sum_j c_j g_j^(tensor 2k)=0` for every `k>=1`, applying `ell^(tensor k)` gives
`sum_j c_j alpha_j^k=0`. For `k=1,...,m`, the resulting Vandermonde matrix is
invertible, including the nonzero factors `alpha_j`. Thus every `c_j=0`.

This proves faithfulness of the family of all positive even evaluations on
finite elements of `C[bar H]`. It does not assert faithfulness at any one
width. In particular quarter phases must not be discarded; restricting to
widths divisible by four would be a different quotient and a different task.

## Necessity for every allowed decoder

By induction over its instructions, each output of a fixed finite linear
program is a finite sum of lifted monomial words applied to each independent
input, with coefficients in `R_S`. At the designated output, independence of
the arbitrary auxiliary values forces their transfer coefficients to vanish
under every required evaluation. Zero scratch and restored dirty scratch
cannot change the coefficient of `z`. Consequently there is a finite
`L in R_S[H]` such that the output is `L_f z` for all widths in the contract.

Exact recovery from `z=A_f y` implies `(LA)_f=P_f` at every positive even
width and for every `y`. Since `A` is dyadic, `LA` has coefficients in `R_S`.
All-even faithfulness forces equality in `C[bar H]`. The coefficient at the
explicit witness class must therefore equal `1243/3870720` in `R_S`.

The rational elements of `R_S` have denominators supported only at 2 and
primes in `S`: take real and imaginary parts of a Gaussian-integer numerator
over such an integer denominator. Since the witness is reduced, each of
3, 5 and 7 must belong to `S`. This proves necessity for all allowed decoders,
not only for the particular pseudoinverse in #4885.

## Sufficiency uses an actual decoder

Being able to write `P` in a ring alone would not establish recovery from
`A y`. Instead use the explicit source inverse polynomial

```
R(t) = -(q(t)-q(0))/(t q(0)),
L = R(C) A* / 16.
```

The exact scalar identity `t R(t)=1-q(t)/q(0)` gives `LA=P`. All coefficients
of `q` are integers, `C` has dyadic coefficients, and division by `q(0)`
introduces exactly the possible odd primes 3,5,7 and no others. Therefore
this particular finite decoder lies in `Z[i,1/2,1/3,1/5,1/7][H]` and is
constructively available whenever those primes are inverted. `verify.py`
checks the scalar polynomial identity and the actual `q(0)` factorization
separately from the projector-denominator calculation.

This is a uniform linear program with a finite number of actual monomial
passes; it is not a claim that fixed-rational scalar operations cost nothing.
Dugongue's [PR #4908](https://github.com/CrocSwap/integer-mult-bounds/pull/4908)
already implements bounded-word fixed-rational rounding with a specified
both-shifts ABI. That algorithm and its conditional tariff are credited
inputs, not newly implemented here. Exact complex-linear algebra and rounded
finite-precision execution are different contracts.

## Validation and limits

Run the registered package with Python 3.12:

```
python3 scripts/research_package.py --package research/resonant-recovery-scalars
```

The primary checker authenticates #4885's executable/source coefficient before
loading it, replays its exact integer annihilator, and derives the new quotient
and localization certificates. Explicit checks remain active under `-O`.
`independent_modular.py` does not import the primary checker or execute the
source checker. It parses only the pinned literal polynomial and target,
uses packed permutation/phase bytes, a separate right-generator group
enumeration, and modular Horner arithmetic modulo `8505=3^5*5*7`. It checks
the full modular annihilator and independently recovers the combined signed
witness residue 2754. Its local valuations are:

| Prime | Raw numerator valuation | Raw denominator valuation | Surviving denominator valuation |
|---|---:|---:|---:|
| 3 | 4 | 7 | 3 |
| 5 | 0 | 1 | 1 |
| 7 | 0 | 1 | 1 |

Modulo 243,5,7 the raw numerator residues are 81,4,3, respectively. These
nonzero finite residues prove the stated exact numerator valuations, with
the exact denominator supplied by the pinned polynomial. This independent
finite check corroborates the odd-prime witness; it does not replace the
primary unbounded-integer certificate or the written all-even proof.
It also rejects omission of a negative-word representative, a changed
polynomial constant, a collapsed quarter phase at literal width two, and an
incorrect monomial inverse. The primary checker has six additional ring,
quotient and inverse-polynomial controls.

| Obligation | Status |
|---|---|
| All-width rank and explicit support inverse | Inherited from #4885 |
| Correct even-phase quotient and faithfulness | Proved here |
| Necessary scalar primes for any decoder in the declared grammar | Proved here |
| Same primes sufficient for an actual recovery decoder | Constructive source polynomial, checked here |
| Fixed-rational rounded scalar implementation | Credited #4908, conditional on its ABI and precision contract |
| Independent canonical Gaussian target encoders | Unknown |
| Missing target complement, physical preparation/routing/storage/restoration | Unknown |
| Complete paid profile, compiler funding, supplier admission and new κ | Not established |

The original retained owners and complements of #4797 are unchanged. This
coefficient-ring obstruction gives no universal lower bound for native
restoration and excludes no approximate, oblique or width-dependent decoder.
The exact source replay and independent finite checks are not human or
proof-kernel acceptance. A separate read-only agent reviewed the proof and
both implementations and independently ran optimized checks without finding
a blocker. No selected-frontier or frozen predecessor is changed.

## Provenance and overlap

All-width source head: #4885 `46ece2fbfb6d7c23c82c42797855deac7204235e`.
Its executable and target are live inputs pinned by raw bytes in `SOURCES.json`.
The #4797 source channel and #4825 width-four rank are preserved through that
lineage. Credit Dugongue for the all-width projector/inverse and #4908
(`7662641e7016a3e38826fd5a9e73c30db751452b`) arithmetic; Nick Petalas for
#4825; JoyboyBrian for #4797; and Yiyang #4710, lee-phys #4688 and Jacob
Sussman #4628 for the phase-prefix and actual free-alphabet lineage.
Prepared by JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.

Initial overlap covered 317 open PRs, 4064 Discussion records and all 6636 local
notes. Exact resonant/dyadic terms had no matching result; this is advisory,
not a novelty certificate. #4902/#4932/#4943 concern distinct coded-native
caller obligations. The former all-even rank task was explicitly replaced
because #4885 had already solved it. No scalar rounding algorithm is repeated.

## Open next questions

1. Can a different, oblique exact accessible-coordinate contract avoid these
   primes while retaining the same amount of information? Begin with an
   explicit uniform decoder/section; changing the output contract invalidates
   the necessity proof above and requires a new consumer ledger.
2. Can a complete chronological consumer afford the known rational recovery
   and all missing coordinates? Specify canonical encoders and every physical
   preparation, complement, restoration and compiler charge before expansion.
   The present ring criterion does not supply that consumer or a saving.
