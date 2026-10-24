# The one-stage terminal gauge has a real cost

The physical normalizers make the coded supplier and its local gauge identities
constructive. They do not make the Y terminal gauge free. This note proves that
distinction for one actual source code, at every positive fiber width. It does
not prove the same statement for a product of different stage codes.

Let `Q` be the Gaussian on the common central line, let `K_i` be the signed
orthogonal permutation taking that line to source port `q_i`, and put

`C_ij = A_ij K_i^{-1} K_j`.

The source code has exactly 5,824 nonzero entries, all off diagonal and equal to
`+1/2` or `-1/2`. Its 112 port vectors are distinct. Write a nonzero block's
monomial as `M = K_i^{-1} K_j`, with binary linear part `G`. Then

`G e = G_i^{-1} q_j != e`,

because `G_i e = q_i` and `q_i != q_j`. Also `G e != 0`. Thus `e` and `G e`
are independent binary vectors. This statement uses the actual source ports,
not just the polynomial satisfied by `A`.

For one digit column, write the central Gaussian as
`Q = (1+i)/2 (I-i T_e)`, where `T_e` translates the address by `e`. If
`M |x> = s(x) |Gx>`, with `s(x)` in `{+1,-1}`, direct expansion gives

`2 Q^{-1} M Q |x>`

`= s(x)|Gx> - i s(x+e)|Gx+Ge> + i s(x)|Gx+e> + s(x+e)|Gx+Ge+e>`.

The four destinations are distinct and every coefficient is nonzero. Every
column, and every row, therefore has exactly four nonzero entries. Equivalently
the Gaussian support rank is two. At fiber width `f`, the same native monomial
and Gaussian act as tensor powers on the digit columns. Each nonzero owner
block consequently has exactly `4^f` nonzero entries per row. The coefficient
`A_ij` is applied once to this block; this argument does not tensor the owner
code or replace a sum by a tensor product.

The different input owners `j` are arbitrary and independent. Entries belonging
to different owners cannot cancel each other in the full operator. Hence the
single-code terminal operator `Q^{-1} C Q` has at least `4^f` input-coordinate
dependencies in each row that meets a nonzero block.

The inverse code has the same obstruction: `C^{-1}=(C+12I)/13`, so every
off-diagonal block of `Q^{-1} C^{-1} Q` is precisely `1/13` times the block
just analyzed. The added diagonal identity cannot cancel an independent input
owner's off-diagonal block.

A fixed finite word made from scalar ADD/SCALE, monomial address maps, and
owned COPY/CLEAR has uniformly bounded row support. Initially the support is
at most one. Monomial operations, scaling, copying and clearing do not increase
the maximum support; an ADD increases it by at most a factor two. A word with
`g` ADDs therefore has support at most `2^g`, even when clean scratch is allowed.
Realizing this terminal operator needs `g >= 2f`. In particular a fixed number
of those physical primitives cannot implement the one-stage decoder uniformly
in the fiber width.

This is a statement about the repository's fixed native scalar/monomial word
model. It is not a general arithmetic-circuit lower bound, a lower bound for
paid Gaussian decoders, or an impossibility theorem for coded callers. It also
does not exclude cancellation in a product `B` of different stage codes. The
terminal gauge `Q^{-1} B Q` of a complete controller needs its own proof.

The independent verifier reconstructs every binary normalizer from the frozen
ports without importing the primary normalizer implementation. It checks the
rank-two support argument for all 5,824 blocks, enumerates every one-column
row and column for three actual blocks, and rejects a diagonal-code mutation.
The identity-conjugation control has support one, so the support test does not
mistake the cancelling case for a rank-two case.

Predecessor credit remains with Dugongue's PR #4929 coded producer, Cinna
Davis's center-free construction, Cao Yifan's native word, and the retained
native and controller contributors. The new result here is the exact terminal
support gate for the actual common-line normalizers.
