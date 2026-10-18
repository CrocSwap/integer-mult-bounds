# Exact endpoint penalties for general idempotent labels

**Adversarial mathematical audit; no new kappa.** The two-unit path penalties
in [the historical cancellation audit](../../docs/research/cancellation-audit.md)
§§3 and 6 hold in their stated scope. For arbitrary rational idempotents
`P,Q`, the sharp endpoint-only penalty is instead

    w(P,Q) = rank(PQ) + rank(QP).

This note supplies a self-contained proof, exact counterexamples to stronger
extensions, and source-bound checks of the existing compiler. In particular,
one-sided annihilation can give penalty one; a nonorthogonal pair of rank-two
symmetric projections can give penalty two rather than four. These are
counterexamples to *extensions of* the historical claims, not counterexamples
to those claims or to the selected construction. We make no priority claim
for the elementary idempotent rank identity.

The other audited transfer is the statement in cancellation-audit §3 that a
common `B` component cancels at later stages. Cancellation explains the
matrix difference, but preserving the **signed rank change** also needs rank
additivity. The retained compiler does supply this missing intermediate
justification: its common and variable blocks have complementary supports.
An arbitrary common additive matrix would not suffice.

## Scope, base and provenance

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. Assignment seed **71**, drawn
with operating-system randomness (`secrets.randbelow(100)`); track:
adversarial mathematical audit. [SELECTION.json](SELECTION.json) records three
candidate tasks, overlap checks, the local claim and the time budget. No
pinned coordination issue existed when checked. This is a new audit of a
historical interface, independent of the author's pending packed-verifier
[PR #752](https://github.com/CrocSwap/integer-mult-bounds/pull/752).

The selected record was followed through
[its actual construction](../complex-k492-owner-repair/README.md),
[maintainer review](../../docs/research/community-k492-review.md) and
[assembly certificate](../community-k492-audit/pr626/replay/ASSEMBLY.json).
The accepted conditional value at this base is
`51110230636731/31250000000000000 = 0.001635527380375392`.
The review pins #626 at `660de893d27bb7abd1d5b01b1640207528a5c851`, #622 at
`f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`, and retained #543 at
`2065fe4f72a914d907f1046603f5a36f17018535`. None is changed or recertified here.
Historical frontier language in the cancellation note is not the current
accepted result.

The precise dependencies being compared are:

- cancellation-audit §§3 and 6: diagonal and common-form rank-one endpoints;
- [rank-product-core §1](../../docs/research/rank-product-core.md): general,
  possibly non-self-adjoint rank-one idempotents with **mutual** annihilation;
- [block-core](../../docs/research/block-core.md): uniform higher-rank labels;
- `check_projector_core`, `check_block_projectors`, and the actual time-2 and
  time-5 matrices in `scripts/experiments/rank_product_core.py::_compile`.

[SOURCES.json](SOURCES.json) pins the audited documents, selected-record
context, complete inherited Python import closure and new witness input.
The replay checks these hashes before importing inherited Python code.
There are no third-party Python dependencies or pending-PR code dependencies.

## 1. Kernel decomposition and exact endpoint rank

Work over the rationals in dimension `d`. Assume `P²=P`, `Q²=Q`; write
`p=rank(P)`, `q=rank(Q)`. No symmetry, common form, equal rank or commutation
assumption is needed. Then

    ker(I-P-Q) = (im(P) ∩ ker(Q)) ⊕ (im(Q) ∩ ker(P)).

To prove this, if `(I-P-Q)v=0`, set `a=Pv`, `b=Qv`, so `v=a+b`.
Applying `P` to this equality gives `a=a+Pb`, hence `Pb=0`. Applying `Q`
gives `Qa=0`. Conversely, such `a,b` satisfy `(I-P-Q)(a+b)=0`.
The intersection of the two summands is zero: a vector there is both fixed
and killed by `P`.

The restriction `Q|im(P)` has image `im(QP)`, and likewise `P|im(Q)` has
image `im(PQ)`. Rank-nullity gives summand dimensions `p-rank(QP)` and
`q-rank(PQ)`. Therefore

    rank(I-P-Q) = d-p-q + rank(PQ)+rank(QP).                 (1)

This is the general mathematical proof. The finite checks below corroborate
it and check the implementation; they do not establish its universal scope.

## 2. The sharp path penalty

For an arbitrary finite matrix path `M₀=P,...,Mₖ=I-Q`, with no restriction
on its internal rational matrices, define

    charge = Σⱼ rank(Mⱼ-Mⱼ₋₁),
    excess = charge - (rank(I-Q)-rank(P)).

Rank subadditivity bounds the charge below by `rank(I-P-Q)`. Since
`rank(I-Q)=d-q`, (1) implies

    excess ≥ rank(PQ)+rank(QP).                            (2)

The single-edge path attains equality, so this is sharp among arbitrary
matrix paths with only these endpoints specified. This does **not** assert
that a scalar circuit admits that single edge, or that different paths can
simultaneously attain their minima. Each individual edge's excess is
nonnegative. Thus for edge-disjoint paths in an already valid frame network,
the corresponding weights may be summed above its telescoping signed rank
sum. Shared edges cannot be charged repeatedly.

In particular, a cancelled scalar coefficient or a zero trace is not a
substitute for either product rank. No new path packing, role count, complete
network rank sum, decoder or recursive recurrence is supplied here.

## 3. Which hypotheses give two units?

For `P=Q`, both products equal `P`, giving exactly `2p`; no common form is
needed for the original private diagonal argument.

If an **invertible** symmetric matrix `H` satisfies
`HP=PᵀH` and `HQ=QᵀH`, then

    H(PQ) = (QP)ᵀ H,

so the two product ranks agree. Common-form rank-one labels have weight zero
when mutually annihilating and weight two otherwise. This recovers the
original nonorthogonal triple-line argument. For rank `ell`, the weight is
`2 rank(PQ)` and need not be `2ell`. Equality of the product ranks alone
does not imply existence of a common nondegenerate symmetric form.

[WITNESSES.json](WITNESSES.json) specifies ten exact pairs. Representative
cases, also checked by a separate determinant implementation, are:

| P | Q | rank(PQ), rank(QP) | Exact minimum excess |
|---|---|---|---:|
| diag(1,0) | diag(0,1) | 0,0 | 0 |
| diag(1,0) | `[[0,1],[0,1]]` | 1,0 | 1 |
| diag(1,0) | `[[1/2,1/2],[1/2,1/2]]` | 1,1 | 2 |
| diag(1,1,0) | diag(0,1,1) | 1,1 | 2 |
| diag(1,0,1) | `[[0,1,0],[0,1,0],[0,0,1]]` | 2,1 | 3 |

The one-sided example has nonzero nilpotent `PQ` of trace zero. Swapping its
labels refutes the analogous one-direction bound using `QP`. The last two
rows distinguish partial block overlap from asymmetric block overlap.
For `P=diag(1,0)`, `Q=[[1,1],[0,0]]`, both product ranks are one, but
`H=[[a,b],[b,c]]` must satisfy `b=0` and `a-b=0`; every such `H` is singular.
That example is already given in rank-product-core, and is credited here as
a regression control, not a newly discovered obstruction.

Dropping idempotence also fails: `P=Q=I₂/2` gives `rank(I-P-Q)=0`, whereas
the right-hand side of (1) would be two. The checker rejects this input
before applying (1).

## 4. Tensor factors and common additive blocks

Tensoring both endpoints with a matrix `A` multiplies the difference rank
and each endpoint rank by `a=rank(A)`. Therefore the sharp endpoint-only
penalty is `a w(P,Q)`. Zero-rank spectators are included.

For the actual compiler, write `E=prior`, `F=future`, and `B=I-E`.
Products of the earlier/future idempotents are tensor products here, so
`E,F` are idempotent. The endpoints have the form

    S = ((B⊗I) + (E⊗P)) ⊗ F,
    T = ((B⊗I) + (E⊗(I-Q))) ⊗ F.

The decomposition of the prior space into `ker(E) ⊕ im(E)` makes these
operators block diagonal. Their common block contributes
`rank(B) d rank(F)` to both endpoint ranks, and their variable blocks
contribute `rank(E) p rank(F)` and `rank(E)(d-q)rank(F)` respectively.
The difference has rank `rank(E)rank(F)rank(I-P-Q)`. Consequently

    minimum endpoint-only excess = rank(E) rank(F) w(P,Q). (3)

For the three-factor uniform-rank interface, `rank(E)rank(F)=ell²` at each
stage. It is one in the original rank-one setting. The replay reads actual
compiled time-2 and time-5 endpoints at every stage, including the compiler's
reversed group ordering at stage one (zero-based). It confirms (3) for
rank-one and rank-two asymmetric examples. This is an endpoint audit, not a
replay of full scalar correctness or full compiled edge-rank accounting.

The complementary-support hypothesis matters. With `P=Q=diag(1,0)` and
an arbitrary shared additive block `B=-P`, the endpoints `B+P=0` and
`B+I-Q=I-2P` have direct charge two and signed rank change two: excess zero.
Their difference agrees with the unshifted pair, but their excess does not.
This is a counterexample to transferring the penalty from cancellation
alone, not to the retained compiler's complementary block formula.

## 5. Reproduction and bounded coverage

From the repository root, using Python 3 and its standard library:

```sh
python3 -I -B research/idempotent-path-rank-audit/verify.py
```

Expected output:

```text
PASS_EXACT_IDEMPOTENT_PATH_RANK_AUDIT: 10 named witnesses; 1936 exhaustive pairs; 30 generated pairs; 400 original triple pairs; 24 compiled endpoint pairs
```

The command recomputes and compares every field of
[CERTIFICATE.json](CERTIFICATE.json). `--out /new/path.json` writes a fresh
certificate and refuses to overwrite an existing file. Rational entries use
exact fractions; there is no floating-point rank tolerance or probabilistic
rank test. The certificate retains explicit kernel bases for the named
witnesses. It also records:

- **Independent exhaustive domain:** all `7⁴=2401` integer 2×2 matrices with
  entries in `[-3,3]`, radius `71 % 4 = 3`; all 44 idempotents and all 1936
  ordered pairs. `independent.py` uses explicit 2×2 determinants and no
  elimination or repository rank routine. Product-rank counts are
  `(0,0):129`, `(0,1):152`, `(1,0):152`, `(1,1):1502`, `(2,2):1`.
- **Generated controls:** exactly six pairs in each dimension 2 through 6,
  seed 71, constructed by rational similarity transforms; two unrestricted
  internal matrices per pair. The generator and transcript hash are retained.
  This is fixed finite coverage, not a search or impossibility theorem.
- **Original projection control:** all 400 ordered pairs of the 20 triples
  at `h=6`, checking the common form and zero/two penalty by intersection size.
- **Original input guards:** both directed side-edge orientations reject
  one-sided annihilation, for rank one and rank two. The same labels pass
  without side edges; mutually annihilating pairs pass with side edges.
- **Actual compiler endpoints:** 12 invocation/stage pairs each for rank-one
  and rank-two labels; both endpoint matrices and rank additivity are checked.

The independent determinant census and focused unit checks also run alone:

```sh
python3 -I -B research/idempotent-path-rank-audit/independent.py
python3 -I -B research/idempotent-path-rank-audit/test_audit.py
```

[VALIDATION.md](VALIDATION.md) records the final commands, negative controls,
source portability check, upstream status and overlap refresh. No original
generator, certificate, selected record or upstream file is changed. The
full multiplication theorem and inherited asymptotic assumptions remain
outside this audit; no proof assistant was used.

## Attribution and license

Prepared by **Curtis Dransfield with substantial OpenAI Codex assistance**,
including a separate Codex worker's determinant implementation and review.
That computational independence is methodological, not independent human
review. New code and text are under the repository's Apache-2.0 license.
The historical cancellation argument and general projector/block interfaces
are Douglas R. Colkitt's retained work with their existing AI disclosures.
Their source commit history includes
`6e564879f51ae16f23d392e9e196c605f36d90df` (cancellation note) and
`d55bcd62ceb8f322bcf311a5a66e94c3ac7724f0` (retained interfaces).
The new contribution is the scoped hypothesis audit, directional penalty
rule, complementary-block justification, and independently replayable
boundary examples. It does not depend on or supersede concurrent supplier
constructions.
