# Independent review of the full matched native data word

The frozen full 112-port native data word passes this independent review.
Both directions and both providers implement the stated response. No
material error was found. This accepts the data word, its physical
boundary, and its local invoice. It does not accept a complete supplier.

The producer freeze is
`b35eae3fb4b53f51cfbed6bec8968b950c70e65bfe777cbe0d15e86c36dd4ab5`.
All consumed hashes are in `CHECKS.json`. This checker imports no
producer module or Clifford compiler. It uses the separate exact phase
interpreter written for the preceding independent pair-code review.
The producer uses a different interpreter from an older lane.

## Complete map and arbitrary state

The review reconstructs the actual response by routing each original
port basis input through the pinned pair rows, signed mode matching,
and inverse code. On the other 64 ports it uses the pinned negative
permutation. That permutation has 32 disjoint negative transpositions;
each source direction is orthogonal to its assigned target direction.
The new 64-port response differs from the normalized Hadamard block in
the earlier matrix packet. The checker rejects substitution of that old
full matrix.

The actual full response E is symmetric and satisfies E^2=I. Its
selected block L equals the earlier eight-port block. The checker
verifies both orders of the selected and ordinary inverses and checks
that their entries are dyadic. Equivalently, writing E=[[L,B],[D,H]],
the ordinary inverse is H-D L^-1 B. The identities E^2=I and L^-1 L=I
prove both inverse orders without a commutation assumption.

A reverse event replay checks every one of the 632 input columns of
each serialized word. It gives exactly

```text
F_E(x,y,h) = (x,y+E x,h),
B_E(x,y,h) = (x-E^T y,y,h).
```

The two productive banks are arbitrary. All 408 helper fields are also
arbitrary and are physically unchanged. Every event acts on one of the
224 data fields. There are no copy, clear, reset, owned-field, or
private-field events. No hidden zero-state premise is used.

The pair code and its inverse preserve each arbitrary initial target
value. A separate forward ledger checks every scalar source and target
frame and every strictly nested native transition. It also checks each
literal matching transfer, its sign, its physical carriers, and the
inclusion of the source plane in the target pair hole. Every mode occurs
once as a source and once as a target. The entire inherited 64-port
suffix agrees with its pinned source, including ordered frame bases and
full native recipe records.

## Physical phases and endpoint order

The independent phase interpreter constructs the monomial permutation
and phase on all 512 binary points. It compares all 18 Pauli images and
one exact Gaussian rational reference state for each Clifford. The
Pauli images determine the operator up to scalar; the nonzero reference
state fixes that scalar. No floating-point comparison is used.

There are 608 distinct native and endpoint comparisons after exact
deduplication. They cover all 384 native recipes in each word and all
224 endpoint records in each word. The checker also compares the
actual I and FULL frames with I and F_9. It retains the literal ordered
bases; it does not replace equal subspaces by equal phase operators.

For an intended exterior map L_p and canonical frame T_p, each stored
endpoint adapter is checked as T_p L_p^-1. This adapter converts an
input exterior to the canonical frame. Its inverse converts a canonical
output to the stated exterior. The source exterior is C_q; the target
exterior is F_9 C_q^-1. Thus the physical forward exit is

```text
(F_9 x, F_9 C_q^-1(y+E x), h)
```

from physical entry (C_q x,y,h). The backward exit has first component
F_9(x-E^T y) and second component F_9 C_q^-1 y. Each port keeps its own
q. No response matrix is moved through C_q. This packet uses the fixed
original exterior, not a new common-W exterior.

The check rejects a wrong matching sign and omission of the complete
pair undo. It also rejects a global phase change that preserves every
Pauli image but changes the exact reference state.

## Full local invoice and scope

Every data field receives exactly eight productive native rank. The
profile is 160 H1, 48 H2, 48 H5, 112 H7, and 64 H8 children. There are
432 children and native mass 1792. There is no separate query rank.

The scalar total is 3032 real primitives in every direction and provider:
2136 for both banks' pair codes and inverse codes, 384 for the 48 signed
matching transfers, and 512 for the 64 negative-permutation transfers.
There are 224 endpoint maps and at most 864 native side maps. No
top-level owned or private fields are used.

Exact absolute row sums after every scalar event give a top-level array
norm bound of six times the largest input-array norm. Native and
endpoint maps are unitary. This does not bound a recursive child's
internal state or establish the full precision contract.

The word does not advance the borrowed helpers to their former native
endpoints. A helper completion must be composed and priced separately.
The complete controller still needs source access, stage transport,
physical terminal maps, restoration, hosting, internal child costs, and
the full precision and recurrence proof. Neither native mass nor the
local scalar reduction alone proves a supplier or kappa improvement.

Run from the workspace root:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/matched-native-review-20261018/check_native.py
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/matched-native-review-20261018/check_native.py
```

The final output is `PASS_INDEPENDENT_FULL_MATCHED_NATIVE`. The normal
and optimized runs produce the same receipt bytes. The frozen H6 and
bundled mode-query services were not independently replayed in this
review; they remain separate producer results. This review was produced
with AI assistance. No publication is authorized.
