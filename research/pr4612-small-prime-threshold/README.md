# Small-prime check of #4612's outer-reserve threshold

**Task:** independent-moment (scoped correction). **Base:** canonical main `f626db5c`. **No κ or exponent change.**

## The claim

Matarener's #4612 (head `7e362114`) audits #4359's BIT row stock. Its "Threshold" paragraph and `outer_reserve()` check concern the bound q0(h, p) ≤ C(log₂h + h^δL³ + 1), with L = log₂p and δ ∈ {0.003, 0.004}. They state that the displayed threshold

```text
H(p) = [1024 C L³]^(1/(1−δ))
```

"already suffices" **for every C ≥ 1**, and that "C(log₂h + 2) ≤ h/1024 there as well". From this, #4612 concludes q0 + O(1) ≤ h/64 and R(h) ≤ 3h/128 + q0 ≤ h/16. Its finite grid uses only L ∈ {8, 64, 1024, 2²⁰, 2⁴⁰}, that is, p ≥ 256.

## Findings

These are scoped, wording-level findings.

- **The intermediate claim fails at p = 2.** At L = 1, C(log₂h + 2) ≤ h/1024 fails at h = H for every tested C, from 1 to 2¹⁰⁰⁰.
- **q0 ≤ h/64 fails at p = 2 for #4612's own constant.** With the width constant C = 232,960, the q0 bound is about 0.0276·h > h/64 at h = H(2).
- **The conclusion R ≤ h/16 can fail at p = 2.** For C = 2⁴⁰, 2¹⁰⁰ and 2¹⁰⁰⁰, R(h) ≤ h/16 fails at h = H(2) for both atoms. Only when log₂C is so large that the factor (1024C)^(δ/(1−δ)) dominates (2¹⁰⁰⁰⁰, say) is the displayed threshold enough again.
- **Why #4612's grid missed this.** The grid uses L ≥ 8, and the verifier confirms that every point in it passes.

## Correction

```text
H′(p) = max( [1024 C L³]^(1/(1−δ)),  4096 C log₂(4096 C) ).
```

**Proof.**

1. Put a = 1024C ≥ 1024. At h = 4a log₂(4a), we have a(log₂h + 2) ≤ h, because log₂log₂(4a) + 2 ≤ 3 log₂(4a).
2. h − a log₂h is increasing for h > a/ln 2, so the inequality persists above that point.
3. Above H we also have C h^δ L³ ≤ h/1024.
4. Hence q0 ≤ h/512 ≤ h/64 and R ≤ h/16. ∎

The added term does not depend on p, so the threshold remains polylogarithmic in p. #4612's conclusions survive with H′. Only the claims "no extra multiple is needed" and "for every C ≥ 1" need the amendment.

The verifier checks the corrected threshold on a grid that includes L = 1 and the small primes 3, 5 and 7, with log₂C from 0 to 10,000.

## Verify

```text
python3 -B research/pr4612-small-prime-threshold/verify.py
```

The check runs in under 1 s and uses the standard library only. It uses log-domain floats, with margins of at least 10⁻³ in log₂ units at every failure.

## Limitations

- **C is unbound.** The actual constant C is still unknown; binding it is #4612's open question 1. With the illustrative log₂C ≈ 2 log₂N + 64 ≈ 1.3·10¹⁰, the displayed H already suffices, because the δ-factor is enormous.
- **No other checks redone.** This package does not re-check #4612's other statements.

## Open next questions

- **Bind C to the #4470 template.** Then state the exact threshold. First step: see #4612's open question 1.

Credit: Matarener (Mark) for #4612, and zxv, Cinna Davis and the #4359/#4470 lineage. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
