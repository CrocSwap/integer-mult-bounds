# Independent Lean audit of the stopped time induction

This verifies one requested implication in [Jose Manuel's PR2234](https://github.com/CrocSwap/integer-mult-bounds/pull/2234): its stated stopped recurrence implies its stated time majorant. The source proof, profile, moment point and saving are credited predecessor results. The contribution is an independent Lean proof of the conditional implication, its exact domain and quantifiers, plus source binding and hypothesis countermodels.

The result applies to positive widths within each root's descendant range. It uses the actual fallback maximum and one local-charge constant shared across the root family. It makes no monotonicity assumption on the cost function, imposes no condition on its width-zero value, and needs no recurrence outside the root's permitted range. It does **not** establish the whole-machine endpoint, fresh-packet realization, ancestor-access cost or existence of the required uniform local charge. No selected supplier, frontier or κ changes.

## Exact formal statement

Write m=64, W=28416 and τ=9983/10000=1−17/10000, with this literal selected profile:

| r | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 42 |
|---|---|---|---|---|---|---|---|---|
| H_r | 381024 | 400416 | 22752 | 26880 | 29376 | 17376 | 26784 | 288 |

Put a_r=H_r/W and b=118606528512/(10^16 W), where the numerator is the retained allowance 32·64²·Σ H_r. Assume

\[
\mu_1=\sum_r a_r(r/64)+b/64\le199/200,\qquad
\mu_\tau=\sum_r a_r(r/64)^\tau+b(1/64)^\tau\le9999/10000.
\]

For each root context u, choose a descendant-width limit N_u, an atom width w_u≥0, and a real cost function T_u(n). There must be **one C≥0 for the entire family**. Assume T_u(1)≥0, and, only on 1≤n≤N_u:

- If n<64, then T_u(n)≤C w_u.
- If n≥64, put f=⌊n/64⌋ and assume

\[
T_u(n)\le\sum_r a_r T_u(rf)
 +b\max_{1\le j\le f}T_u(j)+C(n+w_u).
\]

Then [Selected.lean](lean/Selected.lean), theorem **selected_uniform_bound**, proves

\[
T_u(n)\le200 Cn+10000 Cn^\tau w_u\qquad(1\le n\le N_u).
\]

Root contexts may restrict or couple their widths; the theorem does not require the local-charge estimate for arbitrary independent (n,w,depth). This preserves PR2234's stated root-coupled control-cost domain. The theorem selected_positive_bound gives the one-root version. A zeroed bookkeeping extension is used internally, without constraining the caller's actual T_u(0).

[StoppedRecurrence.lean](lean/StoppedRecurrence.lean) proves the general statement for any finite rank set, 1<m, 0<r<m, nonnegative coefficients and exponent, and the two displayed moment margins. It uses proper-width strong induction. The maximum is bounded by the increasing **majorant**, not by an assumed increasing T. The linear margin pays C n and the power margin pays C n^τ w≥C w. All calls remain in the root's descendant range.

## What the proof establishes and retains

The selected linear moment is proved exactly in Lean:

    2874298095721977 / 2890625000000000 <= 199 / 200.

The selected fractional moment remains an **explicit Lean hypothesis**. Independently of the predecessor's moment engines, [finite.py](finite.py) verifies eight rational enclosures from [POWER-BOUNDS.json](POWER-BOUNDS.json). For a grid numerator u and denominator d, it checks

    (u-1)^10000 * 64^9983 < r^9983 * d^10000 <= u^10000 * 64^9983.

Strict monotonicity of the 10000th power on nonnegative reals justifies the enclosure of (r/64)^(9983/10000). Decimal arithmetic proposed the grid points; only exact integer powers certify them. The resulting rational moment upper bound is

    45161081915007803589191471 / 45166015625000000000000000,

strictly below 9999/10000. This corroborates an existing source inequality; it is not a new supplier-root calculation. The integer certificate is checked by Python and its mathematical interpretation is explained here; it is not silently imported as a kernel theorem.

The physical recurrence itself remains a premise. In particular, this package does not prove the existence of one local C independent of the original root, or audit all endpoint, parking, frozen-field and polynomial-control arguments that PR2234 uses to justify it. The result is one completed formal implication within that proposed proof, not adoption of its complete recursive machine or multiplication theorem.

## Countermodels and finite checks

[Counterexamples.lean](lean/Counterexamples.lean) proves these controls:

- A positive leaf cost can violate the bound when the leaf obligation is omitted, even with zero cost at all larger widths.
- If proper descent is dropped, take m=2, recursive rank 4, coefficient 1/4, C=2, w=1 and T(n)=n². The recurrence holds at **every** natural width, and both moment margins hold at the source exponent. At n=20401, cost 416200801 exceeds the majorant's upper bound 416180400.
- Width-dependent charges can pay n² pointwise, but no fixed nonnegative C bounds it by the claimed source-exponent majorant at every width. This distinguishes ∀n ∃C_n from the required ∃C ∀n.
- For costs [0,1,0], the maximum through width two exceeds the endpoint value. Replacing the fallback maximum with T(f) therefore needs a separate monotonicity proof.

These are countermodels to weakened hypotheses, not counterexamples to PR2234. The full build also submits four invalid proof attempts and requires actual Lean type errors.

The independent exact-rational replay evaluates the literal selected recurrence at all positive widths 1..4096 for w∈{1,3,17,1000}: **16,384 positive-width cases**, plus four bookkeeping zero entries. It keeps a running maximum and independently scans the first 256 prefixes. It checks the stronger integer envelope 200 n+10000 w floor(sqrt(n)), below the formal majorant because τ≥1/2. This is a finite abstract-recurrence check, not timing of the physical supplier. It also checks 4,097 widths of the quadratic countermodel identities. [FINITE.json](FINITE.json) records the results and exact trace digests.

## Reproduction and trust

Lightweight, standard-library checks:

    python3.12 -I -O -B research/lean-stopped-recurrence-audit/verify.py
    python3.12 -I -O -B research/lean-stopped-recurrence-audit/test_package.py
    python3.12 scripts/research_package.py --package research/lean-stopped-recurrence-audit

The first command reports PASS_STOPPED_RECURRENCE_SOURCES_AND_FINITE_ONLY and kernel_checked=false. Nine failure-control groups cover source corruption, proof escapes, missing/extra/duplicate/untrusted axiom reports, strict JSON values, a false power enclosure, mismatched Lean/source counts, receipt drift, existing-output preservation and incomplete kernel-mode arguments. They remain effective under -O.

For a fresh local proof build, install the official Linux Lean 4.33.0-rc1 release identified by [PROOF-SOURCES.json](PROOF-SOURCES.json), verify its SHA256, and use new output paths:

    python3.12 -I -O -B research/lean-stopped-recurrence-audit/verify.py \
      --lake /absolute/path/lean-4.33.0-rc1-linux/bin/lake \
      --work-dir /tmp/stopped-recurrence-new-build \
      --fetch-cache --out /tmp/stopped-recurrence-new-result.json

Instead of --fetch-cache, --packages /absolute/path/to/.lake/packages reuses an existing pinned library cache. The driver checks all nine dependency Git heads and tracked source cleanliness, copies the three local modules to a new directory, builds them, inspects all 14 requested axiom reports and runs the four rejection controls. Only this mode reports PASS_STOPPED_RECURRENCE_KERNEL and kernel_checked=true. Build, axiom and rejection logs remain in the build directory.

The local proof build passed with Lean commit 62eed1db4d67327ec8120be05f1a1b0847d74561 and Mathlib 55b7917b472489c7c56a0fa6393af05cfd536599. Reports contain only propext, Classical.choice and Quot.sound. The scoped [workflow](../../.github/workflows/lean-stopped-recurrence-audit.yml) performs the checksum-pinned installation and Lean build; generic registered replay does not run Lean. Trust includes the Lean binary/kernel and imported Mathlib proof objects from the official cache. Mathlib was not rebuilt from source.

The registered replay passed on Python 3.12.3. Both lightweight commands also passed on Python 3.14.4 from a Git-free, read-only export: all 23 package files were unchanged and a direct write probe was rejected.

The default replay uses immutable local source snapshots. Git provenance is checked by the registered-package wrapper; source-export replay needs no Git or network. Future priority or frontier changes do not change the historical scope of this audit.

## Open next questions

The remaining central obligation is to establish the source's local charge C(n+w) for the realized recursive payload machine with **one** constant over the allowed root-coupled contexts. Start by giving one explicit frozen-ancestor evaluator a physical access and preparation bill, including the largest generation depth, and show how each preparation is amortized against its complete target fibre. A complete packet/caller and parking implementation is a separate prerequisite; this recurrence theorem cannot supply it.

A smaller formal task is to connect the eight exact rational power certificates directly to fractionalMoment in Lean. That would remove the retained numerical hypothesis from the selected corollary while leaving the physical recurrence assumptions visible. Start with one certified rational-power inequality; this alone would not close the full supplier. [TASK.json](TASK.json) records these questions and blockers.

## Attribution and coordination

Prepared by Gareth Davidson (@bitplane) with substantial OpenAI Codex assistance, without subagents or independent human review, under Apache-2.0. The original recurrence, profile, moment point and proposed ordinary saving belong to Jose Manuel (jmbarrancoml) and the credited predecessor lineage. PR2234 is pinned at d047ef86fbc5b1614d3d8e2b8d3441413beab73f; its proof, recurrence checker, [notice](sources/pr2234/NOTICE.md) and [license](sources/pr2234/LICENSE) are retained unchanged. Its checker is not imported or executed. The notice describes that predecessor package, not new authorship of this audit.

Credit remains with DreamingOfClouds, eumemic, alephnan and the geometry, hosting, routing, fallback, descriptor and parking contributors listed there, as well as Lean and Mathlib contributors. The build wrapper adapts this author's earlier [PR2267](https://github.com/CrocSwap/integer-mult-bounds/pull/2267); the new theorem and arithmetic checker are separate.

The final overlap refresh also found Dugongue's concurrent [PR2284](https://github.com/CrocSwap/integer-mult-bounds/pull/2284), pinned at e71574b92f6af546013c71293cd03ff58742a1e6. Its Recursion.lean and PROOF-RECURSION.md were read: they formalize a single active child's linear excess and exponent bootstrap. This package addresses PR2234's weighted branching time recurrence, including the fallback maximum and fractional-power majorant. Both use proper-width induction; this is not a claim to introduce that method. PR2284's complete package was not replayed here.

Original OS nonce e1a6501d422e1e4fca5822db6ad07b8e, priority revision 4, adversarial-audit / supplier-boundary-audit, refined to the explicit review request without rerolling. [Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2209#discussioncomment-18939418). Scientific base 0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2; [SOURCES.json](SOURCES.json) and [PROOF-SOURCES.json](PROOF-SOURCES.json) give exact provenance and byte hashes.
