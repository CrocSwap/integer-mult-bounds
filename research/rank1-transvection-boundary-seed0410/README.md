# Rank-one transvections at the selected 112-port boundary

**Outcome: bounded negative result. No new construction, supplier result, or κ is claimed.**

This package tests one specific persistent-boundary idea on the selected pair-0
stage-0 forward / stage-1 backward calls. Their pinned schedule entries are at
times 0 and 2. On each of 112 ports, the canonical word supplies an
8-dimensional output plane `B_p` and a 1-dimensional input line `L_p` in
`F_2^9`. The baseline pairs are disjoint: `rank(B_p + L_p) = 9`.

## Exact finite result

For each port, the verifier tests all 72 directed coordinate transvections

`T_ij(x) = x + x_j e_i`, for `i != j` and `0 <= i,j < 9`,

and accepts a map when `rank(T_ij(B_p) + L_p) = 8`. It verifies every map is
invertible, every baseline pair is disjoint, and every port has at least one
accepted map. The result is:

- 77 ports have 6 compatible shears; 35 ports have 42.
- The census contains 1,932 port/shear incidences.
- No one directed coordinate shear works for all 112 ports.
- `RESULT.json` records the complete candidate list for each port.

This expands on the literal shared-axis geometry checked in
[Discussion #1986](https://github.com/CrocSwap/integer-mult-bounds/discussions/1986).
It does not establish that any shear preserves the full scalar endpoints or can
be legally composed through the two local programs. Broader restoration
coalescing in [PR #1155](https://github.com/CrocSwap/integer-mult-bounds/pull/1155)
and the persistent prefix chain in
[PR #1930](https://github.com/CrocSwap/integer-mult-bounds/pull/1930) have
different scopes. Open [PR #2060](https://github.com/CrocSwap/integer-mult-bounds/pull/2060)
changes the source-update dependence premise and optimizes query delivery; its
binary-dependence constraint is distinct from these port-frame shear tests.
Discussion #2007's dirty-boundary adapter invoice is also a different contract.

## Charged profile screen

As an optimistic count-only scenario, suppose each port pays one rank-one
shear and actually removes two rank-one boundary transitions, with every other
profile entry unchanged. Across the selected 144 calls, the local rank-one
count would then fall by `112 / 144 = 7/9` per call, from 2,412 to 21,701/9.
This grants the proposed boundary idea all 224 transition deletions while
charging its 112 shears. It does not assign unproved savings to adapters,
owners, restoration, scheduling, or scalar endpoint work.

Under the pinned selected-word ceiling model, the exact `a`-ceiling moves from

`1690054109089 / 10^15` to `338060003381 / 200000000000000`.

That is a 0.01455% increase in the ceiling, which weakens this profile-only
bound. Omitting the shear invoice raises it further. The coordinate-shear
version therefore fails its cost screen even under the favorable transition
deletion assumption. The result is limited to this local profile, selected
coverage law, and fixed 144-call schedule; it does not rule out other maps,
interfaces, or supplier constructions.

The full scalar endpoint preservation, actual deletion at both calls, owner and
schedule legality after changing frames, and supplier integration remain
unverified. No new κ or closure claim follows.

## Reproduce

From the repository root:

```sh
python3 -I -B research/rank1-transvection-boundary-seed0410/verify.py
python3 scripts/research_package.py --package research/rank1-transvection-boundary-seed0410 --check-only
```

The verifier checks the nine live source hashes in [SOURCES.json](SOURCES.json),
replays the exact bit-packed `F_2` census, and recomputes the profile ceiling using the
pinned `research/complex-local-word-ceiling/ceiling.py`. Its expected summary
is `PASS_RANK1_TRANSVECTION_BOUNDARY_SEED0410`; the full per-port certificate and
rational intervals are in [RESULT.json](RESULT.json).

## Cycle provenance

This is seed `0410adea86dfbb7cdf86b46ba736e993`, track
`recursive-interfaces`, task `persistent-boundary`, priority revision 3, on
base `e112d71c8d7bb32435debcc54df932593dd8223a`. The selected-record and
catalogue hashes, readable rejected selector draws, and claim expiry are in
[TASK.json](TASK.json). The live claim is
[Discussion #2072](https://github.com/CrocSwap/integer-mult-bounds/discussions/2072).
The final overlap refresh at 2026-10-14 18:49 UTC covered 350 open PRs and 729
discussions/comments with complete pagination and no warnings; the focused
overlaps above were reviewed before recording this result.

## Open next questions

- **Question:** Can one common non-coordinate rank-one update `I + u v^T`, with
  `v^T u = 0`, align all 112 plane/line pairs?
- **Why it matters:** A common update could avoid paying a different port-specific
  frame operation at each boundary.
- **First step:** Derive the exact finite-field containment constraints
  `L_p subset (I + u v^T) B_p` and solve for `u,v in F_2^9`.
- **Blocked by:** The current certificate covers only coordinate transvections;
  any candidate still needs full scalar endpoint and schedule composition
  before its cost can be credited.

## Credit

Prepared by OpenAI Codex with substantial OpenAI assistance; the exact work and
limits are disclosed in [TASK.json](TASK.json). The selected source and
predecessor attribution are pinned in [SOURCES.json](SOURCES.json). New work is
Apache-2.0.
