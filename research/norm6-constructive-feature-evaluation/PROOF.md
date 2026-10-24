# Explicit norm-six feature evaluation without a shell table

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
This is a constructive algebraic evaluator with explicit integer-arithmetic
bounds, not a physical supplier. Credit Cinna Davis PR2222 for the kernel,
integer-valued features and actual P48p Gram, DreamingOfClouds PR2244 for the
rational rank perspective, Dugongue PR4494 for dyadic lattice factorization,
and Nick Petalas PR5084 for the 19600-term existence result and this explicit
open question. The term bound is inherited; making its features evaluable
without a full-shell matrix is the contribution here.

## Statement and actual input

Fix the exact 48 by 48 P48p Gram G retained in PR2222. For any integral x with
x^T G x=6 and any integral y, write v=Gy and t=x^T G y. The program constructs
19600 integer source features s_k(x) and dyadic target features h_k(y), with

    sum_k s_k(x) h_k(y) = (t^3-4t)/192.

The descriptor is independent of x,y and of the shell cardinality. There is
no enumeration, lookup or reduction of a 26208000-port matrix. The universal
identity follows from polynomial relations; the small actual-shell fixture
only corroborates its source transcription. Positive definiteness, determinant1,
minimum6, shell cardinality and the49-bit chart retain predecessor status.
Only the first two are needed for the optional uniform coordinate bounds below;
the identity itself merely uses x^T G x=6. No condition on y's norm is needed.

## Forty-eight relations with a dyadic pivot minor

Use the original features f_i=(x_i^3-x_i)/3, l_i=x_i,
s_ij=x_i^2 x_j (i!=j), and t_ijk=x_i x_j x_k (i<j<k).
Their count is19648, and their original integral target coefficients are,
respectively, v_i^3, (v_i^3-v_i)/3-v_i, v_i^2 v_j, 2v_i v_j v_k.
The original pairing divides their dot product by64.

For each i the exact relation R_i=x_i(x^T G x-6)/2 is

 R_i = (3G_ii/2) f_i + ((G_ii-6)/2) l_i
       + sum_(j!=i) [(G_jj/2)s_ji + G_ij s_ij]
       + sum_(j<k; j,k!=i) G_jk t_sorted(i,j,k).

All coefficients are integers because G is even integral. The source diagonal
contains21 sixes,26 eights and one ten. Choose j=2, the first diagonal eight.
For each diagonal six remove p_i=s_ji; its coefficient in R_i is4.
For each diagonal eight or ten remove p_i=l_i; its coefficient in R_i is1
or2 respectively. These48 features are distinct.

For i!=j, R_i contains no other removed feature: a removed s_jk occurs only
in R_k and R_j, and a removed l_k occurs only in R_k. Therefore first solve
all i!=j directly. Finally substitute the21 solved s_ji into R_j and solve
for l_j. This one substitution layer expresses each removed feature as

    p = sum_(k retained) C_pk s_k,

with every C_pk in (1/4)Z. Diagonal-ten relations use only1/2, and the anchor
has coefficient1, so no new denominator is introduced. This is an explicit
invertible pivot minor over Z[1/2]; it requires no general saturation algorithm.
The recorded minor has determinant magnitude 4^21*2 (after consistent row/column
ordering). Its odd part is1. Naively eliminating all linear coordinates with
1/6 would not establish this dyadic conclusion.

Keep the other19600 features unchanged. Let a_p(v),a_k(v) be the original
integral target coefficients. Define

    N_k(v)=4a_k(v)+sum_p (4C_pk)a_p(v),  h_k(y)=N_k(Gy)/256.

Substitution into the original factor identity proves the theorem for all
admitted x,y. The evaluator uses integer arithmetic throughout: every4C_pk is
an integer and every (z^3-z)/3 division is exact for integral z. No approximate
real division or rational coefficient oracle is used at evaluation time.
The original features and Gram source bytes remain unchanged.

## Coefficient, operation and workspace bounds

The deterministic sparse construction has54996 nonzero C entries. Independent
exact coefficient expansion certifies |4C_pk|<=48 and, for every retained k,

    4+sum_p |4C_pk| <=52.

These finite descriptor facts are checked against all entries, not sampled.
Let X=max(1,max_i|x_i|), Y=max(1,max_i|y_i|), and V=max(1,max_i|(Gy)_i|).
Each original source feature has magnitude<=2X^3. Each original target
coefficient has magnitude<=2V^3. Consequently every partial accumulation in
N_k has magnitude<=104V^3, and |h_k|<=104V^3/256. The Gram multiplication
prefixes have magnitude<=480Y, since max|G_ij|=10. These prefix bounds include
cancellation in computing v, rather than using the final small V prematurely.
A signed working integer width

    b = 2 + ceil(log2(max(2X^3,480Y,104V^3)+1))

covers source and target evaluation. If only input magnitude Y is known, use
V<=480Y before execution. Output dyadic denominators are exactly represented
by the common public scale256, with no rounding.

For actual norm-six y, Cauchy-Schwarz in the G inner product gives
|v_i|<=sqrt(6G_ii)<=sqrt60, hence V<=7. Target numerators are then at most35672.
For a shell vector, |x_i|^2<=6(G^-1)_ii. By determinant1 and Hadamard on the
positive principal cofactor, (G^-1)_ii<=10^47; thus X,Y<=10^24 is a conservative
uniform integral coordinate bound. Combining these bounds gives a fully
explicit finite working width; no shell enumeration is needed. This bound is
not asserted sharp or a practical physical precision allocation.

A direct evaluation computes v, evaluates the19600 retained target coefficients
and48 removed coefficients, then performs54996 scaled updates. Conservative
counts per target are96596 integer multiplications,116244 integer additions
or subtractions, and48 exact divisions by3. These counts allow two multiplies
per original feature, Gram work at48^2 multiplies/adds, an aggregate three additions per
original feature (including initialization scaling; the linear features need
four, offset by the cubic and square features needing only two), and one multiply/add per
update. Scaling by4 can use shifts; charging it as an addition allowance is
safe via two doublings. The final denominator256 is output metadata, not19600
real divisions. Schoolbook integer arithmetic therefore costs at most a fixed
constant times (96596+116244+48)b^2 bit operations, separately from routing.

A source stream needs at most39200 multiplications,19600 additions/subtractions
and48 exact divisions by3, emits19600 integer values, and retains the48 input
coordinates plus16 scalar temporary/counter slots. Target evaluation needs
19600 accumulator slots,48 input coordinates,48 v slots and16 scalar temporary/
counter slots:19712 signed integer slots. Source and target outputs belong to
the caller; borrowed input coordinates are preserved. If both evaluators
coexist, add both workspaces and all retained outputs rather than maximizing
them. These are integer-array slots in an explicitly indexed arithmetic model,
not a Python heap measurement or a tape-placement guarantee.

An immutable sparse descriptor uses at most245884 integer slots: four per
original feature, three per transform edge (pivot index, retained index,
coefficient), and48^2 Gram entries. Each such integer fits32 signed bits.
A simple sequential descriptor traversal performs fewer than1000000 indexed
reads/writes per target; their physical movement cost remains a separate,
nonzero obligation. Descriptor generation is fixed48-dimensional work: below
2000000 rational additions/multiplications/divisions and3000000 rational slots
suffice by expanding48 rows of at most1177 terms and at most21 anchor-row
substitutions. Each stored final coefficient is quarter-integral with the
certified bound above; generator intermediate rational values are bounded by
1000000 in numerator and denominator by4, using at most21 sums of products of
source coefficients at most15 and direct solved coefficients at most15.
No asymptotic full-shell elimination hides in setup.

## Independent verification and limits

The verifier expands each proposed relation into ordinary cubic and linear
monomials. It derives the only possible linear quotient from the linear
coefficients and checks the entire resulting polynomial against that quotient
times (x^T G x-6). It does not use the relation generator to decide correctness.
All48 identities and all coefficient bounds are exact. It then evaluates all
26 original bounded actual-Gram norm-six vectors against those26 plus12 wider
integer target vectors:988 full19600-term identities. Controls reject a damaged
transform, missing integer-valued cubic correction, an off-shell source, wrong
normalization, inadmissible diagonal and a non-dyadic naive pivot premise.

Retaining the inherited49-bit chart gives the same algebraic support bound
49*19600=960400 as PR5084; that number is not a new gain. This result supplies
no chronological physical I-K side map, frame/owner legality, arbitrary-dirty
restoration, efficient shell enumeration, complete bit supplier, native/Tape
execution, compiler or outer admission. Unknown physical costs are not zero.
No selected-frontier, kappa, human-review or proof-kernel claim follows.

## Open next questions

- Can these explicit features be acquired and consumed by a chronological
  physical side program with all frame, source-access, helper and restoration
  costs charged? Start with one actual source/target block, not a whole-shell
  table or an algebraic support bill treated as a physical invoice.
- Can the conservative coordinate and evaluation bounds be sharpened enough
  to change that complete physical decision? Further coefficient tuning is
  not warranted unless a consumer specifies an allowance it can change.
