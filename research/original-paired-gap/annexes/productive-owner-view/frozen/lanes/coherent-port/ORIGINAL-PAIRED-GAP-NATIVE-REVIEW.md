# Original complex paired phase graphs

This review checks a local construction in the original complex native
frames. It does not use the Walsh change of frame. Two copies of the
reviewed full-mode core have identical port labels and native axes.
Their ordinary helper inputs and their sixteen mode inputs are arbitrary.
Their active data and mode roles must be separate during the paired call.
An ordinary helper owner may be reused only through complete restored
jobs, with the correct consecutive native frames and no intervening
scalar use. Admission of such reuse is part of the owner schedule; the
local wrapper check does not supply it.

The reviewed payload is
`../residual-syndrome/physical-algebra/ORIGINAL-PAIRED-GAP-PROGRAMS.json.gz`,
with decompressed SHA256
`42aeb0902d8b2330f9050718c6d949993111a9fd898acad599ec867bb63a2b20`.
It retains two copies of the full-mode payload
`f271842a741584389e166e700e262f161b0dd570ce8c7a540f2717e90ead5205`.
This review uses the prior exact core contract. It does not repeat the
complete native-event or 1408-column replay of that producer.

## The fixed pair at every tensor size

At port p let Q_p be the tensor power of the inherited C_p. Put

```text
L_p = Q_p^2,
A_p = [[0,I],[L_p,0]],
T_p = Q_p A_p = [[0,Q_p],[Q_p^-1,0]].
```

The exact inherited line identity is C_p squared equals the translation
X_p, with no scalar phase. Thus L_p translates every tensor coordinate by
p. It is an involution. It follows that T_p squared is I. This uses two
replicas for every tensor size. It is not a tensor power of a two-replica
map. All powers of the common full transform commute with these line
transforms and translations.

Extend R and K by the identity on the replica index, and set K=R^T/4.
A acts on the port fields. No action of A on eight mode fields is defined
or used. In particular, this proof does not exchange R A with A R or
A K with K A.

## The four physical boundary graphs

The input frames of (x,y,u) are (Q,I,I). Their output frames are
(F,F Q^-1,F). A physical ADD between different frame types is interpreted
in this order; it is not treated as a scalar ADD on logical contents.

For the forward word, use the following physical graphs in order:

```text
u -= R A X;          run both full-mode cores;
u += R X;            Y += A K u.
```

The first graph gives u=z-R T x. The raw core gives

```text
x'=x,  y1=y+(I-KR)x-Ku,  u1=-u-2Rx.
```

The last two graphs therefore give

```text
v=-z-Gx,  y'=y+x+Hv,  x'=x,
G=R(I-T),  H=(I+T)K.
```

For the backward word, use these physical graphs in order:

```text
X -= 8 Q^2 A K u;    u -= R Y/8;
run both full-mode cores;
u += R Q^2 A Y/8.
```

The first graph reads the old mode z, before the second graph changes it.
Their logical effects are x-=8 T K z and u=z-Ry/8. The raw backward map is

```text
x1=x-(I+KR)y-8Ku,  y1=y,  u1=-u-Ry/4.
```

The output graph uses Q squared A Q inverse equals T. The result is

```text
x'=x-y-8Hz,  y'=y,  v=-z-Gy/8.
```

These substitutions use only T squared equals I for the later feedback
statement. The local endpoint derivation does not need a scalar formula
for RK. It is valid when source, target and mode values are correlated.

The literal graph expansions are as follows. Each R and K acts after the
displayed translation on a port, in the indicated replica.

| Graph | Replica 0 | Replica 1 |
| --- | --- | --- |
| F input mode | u0 -= R X1 | u1 -= R L X0 |
| F output mode | u0 += R X0 | u1 += R X1 |
| F output target | Y0 += K u1 | Y1 += L K u0 |
| B input target | X0 -= 8 L K u1 | X1 -= 8 K u0 |
| B input mode | u0 -= R Y0/8 | u1 -= R Y1/8 |
| B output mode | u0 += R L Y1/8 | u1 += R Y0/8 |

Translate each relevant source or target array, perform its ADD group,
then translate that same array again. Thus each orientation has 448
literal translation maps and 2688 added scalar ADDs. It has no added
native child. The scalar subtotals are 433924 for the forward pair and
442884 for the backward pair. They exclude execution of the translation
maps, the retained native wrappers, and a global owner schedule. Each
pair retains native rank 11044 and restores 944 ordinary helper inputs,
subject to the pinned core contract.

## Exact port routes and phases

Use full-cover fields. At owner d, Q_p is C_(d p) tensored the required
number of times. An actual port route has the form

```text
M_(g,a) f(d,z) = f(dg,z+d a),   g p=p.
```

The owner-dependent translation by d p commutes with this route: the
source translation is d g p=d p, and address translations commute.
Since C_(d p) is a fixed linear combination of I and that translation,
the same statement holds for Q_p, at every tensor size, with no extra
phase. It follows for A and T. This argument includes the exact inherited
entry and exit translations a. It does not replace the cover route by
an address permutation at one fixed owner.

The checker reconstructs all 1008 actual routes from the pinned retained
geometry and binds their labels and translations to the original complex
DATA-PHASES ledger. It checks each route's inverse and fixed port line.
It also checks the inherited positive line kernel on all 57344 spatial
columns, then checks its square, fourth power, and inverse. A global-phase
change and omission of the required L factor are rejected.

For the routed maps

```text
G_s=R D_s(I-T),   H_t=(I+T)D_t^-1 K,
```

G_s H_t is zero for every pair of stages. The cancellation occurs before
R or K and does not require equal routed centre images. Any ordinary
bank operation which is identical in both replicas and commutes with T
can be inserted between these maps. The actual per-port scalar bank
shears have this property. A gate that mixes distinct ports needs its
own check and is not covered by this statement.

## Verification boundary

The independent checker imports no producer code. It checks the literal
boundary event order, coefficients and frame records, a free ordered
operator calculation for both endpoint maps, the exact line kernels,
the route covariance, and the stated component counts. It uses the
existing full-mode core as a pinned dependency.

The earlier complementary-gap proof used a Walsh retarget and a scalar
replica normalization. The earlier original-complex phase-gap word had
the residual R(I-Q squared)K. This construction replaces that residual
with zero by a port-dependent monomial replica normalization in the
original frames. It does not prove that a final odd H or G read is free.
In particular, the old mode transport identities of the form Q H equals
H A inverse and G Q equals minus A inverse G used a common mode action A.
They do not follow for the present port-dependent A and are not used.

To insert the graphs around an unchanged global core, let E be its
monomial input view from global fields to local input fields, and let O
be its output view from local output fields to global fields. The added
graphs are E inverse P E before that core and O S O inverse after it.
This keeps the original core views unchanged. It adds explicit view
maps, which require a separate count. It also requires the stated mode
views at their actual physical locations. The local (I,F) mode contract
alone does not supply a persistent nine-call mode path.

The physical paired-owner schedule, promoted-role replacement, arbitrary
mode closure, recursive admission, precision, and complete supplier
invoice remain separate. No kappa improvement is claimed here.

Research and verification: OpenAI Codex under the user's direction, with
substantial AI assistance. No independent human review is claimed.
