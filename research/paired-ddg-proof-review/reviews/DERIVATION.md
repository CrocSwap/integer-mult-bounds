# External written audit of the paired denominator-13 decision graph

## Verdict, scope and source exposure

**Verdict: the all-depth product law, tail formula and fair-bit optimality argument are valid under the source's fixed nonadaptive-pair contract. The credited 312-state count also has a uniform structural proof, supplied below without enumeration. No structural gap was found.** This audits zxv's PR6072 result; it does not claim discovery of its sampler, state count, expected-bit bound or classical decision-tree method.

The canonical retained source is `research/paired-residue-sampler/` at `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, originally PR6072 head `9011bf83e85ecd0443c789cf03259442f750877d`. Exact inspected inputs are README Git blob `615c4890ec797561fd4287445ceb1019905175bc` and verifier blob `eda448fbda7b6a78f340086fcaac6e7556bf1383`, read as inert text from this review's frozen inputs. This is source-aware AI derivation after original-source exposure, not blind discovery, a human review or proof-kernel acceptance. No peer draft was read before sealing. No scientific program, source verifier, constructor, census, import, compilation, native operation or numerical experiment was executed for this note. Hash/byte/time operations used for its seal are metadata only.

The displayed exact mean for `(a,b)=(1,1)`, the original exhaustive catalogue and literal-tape evidence are inherited source results, not freshly computed here. The all-depth and resource proofs below are written arguments. The scope is neither a physical inverse nor adaptive/native caller integration, runtime performance, a finite latency cap or a new multiplication bound.

## 1. Probability contract

Fix integers a,b in {1,...,12} before drawing any sampler bits. Start in the deterministic root control state, with no uncharged random initial state or entropy reservoir. The bits consumed by this invocation form a fresh independent fair sequence. The algorithm may stop at an unbounded random depth; only expected consumed bits are optimized.

For output labels 00,01,10,11 define

    w0=(13-a)(13-b),  w1=(13-a)b,
    w2=a(13-b),      w3=ab,
    pi=wi/169.

All four weights are positive, less than 169 and coprime to 13. Their sum is 169. They are the four products of the two Bernoulli masses; in particular p10+p11=a/13, p01+p11=b/13 and p11=(a/13)(b/13). Producing these four probabilities therefore proves independence of the two output decisions, not merely their marginals. It does not make either output independent of the consumed random tape.

The fixed-pair assumption is necessary: replacing b after observing the first rounded result is a different distribution and dependency contract. The sampler does not establish that a physical caller exposes this pair before either output is used.

## 2. Exact remainders, digits and unfinished counts

For every integer k>=0 write

    fi,k = floor(2^k*pi),
    ri,k = 2^k*wi - 169*fi,k,
    nk   = 2^k - sum_i fi,k.

Because wi is nonzero modulo 13 and 2 is invertible modulo 169, each remainder ri,k lies in {1,...,168}. Summing the remainder equations gives

    sum_i ri,k = 169*nk.

The sum is positive and at most 672, so the integer nk is always 1, 2 or 3. At k=0 all fi,0 are zero and n0=1.

The probability digit at the next depth is

    di,k+1 = fi,k+1 - 2*fi,k = floor(2*ri,k/169).

It is 0 or 1, and the next remainder satisfies

    ri,k+1 = 2*ri,k - 169*di,k+1.

Subtracting the floor recurrences from the count definition yields

    nk+1 = 2*nk - sum_i di,k+1.                 (1)

Since nk+1>=1, there are enough children of the nk unfinished nodes to assign all indicated output digits, and some children remain unfinished. This proves the no-overfill assertion at every depth, not merely in a finite prefix.

The indexing matches the actual source table: stored phase k uses ri,k and nk *before* the next bit, then computes `2*r//169`, which is di,k+1. The README's depth-k digit convention and the source phase-k convention thus differ by one as expected, rather than by an algorithmic shift.

## 3. Prefix-count invariant and the literal node-index rule

At depth k, define a completed output-i prefix count to mean the number of full length-k binary strings whose traversal already stopped with output i at or before depth k. A leaf at an earlier depth is padded by all possible suffixes. This definition is important: it counts completed fair cylinders at the current resolution, not only leaves located exactly at that depth.

Inductively, the construction has:

1. exactly fi,k completed output-i prefixes;
2. exactly nk unfinished length-k prefixes, indexed bijectively by j=0,...,nk-1;
3. every length-k fair prefix in exactly one of those classes.

The base is the single unfinished empty prefix. At the next level every earlier completed prefix doubles, while each unfinished prefix creates children 2*j+u for u in {0,1}. These are exactly the consecutive indices 0,...,2*nk-1. In output order, label di,k+1 successive children with output i, and retain the remaining consecutive children. Completed counts become

    2*fi,k + di,k+1 = fi,k+1.

The survivors have cardinality (1); subtracting the total number of newly assigned children reindexes them bijectively from zero. This proves the induction.

The source's subtraction loop is exactly that interval allocation. Starting from j'=2*j+u, subtract each di,k+1 in output order; the first subtraction that makes it negative identifies the unique output interval containing the original child index. If no subtraction makes it negative, the final value is in {0,...,nk+1-1}. A zero digit assigns no child. The immediate break at the first negative subtraction prevents a second output from claiming the same child.

Consequently the procedure implements the prefix-count invariant. This is a semantic argument about the actual small update rule, not an assertion that this review executed the verifier or its tables.

## 4. Almost-sure termination and the exact joint law

By the prefix invariant and fair-bit hypothesis,

    Pr(T>k) = nk/2^k <= 3/2^k.                 (2)

This tends to zero, so T is finite almost surely. The completed probability for output i by depth k is fi,k/2^k. Its difference from pi is nonnegative and less than 2^-k; hence it tends to pi. Earlier terminal cylinders are disjoint, so the limiting completed probability is exactly the actual eventual probability of that output. Thus the four labels have law `(w0,w1,w2,w3)/169`, including both independent marginals.

There is nevertheless positive survival at *every* finite depth because nk>=1. No finite draw cap implements this graph exactly. Almost-sure termination and a finite state space do not imply a finite worst-case stopping time.

## 5. A uniform proof of period 156 and the credited 312 states

Here the finite state count need not be left as a 144-case premise.

First, 2 has exact multiplicative order 12 modulo 13. Indeed 2^6=64 is -1 modulo 13, while 2^4=16 is 3 modulo 13. Every proper divisor of 12 divides 6 or 4, so neither test permits a proper order. Also

    2^12 = 4096 = 1+3*13  modulo 13^2.

For any positive integer t, the binomial identity gives

    (2^12)^t = (1+3*13)^t = 1+3*13*t modulo 13^2,

since every term of degree at least two contains 13^2. If 2^k=1 modulo 169, reduction modulo 13 first forces 12|k. Write k=12*t. The displayed identity then forces 13|t. Conversely t=13 gives equality modulo 169. Thus the exact order is 156, proved without scanning exponents.

In particular 2^78 is a nonidentity square root of 1 modulo 169. The only such roots are 1 and -1: if 169 divides (x-1)(x+1), the odd prime 13 cannot divide both factors, so all of 13^2 divides one factor. Therefore

    2^78 = -1 modulo 169.

For every nonzero remainder,

    ri,k+78 = 169-ri,k.

Summing the four remainder identities gives the useful pairing

    nk+78 = 4-nk.                              (3)

The remainder/digit/count arrays are periodic with period 156, and pairing phases k and k+78 for k=0,...,77 shows

    sum_(k=0)^155 nk = 78*4 = 312.             (4)

This uniformly proves the source's selected phase/node construction has exactly 312 internal states for every admissible pair, with no parameter census. It does not prove that no different or minimized controller could use fewer states. The source's expected-bit optimality is a different objective.

The internal states are exactly `(phase k,node j)` with 0<=k<156 and 0<=j<nk. Each is reachable from the deterministic root at its first-period depth by Section 3's bijection. From phase155, a surviving child moves to phase0. At depth156 the remainder array equals its root array and n156=n0=1, so the sole surviving child has node index zero. It returns to the *root control state* to consume another bit; it does not return an output or stop. This distinction is essential. The same controller state may be revisited after a longer history while the fresh future bits continue to realize the periodic suffix law.

The source enumerates states in phase/node order, so `(0,0)` has identifier zero and every internal identifier lies in 0,...,311. Output labels receive identifiers 312,...,315. Both table branches from every state are accounted for by Section 3; no hidden dead state is needed. This establishes the semantic association of the source's hardcoded output offset 312 with its constructed state inventory.

## 6. Exact expected draw formula and the broad inequalities

For any nonnegative integer-valued stopping time, including one that could be infinite, the tail-sum identity follows by summing the indicators of T>k. All terms are nonnegative, so the identity remains valid without assuming convergence in advance. For this sampler, (2) ensures finite expectation and gives

    E[T] = sum_(k>=0) nk*2^-k.

Using the now-proved 156-periodicity and grouping nonnegative terms by phase yields

    E[T] = [sum_(k=0)^155 nk*2^-k] / (1-2^-156).   (5)

The initial n0=1 is part of the numerator; starting at n1 or treating the phase wrap as stopping would give the wrong cost.

The broad source inequalities can also be checked structurally rather than by recomputing its catalogue. Since nk>=1, E[T]>=sum 2^-k=2. Equation (4) forces some phase to have nk>1, so the inequality is strict. Also n1<=2 because it counts unfinished children of the single root, while nk<=3 for k>=2. Thus

    E[T] <= 1 + 2*2^-1 + 3*sum_(k>=2)2^-k = 7/2.

At k=156 the actual count is one rather than the bounding value three, so this upper inequality is strict too. These deductions support the credited `2<E[T]<7/2` result for the fixed source family; they are not a new finite catalogue or executed numerical observation.

The exact displayed `(1,1)` fraction, its particular `<9/4` comparison and source-reported catalogue extrema are not recalculated by this audit. They remain inherited finite arithmetic claims unless checked separately. Formula (5), not acceptance of those particular numerators, is the all-depth conclusion established here.

## 7. Optimality among exact fair-bit trees

Fix the same four probabilities and consider any exact decision tree whose only initial random resource is the fresh fair-bit sequence, with deterministic initial control. Deterministic computation between bit requests is allowed; the objective counts requests, not its time. More general control algorithms in this model induce such a binary decision tree. A free randomized initial state or an uncharged retained reservoir is outside the comparison.

For a depth k and output i, the strings completed with that label by depth k form a union of length-k fair cylinders. Their mass is Mi,k/2^k for some nonnegative integer Mi,k, using the same padding convention as Section 3. Exact eventual output probability pi implies this completed mass is at most pi. Therefore

    Mi,k <= floor(2^k*pi) = fi,k.

Summing over outputs shows that any such tree has

    Pr(T_tree>k) >= nk/2^k                      (6)

at every depth. If a competitor's expected draw count is infinite it certainly does not improve on (5); otherwise the nonnegative tail-sum identity and (6) still give its expectation at least (5). The constructed sampler attains equality at every depth by the prefix invariant. It is therefore expected-fair-bit optimal, not merely asymptotically or up to a constant.

This argument covers arbitrary decision trees in the stated bit model, not just periodic ones or 312-state ones. It does not optimize table size, transitions' physical cost, output writing, or reversible retention.

For a separate non-dyadic Bernoulli decision, at least one fair prefix must remain unfinished at each depth: termination of all prefixes by some depth would make its probability dyadic. Its expected draws are consequently at least two. Two independent standalone invocations without a shared entropy reservoir cost at least four in expectation. The paired graph changes that call boundary, while preserving independence of the resulting decisions. It does not contradict a worst-case obstruction or permit reusing one flag as both independent outputs.

## 8. Resource association and remaining obligations

The selected graph has 312 internal states and two targets per state, hence 624 target entries. All internal/output identifiers are below 316 and thus fit in nine bits. A logically packed target table therefore has

    624*9 = 5616 bits = 702 bytes.

This is an explicit encoding bound for one fixed parameter pair. The literal Python list/tuple/int representation has additional object overhead; 702 bytes is not its measured resident memory. Nor does the bound cover an actual selector/dispatcher across all pairs, obtaining a,b, building a table, random-tape access, output storage, stopping records or cleanup. Source generation of one table at a time does not itself supply those physical invoices. There is no inference from expected consumed bits to wall-time speedup.

The 312 association is structurally established, while the particular source finite-tape tests and exact mean certificates have not been rerun. The audit does not certify arbitrary corrupted tables or all source guards, and it does not import the original verifier as evidence. Current/native caller, all-column/owned-return, numerical error, precision, entropy handling, physical costs and selected-framework obligations remain separately scoped.

PR6096 and PR6546 already address distinct numerical-joining questions; this audit does not describe their work as absent or claim to replace it. It also does not establish an actual nonadaptive inverse-stage pair, an unbounded-call cleanup bill, or adaptive composition merely because the four-outcome law is exact.

Credit remains zxv with substantial OpenAI Codex assistance for PR6072 and its finite denominator-13 catalogue; the dyadic distribution-generation tree and depth-wise optimality method are classical. Retain JoyboyBrian's PR5069/5037 inverse lineage, Nick Petalas's PR6026 stochastic-prefix context, the PR6068 standalone/worst-case boundary and all inherited source/license notices. No predecessor theorem, selected frontier or multiplication bound is changed.
