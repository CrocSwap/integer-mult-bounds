# Two source-derived resource constructions

These are sufficient constructions for complete-owner schedules. They preserve each complete invocation's physical endpoint: Q on the assigned residual coordinates, identity on spectators, with scalar-body arbitrary-dirt restoration certified separately. They do not replace the retained all-size multiplication hypotheses.

## 1. Exchange paths inside a fixed physical owner fiber

Start with a source-bound legal schedule and its complete physical slots. For each call c, let E_c be its available occurrences of width-nine slots. A selected subset S must contain exactly four elements of every E_c. Shrink selected slots from width nine to width eight. Reassign the new provider's width-five, width-eight, and width-nine helpers bijectively to the matching-width slots of that same call, and repack each pending bin contiguously in its original occurrence order.

Sufficient conclusion: the resulting assignment is legal at the resource level. Each call retains its exact set of physical owner families and times; no active data owner is added, no owner is aliased, and every occurrence remains in its original legal idle interval. Packing only shrinks widths, so the concatenated intervals fit their pending child. The final chart must be rebuilt from the assigned helper's actual frame; matching widths alone never proves chart equality. With this chart check and the new provider's endpoint certificate, the whole physical schedule is admitted under the same interface.

A same-call exchange S -> S - {e} + {f}, where e is selected and f is unselected in E_c, preserves the call quota. It is a two-edge exchange path. Adding an auxiliary complement assignment makes it a standard four-edge bipartite switch: selected and unselected degrees are preserved in the extended fiber. Any finite sequence of these exchanges is safe, irrespective of intermediate changes in the remainder histogram. Acceptance is based on the full paid moment, not a local entropy heuristic.

Source read: OAI/Probability/SwitchChain/SwitchInFiber.lean, in particular sameFiber_of_same_side and switchStep_sameFiber. The source proves a degree-constrained graph switch stays in a resampling fiber; it does not itself prove this multiplication admission theorem. The physical proof above supplies that missing specialization.

## 2. Concave remainder costs as an explicit cut network

Let a be fixed with 0<a<1, let r_b be a pending bin's original remainder, and let x_b count the selected shrink events incident to bin b. Its added paid moment before common normalization is

    g_b(x_b) = (r_b+x_b)^a - r_b^a.

The complete objective is the new provider's fixed local histogram plus sum_b g_b(x_b), together with the unchanged controller terms. The increments d_j=g(j)-g(j-1) are nonnegative and decreasing. For a bin of degree d,

    g(x) = d_d*x + sum_{k=1}^{d-1} (d_k-d_{k+1})*min(x,k).

Proof: both sides vanish at zero; their j-th increments equal d_d + sum_{k=j}^{d-1}(d_k-d_{k+1})=d_j. Every coefficient is nonnegative. Each term lambda*min(x,k) is an explicit cut gadget: for every incident event vertex e, add an arc e -> z of capacity lambda, and add z -> sink of capacity lambda*k. With selected event vertices on the source side, minimizing over the auxiliary vertex z gives precisely lambda*min(x,k). The linear term uses event-to-sink arcs. This represents the whole remainder objective as a cut potential, with no unknown optimization oracle.

Source read: OAI/Computability/MatchingCount/CutAlgebra.lean, cut_submodular and cut_push. Its pointwise cut submodularity and exact contraction/lift identity justify graph-level aggregation. Here the discrete-concavity identity supplies the explicit gadget representation. Exact quotas |S intersect E_c|=4 remain additional constraints; unconstrained minimum cut does NOT solve that constrained problem automatically. Our bounded native search uses the potential to accept legal exchanges, and the literal endpoint witness is independently checked. There is no global optimality claim.

## 3. Constructive lift from pattern counts to literal owners

A bin group consists of 112 physical ports sharing one owner replica, pending child, rank and legal time set. For each pattern p, choose n_p ports and a list of helper widths w_1,...,w_d with sum at most the pending rank. Let x_(p,t,w) be nonnegative integers. Require:

- sum_t x_(p,t,w) equals n_p times the multiplicity of w in p;
- sum_w x_(p,t,w) is at most n_p for each pattern and time;
- across all groups and patterns, each call t receives its exact provider width inventory;
- only times in the actual group's legal idle interval occur.

These conditions construct a complete-owner assignment. Split each width's incidences among its distinct positions in the pattern, each position having degree n_p. Form the bipartite multigraph whose left vertices are times and right vertices are pattern positions. Its maximum degree is n_p; add dummy vertices and edges until it is n_p-regular. For every subset S of left vertices, n_p|S| edges enter at most n_p|N(S)| slots, so Hall's condition holds. Remove a perfect matching and repeat. The n_p matchings are literal ports. Every port receives one incidence for each pattern position, never two incidences at the same time. Deleting dummy edges therefore yields the exact desired complete-owner slots. Assign each call's actual helpers bijectively to its matching-width slots. Offsets are contiguous partial sums of the pattern widths.

This is an explicit sufficient lifting theorem, not an assertion that aggregate counts alone imply physical feasibility. The integer time rows, matching decomposition and final independently reconstructed physical chart are all checked. It also explains the exchange-fiber structure: different matching decompositions preserve the same exact time and pattern margins. The earlier cut potential supplies remainder costs before this constructive lift; the final broader integer pattern search additionally permits changes to pattern counts. No theorem about globally optimal constrained cuts is claimed.

## Frozen concrete result

The final provider combines the static44 response selection, PR534 frame lift and one cold-dirt quotient simplification. The final local histogram is

    {1:2284,2:456,3:488,4:168,5:56,6:56,8:8}.

Its 504 helpers have widths 56x5,156x8,292x9. A bounded finite pattern/time search selected these counts across all owner replicas:

    rank8: 5376*[8]
    rank16: 2928*[8,8],448*[5,9],208*[9]
    rank32: 3584*[5,9,9,9]
    rank48: 1923*[9,9,9,9,9],1*[9],1660*[]

The literal matching lift produces 36,288 helper roles across 72 complete calls and 16,128 pending bins. All actual 2,972 full 73-column charts, per-replica event orders, whole-owner uniqueness, spectator axes and residual endpoints pass the independent physical audit; seven genuine corruptions reject. The resulting paid global histogram is

    {1:164448,2:33280,3:37059,4:12096,
     5:4032,6:4032,7:208,8:576,39:1,48:1660}.

The exact deficit is 2,560 at m=73, live stock 7,168 and physical stock 7,682. The fresh scalar invoice charges prefix512 for measured225, and row20161 for measured16467. The certified complex saving is

    b = 796759709641153381751 / 500000000000000000000000
      = 0.001593519419282306763502.

This is a complex supplier saving, not final kappa. The outer assembly must combine it with the independently admitted bit supplier through all strict constraints. All-size compiler, precision/tape and analytic-transfer hypotheses remain the retained interfaces.

The earlier fixed-slot C++ exchange search gave b=0.001590643179579185038482 with the static44 provider and is preserved as a passed intermediate. The final broader pattern search stopped at its finite time limit with a feasible integer witness; no global optimum is asserted. Replaying the final witness needs Python's standard library only, not SciPy, HiGHS, or the optimizer. Both OpenAI sources were read and adapted; neither was newly Lean-compiled. These sources informed the two resource constructions, rather than establishing a claim of two independently additive numerical gains.
