# Whole-owner pooling of the complex supplier

This construction is conditional on the all-size compiler, common-label,
restored-row, precision/tape and analytic-transfer contracts retained by the
pinned PR493 bit and PR484 complex packages. It also retains PR484's explicit
Lemma A realization contract for paid residual wrappers with borrowed spectators.
Its Lemma G schedule/conjugation identities are checked on the serialized local
programs, with independent pre-operation integer bounds. Finite verification
alone does not establish the inherited all-size contracts.

## Placement

Keep PR484's gauge80-kernel42 local word, its exact Gaussian phases, both
orientations, and all entry/exit wrappers. There are 560 helper roles in each of
72 complete local invocations, indexed by nine stages and eight replicas. A
helper of entrance rank e has one residual of width 9-e. No residual is split.

Pool the idle coordinates of all eight physical replicas. A frozen allocation
places every whole residual in a single pending idle child, and a frozen
bipartite edge coloring assigns that slot to its invocation replica. Left
vertices are physical families; right vertices are actual helpers. Each helper
has degree eight and every physical family has degree at most eight at the
stage. The eight matching colors give each invocation exactly one of every
helper and at most one helper on any family. The verifier reads every actual
role, rather than trusting existence of a coloring or the optimizer status.

Every host is an idle pair at that stage. Thus no host is an active data wire,
even if its physical replica differs from its invocation replica. The literal
loop order is retained: recipe phase, replica, cover class, complete local
invocation. Entry wrapper, local word and exit wrapper all finish before the
next replica or cover class. This is necessary when spectators are borrowed
from coordinates that another invocation later uses.

## Actual maps and restoration

For each physical port q, take the pinned orthogonal 73-column basis B_q. A
helper's first w columns are precisely its pending residual coordinates. Its
next 9-w columns are the canonical unused spectator coordinates. Append every
remaining B_q column in increasing basis-index order. The resulting full
matrix is an orthogonal coordinate permutation of B_q, with inverse its
transpose. Both reflected local programs use this same whole-family chart.

The fresh PR484 local check establishes the normalized helper action
L_E^-1 S_E R_E^-1 = C_[w] tensor I on all 512 local address columns, including
spectators, with all global phases. Its emitted scalar word restores arbitrary
dirty helper inputs and its private work. Unique physical owners within a
complete invocation let the scalar/common-label identity be transported through
these full charts without aliasing. Because that invocation restores the
borrowed work before the next, reusing the physical family in a later replica
is allowed under the same whole-invocation realization contract.

Across all calls, occupied cells of each pending idle child are disjoint. The
explicit remainder child uses that family's actual replica, starts at the
recorded pending offset, and executes once. The old `replicas=8` shorthand is
not applied to these heterogeneous remainders. The independent controller audit
checks these cells, execution windows, full charts, source-program hashes,
private-family rebase and cover correction. Deliberately corrupted programs
must fail the controller audit.

## Paid profile and finite charge

All 40,320 whole residuals fit on the 7,680 existing data families. There are no
bank families. The physical stock is 8,258, including unchanged private centres,
reserved tableau and two coefficient registers. The complete paid profile is

```
rank   1       2      3     4      5     6    7     8
count 148440  66816  7472  19728  25664  144  1800  4120
```

Its rank mass is 558,144, and 73*7680 - 558144 = 2496. Both exact moment engines
include the inherited bad-cover fallback. The complete invoice counts unchanged
local primitives, wrappers and selectors, and rebases stock, private families,
idle remainders, routing and final correction to the actual emitted program.
No new factor is hidden in a cached coefficient. For the global prefix, use
maximum stream L2 norm over every physical family and cover class. Each
completed helper endpoint is unitary; each completed data shear or bridge has
at most two unitary summands. For each actual orthogonal chart, right
multiplication permutes the cover classes, so an active stream is visited once
per complete call sweep. The bound uses all 72 ordered call sweeps and nine
bridges, without assuming replica independence. The local scalar/Horner envelope
costs 20 bits; conversion from the initial supremum norm to L2 on 2^73 entries
costs 37 bits; four bits cover primitive arithmetic. Thus 142 bits suffice,
within the retained 192-bit allowance. The verifier checks the actual matrices,
complete-call endpoints, scalar envelope and controller premises used here. Each remainder is at most
rank eight, so the degree-two halving inequality is 73^2 > 2*8^2.

The bit side is reconstructed from PR493 with real Boost. Its physical prefix,
charged three-level coefficient and row coefficient are read from the fresh
receipt. Six bootstrap levels and all 47 strict outer inequalities use the
fresh complex exponent, common row allowance, and C0=2^210000. The next grid
point and zero-eta, zero-beta and unit-beta controls must all fail.

## Provenance and limits

The selection is a finite nomination, not an optimality theorem. Search used
floating-point MILP objectives and matching only to propose the frozen map;
certification uses the actual scalar words, complete emitted role map, exact
integer/rational checks and fresh source replays. The earlier unpooled padding
experiment is retained as provenance, not a separately published record.

This does not use the cross-family split of PR448/480/494. Those submissions
carry a distinct disputed operator interface. This package makes a conditional
whole-owner claim only and does not claim the largest number among all draft
submissions under different assumptions.
