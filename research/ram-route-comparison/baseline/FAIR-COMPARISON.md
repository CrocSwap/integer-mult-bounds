# Fair same-model comparison and a positive dominance criterion

The current native route and the packed-TM route have the same certified conditional Word RAM exponent: kappa = 0.0030217758. The direct native construction removes the TM dependency from its execution proof; that architectural change alone does not establish a faster algorithm.

Prepared for Dugongue with substantial OpenAI Codex assistance. Apache-2.0. This is an informal sufficient comparison theorem and source audit, not a timing experiment or a new multiplication theorem.

## Actual baseline, not one RAM instruction per TM transition

PR #4541 at 46ca24a88b5194725a82c02003aac8aea0c6f53a proves a uniform packed-window simulator for a fixed finite k-tape machine. If its actual run takes T transitions, has total binary input n, output cap m and a fixed polynomial time/address envelope, its bounded-word RAM cost is

    O((T+n+m)/log(n+2) + (n+2)^(1/16) log(n+2)).

It charges table generation on every input, all reads before writes, signed origins, packed binary codecs, partial chunks and genuine halting. Its instruction set is additive/Boolean with logical shifts, indirect memory and branches; it needs neither multiplication nor division. This is therefore a valid baseline on the stronger multiplication-enabled Word RAM used by the direct native route. Both results must use packed input/output, logarithmic word width with sufficiently large fixed coefficient, and the same zero-initialized fresh-memory convention when compared. A one-bit-per-word ABI would impose an additional linear input/output floor on both.

PR #4552 at a821e926e3d7eaeae8b12be974dc5083360f6494 independently checks the exact parameter arithmetic and macro-step invariant. PR #4553 independently checks packed codecs; neither finite check proves the supplied multiplication antecedent. The packed-simulation construction is credited to Dugongue and the classical Hopcroft-Paul-Valiant method, with the explicit sub-n-log-n packed-IO treatment credited to #4541.

Consequently every complete fixed-machine conditional bound

    T(n) = O(n (log n)^(1-kappa_T)),  0 < kappa_T < 1,

already gives a same-model packed RAM bound O(n/(log n)^kappa_T). Apply this to the latest complete conditional TM antecedent at kappa_T = 0.0030217758 only with all of its own retained hypotheses. The direct native transfer at kappa_R = 0.0030217758 then matches the exponent. Comparing it instead with O(T) would invent a logarithmic advantage that #4541 already supplies.

## Positive sufficient theorem: better certified bound

Let two correct algorithms operate on the same packed ABI and Word RAM. Suppose the packed-TM source has the complete bound above at kappa_T, and a fully charged native construction has

    R_N(n) <= C_N n (log n)^(-kappa_N) (log log n)^a

for fixed a >= 0 and C_N, with all setup, precision, restoration and output terms included. If kappa_N > kappa_T, then for every 0 < eta < kappa_N-kappa_T,

    R_N(n) = O(n/(log n)^(kappa_T+eta)).

Proof: put x = log n. For each fixed a and positive delta, (log x)^a = o(x^delta). Take delta = kappa_N-kappa_T-eta. Substitute in the complete native bound. The packed-simulator setup n^(1/16) log n and packed-IO term n/log n are lower order than n/(log n)^kappa_T, so its stated upper envelope is O(n/(log n)^kappa_T). The native theorem therefore supplies a strictly smaller certified asymptotic envelope. This conclusion compares guarantees; upper bounds alone do not prove that one actual implementation is faster on every large input.

For an actual asymptotic runtime speedup, the additional sufficient hypothesis is that the baseline run itself has time Omega(n/(log n)^kappa_T) on the compared input family. Under that explicit hypothesis the same calculation proves R_N/R_baseline tends to zero. With explicit constants and cutoffs, a finite crossover certificate is the check

    C_N (log n)^(-(kappa_N-kappa_T)) (log log n)^a < c_baseline.

No such lower bound, constants or crossover has been established for the present complete multipliers. They must not be inferred from headline big-O statements.

## Positive robust adoption theorem

If both complete algorithms are available with the same packed ABI and independently owned work arenas, alternate one bounded native instruction from each until either genuinely halts, then return its verified output. This uniform portfolio is correct and takes O(min(R_N,R_S)+n/log n) target operations (at most 2 min(R_N,R_S) scheduled source steps, plus constant dispatch/relocation overhead), with the memory sum of the two executions. Each side receives the same input headers and immutable input; unrelated dirty storage is untouched by its ownership protocol. The result follows by counting the alternation rounds until the first completion. It preserves whichever complete bound is stronger and gives a safe comparison harness. It retains a simulated TM branch, so it is a validation/transition strategy, not the user's requested final TM-free execution architecture.

A wholly TM-free production replacement requires the direct native implementation and its proof. Its adoption can be justified structurally by the removed tape semantics and the ability to improve native row tariffs independently, but a statement of computational superiority requires the strict inequality or concrete cost certificate above.

## Preparation distinction

The particular #4541 simulator explicitly constructs every short-window table row. Write lambda=floor(log2(n+2)), c for alphabet-code width, K for the least power of two at least k, r for its epoch length, and b=s+kc(2r+1). Above its fixed cutoff, r >= lambda/(128Kc), hence

    b >= k lambda/(64K).

Thus that chosen eager simulator's table generation has at least 2^b = Omega(n^(k/(64K))) row writes, as well as its proven upper bound O(n^(1/16) log n). If an actual native caller has the retained n^o(1) preparation bound, its preparation is asymptotically smaller than this chosen eager table construction. This is a positive subroutine comparison, not a whole-multiplication speedup: both setup costs remain below the main n/(log n)^kappa work. It is not a lower bound for every possible simulator, and amortizing tables across repeated inputs changes the comparison.

## Scope and next actionable checkpoint

The exact current comparison is equal kappa under separate conditional proof chains. A convincing larger native saving must change a complete native row or supplier/consumer invoice and beat the packed-TM exponent after all native terms are paid. A practical switch claim instead needs emitted instruction counts or reproducible same-ABI measurements, including setup and IO. The positive dominance criterion specifies exactly what either path must establish, without using a naive TM simulator as a weakened baseline.

Sources: https://github.com/CrocSwap/integer-mult-bounds/pull/4541 ; https://github.com/CrocSwap/integer-mult-bounds/pull/4552 ; https://github.com/CrocSwap/integer-mult-bounds/pull/4553 ; https://github.com/CrocSwap/integer-mult-bounds/pull/4610 ; https://github.com/CrocSwap/integer-mult-bounds/pull/4635 . Frozen #4541 source bytes and hashes are preserved alongside this note; source reading, not an exhaustive all-history audit, is claimed.
