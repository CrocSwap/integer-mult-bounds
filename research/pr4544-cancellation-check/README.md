# Independent check of #4544: the sharp cancellation threshold

**Task:** independent-moment (independent source-bound coverage). **Base:** canonical main `f626db5c`. **No new κ.**

Clear1nsight's #4544 (head `0898b3a8`) audits the implication (10) ⇒ (11) in zxv's #4483, `research/rank-convergence/PROOF.md` Section 4, and states that its threshold is sharp. This package checks each of #4544's claims with a separately written exact verifier. Nothing is imported from #4544's checker.

## Results

All of #4544's claims are confirmed.

1. **Slack identity.** With `I = B+F+A`, `(1−β)(ηI−B−F) = (η−β)A − (1−η)F + (1−η)(βI−B)` holds as a polynomial identity in ℚ[β, η, B, F, A]. A rejection control that drops the mirror term fails.
2. **Extremiser.** At `B* = β(A+F)/(1−β)` the exit fraction equals `(βA+F)/(A+F)`. This is checked as a polynomial identity after clearing `1−β`. The fraction is linear-fractional in `B` with derivative numerator `A ≥ 0`, so the maximum over `0 ≤ B ≤ B*` is at `B*`. An exact grid of 11,968 cases confirms that the uniform guarantee holds iff `(η−β)A ≥ (1−η)F`.
3. **Necessity of #4483's own (10).** If only (3) `F ≤ X` and (9) `A ≥ D·X` are known, with `X = P^(G+1)`, the adversary takes `A = D·X`, `F = X` and a saturated mirror. Its exit fraction is `(βD+1)/(D+1)`, and `(D+1)(η − (βD+1)/(D+1)) = (η−β)D − (1−η)` identically. So (10) is exactly the uniform condition, which supports #4544's statement that no better threshold follows from these scalar premises.
4. **Failure controls.** For the root-debit control, with `β = 1/4`, `η = 1/2`, `F = 1`, gross production 2 and `R = 1/2`, the exit fraction is `11/20 > η`. The gross test passes with equality and the net test rejects. The leaf-omission control gives an exit fraction of 1.
5. **Binding.** The pinned source (sha256 `3c971c56…`, blob `75f45183`) states equations (2), (3), `A_t = (T−P)H_t − R_t`, (9), (10), (11) and the premises `B_t ≤ βI_t` and `β < η < 1` verbatim, as #4544 uses them.

I also replayed #4544's registered package at its head: `PASS_REGISTERED_RESEARCH_PACKAGE research/adaptive-cancellation-audit` in 1.3 s.

## Verify

```text
python3 -B research/pr4544-cancellation-check/verify.py
```

This runs in under 1 s with the standard library only.

## Limitations

- This checks #4544's scalar lemma and its binding only. The Chernoff bounds behind `D`, the mirror certificate, funding and realisation are out of scope, as #4544 also says.
- #4544's upstream diff also carries shared CI and navigation repairs from its preparation base. Those are not reviewed here.

## Open next questions

- Whether actual-flow correlations between `F` and `A` give a strictly better uniform threshold than (10). First step: bound the joint occupation of leaf exits and net production on one certified witness and compare it with the adversary in item 3.

Credit: zxv (#4483) and Clear1nsight (#4544). Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
