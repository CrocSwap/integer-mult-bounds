# Historical PR234 five-stage BIT finite bill

The source471 parameter values and numerical examples below belong to the
historical PR234 predecessor. The primitive quantifiers, row accounting,
ordinary-leaf argument and inherited-constant cutoff proof are retained.
For the current source527 hybrid's finite charges, see [PROOF.md](../PROOF.md)
and the source-bound [finite_check.py](../finite_check.py). The three
byte-pinned theorem source files are unchanged.

The executable `finite_check.run` accepts the freshly reconstructed source
ledger, physical tags, independently checked scalar projection, exact current
basis-prime result, exact moment calculation and optional global lowering
result. It reads no saved execution receipt. Source expectations are checked
against those computed objects, not substituted for them. The complete
package runner is responsible for generating its inputs before this call.

## Quantifiers and inherited primitive hypotheses

Fix this candidate and an eligible odd prime q>2^80 before the input widths
n,w are chosen. All represented determinant and route exclusions lie in
{2,3,5,7}. The primitive constant C may depend on q, the fixed source recipe,
the finite bootstrap level and the retained primitive implementations. It
does not depend on n,w, ancestor values or unrelated spectator widths except
through logical volume V.

The three byte-pinned public sources supplied here are
`three-stage-cover-bit.tex`, `three-stage-cover-rows.tex`, and
`copied-centers-lemma.tex`. Their exact-tape, completed ordinary-leaf and
complete-stream hypotheses are retained. All high matrix fibers are batched;
prefix descriptor preparation has fixed polynomial cost in w and is paid
over the complete q^w target fiber. Unrelated spectators use ripple counters.
Fresh child role fields never enter the ancestor weight descriptor. Finite
low-type tables, initialization and sequential scans are charged in C.
There is no unit-cost random-access oracle or new numerical Turing-machine
constant requirement.

## Historical source471 finite recipe

Let m=120, W=23,683, E=495,304, v=1,760, R=16,643, d=m^2 and
J=20v+10R+4v=208,670. The last 4v=7,040 families pay the explicit final
complete-stream exchange; they are not equal-frame payload shears.

The check derives from the fresh word 12,858,690 weighted additions or
21,787,770 unit additions, including all six bridge families. Its
cancellation-free prefix lift is
64*37,623^3*9,430,154^2=303,094,329,841,208,644,962,256,113,408<2^98.
No old defining-integer endpoint is imposed on the F2 supplier.

The actual rational 48-dimensional route is reconstructed, eliminated and
inversely replayed: 195 additions, 44 swaps and 27 scalings, with denominator
set {1,2,3,6}. A missing addition fails reconstruction. Coordinate
permutations and embedding give the other ports and stages.

Per route, pay at most 23,707*|GL_120(F_q)| low-role transpositions and
16*(d+1)^2 high affine factors. Per good edge, pay at most 8m^2+8 elementary
normalizer wrappers. The same compiler pays all exterior completions.
There are 120 copied-center episodes. Their recursive rank-22 calls and
their scalar reads are already included in E and the scalar count; their
copy/erase and parking passes are separately paid by the complete-stream
primitive, using one additional work stream.

For a bad edge with N=2m=240, the exact inherited Gaussian fallback uses at
most 6N(N-1)+3N+6(N-1)=346,314<32m^2=460,800 children. Keep the entire
larger allowance in the moment. Coefficient preparation uses only unit
pivot inversions. Allocate 128N^3 ring operations per edge per low class:
four 8N^3 elimination/inversion allocations and sixteen 2N^3 matrix products
give 64N^3; the remaining 64N^3 pays extraction, copying, generic tests,
factor output and the bad-branch elimination. Matrix bit costs and descriptor
arithmetic are paid by the inherited primitive theorem. Invertibility testing
of each candidate low matrix additionally gets 16m^3 operations.

Overcharging every finite recipe item over every low matrix gives

    B(q) <= [unit+J*16(d+1)^2+J*(W+24)+E*(8m^2+8)
             +E*128(2m)^3+16m^3+120+E+1]*q^14400
         = 1,568,901,757,016,837*q^14400 < q^14401.

These are explicit ring/recipe counts, not single-step machine costs. All
fixed-tape, table, setup and selector constants stay in C_primitive, giving
the normalized toll C*n+C*w^(1-a_old) after increasing one finite C.
No recursive child is absorbed into this nonrecursive constant.

## Weighted induction and rows

Set c=704197288590873/10^18 and tau=1-c. Exact interval recomputation,
adding the entire 10^-16*32m^2 fallback envelope per edge, proves

    1-mu_tau > 774/10^21,
    1-mu_1 = 107421874442783/69383789062500000 > 0.

For the retained recurrence
T(n,w)<=sum_r c_r*T(r*floor(n/120),w)+C*n+C*w^(1-a_old),
take A=C*(1+1/(1-mu_1)+1/(1-mu_tau)). Induction bounds T by
A*(n+n^tau*w^(1-a_old)): the linear and stopped gaps separately pay the
two tolls; the leaves follow A>=C. Floors only decrease the child sizes.

The maximum ratio is 5/6, so four levels halve. The depth bound
4*ceil(log2(max(2,n))) changes stock, not the one-level moment. Paying all
24 temporary roles gives per-level log_q stock below 14400w+1. Add the
inherited old-leaf reserve. The new contribution is at most
57,604w*ceil(log2(max(2,n))). Borrow and restore these complete high digits;
successive residuals and the two-call ordinary wrapper reuse the reserve.
One outer row padding factor is below two; binary-radix padding costs less
than q^2 in logical volume. The temporary roles never enter the denominator W.

## Finite ordinary bootstrap and cutoff

Starting with completed ordinary a0=384599/10^10, set beta=c and repeat
a_(j+1)=(1-c)c+c*a_j exactly three times. The finite result is

    a3=704197288358392787581160456097840009769165126434639147437106139267359/10^72.

At each stage, the paid exponents are 1-c, 1-a_(j+1), c with a logarithm,
and c(1-a_j). The exact positive gaps are c-a_(j+1),
1-a_(j+1)-c, 1-a_(j+1)-c(1-a_j), and 1-c (for row fitting).

Choose a finite integer C>=1 dominating that stage's already fixed primitive,
recurrence, wrapper, row, setup, padding and previous ordinary constants.
Let delta be the minimum positive gap and

    L=ceil(max(1,36/delta^2,2*(4+ceil(log2 C))/delta)), e0=2^L.

For e>=e0, C(1+log2 e)e^(-delta)<=1/16. Indeed for t=log2 e,
log2(1+t)<=3sqrt(t)<=delta*t/2 and log2 C+4<=delta*t/2.
Thus every lower-order toll is covered and the borrowed high part fits.
Below e0 use the previously completed ordinary algorithm. A finite next
constant is C_large+C_old*2^(L*(a_(j+1)-a_j)). This choice is sequential,
not circular, and uniform in the input and complete spectators.

This proves the finite-accounting and ordinary-bootstrap step at the same
conditional theorem level as the retained public baseline. It does not claim
an independent proof of those inherited primitives, a measured universal
machine constant, or execution at every input width.
