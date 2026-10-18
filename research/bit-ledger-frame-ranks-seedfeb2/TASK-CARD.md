# TASK CARD — agent-39

Task ID / proposed scope key: bit-ledger-frame-ranks-seedfeb2 (drawer card: coverage-law-change,
track recursive-interfaces, chooser OS nonce feb25c49413fb33710658d2618c9ea58; scope refined)

Base commit; exact predecessor and dependency heads:
- Base: e112d71c8d7bb32435debcc54df932593dd8223a (origin/main at session start).
- Predecessor artifact: research/selected-suppliers-de-diagnostic/ (TASK.json open question 2,
  "Ledger reconstruction for the bit supplier"), predecessor author Navinor with help from opencode.
- Pinned source: research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz,
  content_sha256 5642fd0e35a1acc11acff8d0c08350c1617e95f310d4d35ad63a651f9eeeba0b,
  file_sha256 e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f;
  tune/EXPECTED.json (word.local_histogram, word.legality, nine.profile).

Concrete object and question:
Rebuild, code-disjoint, the paid-rank accounting of the pinned PR589/PR555-lineage bit word
directly from its gate operations (A/B/C/D lists, label frames, per-register start/final frame
ids) and check it against the recorded aggregates: word.legality.rank_mass = 5129 = 8R + 63 + 14v,
word.local_histogram, and (if reachable) nine.profile. This is the first step of the open
question above: "compute the per-frame transition ranks of the word file and compare against
word.local_histogram and nine.profile".

Scope status: refined (a narrowing of the drawn coverage-law-change card).
Reason: the drawn card's headline objects (plane-port coverage law, two-unpaid-coordinate
templates) are saturated with fresh claims and PRs (threads 1516/1587, PR1825/PR1808/PR1900);
agent-37 just closed connector-alphabet-change (PR2056). This object is the unclaimed
precondition the repository itself names for the bit-side coverage law (mass = 63W + 63N,
deficit = W - 63N), which ctoth's thread-1587 finding explicitly leaves "inferred" because the
hosted bit template is not in the tree.

Existing restriction being changed (or exact claim being audited):
Audited claim: EXPECTED.json aggregates (rank_mass = 8R + 63 + 14v = 5129; local_histogram with
sum of r*n_r = 5129; nine.profile with rank_mass 1808352 = 64W - 10272) hold as a from-operations
fact of the pinned word, not only as outputs of the supplier's own checker chain
(stage_cohort.py + legality_h.cpp + global_k.py).

Method; explicit parameter ranges/candidate alphabet:
Standard-library Python only. Exact F2/integer linear algebra. Parse the pinned gz word; compute
per-register frame transitions from start/final frame ids and the label-frame menu (rank over F2
of label vectors), decompose paid mass per register class (ports vs helpers vs retained totals),
and compare every derived aggregate to EXPECTED.json. No import of the supplier's checkers.

Nearest overlapping PRs and why this adds something:
- research/selected-suppliers-de-diagnostic (merged): prices the aggregates but takes
  nine.profile and local_histogram from EXPECTED.json; names this reconstruction as open.
- ctoth's thread-1587 FINDING: derives the bit coverage identity but marks the bit template step
  "inferred".
No open PR or fresh claim (last 4 hours, discussions 1166/1167/1317/1516/1587) works on a
from-operations rebuild of the bit ledger.

Optimistic full cost budget; required observable improvement:
This is an audit, not a construction: no moment change. Budget: exact recomputation reproduces
(contradicts nothing) the recorded aggregates, or isolates the first field that does not follow
from the gate operations.

Success evidence; falsification test; time/compute cap:
Success: verify.py prints PASS with per-aggregate equality to EXPECTED.json plus semantic failure
controls (mutated word must fail). Falsification: any aggregate mismatch is reported exactly.
Cap: 30 minutes of computation; the emitter-level event-stream rebuild
(COHORT249-RECORDS.bin via stage_cohort.py + legality_h.cpp + C++/Boost) is out of budget and is
recorded as the exact obstruction if the word-level accounting cannot close.

Predecessor authors; intended artifact and reproduction command:
Predecessors: Navinor (selected-suppliers-de-diagnostic open question), DreamingOfClouds
([PR 589](https://github.com/CrocSwap/integer-mult-bounds/pull/589)) on eumemic
([PR 555](https://github.com/CrocSwap/integer-mult-bounds/pull/555)) and their credited
predecessors (the bit word and checkers), Douglas Colkitt (pricing model). Artifact:
research/bit-ledger-frame-ranks-seedfeb2/ with verify.py and README. Reproduce:
PYTHONUTF8=1 python3 -B research/bit-ledger-frame-ranks-seedfeb2/verify.py

Attribution: Aaron Wang, with help from opencode.
