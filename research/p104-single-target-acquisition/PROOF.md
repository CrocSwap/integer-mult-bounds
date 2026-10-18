# Single-target acquisition theorem

Let the original word be the pinned PR1972 `LOWRANK-WITNESS.json`, retained
through PR1991. Let `G[t,s]` be the ordinary Gram matrix of its 104 root lines,
with squared norm two, and let `C = I-G/2`. Work over the rationals (the same
argument holds over characteristic-zero fields). The original channel adds
`(Gx)_t/2` to each target and restores its original dirty helpers.

Use the exact correction model stated in the README. The target index is fixed
for each theorem instance. A new helper lifetime starts with independent dirt
at ZERO, follows an increasing chain of binary frames, and ends restored at
FULL. Coefficients are input-independent. Only original X values may introduce
source information into new helpers; original helper/private/target reads,
writable original X storage, new resets and descending frames are excluded.
All original events and frame paths remain unchanged.

**Theorem.** In this model, the minimum lifetime count `L_t` is:

| `L_t` | Target indices `t` |
| ---: | --- |
| 37 | 53 |
| 38 | 13, 37, 45, 58 |
| 39 | 2, 42, 70, 73, 87 |
| 40 | 5, 8, 11, 15, 23, 40, 48, 76, 80, 82, 84, 100 |
| 41 | 4, 20 |
| 47 | 17, 18, 25, 28, 30, 32, 34, 39, 50, 51, 56, 59, 61, 63, 65, 68, 71, 78, 89, 91, 94, 96, 98, 102 |
| 48 | 0, 1, 3, 6, 7, 9, 10, 12, 14, 16, 19, 21, 22, 24, 26, 27, 29, 31, 33, 35, 36, 38, 41, 43, 44, 46, 47, 49, 52, 54, 55, 57, 60, 62, 64, 66, 67, 69, 72, 74, 75, 77, 79, 81, 83, 85, 86, 88, 90, 92, 93, 95, 97, 99, 101, 103 |

This is 104 separate optimality statements. It is not an optimality statement
for correcting all targets jointly. Y0=48 and Y2=39 are established predecessor
results, retained as controls and credited to PR2393 and PR2496.

## 1. Source binding and complete availability sets

Generate the 120 positive E8 root lines in doubled coordinates and remove the
two specified eight-frames `F0` and `C` from `P104-FIXTURE.json`. Lexicographic
ordering gives roots `r_t`. The original half-Gram coefficient is
`dot(r_t,r_s)/8`. The verifier checks the original channel endpoint through the
full word in every instance, so it also binds this ordering to the source names.
Every correction row has exactly 48 nonzero coefficients.

A cut is the number of completed original events, from 0 through 4058. If a
source transport is original event `i`, its old frame is present at cut `i`
and the new frame first appears at cut `i+1`. Each source is immutable in logical
coordinates; source transports only increase frames. Target frames also only
increase, from ZERO to the eight-dimensional endpoint `H_t`. The original word
does not read any Y register. These premises are checked from all original
operations, not inferred from the source's final frame alone.

For each required source `s`, let `A_t(s)` be **all** frames that X_s occupies
at some cut and that are contained in `H_t`. These families are reconstructed
from every source episode. Time is ignored only in the lower-bound comparison;
the upper constructions must use actual chronological cuts.

## 2. An antichain of source families forces distinct lifetimes

Choose required sources `s_1,...,s_k` such that, for every distinct `i,j`, every
`U` in `A_t(s_i)` and every `V` in `A_t(s_j)` are incomparable by inclusion.
The certificate's `antichain_sources` lists such a set, and the verifier checks
all episode-pair comparisons, including later source frames.

Fix a required source `s`. Its correction coefficient `C[t,s]` is nonzero.
By linearity, expand that coefficient into directed causal paths through the
extra additions. At least one nonzero path must start with an original-X_s
read into a new helper and end at an addition into Y_t. Otherwise the
coefficient cannot change from the original `G[t,s]/2` to `delta[t,s]`.
This conclusion permits any number of repeated reads and cancellations.

Along that path, helper-to-helper additions preserve the frame and helper
transports increase it. The final target contact occurs inside `H_t`.
Consequently the original-X_s read occurs at a frame in `A_t(s)`.
Assign to `s` the helper lifetime performing that read on the chosen path.

If two antichain sources were assigned the same lifetime, that lifetime would
have occupied two incomparable frames. Its frames form an increasing chain,
so this is impossible. The assignment is injective and there must be at least
`k` new lifetimes. Arbitrary helper mixing and extra source reads cannot avoid
this argument. It is an arbitrary-length causal proof with a finite geometric
certificate, not an exhaustive bound on short circuits.

For each target the stored antichain has the size stated in the table. A useful
failure control uses sources X0 and X20 for Y2: their initial lines differ, but
later allowed frames are comparable. Checking initial lines alone would not
certify the claimed source-family antichain.

## 3. Matching chronological upper constructions

For each target, `paths` partitions its 48 required sources into exactly `L_t`
ordered paths. Each entry records a source index, an original cut, and the
source's actual frame basis. Along a path, cuts do not decrease and frames are
nested increasingly inside `H_t`. These facts are checked independently of the
search that proposed the certificate.

Give each path a new helper with arbitrary initial logical value `d`:

1. At cut 0, subtract `d` from Y_t while both are in ZERO.
2. At the recorded cuts, transport the helper up to each source's current frame
   and add `C[t,s] X_s`. Its logical value is now its original dirt plus the
   acquired partial correction.
3. At cut 4058, move the helper to `H_t` and add it into Y_t. Its initial dirt
   cancels the subtraction in step 1.
4. Move the helper to FULL and subtract every acquired `C[t,s] X_s`. All original
   X sources are at FULL by this cut. The helper returns to `d`.

Every transport is nested. Every addition has equal source/destination frames.
The original word never reads Y_t and no other original logical value is changed
by the insertions, so the old computation remains valid. The total new target
increment is exactly row t of `C x`. Thus Y_t becomes `y_t+x_t`, other targets
retain their old updates, and all old and new dirty inputs are restored in their
prescribed final frames. The eight original private COPY/discard lifetimes are
retained, including their inherited nonzero-discard semantics.

The primary checker explicitly interleaves these insertions with every original
event and replays every input column, rather than relying only on this
composition argument. A second implementation uses dense fixed-grid integer
rows; every division is checked exact.

### The new 37-lifetime endpoint

For Y53 the 36 isolated required source families each use one helper. The
remaining twelve sources fit one monotone path:

| Cut | Sources acquired, with correction coefficients | Frame dimension |
| ---: | --- | ---: |
| 0 | `-X81/2` | 1 |
| 542 | `+X76/2` | 4 |
| 711 | `(+X11-X16+X41-X46)/2` | 5 |
| 830 | `(+X10-X17-X47-X54+X74-X82)/2` | 6 |

Delivery and cleanup at cut 4058 then use dimensions 8 and 9. The one helper's
rank steps are 1,3,1,1,2,1. The other 36 helpers use 1,7,1. Hence the combined
profile is `76 H1 + H2 + H3 + 36 H7`, with 114 transports and rank mass 333.
The 37-element all-episode antichain proves that fewer lifetimes are impossible
within the model.

## 4. Accounting and limits

A ZERO-to-FULL increasing path telescopes to rank mass nine when a nested
transport costs its dimension gap. Thus the sharp lifetime minimum implies the
sharp added boundary-rank mass `9 L_t` under this tariff and exit contract.
The upper construction uses 48 acquisitions, 48 cleanup additions, `L_t` dirt
subtractions and `L_t` deliveries: `96 + 2 L_t` scalar ADDs. The ADD counts and
individual rank histograms are attainable bills, not claimed optimal.

This does not prove a recursive excess-cost or native implementation optimum.
The package supplies logical/frame words, not new native Clifford recipes,
physical scalar/address lowering, owners, idle/residual children, precision,
backward admission or an all-size compiler. Changed source paths, original-helper
reads, writable original storage, target feedback, descending/resettable helpers
or joint targets change the premises. In particular, sharing can reuse a helper
across target rows, so **summing this table does not lower-bound a joint network**.

## 5. How certificates were found

For each target, join two required sources when some allowed frames are
comparable. The finite input has 56 targets with 48 singleton components,
24 targets with one size-two component and 46 singletons, and 24 targets with
one size-twelve component and 36 singletons. The search enumerates independent
sets only inside components of size at most twelve.

For the upper witness it stores the earliest reachable time for each
`(acquired subset, current frame)`, then partitions the component into feasible
paths. An earlier state at the same frame can wait until any later state, so
this dominance is safe. Search completeness is not needed for acceptance:
explicit legal paths give the upper bound, and the independently checked
antichain gives the matching lower bound. No solver or numerical tolerance is
part of the certificate.
