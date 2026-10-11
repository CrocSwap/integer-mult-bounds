# Independent cohort-bank completion review

This is a sufficient physical construction for the literal current249 cohort rewrite. It adds no interior residual-bank assumption. The new helper word is the parent lane's literal `COHORT249-RECORDS.bin`: 132 disjoint untouched-helper pairs receive one rank-one entrance each, a paid XOR at their common entrance frame, and a paid inverse XOR at the final full frame. Its scalar semantics are F2; addresses remain over the admitted odd-prime local rings. Integer ADD coefficients must not be discarded in the address calculation.

## Actual census and allocation

The review derives helper families from `249-states.json.regs`, the literal new initial-frame table, and the actual old/new frame registries. The 16,587 physical helper identities are retained. The resulting residual counts are

`4:2200, 6:22, 7:5, 11:48, 12:23, 15:2, 23:132, 24:14155`.

Forty physical replicas are executed in each of five stages. Keep the five stage bank collections separate. In each stage change the old allocation only by taking 5,280 rank-24 blocks and 9,240 rank-4 blocks: they occupy 1,056 old pure-24 banks and 308 old pure-4 banks. Replace them by 1,320 banks with four rank-23 blocks followed by seven rank-4 blocks. Each new bank has width `4*23+7*4=120`; every actual helper/replica occurs once. All other mixed patterns remain unchanged. Pure-24 bank count becomes 113,240 and pure-4 count becomes 2,523. Thus there are 117,519 banks per stage, 587,595 banks total, and 281,600 data families: literal stock is 869,195, exactly 220 below 869,415.

The C++ checker independently enumerates all 3,317,400 helper/replica/stage assignments and checks no duplicate interval and no unfilled coordinate in every bank. It emits all 26,400 new rank-23 assignment records. Assignment hashing is a deterministic FNV receipt, not a cryptographic proof; SHA-256 source/input bindings are recorded separately.

## Actual charts, not rank substitutions

Every new entrance line is spanned by an explicitly emitted integral vector u with sum(u)=0 and u^T u=4. In the inherited form G=I-J/9, G u=u. Consequently its projector is sigma=u u^T/4, its residual is P=I-sigma, and its exact orthogonal complement is ker(u^T).

Choose a coordinate p with u_p=+1 or -1. Put the 23 columns `e_j-(u_j/u_p)e_p`, j!=p, first, and put u last. These are an integral matrix B. Its determinant has absolute value 4. Fractional Gauss-Jordan gives an explicit inverse with denominators dividing 4, checks both inverse products, and checks `B^-1 P B=diag(I23,0)` exactly. The finite checker verifies all 132 charts. At most 30 row factors suffice for each new inverse, below the inherited bound 548. Orthogonality of the two summands is checked directly; no inference from dimensions is used. The unchanged prime guard q>2^80 makes 2,3,4 and all block scalars units over every inherited Z/q^w.

For stage i and assigned block b, take exactly the inherited normalizer

`N_b=(b+1)*Pi_b*embed_i(B^-1)`.

It conjugates the actual residual P_i into the assigned coordinate interval. The explicit permutation Pi_b sends the stage's first residual coordinates to that interval and sends the ordered complements bijectively. Thus the construction applies to the genuine new rank-one entrance frames.

## Dirty correctness and address routing

A helper's literal physical entrance/final frames are sigma and I24. The scalar word restores every arbitrary helper value and has no final data/helper cross block. The nested-frame invariant therefore gives its genuine physical residual partial swap `D_(I24-sigma)`, exactly as in the inherited completed-bank theorem. The new basis gates are already in the source word and paid there; the bank compiler does not delete them. Arbitrary correlations among dirty arrays are allowed.

Use the inherited literal route `d*tau_i*N_b^-1`. A complete GL-cover sweep is a bijection on each bank class, and the endpoint seen at class h is the conjugated coordinate partial swap. Two local helper operands assigned to one family have distinct route keys: on a coordinate outside the stage window, the embedded chart inverse fixes that coordinate, while the explicit permutation and the different unit scalar b+1 distinguish the resulting columns. There are at most 30 blocks in a bank. This nonalias argument depends on the full GL cover, not a projective quotient. No pointwise helper gate is replaced by an uncharged address-independent gate.

Complete each stage/replica cover sweep before the next one. Since complete invocations have no bank/data cross block, later invocations may receive completely arbitrary dirty bank contents. The block projectors are pairwise annihilating and sum to I120. Their partial swaps therefore compose to the full bank swap. The C++ checker executes every distinct layout, forward and backward, on all 240 address columns; it also executes every single-block omission and repetition and verifies the expected nonzero failures. All 3,840 correct endpoint columns and 3,840 failing control columns pass their expectations.

The whole transformed scalar word, its compensated target chronology, old chart admissions, actual common-cover lowering, copied-center work stream discipline, ordinary leaf absorption, and 47 analytic assembly inequalities remain the independently checked parent/public components. This review provides the new finite chart/assignment/completion bridge; it does not claim their certification merely from local columns.

## Paid costs

New inverse chart factors <=30 preserve the old 548 chart-factor ceiling. The conservative bound per normalizer is still `548+119+120=787`. The full out-and-back selector charge is

`2*5*40*((869195-1)+16587*120*787)=626938189600 < 2^40`.

The 132 new Q and Q-inverse pairs add 52,800 literal scalar operations across five stages and forty replicas; 528 deleted old reads remove 105,600, so net 52,800 scalar operations are removed. These scalar changes and every new movement are retained in the full supplier invoice. The raw movement delta is rank1:+132, rank2:+264, rank3:-264; it is not treated as an exponent gain until root pricing composes all supplier and outer terms.

The132 new rank-one helper completions have child width5 in the five-stage ledger. Ordinary width5 children remain. Subtract the explicitly tagged132 completions; do not delete the full width5 histogram bucket.
