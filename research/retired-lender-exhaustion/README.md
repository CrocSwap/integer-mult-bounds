# Independently certify retired-lender exhaustion through every alias sequence

**Scoped finite upper bound; no new supplier or kappa.** PR2559 claims that
its predecessor words have nine retired-lender candidates, at most two can
stack, and none remain in its shipped words. This package independently checks
the candidate set and proves the extra implication needed for exhaustion:
**no sequence in the specified alias class can create a candidate outside
the initial set**. The upper bound is two, attained by the existing shipped
selection under its inherited native admission assumptions.

The nine-pair count and maximum-two claim belong to
[Philippe Van Velzen / PR2559](https://github.com/CrocSwap/integer-mult-bounds/pull/2559).
This is new verification coverage of its all-sequence implication, not a new
alias construction or another evaluation of its moment. PR2559 already checks
changed endpoints, profiles, owner fill and the root independently. Its
`alias_enumerate.py` and committed receipts enumerate necessary conditions;
a final rescan by itself is not a proof that every alternative sequence stops.

## Result and exact class

The fixed initial words are PR2526's two orientations at
`113c427bf6abe2572184621ebfa00ce7cdf06c46`; the shipped words are PR2559 at
`383ce6c84d92b7b3f00fe267cb23bf3233eecc77`. All four compressed inputs are
retained byte-for-byte with SHA256 and Git blob pins. PR2526's later head has
the same word bytes, but no newer source content is silently substituted.

Each alias removes one noncold ordinary helper whose first use is in B and
replaces all its B/restore occurrences by a retired non-target, non-centre
lender. One invertible dimension-preserving warp is inserted at the first
use; its image must fit the required frame. A/prelude, scalar coefficients,
original event slots/frames and terminal labels stay fixed. Cleanup is the
derived inverse-reverse word. Restored-input buffers and existing warp
carriers cannot be chosen as helpers. See [PROOF.md](PROOF.md) for every
eligibility condition and the proof over arbitrary choices of the new warp.

| Quantity, in each orientation | Result |
|---|---:|
| Initial eligible helpers / lenders |64 / 532|
| Necessary pairs after relaxed tests |9|
| Largest compatible subset |2|
| Size-two graph matchings |16|
| Remaining candidates in shipped word |0|

The candidates are 606/635/638/639->68 and 653->49/68/83/98/101. Every
candidate helper lifetime contains B interval [1084,1497], so one lender cannot
carry two. Since all candidate lenders are sources, an alias only removes a
helper and makes its lender's retirement later and no smaller in dimension.
Other helper lifetimes are unchanged. Induction gives candidate noncreation;
the graph then gives the upper bound. The 16 matchings are combinatorial
possibilities, not 16 new native constructions or independently priced fills.

The existing selection 606->68 and 653->49 reaches two. We bind the complete
changed word to exactly those substitutions, check both binary maps on all 512
vectors, check their source/destination frames, derive all inverse cleanup,
and count the full frame ledger independently. The paid delta is **+H1-2H5**;
the inventory removes one width4 and one width5 helper, agreeing with PR2559.
Native dirty endpoints and global/outer admission are inherited, not rerun.

## Independent evidence

`audit.py` imports no predecessor code. It represents each GF(2)^9 subspace
by its complete vector set and uses integer event slots. Its candidate filter
uses only chronology and dimension capacities, deliberately relaxing the
predecessor's exact end-subspace containment. Excluding an alias even in this
larger necessary set therefore does not depend on a restrictive containment
implementation. The entire frame chain and paid profile are checked too.

`independent.py` separately scans per-role timelines and computes dimensions
by binary elimination. It imports neither the set-span auditor nor the
retained enumerator; all four candidate sets agree. Every one of 512 subsets
of the nine-edge graph is checked in each orientation. The proof of
noncreation, rather than this finite subset census alone, covers all sequences.

Six effective controls reject overlapping lender reuse, removing one helper
twice, a singular replacement warp, missing cleanup, an omitted new rank-one
climb and a wrong equal-dimensional frame image. Reversing frame generator
orders is an accepted positive control. The complete typed receipt is
recomputed. Both interpreters are AI-assisted implementations, not human or
formal-kernel verification.

## Reproduce

Standard-library Python3.12, from the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/retired-lender-exhaustion
python3.12 -I -O -B research/retired-lender-exhaustion/verify.py
python3.12 -I -B research/retired-lender-exhaustion/check_integrity.py
```

Expected: `PASS_RETIRED_LENDER_EXHAUSTION words=4 initial_pairs=9 maximum=2 matchings=16 controls=6`.
Default verification is read-only. Explicit `--write` creates a new receipt
exclusively and refuses overwrite. The integrity command checks a Git-free
export from an unrelated working directory and rejects changed word bytes,
a typed receipt change and occupied output. Source bytes are authenticated
before decompression; no executable predecessor code is imported.

## Limits and next interface

This does not exclude lifted-target compensation, changed preludes, source
partner recovery, splitting lifetimes, altered frame paths, changed terminal
labels or a different original word. It does not optimize general dirty
borrowing, source choices, owner packing, physical stock or recursive cost.
No new moment or conditional exponent is claimed; selected/frozen records
are unchanged. Complete native/global/outer replay remains with the retained
source contribution. The graph result does not discharge those assumptions.

## Open next questions

Can one of the other 15 maximum graph matchings improve a complete owner fill?
First build its changed native word, verify dirty endpoints/cleanup and its
full chronological invoice, then compare an actually feasible fill. The graph
does not establish those matchings' native admissibility or physical benefit.

Can a priced lifetime split or source-partner recovery escape this bound?
First specify the changed operations and surviving original reads, then
recompute the event/frame obligations. Candidate noncreation no longer follows
automatically. A complete compensated word and bill, rather than another
rescan of the fixed class, are the missing inputs.

## Provenance and credit

Main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority 4, was freshly fetched.
Picker seed `4befc9c886d4d27dc01247ae04bf4145` selected independent-moment;
its first binding example passed. TASK.json records the changed scope from a
moment enclosure to this specific finite exhaustion implication, complete PR
coverage and the explicitly stale cached Discussion coverage.

Credit Philippe Van Velzen/PR2559 for the aliases, enumeration and asserted
ceiling; Jeremy Kothe/PR2526 and the T74 word lineage; Tekalign/PR2436 and
Cinna Davis/PR2226 for dirty-borrow mechanisms; all retained native/global
contributors for inherited admission. The small retained README and enumerator
preserve their notices and attribution. Prepared by ywz65 with substantial
OpenAI Codex assistance in proof, implementation, validation and prose.
Separate AI peer review is not independent human review or maintainer admission.
New work Apache-2.0.
