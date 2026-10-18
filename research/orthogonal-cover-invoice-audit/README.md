# Audit of the binary cover order in the selected #626 finite invoice

**Adversarial mathematical audit; no new κ.** The selected invoice uses the
correct order of the group preserving the standard binary **bilinear** dot
product in dimension 73. A self-contained counting argument and an independent
exhaustive implementation agree. Recomputing the nine finite guards reproduces
the committed receipt exactly.

This audit also establishes a concrete scope limit: replacing this group by
all of `GL(73,2)` exceeds the retained physical-row coefficient, **21,867 >
20,161**, although the other eight guards still pass. Conversely, four
incorrect smaller group factors pass all nine upper-bound guards; they must
be rejected by the group definition, not by those inequalities. The intact
production code computes the correct factor. These controls are **not**
counterexamples to the selected construction or evidence of acceptance by
its full verifier.

## Reproduce

From the repository root, with Python 3.11+ and no third-party dependencies:

```sh
python3 -I -B research/orthogonal-cover-invoice-audit/verify.py
python3 -I -B research/orthogonal-cover-invoice-audit/test_verify.py
```

Expected verifier output:

```text
PASS_ORTHOGONAL_COVER_INVOICE_AUDIT dimensions=1..7 guards=9 controls=5 kappa=unchanged
```

The second command runs eight tests. Verification checks source hashes and
receipt bindings, recomputes every certificate field, and compares the whole
result with [CERTIFICATE.json](CERTIFICATE.json). To regenerate only this
package's certificate, add `--write-certificate /tmp/cover-certificate.json`.
No repository file is changed during ordinary verification. Assertions are
not used, so the checks also execute under `-O`.

## Object and provenance

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. OS-random assignment seed: **65**.
The [claim](CLAIM.md) records three candidates and overlap checks.
[SOURCES.json](SOURCES.json) pins the consumed bytes, the reviewed #626/#623/
#622/#543 heads, and the selected-record/assembly/invoice/owner chain. The
selected source manifest independently binds both production files audited:

- `research/complex-k492-owner-repair/code/invoice_allcold.py`, function `run`;
- `research/complex-k492-owner-repair/code/assemble.py`, finite-invoice checks.

The consumed invoice is the maintainer's
`research/community-k492-audit/pr626/replay/mixed-global/audit/PREFIX-AND-INVOICE.json`.
Its admitted scalar costs, physical stock and owner profile are inputs here;
this audit does not regenerate or independently admit the supplier.

## Counting argument

Write `B(x,y) = Σ x_i y_i` over `F₂`, and let `Ω=(1,…,1)`. Then
`B(x,x)=B(x,Ω)`. Nondegeneracy makes Ω the unique vector with this property,
so every isometry fixes it.

For odd `n=2r+1`, `B(Ω,Ω)=1`. Thus the whole space is the orthogonal direct
sum of `⟨Ω⟩` and `U=Ω⊥`. On U, the form is alternating and nondegenerate,
of dimension `2r`. Restriction gives an isomorphism from the dot-product
isometry group to `Sp(U)`: every isometry fixes Ω, and every symplectic map
of U extends by fixing Ω.

In a nondegenerate alternating space of dimension `d=2r`, choose the first
nonzero basis vector in `2^d−1` ways. Its partner with pairing one has
`2^(d−1)` choices, because pairing against a nonzero vector is a nonzero
linear functional. Their plane is nondegenerate, leaving an alternating
orthogonal complement of dimension `d−2`. A symplectic map is uniquely
determined by its ordered symplectic basis images. Consequently

```text
S(0) = 1
S(d) = (2^d − 1) 2^(d−1) S(d−2)
|Iso(F₂^(2r+1), B)| = S(2r) = 2^(r²) ∏[j=1..r] (2^(2j)−1).
```

For the even-dimensional comparison, choose e with `B(e,Ω)=1`.
Now Ω is isotropic, the plane `⟨Ω,e⟩` is nondegenerate, and its complement
U is alternating of dimension `n−2`. Every isometry has uniquely the form

```text
Ω ↦ Ω
e ↦ e + u + cΩ
v ↦ Sv + B(u,Sv)Ω  (v ∈ U),
```

where `S ∈ Sp(U)`, `u ∈ U`, and `c ∈ F₂`. Directly checking all pairings
proves these maps are isometries; the decomposition and preservation of Ω
give the converse. Hence the even order is `2^(n−1) S(n−2)`.
This agrees with the existing even-dimensional discussion in
`notes/three-stage-cover-complex.tex`, rather than applying the odd formula
to an even space.

These are standard group facts, not new group theory. See Daniel Dugger,
[Involutions in the topologists' orthogonal group, Propositions 2.3–2.4](https://pages.uoregon.edu/ddugger/invto121616.pdf),
for the distinction from quadratic-form orthogonal groups and these orders.
That reference is not needed at runtime. The proof above supplies the
all-dimensional order argument; the finite enumeration below is a separate
check, not a formal proof of the general formula.

## Independent finite evidence

The enumerator appends every odd-weight vector orthogonal to the existing
prefix. Its identity Gram matrix makes the prefix linearly independent,
and its complete length-n leaves are exactly the ordered orthonormal bases.
No order formula, orbit representative, memoization or symmetry quotient is
used to obtain the counts. Every prefix count and first-column completion
histogram is recorded in the certificate.

| Dimension | Complete ordered orthonormal bases |
|---:|---:|
| 1 | 1 |
| 2 | 2 |
| 3 | 6 |
| 4 | 48 |
| 5 | 720 |
| 6 | 23,040 |
| 7 | 1,451,520 |

For odd n > 1 the apparently legal unit vector Ω has no complete extension:
its complement contains only even-weight vectors. This catches the tempting
but incorrect step of treating every unit first column as extendable. The
test suite independently enumerates **all** binary matrices through dimension
4 using scalar Gram entries, checks that every isometry fixes Ω, and exhibits
64 matrices with unit columns but only 6 isometries in dimension 3.

Completed domain: every ordered orthonormal prefix in dimensions 1–7,
including all 1,475,337 complete bases across these dimensions. Stopping rule:
finish dimension 7, with no randomized search or extrapolation. The assignment
seed selects the audited object, not a subset of bases.

## Exact invoice arithmetic and controls

Put `g=|Iso(F₂^73,B)|`, `W=7670g`, `s=520704g`, `L=4711738180507680g+64`,
and `C=64·74³=25934336`. The audited expressions are

```text
router    = C (L+1) (W+1)²
literal   = 2·2^30000 W² + 8s + 4W + 4 + 32·73
mass      = s + 2^100000
precision = 32·73·mass²
tape      = 2·mass + 18
row       = 2·bit_length(W) + 9909 + 252 + 1024.
```

The new engine uses exact integers and imports no production code. It derives
g by the pair-count recurrence, also checks the algebraically equivalent
product `2^36 ∏[j=0..35](2^72−2^(2j))`, and binds the scalar inputs to the
selected receipt. Results include:

| Quantity | Recomputed value | Retained condition |
|---|---:|---|
| g bits | 2,628 | Exact order above |
| W bits | 2,641 | Exact stock above |
| Router bits | 7,985 | router < 2^30000 |
| Literal bits | 35,282 | literal < 2^100000 |
| Precision bits | 200,012 | precision < 2^210000 |
| Row coefficient | 16,467 | row < 20,161 |

The certificate also records logical, mass, tape, local-primitive and halving
checks. These are the **nine finite invoice guards**, not the full set of
47 assembly inequalities or an independent moment computation.

Five controls replace g by 1, the dimension-72 bilinear order, `S(70)`, the
odd part of g, or `|GL(73,2)|=∏[j=0..72](2^73−2^j)`. All five are rejected
by the exact group check. The first four pass all upper-bound guards; GL fails
only the row guard. Separately, with all other inputs held fixed, inflation
`g ↦ 2^t g` has its last passing integer t at **1846** (row 20,159), and
first failure at **1847** (row 20,161). Since bit length increases by t and
all guards are monotone in g, the two endpoint checks certify the whole
nonnegative integer-t range. This is a sensitivity result for this invoice,
not a paid replacement cover, a revised constant proposal or a new κ.

## Scope, validation and credit

No defect was found in the selected group factor or its finite arithmetic.
The result adds independent evidence for one accounting obligation and
explicit wrong-model controls. See [VALIDATION.json](VALIDATION.json) for
commands actually run. The source/code/receipt integrity checks, implementation
mutations, strict-boundary controls and isolated relocated replay complement
the mathematical enumeration.

All supplier correctness, owner geometry, right-translation realization,
uniform compilation, common-label/mutable-basis realization, whole-call
hosting, normalized residuals, semantic precision, fixed-tape/exact recovery,
bit-supplier H1–H5 and analytic-transfer assumptions remain inherited. No
full cold replay, full repository suite, Linux CI, Lean proof or practical
speedup is claimed. The selected certificate and `upstream/` are unchanged.

Credit: Jeremy Kothe's #622/#623 construction and finite accounting; Chafik
Boukhalfa's #626 owner map and replay; icekylinx's compiler/invoice lineage;
DreamingOfClouds' finite helper audits; Rohan Arun's #559 recurrence review;
eumemic's #543 bit supplier; the maintainer review and all retained predecessor
notices. #717 independently explores moment/invoice sensitivity and program
permutations; none of its code or results is imported here.

Prepared for **Sricharan Vagvala (@theon199)** with substantial **OpenAI Codex** assistance
in task selection, mathematical analysis, code, verification and writing.
Apache-2.0, matching the repository. No independent human peer review is claimed.
