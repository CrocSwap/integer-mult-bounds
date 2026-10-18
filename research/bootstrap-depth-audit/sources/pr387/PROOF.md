# Fixed six-level bootstrap and the retained outer ceiling

## Pinned interfaces and acyclic composition

The base completed ordinary saving is a0=384599/10^10. The bit and complex constructions and paid profiles are unchanged from #384. The complex coarse saving is selected with finer rational precision as established below. Use s=(1-beta)b-10^-24 with beta=eta=10^-18. Exact comparison gives a0<s<c and s<(1-beta)b<b<1/32.

The inherited completed ordinary contract handles arbitrary widths, two complete chunks and arbitrary complete spectators, restores preceding row coordinates, performs required high-digit borrowing internally, and uses a fixed finite tape set. This is stronger than an F2 matrix identity. It is retained conditionally, not proved anew here. Its use for stopped leaves, weighted wrappers, routing and high-part exchanges is explained in the pinned reviewed PR185 proof.

For j=1,...,6 define A_j using the stopped coarse construction at atom width w=ceil(e^s), using only completed A_(j-1) for ordinary leaves, routing, peeled atoms, bounded stopped leaves and high-part exchanges. All scalar adapters, selectors and rare-class fallback work stay paid. Coarse recursive children decrease width; ordinary calls decrease j. A0 never calls a new level. Six is an absolute fixed depth.

The retained stopped-leaf estimate at each fixed level is

`T_j(e)/V = O(e^(1-s) + e^((1-s)^2+s(1-a_(j-1))) + e^s log(e))`.

Therefore `a_j=(1-s)s+s*a_(j-1)=s-s^j(s-a0)`. Induction gives `a_(j-1)<a_j<s<1-a_j`. The checker validates the recurrence, closed form and four exact gaps at all six levels:

- atom: s-a_j;
- borrowing: 1-a_j-s;
- remainder: 1-a_j-s(1-a_(j-1));
- stock: 1-s.

These are strictly positive fixed rationals.

## Finite cutoffs and constants

At each level choose a finite C>=1 dominating its already fixed primitive, recurrence, wrapper, row, setup, padding and previous ordinary constants. There is no claim that the executable has measured C. Let ell>=1 be an integer with C<2^ell, and delta the minimum stage gap. Choose

`L=ceil(max(1,36/delta^2,2*(4+ell)/delta))`, `e0=2^L`.

For t=log2(e)>=L, `log2(1+t)<=3*sqrt(t)<=delta*t/2` and `log2(C)+4<=delta*t/2`. Hence `C(1+log2(e))*e^(-delta)<=1/16`. Each lower-order term is absorbed; their fixed multiplicity may be included in C. Below e0, use the preceding completed algorithm. A finite next constant can be chosen at least `C_large+C_old*2^(L*(a_j-a_(j-1)))`. This choice is sequential, not circular, and independent of input width.

The checker implements this cutoff formula, asserts both sufficient inequalities, and exercises representative bit bounds 1, 80 and 210001 at every stage. Those instances check the implementation, while the algebra above proves the statement for any fixed dominating C. Zero gap and invalid bit bound are rejected.

## Restored rows and fixed tapes

Each inner completed call borrows from its two supplied chunks, keeps all outer fields as complete spectators, and restores its row coordinate before returning. Binary-radix padding and tape/program counts multiply only through six fixed levels. The parent therefore receives the same completed endpoint interface and does not need an external row multiplier. No raw reversal or free weighted operation is assumed. The retained external 252 allowance is unused slack, not an estimate of the new algorithm's internal reserve. The complex finite envelope and external row coefficient 20161 remain unchanged.

This is the same conditional fixed-depth reasoning in the reviewed PR185 mechanism, extended here from three levels to six. It is not an assertion that the previous review already checked six levels or that an all-size tape compiler was machine-verified.

## Exact witness and grid ceiling

Use a=a6, q=a(1-2 eta), epsilon=(1-eta)/(1+q). The pinned outer assembly verifies all 47 strict constraints, including all seven performance margins; their minimum is M=epsilon*q. The result is the greatest 10^-18 multiple strictly below M. The next point, zero eta, zero beta and unit beta are rejected. A separate regression reproduces the former three-level witness at its original coarse input; five levels at the same slacks do not reach the new grid point.

Every valid witness in this unchanged outer formula has a<b and positive eta, so `M<a/(1+a)<b/(1+b)`. Exact comparison proves

`kappa < M < b/(1+b) < kappa+10^-18`.

Consequently the next grid point is impossible within this outer formula at the fixed complex coarse input, including with further finite bootstrap levels. This is not a bound for different suppliers or a different assembly. All inherited #384 and completed-ordinary-interface conditions remain explicit.

## Certified coarse-root precision

The unchanged PR384 complex profile has m=73, stock 14727 and deficit 2496. Let

`b=999632926176283805553/10^24`, `u=b+10^-24`.

Both independent rational engines prove `moment(b)<1<moment(u)`, including the unchanged positive bad density 10^-16 and all `32*m^2*sum(H.values())` rank-one fallback children. Decimal arithmetic only proposes the two rational endpoints. The two separate outward rational calculations admit b and reject u. All coefficient/geometry/finite assumptions remain the same.

Using b rather than its previous 18-place truncation gives the strict six-level witness `kappa=199726931618167/200000000000000000`, exactly 10^-18 above the preceding six-level witness. This is removal of an intermediate rounding loss, not a change to a circuit or the fallback density.

Finally exact arithmetic proves `u/(1+u)<kappa+10^-18`. The true paid-moment root lies below u, so further root precision, bootstrap depth or positive-slack choices cannot reach that next final grid point within the retained outer formula and this unchanged paid profile.
