# Validation record

Environment: CPython 3.12.16, macOS arm64, standard library only.
Base: `e54523517d0f03e58352e647c403a5af3e525a57`.

This command passed in normal and optimized isolated modes:

```sh
python3 -B scripts/research_package.py --package research/edge-matching-even-attainment
```

Both direct runs printed `PASS_EDGE_MATCHING_EVEN_ATTAINMENT`.
The registered marker was `PASS_REGISTERED_RESEARCH_PACKAGE` with
`outcome=completed`. AST parsing and `tabnanny` also passed.

The complete finite domains are:

- All 24 constructed families at `0<=t,r<=4`, t+r>0. All 42,256 nonzero
  patterns are lifted. Each complete pool, rank, matching number, Gram
  rank and connected projector action is checked. All-vector orbit
  closure also runs for n<=9. The largest fixture has k=14 and n=22.
- All 21,284 nonzero raw factor pairs in the four fixtures of width at
  most seven. Their pools equal the pattern-lift pools. Both methods also
  check all 49 raw pairs at the exceptional width-three witness.
- All 36 ordered pairs and 216 ordered triples of the six rank-one
  idempotents on F2^2. All pairs and the 168 triples with idempotent sum
  have a checked common invariant line. A separate orbit method rejects
  irreducibility when the joint image has dimension two.
- All 126 choices of one lift per edge for k=nu from one through six,
  and each corresponding complete disjoint-edge pool.

Four wrong-parity fixtures reject both new links as non-idempotent.
Four singular-pairing fixtures retain idempotence and connected action
but have a checked nonzero common kernel. These test why connectivity
alone cannot establish irreducibility. All checks raise exceptions and
remain active under `-O`.

The five-member pool of PR #7094 is a separate source comparison. Its
15 nonzero patterns, all 961 raw factor pairs at width five, full image,
and every nonzero-vector orbit are checked. Its attained instance is
prior work and is not counted as a new result.

The upper bound is imported from the pinned matching proof. The written
construction, complete-pool argument, small exception and zero-difference
argument cover every finite ambient width. Finite checks corroborate them;
they do not enumerate all embeddings or all maximizing alphabets.

The selected binding-only check passed. No complete predecessor suite,
selected cold replay, native or physical replay, Lean, Docker, independent
human review or proof-kernel check was run. No paid word, supplier admission,
complete multiplication theorem or new kappa is claimed. All five selected
assumptions remain.

Commit-byte, source-history, export, sealed replay and publication checks
are recorded separately in the PR description. Hosted CI is reported
separately and does not replace the local scientific evidence.
