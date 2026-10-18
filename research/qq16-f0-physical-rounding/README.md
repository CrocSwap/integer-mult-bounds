# Deterministic rounding in the native QQ16 F0 producer

The concrete scalar failure in Arham Tahir's [PR3036](https://github.com/CrocSwap/integer-mult-bounds/pull/3036),
head `3717c1e684553c57bc73300410df65438a9ef095`, survives the actual physical
native frame and residual adapters **in the specified mixed arithmetic model**.
This closes its physical binding gap for four finite precisions. It does not
implement rounded native-child interiors or admit a supplier. No new kappa is
claimed.

At `p = 8, 24, 53, 113`, set physical `L112 = ONE`,
`L224 = 2^(p+12) ONE`, and all other fields zero. `ONE` is the real constant
512-component vector, uniform across cover owners. Execute the literal local
`F_0` program, including every native child and endpoint/residual conversion.
Each real and imaginary scalar ADD result is rounded to a binary significand
of precision p, nearest with ties to even and unbounded exponent. Completed
native recipes, their internal arithmetic, conversions, SCALEs and owned
CLEARs are exact. Every scalar coefficient product in the four rounded
executions is separately checked to be exactly representable at p, so a
separate correctly rounded multiplication gives that same product here.

Exactly two scalar instructions round; each gives error `-ONE/2`:

| Zero-based event | Literal instruction | Exact real component | Rounded component |
| --- | --- | --- | --- |
| 3887 | `L112 += -L224/2` | `(1-2^(p+12))/2` | `-2^(p+11)` |
| 4060 | `L139 += -L224/2` | `(1-2^(p+12))/2` | `-2^(p+11)` |

The exact execution returns the chosen input unchanged. The rounded physical
endpoint differs in exactly these five data fields:

```
L112:             -ONE
L114,L137,L190,L211: -ONE/2
```

All 480 physical helper values return exactly to their chosen entrance values;
all eight private fields return zero. This is exact amplitude equality on the
stated family, not a claim about arbitrary dirty inputs or IEEE signed-zero,
NaN or storage-bit representations. The largest error norm equals the original
data norm `H=sqrt(512)`, hence the relative error is exactly one. A separate
`-ONE/32` control has squared input and error norms `1/2`; dyadic scaling
therefore supplies a witness with `H<=1`. Unit irrational normalization is not
assumed to commute with binary rounding.

## Why the physical binding is substantive

[Tekalign's PR3017](https://github.com/CrocSwap/integer-mult-bounds/pull/3017),
head `0f493f4c264fbc70ee14364b68af260d858c143c`, binds an earlier **permitted**
fault at a different instruction and dirty register. It deliberately does not
claim a concrete rounding failure. PR3036 supplies actual scalar rounding but
omits the non-scalar events. Neither predecessor establishes this implication.
Their native conventions, scalar witness and general frame argument are
credited rather than claimed as new.

The new verifier executes every event directly on exact Gaussian-dyadic
vectors. It does not replace native maps with frame labels or scalar
projection. Each of the four cases checks all 364,544 complex endpoint
amplitudes against the stated exact result. `RESULT.json` records the full
event digest, exact local rounding values, every nonzero output-error vector
histogram and canonical endpoint digests. `vendor/pr3017/native.py` retains
Tekalign's exact primitive evaluator byte-for-byte, with its source hash and
head in `SOURCES.json`; the new execution/rounding driver is separate. This is
executable reuse, not a second independent Clifford implementation.

A separate internal rounded-networks specialist rederived the frame argument,
inspected the p=53 literal result, and checked the following finite native
facts with the retained evaluator. Its full source-bound report is local-only and preserved outside the checkout;
public evidence is the literal verifier, receipt, controls and argument below.
No human or formal-kernel review is claimed.

1. L224 has ordinary endpoint frames `(0,1)` and no residual wrapper. Both
   marked ADDs use frame zero, whose physical vector is exactly `ONE`.
2. Every real or imaginary component of the 1,004 canonical vectors
   `v_f=T_f ONE` is in `{0,1,-1,2,-2}`. For unbounded-exponent nearest-even
   rounding, sign symmetry and power-of-two homogeneity give
   `RN_p(a v_f)=RN_p(a) v_f` for real a. This is a written homogeneity lemma
   combined with a finite exact frame fact; frames need not be constant.
3. Exact scalar trajectories from unit L112, unit L224 and unit post-ADD
   errors at each marked site are zero at all residual boundaries: 1,920
   values in total. Those residual monomials act on zero, so their two gauges
   need not coincide. The exact used child and endpoint frame-vector checks
   in the retained native binding also pass.
4. A unit post-3887 error reaches `+1` in L112,L114,L137,L139. A unit
   post-4060 error reaches `+1` in L112,L190,L211 and `-1` in L139. Multiplying
   both by `-1/2` gives the five final errors, with L139 cancelling.

At each marked cut, the exact component is `-2^(p+11)+1/2`. It is strictly
closer to `-2^(p+11)` than to the next representable value toward zero, which
is `2^11` away. This decision is not a tie. The literal four-case inventory,
not this local calculation alone, establishes that no other ADD rounds.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -Werror -I -B scripts/research_package.py \
  --package research/qq16-f0-physical-rounding
```

The main verifier is read-only and compares the complete canonical receipt;
`--write PATH` exclusively creates an absent receipt. Eight behavioral groups
check an independent nearest-number oracle (2,575 integer decisions), native
line/global-phase conventions, all canonical frames, clean helpers, wider
precision on the **same** dirty input, separate rounding-site effects, dyadic
sign/scale covariance, an occupied nonconstant exit-adapter mutation, and
source/JSON fail-closed behavior. The wider control uses 65 bits on the
original `2^65` dirty input; it is an escape witness, not a minimum precision
for arbitrary inputs. Assertions used for scientific acceptance remain active
under optimization.

The immutable scientific inputs are the current joint-query certificate and
three authenticated members of the selected replay archive. They are never
modified. No selected cold replay is needed for this unchanged selected
construction; it is not claimed here.

## Recursive-cost relevance and limits

The larger mechanism is the zero-retention QQ16 interface: it changes query
retention and the paid producer/decoder structure. Nick Petalas's
[PR2965 output-error bridge](../qq16-producer-defect-transfer/README.md) assumes
completed producer tolerances. This witness prevents replacing its F0 premise
by the stated p-bit scalar arithmetic while leaving dirty magnitudes arbitrary,
even when completed native operations are exact and all helpers return.
It does not contradict that conditional theorem.

Increasing p while also increasing the dirty value is four separate finite
fixtures. This package proves no all-p, all-tensor-depth, arbitrary-input,
uniform dirty-range or sufficient guard-bit theorem. The domain is one tensor
factor, nine active axes, 512 payload coordinates and the four named p values,
with the inherited local full-cover semantics and uniform owner inputs.

Exact completed native operations are a material premise. Native internal
rounding, finite exponents/overflow, recursive-child accuracy, physical bit
widths, source access, hosting/movement, storage, all-size compilation, full
B1/decoder consumption and F17 endpoint use remain unresolved. No Boolean or
direct vector work is assigned the original recursive tariff. There is no
favorable complete recursive invoice and no scalar saving, new supplier,
selected-frontier change or new kappa. Family decision: narrow and stop at this
producer obligation; no further search or construction expansion is implied.

## Open next questions

Can a finite native F0 implementation exclude these deterministic losses at
its actual dirty range and paid precision? Pin the input grid and dirty bound,
then specify the native-internal rounding and prove exactness or error at
every occupied cut. Next charge that realization, storage, movement, cleanup
and the F17 consumer together. Exact-grid arithmetic is a legitimate escape;
its complete recursive price remains the blocker. `TASK.json` preserves the
structured handoff.

## Sources, attribution and engineering scope

Scientific base: `d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.
The source manifest pins the selected record and task catalogue as provenance,
the two live inputs, and the exact retained evaluator source. The canonical
[claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2727#discussioncomment-18983447)
records overlap and lifecycle. Metadata coverage is non-atomic and does not
prove novelty or cover unpublished work.

New physical rounding driver, integration and checks by Ross Richardson with
substantial OpenAI Codex assistance, including a separate internal
rounded-networks mathematical reviewer. Credit Arham Tahir/PR3036 for the
concrete scalar witness and PR2995 for the earlier fault, Tekalign/PR3017 for
the exact vector evaluator and native binding, Nick Petalas/PR2965 for the
producer-accuracy handoff, Ali Romman/QQ16, Sagar Thakrar, DLamdata, ywz65,
starship-s, Douglas Colkitt and the retained supplier/native lineage. All new
work is Apache-2.0; the evaluator's original header is preserved.

Verification uses managed Python integers/collections and bounded dynamic
allocation; it is not a fixed-tape machine realization. It traverses 26,099
events, 712 fields and 512 coordinates per execution; integer rounding cache
is capped at 32,768 entries. Tests traverse 1,004 frames and small finite
number systems. Immutable archive containers and decompressed selected members
are hash authenticated; declared member payloads are capped at 12 MB. Python
library allocation overhead is not profiled. Warning-as-error compilation and
normal/optimized runtime checks are used; no static type or proof-assistant
claim is made.
