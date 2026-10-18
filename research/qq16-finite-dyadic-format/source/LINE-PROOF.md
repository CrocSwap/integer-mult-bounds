# A charged line normalization for the zero-retention QQ16 decoder

The predecessor is Arham Tahir's PR2681 at
`ea96706295631be10d92ae149b63c3e24acaeabc`. Its logical inverse, source
reconstruction, full-current observation contract, scalar schedule and
two-chart routing are retained with credit. Full-current invertibility is
already known. This result changes the physical implementation of that word.

## Exact boundary

At the completed B1 cut, the 112 current X fields have chart F17 and the 112
current Y fields have chart F17 C_q^-1. Here F17 is the product of the signed
Fourier line operators on address axes 0 through 16; q is the authenticated
nine-bit normal at the corresponding port. All 224 current fields are borrowed
and never written. The 224 eventual output banks are owned and may contain
arbitrary dirt, which the same paid CLEAR operations remove. At termination
they contain the original 224 logical input arrays, all in F17. No early
values, banks or output availability before B1 are assumed. At most sixteen
owned local scratch arrays are live. Their clearing/disposal contract is the
predecessor's owned-scratch contract, not reversible uncomputation of dirt.

The phase identities below are first stated on the same 73-dimensional
binary coordinate space. For every actual owner coordinate d, substitute
z -> d^T z in each character identity, as in the source's M(g,b) action.
An identity for every character remains an identity after that substitution,
and hence on every owner and every payload tensor factor. No owner coordinate
or payload factor is dropped or sampled.
The checker retains full routed operators on arbitrary arrays; constant
payload samples would not suffice. Logical state is represented separately
from its physical chart. Multiplying a physical array by a line operator
changes its chart and preserves its represented logical value. A cover map
changes the represented logical value by the authenticated address route and
changes the chart by the explicit phase rule below.

## Frame identity

For a list of pairs (v,c), define its Fourier-character phase at z by

    phi(z) = sum c * <v,z> mod 4,

where each binary inner product is interpreted as 0 or 1. C_q contributes
<q,z>; a physical XOR translation X_b contributes 2<b,z>. Thus an orthogonal
involutive route g with its specified payload translation b takes a phase
list Phi to

    move(Phi,g,b) = [(g v,c) : (v,c) in Phi] + [(b,2)].

The g at each port is reconstructed from the unchanged selected native source
and checked against the actual QQ16 registry, in both stages. This is a
physical payload alignment, not a substitution of a physical shift into the
logical route algebra. The represented logical operator remains g.

Let F16 denote the product of lines on axes 9 through 24. A stage-2 route swaps
the eight local directions orthogonal to q with axes 17 through 24, fixes q,
and leaves axes 9 through 16 unchanged. Consequently the image of the F17
frame has the same underlying orthogonal directions as F16 C_q. Their phase
polynomials may differ by an even linear character. Compute b_p from that
difference, and verify the exact identities

    move(F17,g_p,b_p)              = F16 C_q,
    move(F16 C_q,g_p,g_p b_p)      = F17.             (1)

Equality here means equality of complete phase polynomials, including the
constant phase (both words have phase one at character zero). It is not
equality only up to phase or equality of spanned binary subspaces.

The constructor checks every one of the 112 actual ports. Independently, it
evaluates the literal character sums on zero, all 73 basis characters and all
2,628 pair sums. These determine these degree-at-most-two polynomials mod 4:
expanding XOR in such a phase has only linear terms mod 4 and even quadratic
terms; every term of higher degree is divisible by 4. This establishes (1)
on every character of the full address space. The same two methods check
the stage-1 maps preserving F17 with their own current-frame shifts. No
claim that the predecessor's F25 shifts work for these new frames is made.

## Literal lowering and restored intermediate frames

Begin with the complete 4,047-event predecessor word, regenerated and compared
with its retained WORD.json before lowering. Make only these physical changes:

1. Delete all 224 input upgrades to F25 and all 224 final downgrades to F17.
   Normalization of the copied Y fields by the existing 112 positive C_q calls
   is retained. The principal word therefore stays in F17.
2. Implement each stage-1 map with its F17-preserving affine shift.
3. At each stage-2 entry map on W_p, use (g_p,b_p), then a paid C_q^-1. This
   gives chart F16. All 112 W fields and the eight active query scratch fields
   are in that exact common frame throughout the future-query sweep.
4. After that complete sweep, apply a paid C_q to each W_p and the inverse
   affine map (g_p,g_p b_p). This returns every W field to F17. Z fields stay
   in F17 throughout; no scalar ADD crosses the different intermediate charts.

Every scalar ADD, CLEAR, private-scope event, logical route and its order are
unchanged. In particular the noncommuting stage-1/stage-2 order is unchanged.
Equation (1) proves that every changed map/line block implements the same
logical route as its source counterpart. Common-chart induction then proves
that every represented logical state at every scalar event is unchanged.
Both complete inverse orders on 224 free input arrays are replayed, including
the intermediate inverse-B1 checkpoint. The final physical chart is F17 for
every output. Borrowed arrays are untouched rather than temporarily changed;
all scratch ownership and disposal events are exactly the credited ones.

## Native positive children and phase

Each signed C_q is lowered using one positive rank-one child and two explicit
monomial wrappers. Choose a binary basis with first vector q. The positive
kernel has numerator 1+i at x and 1-i at x+q, common denominator two. For the
negative sign, an output XOR by q swaps those coefficients. Equivalently
C_q^-1 = X_q C_q; no negative child is declared free.

The checker verifies all 512 basis columns for each of the 112 normals and
both signs, including exact Gaussian coefficients and global phase. The
wrappers act identically on the remaining 64 coordinates, so these are full
73-coordinate operator identities. Every one of the 336 literal child
occurrences is bound to its signed recipe. Cover maps are affine monomial
permutations, with both translations retained. The phase operations are exact
members of the inherited finite Gaussian-dyadic alphabet. Approximate child
precision and physical address/control work require separate admission; an
ideal unitary identity does not establish a rounded whole-caller guarantee.

## Complete local comparison and bounded decision

The transformed word has 3,823 events, 336 positive rank-one children and no
rank-eight children. There are 672 native monomial wrappers, 464 full-cover
maps, 1,808 signed unit ADDs, 896 signed quarter ADDs and 312 CLEARs. The
inherited real scalar allowance is

    8*1808 + 12*896 + 2*312 = 25840.

These scalar coefficients and that allowance are unchanged from PR2681.
Both words use 224 eventual output banks, at most sixteen local scratch banks
and zero early retention. The old 448 H8 calls are replaced by 224 H1 calls;
all 112 original line normalizations remain. The profile is a constructive
finite upper bound, not an optimum or a placement/tape invoice.

Against PR2540's same-endpoint 224 H1 + 16 H8 decoder, the numerator of the
child-moment difference at the same parent width is

    112 - 16*8^(1-a).

For 0 <= a <= 1/16 this is strictly negative, because
8^15 = 35184372088832 > 33232930569601 = 7^16. Raising positive numbers to
the sixteenth power preserves order; hence 8^(15/16)>7. This includes the
small saving parameters of the selected regime, without asserting a new
selected bound. At a=0 the rank mass is 336 instead of 352.

The comparison also has 192 more monomial wrappers, 256 more cover maps and
8,368 more scalar primitive allowance than PR2540. These are real liabilities,
not zero-cost terms. Whether their physical implementation is favorable is
unknown. The newer output-bank coalescing of PR2651 changes the retained-bank
comparison but still keeps sixteen values across B1; it does not erase these
child and physical-cost distinctions.

Revision-5 decision: retain one local module. The previous recipe's negative
child-cost comparison is not a barrier to zero retention. Do not expand this
construction into a supplier without a named consumer, complete physical
map/wrapper/control prices, legal ownership/lifetimes and rounded precision.
Inherited F0/B1 execution and output consumption also remain paid obligations.
No new kappa, all-size supplier, native hosting or optimality claim follows.

Arham Tahir/PR2681, ywz65/PR2540, the QQ16 authors and retained source/native
lineage keep their attribution. New frame lowering and evidence prepared by
ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
