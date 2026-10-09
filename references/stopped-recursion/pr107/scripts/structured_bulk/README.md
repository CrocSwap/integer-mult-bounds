# Selected structured-bulk producer changes

Copyright 2026 icekylinx, Apache-2.0. Adapted with OpenAI GPT-6 Astra and
Codex assistance from the supplied round-three handoff. The retained pair
and triple modules preserve earlier contributor credits in `NOTICE` and
`SOURCES.json`. The surrounding translated-endpoint and semantic-bulk
interfaces retain their separate public PR #21 and PR #23 attribution;
these finite producers do not reimplement those interfaces.

Run from the repository root:

```sh
python3 scripts/structured_bulk_producer.py --output /tmp/structured-bulk-producers.json
```

The incremental command performs only the new selected work:

- Reuse saved h32 and h30 scalar counts from the previous endpoint-gauge
  certificate. No old positive producer is regenerated or rechecked.
- Regenerate and validate the new ordinary-base h36 bit DAG, and run its
  **original-envelope** carrier matcher. No positive enlargement is used.
- Regenerate the h30 DAG only to feed the new fixed-basis profiler. That
  program reconstructs original-envelope matching, then the full physical
  transition multiset, before extracting all contiguous pivot blocks in
  the rational basis `I+J`. Its result replaces the entire old h30 histogram
  conversion; the old positive histogram is not an input to these profiles.
- Regenerate mixed-center complex producers `(h,d)=(30,19),(40,35)`, including
  exact source supports, doubled-center coefficients, dyadic scatter
  identities, nondegenerate nested binary frames and output orthogonality.
  Run the unchanged deterministic complex matcher once for each distinct
  producer; the repeated h30 tensor factor reuses its result.
- Compare complete selected counts, histograms and block multiplicities,
  and verify exact bounded-minor arithmetic and deterministic primality for
  the CRT profile certificate.

Python assertions must remain enabled. The supplied profiler requires a
GCC/Clang C++17 compiler supporting `unsigned __int128` (`__uint128_t`). Its
modular arithmetic is retained from the handoff. All serialized integer
arrays use the shared little-endian readers/writers; no archived binary or
external checkout is needed. `--work-dir PATH` retains intermediates;
otherwise a temporary directory is cleaned on completion. Profiling stores
about 584 MB of modular frame matrices plus the DAG and normally dominates
runtime. No timing claim is made without running the selected verification.

The exactness argument uses the supplied rational frame formulas and three
proved correction-rank/numerator bounds. `exactness.py` recomputes their
bounded-minor sums, verifies the strict prime-product bounds and denominator
invertibility, and proves the three Mersenne primes by Lucas–Lehmer. The
profiler obtains the rational northeast-corner ranks from modular ranks and
emits its frame, matrix and CRT case counts. Rank-at-most-two transitions
are deliberately left as singleton calls.

The CLI defaults to `certificates/structured-bulk-bit-axes.json`,
`structured-bulk-rankone-profiles.json`, `structured-bulk-rankone-exactness.json`
and `structured-bulk-complex-input.json`, with the earlier
`endpoint-gauge-bit-axes.json` used only for the unchanged scalar provenance.
These finite checks do not constitute formal verification of the full
multiplication machine.
