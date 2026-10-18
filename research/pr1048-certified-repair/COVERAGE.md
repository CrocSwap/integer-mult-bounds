# Bounded transport coverage

`coverage.py` reconstructs a finite transport domain independently of the
PR1048 enumerator and the PR589 nomination heuristic. The legacy implementations
are imported only by an observational comparison adapter. The supplier word,
its frames, and the inherited pipeline contracts remain inputs, not new proofs
of the multiplication theorem.

Run from the repository root:

```sh
python3 research/pr1048-certified-repair/coverage.py --output /tmp/COVERAGE.json
```

Compare the resulting JSON with `evidence/COVERAGE.json`, excluding the separate
`timing` field. The bounded run takes approximately 30 seconds on the review
machine. It does not run the historical 645,900-pair search.

## Declared domain

The first-operation identities are the original tuned-word indices A[2028],
A[2076], A[2129], A[281], and B[1]. For each, the reconstruction visits every
literal insertion slot reachable through commuting elementary ADDs. At each
slot it visits every permitted frame from the original 636-frame catalogue,
plus the rational span closure of the lower-frame requirement. This is not
enumeration of all subspaces or all future catalogue enlargements.

Nesting is checked by root-line set containment. The resulting last A frame of
each retained register must equal its initial COPY frame, including when the
transport removes that register's previous last touch. This restriction is
specific to A. Frame dimensions and lower-bound closures use independently
implemented rational elimination.

At most three first states are selected per operation: its earliest literal
move, its first original nomination in slot/frame order, and its first
alternative frame (or latest literal move). Duplicate selected states are
removed. This yields ten first states. For **each** selected state, every
operation sharing a register with the first operation is considered in **both**
sections, with every legal literal slot and frame in the stated frame domain.
The receipt retains stable identities, current indices, frame masks, candidate
digests, and the concrete selected states.

No first state is discarded because it has the same profile as another state.
Only exact integer profile values are cached within a fixed state's fixed
touch context. Disjoint second operations and Steinberg moves are outside this
bounded domain; no pruning theorem about them is asserted.

## Result

| Quantity | Count |
| --- | ---: |
| Legal first moves | 9,950 |
| Selected first states | 10 |
| Post-first second-operation rows | 150 |
| Legal second moves | 125,698 |
| Cross-section second moves | 9,424 |
| Distinct signed local profile deltas | 24 |
| Certified strictly better transitions | 0 |
| Exact profile ties | 56,685 |
| Certified strictly worse transitions | 78,963 |
| Unresolved transitions | 0 |

Counts of priced transitions combine the first and second domains; they count
paths and may include repeated profiles or algebraically equivalent words.
Every one of the 24 distinct deltas has a representative checked by full
integer-profile replay, in addition to the local register calculation. Every
selected first state is also checked by full replay. Pricing uses the certified
reference-root bracket and includes the inherited surcharge through
`pricing.ReferencePricer`, rather than a fixed-exponent float comparison.

## What the comparisons establish

The original `pair_search` takes its second view from the first move's section.
The receipt includes six concrete cross-section pairs whose individual moves
are original nominations but whose pairing is omitted by that loop. One is
A[281] to slot 280 at frame 127 followed by B[133] to slot 138 at frame 507.
That pair has the identical paid profile and identical certified root. The
omission is a coverage limitation, not an improving counterexample.

Two neutral first transports of B[1] at frame 217, to slots 0 and 367, have
different bounded reachable final-profile sets. The slot-0 state admits the
additional signed local delta `{1: 4, 2: -2}`; the slot-367 state does not in the
enumerated adjacent domain. The receipt supplies a concrete second move for
this difference. This additional delta is strictly worse than the baseline.
Three other compared equal-profile first-state pairs have different literal
candidate domains but identical reachable profile sets. These distinctions
prevent a stronger claim about objective improvements based solely on path
counts or candidate digests.

The chosen initial A[2028] and A[2076] domains include frame/touch classes not
nominated by the immediate heuristic. This does not show that the nominated
frame loses the immediate optimum, nor that an omitted frame yields an
improving continuation. The historical verifier's global-per-operation check
does not supply a proof of per-slot optimality or continuation dominance.
Some `original_all_legal_missing_frame_touch_classes` entries are literal
transports equivalent to the original itinerary, such as A[2076] to slot 2077
at unchanged frame 517; these are not presented as lost improvements.

No legacy `all_legal_moves` output was illegal in this actual bounded word
domain. Its two COPY-rule defects are instead demonstrated on explicitly
synthetic local fixtures: removing the last retained A touch can expose an
incorrect COPY frame, and applying the A-only COPY restriction to B can reject
a valid move. The tuned word has no B operations touching retained registers,
so the latter defect is not claimed to omit a move on this word.

The semantic controls mutate proof-relevant contracts: resulting COPY frame,
section eligibility, and reuse of continuation domains by profile equality.
They adapt the Brian Ross/Krenn falsification methodology to this finite
audit. They do not transfer credit for the supplier, the original mathematics,
or the maintainers' existing counterexamples. Supplier/tuner credit remains
with DreamingOfClouds and the cited predecessors, the original profile audit
with flemhhh, and the reference-bracket repair with woklerx. This contribution
was prepared by Brian Ross with substantial OpenAI Codex assistance.
