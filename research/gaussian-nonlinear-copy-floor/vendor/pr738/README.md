# Gaussian E8 copy floor from clique ranks

**Research note and scoped negative result. No new kappa.** Every asymmetric
scalar binary decoder of the 60-line Gaussian E8 fitting pattern has abstract
copy charge at least **40 Gaussian rank units, or 80 rational rank units**.
This holds for arbitrarily many totals, with the pairing-rank cost of #446.
It does not assume symmetric decoding or full-rank totals.

The [proof](PROOF.md) extends the averaged clique argument of concurrent
[#703](https://github.com/CrocSwap/integer-mult-bounds/pull/703) to the Gaussian
geometry posed in [#620](https://github.com/CrocSwap/integer-mult-bounds/pull/620).
All 640 maximum nonorthogonal cliques have size 12. Each receives weight
1/192. Exact flat-pair checks prove this weighting is valid, and a rank-one
pairing between a rank-two and a rank-three flat proves it is sharp for this
uniform weighting. The actual minimum decoder cost remains between 40 and 60.

Under #595's separate deficit identity and #620's Gaussian rank scaling,

    D/T <= 120(s-1) - 80s = 40s-120.

Thus the three-stage Gaussian format has no positive deficit even before
helper, access, frame, restoration and recursive expenses. This excludes that
specific route to a positive supplier saving. Five or more stages remain
unresolved. The previous notes report a symmetric CP-SAT lower bound of 9 and
a separately solver-reported fitting-matrix minrank of 15. Neither solver
claim is needed for this proof or replay.

## Reproduce

From the repository root, with Python 3.10 or later and no third-party packages:

```sh
python3 -B research/gaussian-clique-copy-bound/verify.py
```

Expected output:

```text
PASS_GAUSSIAN_CLIQUE_COPY_BOUND: cost >= 40 Gaussian / 80 rational; 2579856 flat pairs; 6 negative controls; kappa unchanged
```

The verifier reads the committed [certificate](certificate.json), verifies
the [source hashes](SOURCES.json), and recomputes the result without writing
files. Python optimization is explicitly rejected because the geometry code
uses assertions. A missing or modified source or certificate fails the run.

The complete domain consists of 240 roots, 60 Gaussian lines and 2,272 flats.
Closure of supports preserves their pairing rank and can only increase
clique hits. This reduces every possible support pair to the finite flat
domain. Symmetry reduces it to 2,579,856 nonempty unordered pairs. The empty
flat is handled by the proof. Of these pairs, 2,725 have no joint hits;
1,827,741 satisfy the inequality by the exact dimension bound; and 749,390
receive explicit rational Gram-rank calculations. This is a completed census,
with no randomized search or timeout stopping rule.

Six rejection controls cover a too-large uniform weight, confusion between
Gaussian and rational units, a false clique, a duplicate clique, a missing
decoder diagonal, and a forbidden decoder entry. Positive controls accept
the identity decoder and an asymmetric edit at an orthogonal free entry,
including its cost-60 row decomposition. A separate Fraction elimination
checks arithmetic cases and the sharp witness's expanded Gram matrix.

## Validation record

On 2026-10-13, the command above passed on macOS 26.5.2 arm64 with Python
3.14.8 and 3.11.15. The second run used a temporary directory containing
only this package and the six pinned source files, with `/` as the working
directory. A changed source byte failed hash validation; `python3.11 -O`
failed explicitly. Changing the receipt's floor from 40 to 41 in memory
failed after a fresh complete replay. All six built-in negative controls
passed in the successful runs.

`python3 -B scripts/verify_selected_result.py` also passed. A separate code
review checked the flat-pair argument, pruning inequality and source geometry.
As a development check, independent Fraction elimination agreed on 1,000
integer matrices drawn with seed 46, with row-order and dependent-row checks.
That development sampling is separate from the exhaustive flat-pair census.

The unchanged repository-wide `make verify` and selected construction's
expensive cold replay were not rerun. No Linux CI pass is claimed. This
package does not change their code, generators, certificates or inputs.

## Scope and provenance

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. The selected accepted
certificate at that base has
`kappa=51110230636731/31250000000000000=0.001635527380375392`.
The [local sprint claim](CLAIM.md) records OS assignment seed 46, candidate
selection and coordination. The even seed chose Gaussian over Eisenstein
geometry. No pinned coordination issue existed.

Joel Pulikkan / GamingPuzzled's #620 supplies the extension-ring question,
geometry and previous search results. Its retained head and exact source
hashes are recorded in `SOURCES.json`. DreamingOfClouds' #446/#595 supply the
pairing-rank accounting and conditional deficit framework. Douglas R.
Colkitt / Mister-Meeseeks' #703, pinned at
`358383e2f1b0f292d4d6eb897c06fd8558a4f5e6`, supplies the precursor weighted
clique argument for the different ten-line Hurwitz geometry. This package
imports no predecessor executable code and uses no SAT solver.

The bound covers whole Gaussian-line supports, scalar binary totals and the
specified fitting pattern. It does not cover sub-line supports, vector-valued
totals, other geometries, or alternative stage accounting. It is not a formal
verification of the integer multiplication theorem. The selected construction
and its compiler, realization, hosting, precision, tape and analytic assumptions
are unchanged. This package changes only its own research directory.

Prepared by **Sagar Thakrar (@thakrarsagar)** with substantial **OpenAI Codex
assistance** in proof development, implementation, verification and writing.
No independent human review is claimed. New material is licensed under the
repository's [Apache-2.0 license](../../LICENSE).
