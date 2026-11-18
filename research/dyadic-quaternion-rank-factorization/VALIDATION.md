# Validation

Author checks use CPython 3.12.16 on macOS arm64 and the standard library.
The normal and optimized registered commands treat warnings as errors.
Scientific checks use explicit exceptions, so optimization does not remove
any assertion. The release record reports their actual pass state.

The finite domain has 625 matrices from the complete five-letter `2x2`
alphabet, 35 constructed rectangular cases, five dense rectangular cases,
and four explicit witnesses. Each factor product and both inverse identities
are checked using the retained source multiplication formula. Independent
rational Gaussian elimination of the left-regular block matrix checks rank.
Every operation transcript, pivot and denominator promise is checked.

The complete source response/parity/divisor checks run unchanged. Source
hashes are checked before import. Rounding covers all 4,096 eighth-grid
points in a unit cube. The written rounding, termination and factorization
proofs cover the infinite domain; finite checks do not replace those proofs.

Release checks use committed bytes/source history/modes, a package export,
and both registered commands in a read-only tree without Git or tools on
PATH. The PR and canonical handoff record actual release and hosted outcomes.
Exact-source pins establish provenance, not scientific acceptance.

No historical full suite, selected cold replay, Lean or Docker was run.
The certificate paths share the quaternion definitions and source response;
there is no independent human or formal-kernel acceptance. No source patch,
coefficient monkey patch or physical caller workaround is used.
