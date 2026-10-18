# Independent re-check of the selected PR1042 finite invoice and outer admission

**Status: independent verification. No new κ, and the selected result is unchanged. No discrepancy was found.**

- **Track and seed:** track 75–84 (independent verification), assignment seed **81** from the OS CSPRNG (Python `secrets`).
- **Base commit:** `ba82555c64e1879e4b7decce28186f208fcb8262`.
- **Audited record:** `research/community-frontier1042-audit/ASSEMBLY.json`, sha256 `093f3544…1e54e`. This is the `certificate_sha256` in `certificates/selected-result.json`, with κ = 1672188119205421/10¹⁸.
- **Adds:** this directory and one Makefile target.

## Why

Existing independent checks of the current chain each stop at a stated boundary:

- **#1049** checks the leaver local words.
- **#1091** checks the T16 owner maps.
- **#1069** checks the pricing chain, from profile through deficit and endpoint to κ. It explicitly excludes invoices.
- **#1052** recomputes the 94 outer slacks and 14 bootstrap steps, but only for the historical #942 T37 record.
- **#771** (theon199, open) independently reproduces the nine finite invoice guards and the 2,628-bit group order, but for the earlier #626 invoice (row coefficient 16,467), not the selected #1042 invoice (16,469).

That left the finite invoice of the selected record without a check outside the retained `assemble.py`. The same was true of its seven-plus-seven bootstrap levels and its 47 + 47 outer slacks. The finite invoice covers the per-vertex envelope and the nine strict size guards (router, literal, precision, tape, row and the others listed below).

## What `verify.py` checks

It uses only the standard library. It imports and executes nothing from the repository. All inputs are pinned and read as data:

- the committed assembly;
- the members `t16/global/audit/OWNERS-AND-PROFILE.json` and `PREFIX-AND-INVOICE.json` from the committed `selected-replay.tar.gz`. Each is checked against the assembly's own `input_sha256`, and the archive's `t16/ASSEMBLY.json` must be byte-equal to the committed file;
- PR589's `EXPECTED.json`, checked against git blob `e293ddc5…`.

The verifier recomputes every quantity and compares it exactly with the record.

1. **Profile composition.**
   - There are exactly 144 calls, one per (stage, replica) in 9 × 16, with forward and backward orientations alternating.
   - The per-call paid profiles sum to the selected local profile.
   - The idle remainders `{1:2249, 2:1, 3:400, 7:3, 16:47, 48:4850}` are nonnegative and number 7550.
   - Rank mass is 1,041,408 and the deficit is 73 · 14336 − mass = 5120.
   - The halving guard holds: 73² = 5329 > 2 · 48² = 4608.
2. **Per-vertex envelope.**
   - Actual selected primitives: 28,625,376. Wrapper factors: 9,953,280.
   - Adapter formula, compiler 64 · 74³, nonlocal item count, unhosted per-vertex 3,588,959,010,714,576 and hosted rebased per-vertex value.
   - The retained prior overcharge gives a used allowance of 6,466,906,000,439,144.
   - The physical stock identity sums to 14,826.
3. **The nine strict finite guards.** The table below gives the headroom in bits; all nine recorded bit lengths match.
   - **Group order.** The charged group order is computed in two independent ways: 2^(n²)∏(2^(2j)−1), and the orbit–stabilizer count of hyperbolic pairs. Both give n = 36, i.e. |Sp(72,F₂)|.
   - **Interpretation.** In characteristic two, the orthogonal group of a nondegenerate quadratic form in odd dimension 2n+1 is isomorphic to Sp(2n,q). So this number is |O(73,F₂)| for the parabolic quadratic form, for m = 73. That is one reading of the "full finite orthogonal group" named in `research/native-complex-moment552/PROOF.md`.
   - **Relation to #771.** #771 reads the same group as the isometry group of the standard dot product on F₂⁷³. It checks that reading by enumerating orthonormal bases in dimensions 1–7. That group has the same order, so the invoice is identical under either reading.
   - **Brute-force check.** The verifier enumerates every invertible matrix preserving the parabolic form x₀² + Σ x₂ᵢ₋₁x₂ᵢ. It finds |O(3,2)| = 6 and |O(5,2)| = 720, matching the formula. This is a different object from #771's, so the two checks complement each other.

   | Guard | Bound | Headroom |
   |---|---|---|
   | local primitive bound | 2⁴⁸ | **4 bits** (10,038,040,553,630 ≈ 2^43.19, about 28×) |
   | logical (group · used + 64) | 2⁶⁰⁵⁰ | 3,370 bits |
   | router | 2³⁰⁰⁰⁰ | 22,012 bits |
   | literal | 2¹⁰⁰⁰⁰⁰ | 64,716 bits |
   | mass (streamed mass vs 2¹⁰⁰⁰⁰⁰) | 2¹⁰⁰⁰⁰¹ total | 97,352 bits |
   | precision 32·73·B² | 2²¹⁰⁰⁰⁰ | 9,988 bits |
   | tape | 2²¹⁰⁰⁰⁰ | 109,998 bits |
   | row coefficient 2·2642+9909+252+1024 | 20,161 | 16,469 < 20,161 |
   | halving | — | 5329 > 4608 |

   Prefix: the local maximum is 68 bits. The global prefix is 68+37+144+144+4 = 397, charged at 512; the row reserve is 2 · 512 = 1024.
4. **Bootstrap and outer assembly, for both the native and the conservative endpoint.**
   - **Bootstrap.** It has seven affine levels from 384599/10¹⁰, with target s = min(c, (1−β)b) − 10⁻²⁷ and η = β = 10⁻²⁴. All 14 (exponent, gap, cutoff) records match exactly.
   - **Outer slacks.** All 47 + 47 slacks equal the recorded rationals exactly and are positive.
   - **κ.** Each κ is the largest 10⁻¹⁸ grid point strictly below the absorption margin εq.
   - **Controls.** The four recorded outer controls (`next_grid`, `zero_eta`, `zero_beta`, `unit_beta`) are re-derived as failures.
5. **PR589 bit side.**
   - The bit endpoint equals PR589's recorded `bit_lower`.
   - The bit deficit is 32(2·4·111 − 9·63) = 10,272, and it equals 64·live − mass for PR589's profile.
   - The endpoints are ordered conservative < native complex < bit.

### Additional observations

- **The bootstrap cutoffs do not depend on the prefix reserve.** At every one of the 14 steps the quadratic term ⌈36/gap²⌉ decides the cutoff. It keeps deciding it for any reserve P ≤ 6,566,539 in ⌈2(4+P)/gap⌉. So this lineage's 512-bit linear term, where T37 used 1024, does not affect the recorded cutoffs.
- **The tightest finite guard is the local primitive bound, not precision.** Its value is dominated by local adapters × compiler (387,056 × 25,934,336). Future provider words with more macros or children consume this 28× margin first.
- **The smallest outer slacks are η-scale.** For example, λ − τ = aη ≈ 1.7 × 10⁻²⁷, followed by β = 10⁻²⁴. They are positive by construction, not by numerical margin.

### Negative controls

There are 15 controls, and each must be rejected. Every one is rejected at its intended check:

- one extra idle child;
- one call's primitive count changed;
- one call dropped;
- one orientation swapped;
- one extra physical register;
- the retained prior overcharge dropped;
- recorded router bits off by one;
- row coefficient set to the bound;
- κ + 10⁻¹⁸;
- one outer slack edited by 10⁻⁴⁰;
- one bootstrap cutoff off by one;
- bit endpoint − 10⁻²⁴;
- complex endpoint + 10⁻²⁴;
- a count- and mass-preserving idle edit introducing a rank-52 child, which fails only the halving guard;
- group |Sp(70,2)| in place of |Sp(72,2)|.

## Reproduce

```sh
make frontier1042-invoice-audit-verify
```

Expected output:

```
PASS_FRONTIER1042_INVOICE_OUTER_INDEPENDENT | guards 9 | slacks 94 | bootstrap 14 | controls 15
```

Six unit tests should then pass. The run takes about 1.5 s on Python 3.10+, needs no network, and reads the committed archive without extracting it. `RESULT.json` is regenerated and compared byte for byte; `--write` rewrites it.

## Scope and independence

- **How the formulas were obtained.** The definitions of the envelope, the guards, the bootstrap and the 47 constraints exist only as code. They live in the retained `code/assemble.py` and the `engines/outer.py` engine (sha `c1ebb521…`). Their conceptual source is `notes/three-stage-cover-assembly.tex`, § "Full finite router and completed-child guard". I read those definitions and re-implemented them separately; nothing from them is imported or executed.
- **What this does and does not catch.** It is an independent re-computation. It catches transcription, data-binding and arithmetic errors in the selected record. It does **not** independently justify why these particular formulas are the right charges.
- **What is taken as data.** Taken as given are:
  - the semantic content of the receipts: local words, Clifford phases, owner windows and hosting. Those are covered by #1049, #1091 and the maintainer replay;
  - the two moment endpoints `complex_lower` and `conservative_complex_lower`. Those are certified by the two retained engines and independently by #1069.
- **Inherited assumptions.** All the record's conditions remain: all-size/compiler, common-label/mutable-source realization, whole-call hosting, precision/tape, exact recovery, analytic transfer and bit H1–H5.
- **What this is not.** It is a finite check of one certificate. It is not a formal proof, and it is not a verification of the multiplication theorem.

## Credit

- **Construction:** Jeremy Kothe (#1042 and its chain), with Rohan Arun's #987 slot search, Hao Yan's #858 T16 controller and the full lineage credited in `research/gauge44-slots-t16`. The bit supplier is DreamingOfClouds' PR589 on eumemic's PR555.
- **Assembly and guard engines:** the retained engines and their authors as named in their headers: icekylinx (PR144), Zhihao Chen (PR23), eumemic and hipotures' balanced transform.
- **Predecessor guard audit:** theon199's #771 established the group order and the nine-guard recomputation for the #626 invoice, including the row-guard sensitivity to replacing the group with GL(73,2). This package extends that check to the selected #1042 invoice, the per-vertex envelope, the bootstrap chain and the outer slacks. It does not claim priority for the group-order identity.
- **Neighbouring audits whose boundaries this complements:** #1069 and #1051 (Sagar Thakrar), #1052 (steph4n-gh), #1091 (JosieElliston), #1049 and #1009.

Prepared by Wronskode (@Wronskode) with substantial AI assistance from Claude (Anthropic) via Claude Code. New material is Apache-2.0.
