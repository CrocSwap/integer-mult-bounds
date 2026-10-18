# The selected global supplier in doubled Walsh frames

The unchanged selected scalar word has an exact global doubled Walsh
realization. Its native rank profile is the doubled selected profile.
Its port phase is an involution. The old complex-frame stage, idle,
terminal-port, and cover translations are all replaced by identity.
They cannot be copied into this realization.

The result applies to every positive tensor size and every input array.
It uses the reviewed local native contract, including phases, arbitrary
helper inputs, and private cleanup. It keeps the selected invocation
order, physical families, helper jobs, and idle remainders. No paired
replica schedule or new owner patch is needed.

This note proves the global operator binding for that local contract.
It does not prove a changed centre-free controller, claim a new kappa
value, or claim that the old admission executable accepts a new network.
The finite invoice and analytic recurrence are separate obligations.
The [finite invoice proof](PROOF.md) gives these calculations.

## Inputs and emitted binding

The repository source is commit
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
The selected replay archive has SHA-256

    f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6.

The checker reads these members directly:

* `candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz`;
* `candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json`;
* `candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz`;
* `candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz`.

Their exact hashes are in `evidence/GLOBAL-CHECKS.json`. The canonical word
and both scalar streams match the local review's source hashes. The two
consumed reviews are `evidence/WALSH-RETARGET-REVIEW.json` and
`evidence/DOUBLED-WALSH-REVIEW.json`. Their exact hashes and the native
payload hashes they bind are recorded in `evidence/GLOBAL-CHECKS.json`.
The checker also reads the three native payload files and checks their
complete decompressed contents against these review hashes.

`evidence/DATA-PHASES.json.gz` gives all 112 doubled port charts, all 1,008
stage route matrices, all idle-axis recipes, and all new phase values.
`evidence/GLOBAL-BINDING.json.gz` gives the 482-event schedule, all 69,120
helper jobs, their 17,819 distinct chart recipes, all 7,526 idle suffixes,
and the full boundary adapters. Each job binds a selected source index.
The source scalar streams are referenced by their exact hash. The local
native factors are the explicit doubled payload bound by the native
review. All generated compressed artifacts are bound by their complete
decompressed UTF-8 payloads, so gzip metadata is not mathematical data.
Thus this is a compressed operator binding, not a flattened global tape.

## Exact normalized frames

Use interleaved coordinates `(old_axis,copy)`, with copy zero or one.
For an old rank-r subspace U, write

    Gamma_U = i^(-r) (H_U tensor H_U).

At tensor size mu, take the mu-th tensor power of this complete operator.
For a coordinate U, Gamma_U is the real normalized Walsh transform on
2r axes. In particular,

    Gamma_U^2=I.

The global charts used below are orthogonal. For their subspaces this
definition is intrinsic: a change of orthonormal basis gives the same
operator, including its scalar phase. On two disjoint orthogonal axis
sets A and B,

    Gamma_A Gamma_B = Gamma_(A+B).

For an old orthogonal matrix g, let g2 be its diagonal double. Then

    P_g2 Gamma_U P_g2^-1 = Gamma_(gU).

The full-width statement follows directly from the exact kernel

    Gamma_full(x,y) = 2^-73 (-1)^(x dot y).

Orthogonality preserves the exponent. The normalization is positive and
unchanged. There is no unverified global sign or translation. The same
argument on the active axes proves covariance for a partial frame.
All these are operator identities on the complete array space. The
inputs need not be pure tensors or copies of other arrays.

For an odd source label q, put Q_q=Gamma_span(q). It is a two-axis
operator in the doubled space, and Q_q squared is I. It is not the
one-axis operator for the even vector `(q,q)`.

## Actual port charts and data routes

The checker reconstructs the selected orthonormal port chart

    B_q=(q,b_1,...,b_8,e_9,...,e_72).

It uses the first zero bit z of q, the even vector a=q+e_z, the
transvection x to x+a(a dot x), and the coordinate order that exchanges
zero and z. It checks the full 73 by 73 Gram matrix. The same chart is
used in the pinned idle-axis and owner-route records.

Let E_s be the eight standard axes with indices 8s+1 through 8s+8 for
1<=s<=8. Let W_-1=0 and

    W_s=span(b_1,...,b_8)+E_1+...+E_s  for 0<=s<=8.

At stage zero, rho is I. At a positive stage s, rho exchanges b_j with
the j-th axis of E_s, fixes q, and fixes all remaining orthogonal axes.
The emitted full doubled matrix is orthogonal and is its own inverse.
The checker verifies on exact vectors that

    rho(W_(s-1))=E_1+...+E_s,
    rho(W_s)=span(b_1,...,b_8)+E_1+...+E_s.

A complete local sweep at cover class d uses the data owner at
g=d rho. At physical cover class g, the data frames before stage s are

    X: Gamma_(W_(s-1)) Q_q,    Y: Gamma_(W_(s-1)).

In the invocation chart d, these become the common exterior frame on
E_1+...+E_s times the local frames `(Q_q,I)`. This exterior frame acts
outside the local eighteen axes. It commutes with every local operation.
The reviewed retargeted primitive has, in both orientations, local
entrances `(Q_q,I)` and exits `(Gamma_full18,Gamma_hole16)`. Its logical
map is respectively `(x,y+x)` or `(x-y,y)`.

The exterior frame and the route identities above therefore give the
exact global exits

    X: Gamma_(W_s) Q_q,    Y: Gamma_(W_s).

No entry or exit translation is needed. This uses the deliberately
retargeted backward stream on the same canonical frame IDs as forward.
It does not reuse a theoretical upstream backward coframe without its
new endpoint adapters.

For each fixed port, right multiplication by rho permutes the cover.
Thus the complete sweep performs this map once on every physical cover
class. The complete local map pairs X and Y at the same port and class.
Its intermediate use of other ports does not impose an input relation.

## Whole helper jobs and idle completion

Keep each selected complete helper job. Its old pending width w becomes
2w, its offset becomes twice its old offset, and its spectator indices
are doubled. All old intervals remain disjoint. No helper is split
between two owners or duplicated within an invocation.

The route direction is explicit. Suppose the old orthogonal chart sigma
has columns B_q in the order

    occupied axes, spectator axes, all remaining axes.

Use its doubled matrix sigma2. A local invocation at d uses owner class

    g=d sigma2^-1,  equivalently d=g sigma2.

The emitted chart recipe gives sigma2 by its columns and sigma2 inverse
by the same list used as rows. Hence the local complete Gamma_[2w] job
has physical action

    P_d Gamma_[2w] P_d^-1
      =P_g P_sigma2 Gamma_[2w] P_sigma2^-1 P_g^-1.

This is exactly Gamma on the pending owner axes. The pinned chart audit
already checks these columns as the required pending and spectator
axes. The inverse in the cover index is essential; most charts are not
involutions. The new binding does not rely on an ambiguous route name.
The diagonal cover contains both sigma2 and its inverse.

The full local helper contract gives this complete Gamma job on every
arbitrary helper input. The local data outputs do not depend on that
input. Helpers remain in Gamma coordinates in the global ledger. They
are not changed back to an F job between ledger steps. Literal F children
occur inside their reviewed native lowering, with all Gamma adapters.

The checker executes the actual asynchronous schedule on one frame mask
for each of the 14,336 physical productive families. At each helper job
it adds exactly that job's pending axes. It checks that these axes are
new. At each idle deadline it adds the exact selected suffix and checks
the complete required frame. It also checks each helper's strict
bridge-aware owner window, exact family, width, and route, and all 704
owner identities in every complete invocation.

Thus all 69,120 helper jobs and all 7,526 idle remainders are accounted
for, including partial prefixes hosted before their idle deadlines.
The phase after every idle completion is identity. The proof does not
replace a partially completed owner by a zero or copied input.

## Bridges, virtual inputs, and the terminal exchange

Initially X has virtual frame Q_q and Y has virtual frame I. These are
coordinate descriptions, not paid preparation gates. If the raw inputs
are a and b, their initial logical contents are Q_q a and b.

Every bridge is the literal pair of scalar operations

    X_dst += c X_src,
    Y_src -= c Y_dst.

The second operation has the opposite sign and direction. The checker
checks all 32,256 affected frame pairs: their exact axis masks agree at
the bridge time, after all actual partial helper advances. It then
replays the complete eight-bank integer scalar matrix for each replica.

Before the terminal exchange, all X frames are Gamma_full146 and all Y
frames are Gamma_full146 Q_q. The original scalar controller, followed
by the terminal map `(X,Y)=(old_Y,-old_X)`, is exactly I on the eight
logical inputs. The checker obtains all eight columns, with no modular
or floating-point test.

The terminal exchange also exchanges the physical frame types. The
final X frame is Gamma_full146 Q_q^-1 and the final Y frame is
Gamma_full146. Their raw operations are therefore

    X: (Gamma_full146 Q_q^-1) Q_q^-1 = Gamma_full146 Q_q^-2,
    Y: Gamma_full146 I = Gamma_full146.

Since Q_q squared is I, the X operation is also Gamma_full146.
This is where the old terminal translation
must be removed. The checker verifies the final and initial mask
difference on every productive family, not only a sampled port.

The final Gamma_full146 commutes exactly with every diagonal orthogonal
cover chart. Thus the old cover correction must also be removed. As
controls, the first actual port q=11 and its chart give a nonzero old
terminal translation and a nonzero old cover correction delta=15.
Either retained translation changes the sign of a Walsh kernel entry
whose input is the first coordinate basis vector. These are concrete
operator errors in the new convention.

All selected scalar operations and every source event retain their
order. The old translation event positions become identity checkpoints.
There is no new productive bank. The original private core workspace
is reused between complete invocations under the reviewed cleanup
contract.

## Literal F boundary and complete recursive rank

Let S_146(x)=i^wt(x). At tensor size mu,

    Gamma_full146=i^(-73mu) S_146 F_(146mu) S_146,

where each S factor means its mu-th tensor power. On every productive
array, apply S_146 inverse before the complete network and
`i^(73mu) S_146^-1` after it. The resulting raw operator is exactly the
required F_(146mu). These two monomial maps contain no recursive child.
Their finite execution costs must be paid. They act in raw standard
coordinates after the cover-independent full endpoint is proved.

The complete paid child profile is

    {2:349604, 4:60192, 6:62585, 8:20448,
     10:11808, 14:7, 16:1152, 96:4866}.

Its rank mass is 2,082,816. The productive rank is
`146*14336=2093056`, so the deficit is 10,240. This is exactly twice the
selected rank and deficit; all ratios r/m and the productive family
count are unchanged. The largest child is 96, and
`146^2-2*96^2=2884>0`.

These counts are for the unchanged selected scalar word, including all
its centre children. They do not price a new centre encoder. The local
retarget maps, complete Gamma helper normalizers, and final F boundary
maps have finite scalar and address cost. The complete package invoice
must cover them. This proof does not call rank-zero work free.

## Executed checks and remaining work

After the native generation and reviews, run from the repository root:

```sh
python3 -I -B research/involutive-walsh-lift/global_walsh.py
```

The expected status is `PASS_SELECTED_GLOBAL_DOUBLED_WALSH_BINDING`.
The check uses exact binary and integer arithmetic. It covers every
selected call, owner job, idle suffix, bridge, and productive endpoint.
It includes operator controls for stale C translations, an incorrect
bridge sign, and an incorrect helper route direction. These controls
protect phase and access errors that a rank-profile comparison misses.

The portable generator and separate-agent `review_global.py` both
passed. The review status is
`PASS_INDEPENDENT_SELECTED_GLOBAL_WALSH_HISTORY`, recorded in
`evidence/GLOBAL-WALSH-REVIEW.json`. It imports no producer checker.
It reconstructs the history with explicit axis
sets and checks all emitted charts, helper records, suffixes, events,
checkpoints, and boundary maps. It also checks 10,002 distinct helper
maps and their inverses. A control that omits one complete helper job
fails at an exact bridge-frame check. The local operators and their
full phases also have separate-agent review. The complete package
receipt records the executed portable checks.

No full 146-dimensional matrix is expanded: exact kernel identities,
the complete local contract, and the finite global ledger prove the
operator statement. No new all-size execution engine or analytic
admission is run here. The literal doubled local native payload is a separate checked
artifact used by this binding; the global scalar streams remain in
their selected compressed form.

The construction uses the selected authors' finite cover, controller,
scalar word, ownership, and native compiler work. The local Walsh
retarget and doubling are from the residual-syndrome, interface-proof,
and cover-algebra lanes. The temporal-reuse lane supplied the independent
bridge-sign and virtual-endpoint check that guided this global audit.
New research and verification used OpenAI Codex under the user's
direction, with substantial AI assistance. No human review is claimed.
New material: Apache-2.0.
