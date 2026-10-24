# The complete finite Core consumes the downset allocation

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.

This is a conditional source-bound consumer argument, not a new Gaussian
identity, a physical tape implementation or a multiplication theorem. The
Full/downset theorem, Gaussian conditioning and interval producers, raw wrapper
contract and original Core boundary theorem retain their predecessor status.
The new boundary is the entire ordinary finite Core, including its prepared
Schur pages and the actual inputs of all six executed stages.

## Binding and unchanged mathematical reference

PR5018 binds Gaussian.compile_root and RawGaussian.__init__ to PR4977's
certified Full allocator. Core.__init__ has two consumers of RawGaussian:
its zero-incoming probe for each carved interior, and its final program at the
chosen common grid. Both must use the same bound class. Bind that name in a
private copy of the original constructor's globals; its code object and all
other globals and methods remain unchanged. No source module is patched.

The original carve, coordinates, reference description and matrix, exact
interior inverses, sparse couplings and exact Schur matrix depend only on the
fixed reference and geometry. They do not depend on the Full allocator.
Consequently the reference hashes, exact interior matrices/inverses and exact
Schur factors are unchanged. This does NOT assert that rounded coefficient
pages, circuit coefficients, rounded outputs or temporary widths are unchanged.
They are prepared again by the original routines under the new allocation.

## Common grid and prepared pages

Fix the original admitted geometry, maximum complex-l1 input bound Y0>=1,
target t>=1 and incoming grid F0. Let K be the original five-factor bound and
set Y*=6K^5Y0, e=2^-t/(10K^4), R_D=ceil(sqrt(cap))*Y*, and
 t_D=t+ceil(log2(20K^4)). These quantities and the required immutable-reference
accuracy do not change. In particular lower online precision does not authorize
coarser reference entries or a smaller raw input radius.

By PR5018, interior j's raw data-grid request at incoming F has form
A_j(F)=max(F,a_j) for a_j=A_j(0). It also supplies the forward and stored-inverse
error contracts against that same reference at radius R_D and target t_D.
Let P_sparse, P_boundary and P_apply be the original Core lower bounds for
sparse coupling pages, narrow two-pass boundary solve and broad Schur apply.
The new constructor selects exactly

    P=max(F0,P_sparse,P_boundary if narrow else P_apply,max_j a_j).

Hence A_j(P)=P for every final child. This includes no-interior cases (the last
maximum is omitted), partial source cells and fine incoming grids. Every
child is reconstructed, compiled and checked at P; no old provisional grid
is silently retained. A smaller child floor need not lower P: boundary,
sparse or incoming requirements can dominate.

All dyadic sparse pages and, for narrow Core, both triangular factors and each
consecutive inverse page are generated at P by the original constructor.
The reference Schur matrix is not replaced with one formed from rounded
interior inverses. The original rounded-page estimates therefore apply with
eta=2^-P, including the rounded diagonal argument to sequential inverse-page
lookup. For sparse rows with at most s entries, the pointwise error at Y* is
at most 2eta(sY*+1). For narrow boundary execution the complete complex two-pass
error is less than 2^41 p^16 eta Y*. The unchanged P_sparse/P_boundary/P_apply
lower bounds fund these errors by e and retain the residual-absorption guards.
Both real and imaginary RHS columns and all partial block batches are paid.

## Actual computed inputs and the five-factor recurrence

Use the maximum complex-l1 norm over all rows and RHS columns. Each interior
vector at bound Y* has Euclidean norm at most sqrt(cap)Y*<=R_D. The local raw
error 2^-t_D becomes less than e in complex-l1 norm by the sqrt(2) conversion.
Disjoint interior blocks do not multiply this maximum error by their count.

The narrow executed order is interior inverse; lower negative; boundary
inverse; interior forward; upper negative; interior inverse. The middle two
calls act on disjoint banks. Their local defects at their ACTUAL inputs
combine by a maximum, giving one factor error e, not a gratuitous sixth
factor or an assumption that rounded forward/inverse circuits cancel.
The broad order is the original reversed/inverted factor word, with the same
disjoint-middle argument. Denote exact factors by T_j, ||T_j||<=K. For the
computed state z_j and exact state x_j,

    ||z_(j+1)-x_(j+1)|| <= ||T_j(z_j)-T_j(x_j)||+e <= K E_j+e.

The local defect is evaluated at z_j. No nonlinear rounded operation is moved
through another axis or treated as a linear map. Thus E_5<=5K^4 e=2^-t/2.
The companion magnitude recurrence r_(j+1)<=K r_j+e, and the intermediate
middle state on its two disjoint banks, stay below Y*. This justifies every
raw and page theorem entrance inductively rather than borrowing the root
radius for later states. The proof is per RHS column and has no RHS-count
penalty in the maximum norm.

## Widths, charges and scope

Core recomputes its signed and temporary widths from the maximum of the
sparse accumulator bound, narrow boundary scratch bound 2^46 p^16 Y*, and
EVERY final raw child amplitude/temporary receipt. Sparse and boundary
products retain the 2P fractional grid. Lower P alone is not a proof that
every rational coefficient height or temporary width decreases.

The ledger includes reference/interval/weight setup, exact interior solves,
Schur formation, LU and inverse-page generation, both raw probe and final
preparation, every raw circuit invocation, sparse products, boundary products,
RHS packing/reversal, truncations and all retained backing. The inherited
boundary product count per pass is
(2ceil(n_J/w)-1)ceil(2k/w), each with 7^log2(w) scalar products. Nothing in this
binding changes that tariff. Host Fraction setup, page/address delivery and
physical backing/cleanup are explicit unpriced obligations, not zero costs.

Finite execution must use the original multi-interior fixture and report all
stage-input/page/endpoint checks. It corroborates source application and does
not establish the inherited analytic premises. No complete core/halo/global
Gaussian approximation, physical Strassen owner, native/outer admission,
selected frontier or universal fixed precision saving follows.

## Open next questions

Can the same-reference exact Schur/LU preparation and every rounded page be
produced and delivered at the intended physical tariff? Start with the exact
page identity and bit-height ledger before connecting a physical boundary
solver; count preparation, RHS gather and disposal. The present arithmetic
consumer argument cannot discharge that physical join.

Credit Nick Petalas's block-solve bound, Jose Manuel's original Full/Gaussian/
RawGaussian/Core sources and proofs, Vlado's carve/factor/Strassen lineage,
PR4186's boundary adapter, Jeremy Kothe, Chafik, Mason Hale, and the retained
source authors. PR4977/5018 attribution and frozen sources remain unchanged.
