# Bootstrap cutoffs: the time constant needs no cutoff (repair (b))

**A scoped proof repair for one finite lemma. The numerical κ, the certificate, the suppliers and the frontier are
unchanged. No new bound is claimed.**

PR #1956 ([`bootstrap-cutoff-carry`](https://github.com/CrocSwap/integer-mult-bounds/pull/1956)) showed that the 14
recorded bootstrap cutoffs of the selected #1094 receipt (`research/community-frontier1094-audit/ASSEMBLY.json`)
are not valid instances of the cutoff lemma **as written** in
[PR387's PROOF](../bootstrap-depth-audit/sources/pr387/PROOF.md) and
[FINITE_BIT_ACCOUNTING](../five-stage-source527-banks/proof/FINITE_BIT_ACCOUNTING.md). That lemma's C must
dominate the "previous ordinary constants". The carried time constant `C_old·2^(L·Δa)` is about twice too large
for every stage after the first. PR #1956 left open whether a restated lemma ("repair (b)") makes the recorded
numbers valid. This package answers that question for the time constant: yes, under hypotheses (H1)–(H3)
below, which are read from the retained sources but not re-proved. Under them the cutoff has only one job, to
make the borrowed stock fit, and no previous time constant needs to enter it. The recorded cutoffs then reduce
to a space obligation with a large exact margin. That obligation is **not** discharged, because the actual
stock coefficients σ_j are not computed here.

## The two jobs of the 1/16 condition

At a bootstrap stage, write `a = a_(j-1)`, `a' = a_j = (1−s)s + s·a`, and let δ be the minimum of the four gaps
`s−a'` (atom), `1−a'−s` (borrowing), `1−a'−s(1−a)` (remainder) and `1−s` (stock). The lemma takes
`e ≥ e0 = 2^L` so that `C(1+log2 e)e^(−δ) ≤ 1/16`, and says "every lower-order toll is covered **and the
borrowed high part fits**." These are different requirements.

**Fit (space).** The stopped construction at width e borrows `k = ⌈log_q S(e,w)⌉` high digits, where
`w = ⌈e^s⌉` and `log_q S(e,w) = O(w log e)`. S counts the row divisors over the recursion depth times the
inherited old-leaf reserve. The construction is defined only when `k < e/2`
([`three-stage-cover-rows.tex`](../five-stage-source527-banks/proof/three-stage-cover-rows.tex), "Borrowing and
restoring the stock": "For sufficiently large e, k<e/2 … Small widths use the retained supplier directly").
This needs a genuine threshold. No constant can be enlarged to pay for it.

**Time.** Every other use of the condition only bounds a lower-order time toll by the main term. That needs no
threshold, because each toll is bounded by a constant times `e^(1−a')` for **all** `e ≥ 1`:

> **Absorption bound.** For `δ > 0` and all `t ≥ 0`,
> `(1+t)·2^(−δt) ≤ M(δ) := max(2, 2/(ℯ·ln2·δ))`, where ℯ = exp(1) (e is reserved for the width).
>
> *Proof.* If t ≤ 1, the left side is at most 2. If t ≥ 1, then `1+t ≤ 2t`, and `exp(y) ≥ ℯ·y` gives
> `2^(δt) ≥ ℯ·ln2·δt`. Hence the left side is at most `2/(ℯ·ln2·δ)`.

## Restated lemma

*Retained hypotheses, which are not re-proved here.* (H1) `A_(j−1)` is a completed ordinary algorithm at every
width `e ≥ 1`, with `T_(j−1)(e) ≤ C_(j−1)·V·e^(1−a)`. (H2) Whenever `k(e) < e/2`, the stopped construction is a
completed ordinary algorithm at width e with

    T(e)/V ≤ K·[e^(1−s) + e^(1−a') + e^s(1+log2 e) + w^(1−a)].

Here K is finite and does not depend on e or on the cutoff. K is built from fresh coefficients (multiplicities,
the weighted-induction factor `1+1/(1−μ_1)+1/(1−μ_τ)`, scalar/wrapper/padding counts, the stock coefficient
inside the high-part exchange) and from `C_(j−1)`, which enters through the ordinary leaves, the remainder, the
routing and the high-part exchange. This is the retained stopped-leaf estimate of PR387 with its O-constant
written as K. The sources state it asymptotically ("for large e", `k = o(e)`). Its quantifier "whenever
`k < e/2`" and the independence of K from the cutoff are a reading of those sources, not a quotation.
(H3) `log_q S(e,w) ≤ σ·w·(1+log2 e)`, where σ is a *stock* coefficient. It is built from the
per-level row stock, the depth factor and the old algorithm's logarithmic row-reserve coefficient. It contains
no time constant.

**Lemma (repair (b)).** Let `ℓ ≥ log2(8σ)` and `L ≥ max(2, 36/δ², 2(4+ℓ)/δ)`, and set `e0 = 2^L`. Let `A_j`
run the stopped construction for `e ≥ e0` and `A_(j−1)` below e0. Then:

1. `A_j` is defined (the stock fits) for every `e ≥ e0`.
2. `T_j(e) ≤ C_j·V·e^(1−a')` for all `e ≥ 1`, where
   `C_j = max(K·(4+M(δ)), C_(j−1)·2^(L·(a'−a)))`.
3. L depends only on δ and σ. The time constants `C_(j−1)`, K and `C_j` never enter it.

*Proof.* (1) Put `t = log2 e ≥ L`. As in the original lemma, `log2(1+t) ≤ 3√t ≤ δt/2` and
`log2(8σ)+4 ≤ δt/2`, so `8σ(1+t)e^(−δ) ≤ 1/16`. Since `δ ≤ 1−s` and `w ≤ 2e^s`,
`k ≤ 2σe^s(1+t)+1 ≤ (e/4)·8σ(1+t)e^(−(1−s)) + 1 ≤ e/64 + 1 < e/2` for `e ≥ 4`.
(2) For `e ≥ e0`, apply (H2) term by term. `e^(1−s) ≤ e^(1−a')` because `s > a'`.
`e^s(1+t) = e^(1−a')·(1+t)2^(−(1−a'−s)t) ≤ M(δ)·e^(1−a')` by the absorption bound, since `1−a'−s ≥ δ` and M is
decreasing. `w^(1−a) ≤ 2e^(s(1−a)) ≤ 2e^(1−a')` because of the remainder gap. For `1 ≤ e < e0`,
`T_(j−1)(e) ≤ C_(j−1)e^(1−a)·e^(a'−a) ≤ C_(j−1)2^(L(a'−a))·e^(1−a')`. (3) follows from the definition of L. ∎

The original lemma's next constant `C_large + C_old·2^(L(a_(j+1)−a_j))` dominates this `C_j`, with
`C_large = K(4+M(δ))`. The induction stays sequential: `σ → L → C_j → (σ_(j+1), next stage)`.

**Consequence for the selected receipt.** Read with C = 8σ (a space constant) instead of a constant that
dominates the previous time constant, the receipt's formula `max(⌈36/δ²⌉, ⌈2(4+512)/δ⌉)` is an instance of
the restated lemma whenever `8σ_j ≤ 2^512`, that is, whenever `σ_j ≤ 2^509`. In fact each recorded cutoff supports much more. The verifier
computes the exact largest `ℓ` each one admits (`stock_headroom_log2`). It is 6,562,783 bits at stage 1 and
grows by about 1/s per stage, to about 3·10^23 bits at stage 7. Every one of the 14 recorded cutoffs is
therefore a valid fit cutoff for any stock coefficient `σ_j ≤ 2^(H_j−3)`, where `H_j` is that stage's headroom.
At stage 1 this means `σ_1 ≤ 2^6,562,780`. The carried time constant stays
finite and does not feed back into L. Under the receipt's own assumption that fresh time constants are below
2^512, the verifier's explicit chain bounds `log2 C_7` by a 27-digit integer. That chain also assumes
`K_j ≤ 2^512 + 2^512·C_(j−1)`, which is a modeling assumption stronger than (H2)'s finite K. It only illustrates
finiteness and plays no role in the cutoffs. On the other side, the carried
factor alone gives `log2 C_(j−1) ≥ L_(j−1)·Δa_(j−1)`, which already exceeds the stage-j headroom for every
j = 2..7. This reproduces PR #1956's finding from the other side: the lemma *as written* fails exactly at
stages 2–7.

So, under (H1)–(H3), the recorded cutoff numbers are valid exactly when every `σ_j ≤ 2^(H_j−3)`. If that holds,
only the proof text needs to change. The condition is plausible by a wide margin, but it is not verified here.

## Remaining obligations (not discharged here)

- **(H3) and the stock coefficient.** The stock coefficient must contain no time constant. Each `σ_j` must
  satisfy `log2(8σ_j) ≤ stock_headroom_log2[j]`, which is a margin of millions of bits or more. This rests on
  the retained complete-row contract: the old supplier's row reserve is logarithmic, and that bound has the same
  shape at every stage, so the below-cutoff branch does not multiply it by `2^(LΔa)`. This package does not
  re-derive that contract or compute the actual σ_j.
- **(H2) form.** The retained stopped-leaf estimate is taken with its O-constant K independent of the cutoff, as
  PR387 and the weighted induction of FINITE_BIT_ACCOUNTING state it. If any other "sufficiently large e"
  condition hides in the inherited primitives (PR185 lineage), it is a further fit condition. It needs its own
  coefficient checked against the headroom, and it may not contain a time constant.
- Other lineages (T37's 1024-bit receipts, open PRs #1424, #1586 and #1724) use the same formula. The argument
  applies to them verbatim, but their headrooms are not computed here.
- Every other inherited all-size, precision, hosting and analytic obligation of the selected record.

## Reproduce

```sh
python3 -B research/bootstrap-cutoff-time-space-split/verify.py
python3 scripts/research_package.py --package research/bootstrap-cutoff-time-space-split --check-only
python3.12 scripts/research_package.py --package research/bootstrap-cutoff-time-space-split
```

Expected: `PASS_BOOTSTRAP_TIME_SPACE_SPLIT recorded=14 fit_only_valid=14 written_rule_fails=12
time_constant_finite=2 controls_rejected=7`, in well under a second, using the standard library only.

The verifier checks every input against [SOURCES.json](SOURCES.json). It binds the lemma text, the fit statement
in `three-stage-cover-rows.tex` and the assembler formula in the pinned `upstream1087.tar.gz`. It then checks the
following in exact rational arithmetic:

- the 14 cutoffs reproduce from the receipt's chain;
- δ never exceeds the stock gap;
- each cutoff satisfies the fit-only rule with the exact headroom (`ℓ` passes and `ℓ+1` fails);
- certified rational lower bounds `ln2 > 693/1000` and `ℯ > 2718/1000`, from series partial sums with tail
  bounds;
- the `3√t` step, from `9(ln2)²/2 ≥ 1`;
- the explicit time-constant chain.

The `ℯ` bound needs only a positive partial sum. The quartered-M control (control 3 below) uses the same
floating-point check. A floating-point check at the true maximizer `t* = 1/(δ ln2) − 1` and on a grid confirms that `M(δ)` dominates
the actual supremum. It is a sanity check, not a certificate. The verifier compares its summary with
[RESULT.json](RESULT.json).

Seven controls must be rejected:

1. a recorded cutoff minus one;
2. a stock coefficient one bit above the headroom;
3. `M(δ)/4` in place of `M(δ)`;
4. the false lower bound `ln2 > 0.6932`;
5. the false lower bound `ℯ > 2.719`;
6. the carried time constant put into the fit rule (the lemma as written, at stage 2);
7. a tampered gap.

## Open next questions

1. **Compute σ_j for the selected lineage.** Is `log2(8σ_j)` below the recorded headroom at every stage? We
   expect it to be far below. *First step:* collect the per-level row stock (`14400w+1`, depth factor, the
   `57,604` new contribution in FINITE_BIT_ACCOUNTING) and the old-leaf reserve coefficient from the PR185/#384
   complete-row contract. *Blocked by:* the reserve coefficient is stated only as "logarithmic" in the retained
   sources.
2. **Adopt the wording.** If maintainers accept the restated lemma, the proof texts (PR387 PROOF,
   FINITE_BIT_ACCOUNTING and their successors) could say "C dominates the stage's stock/fit constants"
   instead of "previous ordinary constants". PR #1956's corrected chain would then be needed only by readers who
   keep the original wording. *Blocked by:* maintainer decision. Frozen packages are not edited here.

## Credit

The cutoff lemma, its 1/16 inequality chain and the next-constant rule are from rohanarun's PR387 PROOF and
eumemic's five-stage bank proof. The borrowing/fit construction is from the retained
`three-stage-cover-rows.tex`. The chain and the 512 allowance are from the frozen PR1087 assembler (Jeremy
Kothe's package and its credited lineage) and Rohan Arun's PR1094 selected receipt. The receipt binding and the
question come from PR #1956 (`bootstrap-cutoff-carry`, same author). Prepared by Josie Elliston with Claude Code
(Claude Opus 5.5) assistance. Apache-2.0.
