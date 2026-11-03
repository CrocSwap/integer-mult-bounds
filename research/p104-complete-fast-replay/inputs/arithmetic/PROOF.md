# Bounded arithmetic for the retained exponential

The exact baseline is Nick Petalas's PR6395, which follows ywz65's integer
Taylor method. It returns the same endpoints as the retained source:

    S(x) = sum(j=0..48) x^j/j!
    R(x) = (x^49/49!)/(1-x/50)
    [S(x), S(x)+R(x)], 0 <= x < 1.

This result changes that numerical contract. It contains the original interval
with dyadic endpoints. It does not claim equal rational endpoints.

Put D=2^b, a=floor(Dx), c=ceil(Dx). Thus 0<=a<=c<=D. Start the lower and
upper term integers at D. At step j, compute

    L_j = floor(L_(j-1) a/(Dj))
    U_j = ceil(U_(j-1) c/(Dj)).

Induction with nonnegative factors gives L_j/D <= x^j/j! <= U_j/D.
The sums through j=48 therefore enclose S(x). Next compute

    V = ceil(U_48 c/(49D))
    W = ceil(50 D V/(50D-c)).

The denominator is at least 49D. Monotonicity in both nonnegative arguments
gives W/D >= R(x). Adding W to the upper sum proves containment of both
original endpoints for every supported argument and precision.

## Storage and enclosure width

Each term integer is between 0 and D. Each sum is at most 49D. The largest
recurrence product is at most D squared, apart from a fixed factor 50 in the
tail. The output denominators divide D. After the initial argument division,
all arithmetic therefore has O(b) bits, independent of the input denominator.
The input capacity is 16,384 bits; b is an integer from 8 through 4,096.
Python allocates integers dynamically. This is an arithmetic size bound, not
a fixed-heap implementation or a physical bit-cost certificate.

For a quantitative error bound, set t_j=x^j/j!. At j=1 each term error is at
most 1/D. If an error at j-1 is at most 3/D, the error at j is at most
(3/j + 1/j + 1)/D <= 3/D for j>=2. Here the second term bounds argument
rounding, because t_(j-1) and the integer term divided by D are at most one;
the last term bounds the floor or ceiling. Each sum differs from S(x) by at
most (1+47*3)/D=142/D. The next-term error is at most 3/D. The geometric
factor is at most 50/49. Changing its argument by 1/D changes the tail by
at most 50/(49 squared D), using t_49<=1. Final ceiling adds at most 1/D.
Thus the upper tail error is less than 5/D, and the new interval width is
at most R(x)+289/D. The deliberately loose constant is valid on the full
stated domain, including c=D.

## Bounded logarithms

For a positive integer rank r, write r=2^e m with 1<=m<2. The source uses
log(r)=e log(2)+log(m). For each term let z=(m-1)/(m+1), so 0<=z<=1/3.
Its finite interval is

    [2 sum(j=0..79) z^(2j+1)/(2j+1),
     2 sum(j=0..79) z^(2j+1)/(2j+1) + 2 z^161/(161(1-z^2))].

The implementation first rounds z outward on the D grid. It rounds its square
outward and uses the lower or upper square to advance the corresponding odd
power. Each division by 2j+1 is rounded in the matching direction. Induction
bounds each source power and term. After 80 terms, the power bounds enclose
z^161. The upper square is strictly below one for b>=8 and z<=1/3. The stated
positive geometric tail is increasing in both power and square, so rounding
its division upward encloses the source tail. Nonnegative combination with e
preserves containment. Each log output denominator divides D. The rank capacity
bounds e, so intermediate sizes are O(b+log(e)) after initial argument division.
The exact 80-term contract and its tail are retained, rather than borrowing a
different logarithm engine's truncation assumptions.

## Complete caller and precision

The new Moment object follows the retained h_interval and signed moment
formulas. It uses enclosed logarithms, exact rational reciprocals and
sign-aware sums. It receives its exponential function explicitly. Both modes
use that same object. Tests compare it directly with the original source,
then compare every rank power with its original exact interval. All 108 new
exponential invocations must also contain the exact PR6395 result at their own
argument. The changed log arguments are not claimed to equal the source inputs.

The complete PR6453 price module is retained through PR6505. That predecessor
changes only root search to an independently checked adjacent-grid certificate.
The current change supplies the second engine through its explicit loader
argument. No module is patched. All source price, monotonicity, strictification,
compiler and 54 strict plus four functional outer checks run. The entire
serialized complete_cost object must equal the original source receipt.
Precision 160 passes. Precision 64 is rejected by the same scientific path.
The complete displayed receipt first passes at 124 bits; 123 fails. Doubling D
refines every outward operation and narrows the argument intervals. Induction
therefore gives nested term, log, exponential, reciprocal and moment intervals.
Once the source signs and displayed endpoint cells agree, all finer precisions
also agree. The adjacent checks certify this boundary for this exact receipt,
not a universal minimum for other invoices.
The primary interval engine is unchanged and remains separate.

The verifier tests actual floor-upper, missing-tail and omitted-term code
mutations against the exact baseline. A small tail cannot be dropped merely
because the displayed caller result survives. All source hashes are checked
before import, and all guards run under optimized Python.

## Scope and credit

No paid rank, target credit, physical word, compiler parameter or kappa changes.
Native and caller receipts are pinned inputs, not newly regenerated proofs.
The existing five framework assumptions remain. The interval method is standard;
Ali Romman with substantial OpenAI Codex assistance supplies this source-bound
contract, proof, code and verification. Apache-2.0. Nick Petalas, ywz65, zxv,
Cinna Davis, Cao Yifan, Jacob Alan Sussman and the retained construction lineage
keep their credit. The source files and their notices are unchanged.
