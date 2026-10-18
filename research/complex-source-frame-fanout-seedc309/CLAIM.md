## FINDING — bounded C3 shared-source fanout screen

Cycle seed `c309ff190ac582a9bdcf59a3422822e8`; track `complex-mechanisms`; task `complex-new-helper-inventory`; priority revision 3; base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; selected-record SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.

Scope: every three-consecutive-ADD window within A or B of the pinned selected width-73 word, with one unchanged arbitrary source value, three distinct destinations, no source-frame climb, and at least two positive target climbs. The proposed C3 child replaces target ranks `t1,t2,t3` by one child of rank `t1+t2+t3`. Schedules may choose any non-overlapping subset of the complete window set.

Exact replay covers 3,451 A and 1,846 B operations; it finds 32 qualifying windows and an exact maximum-weight schedule of 25. The schedule's zero-overhead profile has ceiling gain `0.9065527351%`. More strongly, exact weighted interval optimization of certified moment-saving upper bounds proves that every schedule in this finite family remains above moment one at the five-percent target; the strict rational margin is in the certificate. The screen grants zero fanout, adapter, helper, source-read, transition, restoration, precision, and hosting costs. It is a scoped negative only; it neither rejects other schedules nor supplies a physical C3 child or new kappa.

Review package and exact source pins: [PR #1799](https://github.com/CrocSwap/integer-mult-bounds/pull/1799), directory `research/complex-source-frame-fanout-seedc309/`. The source-pinned verifier and six focused controls passed under Python 3.14.7; package metadata and pinned-source checks passed. The repository's registered replay requires Python 3.12, which was unavailable locally.

The refreshed overlap scan at 2026-10-14 10:15:55 UTC covered 460 open PRs and 435 Discussions with complete pagination and no warnings; no remote match was found for the final scope terms.

Remaining obligations: any follow-up must separately handle nonconsecutive source-version intervals and destination dependencies, and must price/verify a physical supplier before claiming construction progress. Claim expiry was 2026-10-14 11:56 UTC.
