# A joint current-query exchange with two selected minors

This construction uses an existing selected X minor as an arbitrary
query register. It does not clear that input or add a productive field.
The joint map retains all original X and Y inputs. It gives two distinct
query records: the future query in Y_A and the current query before
exchange in X_T. The ordinary source response is driven by the old
selected X_T value. This is an ordered local algebra result. The native
word, its complete invoice, and the changing-chart controller remain
separate checks.

## Maps and selected coordinates

Use the actual disjoint orthogonal minors

    A=[0,7,20,27,36,46,57,111],
    T=[21,37,47,76,81,87,92,110].

Let S=A union T and let U be its 96-port complement. In the current
chart s write R=R_s, K=K_s, J=I-KR. The injections K_A and K_U have
zero rows outside their named sets. Set

    P=P_(s,T),      L=ell_(s,T),      Pi=P L.

Here P=D_s^-1 iota_T R_T^-1 and L=R_T pi_T D_s. Thus RP=LP=I,
Pi is the ordinary coordinate projector onto T, and K_T=P. Also

    R K_A=I,       R K_U=12I.

All these formulas hold over the ordered cover coefficient ring. The
normalization by R_T is part of the query basis; it must not be omitted.

Define a source transvection

    Z=K_U-12P,     H=I+ZR,     H^-1=I-ZR.         (1)

Since RZ=0, both inverse orders in (1) are exact. The source query is
unchanged by H. The target response has only selected error rows:

    RH=R,         JH=I-(K_A+13P)R.               (2)

Let t be the next chart, and use the systematic future logger

    E=E_t=I+N_t,
    N_t=P_(t,A)(R_t-ell_(t,A)).

Then N_t has only A output rows and no A input columns, N_t^2=0,
and ell_(t,A) E=R_t. Its inverse is I-N_t. The source matrix H in
(1) changes the T rows. Therefore this construction is outside the
selected-baseline interface in SELECTED-BLOCK-NECESSITY.md.

## Complete pair map

For arbitrary original inputs x and y define

    u=E y,        a=Lx,        b=Ru,
    v=u+P(a-b).                                      (3)

The change (u,a) to (v,b) is the full-query exchange. Since RP=I,

    Rv=a,         u=v+P(b-Rv).                       (4)

Thus this change is an involution on the source and the eight selected
register values. It does not require an initialized register.

The complete desired backward map is

    y'=H v,
    x'=(I-Pi)(x-y)+P b.                             (5)

All X rows outside T perform the exact subtraction x-y. The T rows
contain the clean normalized current query P b. They do not perform
the original target subtraction. The source output has the exact rows

    y'_U=y_U+K_U a,
    y'_A=u_A,
    y'_T=u_T-P(b+11a).                              (6)

In particular,

    ell_(t,A)y'=R_t y,
    Lx'=b=R_s E_t y,
    R_s y'=a=ell_(s,T)x.                            (7)

The three expressions in (7) are different values. The first is the
future query of the original source. The second is the current query
after the future source encoding and before the exchange. The third
is the old normalized selected target input. No equality between these
queries is assumed.

The 96 ordinary source rows in (6) depend on the old selected target
input a, rather than on an unrecorded new ordinary source query. The
Y_A record is in its ordinary source endpoint frame. The X_T record
is in its completed target endpoint frame. A clean scalar query does
not by itself put those two records into one common native frame.

## Exact inverse and restoration boundary

Given all of x' and y', compute in this order

    v=H^-1 y',
    b=Lx',        a=Rv=R_s y',
    u=v+P(b-a),
    y=E^-1 u,
    x=(I-Pi)(x'+y)+P a.                            (8)

Equations (3)--(4) prove both inverse orders. This restores arbitrary
selected target inputs and arbitrary source inputs, not just their
centre projections. It is an algebraic inverse. It is not a free
decoder at the final Y hole frames: the read a=R_s y' can be an old
chart query there. A controller must retain a usable selected history,
or give a native implementation of that read and its later writes.

For the next chart put

    L_ts=R_tP,
    D_ts=R_tK_U-11L_ts.

Then the exact future query relation is

    R_t y'=R_tu-L_ts b+D_ts a.                     (9)

The leading term R_tu is not the stored future query q=R_t y. Instead,

    R_tu=2q-ell_(t,A)y.                           (10)

A unit D_ts would recover a from the other terms only when those
terms have actual access. Its value is I in the constant-chart centre
sector. That value does not prove that the actual routed D_ts is a
dyadic operator unit. Equation (9) does not remove the old A baseline
in (10).

## A core-compatible native sequence to check

At the actual backward entrance, Y has its common local source type
and X_p has the intrinsic input line C_p. The following sequence gives
(5) algebraically and identifies the needed native operations.

1. Apply E_t to Y, obtaining u. This uses the future source alignment.
2. Apply the inverse intrinsic line to each of the eight X_T fields.
   Align those fields with the current common Y frame. Their normalized
   contents are the arbitrary selected register a.
3. Before changing that register, prepare the eight A target rows with
   N_t u-K_A a. Use one owned copy field and one positive intrinsic line
   per A row. The target remains in its original X entrance type.
4. In physical T coordinates set c=X_T, z=u_T and d=u_offT. Define
   D=K_U R_T and B=R_T^-1 R_offT, so BD=12I. Apply these four
   scalar steps in the displayed order:

       Y_U += D X_T;
       SWAP(X_T,Y_T);
       X_T -= 12 Y_T;
       Y_T -= B Y_offT.

   The last read uses the updated off-T source. The result is

       X_T=z-12c,
       Y_U=u_U+D c,  Y_A=u_A,  Y_T=-B d-11c.

   Thus Y=Hv and X_T=P b+(JHv)_T in the normalized coordinates.
   These steps combine the full-query exchange, H, and the selected
   target correction. Each step is invertible on arbitrary inputs.
5. Undo the selected alignment and apply the eight positive intrinsic
   input lines to X_T.
6. Run the retained clean-J backward core.

For the A rows, (2) gives (JHv)_A=u_A-K_Aa. Since y_A=u_A-(N_tu)_A,
the preparation in step3 is exactly (JHv)_A-y_A. Outside S, (JHv)_U
equals y_U, so no target copy is needed. The selected pre-core source
has normalized current query c. Its J image on T is -Bd-12c. Hence
the core leaves X_T=z+Bd=R_T^-1 b. This proves the scalar purpose
of every preparation row.

The component native count is therefore a candidate of eight inverse
X_T lines, eight positive X_T lines, and eight positive A copies. This
is 24 rank-one children if all stated current and future alignments
and the retained core entry types are bound literally. The input and
output maps, scalar bounds, C0 lifetimes, recursive child owners and
whole-cover sweep order still need the independent native check.
The owned private copy may be cleared. None of the eight X_T register
inputs may be cleared.

## Ordered extension with a matrix centre response

The number 12 is not needed for invertibility. Suppose instead that
K=K_A+P+K_U, RP=I, and each injection has the stated output support.
Let M=R K_U be any matrix over the ordered coefficient ring. Put

    Z=K_U-P M,     H=I+ZR.

Then RZ=0 and

    H^-1=I-ZR,    RH=R,
    JH=I-[K_A+P(I+M)]R.

Use the same future map E and exchange (3). Equations (5), (7) and
(8) still hold. The selected source row in (6) becomes

    y'_T=u_T-P b+P(I-M)a.

In the four-step scalar word replace 12 by R_T^-1 M R_T. Indeed,
BD=R_T^-1 M R_T, so the same cancellation proves the output map.
There is no inverse of M and no commutation of its factors. This is
an ordered local theorem. It does not supply native access to a new
matrix M or remove a later controller restoration obligation.

## A variant that preserves both selected pair sums

Keep the same source output y'=Hv. Define the arbitrary original
selected pair sums p_A=x_A+y_A and p_T=x_T+y_T. Replace only the
selected target outputs in (5) by

    x'_A=p_A-y'_A,       x'_T=p_T-y'_T.

The U target output is still x_U-y_U. Both selected pair sums are
unchanged. The exact selected query in the T target is now

    Lx'=b+M a,                                             (11)

with M=12I in the actual instance. It is not the clean query b alone.
The source identities ell_(t,A)y'=R_t y and R_s y'=a are unchanged.

The inverse first sets a=R_s y' and b=Lx'-M a. It then uses (8) to
recover v,u and y. Restore x_U=x'_U+y_U, x_T=P a, and
x_A=x'_A+y'_A-y_A. This proves invertibility on all original inputs.

The short scalar source word remains valid after two changes. The A
input target copy is original y_A-K_A a, so make that copy before E_t
changes y_A. Omit the step X_T-=12Y_T. The selected pre-core target
is then u_T, and the core gives x'_T=P(b+12a). Thus the candidate
native count remains 24, subject to the same actual alignment checks.

The conserved sums are logical equations. Their two terms have
different physical endpoint types. A controller must supply legal
access before it uses either sum. The variant does not prove that a
final selected sum can be read by an ordinary scalar ADD.

## A forward map with the same conserved inputs

For this companion use R K_A=R K_T=I, as in the actual two minors.
Write the current X coordinates as (z,a,c), where z=x_U,
a=ell_(s,A)x and c=ell_(s,T)x. Set

    f=R_U z+a+c,
    w=z-K_U f,
    x'_U=w,       x'_A=P_(s,A)c,       x'_T=P_(s,T)f.

Set y'_U=y_U+w and y'_S=x_S+y_S-x'_S. This preserves the same
two selected pair sums on arbitrary inputs. It moves the previous
selected T value to A and puts the new current query f in T.

The source inverse reads f=ell_(s,T)x' and c=ell_(s,A)x'. It then
sets

    z=w+K_U f,
    a=(I-M)f-R_U w-c.

Restore y_U=y'_U-w and y_S=x'_S+y'_S-x_S. These formulas prove
both inverse orders without a centre inverse. In the actual instance
M=12I, so the second source equation is a=-11f-R_U w-c.

There is an in-place scalar source word at the common completed X
frame. In normalized selected coordinates it is

    c += R_U z+a;
    z -= K_U c;
    a = -a-R_U z+(I-M)c.

The final values are (w,old c,f). The last assignment has diagonal
coefficient -I on a, so it is an invertible scalar update. Raw forward
J transfer already gives the required U and T target outputs. On A
its target differs by P_(s,A)(f-old c), which can be formed from the
two completed selected X outputs. Eight one-way target copies are
the proposed native correction. Their inverse-line phases and the
complete source scalar invoice need the literal native check.

These two local maps give an invertible pair with conserved selected
data. They do not yet give a nine-stage controller. Intervening bank
bridges, chart changes, and the final source and target frames remain
part of that proof.

## Comparison with the earlier forty-row exchange

The preceding five-minor normalizer was H_40=I-K_U R/8 and preserved
all forty selected source fields. Replacing u_T by the old X_T value
while logging b=Ru gave an H_40 query b+a-Lu. That was a new hidden
baseline debt. A full-query exchange instead made that query a, but
retained the forty-row target support. The transvection (1) keeps the
full-query exchange and relaxes the selected T baseline requirement.
It reduces the target support to A union T.

This comparison is about the displayed local interfaces. It does not
prove a global reduction in native work. The complete controller must
route or recover the old selected input in (8), account for intervening
bank writes, and match the final physical source and target frames.

The parent supplied the 16-row transvection. The controller lane
identified the full-query exchange variant. This lane derived the
ordered pair map, inverse and target preparation. The residual-syndrome
lane reduced the scalar source word to four steps. The coherent-port
and residual-syndrome lanes are checking native access and costs.
Research used substantial OpenAI Codex assistance under the user's
direction. New material uses Apache-2.0.
