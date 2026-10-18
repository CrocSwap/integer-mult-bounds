# Low-rank completions with free diagonals

This concerns the **off-diagonal mask**, not PR717's E-graph mask. The
off-diagonal mask fixes every entry with i != j and frees all diagonals.
The E-graph mask fixes diagonals and orthogonal pairs and frees odd pairs.
Neither result should be substituted for the other.

## 1. A half-root spanning bound

Use twice-root coordinates. The 64 half-root lines have representatives

    v = (1, s2, ..., s8),  sj in {+1,-1},  product(sj) = +1.

Every nonzero complex normal annihilates at most **35** of these lines.
Consequently any 36 span C^8. The constant is sharp: the real normal
(1,...,1) annihilates exactly C(8,4)/2 = 35 lines.

Here is a self-contained counting proof. Take a nonzero real normal with
k nonzero coordinates. Flip signs to make its nonzero coefficients
positive. Zero sums among their 2^k sign choices correspond to subsets
of these positive numbers with one fixed sum. These subsets form an
antichain: proper inclusion strictly increases the sum.

An antichain of subsets of a k-element set has size at most C(k,floor(k/2)).
A subset of size t occurs as a prefix in t!(k-t)! permutations. Each
permutation chain meets the antichain at most once. Counting gives
sum 1/C(k,t) <= 1; each denominator is at most C(k,floor(k/2)). This
proves the bound without a classification of E8 flats.

For k=1 there are no zero sums. For 2 <= k <= 7, toggling a zero
coordinate interchanges even and odd parity without changing the sum.
Exactly half of the zero sign vectors have even parity; quotienting
by antipodes divides by two again. The number of zero half-root lines
is therefore at most

    C(k,floor(k/2)) * 2^(8-k) / 4 <= 32.

For k=8, discard the parity restriction, then quotient by antipodes:
at most C(8,4)/2 = 35 lines remain. For a nonzero complex normal, at
least one of its real and imaginary parts is nonzero; the complex zero
set is contained in that part's real zero set. The same bound follows.
All transposes below are ordinary transposes.

## 2. Diagonal completion theorem

Let R contain the real representatives of any surviving E8 root lines,
normalized to squared norm two, including h of the 64 half-root lines.
Put A = 2RR^T. Suppose h >= 52, and choose an integer

    8 <= q <= h - 44.

For arbitrary complex diagonal Delta, put s = |supp(diag Delta)|. Then

    rank_C(A + Delta) <= q  iff  s <= q - 8.

In either case the rank is exactly **8+s**. There is no restriction on
which sparse root lines survive or on the nonzero values in Delta.

**Proof.** The half-root bound gives rank(R)=rank(A)=8. If rank(A+Delta)
<= q, rank subadditivity gives

    s = rank(Delta) <= rank(A+Delta) + rank(A) <= q+8.

At least h-s >= h-q-8 >= 36 half-root lines lie outside the changed
diagonals, so they span eight dimensions. Choose eight independent
rows indexed by B outside supp(Delta). The principal block A[B,B] is
invertible: it is twice the Gram matrix of independent real vectors.

Pivot on that block. A has zero Schur complement because rank(A)=8.
The pivot rows and columns of Delta are zero, so the Schur complement
of A+Delta is exactly Delta on the remaining indices. Hence

    rank(A+Delta) = 8 + rank(Delta) = 8+s,

giving s <= q-8. Conversely s <= q-8 implies rank(A+Delta) <= 8+s <= q.
There are again at least 36 unchanged half-root lines, so the same pivot
proves exact rank 8+s. This proves both directions for arbitrary complex
coefficients. QED.

This is a uniform written proof. The finite checks verify coordinates,
the sharp example, combinatorics and exact matrix fixtures; they do not
enumerate all complex normals or all Delta.

## 3. Consequences and boundaries

The pinned P112 deletes the eight sparse frame lines e_(2j) +/- e_(2j+1)
and retains all 64 half-root lines. Thus q=8,...,20 is covered. A q-term
factorization K=DT^T has rank at most q. If it matches A off the diagonal,
at most q-8 diagonal entries can differ. Eight terms force K=A, and nine
terms can alter at most one diagonal entry.

After deleting p_h <= 12 half-root lines, the covered range is
8 <= q <= 20-p_h, regardless of sparse-line deletions. These are
sufficient bounds, not sharp puncture thresholds or a barrier for q>20.

For eight-term P112 decoders, PR1077/PR968's inherited complex all-pairs
floor therefore applies: the sum of eight support-pairing ranks is >=64.
The new implication is that freeing only diagonals does not escape that
floor. The value 64 and the floor belong to the predecessors. This
corollary retains PR968's flat-classification premise; the completion
theorem itself does not use it.

For nine terms this does **not** prove a copy-cost floor. The completion
A + delta e_i e_i^T has rank nine and matches every off-diagonal entry.
The coordinate eight terms plus that correction have cost 64+1=65.
This is an example, not a lower bound for arbitrary factorizations.

On an independent eight-line frame, a single +1 diagonal change still
has rank eight. This gives a concrete control showing why the redundancy
hypothesis cannot simply be removed.

No physical supplier is constructed. Even granting free preparation,
frames, restoration, hosting and diagonal repairs does not relax the
eight-term identity in the stated domain. Nine-term copying costs,
the E-graph mask, arbitrary off-diagonal masks, approximate identities,
and multiplication/compiler/precision/analytic obligations remain
outside this theorem. No new kappa is asserted.
