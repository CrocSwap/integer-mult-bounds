# Discharge the selected BIT fractional moment in Lean

This proves the numerical hypothesis left explicit in [PR2289](https://github.com/CrocSwap/integer-mult-bounds/pull/2289), then composes it with that package's unchanged stopped-recurrence theorem. For the literal selected BIT profile, including its fallback allowance, Lean proves fractionalMoment < 9999/10000 at τ=9983/10000. The resulting root-family time bound has no supplied numerical moment premise.

The moment point and inequality are credited predecessor results from [Jose Manuel's PR2234](https://github.com/CrocSwap/integer-mult-bounds/pull/2234). The new coverage is the checked implication from rational certificate steps to the actual Real.rpow expression and its recurrence corollary. It does not prove that the physical machine satisfies the recurrence or has one uniform local-charge constant. No selected supplier, frontier or κ changes.

## Exact statement and source binding

The inherited [Selected.lean](lean/Selected.lean) fixes m=64, W=28416, ranks (1,2,3,4,5,6,7,42) and counts (381024,400416,22752,26880,29376,17376,26784,288). Write a_r=H_r/W and b=118606528512/(10^16 W), where the fallback numerator equals 32·64²·ΣH_r. The expression is

\[
\mu_\tau=\sum_r a_r(r/64)^\tau+b(1/64)^\tau.
\]

[SelectedMoment.lean](lean/SelectedMoment.lean) proves the exact Real bound

    μτ ≤ 11290320473664709188758299 / 11291503906250000000000000
       < 9999 / 10000.

The positive rational margin below 9999/10000 is

    54282194665811241701 / 11291503906250000000000000.

This upper enclosure is deliberately coarser than PR2289's Python certificate. Its purpose is to close the formal numerical premise, not to increase an exponent or print more digits.

The two recurrence modules are retained byte-for-byte from PR2289 head 32ef80ad161b8602b32698ed43186ecc2266cb5b and are rebuilt locally. The selected GLOBAL.json and EXPECTED.json profiles must agree, the inherited Lean literals must match them, and ASSEMBLY.json must bind the same bit endpoint. Those JSON files are immutable snapshots of canonical base 0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2. [SOURCES.json](SOURCES.json) records Git identities; [PROOF-SOURCES.json](PROOF-SOURCES.json) pins all proof inputs.

## Why the rational certificate bounds a real power

For 0<x≤1, round τ down to q=130849/131072. The exact gap is τ−q=111/81920000. Since powers of such a base decrease as the exponent increases, x^τ≤x^q.

Read the 17 binary digits b_i of 130849 from least significant to most significant. Set e_0=0, u_0=1 and

    e_(i+1) = (e_i+b_i)/2,
    u_(i+1) ≥ 0,
    u_i*x^b_i ≤ u_(i+1)^2.

Then e_17=q. If x^e_i≤u_i, the square of x^e_(i+1) is x^e_i·x^b_i≤u_(i+1)^2. Both sides are nonnegative, so x^e_(i+1)≤u_(i+1). [DyadicPower.half_step](lean/DyadicPower.lean) proves this implication over actual real powers; upper_of_rounded_exponent supplies the final exponent comparison.

[DYADIC.json](DYADIC.json) proposes each u_i on the grid 10^-12. The 8 ranks require 136 small rational square inequalities. The generated Lean source proves every inequality with norm_num, checks every exponent transition, and aggregates the full selected profile and fallback. No additional axiom, sorry or native_decide is used; every rational certificate obligation is proved. The Python square-root generator is outside the formal trust base: its proposals must survive Lean.

The same Lean module proves why a negative square root and upward exponent rounding cannot serve as these upper bounds. Kernel-mode controls corrupt the first root downward, replace it by its negative, and attempt the reversed exponent comparison. The first two fail on explicit false arithmetic obligations; the third fails with an actual type mismatch.

## Recurrence corollary and remaining assumptions

[ClosedBitRecurrence.uniform_bound](lean/ClosedRecurrence.lean) supplies the proved moment inequality to PR2289's selected_uniform_bound. For arbitrary root contexts u with limits N_u, widths w_u≥0, costs T_u and **one C≥0 shared across the family**, it assumes T_u(1)≥0 and the following only for 1≤n≤N_u:

- For n<64, T_u(n)≤Cw_u.
- For n≥64 and f=⌊n/64⌋, T_u(n)≤Σ_r a_r T_u(rf)+b max_(1≤j≤f) T_u(j)+C(n+w_u).

It concludes

\[
T_u(n)\le200Cn+10000Cn^{9983/10000}w_u\qquad(1\le n\le N_u).
\]

It retains the actual fallback maximum, allows root-coupled widths, imposes no monotonicity assumption on T and leaves T_u(0) unrestricted. The new formal result removes exactly the numerical moment premise. Completed packet endpoints, frozen-ancestor preparation/access, parking, the physical recurrence and the existence of the shared C remain outside this proof.

## Reproduce and interpret the evidence

Python 3.12 standard-library source and arithmetic checks:

    python3.12 -I -O -B research/lean-bit-moment-discharge/verify.py
    python3.12 -I -O -B research/lean-bit-moment-discharge/test_package.py
    python3.12 scripts/research_package.py --package research/lean-bit-moment-discharge

Default replay reports PASS_BIT_MOMENT_SOURCES_AND_FINITE_ONLY and kernel_checked=false. It regenerates the certificate proposals and exact Lean source, checks 136 square steps, checks all 8 final upper bounds by a separate direct 10000th-power comparison at the actual source exponent, and performs 4,774 direct-power calibrations. The calibration domain is 1≤r≤m, 2≤m≤12, 1≤k≤5, 0≤p<2^k. The exponent-one endpoint is explicitly rejected by the low-bit proposal routine; exponent zero is included.

Eleven failure-control groups cover corrupt or negative roots, missing/reversed chains, omitted ranks, changed counts, upward rounding, strict types/JSON, source drift, formal-profile/fallback mismatches, regenerated-source drift, proof escapes, axiom inventory/trust, receipt drift, preserved existing output and incomplete kernel arguments. These are finite checks, not a substitute for running Lean.

Install the official Linux Lean 4.33.0-rc1 binary identified and checksum-pinned in PROOF-SOURCES.json. Then use new paths:

    python3.12 -I -O -B research/lean-bit-moment-discharge/verify.py \
      --lake /absolute/path/lean-4.33.0-rc1-linux/bin/lake \
      --work-dir /tmp/bit-moment-new-build \
      --fetch-cache --out /tmp/bit-moment-new-result.json

Alternatively, --packages /absolute/path/to/.lake/packages reuses a pinned library cache. The driver checks all nine dependency Git heads and tracked-source cleanliness, builds all five local modules from source, requires all 22 axiom reports, and runs the three actual Lean rejection controls. Only this mode reports PASS_BIT_MOMENT_DISCHARGE_KERNEL and kernel_checked=true.

The fresh local build passed with Lean commit 62eed1db4d67327ec8120be05f1a1b0847d74561 and Mathlib 55b7917b472489c7c56a0fa6393af05cfd536599. All inspected theorem dependencies are among propext, Classical.choice and Quot.sound. Trust includes that Lean binary/kernel and imported Mathlib proof objects from the official cache; Mathlib was not rebuilt from source. The scoped [workflow](../../.github/workflows/lean-bit-moment-discharge.yml) performs the checksum-pinned installation and proof build.

The registered replay passed on Python 3.12.3. Both lightweight commands passed on Python 3.14.4 from a Git-free, read-only export with all 22 package files unchanged; a direct write probe was rejected.

To reproduce the untrusted proposals separately:

    python3.12 -I -B research/lean-bit-moment-discharge/certificate.py \
      --out-dir /tmp/bit-moment-new-proposals

This requires a new output directory and explicitly reports that no kernel has run. TASK.json records environments, source pins, overlap review and verification limits.

## Open next questions

The numerical premise at this point is now discharged; another equivalent enclosure is not the next missing implication. Establish the physical local-charge C(n+w) for the realized recursive caller with one C across the permitted root contexts. First give one explicit frozen-ancestor evaluator a complete preparation/access bill, then amortize each preparation against its complete target fibre with the generation-depth bound. A physical packet/caller and parking implementation remains the prerequisite. This arithmetic proof cannot establish that interface.

## Attribution and overlap

Prepared by Gareth Davidson (@bitplane) with substantial OpenAI Codex assistance, without subagents or independent human review, under Apache-2.0. PR2234's recurrence, profile, moment point and proposed ordinary saving retain Jose Manuel's and the credited predecessor contributors' authorship. The selected PR589 profile retains DreamingOfClouds' tuning, eumemic's base word and the hosting/routing lineage. My PR2289 supplies the unchanged recurrence proofs and adapted build/test wrapper.

Earlier Lean PR585/605/842/885 certify other historical complex expressions; their published scopes were read and their achievements are not claimed here. Dugongue's concurrent PR2284 (e71574b92f6af546013c71293cd03ff58742a1e6) proves generic rational aggregation assuming per-term real upper bounds, alongside other moment lemmas. Its MomentTransfer.lean was inspected; no full replay is claimed. This package supplies the missing concrete Real bounds for the selected BIT expression.

Repeated-square-root numerical enclosure is prior art in [independent-queue-ceilings](../independent-queue-ceilings/README.md) and [idle-stability-radical-audit](../idle-stability-radical-audit/README.md). The new contribution is the Lean proof and this source-bound composition, not invention of that numerical method. No predecessor numerical engine is imported.

Original single OS nonce de346470d4c367b36f566f9208c8fab2, priority revision 4, independent-verification / independent-moment, refined without rerolling. [Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2209#discussioncomment-18940025).
