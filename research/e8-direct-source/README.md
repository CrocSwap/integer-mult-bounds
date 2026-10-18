# Direct-source E8: remove 120 paid-copy input helpers

This concrete depth-one variant of [PR647](https://github.com/CrocSwap/integer-mult-bounds/pull/647)
feeds the actual source registers into the pair/gather core. It removes 120
live helpers, 720 global recursive children and their required scalar copies
and compensation work. Both directions restore every remaining dirty helper.

The new exact profile is

    m=27, W=7088, R=6848,
    H={1:40680, 2:240, 7:20160, 8:1080, 9:48}, deficit=24.

It admits the Gaussian-RAM saving **1/14100**, with exact rank-mass slack
above 11/100. The old profile fails at that same value; the predecessor's
explicit certified saving was 1/15000. This is a weaker alternative supplier
than existing community records. No new integer-multiplication kappa or
selected-frontier change is claimed.

Reproduce with Python 3.9+ and no external dependencies:

```sh
python3 -B research/e8-direct-source/verify.py --check research/e8-direct-source/RESULTS.json
python3 -B research/e8-direct-source/test_verify.py
```

Expected: `PASS_E8_DIRECT_SOURCE: 7088 columns in both directions; 120 fewer helpers; 7 negative controls`, then three tests `OK`.

The verifier generates the word, checks every live symbolic column in both
directions, chronological frames, exact phase lowerings, full scalar/child
invoices and rational moments. The receipt binds both words by SHA256.
Additional tests execute 48 physical character instances with modular Gaussian
phases, including center descent/ascent. These are finite checks supporting
[the construction proof and complete recurrence](PROOF.md), not a formal proof.

The pinned predecessor's phase and binary-linear-algebra utilities are
vendored unchanged and authenticated. **Run without `-O`**: that mode is
explicitly refused because the inherited utilities use assertions. This reuse
is disclosed; the entire verifier is not claimed to be an independent rewrite.
All new symbolic execution and construction logic is in `verify.py`.

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
PR647 source: `956bb581e7f97328e1b53baa5aca3d2490f2f607`.
[Source pins](SOURCE.json), [claim](CLAIM.json), [validation](VALIDATION.md),
[attribution and license](NOTICE.md).

The scope is the predecessor's fixed-depth exact complex RAM. Its cover
routes, common positive-kernel charts and explicit padding compiler are
retained with fewer helper roles. Bit arithmetic, numerical precision,
fixed-tape realization and multiplication assembly remain outside this result.
The prior [PR682 audit](https://github.com/CrocSwap/integer-mult-bounds/pull/682)
checks the unchanged predecessor's tensor-depth profile; this contribution
changes the depth-one construction and does not depend on that audit's code.
