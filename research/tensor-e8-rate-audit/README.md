# Tensor E8 rate audit: the center-copy correction controls convergence

The paid profile in PR647's retained tensor-provider proof passes an
independent count and moment audit at every depth 1–66. Its asserted limit
is corroborated, and [PROOF.md](PROOF.md) derives the sharper expansion

    9^n k_n = 28/(2739 log 3) * (1 - (3/2)(3/5)^n) + O(n/9^n).

Here k_n is the root of that profile's moment equation. It is not a new
multiplication saving or a claim to realize a different physical supplier.
The copied-center correction dominates the other asymptotic profile effects.
At depth 66, the scaled root is below its limit by less than 4e-15 relatively.

Reproduce from the repository root, Python 3.9+ with no dependencies:

```sh
python3 -B research/tensor-e8-rate-audit/verify.py --check research/tensor-e8-rate-audit/RESULTS.json
```

Expected: `PASS_TENSOR_E8_RATE_AUDIT: 66 depths; 9 negative controls; exact rational bounds`.
Additional independent checks: `python3 -B research/tensor-e8-rate-audit/test_verify.py`.
Assertions are not used for acceptance, and isolated optimized execution is supported.

Two implementations reconstruct the profile: aggregated chronological register
lifetimes and a closed level sum. Exact rational log bounds give a rigorous
root enclosure without numerical root finding. The receipt records all 66
profiles' hashes, counts, masses and rational bounds. Decimal fields are
truncated display values; use the fraction fields as bounds. This finite
replay supports the accompanying algebraic proof and does not formalize it.

The new evidence concerns the general-depth profile retained in #647;
#647's packaged verifier primarily realizes depth one. Its broader scalar,
frame, ownership, exact-RAM and Fourier claims are not certified by this audit.
No earlier closed search is reopened. No selected certificate changes.

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Audited PR647: `956bb581e7f97328e1b53baa5aca3d2490f2f607`.
[Source pins](SOURCE.json), [assignment and local claim](CLAIM.json),
[validation](VALIDATION.md), [attribution](NOTICE.md).
