# Sharp native cost through the QQ16 A-copy cut

This is a successor to PR2328, not a new controller or a recursive-rank
lower bound. Fix the literal `B_1_2[:80]` boundary in the main QQ16 packet.
It includes the first eight inverse X_T lines and all eight A-copy private
sweeps, including their 64 source cover maps. Event 80, the first future-Y
alignment, is excluded. Require the physical A/T shear from PR2216 before
this prefix. The typed shear correction and its initial-normalization
implementation are credited to PR2252 and PR2328, respectively.

The resulting endpoint requires exactly **24 atomic single-field native
line calls**, compared with 16 in the inherited prefix. This remains true
when arbitrary scalar-linear resynthesis and arbitrary orthogonal cover
maps with even translations are free. In particular these later A-copy
operations cannot absorb the shear's eight extra native lines in this
model. The free scalar coefficients are uniform over owners and independent
of payload addresses and frequencies; they act at the same owner/address.
Cover maps outside that even-translation class, later cuts,
multi-field native primitives and splitting the internal wrappers of a
native recipe are outside the theorem.

## The exact operator boundary

Write `A=[0,7,20,27,36,46,57,111]` and
`T=[21,37,47,76,81,87,92,110]`. At an owner d the inherited common X frame
is F, and port p's Y frame is `F C_(dq_p)^-1`. The common invertible F
commutes with the translation lines, so the logical shear takes the
physical form below. No conjugation of the cover maps by F is used.
Use a, t and v for the eight actual physical input X_A, X_T and
Y_T coordinates, and y for physical Y_A. No logical-zero assumption is
made about any of these coordinates or about the 480 ordinary helpers.

The shear in physical coordinates is

    X_T <- t+a,       Y_T <- v-C_T^-1 a,       X_A <- a.

The diagonal C_T has the eight selected q_T labels; the inverse acts on
the source's payload before its contribution reaches Y_T. A bare physical
`Y_T -= X_A` has the wrong operator and incompatible native frames.

For A port p let V_(p,t) be the literal completed source path for target
t, and let D_(p,t) be the signed half coefficient in that private sweep.
Every row has four nonzero D coefficients, all in T. The exact prefix
endpoint after the shear is

    X_T' = C_T^-1(t+a),
    Y_T' = v-C_T^-1 a,
    X_A'[p] = a[p] + C_(dq_p) (y[p]
                    + sum_t D_(p,t) V_(p,t) C_(dq_t)^-1(t[t]+a[t])).

Here `a[t]` denotes the A input paired with T port t, not an A port with
the same numeric index. All other persistent fields are unchanged.
Each source path is undone after its row. C0 is an existing owned
private register: its arbitrary input is discarded and its output is
zero in I after each private sweep. C1 through C7 remain arbitrary and
unchanged at this cut; they are cleared only by the later retained core.

At **one payload tensor layer (`lambda=1`)**, the checker uses exact
Gaussian rational coefficients and the ordered affine group algebra, with

    M(g,delta) f(d,z) = f(dg,z XOR d delta),
    M(g,a) M(h,b) = M(gh,a XOR g b).

At that tensor length it compares all 712 output rows of the constructed upper word against
the literal inherited prefix composed with the physical shear. This is
an equality of complete ordered affine-operator expressions, before any
character restriction; it suffices for all owners and arbitrary input
arrays at `lambda=1`. Equality is not inferred merely from the two
characters below. The finite nine-axis native recipe binding is checked
separately. This affine replay does not expand a native tensor power at
larger lambda: `C_q tensor C_q` has eigenvalue `i*i=-1` on an odd/odd
character, whereas a two-term simultaneous-translation surrogate has
eigenvalue 1 there. An explicit exact negative control rejects that
incorrect substitution.

The all-layer upper bound instead uses a formal linear-operator identity.
For any linear operator `N_t`, the per-pair constructed prefix executes

    C0 <- 0; C0 <- a; t <- t+a; C0 <- N_t a;
    v <- v-N_t a; C0 <- 0; t <- N_t(t+a).

Its data and persistent-field endpoint is exactly the physical shear
`t <- t+a, v <- v-N_t a` followed by the inherited normalization `N_t`
on t, with a unchanged. The constructed prefix returns C0 zero; the
physical-shear-plus-normalization reference still has arbitrary initial
C0 at this intermediate boundary. Literal suffix events 8 through 11
only map X_T, and event 12 clears C0 before its first read. That clear
annihilates the sole intermediate scratch difference, giving equality
on all 712 fields at the selected final cut. This identity uses only linearity;
it holds in particular for the actual `N_t=(C_(dq_t)^-1) tensor lambda`
at every positive integer lambda. The subsequent literal events 8
through 79 are identical in both compositions, so their complete ordered
operators, helper outputs and scratch outputs remain equal for all such
lambda. A second checker independently replays all 712 endpoint rows as
rational word polynomials in arbitrary noncommuting native and map
operator symbols. It uses one symbol for each literal signed recipe or
cover-map label, without expanding C_q or using any inverse relation.
The constructed word and the inherited word after the physical shear
have identical word-polynomial rows. A changed conversion/subtraction
order is rejected. Interpreting these symbols as the actual tensor
operators proves the all-layer endpoint identity. This fresh formal
operator equality and its tensor interpretation are separate from the
one-layer affine replay. The affine composition law for the unchanged
source maps, and equality of their per-layer frame polynomials, apply
to every layer and supply the same path restoration and typed access.

## A character preserved by the later source maps

Let `Omega=(1<<73)-1`, the characteristic vector for the standard binary
bilinear form. Every orthogonal binary matrix g fixes Omega. Indeed

    Omega dot g v = (g v) dot (g v) = v dot v = Omega dot v

for all v; hence `g^T Omega=Omega`, and invertibility also gives
`g Omega=Omega`. Consider two owner-covariant payload functions with
constant amplitude over owners:

    f_0(d,z)=1,
    f_Omega(d,z)=(-1)^(Omega dot d^-1 z).

The owner matrices d and g are orthogonal. Apply the actual cover action:

    M(g,delta) f_Omega(d,z)
      = (-1)^(Omega dot (g^-1 d^-1 z XOR g^-1 delta))
      = f_Omega(d,z) (-1)^(Omega dot delta).

Thus an even translation delta makes every such map the identity on
both functions. This explicitly includes the owner action; a fixed-owner
payload Fourier mode alone would not justify erasing owner maps.
The source checker verifies orthogonality and even translation for all
64 map events in the selected cut. Arbitrary repetitions, inverses and
products of this class remain in the class. The lower-bound relaxation
may therefore grant any such maps for free, not just their selected order.

A native line `C_(dq)^epsilon` has eigenvalue 1 on f_0 and
`i^(epsilon*(Omega dot q))` on f_Omega. The 16 native labels used by the
inherited cut are odd. Thus inverse T lines have value c=-i, and positive
A lines value b=i. Any arbitrary native label allowed in the relaxation
still changes at most one field coordinate between the two evaluations.

For multiple positive tensor layers choose f_Omega on one layer and
f_0 on the others. The simultaneous owner-relative translations on all
layers then give exactly the same invariant and native eigenvalues.
The lower bound requires at least one payload layer; it makes no claim
for the degenerate zero-layer specialization. The input/output frames
are invertible coordinate changes on independent arbitrary physical
arrays, so they impose no relation that could remove the minor's inputs.

## The 24-dimensional minor

At the two invariant characters every source path is identity. At f_0
both b and c are 1; at f_Omega they are i and -i, so bc=1 in both cases.
Consequently, with D the scalar signed-half matrix, the evaluated map is

    X_T' = c(t+a),
    Y_T' = v-ca,
    X_A' = a+b y+D(t+a).

Only the X_T, Y_T and X_A output rows differ. Set `d=-1-i`. Order the
first 16 rows in paired `(X_T,Y_T)` order and their input columns in
paired `(X_A,X_T)` order; append the eight X_A output rows and Y_A input
columns. The difference minor is block diagonal: eight blocks

    d [ 1  1 ]
      [-1  0 ]

and an eight-dimensional diagonal `(i-1) I`. Its determinant is

    d^16 (i-1)^8 = 256 * 16 = 4096.

It therefore has rank 24, exactly, since only 24 output rows differ.
The checker computes this Gaussian rational determinant from the full
literal operator and records the exact field indices. Without the shear
the only differing output rows are X_T and X_A; the corresponding
16-dimensional minor is nonsingular and the inherited difference rank
is exactly 16.

Now take any finite circuit in the stated relaxation, with arbitrary
additional scalar registers. Pad its register set to fixed size. Evaluate
the circuit on f_0 and f_Omega and telescope the difference of the two
matrix products. A free scalar gate has zero difference. A free
orthogonal/even-translation map has zero difference. Each atomic
single-field native line has difference rank at most one. Product rank
and subadditivity therefore bound the endpoint difference rank by the
number of paid lines. Restricting to original inputs and required outputs
cannot increase rank. This argument allows noninvertible free scalar
operations, copying, projections, owned clears, finite zero-initialized
scratch and discarded private input columns. The rank-24 minor proves
that at least 24 lines are necessary.

## Typed attainment and the complete local invoice

Use PR2328's typed 16-line shear-plus-initial-normalization prefix: for
each pair, clear C0 in F, add X_A to C0 and X_T, apply the inverse T line
to C0, subtract C0 from Y_T, clear C0 to I, and execute the original
inverse X_T line. Append the unchanged literal events 8 through 79.
Every scalar ADD has equal exact phase polynomials, every source path
is restored, and every private body has the whole-owner barrier and
initial/final owned clears. This yields the desired complete endpoint
with 24 lines and no new field.

| Charge | Inherited cut | Attaining sheared cut | Difference |
|---|---:|---:|---:|
| Atomic rank-one native lines | 16 | 24 | +8 |
| Native recipe wrapper maps | 32 | 48 | +16 |
| Explicit cover maps | 64 | 64 | 0 |
| Complex scalar ADDs | 48 | 72 | +24 |
| Owned CLEARs | 16 | 32 | +16 |
| Private row sweeps | 8 | 16 | +8 |
| Scalar real-primitive allowance | 480 | 704 | +224 |

The scalar allowance charges 8 per unit complex ADD, 10 per half ADD,
and 2 per CLEAR. Native children and all map costs remain separate.
The lower bound is sharp for native-line count, not necessarily for the
scalar/map invoice. No physical stream/address cost, precision envelope,
child hosting, controller closure, supplier admission or new kappa follows.

The retained QQ16 maps, source paths, native recipes and arbitrary-helper
contract are credited to Ali Romman's PR1969 and its conserved-QQ16
source contributors. Cinna Davis's PR2216 supplies the shear, Charles
Bethin's PR2252 its native-frame warning, and PR2328 supplies the sharp
initial-prefix obstruction and typed upper construction. The new step
here is the owner-covariant characteristic-vector invariant for the
actual even source routes, its exact later cut and sharp 24-line boundary.
Substantial OpenAI Codex assistance was used. New material is Apache-2.0.
