# Exact rational scalars in an all-column C word

## 1. Interface and result

Ali Romman's [#7834](https://github.com/CrocSwap/integer-mult-bounds/pull/7834),
at `4f0c67d5bb41d4af5501dcd40b3b388b35e0ff02`, tests finite all-column
Gaussian C identities and executes a recursion on complete independent rows.
Its scalar alphabet contains ADD, SUB, HALF, NEG, scalar i and CLEAR.
Its column gates contain positive C, X, S, CZ, CNOT and columnwise i.
Columnwise i acts by i^f at multiplicity f; scalar i acts once.

Add the fixed scalar instruction

    SCALE(a,b,q): z -> (a+i b) z / q,

for fixed integers a,b and fixed positive integer q. Coefficients belong to
the finite program: no payload-dependent divisor or advice is admitted.
Let N>=2 be its base rank, W>=2 its productive-row count, Z>=0 its private
row count and J>=1 its instruction count. A paid instruction applies C on
one base coordinate, hence on f disjoint coordinates at multiplicity f.
The required endpoint is C^(tensor Nf) separately on every arbitrary
productive field, for all f>=1, with complete spectators. Private rows enter
zero. Append CLEAR on every private row at exit if necessary and include
these events in J; no private field receives productive credit.

**Result.** The rational alphabet has an exact finite all-column semantic
test. An accepted word has an exact common-grid realization in the same row
recursion, with O_word(p+h+log(h+1)) bits per real component for p-bit inputs
and requested rank h. Root odd scaling and unscaling cost
O_word(V log(h+2)); each local scalar occurrence costs O_word(V), including
complete scans, head returns and scratch retirement. The paid C count,
productive width and recursive rank profile do not change.

The row entry must contain at least W^d complete independent rows, where
d=floor(log_N h). Padding to the next multiple of W^d costs a factor below
two and is removed only after its zero outputs are checked. Descendants
receive no new padding. In the source address geometry, the required
row prefix is reserved from genuine unselected bits. If it does not fit,
retain the source's literal fallback; no auxiliary field is counted as an
arbitrary productive input.

This is a conditional grammar/numerical extension of the named recursion.
Its disjoint-XOR provider, row placement, scalar service and parking retain
their physical contracts. No funded word is materialized and no new
multiplication saving is asserted.

## 2. Exact all-column semantic test

For each independent productive input, express every output as a finite
sum c_A A^(tensor f). Here c_A is Gaussian rational and A is a nonzero
Gaussian-dyadic one-column matrix. Scalar operations combine coefficients;
column operations left-multiply A. Collect equal matrices exactly, retaining
absolute phase. Accept the prescribed productive expressions and zero
private expressions. Sufficiency follows by instruction induction. The common
row-major/column-major permutation is identical for every term and target;
complete exterior coordinates tensor with the identity.

For necessity, take the distinct nonzero matrices A_1,...,A_m in an output
difference. A complex linear functional L can make all L(A_i) nonzero and
distinct: the excluded functionals form finitely many proper hyperplanes.
Applying L^(tensor f), f=1,...,m, gives a Vandermonde determinant

    (product_i L(A_i)) product_(i<j)(L(A_j)-L(A_i)) != 0.

Every coefficient vanishes. The inherited #7834 argument allows arbitrary
Gaussian-rational coefficients; dyadicity is unnecessary. A check at f=1
alone cannot distinguish scalar i from columnwise i.

Extend unary program codes with signed numerator fields and positive q.
At code length L, N,W,Z,J and coefficient magnitudes are O(L). Pathwise
rational heights are polynomial in L; there are at most W 2^J matrix terms
per row and 2^N by 2^N entries per key. Exact arithmetic, even with pairwise
key searches, costs 2^O(L) poly(L). Enumerating codes through a sufficiently
small fixed multiple of log(p+2) has polynomial cost in p. A fixed rational
funding price uses a fixed integer-power test. Every fixed rational word
eventually appears. This proves effective startup, not existence of a funded
word at a specified price.

## 3. One common odd denominator

Write each denominator q=2^v q_odd and set D=lcm(q_odd), with D=1 for an
empty set. For requested rank h>=1 define

    d(h) = floor(log_N h),
    S(h) = D^(J d(h)).

Scale the original inputs once by S(h). Descendants retain that same scale;
they do not introduce another root scaling. Private zeros have every divisor.

**Odd-debt lemma.** Every intermediate linear expression has odd denominator
dividing D^(J d(h)).

An unfinished raw invocation contains at most J scalar divisions, each
adding at most one D factor. Addition takes the maximum of existing
denominator levels, not their sum. A completed rank-f C child is a dyadic
operator on its entrance, so it adds no odd denominator relative to that
entrance. Completed siblings contribute no continuing internal odd debt.
Only the chain of unfinished invocations contributes, and its depth is at
most d(h). This is simultaneous induction on rank and instruction position:
the exact endpoint of each completed smaller child and its internal-grid
invariant are both induction conclusions. It never assumes an unfinished
child has already returned. Arbitrary correlated values on distinct owned
fields are covered by the same linear-expression argument.

## 4. Binary height, magnitude and exact division

Let m>=2 satisfy |a|+|b|<2^m and q<2^m for every scalar coefficient.
Choose the deliberately generous guard

    G(h) = 8 (N + J(m+2) + 1) (h+1).

At active rank e put f=floor(e/N), r=e-Nf. A completed C child adds at
most f binary denominator bits and f bits of real-coordinate maximum norm;
C has real-coordinate absolute row sum two. The r tail kernels add at most
N-1. Scalar numerator arithmetic and division add at most m+2 bits per
instruction, including staged numerators. There are at most J paid events
in one node. Along an active dependency path,

    sum f <= h/(N-1) <= h,
    number of unfinished nodes <= d(h) <= h,
    sum r <= (N-1)d(h).

The terminal direct branch and its numerator require at most N+2 further
bits. These bounds sum to strictly less than G(h), for both denominator
height and logarithmic magnitude relative to the original entrance.
Addition uses the maximum incoming denominator level and the ordinary
row-sum bound, not the number of earlier completed contexts. Negative and
imaginary coefficients obey the same bounds.

Represent every intermediate value x by the integer I=2^G S(h)x. The odd
and binary bounds prove integrality after every complete instruction.
SCALE forms its full Gaussian integer numerator, then divides exactly by q.
Check the remainder; truncation must not conceal a failed invariant. The
direct C operation forms its full numerator before exact division by two.
If each input limb has absolute value <2^p, signed capacity

    p + 2G(h) + J d(h) bitlength(D) + 4

bits suffices, including temporaries. At return C^(tensor h) has denominator
dividing 2^h, so exact division by S(h) and 2^(G-h) returns the required
integer numerator 2^h C^(tensor h)x. Both drops must be present. The odd
scale is not an extra normalization in the mathematical output.

Capacity is O_word(p+h+log(h+1)). For #7834's h=O(p^.997) it is O_word(p),
so complete logical volume changes by a fixed factor. Outside h=O(p), use
the displayed bound instead of claiming O(p).

## 5. Complete scalar and root bills

D is calculated from the finite program and stored as a binary descriptor.
Perform Jd(h) fixed-D multiplication passes at the root and Jd(h) exact
fixed-D division passes at exit. Each pass scans the full reserved component
capacity, returns heads, and retires scratch. Binary multiplication and
restoring long division use a fixed number of tapes and cost a fixed
polynomial in bitlength(D) times the component width. Thus the new root
bill is O_word(V log(h+2)). Startup uses ordinary binary rational arithmetic; the selected fixed
word's numerical service reads D's bits explicitly. For unary code length
L, the denominator fields share the length budget: sum q_i <= L, hence
D <= product q_i <= 3^(L/3). A D-state table would therefore still have
2^O(L) size; it is not needed by this binary implementation. No growing
alphabet or unit-time wide arithmetic is assumed.

The binary lift and drop are sequential writes/scans of the widened format,
costing O_word(V) when h=O(p). Every local SCALE is a fixed number of integer
multiply/add/divide passes. Preserve both old limbs until both new limbs are
staged. The full O_word(V) bill includes source preservation, cursor return
and temporary retirement under the inherited scalar scan contract. Reused
storage retains its historical extent; erasure does not refund backing.

No new tape is allocated per depth. The source already parks nonchild
owners and continuations on fixed tapes. All fields retain one root format;
there is no conversion at each child boundary. The common-scale exponent
and depth are small descriptors. Scalar scratch is empty before suspension.

If the inherited nonchild tariff is O_word(V(e+1)^sigma polylog p), where
0<sigma<1 and (P/W)N^(-sigma)<1, the O_word(V) local passes fit it.
Geometric recursion plus the root logarithmic bill preserves
O_word(V(h+1)^sigma polylog p). This does not establish the indispensable
disjoint-XOR, placement or parking hypotheses.

## 6. Actual-source relevance and limits

The selected #7000 application uses odd scalars and local scale 1125.
Pending #7828 retains them in its finite compiler. Such a word is outside
#7834's published HALF-only scalar grammar. This extension removes that
specific scalar-alphabet and numerical-grid mismatch without adding paid
C calls. An actual compiled word still needs its literal instruction list,
all-column identity, private endpoints, funding and original owner/route
contract authenticated. No astronomical word is materialized here.

Finite exact executions test nested odd divisions, rational mixing, phases,
grid failure and output scaling. They are not a complete fixed-tape
transition table. The universal result is the written induction under the
named physical contracts. All five selected assumptions remain on the
selected record; this local bridge proves no new kappa.

Open next questions: bind #7828's emitted rational word to this grammar;
supply a faster compatible disjoint-XOR service; or lower the extra root
passes to a literal combined tape graph for a caller requiring that boundary.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Credit Ali Romman for #7834's dictionary/Vandermonde test and physical
recursion and #7828's compiler; the selected #7000 common-grid audit; and
all retained native, compiler and tape predecessors. Common denominators,
binary arithmetic and Vandermonde independence are classical methods.
