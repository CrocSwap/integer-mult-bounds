# An unbounded-term factor-rank obstruction

## Model and cited premises

Let Q be the full 120 E8 root lines used by Ali Romman in
`research/e8-small-redundancy`. Their displayed representatives have squared
length four. Set `K(q,r)=1+(q dot r)/2 mod 2` and
`C=col_F2(K)=row_F2(K)`. For a binary word w on Q, let rho(w) be the
rational dimension of the root vectors in its support.

For `K=A B^T` over F2, the cost of column pair (a,b) is the rational rank
of `(q dot r)_{q in supp(a), r in supp(b)}`. Write this as c(a,b) and add
over all columns. Multiplying the displayed pairing by one half does not
change its rational rank. Let r_A and r_B be the actual binary ranks.

The following are cited premises from Ali Romman's #4967, retained at the
base commit pinned in SOURCES.json. This package does not replay them.

1. C has dimension nine, and every nonzero c in C has rho(c)=8.
2. For every coset v+C other than C,
   `sum_{w in v+C} (8-rho(w)) <= 8`.
   This is equation (1) of TEN-PROOF.md, including all words in that coset.
3. Every basis of a binary space U containing C, with dimension nine,
   ten or eleven, has sum of support ranks at least 72.
   The dimension-ten case is in TEN-PROOF.md and the dimension-eleven case
   is the main basis theorem of ELEVEN-PROOF.md. Dimension nine is premise 1.

These are the only E8-specific premises. The binary expression defining K
and the rational inner product defining the cost are separate operations.

## Normalization does not raise cost or factor ranks

Delete any term with a zero factor. When two left columns agree, replace
`a b_1^T + a b_2^T` with `a (b_1+b_2)^T`, using binary addition. The new
right support is contained in the union of the two old right supports.
For fixed left support, the rank of its rational pairing with that union
is at most the sum of the old pairing ranks. Restricting to the new support
cannot increase rank. Thus the merge does not increase total cost.
The transposed operation handles equal right columns.

Each deletion or merge strictly decreases the finite number of terms.
After finitely many operations there are no zero columns and the columns
are distinct on each side. The product remains K. Each new column is a
binary combination of old columns on its own side, so neither factor space
nor its rank increases. Recompute actual ranks after normalization.
There is no assumption that rank stays constant or that cost-zero nonzero
terms may be discarded.

Every factorization of K satisfies `C subset col(A)` and
`C subset col(B)`, since K is symmetric. Hence r_A,r_B are at least nine.

## Two spaces with at most one extra direction

Consider a normalized factorization with m terms and
`r_A=9+s`, `r_B=9+t`, where s,t are in {0,1}.
If s=0 every left word is a nonzero member of C and has support rank eight.
If s=1, the left space consists of C and exactly one other coset. Its
columns are distinct, so premise 2, with nonnegative defects, gives

`sum_j (8-rho(a_j)) <= 8s`.

The same argument on the right gives defect sum at most 8t.
For rational subspaces U,V in the nondegenerate eight-dimensional root
space, the rank of the restricted pairing is at least
`dim U + dim V - 8`. Therefore

`cost >= sum_j (rho(a_j)+rho(b_j)-8) >= 8m-8s-8t`.

Sylvester's binary product-rank inequality gives
`9=rank(K) >= r_A+r_B-m`, so `m >= 9+s+t`. Substitution yields
`cost >= 72`. The inequalities apply to the normalized factorization;
the original cost was at least as large. This proves the all-term-count
floor when both original factor ranks are at most ten.

For a normalized rank-(10,10) factorization, the intermediate inequality
is `cost >= 8m-16`. At twelve terms this is 80. This stronger expression
uses the reduced term count; arbitrarily padding an unreduced factorization
does not justify substituting its larger term count.

## The rank-nine / rank-eleven boundary

Suppose one original factor has rank nine and the other rank at most
eleven. Delete zero terms. The rank-nine factor's nonzero columns lie in
C and span the full rational root space individually, by premise 1.
Consequently each term costs exactly the support rank of the opposite
column. Select a basis from the opposite factor's columns. Its column
space contains C and has dimension between nine and eleven, so premise 3
prices that basis at least 72. All remaining terms have nonnegative cost.
The total is at least 72. In fact, with m nonzero terms and opposite rank
r, it is at least `72+(m-r)`, because each unselected nonzero word has
support rank at least one. Duplicate merging is not needed in this case.

## Rank-sum consequence and the twelve-term boundary

If r_A+r_B is at most 20, both ranks are at least nine. The only cases are
(9,9), (9,10), (10,9), (10,10), (9,11), and (11,9). The preceding two
arguments cover all of them, for every finite number of terms.
Thus any cost below 72 requires `r_A+r_B >= 21`.

For twelve terms, Sylvester also gives `r_A+r_B <= 21`, and neither factor
rank exceeds twelve. A cost below 72 can therefore occur only at
(9,12), (10,11), (11,10), or (12,9). The theorem does not decide any of
these four pairs. This is a necessary-condition result for the fixed binary
factorization and its separate rational pairing cost. It does not imply a
lower bound for every physical decoder or multiplication algorithm.
