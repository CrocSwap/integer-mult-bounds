# Exact degree 881 for the one-slot doubled centre Gram

For the pinned eight-by-112 query of [#4958](https://github.com/CrocSwap/integer-mult-bounds/pull/4958),
the full one-slot doubled centre Gram `A_1` has **minimal-polynomial degree
exactly 881** in characteristic zero. Every invertible `alpha I + beta A_1`
with `beta != 0` has a scalar-polynomial inverse of minimum degree **880**.
The common fixed Bell vector embeds `A_1` into every positive tensor width,
so those widths inherit degree lower bounds 881 and 880, respectively, with
the latter applying when the affine inverse exists and `beta != 0`.

This answers the one-slot upper-annihilator question left open by #4958
(degree at least 409) and [#5120](https://github.com/CrocSwap/integer-mult-bounds/pull/5120)
(degree at least 410). It supplies the complete upper certificate and matching
lower certificate, rather than another increment from a sampled block.
Canonical claim: [Discussion #5142](https://github.com/CrocSwap/integer-mult-bounds/discussions/5142).

## Statement and evidence

Write `B=4 A_1`. [CERTIFICATE.json](CERTIFICATE.json) contains 21 monic integer
polynomials in ascending coefficient order. Their monic LCM over Q is the
minimal polynomial `P` of B; that of `A_1` is `4^-881 P(4x)`. The SHA256 of
the compact JSON array of P's ascending integer coefficients is
`0008f43f81d1cc41666af45918b4c92b0dcfd4fc491b1f08c9419b3c30d7efd6`.

[PROOF.md](PROOF.md) derives the complete reduction of the 2,097,152-dimensional
operator to six Bell-label representatives. Thirteen source-verified signed
root permutations and the Walsh transform cover all 512 labels. For each
nonzero representative, two commuting involutions split the block into four
integer 1024-dimensional sectors. The remaining representative is checked on
all 512 eight-by-eight matrices.

| Bell representative c | Label orbit size | Degrees for t=0, s=+1/-1 | Degrees for t=1, s=+1/-1 |
|---:|---:|---:|---:|
| 0 | 2 | 9 (whole block) | — |
| 1 | 224 | 71 / 71 | 101 / 101 |
| 3 | 224 | 126 / 88 | 126 / 88 |
| 7 | 16 | 39 / 39 | 27 / 27 |
| 30 | 14 | 26 / 32 | 26 / 32 |
| 128 | 32 | 19 / 19 | 23 / 23 |

[verify.py](verify.py) checks every compressed port against its literal two-term
Bell embedding (286,720 columns). It verifies upper annihilation with arbitrary
precision integer Horner evaluation on complete coordinate-orbit covers, then
proves matching component degrees with nonzero Hankel determinants modulo
2^31-1. Gaussian elimination and modular Bareiss condensation agree on each
determinant. Finally it recomputes the LCM, degree and coefficient hash. Ten
failure controls exercise altered polynomials, source ports, phases, symmetries
and determinant edge cases. No numerical eigensolver is used for acceptance.

The optional [discover.py](discover.py) uses FLINT to propose the component
polynomials. Verification does not import it, require FLINT, or call a matrix
minimal-polynomial routine. A separate clean Python 3.12 environment with only
the registered dependencies is used for the author replay. This is an
author-checked computational proof, not proof-kernel or independent human
acceptance.

The normal and optimized author replays passed in 115.49 and 113.48 seconds,
respectively, under Python 3.12.12 on macOS arm64. Their deterministic receipts
are identical; [RECEIPT.json](RECEIPT.json) records that output for inspection.
The verifier recomputes the evidence and does not read this receipt as a premise.

## Reproduce

From the repository root, with Python 3.12, `numpy==2.4.1` and `sympy==1.14.0`:

```sh
python3.12 -B scripts/research_package.py --package research/exact-one-slot-gram --check-only
python3.12 -B scripts/research_package.py --package research/exact-one-slot-gram
```

The registered runner executes full normal and optimized (`-O`) checks, with
isolated imports, warnings treated as errors and bytecode writes disabled.
Each command has a 600-second limit. Each emits a JSON receipt containing the
source hash, component degrees, Hankel determinants, moment hashes, orbit
coverage and global polynomial hash, followed by `PASS_EXACT_ONE_SLOT_GRAM`.
Assertions are not used for acceptance.

For direct or Git-free source-export replay, run these from the exported root:

```sh
python3.12 -I -W error -B research/exact-one-slot-gram/verify.py --emit-receipt
python3.12 -I -W error -B -O research/exact-one-slot-gram/verify.py --emit-receipt
```

Candidate regeneration is optional and is outside the bounded generic replay.
In a separate environment containing `numpy==2.4.1` and `python-flint==0.9.0`:

```sh
python3.12 -B research/exact-one-slot-gram/discover.py --output /tmp/one-slot-candidate.json
```

An existing output resumes completed sectors; use a fresh path to regenerate
everything. The producer labels its result `CANDIDATE_ONLY`. It took about
20 minutes in the author environment; the exact verifier is substantially
shorter. Discovery timing is not a multiplication benchmark.

## Scope, sources and limitations

Scientific base: `a5df48c55ea806d7952b65acc9c76d878ff09b13`, current main when
the fresh clone was made on 2026-10-23. [SOURCES.json](SOURCES.json) pins exact
source bytes and Git blobs. The source query SHA256 is
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.
The task catalogue and selected record are historical provenance; later
priority updates do not repin the scientific inputs. The actual query and
predecessor attribution files are declared export inputs.

[TASK.json](TASK.json) records the explicit change from the generic
`formal-interface-lemma` card to the handoff's finite exact decoder-algebra
question, the donor budget, overlap coordination and next questions. This is
a scoped obstruction/result about scalar polynomial decoding. There is no
upper annihilator for tensor width greater than one, no bound on arbitrary
ADD circuits or rational/matrix-valued decoders, and no complete accounting
for access, storage, routing, precision or restoration. No supplier admission,
outer multiplication theorem, new kappa or selected-frontier change follows.

## Open next questions

1. **Higher tensor widths.** Is there a uniform upper-degree bound, and what
   new spectrum already appears at width two? Start by deriving joint
   Bell-label blocks with the root coefficient applied once and classifying
   which are equivalent. The missing complete similarity classification is
   the blocker; repeating a small lower-bound experiment would not settle it.
2. **A decoder outside scalar polynomials.** Can a concrete alternative improve
   the actual interface after every cost is charged? Start with an explicit
   decoder and its access, storage, routing, precision and restoration bill.
   The present degree theorem supplies neither that implementation nor a
   general circuit impossibility result.

The structured questions and blockers are also in TASK.json; neither is claimed
as follow-up work by this package.

## Credit

Prepared by Krzysztof Wojt with substantial OpenAI Codex assistance. A delegated
AI worker supplied bounded read-only claim/symmetry inventories and a reduction
consistency review; the primary agent regenerated the used maps and covers.
These are not independent human reviews.

JoyboyBrian concurrently obtained the same six Bell-label representatives and
released an exploratory feasibility gate in
[this handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144258).
It reports no upper polynomial, exact degree or published package. The handoff
was read during submission refresh after this package's derivation; its
independently obtained symmetry reduction is credited, and its exploratory
local scripts are not imported.

Ali Romman's #4958 and #4720 supply the actual query, Bell decomposition and
earlier obstruction; Nick Petalas's #5120 supplies the two-block degree-410
strengthening. Their certificates are not replayed as new evidence here.
The doubled representation comes from [#1719](https://github.com/CrocSwap/integer-mult-bounds/pull/1719).
The historical source and compiler lineage, including icekylinx's Gauge44
work, retain their credit in the unchanged
[predecessor notice](../centre-polynomial-cache-limits/NOTICE.md) and its
retained notices. New work is Apache-2.0; original notices and license text
remain unchanged.
