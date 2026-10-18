# A replica-local prefix bound with borrowed unitary residuals

## Precise statement

This statement concerns #626 at base
`66849e1475c930fd7732b1a0067ffee7e1e95f60`. "Selected" below refers to that
pinned baseline. No prefix estimate for the later upstream frontier follows.

Assume the same normalized finite-family interfaces used by the selected
#626 global-prefix invoice. In particular:

1. Each physical streamed family has a Hilbert norm. Its frame/chart
   changes, phase corrections, residual endpoints and idle operations
   are unitary **within that family**. Permutations of families within
   a replica are also allowed. An arbitrary unitary that mixes families
   is not covered by this assertion.
2. At a completed local invocation boundary, the active data families of
   the invocation replica implement a normalized shear `Y += U X` or
   `X -= U* Y`, with `U` unitary (a contraction would suffice). Every
   borrowed helper has only its own familywise unitary residual endpoint;
   no output in another family depends on that helper's initial dirt.
   Private centres/work are cleared. A call is indivisible.
3. A bridge has coefficient +1 or -1 and operates on two pairs of
   families of the same replica. All other completed controller events
   preserve the maximum individual-family norm within each replica.
4. For any local invocation and arbitrary data/helper inputs, the
   existing scalar/Horner envelope bounds each internal streamed-family
   norm by `L` times the maximum input-family norm, for a fixed `L < 2^101`. The
   inherited normalization/stream-conversion and arithmetic margins
   remain 37 and 4 bits, respectively.

Then the selected asynchronous controller has sufficient global-prefix
allowance **160 bits**, independent of which replica supplies a helper.
All-size compilation, common-label/mutable-basis realization, normalized
residuals, physical hosting, recursive precision, tape/exact recovery and
analytic transfer remain inherited. This statement does not establish
these assumptions anew.

## Norm and endpoint induction

For replica `r`, write

```
B_r = max { ||x_f||_2 : physical data/owner family f belongs to replica r }.
```

If a family is split across orthogonal cover classes, take the maximum
over the corresponding streamed-family instances as in the inherited
prefix argument. This is **not** the Euclidean norm of the concatenation
of every physical family. Thus no uncharged square root of the number of
families is inserted into the inherited 37-bit conversion.

A data shear obeys `||Y + U X||_2 <= ||Y||_2 + ||X||_2 <= 2 B_r`.
The other direction and signs have the same bound. Its helper endpoints
are unitary within their actual owner families. They may change those
families' values, but they leave their individual norms unchanged. Hence
only the invocation replica needs a factor of two in its bound.

Likewise, both components of a bridge are updated from the matching
components of another pair in the **same** replica. Each component obeys
the triangle inequality above, so one factor of two covers the bridge;
there is no extra factor for its two separate destinations.

Let `a_r(t)` count completed local sweeps and bridges belonging to replica
`r` at boundary `t`, including the bridge currently being bounded after
its update. Induction gives

```
B_r(t) <= 2^a_r(t) B_initial,
max_r B_r(t) <= 2^max_r a_r(t) B_initial.
```

The induction does not commute physical calls, reorder helper borrows, or
assume helpers are clean. Interleaved familywise residual unitaries need
not commute with later shears. Their norm-one action is enough. It also
does not claim that 72 physically concurrent calls are legal: the
selected serialized schedule and whole-call hosting are retained.

Every replica has nine local sweeps and nine bridges, so `a_r(t) <= 18`.
The old argument multiplied bounds for all replicas and charged 144
factors. Taking the maximum of the eight independently maintained bounds
charges at most 18 factors.

## Inside a borrowed-helper invocation

At its start, every input/helper family, including a helper owned by a
different replica, is bounded by `2^max_r a_r B_initial`. Apply the
existing local prefix envelope to this **global maximum**. This gives
`2^(101+18) B_initial` as a conservative bound during the invocation.
The inherited whole-family charts are right-translation bijections:
each physical stream occurs once in a complete invocation's cover sweep.
That interface is needed to lift the vertex-local scalar/Horner receipt
to this bound; the receipt alone would not rule out repeated stream use.
It is unsafe to use just the active replica's own counter: a borrowed
helper may belong to a replica that has progressed further.

Consequently the sufficient inherited-style allowance is

```
local scalar/Horner          101
input stream conversion      37
completed replica growth     18
primitive arithmetic margin   4
                            ---
                            160
```

Some other replica can already have completed all 18 factors while a
late invocation is active. We therefore retain 18 in this uniform bound.
Prefixes of bridge additions and atomic familywise unitary events obey
the same allowance. Prefixes inside their compiled realizations remain
covered only by the inherited primitive/compiler-prefix interface.
The final family translations and within-replica signed
exchanges preserve the same maximum norm. The existing 512-bit reserve
is unchanged, and no precision/tape constant is automatically reduced.

## Binding to the retained construction

The prior global maximum-stream norm argument is explicitly credited to
eumemic's [#496 proof at its pinned head](https://github.com/eumemic/integer-mult-bounds/blob/00cf70efd6a8637531deafef698157ca83e249ee/research/r489-pooled-whole-complex/PROOF.md).
It charges 72 local sweeps and nine simultaneous bridge sweeps in that
historical schedule, obtaining `20 + 37 + 72 + 9 + 4 = 142` bits without
using replica independence. This audit preserves its norm, whole-family
chart argument and normalized-helper interface. The additional step is
an individual replica counter for the selected asynchronous schedule,
whose old invoice separately charges 72 local and 72 bridge sweeps.
Neither the norm choice nor its inherited cover argument is claimed new.

`SOURCES.json` identifies every file below by exact source bytes or full
decompressed gzip payload, at the stated base commit.

- The retained `ROUND20-PARENT-TEMPLATE.json.gz` has local stage pairs
  `0,0,0,1,1,2,2,3,3`, and nine bridges with unit signed coefficients.
  In call `(stage, replica)`, all 224 data-owner families are
  `896*replica + 224*pair + j`, `0 <= j < 224`.
- `prepare_supplier_base.py` preserves the recipe, first 30 source
  schedule events and active data owners through supplier substitution.
  `emit_allcold.py` expands source blocks into the selected plan's
  one-replica interleaving. `audit_allcold.py` independently requires
  the exact source projection `0..29` for each replica, indivisible local
  calls and preserved active data owners. The selected template itself
  is not in the committed receipt directory; source review and the
  frozen receipts are inherited evidence, not a fresh template replay.
- `PLAN.json` selects 72 calls (64 JP8, 8 CK); every replica's projected
  call sequence is stages `0..8`. `OWNERS.json.gz` contains 35,424 roles,
  28,404 of them cross-replica. Every call has 492 distinct helper
  families disjoint from its active data families. Our checker verifies
  these exact finite membership conditions, not all hosting geometry.
- `hpe_audit_local.py` and `hpe_audit_and_transport.py` check the
  arbitrary-dirt scalar endpoint on every input column. That endpoint
  restores helper coordinates in the scalar frame. The physical
  interpretation is supplied separately by `hpe_adapters_local.py`:
  a helper residual is normalized to a Fourier transform tensored with
  identity, on its own physical family. It need not be physical identity.
- The selected invoice reports the largest local allowance as 101 bits
  (JP8 backward), and the global allowance as 286. Both native program
  orientations are semantically hash-bound to the consumed invoice.
  We inherit the exact local arithmetic and frame/phase verification;
  merely reading a PASS receipt is not a new replay of those obligations.

## Adverse controls and limits

The finite models test dirty helper restoration and unitary residuals
with exact rational arithmetic. Missing restoration or compensation
introduces cross-replica dependence. A rational rotation that mixes two
different families can increase their maximum norm, although it is
unitary for the concatenated Euclidean norm. Endpoint identity can hide
arbitrarily large intermediate excursions; this is why the 101-bit local
prefix certificate is still needed. These are counterexamples to weakened
interfaces, not counterexamples to the accepted #626 construction.

Schedule mutations reject doubled or inter-replica bridges, omitted
events, changed dispatch, chronology errors and invalid family ownership.
Such finite tests support the argument and its source bindings; they do
not prove the complete multiplication theorem. This result improves an
overcharge in one conditional bound and leaves kappa unchanged.

Brody Arbon, with substantial OpenAI Codex assistance. Apache-2.0.
