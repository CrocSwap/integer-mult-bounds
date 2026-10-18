# Independent bounded bank review

Reviewed architecture-portable-banks.py and architecture-portable-audit.py,
the prior signed-prefix GLOBAL-TEMPLATE, the extended119 local scalar receipt,
and the phase normalization formulas. No other worker's source was edited and
no duplicate scalar/Gaussian full replay was run.

## Findings and required clarifications

1. The emitter's distinct symbolic owner JSON values are not by themselves an
   address-injectivity proof. The actual necessary finite check is distinct
   (bank, owner inverse permutation) pairs within each invocation. The supplied
   consecutive disjoint residual axes prove this: each slot has a different
   offset, so its local-to-bank permutation A has first column e_offset, hence
   its A and A^-1 differ from every other slot in that bank. For any fixed
   orthogonal cover d, right multiplication by d is injective. The architecture
   worker agreed to add the actual permutation check to the decoder.
2. Cross-cover coownership is intentional, not independent helper allocation.
   It uses the inherited arbitrary-correlated dirty/window semantics. The
   finite scalar proof handles arbitrary helper inputs; the two-sided wrappers
   act on complete local helper windows. The endpoint Fourier product alone
   must not be described as an independent proof of the all-size window lift.
3. The v2 template dropped descriptive cover/loop-order metadata. The fixed
   cover enumeration and g=d*A^-1 helper convention should be retained
   explicitly. The architecture worker agreed to restore them in v3.

## Geometry and chronology verified by inspection

A is a literal coordinate permutation: its first r columns are the assigned
r residual axes and its remaining columns list the complement. Therefore
A^-1=A^T exactly, including nonsymmetric routes. Conjugating standard C_r by
this permutation moves precisely those r Fourier factors onto the assigned
axes with no Gaussian phase. Residual axis sets in a bank are disjoint; their
coordinate Fourier factors commute. The padding is exactly the complementary
axis set, so their product is the whole-bank Fourier operator.

The prior interleaved schedule has only two concrete helper-family-range
records: bank padding and the final all-live correction. Both are replaced;
all retained data owners are below7680 and unchanged. Bridge, idle, data phase,
terminal and local-stage chronology remain exactly the prior schedule. Since A is a
coordinate permutation, rowweight(d*A^-1)=rowweight(d), so the inherited
delta_i(d)=(rowweight(row_i(d))-1)/2 mod2 correction is unchanged by new
helper routing. New
helper families are7680+stage*banks+bank, private namespaces start at the new
live width, and the final correction uses all current live families.

The boundary adapters surround the complete old-response/main/cleanup program,
not individual intermediate gates. Local independent symbolic checks bind all
26 entrance charts, zero gauged K, block diagonal helper restoration, private
erasure, and both orientations to candidate SHA256
3b78069c4ce032e95f757a2f79fa5557af923c947430b638b0eb6859be659866.

For W with helper endpoint J=L*C_r*R0, P=R0^-1 before old response and Q=L^-1
after cleanup give Q*W*P the desired helper C_r while keeping data fixed. This
requires the separately verified block diagonal endpoint, not just zero K.
No adapter is commuted through the main circuit. For the backward convention
phi(A)=A^(-dagger), phi(AB)=phi(A)phi(B), and unitary address adapters satisfy
phi(P)=P and phi(Q)=Q. The same chronological wrappers are correct; each real
scalar shear is swapped and negated. No missing inverse-transpose convention
or unexplained noncommutation remains in this sufficient algebra.

## Scope

The changed finite geometry and wrapper theorem are explicit. Completion of
items1 and3 strengthens the actual emitted witness and readback. The inherited
all-size correlated window lift, recursive compiler, fixed tapes, common grid,
workspace/precision/restored-row and analytic contracts remain conditional;
they are not proved by this bounded bank inspection. No new unknown chart,
transformation or correction oracle is introduced by the finite extension.
