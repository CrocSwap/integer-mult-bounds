# Universal block identities for the dirty interval proof

**Independent algebraic verification; no new kappa.** All 16 ordered phase
pairs and the completed parent map/inverse in Charles Bethin's
[PR1278](https://github.com/CrocSwap/integer-mult-bounds/pull/1278) hold as
universal noncommutative block-polynomial identities. One opaque block contains
all reused deeper scratch, with arbitrary dimension independent of the data
dimension. This replaces sampling for this particular algebraic obligation;
it does not replace PR1278's support induction or prove the multiplication theorem.

The checker uses **only four one-sided invariants**:
`P e_y = Q e_y = e_y` and `e_x^T R = e_x^T S = e_x^T`.
All other blocks are independent indeterminates. No inverse relation between
P/R or Q/S is imposed, no factors commute, and no word loses repeated symbols.
Four explicit invertible shear counterexamples show that dropping any one of
these four invariants can invalidate the displayed family while preserving
the other three. This is a boundary of this sufficient hypothesis set, not
a classification of every possible alternative hypothesis.

## Precise proposition and source binding

Work on `D_x direct-sum D_y direct-sum D_z direct-sum W`, with the three copies
of D distinct and W the entire shared scratch. D and W may have different
dimensions; W may be zero. A and B are arbitrary endomorphisms of D. Let

```
H = e_z B e_x^T, E = e_y A e_z^T, G = EH,
U = I+H, V = I+E, F = I+G.
```

The disjoint ports give `E^2 = H^2 = HE = 0`; consequently
`V^-1 U^-1 V U = F`, with inverses obtained by negating E, H, G.
For independently chosen P,Q,R,S satisfying the four invariants above define

```
Z = [P, QU, P U^-1 VU, QF],
L = [R, U^-1 S, U^-1 V^-1 UR, F^-1 S].
```

Then every `Z_j L_i` equals the following entry (row j, column i):

| | i=0 | i=1 | i=2 | i=3 |
|---|---|---|---|---|
| j=0 | PR | P U^-1 S | PR - E U R | PS - G |
| j=1 | QUR | QS | Q V^-1 UR | QS + Q V^-1 H |
| j=2 | PR + E U R | P U^-1 VS | PR | PVS |
| j=3 | QR + G | QS - Q V^-1 H | Q V^-1 R | QS |

For actual source phases, substitute `P=P_b`, `Q=Q_b`, `R=P_a^-1`,
`S=Q_a^-1` from PR1278's proof. Left-child prefixes fix external y; right-child
prefixes never read their target y. Left-child inverse prefixes preserve
their source x; right-child inverse prefixes fix external x. Thus the four
invariants hold. The stronger source/target and disjoint factor-support
conditions in PR1278 remain necessary inputs to its **separate support
induction**; this package does not show they can be dropped from that theorem.

`vendor/PR1278-PROOF.md` retains the exact audited statement at commit
`06b8c006891ae78abe24b30d2fe9d8c188deafe8`. `SOURCES.json` records Git blobs,
SHA256 and base `dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`. No predecessor
executable is imported. PR1278 already proves the all-size squarefree interval
claim and supplies 108 finite constrained-matrix checks. Credit for that
theorem and those formulas remains with Charles Bethin; this package supplies
a code-disjoint universal algebra check and isolates weaker local hypotheses.

## Why the symbolic certificate is universal

Each otherwise unrestricted block receives a distinct typed symbol. A polynomial
is an exact integer coefficient map on **ordered words** of symbols; multiplication
concatenates and addition combines only identical words. Symbols carry D/S
input/output types, so rectangular compositions are checked. The fixed
column/row is filled with the appropriate identity and zero blocks.

Matrix multiplication expands every entry by distributivity. The checker finds
identical coefficient maps for both sides of all 18 identities. Distinct free
words form a basis, so a zero residual is a polynomial identity, valid under
every compatible linear-map substitution. This is not an inference from a
finite selection of matrices. The short hand calculation uses the nilpotent
relations above, `PE=QE=E`, and `HR=HS=H`; these imply all non-adjacent
phase reductions. Adjacent and same-phase reductions cancel complete U,V,F
maps. The 4-by-4 block shape retains a single shared scratch space throughout.

This is an algebraic argument with an exact Python normal-form certificate,
**not a proof-assistant formalization**. Its trusted surface includes the
expression transcription, typed polynomial arithmetic and source correspondence.
The separate dense oracle and corruption controls address implementation faults.

## Reproduce and inspect

From the repository root, standard-library Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/universal-dirty-phase-identities
```

Expected final marker:
`PASS_REGISTERED_RESEARCH_PACKAGE research/universal-dirty-phase-identities outcome=completed`.
Standalone commands are `python3 -I -O -B` followed by this package's
`verify.py`, `check_dense.py`, or `test_package.py`.

- `CERTIFICATE.json`: all 18 exact normal forms, empty residuals, four
  invariant-removal residual families, and 18 additional source-template checks.
- `DENSE-CHECK.json`: independently multiplied full matrices for 540 substitutions
  across `(dim D, dim W) = (1,0),(1,1),(2,1),(1,3),(2,3),(3,2)`, plus four explicit
  nonzero residual matrices with A=B=1. All four modified P/Q/R/S maps in these
  witnesses are invertible shears. The finite oracle is not the universal proof.
- Six package tests cover optimized read-only-file relocation at a path containing
  spaces, source/certificate/dense-receipt corruptions, noncommutative word-order
  mutation, byte-identical regeneration and refusal to overwrite an existing output.
- Arithmetic controls explicitly retain `AB != BA`, retain `AA`, and reject
  the wrong sign of the completed parent shear. No quotient silently forces
  commuting or squarefree words.

No selected supplier cold replay, rounded-leaf substitution, sharper coefficient
bound, hosting/compiler integration, new precision charge or exponent follows.
The repository's selected conditional PR1094 result stays unchanged.

## Open next questions

Mechanize the source-to-template invariant argument in a proof assistant, then
reuse the 18 equalities. This matters because universal local algebra alone
does not discharge dispatcher induction or factor-support preservation. A first
step is to formalize the four invariant-preservation statements for one shear
and its inverse, with a shared scratch direct sum. The blocker is the absent
machine-checked binding to the recursive dispatcher. PR1278's proposed precision
substitution remains a separate task with separate rounded-leaf obligations.

## Credit

Prepared for **Philipp / mightyOil** with substantial **OpenAI Codex
(GPT-6 Astra) assistance** in scope selection, algebra, code, validation and
writing. Charles Bethin supplied PR1278's induction and phase formulas; Hanson
Sun supplied PR1244's noncommuting obstruction/open question and PR1085's prefix
audit; Chafik Boukhalfa supplied PR628/905's dispatcher and prefix framework;
Gareth Davidson supplied PR877's perturbation context. No literature-priority
or independent human-review claim is made. New work is Apache-2.0; retained
source notices and license remain unchanged.
