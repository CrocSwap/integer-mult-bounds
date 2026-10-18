# Exact local fusion and paid implementation

The tape-operation premises come from the original
[ordered affine streams lemma](https://github.com/CrocSwap/integer-mult-bounds/blob/5996e33ecad6a0ccd578aec58831457829d75575/upstream/build/sections/02-streams.tex)
and [address interchange construction](https://github.com/CrocSwap/integer-mult-bounds/blob/5996e33ecad6a0ccd578aec58831457829d75575/upstream/build/sections/04-swap.tex)
of CrocSwap/integer-mult-bounds, pinned at the displayed revision.
The general rank-one lowering, selected unipotent operator and dirty
shared-chart fusion in this packet are a separate contribution.
Source pins distinguish that contribution from the borrowed tape contracts.

## ADDRESS operator

Use six physically ordered fields `(H0,H1,H2,D0,D1,D2)`, each of width
`b=N/3`. Each coordinate lies in the true residue ring `Z/(ell^b)`, where
ell is any odd prime. Unnamed ADDRESS fields may occur between or outside
these fields and remain spectators. Set

```
u = (1,0,1),       t = (1,0,-1),       t^T u = 0,
g = I3 + (1/2) u t^T,
g^-1 = I3 - (1/2) u t^T,
s = (u,-u),       r = (t,-t),
Phi(g) = I6 + (1/4) s r^T.
```

The lift preserves H+D and applies g to H-D; H1 and D1 are fixed.
Since `(u t^T)^2=0`, the displayed inverse is exact. The map is not an
involution over the rationals or any odd residue ring. These are rational
ADDRESS operations specializing to residue rings, not signed arithmetic
on stored VALUE bits.

The following chronological seven-event word equals Phi(g):

```
z2 <- z2-z0
z3 <- z3+z0
z5 <- (z5+5*z0-z2-z3)/4
CHILD_C(0,5)
z2 <- z2+z0
z3 <- z3-z0
z5 <- -4*z5+3*z0+z2+z3
```

Every affine control precedes its target. `CHILD_C(0,5)` is one ordinary
recursive interchange of the selected equal-width fields on the COMPLETE
private BIT stream; it preserves all other ADDRESS fields. It is a
contract invocation, not an implementation of the recursive supplier in
this packet. The affine operations use the original ordered-stream
contract, including its work tapes and head returns. Subject to those
contracts and their row/stack hypotheses, this is a fixed all-b local
implementation with six affine scans, one child and O(V) additional work.
There is no exponential array enumeration in the implementation.

For completeness, the lowering formula is independently checked. For
`M=I+s v^T`, let `D=1+v^T s` and `a=s0*vlast`, both nonzero. Subtract
`(si/s0)z0` from each middle coordinate. Then set

```
zlast <- a*zlast+(D-slast*vlast)*z0+sum_middle s0*vi*zi,
swap(z0,zlast),
zi <- zi+(si/s0)*z0                 for each middle coordinate,
zlast <- (-D/a)*zlast+((D-s0*v0)/a)*z0
         -sum_middle (vi/vlast)*zi.
```

Substitution gives M on every input coordinate. Here `v=r/4`, D=1 and
a=1/4, and only middle indices 2 and 3 need updates. Thus the formula
emits exactly the word above. The checker derives it afresh and verifies
its rational matrix. The literal reverse inverts each affine unit and
uses the same involutive child; its matrix is Phi(g^-1), not Phi(g).

The denominators and affine diagonal numerators exclude only prime 2.
For example, a control coefficient vanishing modulo 5 does not make a
diagonal singular. This proves specialization for every odd ell and b,
including composite rings such as Z/25 and Z/49. Removing only the child
while retaining the affine wrappers changes the operator.

## Exact comparison and native dirty chart

Let `P=u*(1/2,0,1/2)` and `Q=u*(3/4,0,1/4)` denote outer products.
Both row pairings with u are 1, so P and Q are idempotents; Q need not be
orthogonal. Write `R_P=I-2P` and `R_Q=I-2Q`. Since PQ=Q,

```
R_P R_Q = I+2(Q-P) = g.
```

Chronologically apply Q first, then P. `PROGRAM.json` gives a separate
six-affine/one-child word for each lifted reflection. Their full matrix
product, including spectator coordinates, equals the fused word.

For three genuine BIT DATA rows `(x1,x2,x3)` and retained private row q,
all with the same full ADDRESS domain, use this fixed chart:

```
q  XOR= x2
x1 XOR= q
h(q)                 # array permutation induced by Phi(h)
x1 XOR= q
q  XOR= x2
```

Write its complete linear BIT operator as H(h). Its endpoint on arbitrary
dirty inputs is

```
x1' = x1 XOR q XOR x2 XOR h(q) XOR h(x2),
q'  = h(q) XOR x2 XOR h(x2),
x2' = x2,   x3' = x3.
```

Equivalently, with `E=(e1+eq)(e2^T+eq^T)` over F2, E^2=E and
`H(h)=I+E tensor(h-I)`. Hence H(h2)H(h1)=H(h2 h1) for arbitrary arrays,
and in particular `H(R_P)H(R_Q)=H(g)`, including arbitrary initial q.
This proof does not assume a clean private row. There is no F9 codec,
padding promise or signed integer VALUE lift.

The adjacent decoder and encoder in the specified two-reflection baseline
cancel exactly. That baseline already has FOUR XOR scans around its two
ADDRESS queries. The fused word also has four. The verified improvement
is two specified recursive children reduced to one; there is no separate
XOR saving. Twelve baseline affine events is its literal serialized
count before possible affine simplification. Neither affine nor child
optimality is claimed against other possible implementations.

## Orientation, spectators and recovery controls

For modulus m=ell^b and seed e_H0, the orbit is
`z_k=e_H0+(k/4)s`, indexed by Z/m. It has exactly m points because 1/4
and a component of s are units. Phi(g) pushes address index k to k+1;
its array permutation reads old VALUE index k-1. The inverse reads k+1.
The reflection address maps are Q: `k -> -3-k` and P: `k -> -2-k`.
Their chronological composition pushes k to k+1, as required.

The checker applies the actual words to these actual addresses at m=5,
25,7,49. It verifies all six ADDRESS basis columns and unchanged exterior
spectators, as well as H1/D1. On these orbits it checks all 4m dirty BIT
basis columns, 344 total, plus m VALUE spectator columns, 86 total. Each
dirty column agrees with the formula, the full two-stage word and the
chart-cancelled baseline; the literal inverse restores its input.
BIT linearity gives all assignments on each tested orbit, while the
algebraic operator identity above covers arbitrary arrays on the full
ADDRESS domain. Fixed points and their 16 four-role BIT assignments are
also checked. Replacing the WHOLE query by identity gives H(I)=I;
this differs from removing only the recursive child.

At m=5 start with x2 a delta at index 0 and x1=x3=q=0. The forward module
gives `x1=q=[1,1,0,0,0]`. Its proper retained-q inverse restores all rows.
If q is wiped first, that inverse instead gives
`x1=[0,1,0,0,1]`, `q=[1,0,0,0,1]`: DATA is lost. Using g again as the
inverse also fails. These are explicit negative controls, not a claim
that private state can be reset between uses.

## Paid state and limits

Take V as the productive volume of the three genuine DATA streams.
Private q has full volume V/3, including all spectator ADDRESS ranges.
Persistent stock is 4V/3 before evaluator routing, parking, work-tape or
recursion scratch. Initially zeroing fresh q costs V/3. Each fused module
pays one separate child of actual volume V/3 and width N/3, six ordered
ADDRESS affine events, four native XOR scans, setup and head-return work.
The specified cancelled baseline pays two such children and the same
four XOR scans. Each actual separate child call must remain separately
charged in a future supplier recurrence.

The component identity is valid with dirty q, but an enclosing DATA
construction starting from clean q must allocate and initialize it.
Its state is retained through every future use and recovery. A once-only
final wipe costs V/3 and is eligible only after a separately verified
completed DATA endpoint and the last read of q. This unfinished module
boundary does not license that wipe. No DATA row is cleared for free.

The half-integral g is outside an odd-denominator mod-4 generator grammar;
the old rho4 construction is undefined on it. This does not invalidate
that construction on its own alphabet and cannot be priced by extending
it without a new proof.

The packet supplies one exact local query fusion. It does not produce a
complete three-DATA cyclic-interchange c word, a complex C supplier, a
common cover/owner schedule or an all-size weighted-row compiler. Those
missing endpoints and schedules, both suppliers, all separate calls,
movement, dirty recovery and paid stock must be verified before deriving
an integer-multiplication exponent. No kappa improvement is asserted.
