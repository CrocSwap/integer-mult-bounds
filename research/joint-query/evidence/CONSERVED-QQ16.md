# Complete local query words with conserved selected sums

This construction uses sixteen existing data ports to carry centre
queries through a forward or backward call. The forward word puts its
full current source query in eight completed X ports. It moves the old
selected X value to another eight X ports. The backward word puts a
future source query in eight Y ports and a current query, with an
explicit selected-input term, in eight completed X ports. Both words
preserve the logical X-plus-Y sum at each of the sixteen selected ports.
Both complete maps are invertible on arbitrary data inputs.

The emitted backward word has scalar bound 214986 and native mass 5546.
It adds twenty-four rank-one children. The forward word has scalar bound
211210 and native mass 5530. It adds eight rank-one children. Each uses
one existing owned private field C0 and no new field. All 480 arbitrary
ordinary helper inputs are restored. The eight owned private input
values may be arbitrary; the words discard them and return zero.

These are complete local full-cover operator words. The payload gives
the exact owner maps, payload translations, intrinsic line recipes,
scalar gates, sweep barriers, and retained local core. It is not a
complete supplier. Global owner placement for the new sweeps and
children, controller closure, stream and address costs, precision, and
recursive admission remain open. No complete kappa improvement is
claimed. Independent review of this full-word payload is pending.

## Sources and field contract

The literal payload is `CONSERVED-QQ16-PROGRAMS.json.gz`. Its decompressed
SHA256 is

    2efe83c59978aa9c0db2c3e4eccc14cbfdcd3c9ce499432601b5dd34083472ef.

`CONSERVED-QQ16.json` gives the complete producer receipt. The emitter
pins each consumed source. The main inputs are:

- `../CENTRE-FREE-PROGRAMS.json.gz`: the complete reviewed clean-J core;
- `../../residual-syndrome/physical-algebra/CONSERVED-QQ16-SCALARS.json.gz`:
  the two fixed scalar words;
- `../../cover-algebra/JOINT-QUERY-TRANSFER.md`: the ordered pair maps,
  inverses, and conserved-sum extension;
- `../../coherent-port/QQ16-CONSERVED-COMPONENT.json` and
  `../../coherent-port/QQ16-CONSERVED-FORWARD.json`: the intrinsic native
  recipes and component frame checks;
- `../../coherent-port/QQ16-COVER-ACTION-ADDENDUM.md` and
  `../../interface-proof/BRIDGE-REVIEW.md`: the exact cover action and
  its relation to the retained local core.

The field namespace is L0 through L703 and C0 through C7. X is L0
through L111. Y is L112 through L223. L224 through L703 are the 480
ordinary helper fields. The formal replay has all 712 input columns.
No assumption is made that an input data, helper, or private value is
zero. Only owned private fields may be cleared. C0 is returned to
zero in frame I after each target row, before it is used for the next
cover owner. C1 through C7 are not used by the new wrappers. The
retained core clears all eight private fields.

The core has 25155 events in each orientation. This includes 20089
scalar macros, 3486 recursive child events, 1090 adapters, 480 residual
adapters, and ten phase markers. The payload retains all these bytes.
Their scalar bound is 202138 and their native mass is 5522. The existing
local frame checker is rerun on the complete core in both orientations.

## Exact logical maps

Use the actual matrix R, K=R^T/4, and J=I-KR. Then RK=14I. Set

    A=[0,7,20,27,36,46,57,111],
    T=[21,37,47,76,81,87,92,110].

The two minors satisfy R_A R_A^T=R_T R_T^T=4I. Their inverses are
R_A^T/4 and R_T^T/4. Let U be the remaining 96 ports. An injection
with subscript A, T, or U is zero outside that set.

For a current chart s, let D_s be the actual port-diagonal cover
route. Use the normalized queries and injections

    R_s=R D_s,             K_s=D_s^-1 K,
    P_s=D_s^-1 iota_T R_T^-1,
    ell_s=R_T pi_T D_s.

Thus R_s P_s=ell_s P_s=I, K_(s,T)=P_s, and R_s K_(s,U)=12I.
For a future chart t>s set

    E_t=I+P_(t,A)(R_t-ell_(t,A)).

This is a unit. Its added term has only A output rows and no A input
columns, so its square is zero. Its inverse has the opposite sign.

For the backward word define

    u=E_t y,       a=ell_s x,       b=R_s u.

The exact output is

    y'_A=u_A,
    y'_U=y_U+K_(s,U)a,
    y'_T=u_T-P_s(b+11a),
    x'_U=x_U-y_U,
    x'_A=x_A+y_A-u_A,
    x'_T=P_s(b+12a).                              (1)

Consequently

    R_s y'=a,
    ell_(t,A)y'=R_t y,
    ell_s x'=b+12a,
    x'_p+y'_p=x_p+y_p for p in A union T.         (2)

The T target contains b+12a, not b alone. The future selected query
and the current full query are different operator-valued quantities.

For an explicit inverse, put Z_s=K_(s,U)-12P_s and
H_s=I+Z_sR_s. Since R_sZ_s=0, H_s^-1=I-Z_sR_s. From x',y' compute

    a=R_s y',       b=ell_s x'-12a,
    v=H_s^-1y',    u=v+P_s(b-a),    y=E_t^-1u.

Then restore x_U=x'_U+y_U, x_T=P_sa, and
x_A=x'_A+y'_A-y_A. These equations prove both inverse orders.
They do not establish that all inverse reads are free at the output
frames.

For the forward word put f=R_s x. Its output is

    x'_U=x_U-K_(s,U)f,
    x'_A=P_(s,A)ell_s x,
    x'_T=P_s f,
    y'_U=y_U+x'_U,
    y'_S=x_S+y_S-x'_S,       S=A union T.         (3)

In normalized source coordinates (z,a,c), where a=ell_(s,A)x and
c=ell_s x, this is

    (z,a,c) -> (w,c,f),
    f=R_(s,U)z+a+c,       w=z-K_(s,U)f.

Its inverse is z=w+K_(s,U)f and
a=-R_(s,U)w-11f-c. The Y inverse follows directly from (3).
This proves invertibility and conservation of all sixteen selected
pair sums. The two orientations are companions, not inverse circuits.

The proof in the pinned pair note uses ordered multiplication. It
does not require two chart routes to commute. The common-chart
712-column replay checks the emitted coefficient word. The ordered
proof extends that word to the actual full-cover routes. The two
claims are recorded separately.

## Cover action and native phases

At cover owner d, the operator C_(d q) is the inherited complex line

    C_q=(1+i)I/2+(1-i)T_q/2.

It satisfies C_q^2=T_q and C_q^-1=T_q C_q. A negative line therefore
uses the inherited positive rank-one recipe with translation q fused
into its left wrapper. A canonical binary line subspace does not
specify this phase and is not used as a replacement.

At a positive backward stage s, the physical input frames are

    X_p: F_(d U_(s-1)),
    Y_p: F_(d U_(s-1)) C_(d q_p)^-1,

where U_j=L+E_1+...+E_j. After either retained local core, the frames
are F_(d U_s) on X and F_(d U_s) C_(d q_p)^-1 on Y.

For each port and positive chart v, the pinned involution rho_v(p)
fixes q_p and swaps the eight chart vectors in q_p-perp with E_v.
Let beta_p[i]=(weight(B_p[i])-1)/2 modulo two. The Y alignment uses

    delta_Y(v,p)=q_p XOR lift_v(beta_p).

The completed-X alignment uses

    delta_X(v,p)=B_p beta_p XOR lift_v(beta_p).

The actual full-array map is

    M(g,delta) f(d,z_1,...,z_lambda)
      = f(d g,z_1 XOR d delta,...,z_lambda XOR d delta).    (4)

Here g=rho_v(p). The owner changes by right multiplication. The
payload has a separate translation on every tensor layer. Spectators
are unchanged. There is no amplitude phase in (4). The phase of the
native frame changes because its owner and its payload translation
change. The registry gives the complete 73-column owner matrix and
translation for every map used.

For operator composition,

    (g,a)(h,b)=(g h,a XOR g b),
    (g,a)^-1=(g^-1,g^-1 a).

The emitter checks both inverse orders, including the translation.
It computes the full Z4 phase polynomial after every map and native
line. Every new scalar ADD is checked against exact equal phase
polynomials, not just equal binary ranks. For a selected source q
read in target p's frame, the map is A_v(p)^-1 A_v(q).

During emission, an incorrect interpretation of rho as a payload
permutation in one fixed array was identified and rejected before
the payload was frozen. The accepted bridge proof distinguishes
the two actions. The receipt includes a direct witness: give owner I
the constant value zero and owner rho the constant value one. The
correct map reads one at owner I. A payload-only permutation still
reads zero. Independent owner inputs cannot be identified.

Stage-zero F has a separate base case. All X fields already have
the same FULL9 frame, D_0=I, and the source scalar suffix needs no
alignment. Its A output copies still need the eight inverse lines.
No stage-zero Y alignment is inferred.

## Literal sweeps and private lifetime

Every `cover_map` event is the declared bijection (4). A `cover_sweep`
must finish over the full cover before the next event. It is not a
local operation that assumes the other owners have already changed.
The `private_sweep` body is different: for each owner, execute the
whole clear, form, native child, add, and clear sequence before the
next owner. This uses one C0 array, not a full-cover C0 bank.

The backward order is:

1. Apply inverse C_p to the eight X_T fields.
2. For each p in A, move its four selected X source cohorts by the
   exact current paths. Run the private sweep that forms
   original y_p-(K_(s,A)a)_p, applies positive C_p, and adds it to X_p.
   Return C0 to zero/I, then undo all four source-cohort maps.
3. Align all Y fields to chart t. Complete the E_t source sweep and
   undo that alignment.
4. Align Y and the normalized X_T fields to chart s. Complete the U
   scatter sweep, the eight selected swaps, and the final T-query
   sweep in that order. The final query reads the changed U fields.
5. Undo the current alignment and restore X_T with positive C_p.
6. Run the complete retained backward core in its existing embedding.

The forward order is:

1. Run the complete retained forward core.
2. Align all X fields to the current completed chart, except at
   stage zero. Run all five source scalar blocks in the frozen
   order, with a completion barrier after each block. Undo alignment.
3. For each p in A, move its four selected source cohorts into the
   X_p frame. Form the correction from the changed source, apply
   inverse C_p on C0, and add it to Y_p. Clear C0 to zero/I and undo
   all source-cohort maps.

Each aligned port is a bijective view of one complete data family.
Thus, for a fixed common owner, distinct local blocks have disjoint
physical field addresses. The local scalar dependencies are exact
within this view. The barriers make later reads use the completed
earlier update. A target copy reads only unchanged selected source
cohorts and the same-port source until its private body is complete.
The temporary source maps are undone before the next copy row.

These facts define a valid full-cover operator sequence. They do not
assign the new recursive children to unused helper owners, prove that
all sweeps fit the retained controller's live intervals, or price the
address implementation. Those are separate supplier obligations.

## Complete local invoice

All scalar bounds use the retained complex-to-real primitive ledger.
The count includes all new CLEARs, ADDs, signs, and the complete core.
It excludes the separate monomial maps and recursive child costs.

| Word | Added scalar bound | Complete scalar bound | Added rank-one children | Native mass | Added map bound |
|---|---:|---:|---:|---:|---:|
| Backward, positive s<t |12848|214986|24|5546|576|
| Forward, positive s |9072|211210|8|5530|304|
| Forward, s=0 |9072|211210|8|5530|16|

The map bound counts both directions of every full-cover map and two
wrappers for each native line child. Identity maps in positive-stage
formulas are retained in the conservative count.

Backward has 21401 scalar macros: 20654 ADDs, 715 SCALEs, and 32
CLEARs. Forward has 21025 scalar macros: 20278 ADDs, 715 SCALEs, and
32 CLEARs. Each has the original 480 helper fields and eight owned
private fields. Neither adds a productive family.

The backward native profile is

    {1:2436, 2:418, 3:432, 4:142, 5:82}.

The forward native profile is

    {1:2420, 2:418, 3:432, 4:142, 5:82}.

The formal scalar triangle and Horner prefix ceilings are 73 bits
for B and 55 bits for F. These are bounds for this finite scalar
word. They are not a recursive precision theorem or a completed
finite supplier invoice.

## Verification and limits

From the workspace root run:

```sh
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/circuit-interface/qq16/emit_conserved_qq16.py
```

The expected first output is

    PASS_CONSERVED_QQ16_COMPLETE_LOCAL_WORDS

The producer checks both complete words on all 712 formal columns
at the common-chart specialization. It verifies all 480 helper
outputs, all eight private outputs, and all sixteen conserved sums.
It emits and checks 28 native backward cases with 1<=s<t<=8 and nine
forward cases with 0<=s<=8. The retained schedule uses a subset of
these cases. The payload retains their exact full-cover maps and
their scalar-phase order.

All 32 distinct used positive and inverse line recipes are compared
on every 9-axis basis column: 16384 exact Gaussian columns. All 32
scalar-phase mutations are rejected. Other controls reject a late A
input read, an early T query, an early F source update, an early F
target copy, a positive line in place of an inverse line, a missing
payload translation, and a payload-only owner route.

The ordered pair proof and the accepted bridge operator theorem are
material dependencies. The arbitrary-cover conclusion is derived
from them and the literal native frame checks. It is not inferred
from the finite common-chart replay alone. No full multiplication
or supplier verification was run for this candidate.

The parent and encoded-controller lanes supplied the conserved-sum
interface. The cover-algebra lane supplied the ordered inverse and
its extension. The residual-syndrome lane supplied the short scalar
words and their coefficient invoices. The coherent-port lane supplied
the native component bindings and the explicit cover-action correction.
The interface-proof bridge review supplies the exact retained local
embedding. This lane assembles and checks the complete local words.
The construction and its validation used substantial OpenAI Codex
assistance and separate agent work. They have not received independent
human review.
