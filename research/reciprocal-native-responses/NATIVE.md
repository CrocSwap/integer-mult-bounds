# Local native contracts and exact prices

The native source uses two banks of 112 data fields and 416 other
fields. All 640 fields have arbitrary initial values. No word reads
or writes the 416 other fields. Their values and frames are unchanged.
This is identity action on those fields, not productive helper progress.

Let `Q=diag(C_qp)`, `q=Q^-1`, and let `F` be the common nine-axis
advance. Include the pinned input and output adapters. The contracts
are:

| Word | Physical input | Physical output |
| --- | --- | --- |
| `forward_E` | `(Qx,y)` | `(F x,F q(y+E x))` |
| `backward_transpose_E` | `(Qx,y)` | `(F(x-E^T y),F q y)` |
| `forward_inverse_adjoint_E` | `(Qx,y)` | `(F x,F q(y+E^-T x))` |
| `backward_inverse_E` | `(Qx,y)` | `(F(x-E^-1 y),F q y)` |

The factor order is part of each contract. In particular, the proof
does not commute `E` through the field-dependent `Q` maps.

## Direct words

The pinned odd16 source has a transfer position for every ordered
off-diagonal mode pair in each six-mode block and eight-clique.
The forward emitter retains its native edges, ordered frames, pair
codes, and endpoint adapters. It replaces each transfer coefficient
by the corresponding coefficient of `E`. It deletes zero transfers.
The full replay checks the first contract on all 640 columns.

The same construction applies to `E^-T`, whose mode diagonal is also
zero. For each forward word, take the literal inverse adjoint. In
chronological order, replace `ADD(t,s,c)` by `ADD(s,t,-c)` and replace
a real `SCALE(c)` by `SCALE(1/c)`. Keep each native unitary, endpoint
monomial, and event order. This gives both backward words, including
their phases and endpoint factors. The two fields of each changed
ADD still have equal ordered frames.

Each direct word has this original local invoice:

| Item | Count |
| --- | ---: |
| Native profile | `1520 H1 + 64 H2 + 48 H3` |
| Native rank mass | 1792 |
| Native children | 1632 |
| Real scalar primitives | 6440 |
| Explicit endpoint maps | 224 |
| Native side-map upper bound | 3264 |
| Owned or private fields | 0 |

The exact common-frame codes are separate from these native words.
On one bank, `E`, `E^-1`, and `E^-T` each cost 3,308 real primitives;
`R` costs 2,892; `P` costs 728. Each such code leaves the other 528
fields unchanged. These prices include the physical pair codes.

## Diagonal metric conversion

Since `E^-T=J E J^-1`, the forward reciprocal word can also use
`J^-1` on both input banks, the `E` forward word, then `J` on both
output banks. The backward reciprocal word can use `J` on both
input banks, the transpose-backward word, then `J^-1` on both
output banks.

`J` is diagonal on physical fields. Each scale commutes with that
field's spatial map even when different fields have different frames.
Each wrapper adds 128 field-scale instructions and 640 real primitives.
It adds no native child. The total is 7,080 real primitives. A one-bank
conversion costs 320; that price would omit the second bank's baseline
restoration in a native shear.

| Word | Real scalar primitives | Maximum prefix row one-norm | Binary denominator height |
| --- | ---: | ---: | ---: |
| Forward `E` | 6440 | 46 | 1 |
| Backward transpose `E` | 6440 | 16 | 1 |
| Forward `E^-T` | 6440 | 30 | 1 |
| Backward inverse `E` | 6440 | 30 | 1 |
| Forward metric wrapper | 7080 | 60 | 1 |
| Backward metric wrapper | 7080 | 30 | 2 |

These bounds cover literal top-level content prefixes. They do not
bound recursive child interiors or prove complete finite precision.

## Coalesced native cuts

After zero transfers are removed, some intermediate frames have no
scalar use. For each field, collect consecutive native advances until
the next scalar event that reads or writes that field. Replace this
chain by one advance. At the end, emit any remaining chain. Keep
every scalar instruction, coefficient, scalar frame, and scalar-event
order unchanged.

Moving a native map past an event on other fields is valid because
the fields are disjoint. The map of the chain is exactly

```text
(Gamma_k Gamma_(k-1)^-1) ... (Gamma_1 Gamma_0^-1)
    = Gamma_k Gamma_0^-1.
```

The source subspaces are nested, so the new rank equals the sum of
the old ranks. The emitter compiles the new ordered-frame map and
checks its exact phase. An equal subspace label alone is insufficient.

The complete coalesced profile is

```text
971 H1 + 237 H2 + 46 H3 + 12 H4 + 5 H5 + 11 H6 + 10 H7.
```

It has 1,292 children and rank mass 1,792. The scalar prices, 224
endpoint maps, and content-prefix bounds are unchanged. The native
side-map upper bound is 2,584. The payload records the original event
indices in every merged chain, and every original native event occurs
in exactly one chain.

For `0<t<1`, each merge reduces the local native moment because
`(r+s)^t<r^t+s^t` for positive `r,s`. This is a local comparison at
fixed width and dimension. No complete supplier exponent follows
without the remaining costs and admission conditions.

## Verification boundary

Both providers have the same stated invoice. All six words per provider
pass the 640-column content replay, scalar-access checks, ordered-frame
ledger, final-frame check, and serialized-payload replay.

The original direct emitter retains all 1,561 source recipe records
and all 224 endpoint records byte for byte. The independent native
review checks that each native occurrence has the same field, old
frame, new frame, rank, and recipe key as the accepted source. Its
separate forward-row and reverse-column calculations import no
producer interpreter. The phase claim is exact inheritance from
the pinned predecessor review, not a fresh spatial replay.

The coalesced emitter gives a fresh exact check of 206 new recipes.
It uses all 18 Pauli images and an exact reference column to determine
the nine-axis Clifford map, including its global phase. Remaining
recipes and endpoint adapters retain the original bytes. The package
replay runs this phase check in normal and optimized Python modes.

The original independent review freeze is
`3e2903374f415db6e456eeb7e6437a8fdcefe324f2052de142773c994d0afaeb`.
The coalesced producer freeze is
`5802ff4fc629eabfbe386fe7924ad6d05d0284201440255e15073579bae576fc`.
At the historical freeze, the coalesced companion had no separate
independent review. The package does not describe the producer's
206 phase checks as a separate review of the whole companion.

The complete emitted words prove local data service. They do not
allocate centre records, give a routed controller, restore saved
records, implement a terminal decoder, provide helper progress,
or admit the complete recursive supplier.

