# A tensor-width volume obstruction to isolating the two-image prefix

Prepared by Cinna Davis with substantial OpenAI Codex assistance. Apache-2.0.
Written theorem with exact corroboration; no Lean, independent human review,
new κ, or complete small-unit exclusion is claimed.

## 1. Completed interface, rather than an intermediate prefix

Let V=C^8. Fix the actual permutations U and V_0 of lee-phys's PR4688:
U is CNOT from bit 0 to bit 2, and V_0 swaps bits 0 and 1. Define

`C = ((1+i)/2) I + ((1-i)/2) X_0`,
`S e_x = i^popcount(x) e_x`, `P=S U S`, `Q=S V_0 S`.

For any base letter g, write `g_f=g^(tensor f)`. Scalar coefficients act
**after** individual letters have been tensorized. The two source prefixes are

`F_f = C_f (U_f + 2 V_0,f) C_f`,
`F'_f = C_f (P_f + 2 Q_f) C_f`.

PR4688 proves the first family's invertibility and two-call implementation
with one initially zero scratch array and a copy/mix/erase schedule. Yiyang's
PR4710 supplies the phase repair. Dugongue's PR4743 supplies a different,
reversible two-input triangular interface with this prefix off diagonal.
None of those statements promises the following completed interface:

`(x,z_1,...,z_s) -> (F_f x, z_1,...,z_s)`                 (1)

for arbitrary independent x and arbitrary dirty z_j. The same distinction
applies to F'_f. We test exactly (1). We may also allow independent unitary
outputs on the helper banks, since they have unit absolute determinant.

## 2. An enlarged uniform-word model

Fix any finite number of array banks, each of dimension d_f=8^f, and one
finite word whose register coefficients, base letters, bank count and word
length do not change with f. Permit these full-state linear operations:

1. Any fixed complex register mixing M, acting as `M tensor I_(d_f)`.
2. Any fixed invertible 8-by-8 base address matrix B, acting as B_f on a
   selected bank. Several banks or products are permitted.
3. Arbitrary unitary full-state operations, even width-dependent ones.

This grants much more than the source engine's free address permutations
and phases, and includes every unitary paid C direction and its inverse.
It does not price those extra grants or call them physically free. They
make the impossibility statement stronger. No nonlinear operation or
width-dependent nonunitary mixing coefficient is included.

All banks are arbitrary independent inputs; all final banks are prescribed.
There is no owned zero input, omitted output, or discarded input-dependent
garbage. If the final map is invertible, every full-state factor is invertible:
a singular square factor cannot occur in an invertible product. Thus allowing
singular mixing syntactically cannot evade the determinant argument for this
completed contract. This reasoning does not apply on a proper clean-input
subspace, which is why the original clean-prefix construction is compatible
with the result.

**Uniform volume lemma.** For every word in this model with an invertible
output, its normalized absolute log determinant is affine in f:

`log |det T_f| / 8^f = a + b f`.                           (2)

Indeed a register mixing contributes `log |det M|`, independent of f. A
single-bank address letter has
`det(B^(tensor f)) = (det B)^(f 8^(f-1))`, by induction from the Kronecker
determinant formula, so contributes `(f/8) log |det B|`. A unitary full-state
letter contributes zero. Determinants multiply, proving (2). For the narrower
source game with only unitary address letters, b=0. Bank permutations and
permitted free input/output frame changes have the same affine profile.

This is an elementary determinant invariant. The new source-specific content
is the profile below and what it excludes for these completed interfaces.

## 3. Exact determinant profile of both retained prefixes

The permutation `R=U^-1 V_0` has cycles

`(0)(4)(1 2 5 6)(3 7)`.

Its four power traces are `(8,2,4,2)`. Consequently R_f has eigenvalue
multiplicities

`m_1 = (8^f + 4^f + 2*2^f)/4`,
`m_-1 = (8^f + 4^f - 2*2^f)/4`,
`m_i = m_-i = (8^f - 4^f)/4`.                             (3)

These follow from the four order-four character projectors: traces tensorize,
so their numerators use 8^f, 2^f, 4^f and 2^f. They can also be obtained
directly from the lengths of R_f's permutation cycles. All four
multiplicities are positive for every f>=1.

The paid C_f and U_f are unitary. Factor the middle sum as
`U_f (I+2R_f)`. The +1 eigenspace contributes 3, the -1 eigenspace
contributes -1, and an i/-i pair contributes `(1+2i)(1-2i)=5`. Hence

`D_f := |det F_f| = 3^(m_1) 5^(m_i)`.                    (4)

For the repaired word, `P^-1 Q = S^-1 R S` as actual matrices with absolute
phases. It has exactly the same spectrum at every f. P_f and both paid
factors are unitary, so `|det F'_f|=D_f` too. Projective equality would
not suffice for this assertion; the source phase convention is retained.

In particular:

| Width f | Dimension | exponent of 3 in D_f | exponent of 5 in D_f |
|---|---:|---:|---:|
| 1 | 8 | 4 | 1 |
| 2 | 64 | 22 | 12 |
| 3 | 512 | 148 | 112 |

If (2) held, its second difference at these three widths would vanish.
Clearing the denominators 8,64,512 gives

`D_3 D_1^64 / D_2^16 = 1`.

But (4) gives the exact ratio `3^52/5^16`, which is not one. Thus **neither
prefix can be isolated as (1)** by any finite uniform word in the enlarged
model. The number of unitary paid calls is unrestricted. The contradiction
still holds with any number of independent unitary helper targets, since
their absolute determinants are one. It is unaffected by allowed free
frame changes, which add only an affine profile.

In the source's narrower unitary-address game, already widths one and two
contradict a constant normalized determinant:

`D_2 / D_1^8 = 5^4/3^10 != 1`.

This is a completed-module obstruction. It is not a lower bound on every
continuation of the original prefix and does not exclude five-in-fourteen.

## 4. Tuning the two mixing coefficients cannot repair this contract

The same conclusion holds for
`C_f(alpha U_f + beta V_0,f) C_f`, and for the repaired P,Q pair,
for **every fixed complex alpha,beta with alpha beta != 0**.

Put t=beta/alpha. If t is one of ±1,±i, (3) makes the mixture singular
already at width one and indeed at every width. Otherwise all logs below
are finite. Set

`A=log|1+t|`, `B=log|1-t|`, `E=log|1+t²|`.

Using (3), the normalized log determinant of the middle mixture is

`log|alpha| + (A+B+E)/4 + (A+B-E)/(4*2^f) + (A-B)/(2*4^f)`. (5)

It is bounded and converges. If it were affine in f for every positive
width, or even every sufficiently large width, its affine slope would
be zero. The two distinct decaying sequences in (5) then force
`A=B` and `A+B=E`. The first equation gives Re(t)=0; write t=i y with
real y. The second becomes `1+y²=|1-y²|`, forcing y=0. This contradicts
alpha beta != 0.

The classification deliberately leaves the single-image cases alpha=0 or
beta=0 available. Their normalized determinant is constant and the original
single-branch word is implementable with its ordinary calls and scalar mix.
The theorem does not infer impossibility of arbitrary pairs of permutations;
it uses this exact order-four spectral distribution.

## 5. Why the existing dirty-target port is a positive control

PR4743's two-input port has the actual block form

`T_f = [[C_f, 0], [F'_f, C_f]]`.

Its determinant is `det(C_f)^2`, with absolute value one. F'_f is
off diagonal and is dependent information about the first input; both
diagonal channels remain present. This port is therefore compatible with
(2) and is not (1). Extracting F'_f as an independent diagonal output while
returning the other arbitrary input unchanged would be a new contract.

Similarly a nonunitary compensating helper output such as an inverse-volume
partner can remove the volume obstruction. The determinant lemma supplies
no construction of that partner, its Gaussian compatibility, its precision,
or its invoice. Clean initialized scratch, nonuniform width-dependent
coefficients, changing the number of banks with f, nonlinear operations,
or a different global continuation also lie outside the proved exclusion.

## 6. Executed evidence and limits

The independent standard-library verifier authenticates five main inputs
with SHA256 and Git blob ids. It checks the source permutation definitions
without importing its rank engine, constructs the coordinate maps separately,
and checks the repaired ratio's exact phase conjugacy. Direct tensor-cycle
enumeration at widths one through four agrees with (3). Separate exact
Gaussian-rational matrix elimination at widths one and two agrees with (4)
for both prefix variants. These checks operate on the individually tensorized
monomial branches; they do not tensorize a sum.

It also checks a unit-volume triangular positive case, allowed affine-profile
examples, the complex-coefficient identities used in section 4, the singular
coefficient-one control, and the available single-image case. The finite
checks corroborate the proof; the all-width and all-coefficient statements
come from sections 2–4. No large hook-rank replay, native supplier suite,
five-in-fourteen schedule audit, selected cold replay or Lean build is run.

The source scalar program, the phase repair, the triangular native ports,
their rank and conditioning evidence, and all their original attribution
remain unchanged. This result adds a volume invariant for one new completed
dirty-helper boundary, without changing the selected conditional frontier.
