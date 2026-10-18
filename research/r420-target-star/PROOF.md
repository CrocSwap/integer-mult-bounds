# Exact target-star identity and paid scope

All endpoint algebra is over F2. Fix the pinned R420 word, write `s` for its
420 arbitrary helper values and `y` for its 120 arbitrary target values. The
original D has one helper-only row `K_i` per target and implements
`y <- y + K s`. It never changes `s` or the 120 sources `x`.

## Construction

Choose disjoint donor and receiver target sets Q and S. For every receiver i,
choose one donor `d(i)` in Q; different receivers may share a donor. Let P have
one nonzero entry `P[i,d(i)]=1` for each receiver, and zero rows elsewhere.
Every donor row is zero and every nonzero column indexes a donor, so `P^2=0`.
Thus `T=I+P` satisfies `T^2=I`.

Execute at frame zero, before A:

1. For each receiver i, add its donor target into `y_i` (apply T).
2. For receivers, add `(K_i + K_d(i))s` into `y_i`. For every other target,
   including all donors, add the original `K_i s`. This adds `T K s`.
3. Apply the literal reverse of step 1 (T again).

The aggregate output is `T (T y + T K s) = y + K s` for every initial target
vector, not just clean targets. Helpers are only read; sources are untouched.
No receiver is a donor, even when a donor is reused. The preparation operations
commute. For one receiver and its donor d the cancellation is explicitly

`(y_i + y_d) + (K_i + K_d)s + (y_d + K_d s) = y_i + K_i s`.

The identity is predecessor target-interval factoring from #476/#478.
Concurrent #713/#716 apply disjoint target pairs to D. Here several receivers
may share a donor, retaining an immutable helper basis and a square-zero target
change of basis. No novelty of the elementary identity or priority for
frame-zero target-basis compensation is claimed.

## Complete cost and bounded search

For a row K let `|K|` count its nonzero helper coefficients. A receiver i using
donor d costs `|K_i xor K_d| + 2` additions, including preparation and
restoration. Its net saving is

`g_i,d = |K_i| - |K_i xor K_d| - 2 = 2|K_i intersect K_d| - |K_d| - 2`.

The verifier checks both formulas independently for all 14,280 oriented target
pairs. Every other D row has its old cost, so total savings are exactly
`sum(i in S) g_i,d(i)`. For fixed Q, each target outside Q independently chooses
the donor with maximal gain, or stays unchanged if that gain is nonpositive.
This maximizes savings over all receiver subsets and assignments for that Q.
Smaller donor IDs break ties. It does not optimize the choice of Q.

The bounded nomination starts with Q={0} in target coordinates, adds the donor
giving the greatest strict increase in this complete objective, and stops at
16 donors or when no addition improves it. All 1,680 candidate donor sets in
15 addition steps were evaluated. It reached the prescribed 16-donor limit.
The certificate records every candidate score and selected set. No removal,
swap, layered basis or general XOR synthesis was searched; no global or
single-addition local optimum follows from hitting the limit. The initial
single-donor experiment remains the first trace entry: 892 additions saved.

The final 16 nominated donors serve 100 receivers, with total gain 3,288.
The middle step costs 16,434 helper additions; preparation and restoration cost
100 each. D therefore costs 16,634 instead of 19,922. Every source-access term
is individually emitted; no multi-input XOR is priced as one addition. The
complete native word costs 23,628 instead of 26,916, including unchanged A,
B, C and scatter additions. This is 138 fewer additions than #713/#716's
reported 3,150-saving disjoint-pair construction, without importing, replaying
or composing it.

There are no new registers, copied centers, helper preparations/restorations,
frames, frame changes or recursive children. All targets and helpers start at
frame zero. D finishes before A; the actual MOVE/COPY/ERASE sequence is identical.
The 2,940 MOVEs, nine COPYs, nine ERASEs, per-register ordered frame paths,
histogram `{1:1320,2:1440,4:60,5:120,8:9}` and rank mass 5,112 remain unchanged.
Both words are actually exported; their complete streams and ADD counts are
checked. No accounting equality is inferred only from syntactic gate counts.

## Interface extension

The pinned #543 lemma uses `z=(x,s)` and allows interleaved z-writes in B. Its
raw A/scatter/B map has the certified form

`z' = U z, y' = y + x + K s`,

and C is the literal inverse of the z-destination gates. H2 requires D to read
helpers only. A sufficient replacement is that all D gates act at frame zero
on target/helper registers and the aggregate D operator equals
`(x,s,y) -> (x,s,y+K s)`.

The identity above proves this replacement, while keeping helpers unchanged
even between gates. Since A/scatter/B/C are unchanged, composition gives the
same restored native endpoint `y <- y+x`. All 660 independent input columns
include every source, initial target and dirty helper.

The old H2 and literal `K_equals_D` extractor remain false on this syntax.
The verifier requires precisely these diagnostics to fail and all others to
pass. It compares complete D operators, independently replays the whole word
and the exported stream, and checks the replacement frame/operand condition.
Actual changed-word geometry is checked; no normalized helper-only substitute
is passed off as the candidate's native execution.

## Integer lift and remaining obligations

The two F2-equivalent recipes are not claimed to have the same unsigned integer
matrix. The cancellation-free forward row-sum bound stays 144,651. The inverse
bound rises from 2,270,064 to 3,798,646. The exact native formula gives

`64 * forward^3 * inverse^2 = 2795129547373030713462210657024 < 2^104`.

Its bit length is 102. Every actual exported ADD, COPY and ERASE is counted in
both directions, including intermediate target mixing. Fewer gates alone do
not imply a lower integer prefix bound. The unchanged C++ checkers independently
confirm both directional bounds, the invoice and 5/9/11-stage finite endpoints.

The unchanged rank profile cannot improve the recursive moment by itself, and
the selected assembly is complex-limited. No new kappa is claimed. Acceptance
of the new D contract, hosted-parent/whole-owner reconstruction, global prefix
bounds, complete finite invoices and changed-word assembly remain separate work.
All-size/common-label/mutable-basis realization, pooled hosting, residual,
precision/tape/recovery and analytic assumptions are inherited. Finite replay
is not a formal proof of the complete integer-multiplication theorem.
