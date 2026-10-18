# Local task card (autoresearch.md section 3)

Task ID / proposed scope key: `connector-alphabet-change` / `ff4f5113ed2256ab19ed`
(draw: `scripts/choose_research_task.py`, seed `bf263697e6c72cee43b6ded62be24c62`,
track `recursive-interfaces`; OS-random draw, seed recorded only for reproduction)
Refined scope key (my actual object): `connector-duo-toggle-five-source` —
one new complete call type, five-source instance.

Base commit; exact predecessor and dependency heads:
- Base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f` (origin/main at session start).
- Predecessor: `research/universal-connector-boundary` (merged
  https://github.com/CrocSwap/integer-mult-bounds/pull/943, Ross
  Richardson), pinned in-tree; its frozen census and cost recurrence are the
  baseline. `research/universal-connector-boundary/CERTIFICATE.json` unchanged.
- Comparison heads (not dependencies): open
  https://github.com/CrocSwap/integer-mult-bounds/pull/1185 head
  `4a60772285ce70f6414458f6d3a54948652bbed0` (f(6)=16, unchanged alphabet);
  open https://github.com/CrocSwap/integer-mult-bounds/pull/1340 head
  `f1dcab36fa63f8226f70dd07e26f44afb9d39b51` and open
  https://github.com/CrocSwap/integer-mult-bounds/pull/1370 head
  `8a9b633879b5bfe03400a6c09c31bae7568e6261` (mutable-source shear
  mechanism, discussion 1352) — different mechanism and hypotheses.

Concrete object and question:
The five-source universal dirty-connector interface of
`research/universal-connector-boundary/README.md` ("Exact interface"). Add
exactly one new complete call type

    DUO_{j,k}: z += B_j x_j + B_k x_k      (j != k; one dispatch, sources read-only)

and ask: what is the exact Pareto frontier of (source-call count k, source
toggle-adds W) for a restored source word whose paired-readout difference set
D(w) is all 32 five-bit masks, in the alphabet {B_j} ∪ {DUO_{j,k}}? In
particular, is there a word with k <= 10 and W <= 12, i.e. strictly fewer root
queries than the frozen 74-query optimum at no extra adds?

Scope status: refined (same card, same connector object and boundary; the card
asks for "one additional operation and a small source count for its first
counterexample", I fix the operation to the two-source combined toggle and the
domains to 3 sources (tiny falsifying instance) then 5 sources (the frozen
74-query instance)). The five-source, all-31-row batch is the priced object.

Existing restriction being changed:
"No combined queries" (universal-connector-boundary README, Exact interface
list). Everything else is unchanged: complete calls only, arbitrary dirty rows,
restoration of z and all scratch, paired A_i readouts, no free copies, no
frame/role changes, generic admissible operators.

Method; explicit parameter ranges/candidate alphabet:
- Reduction: the prefix-difference characterization of
  `research/universal-connector-boundary/README.md` carries over verbatim to
  DUO steps (q_t = source parity vector; a DUO call adds one weight-2 vector),
  so generic schedules are exactly closed walks with steps of weight 1 or 2.
  Re-derive and state it; do not assume it.
- Finite census (exact, stdlib, no floats): (i) 3 sources, all closed walks
  k <= 6 — smallest falsifying instance first; (ii) 5 sources, enumerate
  difference-cover prefix sets P (9 <= |P| <= 10, 0 in P, P+P = F2^5) and all
  closed walks on them with k <= 10 and W <= 12; heuristic-only search beyond
  that scope, labelled as such.
- Correctness replay: dense F2 replay at L = 1,2,3 with generic noncommuting
  matrices, arbitrary dirty z/sources/scratch, forward and inverse; compare
  realized rows against the prefix-difference prediction; mutation controls.
- Pricing: charge DUO completely (two coefficient/source traversals, one
  target update cycle, one dispatch/entry-exit frame/head return); parametric
  break-even in per-call overhead o vs per-add price p against the frozen
  74-query/12-call schedule and its own README concrete dense-bit-matrix
  implementation macro counts.

Nearest overlapping PRs and why this adds something:
- https://github.com/CrocSwap/integer-mult-bounds/pull/943 (merged predecessor): fixed alphabet; its 945-pairing exclusion is for
  singleton toggle words only. My census is a different (extended) alphabet.
- https://github.com/CrocSwap/integer-mult-bounds/pull/1340 and
  https://github.com/CrocSwap/integer-mult-bounds/pull/1370 (discussion 1352):
  mutable-source shear path (sources temporarily writable, four source XORs,
  ten queries). My mechanism keeps every source read-only and changes the
  operation instead; the two are different hypotheses and are priced
  separately, theirs credited.
- https://github.com/CrocSwap/integer-mult-bounds/pull/1185: f(6)=16 in the
  unchanged alphabet; side comparison only.
- `find_overlap.py` queries 'two-source toggle', 'combined query', 'combined
  toggle', 'pair toggle', 'additive basis', 'difference cover', 'multi-toggle',
  'double toggle' (fresh remote snapshot 2026-10-14T00:11Z, complete
  pagination): 0 matches. No matches is not proof of novelty.

Optimistic full cost budget; required observable improvement:
Optimistic: a walk with (k, W) <= (10, 12) exists, giving 72 root queries at
74 adds vs the frozen 74 queries at 74 adds; strictly better completed cost for
any positive per-call overhead. Required observable: either such a witness with
exact replay, or an exact exclusion of the searched domain with the frontier
and the break-even region recorded. Target "favorable completed budget" is
k <= 10, W <= 12; if the frontier misses it, stop and record the obstruction
rather than lowering the target.

Success evidence; falsification test; time/compute cap:
Success = independent second implementation agreeing on the frontier/witness
records + dense dirty-state replay with failure controls + exact rational
pricing comparison. Falsification-first: 3-source instance decides whether the
mechanism can beat 2n = 6 singleton calls at all before the 5-source census.
Compute cap: minutes of stdlib Python, no network in the census.

Predecessor authors; intended artifact and reproduction command:
Ross Richardson (universal-connector-boundary,
https://github.com/CrocSwap/integer-mult-bounds/pull/943 /
https://github.com/CrocSwap/integer-mult-bounds/pull/934 lineage);
Arham Tahir (https://github.com/CrocSwap/integer-mult-bounds/pull/1340 /
https://github.com/CrocSwap/integer-mult-bounds/pull/1370 shear mechanism, discussion 1352) for the
comparison. Intended artifact: `research/duo-toggle-connector/` with
README.md, TASK.json, SOURCES.json, CERTIFICATE.json, EXPECTED.json,
generate.py, independent.py, verify.py; reproduction command
`python3 -B research/duo-toggle-connector/verify.py`.

Attribution: Navinor, with help from opencode. Apache-2.0.
