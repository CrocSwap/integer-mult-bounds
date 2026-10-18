# Local validation receipt

Validated on 2026-10-17 UTC using Python 3.12, on base
`997e6a9ca7b4f95d50e366f61412fd640d72a88a`:

```sh
python3.12 scripts/research_package.py --package research/rank7-terminal-information-barrier
```

Result: `PASS_REGISTERED_RESEARCH_PACKAGE`, outcome `negative-result`.
Both registered commands ran with `-I -O -B` and returned success:

- `PASS_ALL_RANK_LE7_ENDPOINTS_DYADIC_NUISANCE_SURJECTIVITY`
- `PASS_INDEPENDENT_TERMINAL_INFORMATION_BARRIER`

Both authenticated providers produced 43,435 endpoints, 239 support classes,
maximum support size 16, 58 eligible low-rank slots, and the determinant counts
in the README. The primary path checked both inverse products for each minor,
eight rejecting controls per provider and the actual rank-eight pre/post maps.
The independent path checked seven rejecting controls with exact expected
diagnostics, complete scalar blocks over the dyadic ring, and a separate
rank-eight inverse-column/adjoint-row pairing. The fixed certificate SHA256 is
`aa720fe2591cc511b58a0faea7752aba3c72ef90164b606eb9c0e437b9fa8863`.

A separate specialist review compared the two implementations on all 4,583
operations, 520 frame spans, 165 complete output rows (164 of rank at most seven
plus register42), 239 support multiplicities, and the rank-eight inverse vector.
It found exact agreement. Mathematical review confirmed the causal and
indistinguishability arguments and led to the explicit linear-encoding
restriction on the secondary dimension bounds.

A fresh pre-submission review additionally compared all 520 complete operator
rows and 11,912 coefficients on each provider, all 520 frames, the endpoint
partition and the rank-eight inverse vector. Fourteen disposable variants with
named validation checks removed were detected by the existing controls; a valid
alternative gzip encoding separately tested source-byte authentication, and a
noncommuting two-generator fixture checked word direction and cancellation.
This was additional author-review work, not a third registered independent
verifier; its scripts and receipts are retained by the author outside the package.

The pre-submission mathematical fixes make the post-prelude entrance cut and
inherited center-cut frame convention explicit, fix the dependency graph and
output identities against control side channels, require joint ancillary
independence, and qualify sharpness by a nonzero module. The task card now
declares changed scope: this negative result does not satisfy the original
positive-construction acceptance gate. Fresh mathematical and packaging reviews
found no remaining issue within those stated limits.

This receipt records local computation and AI-assisted mathematical review.
It is not hosted CI, human peer review, formal-kernel verification, a full native
supplier replay, or admission of a new multiplication bound. The original selected
certificate and all predecessor sources are unchanged.
