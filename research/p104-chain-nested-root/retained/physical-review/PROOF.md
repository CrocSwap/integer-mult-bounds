# Finite physical and invoice argument

This is an independent application audit of the literal #6726 source at `435bbe91fb28cb1d7a569ca70c6c4e9eb302d486`, not a new construction or an unconditional integer-multiplication theorem. The implementation is `verify.py`; its data inputs are frozen and authenticated. No author implementation is executed by this verifier.

## 1. Exact phase equality from parity evaluations

Let `T_a` be translation by a binary address vector `a` and let

`G_a = ((1+i)/2) I + ((1-i)/2) T_a`.

On a binary Fourier character indexed by `z`, this Gaussian has eigenvalue `i^(a·z mod 2)`. A signed product of these commuting Gaussians is therefore described by

`f(z) = Σ_a c_a (a·z mod 2) mod 4`.

Every factor equals one at `z=0`. Thus there is no undetected global scalar phase in this representation. For Boolean coordinates,

`a·z mod 2 = Σ_{i∈a} z_i − 2 Σ_{i<j, i,j∈a} z_i z_j (mod 4)`.

All terms of degree three and higher have coefficients divisible by four. Consequently, a difference of two such phases is completely determined by its values at single-coordinate and two-coordinate frequencies. The verifier evaluates the parity expression directly at those points. It does not import or reconstruct the author's linear/quadratic coefficient-array algorithm.

A phase difference is an ordinary translation precisely when every singleton value is even and every pair value is the sum of its singleton values modulo four. The translation mask has bit `i` set exactly when the singleton value is two. A zero mask then certifies equality on **every** Fourier character of the finite carrier. This is an exact finite identity, not numerical sampling.

## 2. Independently constructed native-to-fresh route

For each retained central port `q`, the supplied eight vectors `b_1,...,b_8` and `q` form an orthonormal basis of the original nine-dimensional binary space. The verifier checks every Gram entry, every vector range, and the odd norm of `q`.

At stage `s`, let `f_1,...,f_8` be the new coordinate axes of that stage. The new route exchanges the coordinates along `b_i` and `f_i`, keeps `q`, and keeps every other coordinate. The implementation obtains a vector's old `b_i` coordinates by dot products, inserts its fresh coordinates along the corresponding old vectors, and retains its `q` component. This coordinate-decomposition construction is independent of the source's transvection/swap-vector formula.

The complete affected 17-axis map is checked to be orthogonal and involutive; every other axis is fixed by construction. Its action fixes `q`. This establishes the route, its inverse and the fixed 17-axis support bound.

For every one of the 18 literal LOCAL events and 104 retained ports, the verifier builds four requested contacts: both entries to the native supplier and both exits back to the fresh-stage caller charts. Applying the route to the incoming phase and comparing with the outgoing phase determines the ordinary translation. Both forward and inverse phase identities are checked using the preceding parity lemma. The translation and inverse translation each have support at most 17.

There are 18 × 104 × 4 = 7,488 contacts. All reconstructed translations are nonzero. The independent serialized contact payload has exactly the digest recorded in the author's receipt. Digest agreement is a cross-check after independent reconstruction, not the mathematical phase test.

Write `D_s` for the product of the eight positive Gaussian factors on the fresh stage block. The checked raw diagonal ratios on both native main coordinates are `D_s`; the cross ratio is `D_s Q^-1`, including its absolute phase. Spectators are retained in the contact expressions and cancel only through actual equality. Each stage is checked to occur once in the literal chronological sequence 1 through 18.

## 3. Native scalar word, chronological charts and helper ranks

The source native word has 771 public inputs and 29 owned labels. The checker starts each public scalar row as an independent rational basis vector. It executes every ADD, SCALE and COPY with exact `Fraction` arithmetic, tracks every current frame, and permits scalar interactions only between equal current charts. A MOVE changes the field's chart without changing its chart-relative scalar row.

Each frame's listed axes are verified to be independent in the nine-dimensional binary space. The checker explicitly constructs its finite binary span. Every paid MOVE must start at the field's current frame and have strict subspace containment in the declared forward or backward direction. Its paid rank is the difference of the two span dimensions. No histogram or price constant is used to determine these ranks.

INIT requires an inactive owned label and starts a new zero row. COPY requires a currently live owned destination whose actual scalar row is zero. CLEAR requires a live owned label at its current chart, then ends that lifetime. Erasure is an explicit inherited assumption: this audit checks legal chronological use of that contract and does not prove its physical realization. All 47 lifetimes end; the maximum live count is 14.

Every public endpoint row is then compared with the native interface: identity on each helper and main X field, and the prescribed X-to-Y shear on every one of the 104 main pairs. These sparse rational row equalities cover all 771 independent public inputs. They do not assert arbitrary initial values in the owned zero storage.

The first and second main coordinate sets are disjoint. Their input charts are the specified Q/I charts. X's final chart is the full nine-axis frame; Y's final frame is a rank-eight subspace orthogonal to its particular q. The retained native physical adapter theorem identifies these chart operators, with absolute phases, with the raw interface used in Section 2. That general physical adapter theorem is not inferred merely from the scalar rows or frame ranks.

Each of the other 563 public fields has a strict nested input-to-output frame pair. The rank difference gives its normalized positive Gaussian helper job under the retained whole-job adapter contract. Independently recounted local histograms are:

| Rank | Paid | Productive helpers |
| ---: | ---: | ---: |
| 1 | 2231 | 14 |
| 2 | 454 | 8 |
| 3 | 490 | 4 |
| 4 | 109 | 108 |
| 5 | 152 | 16 |
| 6 | 8 | 3 |
| 7 | 9 | 9 |
| 8 | 1 | 40 |
| 9 | 0 | 361 |

The 3,454 paid requests come directly from the 3,454 literal MOVE events. No new dense-column proof of each native paid physical map or helper normalizer is claimed.

## 4. Independent fields, ordinary normalizers and retention

The complete caller receives 34 arbitrary main inputs at each of the 104 ports. Each LOCAL invocation additionally receives 563 distinct arbitrary helper inputs. The allocation uses distinct names `(invocation, helper label)`; no such name can equal a main-field name or a name from another invocation. Each local public interface is injective. Thus there are exactly

`34·104 + 18·563 = 3536 + 10134 = 13670`

independent productive fields.

All 29 native owned labels receive reserved nonpublic slots. Those slots may be reused only because each atomic LOCAL invocation returns with all its owned lifetimes closed. The one separate thin-query scratch slot is uncredited. Each query copies the needed value into owned zero, applies its charged rank-one Gaussian, adds the result into the destination, and clears the scratch under the retained owned-erasure contract. Native and query scratch do not alias public inputs.

The first retirement witness records handoff 166 for the intermediate word. The second retirement prepends three gates, giving actual final-word handoff 169. The second actual handoff is 401. The checker locates each complete cut basis directly after its paid IDLE_ONE fragment and requires the fresh field's first use to be the next gate. It checks that the fresh input has no earlier use and the retired output has no later use in the final 606-event word. This proves chronological availability and retention relative to the supplied scalar retirement identities. It does not reprove those identities; the full symbolic caller proof is the separate exact-source obligation checked by #6733.

For a total central operator `Q` with `Q^4=I`, the ordinary normalization is

`λ_± = ((1±i)/2) I + ((1∓i)/2) Q²`.

The checker evaluates all four central characters, checks `λ_+λ_-=I` and `(λ_+Q^-1)²=I`, and charges all 100 literal normalizations. These scalar polynomials act on the **total** central operator. They must remain outside tensor powers: when two factor characters are both `i`, total Q is `-1` and its λ is `+1`, while tensoring the two individual λ values incorrectly gives `-1`. The included exact two-factor control records this discrepancy.

## 5. Physical endpoint and whole-idle invoice

Each literal declared main endpoint has exponent `q^p` with `p∈{-1,0,1}`, no stage-zero factor, and a set of distinct fresh stage blocks. The positively normalized Gaussian uses the selected eight-axis blocks and, exactly when `p≠0`, the central q axis. Their complete Gram matrix is the identity. The parity evaluator checks the exact required endpoint translation: q for `p=-1` and zero otherwise. There are 3,328 nonzero main-output translations; all 3,536 output fields receive budgeted normalizers/routes.

Every IDLE or IDLE_ONE event is expanded into its literal owner/port jobs. It receives all eight axes of every declared stage, with no repeated stage or repeated axis. Since this caller has only positive fresh stages in its idles, these are positive canonical Gaussian products with no hidden initial-block phase. There are 3,120 such jobs, of ranks 8, 16, 32 and 40. A two-owner IDLE is two paid jobs for each port, not one.

To convert a job on scattered canonical axes into the standard rank-r Gaussian, pair the selected axes outside the first r coordinates with the missing coordinates inside the first r. Exchanging each pair gives an explicit involutive permutation taking the selected axis set onto the canonical set. At most r two-axis exchanges suffice. The verifier constructs and checks the actual exchange list. It charges both the input and output permutations for every paid whole idle, rather than treating these adapters as free.

For each main job carrying q, an additional orthogonal map supported on the original nine coordinates sends q to coordinate zero and its checked orthogonal basis to coordinates one through eight. The selected fresh axes are then canonicalized by the explicit exchanges just described. Both boundary q-basis maps are charged, along with the required output phase translation. Both canonicalizing maps are charged even when a more permissive target interface would avoid them. Thin queries similarly receive two nine-axis q-basis conversions and the translation required for an inverse Gaussian. These address permutations and translations are ordinary maps; the paid Gaussian rank is unchanged.

The input adapter of a fresh field is scheduled immediately before that field's first use, rather than before the completed prefix. Since the prefix never uses that arbitrary field, this realizes the independently normalized job while preserving the checked handoff chronology. A retired output's final normalizer can be deferred to the final output boundary, after which it is retained unchanged. These are explicitly charged boundary adapters around the pinned 606-gate logical caller, not edits to its frozen bytes.

The complete paid ledger adds one independently recounted native profile for each of 18 LOCAL events, one rank-one job at each port for each of 15 QUERY events, and every explicit whole idle. Productive credit adds each physical main target and each distinctly allocated native helper job. The exact resulting histograms are in RESULT.json. They contain 66,852 paid requests and 13,670 productive targets. Their rank masses are 178,080 and 178,840. Both counts and both full histograms are checked, not just the surplus 760.

The two fragment replacements, each at 104 ports, change a target 41 into 32+9 and a paid job 40 into 32+8. This gives the familiar local signed change `208((H9-H8)-(H41-H40))`. The current audit establishes the complete finite invoice on which that comparison rests; it does not run a new root search or claim a new κ.

## 6. Ordinary costs and explicit retained rates

An independently recounted conservative binary-Horner scalar realization of the native word costs at most 283,608 real scalar units. This exceeds the source's optimized 137,990 allowance, but still fits the stated per-call envelope. The route census charges each native paid map, twice each of 563 helpers for whole-job normalizers, 208 main adapters, 416 caller contacts and four passes for each of 47 owned lifetimes. At the retained fixed-map rate of 1,000 units, this is 5,392,000. The resulting independently recounted local bound is 5,675,608 < 10⁷. These are sufficient upper bounds, not exact minimum operation counts.

Every literal caller coefficient is checked as a nonzero dyadic, and SCALE is a dyadic unit. Direct binary multiplication, component additions, halvings, signs, swaps and λ normalizations fit a 32-unit per-gate bound. Scanning all 34 fields for all 606 gates at all 104 ports gives the deliberately conservative 68,570,112 caller allowance. The 15 thin queries contribute 24,960 scalar units. The ordinary arithmetic part of all 3,536 main output normalizers contributes 91,936 units.

The independently generated canonical-job adapter inventory is:

| Ordinary map | Count |
| --- | ---: |
| Main input/output two-axis exchanges | 144,768 |
| Main input/output nine-axis q-basis maps | 6,656 |
| Main endpoint phase translations | 3,328 |
| Whole-idle input/output two-axis exchanges | 127,296 |
| Thin-query input/output nine-axis q-basis maps | 3,120 |
| Thin-query phase translations | 1,560 |

There are 286,728 elementary maps, each supported on at most nine axes. At 1,000 units each they contribute 286,728,000. Thus the complete sufficient ordinary bound is

`18·10⁷ + 68570112 + 24960 + 91936 + 286728000 = 535415008 < 10⁹`.

The 1,000-unit assumption is the retained rate for a fixed native whole-job map or a map on at most 17 specified axes, with other coordinates carried as spectators. It is **not** asserted for an arbitrary map acting on all 153 axes. The new full-carrier main/idle maps are explicitly decomposed into the two-axis exchanges above, and the rate is charged for each exchange separately. The extra q-basis and phase maps use at most nine axes. Native contacts continue to satisfy their independently checked 17-axis support bound. Applicability of the retained physical movement/tape rate to these fixed embedded elementary maps remains part of the stated framework contract.

This recount includes all added input/cut/inverse bases, both fresh outputs, both boundaries of every whole idle, both boundaries of each canonical main target, and the thin-query adapters. The rate and native physical realization remain framework contracts; independently counting their uses does not prove those rates from machine instructions. All added address permutations and translations have coordinate sup norm one. With every Gaussian rank charged, the usual conservative scalar/paid-mass envelope remains `2^(10⁹+178080 f)`, subject to the retained local physical precision/tape conventions. This audit does not establish the rounded machine implementation or uniform stock theorem.

## 7. Negative controls and limits

The verifier actually runs mutants that omit a physical translation, alias native helpers between calls, delete a paid whole idle, omit a whole-idle adapter, claim an unearned central target on fresh field 33, place the second cut too early, omit its λ normalizer, corrupt a native chronological source chart, alter paid rank mass while keeping request count, and alter the histogram while preserving both count and mass. Each is rejected by the relevant phase, ownership, chronology or complete-invoice condition. Source-contract mutants do not replace the full scalar-caller theorem.

The remaining conditional assumptions are exactly `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, and `analytic_recovery`. In particular, complete finite contact identities are not an all-column implementation theorem, and a correct finite invoice is not compiler or outer admission. This audit supplies new independent evidence for the stated finite application obligations only.

Independent audit: Jerry Chen (@CubeJerry), with substantial OpenAI assistance, Apache-2.0. #6726's zxv construction and all source-specific predecessor notices and authors retain their credit.
