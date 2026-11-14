# Independent audit of capped dyadic interiors and local gauges

This audits `work/phase_assembly_ultra/CAPPED-INTERIORS.md`. The cap is valid with the exact already-rounded matrices. The conclusions below are analytic/interface claims; they do not independently certify the final exponent ledger or simultaneous tensor routing.

## 1. Capped dyadic carving

Let W be the common retained physical half-bandwidth, and choose the cap

`Bcap=2^floor(log2(Bmax))`, so `Bmax/2<Bcap<=Bmax`.

Inside each original physical phase cell of length L, reserve its first and last W vertices as boundary. If L<=6W, declare the cell wholly boundary. Otherwise, while remaining length R>4W, choose

`B=min(Bcap, 2^floor(log2(R-W)))`,

retain the next B vertices as an interior, then the next W vertices as boundary, and decrement R by B+W. Declare the final R<=4W vertices boundary.

There are `O(L/Bcap+log Bcap)` interiors: while the cap is active, each step removes at least Bcap vertices; after it ceases to be active, the remaining length halves at each step. Every interior length is dyadic and at most Bcap. Every interior produced by the loop is longer than W; two successive interiors are separated by at least W retained coordinates.

Total boundary count per original cell is

`O(W(L/Bcap+log Bcap))`.

Since original cell lengths are Theta(d), total boundary density is

`O(W/Bcap + W log Bcap/d)=O((W/Bcap) polylog p)`

when Bcap<=d. The same selected-input and target-output physical period cuts must be preserved. A clipped endpoint cell of O(W) length is wholly boundary.

Interior elimination only fills between the adjacent boundary groups of one interior. Each group has O(W) vertices: inserted groups have W; an end remainder has at most 5W after joining the reserved end. Hence scalar Schur half-bandwidth remains O(W), independently of the cap and the number of pieces. No retained matrix coefficient is changed by this new partition.

## 2. Narrow Gaussian: exact recentering of the existing rounded weights

In one original phase cell, beta_i=theta*i-c and

`log a_i=-a(1/4-beta_i^2)/theta`.

For any two coordinates i,j in that same cell,

`log(a_i/a_j)=a(i-j)(beta_i+beta_j)`.

Since both beta values lie in [-1/2,1/2),

`|log(a_i/a_j)|<=a|i-j|`.

Thus a capped interior of at most Bcap vertices has ideal weight range at most exp(a Bcap), even when the absolute full-cell gauge has range exp(O(ad)).

The actual matrix uses already-rounded positive weights ahat_i. Suppose, as ensured by the retained high-precision setup,

`(1-epsilon) a_i <= ahat_i <= a_i`, with epsilon<=1/2.

Then for an anchor m in the capped interior,

`(1-epsilon) exp(-a Bcap) <= ahat_i/ahat_m`

` <= exp(a Bcap)/(1-epsilon)`.

Replacing ahat_i by `ahat_i/ahat_m` in both diagonal factors of

`A=diag(ahat) Ghat diag(ahat)^-1`

is **exact**. It changes neither A nor the fixed globally rounded H. These ratios must be formed in coefficient setup; the data circuit must not apply the full-cell diagonal and hope to cancel it later. One may anchor at the maximum ahat in the piece to make the direct diagonal contractive and its inverse at most `2 exp(a Bcap)`.

The old setup provides absolute error below `4*2^-P` and ideal minimum at least exp(-a/(4theta)). It suffices that

`4*2^-P exp(a/(4theta)) <= epsilon`.

In the retained family a=Theta(log p), theta^-1=O(d), d=p^epsilon0 with fixed epsilon0<1, so ad=o(p). The existing P=Cp setup precision easily gives epsilon<=2^-cp. The **ad cost occurs in offline coefficient accuracy**, not in the runtime norm of the recentered diagonal. It is not multiplied by the number g of simultaneously executed axes. More explicitly, if the raw relative error is delta0<=4*exp(a/(4theta))*2^-P, then an anchored ratio has relative error at most 2delta0/(1-delta0). A g-fold product of anchored diagonals has error bounded by a polynomial factor times g*delta0*exp(O(g*a*Bcap)). Thus the needed precision is P>=p+O(ad+g*a*Bcap+log g+polylog p), rather than p+O(g*a*d). Both added power terms are o(p) in the proposed parameter family.

## 3. Broad forward Gaussian: local gauges

Use the target-grid notation from FORWARD-SMALL-A-AUDIT.md. With lambda=1/rho, b0=pi/alpha^2, original phase c, and an anchor m in the capped interior,

`delta=(1-lambda)m-c`, `x=i-m`, `y=k-m`.

The exact split is

`Dcol(i)=exp[-b0((1-lambda)x^2+2delta*x)]`,

`Drow(k)=alpha^-1 exp[b0 lambda(1-lambda)y^2+2b0 delta lambda*y-b0 delta^2]`,

with a fixed Toeplitz kernel `exp[-b0 lambda(i-k)^2]`.

Throughout the original selected-target phase cell, `beta'_i=theta*i-rho*c` lies in [-1/2,1/2). Therefore

`d(log Dcol)/di = -2 b0 lambda beta'_i`,

`d(log Drow)/dk = 2 b0 lambda^2 beta'_k`.

Their absolute slopes are at most b0 and b0 respectively. Both diagonal logarithmic ranges on the capped block are at most `b0 Bcap`. At the anchor, Dcol=1 and Drow=alpha^-1 exp(-b0 delta^2), so their absolute values also have logarithmic size `O(b0 Bcap+log alpha)`.

If a globally rounded broad block was already defined using a different anchor, use exact constant ratios to recenter its two diagonals: divide the column diagonal by its value at m and multiply the row diagonal by the same value. Ideal changes of anchor differ only by reciprocal constants, since the derivatives above are independent of m. Uniform relative coefficient error changes the range by only O(1), just as in the narrow case. This preserves the already-defined rounded block exactly. Alternatively the broad block can be initially defined with the capped anchor, using one globally specified rounding construction.

Holes remain boundary. The completed narrow and broad interior inverse bounds and the completed global/Schur norm bounds proved earlier do not depend on the cap: every new interior is still a contiguous principal block of the same original phase matrix.

## 4. Group guard and circuit count

Each capped narrow diagonal contributes at most `a Bcap+O(1)` to the logarithmic norm; the broad contribution `O(Bcap/alpha^2+log alpha)` is smaller. Shallow Toeplitz circuit amplification contributes polylog(p) per axis. The number of capped blocks per line does not multiply these bounds: they are disjoint direct-sum blocks and their circuits run in parallel, padding completed smaller circuits with identity gates.

Consequently g simultaneously executed axes require

`O(g a Bcap + g polylog p)`

extra logarithmic precision. With `Bcap<=p^b`, `g<=p^beta`, a=Theta(log p), and beta+b=1-r-zeta with r,zeta>0,

`g a Bcap=O(p^(1-r-zeta) log p)=o(p)`.

In particular no remaining full-cell term g*a*d may be charged after exact recentering. Offline accuracy still needs to dominate ad=o(p), as above.

## 5. Schur solves and whole-group ordering

For the narrow matrix, strict row dominance is inherited by any interior elimination, so all completed Schur and inverse norms remain polynomial under the cap.

For the broad matrix, completed Schur/inverse norms follow from the square identity-hole completion and polynomial principal-interior bounds in FORWARD-SMALL-A-AUDIT.md. To obtain uniform norms for a banded online factorization, eliminate **whole boundary groups** of W to O(W) vertices, rather than appealing without proof to scalar prefixes inside one group.

After all interiors and a prefix of whole boundary groups are eliminated, the eliminated set is a direct sum of one physical contiguous prefix and disjoint future interiors: each remaining full group contains at least W uneliminated coordinates, blocking every width-W connection across it. The same holds after adding the next whole group. A physical prefix reduces, under selected/hole ordering, to the small-b normalized Gaussian block plus identity hole columns, so it has polynomial inverse norm. Each future interior also has polynomial inverse norm. Thus every required eliminated-set inverse is polynomial, uniformly in the number of pieces.

At the final group on a full periodic line, use the already-established full periodic H inverse bound instead of a nonperiodic-prefix bound. For a clipped principal window the complement-gap condition excludes wrap edges, so the prefix statement applies directly. Each block pivot inverse is a principal block of the inverse after adding that group. Block Schur entries are bounded by `H+H H_EE^-1 H`, hence polynomial. There are only O(1) neighboring boundary groups in a band row. The resulting block-L and block-U norms are polynomial; their full inverses are polynomial as well, from `L^-1=U S^-1` and `U^-1=S^-1 L`. A scalar expansion inside a group is unnecessary: precompute its dense O(W)-square inverse and apply the block updates to batches by Strassen.

This whole-group order prevents the subtle gap in which a partially consumed separator of fewer than W vertices permits a connection to the next interior. It preserves the claimed batched boundary exponent and is unaffected by capped subdivision.

## Scope

The capped local-gauge change is valid. The listed exact controls check carving, analytic slope identities and preservation of the already-rounded narrow matrix. The final recurrence arithmetic and tensor routing remain separate reviewed components.
