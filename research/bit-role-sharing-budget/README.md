# Bit role sharing: cost first, no new κ

This is the budget gate requested before building a shared-role bit supplier.
It extracts the paid profile from the actual pinned PR589 word, checks every
local Boolean column, and prices complete hypothetical profiles with the
retained boundaries, live volume and bad-class charge.

**Decision:** do not build identical-role pooling or a sharing scheme confined
to one stage for κ=0.01. Pooling saves dispatches but not volume-weighted
recursive work. Even perfect rank-8 consolidation plus free retained-total
copies fails the target. Sharing that changes rank mass or stage boundaries
remains open.

| Screen | Result at necessary bit saving 1/99 |
|---|---|
| Existing complete profile | Moment 1.02773949493: fails |
| Pool identical calls across arbitrary roles | Same moment after batch volume is charged |
| Perfect local consolidation into rank 8 | Moment 1.01604271595: fails |
| Same, with all retained-total copies free | Moment 1.00585416925: fails |
| Preserve boundaries and rank mass; increase child rank cap | Cap 55 fails; cap 56 first permits an optimistic passing invoice |
| Repack all boundaries as well, preserving total rank mass | Cap 36 fails; cap 37 first permits a passing relaxation |

The hypothetical rank-57 invoice leaves room for only **431 extra rank-1
children across the whole program**, including their fallback charge. It
requires fusing more than **98.48% of the local rank mass**, even when the
unfused work is granted ideal rank-8 calls. Fusion restricted to one port's
active spaces would need at least eight stages; cross-port fusion can have a
larger span and is not subject to that stage-count argument. This is a precise design requirement,
not a construction or a proposed κ certificate. The complex endpoint would
also need to improve for κ=0.01.

An alternative arithmetic target is **100 net rank units removed per local
invocation**, plus ideal rank-8 consolidation, with the boundary remainder
and live denominator fixed. Removing 99 fails the target; removing 100
passes. This is an invoice reduction after hosting, not a helper-count or
scalar-gate reduction. No mechanism achieving it is supplied.

The [hosting follow-up](../bit-sharing-hosting-gate/README.md) tests a
running decoder cache and reconstructs every physical helper reservation.
Thirteen free helper eliminations give 104 gross units but zero net units
after owner restoration. With the rank-7 data boundaries preserved, the
corresponding favorable consolidation screen first passes at 102 units.
This refines the implementation requirements; it does not invalidate the
rank-8 relaxation above or supply a replacement operator.

[PROOF.md](PROOF.md) states the fixed-query direct-sum obstruction, complete
cost ledger, relaxation domains, thresholds and repair allowance. Unlike the
earlier three-shear adapter obstruction, its role-query argument allows
arbitrary invertible XOR mixing and any restored dirty private roles. Its
scope is a fixed address permutation; distinct native primitives and
address-dependent charts are outside it.

## Reproduce

From the repository root, standard-library Python only:

```sh
sh research/bit-role-sharing-budget/replay.sh /tmp/bit-role-sharing-budget
```

Use a new output directory. Expected:

```text
PASS_BIT_ROLE_SHARING_COST_SCREEN_NO_NEW_KAPPA
PASS_BIT_ROLE_SHARING_REPLAY
```

The verifier also supports `python3 -I -O -B`. Its positive-atanh rational
interval engine is separate from the inherited Mercator engine and reproduces
the pinned adjacent 10^-24 bit root bracket. The finite coverage is 661 local
Boolean columns, all local frame transitions, all caps 1..63, pool sizes
1/2/4/8/16/32, 108 small coded-query programs and 384 positive-control basis
columns. Four incomplete-cost controls are rejected. No random or open-ended
search is involved.

[evidence/PRICE.json](evidence/PRICE.json) contains the exact intervals and
conditional integer profiles. [SOURCES.json](SOURCES.json) binds every input.
The frozen global remainder is repriced, not freshly rehosted. The physical
supplier, all-size compiler, new storage/layout and new tape program are not
built because neither pooling nor stage-confined sharing passes the target
budget. The rank-57 arithmetic target has no supplied operator.

## Provenance and overlap

Base: `bfff94e78f0e75ebd2593e3cc7710ae5290e8be3`; original main base:
`66849e1475c930fd7732b1a0067ffee7e1e95f60`. PR589 pin:
`a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`. The selected result, producer,
profiles and upstream source are unchanged. This continues
[PR673](https://github.com/CrocSwap/integer-mult-bounds/pull/673).

The queue review through #700 found separate scalar-word optimizations
(#694/#696), a complex RAM direct-source construction (#697), the different
fixed-native-query DATA shear (#677), and complex selector volume pricing
(#679). Those are context, not consumed dependencies. Existing closed local
word searches are not rerun: the new object is a sharing-class cost screen
with arbitrary role mixing and explicit cross-stage target budgets.

The final refresh through #716 also checked #705's complex graded-path
determinant obstruction, #708's scalar decoder sharing, #714's clean root
checkpoint and #715's mixed-port label extension. They change different
objects or contracts and are not dependencies of this cost screen. No pinned
sprint coordination issue was present; the completed claim is local.

Credit eumemic, DreamingOfClouds, chafreaky and their retained source lineage;
Greer Guthrie's related volume-accounting note and commdata2338's query-model
audit. Prepared for **@androolloyd with substantial OpenAI Codex assistance**,
under Apache-2.0. Finite verification is not a formal proof of multiplication.
