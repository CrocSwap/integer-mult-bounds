# Validation record

All commands below ran on Windows 11 with CPython 3.13 from the repository
root of branch `research/agent-10-bit-seed16`, base
`007664306fff84fbb1c9a1b4053b69f439764034`. Prepared with help from
opencode.

## Completed runs

1. Discovery run (scratch prototype) on frames 506/521/523: greedy
   min-excess reduction found 21/31/26 gates in minutes; plain uniform
   random trajectories found only 41 on frame 521 in 3,000 trials,
   reproducing the weakness of earlier bounded random searches. This was the
   evidence pivot from "another random search" to the deterministic
   three-phase search.
2. Ten-block search (`search.py`, one process per block): reproduced the
   scratch bests exactly and completed all 10,000 trajectories plus the
   beam phase on every block. Output: `PASS_R439_BSECTION_MULTWRITE_SEARCH
   frames=506,507,519,508,520,509,521,522,523,524 gates=388->262`.
   Every candidate's forward matrix was re-derived from its gate list and
   compared with the block map inside the search as well.
3. `verify.py --record-certificate`: `PASS_R439_BSECTION_MULTWRITE
   gates=388->262 ADDs=24305->24053 columns=661 controls=8 rank_mass=5129
   kappa=unchanged`. The report is pinned in `CERTIFICATE.json`:
   - forward positive bound 49,347 -> 26,653;
   - composed reverse positive bound 1,113,070 -> 776,006;
   - payload 93 -> 90 bits (cap 104);
   - records 27,234 -> 26,982; COPY/ERASE pairs 9/9 unchanged;
   - paid profile and rank mass 5,129 unchanged; 636 closed frames;
   - nine rank-seven copy totals retained.
4. `verify.py` again against the pinned certificate: same PASS line
   (certificate match). This is the reproduction command in README.md.
5. `search.py` regeneration reproduced `CANDIDATE.json` identically to the
   discovery run's candidates (same seeds, same phases, byte-for-byte gate
   lists).

## Mutation controls (all rejected)

`mutated_source`, `dropped_gate`, `illegal_frame`, `swapped_block`
(frame-520's program in frame 508's slice), `omitted_cleanup`,
`missing_gate_matching_cleanup`, `illegal_frame_word`, `stale_cleanup`.

The stale-cleanup control is deliberately informative: the original cleanup
still restores the **F2** endpoint after the splice (every shear is an F2
involution, so any cleanup inverse to the block's F2 map restores), and is
rejected only by the H4 literal-cleanup comparison. Endpoint checks alone
cannot detect a non-literal cleanup; the two checks are complementary.

## Development defects caught before the committed runs

1. The column-subtraction legality test was written with the comparison in
   the wrong direction (allowing column growth instead of column
   subtraction); caught by hand-checking a two-register case before any
   search run. No candidate was produced under the wrong rule.
2. The first draft of the splice replaced B slices in ascending order, which
   shifts later slice indices after a shrinking replacement; fixed to
   replace from the end of B backwards before the verification run.
3. The negative-control inventory check compared a sorted frame list with
   the unsorted B-order list and would have failed on a valid candidate;
   fixed before the run.

## Scope of the evidence

The finite checks cover the exact integer maps, the complete Boolean block
tables, the full-word F2 endpoint on all 661 dirty-input columns, the H1-H5
interface of the pinned checker, and the exporter's record bills and
positive/payload bounds. They do not run the C++ native legality or
5/9/11-stage checkers, do not rebuild hosted emission, precision invoices,
supplier bindings or the outer assembly, and do not formalize anything in
Lean. The search is completed coverage of its stated trajectories and beam,
not an impossibility theorem; no block minimum is claimed.
