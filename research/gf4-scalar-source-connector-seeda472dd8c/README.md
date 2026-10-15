# Six-call GF(4) scalar-source connector for two sources

**Recursive-interface construction; no supplier admission or new `kappa`.**
Adding a paid scalar label to a one-source connector update gives a shortest
universal source path for all 15 nonzero coefficient rows on two sources over
`GF(4)`. The path uses six complete source calls, the counting lower bound, and
30 complete target readouts. It restores an arbitrary dirty connector and uses
no extra copy or helper row.

The source path is

```text
S(0,1) S(1,1) S(0,w) S(1,w) S(0,w^2) S(1,w^2)
```

where `S(j,a)` means `z += a B_j x_j` and `w^2+w+1=0`. With the encoding
`0=0, 1=1, 2=w, 3=w^2`, its closed prefix sequence is

```text
(0,0), (1,0), (1,1), (w^2,1), (w^2,w^2), (0,w^2), (0,0).
```

The six nonterminal points have 15 distinct unordered differences, exactly all
nonzero vectors of `GF(4)^2`. [CERTIFICATE.json](CERTIFICATE.json) lists the
boundary pair for every target row and the literal 36-event program stream.

## Interface and dirty-state proof

The changed operation family is the single-source update

```text
S(j,a): z += a B_j x_j,   a in {1,w,w^2}.
```

The base alphabet has only `a=1`; `a=w,w^2` are added. The two source arrays
are read-only. `z` and all targets may start arbitrarily dirty. `B_0`, `B_1`,
and each `A_r` are arbitrary fixed `GF(4)`-linear maps. The target batch is
exactly the 15 nonzero rows `(u_r,v_r)` of `GF(4)^2`:

```text
y_r += A_r (u_r B_0 x_0 + v_r B_1 x_1).
```

After a source prefix `q=(q_0,q_1)`, linearity gives

```text
z_q = z_initial + q_0 B_0 x_0 + q_1 B_1 x_1.
```

For row `(u_r,v_r)`, call `A_r` at its two certified prefix boundaries. The
two readouts add to
`A_r((q_s+q_t)_0 B_0x_0 + (q_s+q_t)_1 B_1x_1)`. Their dirty `A_r z_initial`
terms cancel because the field has characteristic two, and the certified
boundary difference is `(u_r,v_r)`. At the end, each source has been updated
by coefficients `1+w+w^2=0`, so `z` returns exactly to its entry value.
Readouts change no source or connector state; no data-dependent branch is
used.

The lower bound is exact in this domain. A closed path of `k` source events
has at most `k` distinct prefix points because its initial and final points
coincide. In characteristic two each unordered pair supplies one difference.
Covering all 15 nonzero rows therefore requires `binom(k,2) >= 15`, hence
`k >= 6`. The six-event construction attains it. The verifier also exhausts
all 594 closed source words of lengths 1 through 5; the largest observed
coverage is 7 masks. This finite census is a control; the pair-count argument
is the general lower bound for this fixed two-source target family.

The pair-count argument assumes exactly two readouts per target. To justify
full-call optimality even when additional even readouts are allowed, use the
following source-span argument. Every readout coefficient is a prefix of the
source-event sequence, so any sum of readouts lies in the F2 span of those
events. Realizing all 15 rows requires the full four-dimensional F2 space
GF(4)^2. Each source coordinate must therefore supply two independent field
coefficients. Restoration makes its event coefficients sum to zero. Zero or
one nonzero event cannot do this, and two restoring events have equal
coefficients and span at most one dimension. Thus each of the two sources
needs at least three events, for six source events even with arbitrary even
readouts. This argument uses only the declared single-source scalar updates;
no extra connector scaling or root-frame operation is free.

The full call count is therefore also optimal in this alphabet. With `B_0=B_1=0`, an
arbitrary dirty connector must leave every target unchanged, so each nonzero
row's distinct `A_r` target update must occur an even number of times. Since
every nonzero target row must be realized, this requires at least 30 readouts.
The six source events plus those 30 readouts attain the 36-call lower bound.

## Complete cost comparison

The complete source-event price `c_Bj` includes source access, the full `B_j`
child, connector accumulation, per-call dispatch, frame and head travel, and
private scratch restoration. Multiplication by `w` or `w^2` is not free: in
the polynomial basis each costs exactly one binary XOR per `GF(4)` symbol, or
`L` XORs for length `L`. A complete target event price `c_A_r` includes the
full `A_r` child and target update. Both constructions reserve the same two
sources, one dirty connector, and 15 dirty targets; neither adds a copy,
helper row, frame switch, or precision assumption.

For all 15 rows, six have one nonzero coordinate and nine have two. A
per-target closed schedule applies each nonzero source coefficient once on
the forward leg and once on the return leg. It uses 48 source calls and the
same 30 target readouts. Each of the six `(source, coefficient)` event types
occurs eight times. The shared path uses each event type once, for six calls.
Its four nonunit source multiplications cost `4L` XORs, versus `32L` for the
per-target schedule.

The literal event stream is encoded with a prefix record: a source event has
type bit `0`, one source-ID bit, and a two-bit coefficient; a readout has type
bit `1` and a four-bit target ID. The stream's order encodes its boundary
placement, so no uncharged pair-lookup table is required. This uses 174 bits
for the shared path (six source events, 30 readouts) and 342 bits for the
per-target schedule (48 source events, 30 readouts). Let `beta` be the price
per stored descriptor bit and `D_common` the shared interpreter/setup bill.
Then

```text
C_shared =  3(c_B0+c_B1) +  4L + 2 sum_r c_A_r + 174 beta + D_common
C_serial = 24(c_B0+c_B1) + 32L + 2 sum_r c_A_r + 342 beta + D_common
C_serial - C_shared = 21(c_B0+c_B1) + 28L + 168 beta.
```

Thus the explicit source child, scalar-XOR, and event-storage terms all
decrease in this exact program model. A physical supplier still has to supply
the added field operations and meet its precision, hosting, and assembly
contracts; none is inferred from this interface result.

## Open next questions

Does a source-pinned multiplier supplier expose GF(4)-linear source maps and
admit the added scalar updates at a lower complete recursive cost? This matters
because only a source-bound caller and hosting bill can transfer the interface
saving to an existing multiplication construction. The first step is to search
the current selected supplier sources for a two-source GF(4)-linear connector
boundary and price each scaled event, scratch restoration, precision, and
event storage in the supplier's complete-cost model. This package establishes
no such supplier occurrence.

## Scope, provenance, and overlap

The accepted assignment was seed
`a472dd8c6aee62b83f9dbc2e489790b0`, task
`recursive-interfaces / connector-alphabet-change`, priority revision 4,
selector scope key `ff4f5113ed2256ab19ed`, at exact base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. The selected-record SHA-256 is
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
Scope is refined from the card's one-extra-operation prompt to a single-source
scalar family over `GF(4)`, two sources, and the full 15-row target family.
The live claim is [Discussion #2262](https://github.com/CrocSwap/integer-mult-bounds/discussions/2262);
the focused contribution is [PR #2266](https://github.com/CrocSwap/integer-mult-bounds/pull/2266).

The fixed binary dirty connector begins with Ross Richardson's
[PR #943](https://github.com/CrocSwap/integer-mult-bounds/pull/943). Nearby
extensions include the two-source combined event in merged
[PR #1531](https://github.com/CrocSwap/integer-mult-bounds/pull/1531), the
atomic triple-source event in [PR #1518](https://github.com/CrocSwap/integer-mult-bounds/pull/1518),
the six-source DUO construction in [PR #2128](https://github.com/CrocSwap/integer-mult-bounds/pull/2128),
and higher-arity source bundles in [PR #2249](https://github.com/CrocSwap/integer-mult-bounds/pull/2249).
Those bundle several sources per event or change the source-count domain. This
construction keeps one source per event and changes the coefficient alphabet.
The paired-output packet in [PR #2230](https://github.com/CrocSwap/integer-mult-bounds/pull/2230)
changes output events instead. The latest live overlap also found new
[PR #2259](https://github.com/CrocSwap/integer-mult-bounds/pull/2259), which
fuses four aligned `F2[C2^2]` source contributions into a single physical
stream event and proves a data-traffic/head-return saving for one target. That
uses a four-source bundled event and identity coefficient frame. This package
uses one source per event with a nonbinary `GF(4)` coefficient, covers all 15
two-source target rows, and proves the exact six-event difference cover for
arbitrary fixed linear maps and dirty connector/targets. The mechanisms,
domains, cost terms, and evidence differ; no supplier or `kappa` comparison is
claimed. The fresh full overlap snapshot and targeted field-term scan are
recorded in [TASK.json](TASK.json); overlap results are leads, not proof of
novelty.

The live selected result remains the maintainer-reviewed conditional
construction at `kappa = 836330098538459/500000000000000000` on base
`0fdd7d82...`. This GF(4) connector theorem does not alter that result, select
a supplier, or establish a new multiplication exponent.

## Reproduce

From the repository root, with the Python standard library:

```sh
python3 -I -B research/gf4-scalar-source-connector-seeda472dd8c/verify.py
python3 -I -B research/gf4-scalar-source-connector-seeda472dd8c/independent.py
python3 scripts/research_package.py --package research/gf4-scalar-source-connector-seeda472dd8c --check-only
python3.12 scripts/research_package.py --package research/gf4-scalar-source-connector-seeda472dd8c
```

Expected first two lines:

```text
PASS_GF4_SCALAR_SOURCE_CONNECTOR targets=15 source_calls=6 minimum=6 readouts=30 short_closed_words=594 max_short_cover=7 dirty_cases=245760 scalar_ops=4_vs_32 descriptor_bits=174_vs_342 controls=3
PASS_GF4_SCALAR_CONNECTOR_INDEPENDENT rows=15 pair_differences=15 dirty_states=245760 omitted_source_and_misplaced_read_controls=2
```

Prepared by OpenAI Codex with substantial AI assistance. No independent human
review, physical supplier realization, or hosted CI result is claimed.
