# Separate mathematical review and complete replay

**Accepted within the stated finite domain.** The complete primary and
separate censuses agree, and the reductions in [PROOF.md](PROOF.md) cover the
remaining operation choices. No improving or unresolved case remains for
at most two legal transports of the frozen PR589 word under the fixed
636-frame catalogue plus each slot's own lower-span closure.

This review and the separate checker were prepared by a GPT-6 Astra agent
at xhigh for Brian Ross, with substantial AI assistance. This is not
independent human peer review or a formal verification of multiplication.
The earlier package at `ce0b65fd` remains unchanged. All work was local.

## Mathematical findings

- **Register-disjoint movers reduce to singles.** Removing the first mover
  preserves the second mover's register itineraries, commuting barriers,
  section boundaries, lower closure and COPY conditions. Its projected slot
  lifts to a legal baseline single or identity. The affected register sets
  are disjoint, so their surcharge-inclusive J values add at the same
  reference root. Complete single non-improvement therefore excludes them.
- **Repeated choice of one occurrence reduces to singles.** Removing that
  occurrence leaves the same background. Neither move crosses a fixed
  noncommuting blocker. Its final slot/frame has the baseline single's
  eligibility, including COPY and the slot's local closure. This depends on
  the fixed catalogue, not an accumulated pool of previously created frames.
- **Pair-specific projection preserves reachable final profiles.** For fixed
  distinct overlapping movers x,y, retain in both sections every operation
  touching `supp(x) union supp(y)`. Every erased operation commutes with both
  movers and affects no relevant frame. Each projected move lifts through a
  corresponding full-word gap; the second lift is taken after the first.
  Identity moves explicitly cover erased-only crossings. Profiles are replayed
  only on the relevant registers, never on an incomplete global background.
- **Only final-step frame/touch caching is used.** First states retain their
  pair-specific literal positions. Identical first prices, profiles, or
  own-register touch signatures do not justify merging continuations.
- **Root existence is uniform.** Climb dimensions telescope, COPY dimensions
  stay pinned, and global rank mass remains 1,808,352. With `N <= M`,
  `F(0) = -10272 + lambda*N < 0`; the positive surcharge makes F strictly
  increasing and unbounded. The comparison at the rigorously bracketed
  reference root is therefore valid throughout the transport class.

The ordered-occurrence partition was checked:
`3064^2 = 3064 + 9325034 + 59998`. These are repeated, register-disjoint,
and distinct overlapping choices, respectively. Of the last group, 13,054
cross sections. These counts are not literal-path or distinct-word counts.

## Completed evidence

[independent-comparison.json](independent-comparison.json) binds all four
complete receipts by SHA256 and records the cross-check results.

| Complete check | Agreed result |
| --- | ---: |
| Single-operation domain records | 3,064 |
| Literal single moves | 1,452,893 |
| Single profile-delta classes | 22 |
| Distinct overlapping ordered pairs | 59,998 |
| Pair-projected first states, including identities | 327,963 |
| Priced final frame/touch representatives | 1,379,084 |
| Pair profile-delta classes | 93 |
| Exact profile ties among pair representatives | 1,282,055 |
| Strictly worse pair representatives | 97,029 |
| Better or unresolved representatives | 0 |

All 3,064 single-operation domain digests match between
[primary-singles.json](primary-singles.json) and
[independent-singles.json](independent-singles.json). Every single delta,
occurrence count and status matches. Every independently computed rational
price interval lies inside the corresponding primary interval.

The complete pair receipts are
[complete-pairs.json](complete-pairs.json) and
[independent-complete-pairs.json](independent-complete-pairs.json).
Their complete canonical candidate transcript hashes are identical:

```text
b39d6d23210ab7eee24c04e165b078e39ea00053e4be4b523f7c793e24b79679
```

All aggregate counts, all 93 delta frequencies and statuses also match;
every independent price interval is enclosed by its primary counterpart.
Both witness lists requiring further examination are empty.

The primary complete pair run took **372.174 seconds**, including setup.
The independent run took **125.896 seconds**. The commands were:

```sh
python3 research/pr1048-complete-feasibility/pairs.py --full --time-budget 900 --output research/pr1048-complete-feasibility/complete-pairs.json
python3 -I -O -B research/pr1048-complete-feasibility/independent_pairs.py --full --time-budget 1200 --output research/pr1048-complete-feasibility/independent-complete-pairs.json
```

Both exited successfully with `complete_domain: true`, `status: COMPLETE`.
The separate comparison reported
`PASS_COMPLETE_SINGLE_AND_TWO_TRANSPORT_CROSS_CHECK`.

## Independent implementation and controls

`independent_pairs.py` imports the frozen separate integer-geometry/rational-
series checker. It does not import the primary pair driver or primary pricing
and enumeration engines. The canonical transcript format is shared as an
external comparison format. The enclosing arithmetic remains separately
implemented, with no floating-point acceptance decisions.

The compact `Projection` adapter restricts current-frame cells, D touches and
final climbs to the pair's two or three relevant registers. Its event order,
COPY snapshot and reconstructed full-frame C touches were reviewed against
the unoptimized replay. The 128-pair compact and unoptimized pilots have
identical candidate transcripts and totals. The 1,024-pair pilots additionally
have identical complete delta/price records; their shared transcript hash is
`5e50a1e0013065cf6423912a06a71e7533aac7f9954dc28067e629427fa71035`.
This removes irrelevant replay work without shrinking the move domain.

Exact integer basis reduction checks that all **636 original masks equal
their rational span closures** within the source line set. Thus the mask
containment tests represent the claimed subspace containments.

A small explicitly synthetic control has all baseline single deltas equal
to zero. Two first placements share the same frame and own-touch signature,
but only the later placement admits delta `{1:-1, 2:-1, 3:1}`. Its price is
strictly negative because `3^(1-c) < 1 + 2^(1-c)` for `0<c<1`, with an
additional negative surcharge difference. The independent replay detects the
improvement and rejects the unsafe first-touch quotient. This is a control
of the reduction logic, not an improvement to the frozen supplier.

Reviewed current-source SHA256 values, rechecked against the completed receipts:

```text
singles.py
9b2ef8aa45278947961a518643d5dbf69df5d9892dcecc114c0ef34b6dee48d1
pairs.py
50dbba217e7875724367240479044ec107853db93ac43f0ae9a2027bd155adbe
independent_pairs.py
a1b5332fa9f8f31e9163f0cafdea4294cc57315d8ee2ebbb50011a3534097ac0
frozen independent.py
e04e7364a4aa53f00d21271c71d33063a7fa27946bde1272dddd9c794177c1ea
```

No remaining blocker was found for this finite two-transport exclusion.
Longer paths, growing catalogues, arbitrary new subspaces, noncommuting or
Steinberg rewrites, supplier/native admission and the all-size multiplication
theorem remain outside the claim. Source, supplier, predecessor and Brian
Ross/Krenn/ThetaTwist methodological attribution is preserved in PROOF.md and
the unchanged predecessor notices.
