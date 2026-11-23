# Sharp state count at a serialized carry cut

This is a scoped written proof, produced by Nick Petalas. Finite enumeration
corroborates the proof; it does not replace its quantifiers.

## Contract

Fix integers q>=2, Q>=1, A in Z and D>=1 with gcd(D,qQ)=1. The parameters are public.
The source low digit x and target low digit y independently range over
{0,...,q-1}. Put

    t = (y + A D^(-1) x) mod q,       0<=t<q,
    K(x,y) = (A x + D y - D t)/q,
    C(x,y) = D^(-1) K(x,y) mod Q.

Each inverse is taken in the indicated modulus. When Q=1, C is zero. The
integer K is well-defined. C is the high translation of the rational shear
on the full modulus qQ, with source and target high digits initially zero.

A deterministic producer reads all of x before any of y. After that cut it
cannot reread x, inspect an x-dependent external object, or retrieve an early
output. It must subsequently produce C exactly for every y. Every retained
x-dependent datum, including control and head positions, is part of its cut
state. Computation on the public parameters is unrestricted. The theorem
counts distinguishable states at this cut, not total peak workspace or time.

Two source digits may share a state exactly when their complete response
functions y -> C(x,y) agree. A common state gives identical future behavior,
and an equivalence-class label is a sufficient one-way message.

## Theorem

Write

    g = gcd(A,q),     d = q/g,     e = Q/gcd(A/g,Q).

The convention gcd(0,q)=q applies. The exact minimum number R of cut states is

    R = 1                         if Q=1,
    R = d min(g,e)                if Q>1.

Consequently ceil(log2 R) binary bits are necessary and sufficient for an
encoding at this cut. Sufficiency permits later unrestricted computation;
it is not a constant-workspace physical producer.

### 1. Every response is a single step

Let

    r_x = (A D^(-1) x) mod q,
    b_x = (A x - D r_x)/q.

Since 0<=r_x,y<q,

    K(x,y) = b_x + D 1[y >= q-r_x],
    C(x,y) = D^(-1)b_x + 1[y >= q-r_x] mod Q.

For r_x=0, the threshold is q and the indicator is always zero.

If Q>1, two different r values give different response functions. At y=0
their constant terms either differ already, or agree. In the latter case,
choose y=q-max(r_x,r_x'). Exactly one indicator is one, so the responses
differ by one modulo Q. This y lies in {1,...,q-1} when the r values differ.

For equal r, the response functions agree precisely when b_x=b_x' mod Q,
because D is a unit modulo Q.

### 2. Count each fiber exactly

Multiplication by A D^(-1) modulo q has exactly d image residues and g
preimages per image residue. Equal-r digits have the unique form

    x = x0 + j d,      0<=x0<d,      0<=j<g.

The r value depends only on x0, and different x0 have different r values.
Within this fiber,

    b_(x0+jd) = b_x0 + j A/g.

The additive order of A/g modulo Q is e. The g consecutive j values
therefore give exactly min(g,e) distinct b residues. Different fibers cannot
merge by part 1. This proves R=d min(g,e). For Q=1 every response is zero,
so R=1. The argument includes A=0: then d=e=1.

### 3. Attain the bound

For Q>1 put m=min(g,e), write x=x0+jd as above, and retain

    label(x) = x0 m + (j mod e).

The labels are exactly {0,...,dm-1}. Decode a label into

    x_star = floor(label/m) + (label mod m) d.

This is a valid source digit with the same r and the same b modulo Q as x.
Computing C(x_star,y) therefore returns the correct answer. For Q=1 retain
the single constant label. Thus the information lower bound is attained.

## Quarter-shear consequence

Take A=1, D=4, odd q>=3 and Q=q^(w-1). If w=1, the high output is trivial and
R=1. For every w>=2, g=1 and R=q. The exact serialized-cut storage is therefore
ceil(log2 q) binary bits, despite a width-independent final carry packet.

The literal fixture q=257,w=2 has 257 pairwise distinct response functions,
requiring nine binary bits at the cut. Its integer K takes only eight values,
{-3,-2,-1,0,1,2,3,4}; the verifier enumerates every x,y in this fixture. A
small final packet alone therefore cannot justify constant retained state in
this access order. The theorem leaves interleaved reads and rereads open.

## Exact packet variant

If the output is the integer K rather than its high-modulus image, the same
step argument applies over the integers. Equal r values have different b
values whenever A is nonzero and x differs. Hence there are exactly q cut
states for every A!=0, and one for A=0. This holds even at Q=1, where producing
the high correction instead needs only one state. The two output contracts
must not be conflated.

## Relation to the predecessor

Ali Romman's PR #5849 at `35ee8364ccfe54d6d5ec154fbf74993624b0a0d4`
implements an original-owner runtime rotation from a supplied carry packet
and explicitly leaves production from the low cache open. PR #5841 at
`58a032ffafc2c5d08b8f53c2e98657b75c48379d` supplies its fused carry algebra.
Those results and physical bounds are cited premises, not replayed or
independently validated here. The scalar rational shear above isolates one
packet-production boundary; it does not assert that every released G20 route
uses this serialized access order or contains this precise scalar fixture.

The state-equivalence argument is the standard deterministic one-way
communication method. The contribution is its exact rational-carry quotient,
including the nonunit-coefficient collapse and an attaining encoding.
No claim is made to invent communication complexity or modular arithmetic.

## Limits

This is not a lower bound for arbitrary tape algorithms, interleaved access,
multiple passes, early output, a previously computed low cache, or amortized
production of several packets. The encoding is not a literal finite-tape
program. Its computation, source access, erasure, routing and interaction with
the complete caller remain unpaid. No selected saving, frontier or framework
assumption changes, and no complete multiplication theorem is claimed.
