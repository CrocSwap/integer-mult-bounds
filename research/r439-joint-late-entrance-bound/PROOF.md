# A joint obstruction for late-compensated helper entrances

All scalar spaces below are over F2; frame subspaces are over Q. This is a
source-bound finite argument for the PR589 word, not a formal proof-assistant
verification or an integer-multiplication theorem.

## 1. Boundary and domain

Write the independent input coordinates as `(x,y,h)`, with 111 sources, 111
targets and 439 helpers. The selected raw `A; scatter; B; C` restores sources
and helpers and sends targets to `y+x+Kh`. The checker rederives this operator
on all 661 columns and checks that the selected frame-zero D implements K.

Let P be a set of k independent helper inputs initially at nonzero rational
frames E_i. Consider the following replacement interface:

1. Before A, a frame-zero prefix D' may change non-elevated helpers and targets.
   It does not touch the elevated inputs or sources. Then an invertible,
   helper-only change of basis G is performed with monotone frames. No other
   source/target routing or COPY is added before the scatter.
2. A and its gate frames are fixed. Every helper carrying elevated input i
   must be able to reach its original first A-contact frame F_h. Thus the
   helper column c_i of that input has E_i contained in every F_h in its
   support. These are the **common-first-contact support columns** below.
3. The nine retained COPY snapshots and their centres/ranks are fixed. Targets
   remain at frame zero before the scatter; scatter rows may gain snapshot
   terms. The actual frame at the post-scatter cut is the raw frame: every
   helper is touched in A, and the permitted prefix reaches its first contact.
4. After that cut, allow arbitrary finite invertible F2 common-frame operations,
   with monotone frames and any fresh independently initialized registers that
   are restored. There is no new COPY, frame descent or reset. B and C may be
   replaced. Every original register must reach its required final frame and
   the endpoint must be `(x,y,h) -> (x,y+x,h)` on arbitrary dirty inputs.

These premises extend PR1932's single-elevated-input setting to a joint batch.
They exclude source-donor entrances, changed A, pre-scatter target routing,
additional correlated copies, different first contacts, and an altered endpoint.
They do not restrict the length of the post-scatter program or storage relays.

Let Gamma denote the linear map before A. Its columns on the original x inputs
are unchanged identity columns. Its columns on the elevated inputs have zero
source/target parts and helper parts C=[c_1 ... c_k]: D' cannot access those
inputs, and G acts only on helpers. G is invertible, so rank(C)=k.

## 2. Joint necessary condition

Fix target t with final frame U_t. Let sigma_r be the raw post-scatter value of
register r. Define S_t as the span of:

- sigma_r for r other than the target whose raw frame at the cut lies in U_t;
- all nine raw COPY snapshots.

Let W_t be the helper parts of the source-free vectors in S_t, ignoring their y
parts. Discarding y is a favorable relaxation. The checker derives W_t directly
from the pinned word using exact rational frame containment and binary
elimination; it does not import PR1932's implementation or recorded spaces.

The joint condition is

    K_t C belongs to { u C : u in W_t }.                         (J)

In particular, passing each column separately does not imply (J): the same u
must produce the entire response vector.

Proof. The monotone-span argument from PR1128/PR1932 applies with any number of
elevated inputs. Operations inside U_t only mix values already in U_t;
operations outside U_t remove their operands from this set permanently. Fresh
independent coordinates cannot remain in the required endpoint. Including all
snapshots favors admissibility even if some are not physically available later.

Consequently there is a vector v in the span of the raw cut values in U_t and
the snapshots such that `v Gamma = y_t+x_t`. Extra allowed scatter terms are
already included in this span. Since Gamma leaves the original source columns
unchanged, the x part of v is x_t. Since its elevated-input columns are C in
the helper rows and zero elsewhere, the helper part of v satisfies `v_h C=0`.

The legal raw suffix gives `b=y_t+x_t+K_t h` in the same raw span. Thus v+b has
zero x part and helper projection satisfying `(v+b)_h C=K_t C`. If this
combination uses the target's own cut value, replace that value by the sum of
its scatter snapshots. They differ only by y_t, because A does not touch
any target (checked). This leaves the source and helper parts unchanged and
puts the combination in S_t. Its helper part u is in W_t and satisfies (J).

This proof needs no assumption that the later compensation is target-only or
that relays are read-only. It does require the complete boundary above.

## 3. Finite domain and the eight witnesses

The geometric completeness dependency is the pinned PR1253
`r439-kernel-entrance-closure/PROOF.md` and its certificate. First-contact
spaces are lines or planes. Their complete nonzero intersection closure has
366 classes V, each with eligible set `I(V)={h: V <= F_h}`. Every common-frame
support is a nonempty subset of some I(V), including entrances at arbitrary
rational sublines. The union has 4,954 distinct supports.

This package consumes that closure, rechecks every class's complete eligible
set against the raw word, and enumerates every support. It does not rerun
PR1253's separate plane-intersection completeness engines. That established
geometry proof remains an explicit dependency.

Applying the one-column projection of (J) to all 4,954 supports leaves exactly

    c1 = e444 + e470,
    c2 = e444 + e470 + e578.

This independently recovers PR1932's two individual survivors on PR589. Their
joint response and accessible image, at each target below, are

    K_t [c1 c2] = (0,1),
    {u [c1 c2] : u in W_t} = span{(1,1)}.

| Physical target | Basis of W_t, as helper coordinates |
|---:|---|
| 113 | 436, 470 |
| 118 | 227, 415, 470 |
| 150 | 451, 470 |
| 153 | 398, 470 |
| 192 | 245, 394, 470 |
| 197 | 394, 470 |
| 214 | 277, 470 |
| 219 | 227, 470 |

The dual vector `(1,1)` annihilates the accessible image but pairs to 1 with
the required response. Equivalently, `c1+c2=e578`, while every listed W_t has
zero coordinate 578 and `K_t[578]=1`. CERTIFICATE.json includes all eight
witnesses and explicit XORs of raw register/snapshot values producing every
listed dirt basis vector. One witness suffices to reject the pair.

## 4. Rank conclusion and cost limit

Any admitted joint set must pass every one-column projection of (J), so each
nonzero column is c1 or c2. If rank(C)>=2, both occur; projecting onto those
two columns contradicts any of the eight witnesses. Hence **rank(C)<=1**.
Repeating the same column does not evade the result: repeated columns have
rank one and cannot represent independent elevated inputs of invertible G.
The checker tests this distinction, all six invertible changes of the two-column
basis, and an exhaustive four-element image oracle at all 111 targets.

The ceiling is attained as a necessary-condition rank: c1 passes, as does c2
alone. PR1179 already constructs c1's finite kernel entrance. No construction
of c2, or proof that c2 is impossible, is supplied here. The broad single-triple
restoration question from PR1932 is unchanged.

Both directions contain helper444, whose first-contact frame79 is a line.
Thus each surviving entrance frame has dimension at most one, and at most one
independent helper input can be elevated. Even granting free prefix synthesis
and free late compensation, this mechanism cannot eliminate two units of
initial helper-climb rank mass. A physical implementation can add further
climbs and ADDs; none is assumed free in an admitted construction.

For context only, the pinned PR1179 receipt gives its known c1 word's full
local profile as the PR589 profile minus one rank-one child: rank mass
5129 -> 5128 and ADDs 24305 -> 24252. Those are credited inherited measurements,
not rerun here. PR1179/PR1253 already explain that the unchanged width-eight
hosting pays an additional rank-one remainder, cancelling this local rank
saving. No new hosted bill, supplier admission, precision improvement, outer
assembly or kappa follows from this obstruction.
