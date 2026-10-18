# Verification record

Base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
Selected source head: `0fc329d0bec93ca7cd288eaea1295172e8789810`.
Local verification date: 2026-10-14 UTC.

The registered package replay passed with CPython 3.12.13 on macOS arm64:

```sh
python3.12 -B scripts/research_package.py --package research/p112-linear-endpoint-lifts
```

It ended with
`PASS_REGISTERED_RESEARCH_PACKAGE research/p112-linear-endpoint-lifts outcome=negative-result`.
The metadata-only command also passed. It authenticates the ten source files
against their exact base Git blobs and SHA256 values.

The direct replay also passed with CPython 3.14, with optimization enabled:

```sh
python3 -O -B research/p112-linear-endpoint-lifts/verify.py
```

The recomputed result equals RESULT.json after JSON parsing. No check uses an
`assert` statement. A separate deliberate all-zero archive SHA256 pin was
rejected by the source reader before archive parsing.

## Decisive coverage

- The selected 112 norm-one ports and all 12,544 binary pairings.
- Eighty independent graph-edge tensor rows; the identity form is their sole
  bilinear null direction in dimension 81.
- Eight clique anchors and 24 edge vertices; all witness incidences and
  nonincidences, including the missing perfect matching.
- Both selected local emitted programs: 3,494 native transitions each,
  with exact frame-distance equality. All eight copied-centre paths are included.
- The selected global program and 144 complete calls, 704 distinct live owners
  per call, each replica's event sequence, and the final live-family range.
- All 7,526 literal idle children and their independent orthogonal axes.
- The full 510,662-child histogram and rank mass 1,041,408.
- Rational series bounds for both complex root endpoints and the exact outer
  necessary inequality that excludes the next selected kappa grid point.

Five input mutations are rejected: a nonedge in the tensor basis, a missing
basis row, an aliased graph witness, a rank-seven charge for a rank-eight
centre, and an overcharged reference edge. Small exact controls cover 4,489
subspace pairs and 5,265 symmetric rank-one updates with an update vector
outside the old image. Three tensor-fibre forms give the dimension-18 positive
control, including alternating and nondiagonal forms. A common isotropic
plane in dimension four shows that dropping endpoint nondegeneracy invalidates
the dimension theorem.

These finite checks do not prove the universal statements by exhaustion.
PROOF.md gives those statements and their proofs. In particular the arbitrary
plane bound and the linear-lift cost bound have different scopes.

## Independent review and overlap

A separate Codex coordinator recomputed the edge-tensor rank from the selected
source-bound PROTOTYPE model without this package's code. It obtained rank 80
and the identity null form. It also found an independent 8-anchor/24-edge
witness and checked the dimension-17 contradiction. The coordinator reviewed
the cost proof. Its review led to two improvements: bind every old charge to
minimum Fourier rank, and telescope padding only on persistent live paths.
No independent human review is claimed.

A live GitHub metadata refresh during final verification reached PR1401.
The exact phrase search also checked linear lifts, two-plane labels, endpoint
dimension and bilinear rigidity. Relevant related heads are in SOURCES.json.
PR791's full note was read at its pinned head. Its rational-idempotent warning
is respected. PR1262's emitted ledger and PR1387's idle-axis counterexample
are credited; neither is presented as a new result here. PR1325 is about a
scalar decoder normal. PR1014 is about a different parity DAG. No overlapping
P112 plane-dimension or coupled-linear-lift theorem was found in these bounded
searches. This is not an exhaustive novelty claim.

## Checks outside this result

No selected supplier cold replay, complete native compiler replay, proof
assistant, hosted Linux CI or repository-wide test suite was run. The source
pins authenticate inherited evidence; they do not rerun it. The exact scalar
map, phases, owner-chart validity, precision/tape, analytic transfer and bit
H1--H5 obligations remain those of the selected review.

Only this research package is changed. The selected certificate and upstream/
are unchanged. The independent dimension theorem leaves nonlinear labels in
dimension 18 open. The cost theorem excludes new scalar words, new controllers,
and joint multi-array children across retained edges.
