# Kernel-checked rank interface for overcomplete coupling

PR2277's Lemma OC already proves in prose that an exact factorization
`X Yᵀ = I_T` makes `K = Yᵀ X` a rank-T idempotent, with complement rank
`m−T`. Its shipped Lean file formalizes idempotency, traces and the square
case, and explicitly leaves the rank statements and one-extra consequence
as written proofs. This package completes those **forward formal obligations**.
It does not claim a new mathematical rank theorem or a new decoder cost floor.

`Coupling.lean` proves, over **every field**, for arbitrary finite index types:

* `rank X = rank K = T`;
* `rank(I_m−K) = m−T`;
* if `m=T+1`, there are vectors `a,b` with `I_m−K = a bᵀ` and `bᵀa=1`;
* consequently `K_ij = −a_i b_j` for `i≠j`, and `K_ii=1−a_i b_i`.

The size difference is a natural-number difference. Exactness itself forces
`T≤m`. Empty finite types are allowed by the general theorems; the one-extra
premise forces the complement to be nonzero. No positivity, characteristic
zero, symmetry, root-system classification, finite search or rank conclusion
is assumed in a theorem hypothesis.

## Proof structure

The product `XYᵀ=I` and the matrix rank inequalities force `rank X=T`.
Next `XK=X` gives the lower bound for `rank K`, while `K=YᵀX` gives the upper
bound. This avoids using trace to infer rank: over F2, the three-dimensional
identity has trace one and rank three.

Idempotency gives `K(I−K)=0`, so their ranks sum to at most m. The matrix
rank subadditivity inequality and `K+(I−K)=I` give the reverse inequality.
Natural-number arithmetic then gives the stated complement rank.

For a rank-one matrix, the proof chooses a nonzero actual column. Its column
space has dimension one, so every column is a scalar multiple of that column.
This yields an outer product with two nonzero factors. Applying idempotency
to a nonzero entry and cancelling that entry proves `bᵀa=1`. The two entry
formulas follow directly from `I−K=a bᵀ`.

The proof reuses the elementary idempotency calculation from the credited
source, and Mathlib's established rank and finite-dimensional APIs. Six final
roots are printed with `#print axioms`; each depends only on `propext`,
`Classical.choice` and `Quot.sound`. There is no `sorry`, custom axiom,
native-decision axiom or finite fixture assumed by a theorem.

## Reproduce the formal result

The predecessor pins Lean **4.33.0-rc1**, commit
`62eed1db4d67327ec8120be05f1a1b0847d74561`, and Mathlib commit
`55b7917b472489c7c56a0fa6393af05cfd536599`. `TOOLCHAIN.json` also records
the dependency-manifest hash and the official Windows release archive's
SHA256, checked before the local run. Install that Lean release in a local
directory, then prepare a separate Mathlib checkout:

```sh
git clone https://github.com/leanprover-community/mathlib4.git /path/to/mathlib4
git -C /path/to/mathlib4 checkout 55b7917b472489c7c56a0fa6393af05cfd536599
# With the pinned Lean bin directory on PATH, in /path/to/mathlib4:
lake exe cache get Mathlib.LinearAlgebra.Matrix.Rank Mathlib.LinearAlgebra.FiniteDimensional.Basic
# Back in this repository:
python3.12 -I -B research/overcomplete-rank-interface/leancheck.py \
  --mathlib-root /path/to/mathlib4 --lean-bin /path/to/pinned-lean/bin
```

The checker verifies compiler version/commit, Mathlib HEAD, tracked source
cleanliness and the exact dependency manifest. It compiles a temporary copy
without writing generated files into this package or changing Mathlib.
It audits all six roots and rejects four altered contracts: ambient size
instead of T, zero product instead of exactness, two extra columns instead
of one, and normalization zero instead of one. A missing toolchain is an
error, not a skipped formal pass. `--out NEW.json` writes a new recomputed
receipt and refuses an existing path. Normal replay compares the retained
`FORMAL-RESULT.json`.

As with a standard Mathlib build, the compiler and imported library artifacts
are trusted dependencies. The checker is not a hermetic rebuild or an audit
of the entire Mathlib library. No hosted CI formal run is claimed.

## Separate finite and export evidence

```sh
python3.12 -I -B scripts/research_package.py --package research/overcomplete-rank-interface
```

This registered Python replay is intentionally **separate from Lean**. It
authenticates the retained predecessor and formal-source receipt, then checks
448 exact factorization fixtures over Q, F2, F3 and F5, with T from one to four
and zero through three extra columns. The 112 one-extra cases independently
recover an outer product from a pivot and check its normalization and entries.
Four semantic controls include trace-one/rank-three in F2, failed exactness,
the two-extra boundary and a nonsymmetric idempotent positive control.
Git-free optimized export checks exercise read-only replay, predecessor and
formal-source corruption rejection, and refusal to overwrite a receipt.
These finite checks illustrate and test the interface; they do not prove its
universal quantifiers or rerun the source's root-code tables.

## Provenance, binding and decision

The exact source is DreamingOfClouds's
[PR2277](https://github.com/CrocSwap/integer-mult-bounds/pull/2277), head
`ca7f99921f03398d303bba90245d3ee2e38e95c3`, README section 4 (Lemma OC and
consequence b). `DEPENDENCY.json` records Git blob IDs and SHA256 hashes for
the unchanged README, original Lean file and three environment files. The
notation is direct: source X,Y and cross matrix `YᵀX` have the same matrix
dimensions and orientation in this package. The formal theorem requires
exactly the source's `XYᵀ=I`; no source geometric calculation is imported.
All source credit is retained. This package's new proof and replay code were
prepared for ywz65 with substantial OpenAI Codex assistance, Apache-2.0.

The task picker selected the P104 card, nonce
`ad89b619e94d237299b77316f1d1a534`; the baseline orientation passed. Adjacent
ceiling domain defects were handed to a single separate repair. This scope
instead closes an expressly unformalized decoder-coupling obligation.
`TASK.json` records the change. Main provenance is pinned to `1884c509`;
pending source provenance is pinned independently to the PR head above.

The decision is **finish this bounded formal audit**. It constructs no new
physical family. Native access, copy/hosting, restoration, precision and
consumer costs are not evaluated and remain unknown for any proposed use;
they are not assigned zero. No new supplier, kappa bound or all-size integer
multiplication result follows. The converse, prescribed-direction criterion,
geometric floor tables and source SAT claims are outside this proof.

## Open next questions

Formalize the converse of Lemma OC by cancelling the full-rank rectangular
factors, then its prescribed-direction criterion. Those are separate written
obligations in the source. A later root-code application must also bind its
finite geometric tables and cost model to the exact formal hypotheses; the
present generic algebra theorem supplies no such table or physical bridge.
