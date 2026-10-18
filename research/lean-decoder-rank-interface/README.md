# General decoder rank and minor interfaces in Lean

This completes the general rank-to-cost interface requested in item 5 of
[DreamingOfClouds's Lean handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18934590).
It formalizes a rectangular, field-extension version of the rank argument
already stated in [PR2162](https://github.com/CrocSwap/integer-mult-bounds/pull/2162),
and supplies the nonzero-minor corollary needed to use that argument with a
rank witness. This is a formal interface completion, not a new mathematical
rank principle or a formalization of the full jet argument.

The local Lean 4.33.0-rc1 build passed with Mathlib pinned to
`55b7917b472489c7c56a0fa6393af05cfd536599`. All 18 requested axiom reports
contain only `propext`, `Classical.choice` and `Quot.sound`.
An independently implemented finite check passed **196,608 cases**.
The original diagonal-output theorem and its helpers are imported from an
unchanged, credited copy of the predecessor. No supplier or selected κ changes.

## Exact propositions

Let `F,K` be fields, `f : F →+* K`, and `I,J,T` finite types. Let `B` be an
`I × J` matrix over `F`. For each `t : T`, let `p_t : I → K` and
`q_t : J → K`, with supports contained in declared finite sets `S_t,U_t`.
The sets may contain coordinates where the corresponding weight is zero.
Define

\[
C_F=\sum_{t\in T}\operatorname{rank}_F B[S_t,U_t],\qquad
M=\sum_{t\in T}\operatorname{diag}(p_t)f(B)\operatorname{diag}(q_t).
\]

[DecoderRankBound.lean](lean/DecoderRankBound.lean) proves:

1. `rank_weighted_le_cost`: `rank_K M ≤ C_F`.
2. `weighted_eq_hadamard`: `M[i,j] = f(B[i,j]) Σ_t p_t[i] q_t[j]`.
3. `rank_hadamard_le_cost`: the same bound for that entrywise matrix.
4. `minor_le_cost`: for any finite type `D` and selectors `rows : D → I`,
   `cols : D → J`, a nonzero determinant of the selected square submatrix
   implies `card D ≤ C_F`.
5. `charTwo_rank_le_cost`: specialization to `F = ZMod 2` and any field `K`
   of characteristic two, retaining the original binary block ranks in `C_F`.

The first three statements require no output-diagonal, nonzero-diagonal,
invertibility, unit-diagonal, admissibility or nonempty-index hypothesis.
The minor theorem adds precisely its nonzero determinant assumption. It does
not separately require injective selectors: the determinant assumption already
excludes repeated rows or columns. The field homomorphism is essential; this
does not permit entrywise reinterpretation in a different characteristic.

[Contract.lean](lean/Contract.lean) applies the theorems to three signatures
with the sums, matrix entries and base-field block ranks written explicitly.
These provide a check of the advertised proposition independent of the short
`weighted`, `hadamard` and `cost` names.

## Proof lineage and hypothesis controls

The first proof composes `DecoderDuality.rank_sum_le`,
`rank_diag_mul_mul_diag_le` and `rank_map_le`. Those helpers, and the earlier
diagonal theorem, are **DreamingOfClouds's work**, retained byte-for-byte from
PR2162 head `113a718265c62aec301c5695f4bfb9c421bef7ab`, original path
`research/char2-jets/lean/DecoderDuality.lean`. The Hadamard identity uses
entrywise ring arithmetic; the minor corollary uses Mathlib's rank of an
invertible square matrix and rank monotonicity under taking submatrices.

[Examples.lean](lean/Examples.lean) checks a genuinely rectangular `2 × 3`
binary matrix with a nonzero off-diagonal entry. Its first two columns have
nonzero determinant after embedding into `RatFunc (ZMod 2)`; the new interface
then proves the binary block cost is at least two. Empty term families and
zero row weights are also accepted.

The same file proves explicit counterexamples to dropping either support
condition or the nonzero-minor assumption. The full build driver then submits
three invalid proof attempts for those exact propositions and requires actual
Lean type errors; a missing import does not count as rejection. A further
Lean theorem proves that no field homomorphism `ZMod 2 →+* ℚ` exists.

[finite.py](finite.py) uses binary bitset elimination, an independently
implemented `F₂[x]/(x²+x+1)` field, and a proportional-row rank test. It checks
all 64 binary `2 × 3` matrices in three families, 65,536 cases each:

- all pairs of binary row/column weight vectors;
- every single-query weight vector over the four-element extension;
- each extension-field query plus a fixed all-ones query, including cancellation.

It compares rank with the exact original binary support-block cost and the
full-support upper bound. For one query it checks equality. Separate exact
counterexamples check the three missing hypotheses and a characteristic change:
`[[1,1,0],[1,0,1],[0,1,1]]` has rank two over `F₂` and three over `F₃`.
[FINITE.json](FINITE.json) records the complete rank/cost histograms. These
finite checks are useful independent evidence, not a universal proof.

## Reproduction

The standard-library command performs source binding and finite checks only:

```sh
python3.12 -I -O -B research/lean-decoder-rank-interface/verify.py
python3.12 -I -O -B research/lean-decoder-rank-interface/test_package.py
python3.12 scripts/research_package.py --package research/lean-decoder-rank-interface
```

Its success marker is `PASS_DECODER_RANK_SOURCES_AND_FINITE_ONLY` and it reports
`kernel_checked=false`. Eight test groups cover source changes, proof escapes,
missing/extra/duplicate/untrusted axiom reports, strict JSON values, corrupt
field arithmetic, receipt drift, existing-output preservation and incomplete
kernel-mode arguments. No assertion depends on Python optimization being off.

For an actual Lean build, install the Linux release named in
[PROOF-SOURCES.json](PROOF-SOURCES.json), verify its recorded SHA256, and run:

```sh
python3.12 -I -O -B research/lean-decoder-rank-interface/verify.py \
  --lake /absolute/path/lean-4.33.0-rc1-linux/bin/lake \
  --work-dir /tmp/decoder-rank-new-build \
  --fetch-cache --out /tmp/decoder-rank-new-result.json
```

Both output paths must be new. Network access is needed for dependencies and
the official Mathlib cache. Instead of `--fetch-cache`, an existing cache may
be supplied with `--packages /absolute/path/to/.lake/packages`. The driver
checks the exact Git head and tracked source cleanliness of all nine dependency
repositories. It always copies the local Lean sources into a new build
directory and compiles them there. It then queries the complete 18-theorem
axiom inventory and executes the three rejection controls.

Only this mode reports `PASS_DECODER_RANK_KERNEL` and `kernel_checked=true`.
It retains build, axiom and rejection logs in the new build directory.
The scoped [Lean workflow](../../.github/workflows/lean-decoder-rank-interface.yml)
uses the checksum-pinned official binary and fresh cache retrieval. The generic
package workflow runs only the lightweight checks.

The local full build used official Lean commit
`62eed1db4d67327ec8120be05f1a1b0847d74561`, with the Linux release archive
SHA256 `25e7b3e18ec75a4e2529fc23194be8e3cc3183df99b553f870d8a111c7488210`.
The independent Python check uses no Lean output or theorem receipt.
Trust includes the Lean binary/kernel, imported Mathlib proof objects and their
official cache. This run rebuilt all four local Lean modules; it did not
rebuild all of Mathlib from source or execute a native multiplication supplier.
Both the existing-cache mode and the fresh dependency-fetch mode passed locally
and produced identical receipts. The lightweight replay and all eight controls
also passed in a read-only, Git-free source export under CPython 3.14.4 with
`-I -O -B`; all 18 exported files remained unchanged.

## Open next questions

The requested generic interface is complete. The next mathematical obligation
is to formalize the specific jet/valued-field rank witness: define the proposed
extension-field entries, establish the support hypotheses, and prove that a
chosen leading coefficient makes a selected minor nonzero. First instantiate
`minor_le_cost` for one pinned jet certificate and expose the remaining
determinant obligation. This could connect the existing certificate to the
base-field cost theorem; it requires a separate formal treatment of valuations
and the certificate. The present work does not prove the full jet theorem,
the anti-Fano certificate, a `T=3` conjecture, all-size admission or a better κ.
Structured next steps and scope history are in [TASK.json](TASK.json).

## Attribution and coordination

Prepared by Gareth Davidson (`@bitplane`) with substantial OpenAI Codex
assistance, without subagents or independent human review, under Apache-2.0.
The imported source's [notice](PR2162-NOTICE.md) and
[license](PR2162-LICENSE) are retained; the notice describes the predecessor
package, not new authorship of this extension. Credit also belongs to Lean
and Mathlib contributors and the earlier decoder work cited in that notice.
The exact predecessor, library pins and source hashes are in
[PROOF-SOURCES.json](PROOF-SOURCES.json); selected-record and task-catalogue
provenance are in [SOURCES.json](SOURCES.json).

Original OS nonce `d8d89da538eb6248543c95377394d893`, priority revision 4,
`independent-verification / formal-interface-lemma`. The drawn binding-audit
method was refined to the explicit formalization handoff, without rerolling.
Canonical investigation: [Discussion2254](https://github.com/CrocSwap/integer-mult-bounds/discussions/2254).
