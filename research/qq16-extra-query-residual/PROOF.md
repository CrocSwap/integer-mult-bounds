# Residual selected information after a free pre-F0 ordinary query

The fixed QQ16 `F0/B1` pair and retained ordinary bank schedule still
cannot restore every original selected input after the complete value
`B2 X_U` is supplied immediately before `F0`. This statement grants that
query exact, free, read-only access and indefinite retention. There are
at least `ceil(32 |G| / 7)` independent missing selected-input directions
on a finite regular cover `G`. This is an information-space dimension,
not a paid recursive-child rank or a native operation count.

This note addresses Cinna Davis's proposed extra query in
[PR #2079](https://github.com/CrocSwap/integer-mult-bounds/pull/2079),
head `49df8190b158e3028e702b2c6b798117006f7249`, and
[discussion #2074](https://github.com/CrocSwap/integer-mult-bounds/discussions/2074).
The source checkout is `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
The predecessor identifies a real observation absent from the old
witness. The new result is that supplying that particular observation
does not suffice for this fixed controller.

## Exact model and source obligations

Use the sets and ordered maps in
[`CONSERVED-QQ16.md`](../joint-query/evidence/CONSERVED-QQ16.md) and
[`JOINT-QUERY-TRANSFER.md`](../joint-query/evidence/JOINT-QUERY-TRANSFER.md):

```text
A = [0, 7, 20, 27, 36, 46, 57, 111],
T = [21, 37, 47, 76, 81, 87, 92, 110],
U = {0,...,111} minus (A union T),   |U| = 96.
```

Write `R_s = R D_s`, `B_s = R_s iota_U`, and
`ell_(s,A) = R_A pi_A D_s`. The selected section `P_(s,A)` satisfies
`ell_(s,A) P_(s,A) = I` and is supported on A. Define the analogous T
section and query. All selected sections are dyadic units between the
eight selected coordinate fields and the eight query coordinate fields.
Stage zero has `D_0 = I`.

Let `G` be the finite cover group, or a finite subgroup containing all
routes used below, with its regular right action. Put `N=|G|` and work
over `Q`. For a cover route `g`, write

```text
(Q_g f)(d) = f(d g),        Q_g Q_h = Q_(g h),
Q_g* = Q_(g^-1),            tr(Q_g) = N if g=1, else 0.
```

The last equality requires this regular action. Distinct abstract route
labels in a nonfaithful quotient representation would not suffice.
The actual routes are finite binary invertible matrices; the subgroup
they generate is finite. A larger cover splits into orbits `dH` of
the subgroup H's right action, so the calculation applies per orbit.

For `p in U`, let `r_p` be column p of R and `g_(s,p)` the actual
stage-s route. On logical fields constant in every payload coordinate,

```text
B_s = [ r_p Q_(g_(s,p)) ]_(p in U).
```

This restriction keeps arbitrary independent cover values. It does
not identify cover owners. The full cover action is
`f(d,z_1,...,z_lambda) -> f(d g,z_1+d delta,...,z_lambda+d delta)`;
payload translations act trivially on these constant logical fields.
Thus they form an invariant subspace of the routed logical maps at
every positive tensor size. The proof uses the inherited invertible
endpoint-frame conventions, including their phases, as bound by
[`BRIDGE-REVIEW.md`](../joint-query/evidence/BRIDGE-REVIEW.md), sections
1--4. Converting the logical initial state to physical input coordinates
is an invertible frame change, as is converting each output endpoint.
Zero observations remain zero, and a nonzero required selected value
remains nonzero. No new assertion that a native frame fixes the constant
function is needed for the rank argument.

The finite, source-bound checking obligations are precisely:

1. `r_p^T r_p=4` for every `p in U`, and
   `sum_(p in U) r_p r_p^T = 48 I_8`.
2. For each separate pair `(s,t)=(0,1),(0,2),(1,2)`, the 96 labels
   `g_(s,p) g_(t,p)^-1`, as p ranges over U, are distinct.

Labels need only be distinct within each pair, not across the union
of all three lists. The companion exact route check discharges these
finite obligations using the actual source columns and route matrices.
The proof below does not enumerate G, compute its size, or expand a
full regular-representation matrix.

## Three-query rank bound

Each query is a scaled coisometry:

```text
B_s B_s* = sum_p r_p r_p^T tensor I_G = 48 I_(8N).
```

For `s != t` set `C_st=B_s B_t*`. If
`a_p=g_(s,p) g_(t,p)^-1`, then

```text
C_st = sum_p r_p r_p^T tensor Q_(a_p).
```

In `C_st C_st*`, a term has identity route exactly when `a_p=a_q`.
Pairwise route injectivity forces `p=q`. Its identity coefficient is

```text
sum_p (r_p r_p^T)^2
  = sum_p (r_p^T r_p) r_p r_p^T
  = 4 sum_p r_p r_p^T
  = 192 I_8.
```

Nonidentity routes have zero regular trace. Consequently

```text
tr(C_st C_st*) = 1536 N,                s != t,
tr((B_s B_s*)^2) = 18432 N.
```

Stack the three maps as `S=[B0; B1; B2]`, and put `K=S* S`. Then

```text
tr(K)   = 3 (8)(48) N = 1152 N,
tr(K^2) = 3 (18432) N + 6 (1536) N = 64512 N.
```

The real symmetric matrix K is positive semidefinite. Cauchy--Schwarz
on its nonzero eigenvalues gives

```text
rank(S) = rank(K) >= tr(K)^2 / tr(K^2) = (144/7) N.
```

All entries are rational, so rational and real matrix ranks agree.
Let `Q=[B1; B2]` and `V=ker Q`. Projection from the image of S onto
the image of Q is surjective; its kernel is
`{(B0 h,0,0): h in V}`. Thus

```text
rank(B0 restricted to V) = rank(S) - rank(Q)
                        >= (144/7) N - 16 N
                        = (32/7) N.
```

In particular,

```text
dim_Q B0(ker B1 intersect ker B2) >= ceil(32 N / 7) > 0.       (1)
```

No assertion that `rank(Q)=16N` is needed.

## Rational, integer, and dyadic inputs

Equation (1) supplies an h with

```text
B1 h = B2 h = 0,          B0 h != 0.                         (2)
```

This can be chosen rational: a rational nullspace basis for Q spans
its real kernel, and B0 cannot annihilate every vector in that basis.
Clearing the finitely many denominators gives an integer h satisfying
(2). All selected sections are dyadic, so the initial logical data
below are dyadic. Multiplying h by a further common power of two also
makes those finitely many initial selected values integer. Conversely,
division of the complete input by a sufficiently large power of two
fits any prescribed positive magnitude bound without losing (2).

For each fixed tensor size, the inherited frames and their inverses
are finite products of native lines and translations with
Gaussian-dyadic coefficients. The physical pullback is therefore an
admitted exact complex dyadic input. The rational and integer
statements above concern logical coordinates; the obstruction does
not require a general frame to preserve real-valued physical arrays.

This is an exact existence proof on each finite regular cover. It does
not exhibit a compactly supported formula for h independent of N,
bound the denominator or bit length needed for a chosen magnitude
bound, or provide a recursive precision implementation.

## Ordered trajectory through the fixed first two calls

Set all other pairs, helpers, and private fields initially to zero.
In pair 0 take

```text
X_U = h,                    Y_U = 0,
X_A = -P_(0,A) B0 h,        Y_A = P_(0,A) B0 h,
X_T = 0,                    Y_T = 0.                       (3)
```

Zero helper values are permitted under an arbitrary-input contract;
failure on this subspace already precludes universal restoration.
The two selected pair sums vanish. Also `X_A != 0`, because
`ell_(0,A) P_(0,A)=I` and `B0 h != 0`. The added pre-F0 observation is
exactly

```text
q_extra = B2 X_U = B2 h = 0.                               (4)
```

The forward map at chart 0 is

```text
f0 = B0 X_U + ell_(0,A) X_A + ell_(0,T) X_T,
X'_U = X_U - K_(0,U) f0,
X'_A = P_(0,A) ell_(0,T) X_T,
X'_T = P_(0,T) f0,
Y'_U = Y_U + X'_U,
Y'_S = X_S + Y_S - X'_S,                 S=A union T.
```

Substitution of (3) gives `f0=B0 h-B0 h=0`, so after F0,

```text
X_U=Y_U=h,           X_A=Y_A=X_T=Y_T=0.                    (5)
```

For the backward call B1 with future chart 2, define

```text
E2 = I + P_(2,A)(R2-ell_(2,A)),
u = E2 Y,        a1=ell_(1,T) X,        b1=R1 u.
```

On (5), the full future query `R2 Y` equals `B2 h=0` and the
selected A baseline is zero. Therefore `u=Y`, `a1=0`, and
`b1=B1 h=0`. The conserved backward formulas are

```text
Y'_A=u_A,
Y'_U=Y_U+K_(1,U) a1,
Y'_T=u_T-P_(1,T)(b1+11a1),
X'_U=X_U-Y_U,
X'_A=X_A+Y_A-u_A,
X'_T=P_(1,T)(b1+12a1).
```

They leave exactly

```text
Y_(0,U)=h; all other ordinary and selected fields are zero. (6)
```

Every cancellation uses the displayed order of operators. No two
chart routes, selected sections, or query operators are commuted.

## Retained observations and restoration obstruction

State (6) is exactly the post-B1 state used by the predecessor
[`selected-output witness`](../joint-query/evidence/QQ16-SELECTED-WITNESS.md)
and its
[`rational observation review`](../joint-query/evidence/QQ16-RATIONAL-OBSERVATION-REVIEW.md).
We retain that ordinary bank schedule and its source-bound tail
statement. The positive `(0,1)` bridge places `-h` in `Y_(1,U)`.
F2 has zero X source and makes no change. The negative bridge removes
that `-h` before B3. Later active ordinary pairs have zero inputs.
The last three ordinary bridges leave only `Y_(0,U)=h`, and the
terminal moves it to named `X_(0,U)` with the former-Y native type.
Every completed-X descendant is zero. The predecessor's independent
tail receipt also includes the control that omitting the first
negative bridge fails at B3.

The first two calls remain exactly the fixed F0/B1 pair derived above;
the observation grant does not insert a changed controller between
them. All selected fields are already zero after F0 and remain zero
after B1. Subsequent homogeneous selected-only linear operations
therefore keep them zero, including cross-bank, port, cover and
selected-terminal maps. They must not read ordinary data. All five
forward query histories
`f0,f2,f4,f6,f8` are zero. Equation (4) adds another zero observation.
Thus the entire allowed record

```text
all selected output endpoints from F0 onward,
all completed-X descendants at the retained output endpoint,
all five forward-query histories,
the complete pre-F0 value B2 X_U
```

is identical for (3) and the zero input, while the required original
selected value `X_(0,A)=-P_(0,A) B0h` differs. No decoder determined
only by that record can restore all original selected inputs. This
indistinguishability argument is stronger than a restriction to
rational-linear decoder coefficients. The record does not include
an intermediate ordinary read of `X_U=h` immediately after F0.
Granting the selected F0 output as an additional read-only observation
does not authorize changing the fixed first pair.

More quantitatively, varying h over V gives an invisible family whose
original selected A values have dimension `rank(B0|V)`. By (1) that
dimension is at least `ceil(32N/7)`. Any additional *linear* observation
map that restores every such selected value must have at least this
rank on that family: its kernel there must be contained in the kernel
of the required selected-value map. This remains a statement about
information dimension, with no conversion to native or recursive cost.

As a positive distinction, a retained initial observation `B0 X_U`
detects every member of this family with nonzero selected defect,
because the required A value is exactly `-P_(0,A) B0 X_U`.
This does not prove that adding B0 repairs other inputs or closes the
whole controller.

## Covered domain and remaining obligations

The theorem covers these exact F0/B1 maps, the retained ordinary tail,
restoration on arbitrary rational or dyadic logical inputs, regular
cover action, every positive payload tensor size, and the specified
side-effect-free ordinary query `B2 X_U`. The chosen witness is dyadic
and has an admitted complex dyadic physical pullback. The same finite
source obligations imply the dimension theorem for every finite
regular cover containing the distinct route labels.

The full original query `R2 X` is a different observation: on (3) it
equals `-ell_(2,A) P_(0,A) B0 h` and need not vanish. Neither the old
selected witness nor this note silently substitutes it for `B2 X_U`.
Changes to the first local pair, ordinary-to-selected access, source
mutations, extra observations, or a different ordinary schedule require
a new analysis. Restoring only the conserved selected pair sums is also
a weaker task than restoring the arbitrary original selected inputs.

The new rank and first-two-call arguments are written all-parameter
linear-algebra proofs. Actual column and route premises are finite exact
checks. The later bank schedule is an explicitly inherited,
source-bound predecessor obligation, not a newly derived general
scheduling theorem. No formal-kernel proof is claimed. Native address
access, precision bounds, paid recursive costs, complete supplier
admission, and a multiplication-exponent improvement remain outside
this result.

The QQ16 maps, cover semantics, old witness, and retained schedule are
credited to the contributors recorded in `research/joint-query/NOTICE.md`.
Cinna Davis proposed the additional ordinary query being tested here.
This residual proof and its checking used substantial OpenAI Codex
assistance. New material is Apache-2.0.
