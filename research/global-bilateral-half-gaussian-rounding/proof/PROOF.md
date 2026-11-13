# Sharp bilateral half-unit radial distortion for a Gaussian lattice bijection

Let U=H/2 with H=((1,1,1,1),(1,-1,1,-1),(1,1,-1,-1),(1,-1,-1,1)).
Put R_abs(F)=sup_x | ||F(x)||-||x|| | and
Delta_+(F)=sup_x(||F(x)||-||x||).

**Theorem.** Every total integer-output map with ||F(x)-Ux||<=1 has
R_abs(F)>=1/2. An explicit bijection F:Z^4→Z^4 has error0 on even-sum
inputs and error1 on odd-sum inputs, preserves total parity and satisfies
| ||F(x)||-||x|| |<1/2 at every input. Both Delta_+(F) and Delta_+(F^-1)
have supremum1/2. Thus the optimal bilateral bound among error-one
bijections is exactly1/2. No parity, period, sum or equivariance premise
is imposed on the competing maps in the lower bound.

This does not prove a universal forward-only lower bound1/2. It gives a
constructive forward upper bound1/2. No selected physical tariff follows.

## 1. Unrestricted lower bound from all sixteen corners

U^T=U and U^2=I. Coordinates of Hx have parity sum_i x_i. An integral
image has nine error-one integer neighbors: its center and eight signed
unit translates. A half-integral image has exactly16: the nearest two
integers in each coordinate. Each corner has squared error1; every other
integer point has squared error at least3.

For integer m>=2 take z_m=(m+1,m,m,m). Its image is
(2m+1/2,1/2,1/2,1/2), and A=||z_m||^2=4m^2+2m+1. Its16 outputs have
first coordinate2m or2m+1 and other coordinates0/1. The lower squared
norms4m^2+k,k=0..3 have multiplicities1,3,3,1; the upper norms
(2m+1)^2+k have the same multiplicities. Put B=4m^2+3 and C=(2m+1)^2.
Then B<A<C. The closest lower radius is sqrt(B), uniquely at(2m,1,1,1).
The upper radius has larger gap because

BC-(4m^2+2m)^2=3(2m+1)^2>0,
B+C=4A-2(4m^2+2m),

so sqrt(B)+sqrt(C)>2sqrt(A). The exact minimum absolute radial change
is beta_m=sqrt(A)-sqrt(B)=(2m-2)/(sqrt(A)+sqrt(B))→1/2.
Hence every total admissible map has R_abs>=sup beta_m=1/2, without any
injectivity, parity or matching premise. No finite beta_m equals1/2.

## 2. Half-grid colors and exact coset maps

Let Z_0={x∈Z^4:sum x_i even}, Z_1=Z^4\Z_0 and L_h=(Z+1/2)^4.
Split L_h into A={t:sum t_i odd} and B={t:sum t_i even}; its four
half-integers always have an integer sum. Define

J=diag(1,1,1,-1), E=JU, s=(1,-1,-1,1), R=UJU=I-ss^T/2.

These maps are orthogonal, R^2=I, and ER=U. U bijects Z_0 onto itself:
it is integral there, sum(Ux)=2x_0, and U^2=I.

R bijects Z_1 onto A. For odd x, s dot x is odd, so Rx is half-integral
in all coordinates. Its sum equals that of x since sum s_i=0. Conversely,
for t∈A, s dot t is odd: writing t=h+z, h=(1/2,1/2,1/2,1/2), gives
s dot h=0 and s dot z≡sum z_i≡sum t_i modulo2. Thus Rt is integral
with odd sum; R^2=I supplies the inverse.

E bijects B onto Z_1. For t=h+z∈B, z∈Z_0 and Ut=e_0+Uz is integral
with odd sum; J preserves integer parity. Conversely E^T y=UJy is
half-integral for odd y and has even sum2(Jy)_0. Orthogonality supplies
the inverse. These statements establish complete coset maps, not just
inclusions or finite counts.

## 3. A global involution on the half-grid

Use indices0,1,2,3. On axes0,1 pair, for k>=0 and sigma=±1,

{sigma(2k+1/2),sigma(2k+3/2)}, score2k+1/2.

On axes2,3 use{-1/2,1/2}, score0, and

{sigma(2k+3/2),sigma(2k+5/2)}, score2k+3/2.

Each coordinate rule partitions all half-integers into disjoint unit pairs.
At t select the coordinate with least(score,index), and toggle it to its
partner. Call the result M(t). Every score is unchanged, so the same
coordinate is chosen on return. The partner operation reverses itself:
M is a global involution. Its one signed unit step flips sum parity and
therefore restricts to inverse bijections A↔B.

## 4. Uniform radial bound

A central toggle preserves radius. For a noncentral chosen pair let a>0
be its lower absolute magnitude. Every other score is at least a. The
two opposite-phase scores are at least a+1, because the positive score
lattices1/2+2Z_>=0 and3/2+2Z_>=0 interleave; score0 would have won.
Their magnitudes are at least a+1. The other same-phase magnitude is at
least a. At the lower-magnitude endpoint of the edge, its radius r obeys

r^2>=a^2+a^2+2(a+1)^2=4a^2+4a+2=(2a+1)^2+1.

The squared-radius change is2a+1, so the radial jump is
(2a+1)/(sqrt(r^2+2a+1)+r)<(2a+1)/(2r)<1/2.
This treats either traversal direction, all signs, both phases and ties.

## 5. The lattice bijection, inverse and directional suprema

Set F(x)=Ux on Z_0 and F(x)=E M(Rx) on Z_1. The even branch bijects
Z_0 onto itself. The odd branch composes Z_1 --R→A --M→B --E→Z_1.
There are no cross-parity collisions. Its inverse is Uy on Z_0 and
R M(E^T y) on Z_1. For odd x, ERx=Ux and M changes one coordinate unit,
so the error is exactly1 by orthogonality of E. It is a nearest integer
output. The even branch is exact. The orthogonal R/E factors transfer
the strict radial bound to F and to its inverse.

For sharpness, let a=1/2+2k,k>=0. The point
t=(a,-a,a+1,a+1)∈A selects axis0 and toggles outward. In integer
coordinates this gives

x_out=(0,0,4k+2,1),
F(x_out)=(2k+2,2k+1,-2k-1,-2k-1).

Lower and upper squared radii are16k^2+16k+5 and16k^2+20k+7.
Their difference of square roots tends to1/2. For the reverse direction,
t=(a,a,a+1,a+1)∈B selects the same outward toggle. It yields

x_in=(2k+1,2k+1,2k+2,2k+1),
F(x_in)=(4k+2,0,-1,0).

This is inward by the same radial amount. Thus Delta_+(F)=Delta_+(F^-1)
=1/2 as suprema, with no individual input attaining a half-unit jump.

For any bijection G, Delta_+(G^-1)=sup_x(||x||-||G(x)||). Hence
max(Delta_+(G),Delta_+(G^-1))=R_abs(G). Section1 proves bilateral
optimality among all error-one bijections. It does not select a direction
for every competing G. Forward-only optimality remains a separate question.

## 6. Gaussian transfer and source-specific non-inheritance

Use S=diag(1,-1,1,1) and L(a,b,c,d)=(a,c,-d,b). The frozen R5 proof
checks H=L(2C_+)S, so F_C=L^-1 F S is an error-one bijection for the ideal
Gaussian pair C_+. Its actual inverse is S F^-1 L, which approximates
C_+^-1=C_- with the same error and radial bounds. Conjugating F_C by
complex conjugation K gives a different admissible approximation to C_-;
it is not asserted to be the inverse. At x=(-2,-2,-2,-1), the separate
exact root control gives K F_C K(x)=(-2,-2,-1,-2), whereas
F_C^-1(x)=(-2,-1,-2,-2). Signed-permutation transfer does not preserve
arbitrary stronger invariants of another nonlinear rounder.

For example F_C(0,0,2,1)=(2,-1,1,1), obtained directly from k=0 in the
outward family and L^-1. The exact complex pair sum changes from(2,1)
to(3,0). Thus this is not an automatic replacement for #6509's exact-sum
map. Separate exact root controls also show failure of Gaussian phase
covariance and fourth-power identity; their pinned receipts are evidence
about this construction, not premises of the universal radial proof.

No tensor-stage commutation, nonlinear native-graph consistency, actual
selected caller, same dirty-port wrapper, all-width precision propagation,
fixed-tape tariff or compiler/outer admission is established. Exact inversion
uses the stated inverse, rather than repeated positive calls or an ideal
linear identity. All five framework assumptions and kappa are unchanged.

## 7. Credit, relation to Q and evidence boundary

The current CubeJerry workstream supplied the staggered matching candidate,
its application to U and the constructive question. Coordinate pairings,
coset linear algebra and radial estimates are elementary classical methods.
The exact unrestricted corner lower bound is the bilateral consequence of
the preceding parametric ball-core analysis. Ali Romman/#6509 supplies the
ideal Gaussian pair and earlier stronger-invariant reversible rounding;
Nick Petalas/#6619 supplies the rational norm-contraction obstruction,
crediting ywz65/#2589's finite-ball argument. Frozen R5/compact Hall work
supplies the distinct forward lower bound sqrt21-sqrt19 and transfer.
All full predecessor notices and method credits remain effective.

The earlier minimum-coordinate contraction Q is not the bijection here:
Q(3,0,0,0)=Q(2,-1,-1,1)=(1,1,1,2). Its preserved checkpoint explains
why a local inward selector alone loses injectivity. The staggered M instead
uses partner-invariant scores, giving a genuine global involution.

The universal theorem rests on the explicit proof above. Independent C/root
implementations and finite controls corroborate it; no human or formal-kernel
acceptance is claimed. This proof/source review does not import those
implementations or C's search. Prepared with substantial OpenAI Codex
assistance, Apache-2.0. Publication is left to the root review process.
