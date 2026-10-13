# Recursive interfaces: seed 51

- Assignment: OS randomness, `secrets.randbelow(100) = 51`.
- Exact base: `91a2094f2e022930069e8cfdc810a3ea1b81cd09`.
- Started: 2026-10-14 00:00:48 Australia/Melbourne (13:00:48 UTC).
- Time box: 40 minutes; finish by 00:40:48 Melbourne; final ten minutes
  reserved for verification, overlap refresh and handoff.
- Selected object: three independent binary sources, three independent outputs,
  one arbitrary dirty connector, and only the six complete factor-shear oracles
  `z += B_j x_j`, `y_i += A_i z`. Eliminate intermediate connector restoration
  by carrying partial source sums between output reads; restore it at the end.
- Method: exact shortest paths on the complete 32,768-state symbolic interface
  graph; all 512 binary 3-by-3 requested product matrices. Seed 51 chooses
  dimension `2 + 51 % 2 = 3` and deterministic witness tie breaking.
- Expected deliverable: a priced explicit schedule, written interface argument,
  independent exact replay and shortest-path certificate, mutation controls,
  and a scoped research note. No new kappa or selected-supplier change.

Three candidates were considered: dirty restoration for the arbitrary-stride
cyclic inverse (#846), connector reuse inside product trees (#822), and carrying
source sums across a multiple-input/multiple-output binary batch. The first two
have substantial pending implementations. The third changes #889's one-source
fanout model: the connector need not return to its initial value between stars.
Unlike #522's coordinate-sector construction, this is a black-box product-shear
interface with independent source arrays. The existing coordinate-Fourier
negative result is not reopened: no address-mixing operation is free here.

The API returned no pinned issues, and neither open issue (#650, #913) was a
sprint coordination issue. No reservation issue was opened. Initial overlap
inspection covered 713 open PR titles, the review ledger, #522/#822/#846/#889
bodies and #889's implementation, plus all-state searches for biclique, fanin,
connector walk and multiple inputs. This is not a claim to have reviewed every
pending submission.

## Result (one completion update)

Completed the full 512-pattern certificate and independent free-algebra replay.
Every pattern attains two queries per active factor in the specified alphabet.
The six-edge cycle uses 12 queries instead of 18, or 198 lowered leaves instead
of the better star comparator's 228, with the same four dirty borrowed arrays.
All 23,040 dense cases, 11 obligation-specific controls, 120 tape-formula cases,
regeneration/relocation and four package corruption checks pass. No new kappa.

The [reviewable result and evidence](https://github.com/RossRichardson/integer-mult-bounds/tree/research/recursive-seed51-20261014/research/binary-connector-walk)
are on the isolated contribution branch; VALIDATION.md records the limits.
The prepublication refresh reached #931, including the distinct grouped inverse
in #929. No coordination issue was created. The final verification/handoff
phase began after the implementation was complete, with the session's remaining
time reserved for it.
