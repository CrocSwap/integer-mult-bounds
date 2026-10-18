# Independent review of PR1731's rectangular batching and radix-distributed union schedule

**Independent review; no new κ. No mathematical error found in the reviewed scope; three
documentation inconsistencies noted.**

[PR1731](https://github.com/CrocSwap/integer-mult-bounds/pull/1731) (jeremykothe2, head `0666300e`)
claims conditional κ = 0.0016781238306335… on PR1673's capped phase-cell fusion outer. It adds two new
constructions. The maintainer's triage asks to "review the new W^5 rectangular boundary batching and
radix-distributed union schedule … and verify the cited rectangular exponent". This package does that
for the stated scope, with executable checks that import no PR1731, PR1673 or repository code.

## Findings

1. **The cited exponent is correct.**
   * Le Gall, *Faster Rectangular Matrix Multiplication by Combination Loss Analysis* (SODA 2024,
     arXiv 2307.06535 v2), Table 3 ("Our new upper bounds on ω(κ)") lists **κ = 5.00 → 6.156708**.
     Table 2 (the previous bounds of Le Gall–Urrutia 2018) has 6.157233. This was checked against the
     arXiv HTML rendering; it cannot be checked offline.
   * The paper's ω(κ) is the exponent of an n×n by n×n^κ product (`<n, n^κ, n>`). Cyclic invariance of
     the matrix-multiplication tensor gives ω(1,1,5) = ω(5), as PR1731 states.
   * PR1731 uses σ = 6.1567081, strictly above the bound, and its `RECT-BOUNDARY.md` supplies the
     effective-formula step: a fixed exact ⟨n,n,n⁵⟩ formula of rank below n^σ from strict slack,
     algebraic coefficients via the weak Nullstellensatz, and a polynomial roundoff envelope.
2. **The rectangular bookkeeping is consistent.** One ⟨W,W,W⁵⟩ product serves W·W⁵ right-hand-side
   entries. So the boundary arithmetic per axis is `(VW/B)/W⁶·W^σ = (V/B)·W^(σ−5)`. That is the old
   form `(V/B)·W^(τ−1)` with **τ_eff = σ − 4 = 2.1567081**.

   The other side conditions hold: σ > 6 (the leaves dominate the additions) and 2 < τ_eff < 5/2.
   Inside the union schedule, every line of one axis in a microbox shares that axis's factor page, and
   a microbox holds superpolynomially many records, so W⁵-wide batches are available; partial-batch
   padding is negligible.
3. **The radix-distributed union schedule is correct as an operator identity, and its movement row is
   right.**
   * *Why it is correct.* Each sparse factor is `T_i = I_{E_i^c} ⊕ T_i|E_i`. So the Kronecker product
     `Θ = ⊗T_i` is block diagonal over the flag classes `C_F = {x : F(x) = F}`, and on `C_F` it equals
     `⊗_{i∈F} T_i|E_i ⊗ I`.
   * Each `C_F` is a product set. The round-r axis-f substream depends only on the coordinates other
     than `x_f`, so it consists of complete `E_f`-lines (the key lemma). The `T_i` act on different
     tensor factors, so they commute.
   * Applying each record's flagged axes in successive rounds therefore reproduces Θ. The total
     movement is `Σ_r |S_r| = Σ_x |F(x)| = Σ_i |U_i|`, which gives the row exponent `ε + 1/2 − ξ`.
   * *Checked here.* An operator-level re-implementation built from the written description matches
     the mode-product Kronecker action exactly on 30 random integer instances (g = 2–4, L = 4–6) and
     on a dense-window instance with three flags per record. Both "smallest-first" and "largest-first"
     axis orders match, confirming commutation, and the volume identity holds.
   * *Negative controls.* A `T_i` that leaks `E_i^c → E_i` is rejected, which shows block
     diagonality is essential. So are a skipped second round and a truncated line.
   * *Why it was needed.* At PR1731's balance, PR1673's sparse-fraction premise is false
     (`ξ − β − 1/2 = −0.3419`), and the old g-factor union row has saving −0.3409.
4. **The balance and κ reproduce exactly.** From the written rows and PR1731's free slacks, this
   package re-derives ε = 0.999028950…, ξ = 0.579061124…, β = 0.420938875… and
   `κ = ⌊10¹⁰⁰·εq⌋/10¹⁰⁰ − 10⁻⁷⁶` = 0.001678123830633547…. The nine rows used are:

   | Row | Saving |
   |---|---|
   | main transform | εq |
   | fused Gaussian | 1−ε+qβ |
   | boundary | (3−τ)/2+ξ−ε |
   | group bit router | 1−ε+aβ |
   | global router | a |
   | group scans | 1−ε+β |
   | union | ξ+1/2−ε |
   | polynomial products | ε |
   | core-face corrections | 1−(ε+β−3) |

   The rows that bind are the main transform, fused Gaussian, boundary (+slack) and group bit router.
   The new union row has saving 0.0800, and every other row is far above κ.
5. **The supplier endpoint arithmetic is confirmed at 10⁻⁶⁴.** For the T74 profile
   `{1:1560432, 2:336336, 3:278724, 4:84912, 5:54612, 8:5328, 48:22748}` (m = 73, W = 66,304,
   deficit 23,680), the moment `Σ n_r r (m/r)^a/(mW) − 1` was enclosed with 220-digit correctly
   rounded `decimal` ln/exp, with outward widening:
   * it is **−2.9215·10⁻⁶⁴ at b** = certified endpoint − 10⁻⁶⁴ (accept);
   * it is **+2.9215·10⁻⁶⁴ at b + 2·10⁻⁶⁴** (reject).

   This checks only the moment arithmetic, not supplier admission.

### Documentation inconsistencies (no effect on the arithmetic)

* `outer/check_ledger.py` line 5 still describes "c=3/10 (tau=12/5, … ω<2.3728639 …)", and line 86's
  comment repeats it. The code actually uses `tau_eff = σ − 4`.
* Line 146's comment says the format is `<n,n,n^2;R>` and needs "σ > published ω(1,1,2)". The check
  is for k = 5.
* `outer/UNION-SCHEDULE.md` §4 says the reinstated old union row "is about −0.125". At this package's
  balance it is −0.341, as §5b and this review state; −0.125 appears to be left over from the k = 2
  package.

## Not reviewed (remaining obligations)

* **PR1673's inherited outer proof**, which this whole family depends on: the Toeplitz circuits,
  Gaussian conditioning, capped interiors, precision/tape and layout lemmas. The maintainer's triage
  of PR1673 asks for an independent audit of exactly these. They are taken as hypotheses here, as in
  PR1731.
* **T74 supplier admission** (controller, geometry, invoice, regenerated artifacts).
* The **tape-level** realization of the schedule: the variable-length transpose and the head
  accounting. PR1731's `sched_test.py` and LeverRank's `sched_review.py` implement it; this package
  checks the operator identity and volume, not head travel.

## Reproduce

Standard library only, from the repository root:

```sh
python3 scripts/research_package.py --package research/pr1731-union-rect-review --check-only
python3 -I -B research/pr1731-union-rect-review/verify.py
```

Expected output, in under a second:

```text
PASS_PR1731_UNION_RECT_REVIEW schedule_instances=30 kappa=0.001678123830633547 supplier_moment_resolution=1e-64x2 no_new_kappa
```

[PR1731-INPUTS.json](PR1731-INPUTS.json) vendors only the exact values used: the ledger's ε, ξ, β, κ,
q, a and slacks, plus B.json's b, b_above and profile. It records the SHA256 of the original
`LEDGER.json` and `B.json` at PR1731 head `0666300e5dfb35e3e6b90e65326fad6d049ff30a`. `--write`
regenerates [RESULT.json](RESULT.json). The script refuses to run under `-O`.

## Open next questions

1. **Independently audit PR1673's outer proof.**
   * *Why it matters:* PR1673 is the foundation of PR1721–PR1789 and later candidate κ claims; none of
     them can be promoted without it.
   * *First step:* take one interface the triage names, such as precision/tape composition or
     movement, and check one lemma of `phase_fusion_note.tex` against its supporting audit file with
     an adversarial instance.
   * *Blocked by:* the proof is long, and the review needs dedicated effort per interface.

## Credit

* **Constructions:** jeremykothe2 (PR1731's rectangular batching and union schedule).
* **Outer:** Vlado Vojdanovski (PR1673).
* **Earlier specialization of the matrix boundary:** Chafik Boukhalfa (PR1699).
* **Independent schedule implementation:** LeverRank (`sched_review.py`).
* **Cited exponent:** F. Le Gall.

Prepared for rtyu193-rgb with Claude Code (Anthropic Claude Opus 5.5) in one session, with no
subagents and no independent human review. Apache-2.0.
