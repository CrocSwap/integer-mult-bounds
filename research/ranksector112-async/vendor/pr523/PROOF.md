# Conditional construction argument

The exact finite result is
`kappa = 182243220215421/125000000000000000`.
This note explains how the changed finite ingredients satisfy the same
interfaces used by pinned PR514. It does not prove the inherited all-size or
analytic interfaces. Full credits are in `NOTICE.md` and `SOURCES.json`.

## Proposition 1: exact direct-sum restriction

Let P be the original normalized scalar operator after arranging its eight coordinate
source/target pairs separately from the other registers. The old Hamming
scalar word, its canonical transport and the new word are supplied explicitly.
Comparison of A, B, precondition, compensation, cut and cleanup shows that
the deleted registers have exactly eight occurrences: unit shears on their
own source/target pairs. Hence

$$
P=\left(\bigoplus_{i=1}^8 J_i\right)\oplus P_{112},
\qquad J_i(x_i,y_i)=(x_i,y_i+x_i).
$$

The old identity on all arbitrary data and helper columns implies that
P112 is the required 112-data-port shear and restores every helper in this
normalized scalar interface. Physically, a complete invocation leaves the
declared residual transform on a helper's owner and restores its spectator
coordinates, as specified in Proposition 3. The
separate exact transport and emitted-program replays verify this conclusion
directly in both orientations. They also verify the actual frame at each
operand, nested recursive steps, cleared private work, and ordered wrappers.

No retained frame, coefficient, scalar gate or helper entrance is modified.
The exact local Clifford and residual-wrapper checks therefore realize the
same conditional operator interface on the retained registers. The new local
cost is obtained by deleting precisely sixteen rank-8 and eight rank-1
children. Its rank mass is 6706 and its center-rank sum is 64.
See `proof/LOCAL-RESTRICTION.md` for indices, coefficients and source checks.

## Proposition 2: retained global data controller

The old controller's data families are indexed by replica, one of four pairs,
side, and port. Keep precisely the 112 canonical ports selected in Proposition
1, and reindex each data-family component by the same order-preserving map.
Each full local invocation is replaced by P112 in the appropriate orientation.
Every data chart, bridge, idle axis, stage translation and terminal correction
for a retained port is exactly the corresponding old object.

The local source/target basis operations may mix the code ports inside a
complete invocation. Proposition 1 is why that fact is harmless: no removed
coordinate register participates, and the complete endpoint is the required
portwise data shear. The outer controller is restricted only at complete
invocation boundaries. The proof does not assume that every individual
factory instruction is portwise independent.

The independent restriction audit compares all retained recipe objects,
reconstructs every actual 73-dimensional orthogonal basis, and verifies the
complete per-replica event order and terminal correction. This establishes the
data-controller induction, subject to the same inherited local operator and
cover interfaces. See `proof/GLOBAL-RESTRICTION.md`.

## Proposition 3: whole physical owners implement every residual

Order the 72 complete invocations lexicographically by
`(7*stage + 6*replica, stage, replica)`. This preserves every replica's original
controller order. The literal assignment lists all 72*560 helper uses.

For each use, the independent audit establishes:

1. The owner is an actual retained data family and is idle throughout that
   complete invocation, taking account of every bridge touch.
2. The family's pending child contains the assigned residual factors, as
   actual vectors in its orthogonal port basis.
3. Residual and spectator coordinates extend to a full orthogonal 73-column
   chart. The existing normalized wrappers act identically on the spectators.
4. All 560 helper families are distinct and avoid all 224 active data families
   of that invocation. Its full 784-owner map is injective.
5. Assigned factors in each pending child are disjoint, and every unassigned
   factor is covered by its explicit paid remainder before the family's next
   touch.

The complete local interface accepts arbitrary helper dirt and restores its
spectators. Induction over the actual event schedule therefore substitutes
each invocation's specified residual for a factor of its owner's original
pending child. The product of all such factors and the paid complement is
exactly that child. No residual has more than one owner, and no gate crosses
an unfinished local invocation.

Consequently the final hosted template has the same required retained data
endpoint as Proposition 2. Its full private namespace is disjoint from its
7168 data families. Its physical stock is 7738. Intermediate legacy bank
display metadata is inactive: the final template's bank family list is empty.

## Proposition 4: exact complete recursive invoice

Literal replay gives local profile

$$
H_{\mathrm{loc}}=\{1:2531,2:160,3:530,4:88,5:298,6:68,7:1,8:1\}.
$$

Subtracting the verified assigned pending axes from the original idle children
gives the remainder profile

$$
H_{\mathrm{rem}}=\{3:3354,5:3270,7:60,48:230\}.
$$

There are exactly 72 complete invocations, so

$$
H=72H_{\mathrm{loc}}+H_{\mathrm{rem}}
=\{1:182232,2:11520,3:41514,4:6336,5:24726,6:4896,
7:132,8:72,48:230\}.
$$

Direct integer summation gives

$$
\sum_r rH[r]=520704=73\cdot7168-2560.
$$

This agrees with the independent geometry identity
`D = 8*((9-1)*112 - 9*64) = 2560`.
The maximum child rank is 48; `73^2 > 2*48^2` verifies the retained halving
condition. The exact finite invoice charges all local scalar primitives,
wrappers, physical routing, terminal correction and private work. Its global
prefix is bounded by 206 bits while retaining a 512-bit allowance, including
72 complete local cover sweeps and 72 individual bridge sweeps.

These facts are independently checked from the final program and actual
owner footprints, not inferred from the nominal optimization objective.
The objective and its solver gap have no proof role.

## Proposition 5: complex moment and global assembly

For the fully paid H above, m=73 and W=7168, the inherited complex moment
including its exceptional-class envelope is

$$
F(a)=\sum_r\frac{rH[r]}{mW}\left(\frac mr\right)^a
 +\frac{32m\sum_r H[r]}{10^{16}W}m^a.
$$

The Mercator and independent base-two implementations produce enclosing
rational intervals at both neighboring endpoints. Both establish

$$
F(b)<1<F(b+10^{-24}),\qquad
b=\frac{1460074471110324279467}{10^{24}}.
$$

The same two engines reprice the pinned PR493 bit histogram at

$$
c=\frac{391360506745414227149}{250000000000000000000000}.
$$

Its unchanged physical operator remains a cited dependency. Set
`eta=beta=10^-18` and
`s=min(c,(1-beta)*b)-10^-24`. Starting at the inherited certified seed
`a0=384599/10^10`, six steps use

$$
a_{j+1}=(1-s)s+s a_j.
$$

Every step's strict gap and sufficient finite cutoff are recorded exactly.
Then `q=a6*(1-2*eta)` and the selected kappa is the largest multiple of
`10^-18` strictly below `(1-eta)*q/(1+q)` for this assembly. The inherited
outer engine checks all 47 strict rational inequalities, including row,
literal scalar, precision and exposed-work constraints. All pass at

$$
\kappa=\frac{182243220215421}{125000000000000000}.
$$

The next grid point and invalid eta/beta controls fail. The exact proof
objects are `evidence/EXACT-ASSEMBLY.json` and its reconstructed counterpart
under the requested work directory.

## Conditional conclusion and comparison

Under the same all-size compiler, common-label/mutable-basis, normalized
Lemma A, restored-row, precision/tape and analytic-transfer contracts as
PR514, Propositions 1-5 give the claimed global exponent saving in the
inherited integer-multiplication framework. No stronger interface is introduced
by the puncture or the whole-owner allocation.

The exact improvement relative to pinned PR514 is

$$
\frac{\kappa}{0.001391523459591829}-1
=\frac{66422302131539}{1391523459591829}
\approx0.0477335122693673.
$$

The newer comparison PR518 gives `0.001393662920776407`; the same new witness
exceeds it by approximately 4.6125099541 percent. Neither comparison means
that runtime at a practical input size improves by that percentage.
