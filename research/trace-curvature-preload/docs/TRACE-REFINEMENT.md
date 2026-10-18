# Frame-sensitive trace refinement and the preload60 construction

## Sufficient meta-theorem

Let a finite reversible scalar program act on registers indexed by I over a field K. A scalar addition is T(t,s,q)=I+q e_t e_s^T, with t != s. Each register has an explicit initial frame, an explicit terminal frame, and a monotone chain of finite subspaces at its actual uses. Certain observation checkpoints (for example retained totals at a scatter) are fixed.

Construct another program by the following certified operations:

1. Factor a multi-source addition into elementary additions with the same destination and unchanged coefficients.
2. Permute elementary additions only through explicitly checked commuting gates, without crossing protected observation checkpoints.
3. Assign a new common frame to each relocated addition. Require that every touched register's predecessor frame is contained in it and that it is contained in that register's successor frame, including fixed initial, terminal and observation frames.
4. Rebuild the inverse background cleanup literally. Recompute every actual frame transition, retained-copy rank, scalar prefix bound and finite realization invoice.

Then the new scalar program has exactly the same complete arbitrary-input endpoint. Its framed program satisfies the retained native frame-realization interface, and its exact recursive profile is the profile recomputed from those new chains, together with all retained-copy children. If the entrance and terminal signatures stay fixed, every old whole-owner allocation remains usable with unchanged residual-width and idle-remainder accounting. The changed physical finite realization still requires its actual phase/compiler and prefix checks; the theorem does not make those checks or inherited all-size hypotheses disappear.

This is a calculus of representations of the SAME scalar word: it searches the trace-equivalence class and then selects a different legal frame labeling. A fixed event-order frame optimizer cannot expose every member of that class. A scalar-only optimizer cannot see the cost of its frame chains. Their joint finite certificate is the sufficient object.

## Algebraic proof

For t distinct from all s_i, the elementary additions to destination t commute, since e_(s_i)^T e_t=0. Hence

    I + sum_i q_i e_t e_(s_i)^T = product_i T(t,s_i,q_i).

For distinct-source/destination elementary additions T(t,s,q) and T(u,v,r), the sufficient commuting condition is t != v and u != s. Expanding both products gives the same identity, two linear terms and zero cross terms. (There are further special commuting cases; they are not needed.) A scale on register u commutes with T(t,s,q) when u is neither t nor s.

Every allowed adjacent exchange therefore preserves the entire linear operator. Induction on the explicit exchange list proves equality of the reordered body. It holds on arbitrary source, target and dirty-helper columns, not merely clean inputs. A word can be moved through a whole interval if it commutes with every gate crossed. Protected checkpoints are preserved because no move crosses them.

If background updates do not read target registers, the background transformation is independent of targets. Reversing the order and inverting each actual new background gate gives its exact inverse, restoring all source/helper inputs. For an addition this negates its coefficient; over F2 the coefficient is unchanged. The body's target output is unchanged by the trace identity. Thus the full dirty-register endpoint is unchanged. Existing compensation can be retained because the body map itself, on every column, is unchanged.

At a relocated instruction, the explicit predecessor/common/successor inclusions establish native frame legality. All other chains retain their previous inclusions. Applying the existing compiler interface to the actual changed word gives the same final labeled endpoint, with exactly the newly listed transition ranks. This last statement is conditional on that pre-existing all-size compiler interface; finite column replay is not an independent proof of the all-size interface.

## Critical pair: splitting plus scheduling plus reframing

Consider a two-source cell h += x+y first formed at a rank2 frame containing the rank1 source frames. Suppose its x addition commutes through the entire prefix, h initially has frame0, and the prefix does not observe h. Factor the gate into h += x followed by h += y. Move h += x to the beginning and perform it at x's rank1 frame. The later h += y remains at the original rank2 frame.

The scalar map is identical. In the actual selected instance, the helper's former rank2 climb splits into two rank1 climbs. Meanwhile x no longer needs a formerly unique intermediate rank2 use between rank1 and rank4: its two climbs of ranks1 and2 coalesce into a rank3 climb. Therefore the net child-profile change is

    +delta1 - 2 delta2 + delta3.

This is why neither a fixed-position scalar rewrite nor a fixed-order frame-coalescing pass alone finds the gain. The seam is moved before the frame assignment is simplified. The general theorem does not assume this particular delta: it always recomputes the actual changed chains.

For every 0<a<1, strict concavity of r^a gives

    1^a + 3^a < 2*2^a.

The delta has zero rank mass, so it strictly reduces the recurrence moment for every saving exponent 0<b<1 when a=1-b. The theorem is sufficient for strict moment improvement in every compatible context with unchanged residual signatures. It says nothing about a numerical bound until the changed finite invoice and outer assembly pass.

## Batch compatibility rather than a hidden optimizer

In the selected 60 cells, each destination is a different helper, each preloaded source is an original source register, and no helper destination is itself a preloaded source. The 60 new prefix additions therefore commute with each other. For each chosen cell, the constructor explicitly verifies that no preceding old gate reads its helper destination or writes its preloaded source. Consequently its elementary addition commutes across that entire old prefix.

The constructor only chooses gates with exactly two original sources. It checks the source pin, emits all 60 rank1 preloads in the original cell order, replaces each old grouped cell by its remaining term, and regenerates C as the literal inverse of the changed A. B, D, scatter, start and final frames are unchanged. No new frame type, extra helper, non-dyadic coefficient, oracle, probabilistic claim or allocation splitter is introduced.

## Actual finite witness

Input is the pinned PR510 R480 bit word, canonical JSON SHA256

    8639e22008c24a5690dd250eba702fe5fca85ddd036dcbec20baba77b7e213ba.

Portable builder: build_preload60.py --input WORD --out NEWDIR.

It independently checks all720 arbitrary formal columns over F2, exact rational frame-subspace incidence, literal inverse cleanup, all nine retained-total ranks and all unchanged interface fields. The changed canonical word SHA256 is

    cb9c80a62d75c5dfc8bc8933d4b1d44e6b6b816db47c2444bc2dbba6b3a6e454.

The local chain profile changes from {1:1200,2:1440,4:180,6:120} to

    {1:1260,2:1320,3:60,4:180,6:120}.

The nine retained rank8 copy children are unchanged and MUST also be paid. The complete local profile is

    {1:1260,2:1320,3:60,4:180,6:120,8:9}.

All480 helper entrance widths stay8. The current public controller uses nine stages and32 replicas, hence288 calls. Its global delta is +17280 delta1 -34560 delta2 +17280 delta3, with every original idle remainder retained. The resource lane exact moment engine certified c=0.001589735702947998836661 under the existing bad-case envelope. That is a provisional supplier price, subject to the changed official physical/prefix/compiler invoice; it is not itself an achieved outer kappa.

## Bounded discovery and failure actions

The first native screen on the previous complex word tested1,237,484 insertion positions, including1,154,361 legal ones, and found no strict gain. Switching to the actually binding bit supplier tested1,431,669 positions,1,388,956 legal ones, with68,400 positive nominations. The explicit60-move family above was then independently constructed and replayed over exact arithmetic.

A second native screen on that new word tested1,451,628 positions,1,386,258 legal ones, and found no further single-move improvement. This is a bounded single-gate scheduling result, not a universal optimality theorem. The modular rank screen only nominated candidates; exact rational ranks in the constructor establish the submitted witness. No unverified modular result contributes to the numerical claim.

## Sources and novelty scope

Mathlib.LinearAlgebra.Transvection.Basic supplies exactly the structural factorization pattern: transvection.comp_of_right_eq expresses composition with a common displacement vector as addition of linear forms; comp_of_left_eq is the dual common-form rule. These formal source statements were actually read. The DAG's source search located transvection commutation and matrix-unit composition results; source-only hits were not treated as newly checked typed ports.

OpenAI OAI.Combinatorics.Chromatic.GradedAlgebra.InputOrderedProduct.push_partial_list and push_partial_union construct ordered products from pairwise noninteraction hypotheses. Their domain is weighted torus series, so they are structural guidance for the explicit no-interaction interval certificate, not direct formal proofs of this compiler transformation.

Elementary transvection algebra, trace equivalence and concavity are established mathematics. The claimed application here is the new jointly scheduled and reframed60-cell construction, its sufficient contextual resource proof and its actual checked profile gain. We do not claim global originality of those elementary theorems or an unconditional multiplication theorem.

## Subsequent native admission

The unchanged upstream C++ checkers have now passed on the actual changed records: common-frame/lifecycle legality;960 five-stage formal columns;1440 formal columns for the actual nine-stage controller; all18 omitted-bridge controls; conservative payload102bits. Six structural record corruptions and three mutable-source corruptions were rejected. The separate KPAIRS5 run also passed1680 columns and24 bridge controls. Source hashes and exact configuration are recorded in native/NATIVE-REVIEW.json. Global owner routing, complete invoice and outer assembly remain separate until their final receipts.
