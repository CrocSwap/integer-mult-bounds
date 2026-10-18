# A complete P104 backward word with collectors restored to zero

**Finite exact construction; all eight private collectors restore to zero.**
The complete 4,734-event forward word in
[PR2458](https://github.com/CrocSwap/integer-mult-bounds/pull/2458), exact head
`3170afd2fc13a990bfe28f5ab6421bcda4ffd0f6`, now has a literal backward word:
4,982 events, including 208 explicit source sign operations. It implements
the logical inverse-transpose on all **358 arbitrary boundary inputs**, in
the reversed endpoint charts. Each of the eight forward private COPY
lifetimes becomes a zero-initialized collector, a rank-seven upward
transport, one accumulation into its owner, a return transport, inverse
gathers, and erasure of exact zero. A complete cheaper adjoint word is
retained for comparison: it has 4,942 events and requires nonzero discard.
The zero-restoring completion adds exactly eight H7 transports and 32 ADDs.

This addresses PR2458's explicitly remaining complete-program handoff.
That predecessor certifies forward composition and the adjoints of the
161 newly added transport types, but does not transpose COPY/discard or
compose a complete backward program. The construction here covers both
the retained channel and PR2445's two-target correction, including every
dirty helper, all native transports, and the intrinsic endpoint adapters.
It does **not** supply the repository's full physical paired supplier or
turn reversed persistent paths into monotone paths.

Nearby [PR2479](https://github.com/CrocSwap/integer-mult-bounds/pull/2479),
head `65e58f85d98b4a6344c6221623df1d4caa519604`, covers the original uncorrected
G/2 channel using public macro shears and an explicit nonzero-discard
accumulator contract. It does not cover this corrected 358-input word or
zero restoration. The present theorem deliberately states backward chart
coordinates; it does not inherit that PR's physical inverse-transpose claim.
General adjoint transposition is not claimed as a new mathematical principle.

## Exact boundary theorem

Order the logical inputs as X (104), Y (104), H (150). The checked forward
matrix is the real block shear

```text
S = [ I  0  0 ]      C[t,s] = delta[t,s],       t=0,1
    [ C  I  0 ]               <p_t,p_s>/2,     t=2,...,103
    [ 0  0  I ]
```

Here the p are the original P104 roots; their doubled integer coordinates
are independently reconstructed from E8 and the pinned removed-root set.
The forward word and the backward word are each checked against all
128,164 entries of their expected 358-by-358 matrices. In the backward
word, X_s gains `-sum_t C[t,s] Y_t`, while every Y and H restores logically.
The checker also multiplies the independently replayed matrices to verify
`S^T D = I`. Because the corrected first two rows make C nonsymmetric, a
mistaken C in place of C^T is detected.

Let Gamma_i and Gamma_f be the block-diagonal canonical chart unitaries
at the forward endpoints. The forward physical operator is
`F = Gamma_f S Gamma_i^-1`. Reverse chronological adjoints of the complete
forward word implement `F* = Gamma_i S^T Gamma_f^-1`.
Define J to negate all X registers and leave Y and H unchanged. Since
`(S-I)^2=0`, direct block multiplication gives `J S^T J = S^-T`.
J commutes with the block-diagonal charts. Thus the emitted word implements

```text
D_physical = J F* J = Gamma_i S^-T Gamma_f^-1.
```

This is the **logical inverse-transpose in backward canonical charts**.
It is not a claim that the emitted physical matrix is F^-T. In particular,
the complex chart factors may not be dropped or silently transposed.
An added helper originally goes from ZERO to FULL; here it goes from FULL
to ZERO. Logical helper restoration does not imply the physical arrays
are identical across those endpoints.

## COPY/discard adjoints and the zero-restoring completion

All registers hold arbitrary complex 512-vectors. ADD uses a real rational
coefficient and an identical current chart on both operands. The backward
compiler reverses the complete event order and uses these rules:

| Forward operation | Backward adjoint operation |
| --- | --- |
| `d += a s` | `s += a d` |
| create private C with value zero | discard private C |
| discard private C | create private C with value zero |
| `COPY C <- q`, C known zero | `q += C` |
| native transport A to B | native adjoint B to A |

To justify COPY, regard the forward COPY as ADD into its known zero
destination. Its adjoint is accumulation into the old source, leaving C
unchanged. The adjoint of the preceding zero embedding is projection,
which discards that remaining C. The adjoint of forward projection creates
a zero collector. These are maps between the explicit live register spaces;
rectangular embedding/projection is included in the adjoint identity.

The intermediate program [DUAL.json](DUAL.json) contains all eight complete
lifetimes. The receipt records their frames, event ranges, nonzero support
at discard, and the number of gathers and owner accumulations. Lifetimes
do not overlap, so at most one private collector is live. No COPY operation
remains. The checker rejects the assertion that this intermediate word's
collectors are zero when discarded.

The final program [CLEAN-DUAL.json](CLEAN-DUAL.json) removes that requirement.
Every collector gathers 3, 4 or 5 D registers at one line chart, climbs to
an eight-dimensional cap, and accumulates into a Q owner. The entire
lifetime's only writes are to C and that Q; every D source is different
from Q and retains its value and chart. After accumulation, transport C
back to the line and subtract those same D values in reverse order. C is
then exactly zero, for every arbitrary persistent input. Erase it at the
line chart. None of these cleanup steps changes a persistent register.

`bind_clean` checks the complete local event pattern and disjoint-source
premise rather than assuming that a saved value remains available. An
independent all-input row replay then enforces zero at every erase and the
same complete persistent endpoint. The receipt records both words, each
cleanup extension and all eight zero-output lifetimes. The final word
needs one reusable zero-initialized private register; it does not need a
nonzero-discard permission or an extra dirty helper.

This is logical zero restoration with exact native transport operators,
not yet a physical tape implementation. Every zero, erasure, sign, inverse
gather and adapter remains explicit work requiring physical lowering.

## Native operators and invoice

The intermediate word's **1,646 transport occurrences** bind to the
adjoints of **901 exact directed frame pairs**: 740 retained and 161 from PR2458.
The clean completion has **1,654 occurrences and 909 directed pairs**.
Its eight additional transports are the already-certified forward
operators of the eight collector climbs, so no new native recipe is assumed.
Exact physical chart representatives, not merely equivalent span sets,
are checked. The retained Gaussian-dyadic interpreter verifies all signed
Pauli images plus the exact image of basis zero, including global phase.
That identifies the complete 512-dimensional Clifford operator.

For a retained recipe `L F_k R`, use the explicit chronological program
`L* ; F_k ; XOR(2^k-1) ; R*`. This is its adjoint because
`C_j^-1 = X_j C_j` and hence `F_k^-1 = X_(2^k-1) F_k`.
The XOR is rank-zero adapter work, not a second child. This gives one
positive rank-k child for every retained backward transport. The 161 added
recipes already contain a positive-child adjoint recipe; those literal
recipes are rechecked. No new Clifford compiler is trusted.

The 208 intrinsic endpoint adapters are also checked in both directions.
To use intrinsic input/output charts, prepend the adjoints of the forward
Y exit adapters and append the adjoints of the forward X entry adapters.
All are block diagonal, so the X sign passes commute with them. This gives
the same theorem with the corresponding intrinsic endpoint chart unitaries.

| Complete backward quantity | Value |
| --- | ---: |
| Persistent X / Y / arbitrary dirty H | 104 / 104 / 150 |
| Literal events | 4,982 |
| Scalar ADD / sign / zero / zero erasure | 3,104 / 208 / 8 / 8 |
| Transport occurrences / distinct pairs | 1,654 / 909 |
| Positive child profile | 1216 H1 + 74 H2 + 86 H3 + 104 H4 + 48 H5 + 42 H6 + 76 H7 + 8 H8 |
| Positive transport rank mass | 3,126 |
| Intrinsic rank-zero endpoint adapters | 208 |
| Simultaneously live private collectors | at most 1 |

The clean profile is the full forward profile plus eight H7 returns,
an additional rank mass of 56. This is a
finite local invoice, not a recursive excess or running-time bound. It
omits no events from the literal word but does not price adapter routing,
physical scalar lowering, controller allocation, idle/residual work,
precision, or an all-size compiler. No new kappa or helper minimum follows.

## Reproduce and evidence boundary

Python 3.12, standard library, from repository root:

```sh
python3.12 -I -O -B research/p104-owned-collector-dual/verify.py
python3.12 -I -O -B research/p104-owned-collector-dual/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-owned-collector-dual
```

The verifier reads both frozen programs and [RESULT.json](RESULT.json); it
does not regenerate missing evidence or import build.py. Optional
regeneration is `build.py --out NEW_FILE` for the intermediate word and
`build.py --clean --out NEW_FILE` for the completed word; output must not already exist.
The behavioral checks compare a regenerated mathematical payload, replay
in a Git-free read-only export, reject missing/corrupted evidence and source
drift, and test exclusive output creation. Twelve semantic negative controls
cover native phase, sign omission, event order, collector accumulation,
entry charts, missing transports, incorrect transpose, nonzero discard,
omitted cleanup transport, missing inverse gather and wrong cleanup sign.
A permuted order of independent input signs is accepted as equivalent.

The new independent components are scalar matrix replay, E8 endpoint
reconstruction, complete native occurrence binding and explicit lifecycle
transposition. The existing native interpreter is reused with credit, not
presented as newly independent. This is exact finite computation and a
written composition proof, not proof-kernel verification. No full selected
frontier cold replay or hosted CI result is claimed.

[SOURCES.json](SOURCES.json) pins main-tree inputs; [PREDECESSORS.json](PREDECESSORS.json)
pins the two unchanged PR2458 data files by exact commit, blob and SHA256.
The selected record is unchanged, SHA256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.

## Open next questions

1. Can the collector lifecycle be admitted with a complete physical
   initialization/gather/accumulate/zero-return bill? Begin with one frozen
   lifetime and actual 512-coefficient storage, then retain all dirty owner
   data. This matters because exact logical zero restoration is not a tape program.
2. Can backward charts be converted into the desired complementary-frame,
   monotone persistent paths without increasing the full invoice? Begin
   with the eight rank-seven collector climbs and added FULL-to-ZERO helper
   paths. The current reversed paths do not establish that supplier condition.

These are live interface obligations, not separate claimed completed results.

## Credit

Prepared by ywz65 with substantial OpenAI Codex assistance for construction,
code, proof drafting and checking. Separate AI review is recorded in TASK.json;
it is not represented as human review. New work is Apache-2.0.

Credit PR2458 for added exact native recipes and its explicit backward handoff;
Ross Richardson / PR2445 for the two-target logical word and sharing result;
commdata2338 / PR2393 for the one-target acquisition proof; Hiroki Kumazaki /
PR2353 and Philippe Van Velzen for the relay model. Chafik Boukhalfa / PR1991
provides native channel lowering and physical labels, Rohan Arun / PR1972 the
scalar/frame channel, Adam Gall / PR1940 its schedule, Josie Elliston / PR1071
the fixture, and Ali Romman / PR1125 and PR1862 the geometry/interpreter lineage.
The retained native ancestry includes icekylinx / PR531 and PR523/514/507/425/433.
Original notices remain in `research/p104-native-channel/notices/`; no
predecessor source or selected certificate is modified.
