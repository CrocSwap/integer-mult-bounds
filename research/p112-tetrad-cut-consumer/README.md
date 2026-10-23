# P112 kernel bases and the selected centre cut: dirty-state audit

**Exact conditional consumer maps and a dirty-baseline correction; no selected-kappa improvement is claimed.**

## Result

For each of the selected provider's fourteen P112 tetrads, the source-bound
unimodular output change `U` has four rows in the left kernel of that block's
rank-four update. The actual selected gauge44 centre-cut matrix `S` admits the
conditional composition

```text
S_new = U^{-T} S
S_new^T (U y) = S^T y.
```

This identity is exact over the rationals for every **fully transformed** port
vector `U y`. Rebuilding its aggregate additive cut changes 176 coefficients
to 286 (+110). It does not imply that coefficient fusion supplies `U y` on an
arbitrary dirty workspace.

The P112 coefficient-fusion identity changes the product update from `K x` to
`U K x`, but leaves an arbitrary dirty baseline `d` unchanged. Its output is
`d + U K x`, whereas the vector required by the conditional consumer is
`U(d + K x)`. The distinction has an exact first-block counterexample. In the
block's `U`-ordered ports, take `d = (1,0,0,0,0,0,0,0)` and `x=0`. The old cut
adds `(0,0,0,0,0,0,0,0)` to the centers; applying `S_new` to the unchanged dirty
vector adds `(0,0,0,0,0,0,1/4,-1/4)`. Using the old cut `S` on the coefficient-
fused product update also fails: `S^T U K` and `S^T K` differ in 16 entries on
the first block and 288 entries across all fourteen.

There is an exact conditional repair if the original dirty baseline remains
available as a separate input. Set `C = S - S_new`; then

```text
S_new^T (d + U K x) + C^T d = S^T (d + K x).
```

The correction has 281 nonzero coefficients across all fourteen blocks (59 on
the first three). It would require both the fused output and a separately
retained dirty input at the consumer. The combined cut and correction have 567
coefficient incidences, 391 above the original 176. The current source binding
does not establish that the dirty input is available there.

| Tetrad | Old cut `S` | Conditional cut `S_new` | Dirty correction `C` | `S_new` delta |
|---|---:|---:|---:|---:|
| `(0, 1, 2, 3)` | 8 | 19 | 16 | +11 |
| `(0, 1, 4, 5)` | 16 | 23 | 20 | +7 |
| `(0, 1, 6, 7)` | 16 | 24 | 23 | +8 |
| `(0, 2, 4, 6)` | 8 | 19 | 16 | +11 |
| `(0, 2, 5, 7)` | 8 | 21 | 21 | +13 |
| `(0, 3, 4, 7)` | 16 | 16 | 26 | 0 |
| `(0, 3, 5, 6)` | 16 | 12 | 15 | -4 |
| `(1, 2, 4, 7)` | 16 | 23 | 28 | +7 |
| `(1, 2, 5, 6)` | 16 | 23 | 20 | +7 |
| `(1, 3, 4, 6)` | 8 | 21 | 21 | +13 |
| `(1, 3, 5, 7)` | 8 | 19 | 16 | +11 |
| `(2, 3, 4, 5)` | 16 | 23 | 20 | +7 |
| `(2, 3, 6, 7)` | 16 | 24 | 23 | +8 |
| `(4, 5, 6, 7)` | 8 | 19 | 16 | +11 |
| **Total** | **176** | **286** | **281** | **+110** |

The coefficients use denominators in `{1, 2, 4}`. The direct row-word route
does transform the full dirty vector, but the predecessor's role-scaled screen
shows that implementation misses `κ=0.003`; coefficient fusion avoids that
word only for the update component.

## Hybrid cut: a lower conditional correction

Each selected transform also has four zero rows in `U K`. Keep the old cut on
those four unchanged coordinates and use the inverse-transpose rows only on the
four updated coordinates:

```text
H_top = S_top,     H_bottom = (U^-T S)_bottom
C_top = 0,         C_bottom = S_bottom - H_bottom
```

Then `H^T d + C^T d = S^T d`, while `H^T U K = S^T K`. Across all fourteen
blocks, `H` has 225 nonzero coefficients and the bottom-only correction has
152. The net is 201 extra incidences over the old 176-add cut, compared with
391 for the full separate-dirty correction. The exact first-three-block net is
43 incidences.

Under the same rank-72, one-rank-1-unit-per-net-incidence sensitivity screen,
three transformed blocks give a complex-only ceiling of `0.004947467105`.
The four checked prefixes (3, 5, 9 and 14 blocks) give `0.004947467105`,
`0.011471186230`, `0.022871681937` and `0.033708626028`. These are planning
sensitivities, not a scalar tariff, supplier or achieved κ.

## Source-side correction without a separate dirty stream

For the hybrid reader `H` and its bottom-only dirty correction `C=S-H`, set
`J=C^T U K`. The exact identity

```text
S^T(d + U K x) - J x = S^T(d + K x)
```

uses the original cut `S` and a correction sourced from the input update; it
does not require retaining `d` as a second consumer input. The checker verifies
the identity over all fourteen source-bound tetrads. The per-block supports of
`J` are `16,24,24,16,16,24,24,24,24,16,16,24,24,16`; the 3/5/9/14-block
prefixes have 64/96/192/288 correction coefficients. Charging each coefficient
as one hypothetical rank-1 unit gives complex-only sensitivities
`0.004756582174`, `0.011073245628`, `0.020601886496` and `0.029934752880`.
This removes the separate-`d` algebraic obligation, but source access to `Jx`,
its frame and lifetime at the consumer, and its actual scalar price remain
unproved.

The same exact screen tests whether the unchanged cut `S` can consume the
coefficient-fused update without any correction by changing only the four
updated rows of a unimodular completion. Writing `K=E E^T`, each block must
satisfy `S_bottom^T F = S^T E`. Two blocks have zero `S_bottom` and nonzero
right-hand side. In the other twelve, the equation has a unique `F`; relative
to the pinned complementary basis, its quotient transfer has rank two on two
blocks, determinant 2 on four and determinant 16 on six. None is unimodular.
Thus this exact route has no unimodular completion that preserves `S` without
a correction. This is a scoped result for the selected reader and
four-kernel-row fusion, not an obstruction to other readers or endpoint
contracts.

The pinned forward program places the 176 cut additions at event positions
12554–12757, after phase `A` and before phase `B` (which starts at 12759).
The canonical scalar prefix `precondition + compensation + A` maps the initial
112 dirty output coordinates to a full-rank response with 272 nonzero entries;
no other initial scalar columns enter that word-level map. Phase `B` then adds
to all 112 output ports and does not touch the eight centre carriers. For the
canonical word, an exact inverse-transpose change of readout now moves the
centre consumer across `B`. It keeps the retimed coefficients on the 112 output
ports, but does not expand native adapters or establish availability of both
the fused update and the separate dirty-baseline stream at that boundary.

## Target sensitivity

The ceiling engine does not price scalar cut additions. To gauge budget margin,
the table below charges each net added incidence as one hypothetical rank-1
unit, while retaining the relaxed rank-72 complex children, centre charge
`112-4k`, and unpaid average `1+k/28` at `a=3/997`:

| Fused tetrads `k` | Full-basis cut incidences | Complex ceiling if full `U y` is supplied | Cut plus dirty correction incidences | Complex ceiling with separately available `d` |
|---:|---:|---:|---:|---:|
| 3 | 26 | 0.005113645447 | 85 | 0.004579932924 |
| 5 | 50 | 0.012033839741 | 146 | 0.010190388089 |
| 9 | 60 | 0.025620878335 | 245 | 0.019105930385 |
| 14 | 110 | 0.038865401047 | 391 | 0.026445058957 |

| Fused tetrads `k` | Hybrid cut plus bottom correction, net added incidences | Hybrid complex ceiling |
|---:|---:|---:|
| 3 | 43 | 0.004947467105 |
| 5 | 76 | 0.011471186230 |
| 9 | 125 | 0.022871681937 |
| 14 | 201 | 0.033708626028 |

## Exact readout retiming across canonical `B`

Let `x_B = M_B x` be the exact state map of the pinned canonical `B` word. For
any `112 × 8` centre readout `A`, the identity

```text
A^T x = (M_B^-T A)^T x_B
```

moves its eight readouts from before `B` to after `B`. The verifier expands all
1,846 canonical `B` operations (1,790 adds and 56 scales), computes the
inverse-transpose map over exact rationals, and checks `M_B^T A_post = A` for
every ordinary role and centre. The original 176-coefficient cut becomes a
448-coefficient post-`B` reader: 56 coefficients per centre, all on output
ports, with none on inputs or helpers.

The same transform applies to each hybrid cut and its separately sourced dirty
correction. Their sum remains exactly the retimed original cut. The table
charges both post-`B` readers against the original 176-add cut, using the same
hypothetical one-rank-1-unit-per-net-incidence tariff and relaxed rank-72
complex profile as above.

| Fused tetrads `k` | Post-`B` hybrid support | Post-`B` dirty-correction support | Net incidences over original cut | Extra over retimed original | Incidence-only complex κ ceiling |
|---:|---:|---:|---:|---:|---:|
| 3 | 450 | 52 | 326 | 54 | 0.003212495586 |
| 5 | 454 | 76 | 354 | 82 | 0.007657155804 |
| 9 | 441 | 140 | 405 | 133 | 0.015679681607 |
| 14 | 437 | 215 | 476 | 204 | 0.024130777318 |

### Native frame compatibility at the cut and post-`B` boundaries

The native label trace also tests the alternative of keeping the consumer at
its selected location, after `A` and before `B`. Throughout the existing cut
window, all 112 output roles and all eight active private centre accumulators
are in frame 0; the 176 source-bound cut ADDs use that same frame. A hybrid
reader placed at this boundary therefore needs no candidate frame-join units
for its added terms. Its three-block incidence-only sensitivity remains
`0.004947467105`, above `0.003` under the relaxed profile.

This is a frame-compatibility result, not a new native schedule: it does not
establish that the changed coefficients and separately sourced dirty-baseline
correction can be installed at this event window. It does show that the
post-`B` frame join below is avoidable if the consumer stays before `B`.

The incidence-only table treats each added scalar coefficient as one
hypothetical rank-1 unit. The selected native execution has a further boundary
cost: its 112 output roles occupy 112 distinct rank-8 frames after `B`, while
the eight centre roles occupy frames 415–422. Their union has rank 9; the only
common selected frame is frame 1. Therefore none of the 448 original retimed
coefficients is a direct same-frame ADD at this boundary. The three-block
hybrid and correction likewise have 450 and 52 cross-frame coefficients.

The native recipe audit exactly checks one rank-1 child recipe from each of the
120 distinct role frames to frame 1. Charging those 120 units as one shared
common-frame pass gives this further optimistic sensitivity:

| Fused tetrads `k` | Extra frame-join rank-1 units | Complex κ ceiling after one pass |
|---:|---:|---:|
| 3 | 120 | 0.002797088144 |
| 5 | 120 | 0.006698357356 |
| 9 | 120 | 0.013825363860 |
| 14 | 120 | 0.021482998123 |

Thus retiming the three-block route to post-`B` falls below `0.003` even under
this one-pass ideal profile, before restoration, a separately executed
dirty-baseline stream, or other endpoint costs. The larger post-`B` prefixes
still clear `0.003` only as sensitivities. This is not a universal obstruction:
the source-bound pre-`B` window avoids the candidate joins, while adapter
expansion, endpoint ownership, dirty-stream availability, cleanup/restoration,
the actual scalar tariff, and the complete bit-side invoice remain open. The
selected κ remains `0.001672660197076918`.

The highest checked conditional ideal sensitivity is `0.038865401047` when a
producer supplies the full transformed vector at no separately priced basis
conversion. The coefficient-fused update with an explicit dirty correction
reaches `0.026445058957` under the same sensitivity tariff, provided `d` is
available. The inherited bit rank-63 ideal ceiling is `0.052325479379`, so both
remain complex-limited if that bit relaxation is retained unchanged. The hybrid
14-block sensitivity is `0.033708626028`. These are not physical invoices or
achieved kappa values: the incidence tariff, rank-72 children, dirty-input
ownership, bit supplier, and full implementation remain unproved. The selected
kappa remains `0.001672660197076918`.

## Obligation ledger and comparison

| Obligation | Status |
|---|---|
| Source binding of selected P112 port labels and all fourteen gauge44 cut blocks | **Proved** against pinned archive hashes |
| Four integer update-kernel rows and unimodular transform per block | **Proved** over the integers |
| `S_new^T U = S^T` when the entire vector is transformed | **Proved** over the rationals |
| Coefficient-fused output leaves dirty baseline unchanged | **Proved** in the model `d + U K x`; the cut counterexample is exact |
| Separate correction `C=S-S_new` restores the old dirty contribution | **Proved** over the rationals; support 281 |
| Hybrid cut and bottom-only dirty correction identities | **Proved** over the rationals; supports 225 and 152 |
| Input-side correction `J=C^T U K` restores the old product readout without a second dirty input | **Proved** over the rationals; supports 64/96/192/288 on the checked prefixes |
| No correction can preserve `S` under a unimodular four-kernel-row completion for this route | **Proved** by the exact completion census; not a universal obstruction |
| Selected cut position relative to `A`/`B` and word-scalar dirty response | **Proved** against pinned source; native adapters are not expanded |
| Availability of the fused update at the selected cut after adapter expansion | **Unknown** |
| Source, frame and lifetime for the input-side `Jx` correction | **Unknown** |
| Scalar price of the extra incidences and rank-72 implementation | **Unknown** |
| Chronology, precision/magnitude limits, cleanup, restoration, and full bit-side invoice | **Unknown** |
| Selected frontier update | **Not claimed**; selected kappa is unchanged |

This differs from the related [gauge44 port-syndrome encoding](../gauge44-port-syndrome-encoding/README.md),
which uses 104 row shears to concentrate the centre signal into eight anchors
while leaving a residual consumer. Here the P112 update-kernel rows change the
coefficient output basis, and this audit isolates the dirty-baseline cost of
connecting that update to the actual selected centre cut.

## Open next questions

1. Can the three-block source correction `Jx` be produced at the pre-`B`
   frame-0 cut from an admitted source and kept live through the centre readout?
   Bind one tetrad through the adapter-expanded provider and exact owner
   chronology, then price its scalar operations and cleanup. The 64-coefficient
   sensitivity is only a planning profile; source access, lifetimes and the
   actual tariff are not established.
2. Does the complete joint scalar and bit-side invoice retain a κ target above
   `0.003`? Replace the rank-72 children and rank-1 incidence assumption with
   an admitted complex supplier, and combine its complete cut/restoration cost
   with an independently admitted bit supplier. Neither supplier nor the full
   invoice is established here.

## Sources and reproduction

The selected source archive, P112 basis witness, port binding, geometry, bit
price dependency and ceiling engine are pinned in [SOURCES.json](SOURCES.json).
The selected record and task catalogue are provenance; the other listed files
are live inputs.

From the repository root:

```sh
python3 scripts/research_package.py --package research/p112-tetrad-cut-consumer --check-only
python3.12 scripts/research_package.py --package research/p112-tetrad-cut-consumer
python3.12 -B research/p112-tetrad-cut-consumer/verify_input_correction.py
```

The verifier uses Python's standard library and exact `Fraction` arithmetic.
It does not replay the full native program.

## Open next questions

- Can the canonical post-`B` hybrid reader be realized after native adapter
  expansion for both the fused update and separate dirty-baseline stream? Bind
  one tetrad through adapters, `B`, cleanup and owner lifetimes; include any
  duplicated `B` execution in its invoice.
- Can another unimodular completion reduce both the dirty-correction support
  and the fused term's copy cost? Search only after the dirty-source contract
  and an explicit scalar allowance are established.
- Can a concrete transformed supplier, exact scalar tariff, and admitted bit
  side keep the joint target above `0.003`? The rank-72 and incidence screens
  are planning sensitivities only.

## Credit

Prepared by Gonzalo Mier with substantial OpenAI Codex assistance. The local
P112 tetrad construction retains the predecessor attribution in its source
package; the selected provider and archived sources retain their original
credits. New work is Apache-2.0.
