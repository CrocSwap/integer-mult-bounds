# Minimal numerical templates through the recursive native caller

Prepared for @CubeJerry with substantial OpenAI assistance. This is a
source-bound mathematical audit, not a formal-kernel proof. It concerns the
historical dimension-64, rank-at-most-42 caller used by
CrocSwap/integer-mult-bounds#2809 and CrocSwap/integer-mult-bounds#2899. It does not admit the selected
CrocSwap/integer-mult-bounds#6030 implementation or change kappa.

## 1. Exact proposition and inherited boundary

Fix an admissible compiled source prime q and its selected vocabulary. Let
M=q^w, w>=1, and let n0>=64 be the root body width. Put

    b=bitlength(n0), I=b+1,
    a=bitlength(M), L=a+1.

Use unchanged `PhysicalArena.prepare` from CrocSwap/integer-mult-bounds#2899 with canonical Count
inputs n0 and M. Each current internal node has generated width n>=64,
f=floor(n/64), delta=n-64f, and chronological depth h. Every generated child
has positive width c equal to r*f (1<=r<=42), f, or floor(f/2); the last
case is entered only when positive. A frozen input history is a valid
chronological chain from n0, including record lengths, source labels,
parent/child extents and raw fields. The ordinary root has empty history.
The banks keep the same templates through descendants, grants, leaves and
exact-slot restoration.

The asserted banks are the two retained native working banks and the
matching ingress words copied into them. Ordinary's separate high/tail
preparation helper rings have their own maxima and templates; they are not
identified with these two banks or covered by this native-width conclusion.
The canonical matching ingress records and their producer are included.

The semantic inputs are the mathematical source contracts of
CrocSwap/integer-mult-bounds#2449/#2501/#2569/#2753: admitted low classes, valid field/coordinate and
child-event domains, canonical residues, correctly bracketed ownership and
serialization. Interpret these contracts over unbounded integers; they do
not assume the finite-word overflow guards have already passed. Selected
finite labels have dimension64, ranks1..42 and row/field labels0..127.
Operations remain subject to non-width checks, including unit pivots and
exact source binding. Width bounds do not prove those checks or termination.

**Theorem.** At every finite execution prefix on that domain, before an
unrelated failure, the two native banks' numerical words, matching ingress
words and range-sensitive
arithmetic fit the two templates. Every `Unsigned.divmod` divisor has its
required zero high bit. No carry-out, high-bit shift, bounded increment,
finite-literal or word-record extent check can be the first failing width
guard. Capacity sufficient for the reached prefix remains a separate
condition. No successful complete reference execution is assumed.

This does not prove the complete Boolean endpoint, stock/descriptor
semantics, scratch inventory, termination, source preparation costs,
rejection cleanup, or overall native action/space theorem. It does not
transfer historical admission to the current selected supplier. The
published recursive numerical-capacity result at
`0ca312ed12585a1dc56bcb3d90354f8c6307dc28` is complementary: it bounds slots;
this audit bounds values and extents inside those slots.

## 2. Existing results and new reviewed implication

CrocSwap/integer-mult-bounds#2449, `research/selected-binary-control/PROOF.md` sections2--4, proves binary
arithmetic, modular preparation, generated evaluation and local coordinates
on these exact widths. Its multiplication, Euclidean and callback invariants
are inherited, not new results. CrocSwap/integer-mult-bounds#2501 supplies encoded residual/leaf traces;
CrocSwap/integer-mult-bounds#2569 supplies directories and high routes; CrocSwap/integer-mult-bounds#2753 supplies recursive geometry;
CrocSwap/integer-mult-bounds#2769/#2809 park and restore active banks; CrocSwap/integer-mult-bounds#2899 initializes minimal templates.
CrocSwap/integer-mult-bounds#2831 and CrocSwap/integer-mult-bounds#5191 separate backing/capacity from width premises.

The new implication is that the *complete actual recursive geometry and
producer chain* satisfies those minimal-width interfaces, including the
one-past body endpoint, external-gap insertion, leaf depth extension,
terminal route cursor and exact-width child/parent records. The pinned
operation inventory exposes the source boundary; it is not a general Python
range analyzer. Written invariants below cover all loop lengths.

## 3. Template and arithmetic margins

A positive canonical Count for X has exactly bitlength(X) digits. `prepare`
copies one zero per digit, then an extra zero and RIGHT; induction on that
scan gives the stated width and restored input head. `load(X)` stops before
the extra zero. Arbitrarily padded Counts are outside this claim.

    n0 < 2^b, 2*n0 < 2^I,
    M < 2^a, 2*M < 2^L.

These strict bounds also hold for powers of two. An index word may contain
2*n0 with its top bit one; representability does not imply a divisor margin.
Section7 separately classifies divisors.

The inherited bit-loop proof can be used before a first width failure:
addition is exact with zero carry when its mathematical sum is below the
word limit. `times_small(x,k)` builds nonnegative binary prefixes of k, so
each partial product is at most k*x. A bound on the final product covers
every internal addition. Increment is safe when the new value is below the
limit. Subtraction does not grow a word; no-borrow is a separate ordering
fact. For division with d<2^(I-1), the invariant r<d gives
2*r+bit<2*d<2^I. A numerator may have its top bit one. The residue version
uses L instead of I.

## 4. Histories, callbacks and emitted child records

Every chain n0>n1>...>nh=n of positive integers satisfies h<=n0-n.
At an internal node n>=64, h+1<=n0-63<n0. A positive child c<n has
h+1<=n0-c. Thus validation counters, frozen-field slots, current-field
scopes, depth+1, new Program depths and grants are at most n0. A leaf
program retains the original root n0 and the same template, even when its
own width is below64. The root's canonical high-zero/next-one check is
unchanged.

The source computes f by division by64. Its expected good child r*f is
at most42*f<64*f<=n; pair/unit and halved children are at most f. Every
fixed-multiplier prefix satisfies the same bound. An ancestor callback
requests either the same coordinate (good), or row*f+j with row<64 and
0<=j<f (pair), hence a coordinate below the parent width<=n0. Reverse
column f-1-j stays in that interval. Rows>=64 supply constants and do not
become parent coordinates. This composes CrocSwap/integer-mult-bounds#2449's original local argument
with the actual child/depth producer.

Program/Fields/Stack serialization copies exactly I or L bits, padding
included. Child ROOT copies original root width/unit and incremented depth;
STEP copies parent/child words from the same bank. Resets preserve global
chronological slots rather than rebasing depth. All record readers therefore
meet the unchanged extent template whenever the inherited record grammar
holds.

## 5. Complete body geometry and original external gap

Write n=64*f+delta, 0<=delta<64. The compact128*f-atom core embeds into
the actual2*n-atom body by

    phi(x)=x                  for x<64*f,
    phi(x)=x+2*delta           for x>=64*f.

For 0<=x<128*f, 0<=phi(x)<2*n. The stored core=64*f, extra=2*delta and
total=2*n, including all intermediate nonnegative products, fit I. External
gap cardinalities multiply Count/Natural tapes; they never multiply a
fixed-word atom position.

At physical positions a<b, the differences 2*n-last, 2*n-last-1, b-a and
b-a-1 lie in [0,2*n]. Nonnegativity follows from admitted ordered distinct
positions. Exactly one spectator Count receives the external gap factor;
this changes no bank-stored atom position.

The source's chunk families obey:

* Good: starts0 and(128-r)*f, width r*f. Each chunk lies in one compact
  bank; they are disjoint and the second ends at128*f.
* Pair: starts i*f and k*f, width f, for0<=i<k<=127. Each is a complete
  field contained in one bank.
* Orientation: starts k*f and(k+1)*f-u, width u=floor(f/2)>0. Both lie in
  one field and2*u<=f. The source only enters this family for same-bank pairs.

The exact checker enumerates finite row/rank labels and verifies affine
inequalities in nonnegative symbolic width parameters. It does not infer
all-size validity from a finite list of n.

`Layout.child_extents` constructs physical starts a,b, ends a+width,b+width,
width-1, compact last coordinates, mapped/expected last coordinates,
between=b-(a+width), and after=2*n-(b+width). The chunk facts put every
start/last/end in [0,2*n] and every difference in the same interval. Phi is
applied to *last* coordinates, not a one-past endpoint at the bank boundary.
The actual code forms ends from physical starts plus widths, correctly
handling a head chunk ending at64*f without inserting the gap into it.

Both leaf and internal `trace.child` compute the same disjoint-chunk end.
For0<=j<width, first+j and second+width-1-j remain in their chunks. The
last increment produces width<=n0. Adapter `Geometry.point` gives
row*f+j in the head and row*f+f-1-j in the tail, always below128*f. The
column loop's final increment gives f<=n0.

Original-offset peel visits coordinate64*f,...,n-1 and
right=2*n-1-coordinate, then increments to n. These and total=2*n fit I.
The same inequalities cover delta=0 (empty peel) and n0=64.

## 6. Residues, high digits and the terminal route cursor

Matrix/scalar/callback outputs lie in [0,M) by the inherited ring invariant.
Their addition/subtraction temporaries are below2*M. Euclid keeps remainders
at most M and quotients at most M, reducing a quotient equal to M before
modular multiplication. Signed rational constants use `Ring.literal`'s
modular loop; no arbitrarily large unsigned literal is loaded directly.

Context/radix setup divides powers of q by q with operands at most M.
Unsigned literals here are q, one and low entries<q, all fitting because
q<=M. The high cap=M/q. Each odometer increment goes from a value<cap to
at most cap and immediately resets equality. Raw entries g0+q*G are formed
as canonical ring expressions. Route keys have canonical common entry x
and low entry ell=x mod q, so x-ell>=0 and(x-ell)/q<cap.

The complete ADD's source-coordinate Word x ranges from0 to M-1; its
source counter is decremented before deciding whether to increment x, so
there is no increment after the final source atom. The split length
M-offset is in[1,M]. The active `inputs/pr2753/stream_runner.py` dispatches
signs to `inputs/pr2753/linear_sign.py`, rather than the inherited vendor
stream runner. That sign primitive loads the unsigned literal2 and forms
M-2 and M-1. Since M>=2, these are nonnegative and all fit L; it performs
no fixed-word division. These lengths become separate cardinality counters,
not larger residues. The loader authenticates these actual import paths.

An actual exceptional Word is the radix-sort cursor in `routes.route_cube`.
It doubles from1 through2^(L-1). The source tests its top physical bit
*before* another shift: every executed shift has zero outgoing carry, and
the terminal cursor is representable. We do not claim it is a canonical
residue or below M. `partition/copy_key` scan its bit mask; they do not use
it as a divisor or modular Ring operand. Its final high-bit partition sees
zero bits in all canonical high keys.

## 7. Divisors, transfer and restoration

| Bank | Divisor | Required bound |
|---|---|---|
| Index |64 or2 |<=n0<2^(I-1) |
| Index |positive columns f |<=n0/64<2^(I-1) |
| Residue |q |<=M<2^(L-1) |
| Residue |positive Euclidean remainder |<=M<2^(L-1) |

No doubled endpoint, family count, source label or terminal route cursor
enters fixed-word division. Arbitrary cardinality division has its separate
growable format. The source inventory covers current layout, trace, peel,
residual_blocks, macro_machine, macro_binding, packet_engine, coefficient
modules and route/directory helpers. ToyBinding, fixture constructors and
host-only fixed-source compiler arithmetic are excluded explicitly.

`prepare_child`, `call` and `complete_return` transfer already bounded
values. The numerical codec writes all bits to RIGHT. Restoration allocates
from the unchanged template, copies the same bits and checks the terminator.
Stream-role parking preserves Program/Fields separately. No new extent is
derived from the child width. Warm free-list permutations do not change
the restored original Word object or its template extent.

## 8. First-width-failure argument and evidence limits

Choose a shortest admitted finite prefix ending at a failing width guard.
All earlier loop, template, geometry and canonical-value invariants hold.
Sections3--7 give a strict representability bound for a pending sum, shift,
increment or literal; a high-zero divisor bound; or an exact-length record
copy. Each contradicts the proposed first width failure. No successful
complete reference run is used. Unrelated malformed input remains excluded.

Finite checks execute unchanged arithmetic/geometry on PhysicalArena
templates, including powers-of-two boundaries, both compact banks,
remainder63, depth extension, high route masks and serialized restoration.
Removing the extra bit, using a top-bit divisor, shifting the terminal mask
or crossing the admitted chunk boundary supplies negative controls. These
checks corroborate the written all-size argument. No full GL64 payload,
new exponent, independent human review or proof-kernel acceptance is claimed.
