# A matching floor for scalar port decoders

This is a rational scalar-factor theorem with a binary full-port tariff. It
does not identify scalar factors with legal native calls. All transposes below
are ordinary transposes.

## 1. Contract and matching lemma

Port i carries a binary subspace E_i with a nondegenerate restriction of the
ambient bilinear pairing; write d_i = dim E_i. A scalar decoder is a finite
factorization

    K = A diag(c_t) B^T,       c_t != 0,

over the rationals. Zero terms may be discarded. For term t define

    L_t = sum_{i: A_it != 0} E_i,
    R_t = sum_{i: B_it != 0} E_i,
    rho_t = rank_F2(pairing restricted to L_t x R_t),
    C = sum_t rho_t.

The tariff includes each touched port's complete space, not just its original
line label. Rational magnitudes, signs and denominators do not enter this
tariff. They do enter the exact scalar identity.

Let J be any port set for which K[J,J] is nonsingular. Then A[J,:] has full
row rank |J|: otherwise its product with diag(c_t) B[J,:]^T could not have
that rank. Choose a nonsingular square column minor of A[J,:]. A nonzero
determinant has a nonzero Leibniz summand. It supplies an injection

    f : J -> terms,             A_i,f(i) != 0.

This is the only matching assertion needed; it follows from exact scalar
rank, not from a finite search or an assumption of generic coefficients.

Suppose each term has equal complete source and target port-space spans:

    L_t = R_t.

This includes identical supports, but permits different supports and different
coefficients. Since A_i,f(i)!=0, L_f(i) contains E_i. Equality of the spans
puts E_i in R_f(i) too. Choose bases on both sides extending a basis of E_i;
the pairing matrix then contains its nonsingular d_i-by-d_i Gram submatrix,
hence rho_f(i) >= d_i. The terms f(i) are distinct, and every remaining rho_t is nonnegative. Therefore

    C >= sum_{i in J} d_i.                         (1)

The proof permits any finite number of terms, arbitrary rational entries and
nonzero weights, even denominators and negative weights. In particular it
includes Gram factors A=B with signed quarter weights. Positivity,
half-integrality, identical supports and a fixed factor menu are unnecessary
here. The spans are of **complete port spaces**, not just original line labels.

The nonsingular principal-set hypothesis is essential. In a masked decoder
the diagonal is a common c!=0 and K_ij must vanish for nonorthogonal distinct
port spaces; orthogonal pairs are free. A pairwise nonorthogonal J forces
K[J,J]=c I. A set containing free pairs need not do so. Thus (1) does not
contradict the E8 Gram savings on line masks with free entries, or imply a
general floor on every plane mask.

## 2. Exact retained covers

The selected labels and the unchanged PR2297/PR2041 partitions are authenticated
through SOURCES.json. No predecessor executable is imported. Every group is
orthonormal, and every port in a group is assigned that group's whole space.

**PR2297:** 110 ports have dimension five; two have dimension two. The exact
group mask has no orthogonal pair, including the residual pair against the
five-frames. (The five-versus-five case also follows from 5+5>9.) Consequently
J is all 112 ports and (1) gives

    C >= 110*5 + 2*2 = 554.

The direct scalar identity, one term per port, costs exactly its d_i. It has
equal spans and attains 554, so this minimum is sharp in the stated class.

**PR2041:** there are 37 three-frames and one line. Among the three-frames the
only orthogonal group pairs, in zero-based candidate group order, are

    (6,13), (7,12), (9,19), (22,25).

Discard the line and groups 6,7,9,22. The other 33 three-frames are pairwise
nonorthogonal. Take all three ports of each: K[J,J]=c I_99 and

    C >= 99*3 = 297.

This is a lower bound, not an asserted optimum. The direct 112-port identity
costs 334. The small checker verifies the explicit 33-group witness; it does
not need to certify that no larger clique exists.

## 3. Consequence under the retained coverage law

In the same portwise, nine-stage, four-bank-pair planning law used by the
predecessor audit, there are 8/9 live families per port per call. Even before
native overhead, the available rank deficit is

    D = (8/9) sum_all_ports d_i - C.

For the actual mixed covers, (1) therefore gives

| Cover | Unpaid budget | Cost floor | Deficit upper bound |
|---|---:|---:|---:|
| PR2297 | 4432/9 | 554 | -554/9 |
| PR2041 | 2672/9 | 297 | -1/9 |

Both are unfavorable already at saving a=0. With no negative extra charges
and children of ranks at most the parent width, the normalized recursive
moment cannot fall below one for a>=0. Thus these equal-span decoders
cannot supply a positive saving under this coverage model. This is a more
limited claim than rejecting every possible k-port mechanism.

In particular, the PR2041 conclusion uses its literal residual **line**, not
the unconstructed uniform-three completion. The latter's budget is 896/3,
which exceeds 297, and is not excluded by this particular lower bound.

## 4. A necessary asymmetry budget

For an arbitrary asymmetric decoder on the same J, define

    delta_t = max({0} union {d_i-rho_t : i in J, A_it != 0}).

Using the same matching, d_i <= rho_f(i)+delta_f(i). Hence

    C >= sum_{i in J} d_i - sum_t delta_t.          (2)

If delta_t>0, some source-side E_i cannot be contained in R_t: otherwise
its nondegenerate Gram minor would force rho_t>=d_i. Since E_i is contained
in L_t, such a term has **unequal complete port spans**. Mere unequal supports
or unequal spans do not guarantee a positive delta.

For PR2297, every nonzero term has rho_t>=1, since every nonempty source/target
port pair has a nonzero pairing. Also d_i<=5, so delta_t<=4. Positive saving
would require the integer C <=492, hence sum delta_t>=554-492=62. Therefore
**at least 16 terms must have positive delta_t** and hence unmatched spans.
A repair with at most 15 such low-rank unmatched-span terms cannot work, irrespective of coefficients or
denominators. This is a necessary condition, not an existence claim at 16.

For PR2041 the exact budget similarly requires at least one positive-delta
term relative to its 99-port set. The checker records these integer bounds;
neither condition supplies a favorable asymmetric construction.

## 5. Evidence and remaining obligations

The universal assertions are the written determinant/matching and Gram-minor
arguments. Finite evidence separately authenticates both covers, checks every
group-pair tariff with two binary-rank implementations, records the principal
sets, and reproduces the direct 554/334 charges. Exact rational controls include
half-weight Gram, unequal factors with equal supports, unequal supports with
equal spans, and signed quarter/third weights; all 512 binary 3-by-3 matrices
test the rank-to-matching implementation.

Failure controls cover missing matching, unequal spans, scalar diagonal and
cross-entry failures, degenerate port spaces, line-only underpricing and an
invalid full-rank inference across a free pair. They illustrate why each
premise matters, not independent proofs of the theorem. Artifact tests cover
read-only Git-free export, authenticated input corruption, typed receipt
corruption and overwrite refusal. Assertions are not used for acceptance.

No arbitrary-unmatched-span cost floor, native implementation, hosting, precision,
all-size compiler, outer analytic transfer, proof-assistant verification or
complete multiplication theorem is established. The selected supplier and
kappa are unchanged. This closes a scoped algebraic escape; it does not justify
expanding a family without a favorable complete boundary/cost ledger.

Credit: Sagar Thakrar/PR2532 supplies the k-port masks, 2-integral floors and
nonorthogonal-clique lead; Cinna Davis supplies PR2297/PR2041; Adam Gall/PR1889
and Philippe Van Velzen supply the mask/full-port tariff foundations; Tekalign/
PR2782 supplies the related positive half-integral Gram gate. Adam Gall's
`research/p112-matched-frame-copy-floor` treats a different line mask, permits
matched label spans, and excludes terms of rank at most four via a
characteristic-zero lift. Here the principal-set argument has no term-rank cap
but requires its full-port nonsingularity premise. The determinant
matching argument is elementary. New source-bound application and exposition:
Arham Tahir, with substantial OpenAI Codex assistance. Apache-2.0.
