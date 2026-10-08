# Merged endpoints with deferred storage

The selected finite conditional certificate gives

\[
\kappa=\frac{28149877760063}{500000000000000000}
      =5.6299755520126\times10^{-5}.
\]

It combines a freshly regenerated PR91 h23 circuit, the frozen deferred-span
h25 circuit, PR93/94 final coordinate changes, and PR96 merged auxiliary
endpoints. The dimensions remain 23 and 25, with 26,387 and 34,749 auxiliary
roles. Width is 130,377,179 and rank deficit is 1,846,900. The complete paid
child list and exact rational inequalities are in `certificate.json`.

## Reproduce

```sh
python3 research/merged-span-frames/verify.py
```

This regenerates both parent circuits, performs the final coordinate actions,
replays every ordinary and arbitrary dirty basis vector in both orientations,
rebuilds literal transitions, recomputes all exact local and merged profiles,
and runs independent endpoint, corner-rank, ledger and arithmetic checks.
Temporary construction files live outside the repository. Ordinary
verification compares every frozen source and result without changing them.
`--record` changes only `verification.log` and the timing receipt
`validation.json`. `--workers N` controls each endpoint-profile worker pool.

`retirement/` preserves the diagnostic that merges only final cleanup
segments. Its exact conditional value is 5.3955378607315×10⁻⁵.

## Contributions and scope

- **Chafik Boukhalfa**, with OpenAI Codex assistance: PR91 composition and
  its smaller h23 circuit, pinned at
  `264f202b52edc04d0c72ca9cb3138282ca68b9ad`.
- **Thomas DiFiore**, with OpenAI Codex assistance: the inherited aligned
  partition construction, protected deferred storage, and this composition.
- **Rohan Arun**, with OpenAI Codex assistance: PR93's h23 5/6 and h25 22/23
  final label swaps, pinned at `c42039369af319a4ccc249b11efcfedecc2cc72f`.
- **Maxime Fleury**, with Codebuff assistance: PR94's additional h25 5/6
  swap, pinned at `0c440e40c9d4a5a02ca5bd028a2ebb5ebbca55d7`.
- **eumemic**, with Anthropic Claude assistance: PR96 merged exteriors and
  exact complementary-projector corner ranks, pinned at
  `606d16d6dfc714d2a467190dc91b2f8dcab38d9c`.

The original PR91/96 Git blobs, licenses and notices are preserved under
`references/frame-compiler/pr91` and `pr96`. Inherited credit includes
eumemic, Rohan Garg, Avi Eisenberg, Dominik Scholz, Rohan Arun,
Alejandro Zarzuelo Urdiales, Chafik Boukhalfa, Thomas DiFiore, jamesyc's PR34
fixed basis, PR29's two-stage endpoint construction, and all contributors
named in those notices. Apache-2.0 continues to apply.

The endpoint proof uses actual multiplicative partial-swap operators, as
spelled out in `endpoint-proof.md`. The new exponent remains conditional on
the inherited analytic, all-size residual-compiler, recursion, routing,
prime-selection, recovery and fixed-tape hypotheses. This is a finite
certificate, not a practical multiplication implementation or a proof of
global optimality.
