# A stronger conditional integer multiplication witness

\[
\boxed{\kappa=\frac{1026571615319}{20000000000000000}
=0.00005132858076595},\qquad
T(n)=O\!\left(n(\log n)^{1-\kappa}\right).
\]

This is **0.5898983% above pinned PR #63** and **0.5776964% above PR #67**,
the highest claim in the site snapshot fetched at 2026-10-08 18:48:39 UTC.
The construction saves **994,796 physical wires**. These percentages compare
asymptotic exponent savings, not measured multiplication speed.

| Quantity | Pinned PR #63 | This construction |
| --- | ---: | ---: |
| h=23 scratch roles | 27,918 | 27,698 |
| h=25 scratch roles | 36,586 | 36,310 |
| Physical width | 137,151,806 | 136,157,010 |
| Conditional kappa | 0.00005102757 | 0.00005132858076595 |

The improvement combines a different legal ordering of scalar nodes,
selection of explicitly paid clearing operations, and coordinate relabeling.
Every selected operation, copied center, data block and endpoint correction
is charged in the complete recursive profile.

The original OpenAI framework and the inherited general analytic, all-size
compiler, fixed-tape, precision, routing, prime-selection and recovery
hypotheses remain assumed. This is a verified finite conditional witness;
it is not an unconditional theorem or full formal verification.

## Evidence

- [Proof and dependency argument](PROOF.md)
- [Exact rational certificate](certificate.json)
- [Selected construction parameters](selection.json)
- [Immutable source pins](SOURCE.json)
- [Independent arithmetic audit](independent-audit.json)
- [Independent dense scalar-graph audit](graph-audit.json)
- [Full verification receipt](validation.json)
- [Full verification log](verification.log)
- [Current-upstream integration receipt](integration-validation.json)
- [Current-upstream integration log](integration-verification.log)
- [Dated leaderboard comparison](benchmark.json)

On the recorded PR #63-based source state, full `make verify` passed: **467 broad tests, 92 focused test executions and
20 historical patch checks**, plus fresh construction producers, both
complete dirty-basis orientations, all paid fixed-basis profiles with zero
CRT disagreements, 47 strict assembly inequalities and seven margins.
The adjacent bit-saving and kappa grid points are rejected. The independent
arithmetic checker also rejects three deliberately corrupted fixtures.
No inherited generated certificate or patch changed.

After merging upstream main at `56b66d58297deca1d7dd130247d720e960f77a37`,
a fresh `make ordered-frames-verify`, parameter-refinement check and six
inherited rank-pair regression tests passed in 131 seconds at `dfc3681`.
All source pins still match and regeneration changed no tracked artifact.
The complete integrated upstream suite and formal packages are separate
GitHub CI checks; the historical full-suite receipt does not cover them.

## Reproduce

Use Python 3.11 or newer and a C++17 compiler with unsigned 128-bit support.
From the repository root:

```sh
make ordered-frames-verify
```

This freshly rebuilds both words, checks the dense scalar graph, independently
replays the serialized words, regenerates every paid profile and verifies
both arithmetic certificates. The full inherited suite is:

```sh
make verify
```

The original parameter-only refinement is retained separately in
`research/rank-pair-refinement/`. This stronger construction uses its exact
logarithm/exponential enclosure helper, while changing the finite network.

## Credits

Prepared with substantial OpenAI Codex assistance for Thomas DiFiore.
The construction builds on Dominik Scholz (#63), Chafik Boukhalfa (#60),
Avi Eisenberg (#62), eumemic (#57), Alejandro Zarzuelo Urdiales (#61), and
the complete community dependency chain credited in [the proof](PROOF.md).
Concurrent schedule and slot-selection contributions in PR #65 and #67 are
acknowledged. No priority or global-optimality claim is made. All inherited
licenses and author notices remain in force.
