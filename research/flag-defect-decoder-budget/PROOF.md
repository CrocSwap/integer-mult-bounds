# The rank budget for a defect in port flags

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

Nick Petalas's PR6471 proves the equal-width compatible-flag floor.
This contribution permits unequal widths and gaps in flag levels. It
quantifies the rank of a violation, proves a sharp family, and gives the
complete field-operation word for that family. The odd-cycle edge code
and elementary rank inequalities are classical; neither is claimed new.

## Declared interface

Let K be a field. Port i has dimension d_i>0 and a fixed ordered basis.
Give its basis vectors distinct increasing integer levels l_(i,a).
F_i^t is the span of vectors whose levels are at most t. Thus each port
can gain zero or one dimension at each level. The levels may have gaps.
Ordinary unequal complete flags have l_(i,a)=a for 1<=a<=d_i.

Let Z be a directed zero mask on distinct ports. A fitting matrix M has
rectangular blocks M_ij:K^d_j -> K^d_i, identity diagonal blocks and zero
blocks on Z. For a port set I, mu_K(Z[I]) is the minimum scalar fitting
rank on that induced mask, with diagonal one. Put mu(empty)=0. Let

    I_t={i: port i has a basis vector at level t},
    B=sum_t mu_K(Z[I_t]).

Define E by retaining precisely the entries of M whose target level is
strictly greater than their source level. All other entries of E are zero.
The defect rank e is rank E. This definition uses the declared adapted
bases, including their complements, not just the abstract flag subspaces.
No entry of a forbidden block or a diagonal identity is changed.

## Theorem

The exact minimum among compatible matrices, those with E=0, is B.
For every fitting M, compatible or not,

    rank M >= B-rank E.                                  (1)

Consequently a query factorization M=DQ through q field coordinates obeys
q+rank E>=B. A claimed saving of s query coordinates below B needs at
least s defect rank in every choice of adapted port bases and flags.
The defect is a diagnostic quantity, not a separately free physical channel.

To prove the compatible minimum, order coordinates by level. The matrix
is block upper triangular. At each occupied level t its diagonal block
fits Z[I_t], so it has rank at least mu_K(Z[I_t]). The nonzero-minor
argument in PR6471 gives rank M>=B. Conversely choose a scalar minimum
independently at each level and set every cross-level entry to zero.
This has identity diagonal blocks and all required zeros. Its rank is B.
Conjugate by the prescribed port bases to realize the same construction
for arbitrary given flags. This includes gaps and unequal dimensions.

For an arbitrary M, A=M-E is compatible. The standard inequality
rank A<=rank M+rank E proves (1). Thus the coefficient of the defect
rank is exactly one. The next family proves that it cannot be reduced.

These formulas use scalar minima over K. Flags or bases available only
over an extension L give minima over L. No base-field substitution is
implicit. The result gives no efficient general minrank or flag algorithm.

## A sharp defect of every positive rank

Fix n=2k+1>=5 and s>=1. The zero mask is the cycle C_n: only diagonal
and neighbor blocks are allowed. At each port put two coordinates for
each of s copies, one for each incident edge. Let Q sum the two source
coordinates on each edge in each copy. Let D copy each edge value to
its two incident output coordinates. Then M=DQ has diagonal I_(2s),
zero nonneighbor blocks, and rank ns over every field. Indeed each
edge contributes one nonzero all-one two-by-two block on a disjoint
pair of coordinates. This is the classical edge representation.

For clarity, the scalar cycle minimum is k+1 over every field. A cover
by k disjoint edges and one vertex gives rank k+1. For the lower bound,
the odd-indexed ports 1,3,...,2k-1 form an independent set of size k.
If a fitting factorization had rank k, their encoder vectors and decoder
rows would be dual bases. Port 0's encoder and decoder then use only
the first basis direction, and both coefficients are nonzero because
its diagonal is one. The nonneighbor entry from row 0 to column 2 forces
the first coefficient of encoder 2 to vanish. Encoder 2 can use only
the first two basis directions, so its second coefficient is nonzero;
its diagonal forces decoder 2's second coefficient to be nonzero.
Repeat using the nonneighbor entry from row 2 to column 4. Induction
forces encoder 2k-2 to use only the last basis direction. Decoder 2k
also uses only that last dual direction, with nonzero coefficient.
Their nonneighbor entry is then nonzero, a contradiction. This proof
uses directed zeros and works in every characteristic.

The compatible floor is therefore 2s(k+1)=ns+s. Inequality (1) proves
that rank E>=s for this M under EVERY local complete flag and adapted
basis. To attain s, order copies consecutively and alternate the two
incident edge coordinates at successive ports. Every cycle edge except
the closing edge then connects equal levels in each direction. The
closing edge has one entry below the level order in each copy. These
s entries have distinct rows and columns, so rank E=s. Thus

    min_(all local flags and adapted bases) rank E = s,
    rank M = B-s.

This exact result holds for all odd n>=5, all s>=1 and every field.
It proves the quantitative bound is sharp at arbitrary defect rank.
It does not assert a new unrestricted vector minrank theorem for C_n.
The edge-code rank and scalar cycle minimum are established context.

## Literal word and its complete field-operation bill

Sources x are read-only. Outputs y can have arbitrary initial values.
For each edge/copy with source fields a,b and output fields u,v, use one
reusable scratch field q. With q initially zero, execute

    q += a; q += b; u += q; v += q; q -= b; q -= a.

After each group, q is zero, the sources are unchanged, and the two
outputs have received a+b. The complete word has 6ns field additions,
12ns operand reads and 6ns destination writes. There are ns encodings,
2ns output uses and ns complete uncomputations. Scratch is one field,
not ns retained fields. The initial clean field is an explicit premise.

If q must instead start with arbitrary dirty value z, first execute
u-=q and v-=q before the same six operations. This costs 8ns additions,
16ns reads and 8ns writes, and restores q=z after every group. Both
output increments are still exactly a+b and independent of z. No CLEAR
of a nonzero field, hidden transcript or unpaid initialization is used.
All 2ns output coordinates are updated once per complete code application.

For exact integer data with initial absolute values at most H, all clean
word values are bounded by 3H. The dirty word has q=z+a+b, intermediate
outputs y-z, and final outputs y+a+b, so the same 3H bound holds at every
event. It is sharp. A signed width w with 2^(w-1)>3H is sufficient.
No division or fractional rounding is needed. These are indexed field
operations. Physical movement, control, record precision and native
recursive costs have NOT been priced. A direct four-ADD-per-edge program
also applies the same matrix without exposing Q. Thus fewer abstract
queries do not imply fewer scalar operations or a physical speedup.

## Evidence and limits

The finite verifier independently enumerates small binary fitting matrices
with unequal widths and checks both compatible minima and (1). It tests
gapped levels, directed masks, fields 2,3,5, explicit sharp words and all
binary local two-dimensional bases for C5. Literal ADD traces verify
source preservation, arbitrary dirty output/scratch behavior, every range
bound, the full operation invoice and omitted-operation failures.

The written proof supplies the unbounded result. The finite corpus is
corroboration, not independent human or proof-kernel acceptance. No
native supplier, profitable actual caller, complete physical invoice,
new kappa or selected-frontier change is claimed. All five selected
assumptions remain. The useful next task is a source-bound decoder that
pays for the required defect and still wins after its full caller costs.

Credit Nick Petalas / PR6471, ywz65 / PR2541, Aaron Wang / navinor /
PR825, Cinna Davis and the retained geometry/native/compiler lineage.
Bukh, Cox and Blasiak retain the fractional Haemers framework credit.
See Bukh and Cox, [On a fractional version of Haemers' bound](https://arxiv.org/html/1802.00476v2).
No global literature-priority claim is made.
