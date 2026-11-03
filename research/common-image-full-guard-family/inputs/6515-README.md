# Six-event binary full-guard product inequality

**Claim type: scoped counting proof with an exhaustive finite spectrum. No new κ.**

For every m ≥ 6, six pairwise orthogonal rank-one full-guard events on a
uniform matrix G ∈ GL_m(F_2) are strictly rarer than the sixth power of one
such event. At m = 6 the joint count is 0. At m = 7 it is exactly 23,040
headers. The ratio then increases toward 1 and stays below it.

This is the k = 6 case left open by JoyboyBrian's handoff
[comment 19144831](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144831).
The character law is Nick Petalas's #4275. The k = 5 theorem is Ryanson
Jonathan's #4607. The single-arc and two-star eigenvalues are the sharp
#5146 spectrum, used here only at k = 6. Selected κ stays
781451/250000000.

## Result

The proof enumerates all 2^30 zero-diagonal characters. Their signed
transform is

```text
N_n = 729^n − 30·567^n + 120·513^n + R_n,    R_n ≤ 1073741673·495^n.
```

Exact integer comparison gives the strict ratio for 7 ≤ m ≤ 130. For every
larger m, that tail fits under 27 single-arc modes. The three modes left
over dominate the degree-four gap between (X−1)^5 and the six-event GL
denominator. Details, the induction, and the limits are in `PROOF.md`.

## Reproduce

From the repository root, CPython 3.12 and gcc, standard library only:

```sh
python3.12 -B research/six-event-guard-correlation/verify.py
python3.12 -B scripts/research_package.py --package research/six-event-guard-correlation
```

The verifier compiles `spectrum.c`, checks the three-state sum against the
subset form at k = 3 and k = 4, matches the published k = 3 and leading k = 5
coefficients, then checks the k = 6 theorem. It prints
`PASS_SIX_EVENT_GUARD_CORRELATION`. One normal run is the certificate. The
2^30 pass takes under a minute on this host. No files are written into the
package. Lean, Docker, selected-frontier replay and an independent human
review were not run.

## Open next questions

1. **k ≥ 7 in the finite strip.** The same product inequality is open for
   seven or more orthogonal guards below the #5146 eventual range. The first
   step is a support-truncated spectrum, or an exact count of length-k
   rectangle decompositions of J−I, at k = 7. The blocker is that the raw
   character space has order 2^42, so the k = 6 Gray code does not extend.
2. **Nonorthogonal kernels.** A single shared direction can change both the
   marginal and the joint count. The first step is one explicit pair of
   nonorthogonal rank-one idempotents at m = 7 whose six-event ratio meets
   or exceeds 1, or a reduction to the orthogonal case. Nothing in this
   package prices that configuration.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
