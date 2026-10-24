# A full native involution with no extra query child

## Result and exact boundary

This packet gives a full 112 by 112 response E with

    E^T = E,
    E^2 = I.

It emits both native shears for both current providers:

    F_E(x,y,h) = (x, y+Ex, h),
    B_E(x,y,h) = (x-E^T y, y, h).

The 48-port component is the controller lane's signed matching of pair modes. The 64-port component is the history lane's negative physical permutation. The latter replaces the half-Hadamard component in the controller's original matrix packet. This distinction is recorded in the payload and checked by an exact full-matrix square.

The word uses only the native progress of the two productive data banks. It uses no owned field, no private field, and no extra query child. All 408 arbitrary borrowed fields are unchanged. Their previous native progress is not supplied by this data word. A separate helper completion, recursive host, complete controller, precision bound, and final assembly remain obligations. This packet does not claim a kappa improvement.

The physical entry is (C_q x,y,h). The forward exit is (F_9 x,F_9 C_q^-1(y+Ex),h). The backward exit is (F_9(x-E^T y),F_9 C_q^-1 y,h). Each port uses its own q. All native and endpoint phase records use the original fixed exterior. No common-W exterior is used in this packet.

## The 48-port matching

Each of 24 physical pairs has a signed Hadamard code H_e, with H_e H_e^T=2I and H_e^-1=H_e^T/2. Let H be their direct sum. The code has two modes per physical pair. The two modes belong to the two incident centre vertices. At each of the eight vertices, the six incident modes are paired in a signed matching. Its matrix A_v is symmetric, has zero diagonal, and satisfies A_v^2=I. Let A be their direct sum. The physical response is

    E48 = H^-1 A H.

It follows that E48 is symmetric and squares to I. The chosen matching also preserves the intended selected principal block. These facts are proved in the pinned controller packet and are checked again for the full response in this producer.

For mode i, let P_i be the rank-two span of the two q labels in its physical pair. Distinct incident pair planes at one vertex are orthogonal. If source mode i is matched to target mode j, then

    P_i subset P_j-perp.

The target pair hole P_j-perp has rank seven and lies in each of the two final target holes for that pair. The producer checks all these inclusions from the literal binary labels in each provider. It lowers each literal canonical frame pair, so equality of subspaces is not used as equality of phase operators.

## Native schedule

The X fields of each physical pair move from their rank-one entry lines to P_i through rank one. They receive the pair code H_e at P_i. The Y pair receives the same code at its common I entry.

For each target mode j with matched source i, execute the following steps:

1. Move the coded Y_j field from I to the exact source frame P_i through rank two.
2. Add A_ji X_i to Y_j. Both fields have the same canonical frame.
3. Move Y_j from P_i to its pair hole P_j-perp through rank five.

All X fields then move from their pair planes to FULL through rank seven. The inverse pair code restores the physical X coordinates at FULL. Each Y physical pair now has both coded fields at its common pair hole. The inverse pair code is applied there. Each field then moves from the pair hole to its own final hole through rank one.

The resulting logical Y update is H^-1 A H x. Every arbitrary initial Y input has coefficient one after its code and inverse code. No initial Y value is assumed to be zero.

For the backward word, replace step 2 by X_i <- X_i-A_ji Y_j. Keep the native progress directions unchanged. Since H H^T=2I, the decoded update is -E48^T y. Each X source mode and each Y target mode occurs in one matching edge, so a transfer cannot change another transfer's input. The producer checks the full map without relying on that argument alone.

## The 64-port component

The other 64 ports use the history lane's frozen negative-permutation word. Each source line is orthogonal to its assigned target label. The target moves from I to that source line through rank one, receives one signed ADD, and completes its hole progress through rank seven. The X source completes FULL through rank eight.

This component consists of 32 disjoint negative transpositions, so its response is symmetric and squares to I. It is disjoint from the 48-port word in both data banks. The merged emitter remaps frame identifiers by their literal ordered bases, checks the inherited native records in canonical JSON form, and replays the full union. It does not replace a native record merely because two frames span the same subspace.

## A general sufficient condition

Let a pair code H have H H^T=cI for a scalar unit c. Suppose a one-to-one mode assignment i -> j has an admitted common source frame P_i, and P_i lies in a common pair hole for target j. Suppose the source and target native paths through these frames have the same total rank as their required productive progress. Then any admitted scalar weight on that assignment can be transferred at P_i with no extra query child.

The resulting forward response is H^-1 A H, where A is the weighted mode permutation. Reversing the scalar transfer gives its transpose in the backward shear. A weighted permutation is a unit when all weights are units. A symmetric signed matching gives an involution. This construction changes the source and target native paths; it is outside the old fixed-word transfer span and its orthogonality obstructions.

The frozen payload proves the stated matching and actual phase recipes. It does not claim every abstract matching has the required frame inclusions. Those inclusions and phase recipes remain explicit hypotheses of the general statement.

## Selected and ordinary principal units

The selected set is S={0,7,15,36,42,46,79,89}. The selected block L=E_SS is the same as the controller's pinned block. Its exact dyadic inverse is part of this payload and is checked in both the inherited proof and this producer.

Write the full response in selected and ordinary blocks as

    E = [[L,B],[D,H0]].

Since E^2=I and L is a unit, the ordinary principal block is also a unit, with

    H0^-1 = H0-D L^-1 B.

Indeed H0^2+DB=I and H0D=-DL, so both products with the stated inverse are I. The producer constructs this inverse and checks both orders exactly. This establishes the scalar principal-unit premise required by the proposed interface. It does not by itself admit a new native use of that inverse at an arbitrary frame.

## Invoice

The complete data word has native profile

| Rank | Child count |
| --- | ---: |
| 1 | 160 |
| 2 | 48 |
| 5 | 48 |
| 7 | 112 |
| 8 | 64 |

The total is 432 children and rank mass 1792. Each of the 224 productive fields receives total rank eight. The 48-port part has mass 768; the 64-port part has mass 1024. There is no query capture to add to this invoice.

The exact scalar cost is 3032 real primitives in each direction and provider. All source and target pair codes, inverse codes, matching transfers, and inherited 64-port ADDs are included. There are no top-level owned or private fields. There are 224 endpoint maps and at most 864 native side maps, before internal recursive costs. The top-level maximum-array norm bound is 6. It is computed from exact absolute coefficient row sums after every scalar operation.

The native rank total alone is not a full recurrence. A helper completion must supply its actual physical endpoints and all of its native, map, owned, private, and restoration costs. The complete controller must also account for stage changes, exterior phases, terminal decoding, and all recursive children.

## Verification and credit

The producer verifies all 632 input columns, including 408 arbitrary borrowed columns. It checks every scalar frame, every native frame and rank, each endpoint, and the complete response. It reads the serialized payload and repeats the full coefficient and frame replay. It checks symmetry, the full involution identity, and both principal inverses with exact rational arithmetic.

Every distinct new physical native edge is checked by an exact interpreter separate from the Clifford compiler. The check includes all Pauli images and an exact reference state, so it fixes global phase. The original endpoint adapter order is checked for both providers. The proof and receipt state the scope of these producer checks; independent review is separate.

The controller lane supplied the signed matching and selected principal-unit construction. The history lane supplied the 64-port negative-permutation word. The root agent supplied the sparse matched routing schedule. The paired-centre work supplied the pair-code source representation and its actual frame geometry. The exact tools and all dependencies are pinned. This work used AI assistance. No PR or publication is authorized.

Run the producer from the workspace root:

```text
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 work/centre-encoding-campaign-20261014/lanes/oblique-native-20261017/matched-native-involution/emit_matched_involution.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -O work/centre-encoding-campaign-20261014/lanes/oblique-native-20261017/matched-native-involution/emit_matched_involution.py
```

Each run must complete all four words with native mass 1792 and scalar cost 3032. The frozen normal and optimized payload and receipt bytes agree.
