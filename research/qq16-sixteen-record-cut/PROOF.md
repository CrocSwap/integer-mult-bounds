# Sixteen retained arrays for a changed immediate-cut contract

## Scope and sources

PR2443 recovers the original QQ16 pair-0 input from a specified two-cut record;
PR2456 independently checks its ordered routed operators. PR2470 counts that
record's retention and gives an L2 alternative using 32 early selected arrays,
plus additional current ordinary Y reads. We change that L2 observation contract
by using the **current selected pair sums** and retaining only selected X.
PR2480 subsequently proves that 24 early arrays are necessary and sufficient
for the same 200 live outputs `X2_U,Y2_U,Y2_A`. Our read set replaces the last
eight outputs by sixteen selected sums: eight more outputs, 24 more physical
fields, and eight fewer early retained arrays than that sharp result. Neither
fixed interface's bound applies to the other. All preceding results retain credit.
PR2468 supplies the signed native
line conventions and an actual future-X query read; its 192-child query is not
silently assumed free or imported into our bill.

Use the actual sets A,T of eight ports each, U of 96 ports, and V=A union T.
Let `(x1,y1)=F0(x,y)` and `(x2,y2)=B_1_2(x1,y1)`. Decode immediately after
the completed B1 call, **before the next bridge**. The archive's actual first
two events are these consecutive calls on pair 0. Other bank pairs can be
arbitrary, but are not touched or observed in this prefix.

The decoder receives exactly:

| Block | Arrays | Time | Meaning |
| --- | ---: | --- | --- |
| r | 16 | retained after complete F0 | `x1_V` |
| c | 96 | current after complete B1 | `x2_U` |
| z | 96 | current after complete B1 | `y2_U` |
| s | 16 | current after complete B1 | `x2_V+y2_V` |

Thus there are 16 early array coordinates and 208 current observation coordinates.
The current observations depend on **224 physical fields**, because each selected
sum uses two fields. The interface exposes the completed sums, not their two
summands or a sum macro's intermediate values. If the individual selected X
values are also exposed, the full post-B1 state can be reconstructed and zero
early retention suffices; this was already noted in PR2470. The theorem below
is a sharp bound for the stated output interface, not an unrestricted controller
or memory minimum. Current Y_U reads are a changed assumption from PR2443.

An array is an arbitrary rational-valued function on the common finite
owner/payload domain Omega; let N=|Omega|. More generally the sufficiency holds
in any common array module where the retained route operators and their inverses
are defined. For the rank lower bound fix the finite rational vector space
Q^Omega. Count total rank of retained rational-linear information, allowing
arbitrary mixing across owners and payload coordinates.

## Ordered reconstruction

Use the source's actual routed operators

```text
ell_(j,W) = R_W D_(j,W),
P_(j,W)   = D_(j,W)^-1 R_W^-1,           W=A,T,
K_(j,U)   = D_(j,U)^-1 R_U^T/4.
```

The selected Grams are `R_A R_A^T=R_T R_T^T=4I`; routes are port-dependent
operators and must not commute through scalar mixtures. The two equations in
CONSERVED-QQ16 (1) for ordinary outputs are exactly

```text
c = x1_U-y1_U,
z = y1_U+K_(1,U) ell_(1,T) x1_T.
```

The four selected output equations give the source's conserved sums, hence
`s=x1_V+y1_V=x_V+y_V`. All c,z,s above are expressions of **current** fields;
there is no substituted past Y value or future endpoint.

The retained r gives both x1_A and x1_T. Recover in this order:

```text
h    = ell_(1,T) r_T,
x1_U = c+z-K_(1,U) h,
f    = ell_(0,T) r_T,
t    = P_(0,T) ell_(0,A) r_A,
x_U  = x1_U+K_(0,U) f,
x_T  = t,
x_A  = P_(0,A) (f-B_0 x_U-ell_(0,T) t),
y_U  = -c,
y_V  = s-x_V.
```

Here `B_0=R_U D_(0,U)`, with the source's initial chart. The first two equations
are PR2470's L2 identity. The X reconstruction is the credited F0 inverse from
PR2443/2456. The new step is that, once the entire x1_U is obtained this way,
the intermediate selected Y1 data and future A logger are unnecessary: use
the current conserved sums for original selected Y, and c for ordinary Y.
No 88-port read, unread minor inverse or `B_2 c` query is used by this contract.

These identities prove `decode observe=I` on every original pair-0 array.
They hold in the ordered operator ring; there is no commuting-routes assumption.
In particular, logical `D=(rho,0)` must not be replaced by the physical native
alignment `M(rho,delta)`. The retained operator algebra computes both inverse
orders using all 224 independent formal arrays and the actual 73-dimensional
routes. The injected physical/logical substitution has a nonzero payload
residual while passing after all payload translations are forgotten.

## Matching lower bound, without a finite-to-universal inference

For arbitrary r,c,z,s, the reconstruction above defines original x,y. Applying
F0 followed by B1 gives exactly those r,c,z,s. One direct way to see the second
order is to set x1_V=r and x1_U=c+z-K1 ell1T r_T, reconstruct X by the exact
F0 inverse, then set original y_U=-c and y_V=s-x_V. F0 gives
`y1_U=-c+x1_U`; B1 therefore gives c and z as specified. Both maps preserve
selected sums, giving s. The selected F0 X output is r by its inverse identity.
Thus the combined map

```text
T : Q^(224N) -> Q^(16N) x Q^(208N),    original -> (r, live)
```

is a linear isomorphism, with the displayed inverse. Its live projection is
surjective of rank 208N and has a kernel of dimension **16N**. If another
retained rational-linear record L has rank less than 16N, its restriction to
this kernel cannot be injective. A nonzero element of `ker(live) intersect
ker(L)` has the same observations as zero and cannot be fully recovered.
Therefore total retained linear rank at least16N is necessary. The 16 arrays r
attain it. This allows arbitrary cross-owner/payload mixing in L; it does not
claim a bound for unrestricted discontinuous encodings, additional current
observations, final-only cuts or different target recovery tasks.

The proof is the explicit operator isomorphism, not a sampled numerical rank.
The checker also parametrizes the entire live kernel by 16 independent formal
arrays, verifies every single retained coordinate has a nonzero invisible
witness when omitted, and runs the inverse in both orders on free observations.
The separate `independent.py` checks exact ranks on the constant-owner/payload
subspace using modular elimination on two primes, without importing either
operator checker. This corroborates a finite case only. It also verifies that
16 early Y coordinates are an alternative attaining record, redundant early
sums do not help, and exposing current selected X eliminates early retention.

## A concrete local read of the current selected sums

The native source states that the immediate post-B1 types at owner d are

```text
X2_p : F_(d U1),
Y2_p : F_(d U1) C_(d q_p)^-1,    p in V.
```

Consequently an unnormalized scalar addition of their physical arrays is
invalid. For each selected p, own an output O_p in frame F_(d U1) and execute

```text
CLEAR O_p;  Y2_p <- C_(d q_p) Y2_p;
O_p += X2_p;  O_p += Y2_p;
Y2_p <- C_(d q_p)^-1 Y2_p.
```

Frame operators commute because they are products of translation operators.
The middle Y is exactly in the X chart. The output holds the desired logical
sum and both sources restore physically. These operations access only current
fields and can complete before the next modifying bridge. All 16 output arrays
are additional **owned** storage; their prior contents are discarded. The
macro does not claim to restore borrowed dirty output buffers.

The actual q are reconstructed from the source phase archive. The credited
normalization uses a binary invertible G with G e0=q:
`C_q=P_G C_e0 P_G^-1`, and `C_q^-1=T_q P_G C_e0 P_G^-1`.
The translation fuses into a monomial wrapper. Both signs have one positive
rank-one child and two wrappers. The checker compares both Gaussian kernel
coefficients at all 512 local basis addresses for each of 16 ports/signs,
16,384 columns total. It replays the literal 80-event macro with independent
X/Y/output content and all local Fourier characters, including physical Y
restoration. Equality of complete local operators lifts by owner conjugation
and tensor powers; arbitrary spectators are unchanged. These are exact local
identities, not native owner allocation or a tape implementation.

The local sum read costs 32 rank-one children, 64 monomial wrappers, 32 signed
ADDs, 16 CLEARs, no cover maps, and 16 owned outputs. Under the same retained
per-real-component primitive allowances as PR2468, the scalar allowance is
`2*(4*32+16)=288`, excluding child/wrapper/storage costs. It is one part of the
changed decoder. Retaining r across B1, reading all192 current ordinary arrays,
the routed reconstruction, conversions between earlier/current charts, output
storage, cleanup, complete hosting, precision and all-size costs remain unpriced.
No favorable completed moment or new kappa follows from this partial invoice.

PR2492's paid ordinary L2 reconstruction already uses this normalization/sum/
restoration pattern on U, followed by stage removal and routed correction.
Its 400 H1 + 96 H8, 208 cover maps, 992 wrappers, 6,624 scalar primitives,
96 owned outputs and one scratch are a separate partial construction, not a
free logical subroutine or the complete decoder. The selected-port sum pattern
here retains that method's credit. Its role in this result is to implement the
new observation interface, whose complete ordered inverse and kernel were
proved above. In particular, the sixteen new owned current sum outputs must be
scheduled alongside earlier records and PR2492's old-frame outputs before any
net cost or storage comparison is possible. The changed contract removes the
future logger dependency; it does not demonstrate a cheaper supplier.
