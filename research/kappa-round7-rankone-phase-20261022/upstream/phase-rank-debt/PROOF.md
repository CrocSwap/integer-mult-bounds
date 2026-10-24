# Phase gains must pay their own concave rank debt

Prepared by Cinna Davis with substantial OpenAI Codex assistance. Apache-2.0.

## Statement and scope

Consider the frozen PR4610 word and the symmetric-bilinear-form grammar
described in Dugongue's PR4654 and Cinna Davis's PR4665. Retain its subspaces,
scalar order and coefficients, logical warp maps, and all main and explicit
adapter boundaries. Scalar operands must still meet in one common chart.
Allow arbitrary symmetric forms at the helper boundaries and intermediate
charts, including the owned-center contacts. Allow **increased paid ranks**
and new paid corrections at formerly rank-zero transitions.

Pay each changed single-field contact block at its actual Fourier rank. Keep
the owned center uncredited. This model does not introduce a shared paid
instruction on several field owners, change the main operator, change the
subspaces or scalar graph, or delete a source operation.

For every such legal deformation and every 0 <= t <= 1, let T_t and P_t
denote the complete productive and paid rank moments, omitting rank-zero
jobs. Then

    T_t(new) - P_t(new) <= T_t(old) - P_t(old).

Thus paid phase corrections cannot improve the recursive moment of this
fixed word. Applying the same replacement in an unchanged path controller
cannot improve its complete moment either. This is a scoped cost theorem,
not a universal obstruction to phases, new native suppliers or higher K.

The phase grammar is a premise: a nested transition U subset W with forms
b_U,b_W has rank

    dim(W)-dim(U) + rank((b_U+b_W)|U).

More generally, for G U subset W the rank is dim(W)-dim(U) plus the
rank of b_in + G^* b_out on U. This includes an originally monomial warp
as the equal-dimension case. All added ranks are nonnegative.
Absolute-phase implementation and the all-column native theorem are not
re-proved here. The argument is conditional on these exact rank formulas;
it is not justified by ordinary rational matrix rank alone.

## 1. The exact word has monotone paths, including its logical warps

For each persistent field, every paid transport strictly increases its
subspace. A logical warp maps its complete old subspace isomorphically to
its new subspace, preserving dimension. Consequently the sum of old paid
ranks on field i is

    h_i = dim(final_i)-dim(initial_i).

The verifier reconstructs these paths directly from the complete forward
and backward words, checks every scalar contact and center transport, and
recounts the full paid profile

    {1:2201, 2:412, 3:510, 4:127, 5:40, 8:8}.

For all 408 helpers the endpoint spaces are nested and h_i>0. Their ranks
are {4:28,7:7,8:47,9:326}, with total 3471. Every composed logical warp
fixes that helper's entrance space pointwise. This last assertion is
checked as a map on every entrance basis vector, rather than inferred
from endpoint dimensions. Each old paid step r_ij therefore satisfies
0 <= r_ij <= h_i. Rank-zero contacts and logical warps may be included
as additional steps with r_ij=0.

For the cost comparison use the blocks between consecutive scalar contacts
on each helper, also cutting at fixed adapters and the two endpoints.
Operations on other owners commute with a block until its next scalar
contact. A block may include logical warps and can be refactored as one
whole job; the proof does not charge a separate phase correction when it
can be absorbed into that job's monomial normalizers. The verifier checks
that every original helper block contains **at most one positive paid
call**. Consequently its original moment is exactly r_ij^t, with r_ij=0
when it was wholly monomial. Transported entrance spaces stay nested
through the entire block, so the generalized rank formula applies to
the block's composed G. Every r_ij is still bounded by h_i. Fusing across
a scalar contact or introducing a shared multi-owner operation changes
the model and is outside this theorem.

## 2. Helper rank gain is bounded by its own added paid ranks

Fix a helper and transport its entrance space along its actual field path:
use inclusion at an ascending step and G at a logical warp. Pull each
intermediate symmetric form back to this fixed entrance space. At a
common scalar contact there is a single form, so no discontinuity occurs.
At a contact block, the rank of the difference between
the two pulled-back forms is at most its added paid rank delta_j:
restriction cannot increase bilinear-form rank.

The sum of these differences telescopes. Because the final composed warp
fixes the entrance pointwise, its sum is exactly the helper endpoint
difference form. The grammar gives the new helper rank h+g, where g is
the rank of that difference. Rank subadditivity yields

    g <= sum_j delta_j.

This also allows new corrections at previously equal charts. Such a
correction is not a free phase change: its old rank is zero and its
positive new rank must be paid. Corrections to fixed adapters, if needed
inside a proposed implementation, must likewise be paid; omitting them
does not invalidate this necessary lower bound.

## 3. Concavity prices that debt at least as highly as its reward

Let h>0, 0<=r_j<=h, delta_j>=0, D=sum delta_j and 0<t<=1. Put
D_j=sum_(k<j) delta_k. The function t x^(t-1) is nonincreasing for x>0.
For each step, using the improper integral at zero when necessary,

    (r_j+delta_j)^t-r_j^t
      = integral_(0..delta_j) t(r_j+u)^(t-1) du
      >= integral_(0..delta_j) t(h+D_j+u)^(t-1) du.

Summing gives

    sum_j [(r_j+delta_j)^t-r_j^t]
      >= (h+D)^t-h^t
      >= (h+g)^t-h^t.

Thus every helper's added productive moment is at most the increase in
paid moment on that same helper's path. These paths have distinct paid
field owners, even where their scalar contacts share a chart; no paid
occurrence is charged to two helpers. Main boundaries are fixed, so their
productive moments do not increase. Added main and center costs are
nonnegative. Summing proves the claimed inequality.

At t=0, every helper already has positive rank, so its productive job
count is unchanged. An old positive paid step stays positive, while a
corrected zero step adds a paid job. Therefore the inequality also holds
at t=0 with rank-zero jobs omitted. At t=1 it is just the rank-debt bound.

For an unchanged controller, each full native call gets the same fixed
main operator and its own independent helper inventory. Apply the local
inequality per invocation; thin queries, idle calls and all other main
contributions stay as prescribed by that controller. No controller
optimality theorem or outer-transfer assumption is required for this
comparison. A new controller or a change to its main contract is outside
the statement.

## Verification boundary

The analytic argument above covers all exponents and every legal form
assignment. Computation checks the exact source-specific hypotheses, not
an exhaustive search of phase assignments. It also exhausts the 512 triples
of symmetric forms on F_2^2 to check the endpoint rank triangle, proves two
strict square-root comparisons with outward rational intervals, rejects
four mutations of the actual word, and changes every frame basis without
changing the certificate. These are author checks, not a formal proof or
independent human verification.

PR4665's homogeneous zero-solution certificate is a predecessor with a
different scope. This proof does not need every form to vanish. In
particular it permits paid rank increases and arbitrary compatible center
forms. An exploratory relaxation of its owned-contact freezes left 288
coordinates on empty center resets and no nonzero helper difference;
that experiment is motivation only and is not a premise of this theorem.
