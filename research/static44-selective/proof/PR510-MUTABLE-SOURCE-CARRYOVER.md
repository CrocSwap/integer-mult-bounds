# PR510 as a conditional bit dependency: mutable-source carryover

## Review conclusion

PR510 at commit **`64edee18af02aab0c1696b677a0287dd0146381b`** may be used as an
explicitly cited conditional bit supplier with

$$
c=\frac{396861776523137034277}{250000000000000000000000}
 =0.001587447106092548137108.
$$

Its nine-stage mutable-source realization is covered by the same role-independent
common-label/mutable-basis contract already retained by PR493 and PR531. The
lemma below supplies the short carryover argument that PR510's README lists
as a review point. It does **not** discharge the inherited all-size compiler,
target-label, whole-call correlated-helper hosting, compressed-window, restored-work,
common-grid/tape, precision, row, or analytic contracts. A claim that the bit
supplier is unconditional would be unsupported.

The pinned PR510 README and source were reviewed, together with PR472's
“Shared physical labels and residual routes” proof and PR443's replication
proof. No long bit replay was run for this review.

## Role-independent local realization lemma

Work over an admitted odd **address** field. Stream **values** are in
$\mathbf F_2$; these two fields are distinct. For an orthogonal projector
$P$, the bit address permutation is

$$
D_P=\begin{pmatrix}I-P&P\\P&I-P\end{pmatrix},\qquad D_P^2=I.
$$

Let $\Lambda_D f=f\circ D$ denote pullback by an address bijection. Then,
for arbitrary streams $f,g$,

$$
\Lambda_D(f\mathbin\oplus g)=\Lambda_Df\mathbin\oplus\Lambda_Dg.
$$

Consequently, if both operands carry the same current address label, an XOR
into either operand commutes with that common label. This statement has no
condition on whether its destination is designated a source, helper, or target,
nor on whether the stream still equals its original input.

For nested frames $F\subseteq G$, their orthogonal projectors satisfy
$P_GP_F=P_F$. Thus $P_G-P_F$ is a projector orthogonal to $P_F$, and

$$
D_{P_G-P_F}D_{P_F}=D_{P_G}.
$$

This is the usual paid frame climb. Induction through the literal frame climbs
and common-frame XORs therefore gives the same local realization when source
registers are written. The inherited COPY/ERASE semantics for the retained
totals are unchanged.

In the compressed nine-stage construction, the local projector is extended
by the same exterior stage projector for every register in one invocation.
The exterior summand cancels from nested differences. The explicit port
isometries provide the entry and exit coordinate transports; their conjugacy
is the elementary identity

$$
(\rho\oplus\rho)D_P(\rho^{-1}\oplus\rho^{-1})=D_{\rho P\rho^{-1}}.
$$

After these specified transports, each common-frame gate uses one common local
chart. Different port transports are not silently identified. The geometry's
endpoint identities, including $D_I D_P=D_{I-P}$, also give the reflected
invocation. Neither induction depends on the number of stages, the replica
number, or the names of its physical source owners.

## Application to the actual word and owners

R480 retains PR493's mutable-source structure. Its source writes are the
577 block-D4 XOR gates in phase A. The parent `interface.py` checks that no
target feeds a source/helper, the dirt compensation is target-from-helper at
frame zero, phase B writes only targets, and the full-frame cleanup is the
literal reverse of every source/helper operation. Writing $z=(x,h)$, the
raw map consequently has the triangular form

$$
z'=Uz,\qquad y'=y+Jx+Kh.
$$

The checked compensation and scalar columns establish the intended target
map; literal $U^{-1}$ restores every source and helper. The preceding
pullback lemma realizes this argument at the recorded frames even while a
source is temporarily changed below the full frame. F2 column replay verifies
the scalar identity; the pullback identities supply the separate address
argument. One is not being substituted for the other.

The nine-stage `global_k.py` reads both operands' actual frame IDs uniformly,
replays all local and global data/helper columns, and maps the data registers
by the explicit replica/pair/side/port formula. It makes no read-only-source
assumption in that replay. Repetition over the 32 replicas is a direct sum of
the same nine-stage identity. A restored local source may subsequently be a
bridge operand just as in the eleven-stage construction.

Finally, PR510's `emit_k.py` changes only whole residual owners. Apply the
retained PR442 hosting contract to the **complete arbitrary-dirt local call**;
do not infer a free gate-by-gate identification of different physical families.
The hosting windows exclude every local or bridge touch of their host data
pair. A mutable source in the active pair therefore cannot also be one of that
call's idle hosts. This is the same owner/window obligation as before.

## Provenance and limited review scope

- [PR510 README, pinned](https://github.com/DreamingOfClouds/integer-mult-bounds/blob/64edee18af02aab0c1696b677a0287dd0146381b/research/e8-r480-nine-stage/README.md): exact bit endpoint, stage count, declared interfaces and review point.
- [PR493 README as vendored at that pin](https://github.com/DreamingOfClouds/integer-mult-bounds/blob/64edee18af02aab0c1696b677a0287dd0146381b/research/e8-bit-carrier-skeleton/README.md), and its `code/bit/independent/interface.py`: mutable-source word and structural guards.
- [PR472 proof, pinned](https://github.com/chafreaky/integer-mult-bounds/blob/259c68488b7aa8a14cf3fcae7fc499381c9bf729/research/e8-r715-whole-hosted/PROOF.md): role-independent common-label pullback and whole-call hosting scope.
- [PR443 proof, pinned](https://github.com/chafreaky/integer-mult-bounds/blob/5a514e94f156edcc5fd827b87494d962f79d0f6c/research/e8-r740-replica32/PROOF.md): direct-sum replica construction and conditional realization scope.

The source review also covered PR510's vendored `global_k.py`, `emit_k.py`,
and the parent `code/nine/geometry.py`. This review does not re-certify the
published bit price or all hosting assignments; those remain pinned dependency
evidence to be bound by the combined package.

Credit: DreamingOfClouds and disclosed Claude assistance for PR510 and its
nine-stage integration; eumemic for PR493; the attributed PR503 R480 change;
Zhihao Chen for PR425's mutable-basis lemma and PR386 geometry; chafreaky for
PR443/444/472 and their disclosed assistance; DaysSky for PR442 hosting.
This carryover exposition was prepared for icekylinx with GPT-6 Astra assistance.
