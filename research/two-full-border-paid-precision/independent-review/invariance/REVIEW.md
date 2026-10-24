# Independent review: logical zero-address invariant

**Conclusion.** The scalar specialization used in the paid-site sensitivity
census is valid for the pinned PR4610 word in both source orientations, under
the inherited exact moving-frame/operator semantics. The proof is an invariant
of every primitive, not a match of the final scalar endpoints. It does **not**
assert that every physical operator fixes the physical vector delta_0.

The independent standard-library checker `check_invariance.py` passed on the
source, producing `INVARIANCE.json`. It imports neither the producer checker nor
an inherited evaluator. It independently checks all 42,898 literal events,
all scalar common-frame contacts, all paid frame/rank transitions, every warp
frame incidence, both final frame inventories, and the signed/oriented
zero-address action of all 72 matrices. Each direction has 3,298 paid sites,
240 warp events, 448 adapter markers, ten section labels, 632 persistent owners
(224 main plus all 408 helpers), and only the single reused owned center C0.
There are no `residual_adapter` events in this exact word.

## Source authentication and orientation

The compressed source is
`research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz`.

| Object | Exact identity |
| --- | --- |
| Compressed SHA256 | `7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05` |
| Uncompressed payload SHA256 | `cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd` |
| Git blob, recomputed from these compressed bytes | `46d929df83817b85a5387bcdb9745e0627d6366e` |
| Public source commit whose local tree binds that blob | `1eb8da6cfb35512c0cc2533413e5ca42f48e13c6` |
| Public source path | `research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz` |
| Forward program canonical-JSON SHA256 | `03e406a5672ada3e1762011d667c79ec04a55d7d1163a9423d0005720234d2ca` |
| Backward program canonical-JSON SHA256 | `a4ff7b7ca8f23c858f8e6f1044bc6abf92168ab17abd2aa420ad384f58a519d3` |

The source-profile head `0ce1b5c9fb7163d0b2f0ac3db95fc418dbbcec62`
printed by the producer is historical metadata; its tree is not available in
this offline checkout and was not independently authenticated here. The actual
bytes are instead authenticated by the SHA256 and the Git blob above, including
both distinct orientation-specific programs. Do not present this as a fresh
verification of that historical profile commit.

## Exact invariant

Let T_U be the inherited exact unitary canonical frame at frame U. A physical
register value in the forward orientation is represented as T_U z, where z is
its logical value. In the backward (inverse-transpose) orientation, use
conjugate(T_U) z. A scalar row in the census denotes a linear combination of
independent owner inputs times the same logical address vector delta_0.

1. **Paid climbs and centers.** The forward physical transition from U to V is
   T_V T_U^{-1}. Therefore it sends T_U z to T_V z: its logical action is exactly
   the identity, including normalization and phase. Its inverse transpose is
   conjugate(T_V) conjugate(T_U)^{-1}, giving the same statement in the backward
   gauge. This applies equally to ascending persistent-owner climbs and the
   oriented C0 center transports. Replacing the paid normalized child G by
   (1+eta)G multiplies the whole logical register by (1+eta), because the scalar
   commutes through the unchanged exact left/right normalizers. No hypothesis
   that a normalizer individually fixes physical delta_0 is needed. The same
   observation holds when one rank-r transition is split into smaller paid
   Gaussian factors and exactly one factor receives this scalar-relative fault.

2. **Logical warps.** The inherited definition is not merely a permutation.
   For invertible binary G,

   K_G delta_x = i^{q_M(Gx)} delta_{Gx},
   M = I + G^{-T}G^{-1},

   where

   q_M(y) = sum_i M_ii y_i + 2 sum_{i<j} M_ij y_i y_j mod 4.

   There is no affine address offset and no constant phase term. Consequently
   G0=0 and q_M(0)=0 give K_G delta_0=delta_0 exactly, not just an invariant line.
   Its inverse and the entrywise conjugates of both signs also fix delta_0.
   These conjugates, not an identification with the adjoint, are the logical
   warp operators in the inverse-transpose orientation. The physical warp is
   T_V K_G^{+/-1} T_U^{-1}; decoding the new frame leaves exactly the stated
   logical K operator. The independent checker checks every actual G is
   invertible, computes its quadratic form, and verifies all four signed and
   oriented zero images are address zero with phase exponent zero. It also
   verifies every actual warp carries the declared frame to the next frame.

3. **Scalar operations and the owned field.** Every ADD or COPY has source and
   target in the same actual frame, so physical componentwise rational
   operations act by the same scalar row arithmetic in logical coordinates.
   SCALE has the same property. Every CLEAR targets C0, and every COPY overwrites
   only C0; no borrowed main or helper field is cleared or overwritten. C0 is a
   single reused owner, rather than eight independent center registers. Its
   clears act as zero maps and must be retained in the suffix sensitivity
   recurrence; the invariance audit does not remove them. All 408 helper owners
   participate in the same checked frame inventory and remain eligible output
   observations. Setting their entry data to zero for a particular witness is
   a legitimate specialization of arbitrary inputs, not a clean-helper promise.

4. **`phase` and adapter markers.** `phase` entries are section labels from the
   emitter, not physical scalar-phase gates. Main adapter markers describe a
   change between the old boundary reference and canonical gauge. For example,
   a forward entry adapter T_U O^{-1} sends O z to T_U z, and an exit adapter
   O T_U^{-1} sends T_U z to O z. Hence they preserve the abstract logical z;
   they need not fix physical delta_0. The backward convention is the conjugate
   one. The exact source has no residual-helper adapter events, so no general
   claim about arbitrary future residual wrappers follows from this audit.

   There is one necessary chronology qualification: **82 X-output adapter
   markers per orientation occur before the retimed final climb to FULL**.
   E.g. forward event 15611 marks X0's output adapter at frame1 while the current
   frame is648; the final648-to1 climb is at15852. These markers are harmless
   because both X's old output reference and canonical final frame are exactly
   the same FULL Fourier F. Their physical adapter is literally I. All other
   boundary adapter markers agree with their current frame. An unconditional
   assertion that every adapter marker already occurs in its advertised final
   frame would be false. The independent checker explicitly isolates and
   permits only this exact-identity exception.

   The checker also verifies that no X field is accessed before its input
   adapter section and no Y field is accessed after its output adapter section.
   Thus the potentially nonidentity adapters can indeed be absorbed into the
   boundary-coordinate definitions; no later scalar contact silently uses the
   canonical gauge after a nonidentity output conversion.

Starting with logical multiples of delta_0, these facts prove by induction that
every intermediate logical register is a scalar multiple of delta_0, with the
coefficient computed by the scalar program. A scalar-relative child fault
preserves the same invariant. Thus ignoring only the logically inert transports
and the zero-fixing warps is valid for this restricted fault direction.

For f tensor fibers, use delta_0 tensor-power f and the tensor powers of each
address frame/warp. Each K has zero-address phase exactly1, so its tensor power
still fixes that vector; no hidden parity or width-dependent phase is introduced.
The owner scalar coefficients retain their literal values. This proves the
same invariant at every fiber count, assuming the inherited tensorized primitive
contract. It is not an extrapolation from one finite dimension's endpoint.

## Inherited definitions versus newly checked premises

`source/PINS.json` records the upstream definitions inspected during review: `bw_gauss.py`,
`bw_adapters.py`, `bw_phases.py`, and `bw_emit.py`, all at
`b58ad9ef4d4e861b0eaa5dba41742bdc072dca51` under
`research/transported-warp-frames/native/vendor/native/new/code/borrow/`.
The key `bw_gauss.py` hash is
`0884b14d6d77cde419a3c773ad9b21d0d18de1e6e20e6b6d5add458ed32ba4cb`.
Its `monomial` defines the zero-constant quadratic phase above; `warp_product`
defines T_V K T_U^{-1}. `bw_phases.py` defines the exact paid frame transition
and the main old references C_q and F C_q^{-1}. These source definitions were
read and authenticated from local Git objects; they are provenance, are not imported by this checker, and are not duplicated in this review bundle. Their full numerical or physical
phase verifiers were not rerun in this task.

Newly checked here are the exact current word's event grammar, all frame
incidences/common-frame contacts, all G matrices and zero-address phases, both
orientation pins, the absent residual adapters, all-owner inventory, and the
82 early identity markers. The interpretation of its primitives as exact
phase-normalized physical operations is inherited source semantics, rather than
a newly proved physical implementation or regenerated PR4610 phase receipt.

## Scope and remaining premises

- This supports individual independent scalar-relative operator faults. It
  does not assert these faults arise from a particular deterministic rounded
  implementation or exclude correlated errors/cancellations.
- It does not justify a physical delta_0 invariant, arbitrary affine/phase
  normalizers with nonzero constant term, or a future word with residual
  adapters. The moving-frame convention and exact unchanged normalizers are
  essential premises.
- The Laurent outer boundary substitutions, selected input norms, exact pole
  coefficients, and inference from local error tolerances to a paid precision
  tariff belong to the separate boundary/census audit. This review does not
  infer them solely from a logical invariant.
- This is an independent agent/source audit within the same author process,
  not independent human or proof-kernel acceptance. No new bound is claimed.

Replay:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B check_invariance.py \
  --source /path/to/PR4610-ACTUAL-WORD.json.gz --out /fresh/INVARIANCE.json
```
