# Endpoint-aware bank and price review

Independent source/interface review, 2026-10-09. No blocking defect found in `endpoint-banks.cpp` or `endpoint-price.cpp`. This is a source review, not another full end-to-end replay.

The bank extension uses the actual supplied final endpoint H and initial frame U for every role. Its residual operator is P_H-P_U. It checks both projector nesting identities P_U P_H=P_U=P_H P_U. With the nondegenerate Gram inversions already checked, this is the orthogonal projector onto H intersect U-perp. The constructed ordered chart [H intersect U-perp, U, H-perp] has exactly24 columns. Both matrix inverse identities, conjugacy to diag(I_r,0), idempotence, and orthogonality of the residual against its complement are checked over exact rationals. Full H uses an empty exterior complement; ZERO U is explicitly supported in the projector function. The accepted final runs have positive residual ranks, within the implemented scope.

The new chart operations enter max(744,new_max)+239, including conservative four-factor row swaps and the existing prime guard. The inherited original frames and all newly changed endpoint pairs are handled separately: pairs are collected whenever the initial frame is new or the final rank differs from24. Thus every one of the rank23 cleanup endpoints receives an explicit chart check.

The bank census is recomputed from the original initial frames and the supplied final endpoints before subtracting the new entrances. The440 early restorations change440 original rank4 residuals to rank3, giving base families706 at rank3,1760 at rank4, and13928 at rank24 for n19914/R16394. Rank3 and rank4 homogeneous banks consume exactly3 and4 banks per role at120 replicas. Existing kernel gauges and the added transported entrances are counted against the full-residual roles, and their actual role/replica slots are enumerated. The added29 rank18 entrances introduce residual6, inside the generic mixed-width bank construction; the remaining rank4 filler count is checked nonnegative.

For the combined transport+cleanup input, total new entrance rank is1552+522=2074 and endpoint deficit440. Therefore banks per stage are

    343870 - 440 - 2074 = 341356,

literal stock is844800+5*341356=2551580, and normalized stock is510316. The price interface requires precisely

    W = 119374 + 24*R - endpoint_deficit - new_entrance_rank.

The baseline stock adds both2074 and440 back, not merely the kernel rank. The baseline histogram is recovered by subtracting the complete actual cumulative delta; both baseline and candidate deficit must equal105600. This prevents the endpoint saving being counted only in stock or only in the histogram. Subsequent fixed-prime and literal finite-invoice stages must still bind the final emitted word, which is outside these two files' scope.

Reviewed hashes:

- endpoint-banks.cpp: `94f62f0c57a20dc73408bed900a0e31bf8d98ae9e4fadc5cdfcbdaf4164a2620`
- endpoint-price.cpp: `5b172f0e3f6fcb849be13d19f239ad256965c164272af3a8c3b7d4851662cb6c`

The bank program reads final frames from `baseline_export/249-states.json`; callers must supply the endpoint-adjusted export paired with the actual final word. Supplying the old sink export would reject or misdescribe the intended440 endpoint changes. The existing parent orchestration is responsible for that explicit source binding. No code edits made in this review.
