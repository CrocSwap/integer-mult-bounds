# Kernel-checked split residual interface for selected BIT

Jose Manuel's [PR2195](https://github.com/CrocSwap/integer-mult-bounds/pull/2195)
proves the selected BIT local-ring integration conditionally on completed
callees. Section 1 supplies an explicit split-rank factorization instead of
inferring rank from trace modulo the prime. This package kernel-checks that
algebraic implication and its conjugation behavior. The mathematical
factorization retains PR2195 credit; the contribution is the formal boundary,
not a new supplier or exponent.

## Exact proposition

Let A and M be additive commutative groups, represented by Lean's IntModule
class. Let B:A->M, V:M->A and C:M->M preserve zero, addition and negation.
Assume V(B(a))=a for every a. Put P=BV and define

    D(x,y) = (x-Px+P(Cy), C(Px)+y-C(P(Cy))),
    F(z) = D(z)-z,
    U(a) = (-B(a), C(B(a))),
    W(x,y) = V(x)-V(C(y)),
    L(x,y) = -V(x),     R(a) = (B(a),0).

SplitResidual.lean proves F=UW, LU=id and WR=id. It also proves that the
image of F is exactly the image of U, and U is injective. Every residual
image element therefore has a unique A coordinate. P is idempotent.
With the additional hypothesis C(C(x))=x, D is involutory.

For an invertible additive change of coordinates T, the formalized
residual-conjugation identity is

    T D T^-1 - id = T (D-id) T^-1.

Transformed factors TU and WT^-1 have retractions LT^-1 and TR. This
includes weight/chart changes once their additive bijections are supplied.
No orthogonality or transpose-as-inverse assumption is used. The factorization
and retractions do not require C^2=id; only D-involution uses that premise.
No field, characteristic, trace or diagonalizability hypothesis enters the proof.

## Formal/source correspondence

| Lean roots | Exact meaning and assumptions |
|---|---|
| map_sub, factorization | Distribute the explicit additive maps through the residual |
| left_inverse, right_inverse | The displayed retractions, using VB=id |
| projection_idempotent | P=BV is idempotent |
| image_iff, lifted_injective | Residual image is a uniquely coordinatized copy of A |
| involution | D^2=id, additionally using C^2=id |
| conjugate_factorization, conjugate_left_inverse, conjugate_right_inverse | Factorization and retractions survive an explicit two-sided bijection |
| conjugate_residual | Actual conjugated operation minus identity equals conjugated residual, requiring subtraction preservation |
| integer_example, integer_split_example | Concrete signed-swap instance over integers |

For the source matrices take A=R^r and M=R^m over R=Z/q^w, B,V from the
split image/kernel basis, and C the reversal. Source section 1 states VB=I
and F=[-B;CB][V,-VC]. The formal formula is precisely this block formula
evaluated on a pair, not a renamed conclusion supplied as a hypothesis.

**Remaining external obligations:** construction and authentication of concrete
B,V,C; their module instances and scalar linearity; the determinant-unit lift
from residue-field bases; and a formal dimension/rank theorem. The kernel
proves retractions and image correspondence, not a library assertion
rank(F)=r. Mathematically, R-linear B,V,C and A=R^r identify the residual
image with that free module. Finite fixtures corroborate this specialization
without binding every selected frame in Lean.

The selected word, profile, completed callees, physical hosting, row allocation,
tape/precision and outer analytic transfer remain separate. Their assumptions
are unchanged.

## Reproduce

Python 3.12, standard library, from the repository root:

    python3.12 scripts/research_package.py --package research/lean-split-residual
    python3.12 -I -O -B research/lean-split-residual/verify.py --lean /absolute/path/to/lean

Use Lean 4.34.1. The explicit --lean command recompiles all source in a fresh
temporary directory with warnings treated as errors, then queries all fourteen
roots and rejects axioms outside propext, Classical.choice and Quot.sound.
It never accepts a saved compiler log as evidence. Four material theorem
mutations must fail compilation. A genuinely compiled declaration depending
on an injected axiom must be rejected by the audit.

The registered Python hook runs finite fixtures and export controls.
**It does not run Lean automatically.** The explicit live command was run
during development on Windows with Lean 4.34.1 and CPython 3.12.14.
RESULT.json binds the Lean source SHA-256, also reported by live verification.

Default verification is read-only; --write explicitly replaces RESULT.json.
Git-free exports need this package and the declared PROOF.md input at their
repository-relative paths. The generic runner additionally audits historical
task/source provenance.

## Evidence and controls

The 252 exact modular matrix cases cover m=1..6, every positive r<=m,
three basis charts, primes 3/5 and widths 1/2. They check VB=I, P^2=P,
F=UW, LU=I, WR=I, D^2=I, residue ranks and conjugated identities.
**42 cases have positive rank but zero trace modulo the prime.**
Unit-pivot inversion and separate residue-field elimination use exact integers.

Five controls cover a missing lift sign, absent retraction premise,
transpose-as-inverse, absent C-involution premise, and the rank-zero boundary.
The last is a positive identity boundary, not a rejected counterexample.
The four live Lean mutations change/remove the lift sign, VB hypothesis,
right section and C^2 hypothesis. Git-free CLI tests reject source and
Lean-byte corruption and Boolean/float receipt substitutions, and verify
read-only success. All Python checks remain active under -O.

The source's 636 frames and 531 residuals are not rerun here. These small-ring
controls do not replace its geometry checks. No selected cold replay, hosted
CI, human review, Mathlib matrix theorem or full multiplication theorem is claimed.

## Provenance and overlap

Scientific base 21ec98bfd2e9f27810a8718d95d9b5d19a5df7d7, priority 5;
picker nonce dba52022fd62ead90880b092efd7d755. The prescribed binding baseline
passed. SOURCES.json pins the exact retained source proof, catalogue and
selected record. Original PR2195 head:
3a1cf78a1ba6322129e42d80c50d21765524d612, Jose Manuel (jmbarrancoml).

The card was narrowed to this boundary after reading the already formal HPE
wrapper/label proofs. Local Lean and merged notes, open PRs and targeted
REST queries showed no exact existing kernel treatment. TASK.json records
coverage limits, including the stale Discussion snapshot; no search proves
novelty or exhausts diffs. Claim: PR2195 comment 6199233287.

Retain PR2195's credits to alephnan PR1627, eumemic PR490/source527,
DreamingOfClouds PR589 and the selected construction lineage. The small live
axiom-audit pattern follows our PR2618 verifier; no new audit framework is
claimed. Prepared for ywz65 with substantial OpenAI Codex assistance.
Apache-2.0.

## Open next questions

1. Bind one actual selected rank-divisible-by-prime frame to the kernel.
   Begin with finite-ring B,V,C literals and VB=I; concrete representation
   and authenticated translation remain missing.
2. Connect the image correspondence to a free-module dimension API and
   formalize the determinant-unit basis lift. The rank-library bridge
   remains external to the present proof.
