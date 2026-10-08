# Sharper bit moment on the deferred/signed round-seven basis

This is an **additive analytic refinement of PR #97**, not a new multiplication
network. It requires CrocSwap PR #97 at
`f5f9c56e637463cac1e300d1589ccf42838f688a`. The unchanged physical bit
histogram is `(m,W,s)=(529,108516254,57403754177)`; the unchanged complex
saving is `36926111/500000000000`. The same semantic bridge, `C1=1`,
`eta=1/10^8`, `beta=1/10`, and the `10^-12` final grid are used.

The exact exponential moment accepts
`a=63983013240044/10^18` and rejects the adjacent `10^-18` point. Both
directions are proved by two independently implemented rational enclosures.
Replacing only the bit saving in PR #97's balanced assembly gives

`kappa=63974824/10^12 = 6.3974824e-5`,

versus PR #97's `63965813/10^12`. This is a gain of `9011/10^12` in
**conditional** `kappa`. All 47 strict assembly constraints and seven
cost margins pass. The next `10^-12` grid point fails the binding compact
phase-layer margin.

Run from repository root:

```sh
python3 research/round7-moment-followup/check_sources.py
python3 research/round7-moment-followup/verify.py
python3 research/round7-moment-followup/independent_moment.py \
  --case accepted=exp:accept:63983013240044/1000000000000000000 \
  --case adjacent=exp:reject:63983013240045/1000000000000000000 \
  --output /tmp/croc-round7-moment-independent.json
make deferred-signed-verify
```

`verify.py --output NEW_PATH` writes a full exact assembly receipt, refusing
to overwrite an existing file. The committed `certificate.json` is one such
receipt. The independent checker can likewise write a separate receipt.
Assertions must be enabled. No float decides a bound.

This result inherits PR #97's physical word argument and the repository's
analytic/fixed-tape interfaces; the finite certificates do **not** formalize
the full integer-multiplication theorem. The bit histogram originates with
Swapnil Jain's pinned round-seven construction. Zhihao Chen's PR #97 supplies
the deferred/signed endpoint and assembly integration. The sharper moment
enclosure was first developed in SovereignSteak's companion PR #2; this
package ports its analytic improvement to CrocSwap's distinct assembly.
The work was prepared with OpenAI Codex assistance. All original author,
license, and AI disclosures remain in `research/deferred-signed/`.

No repository-wide best-known claim is made. Review and merger of PR #97 are
separate from review of this overlay.

The stacked patch also removes four PR #97 `SOURCE.json` entries for prior
`*.log` files absent from its Git tree (and ignored by `.gitignore`).
No committed source pin is relaxed; this permits its original
`make deferred-signed-verify` regression to run.
