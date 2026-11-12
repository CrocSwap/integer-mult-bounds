# Wave 5 B5 scope and optimistic-budget gate

Status: proceed to one narrowly scoped literal implementation, not a new kappa.
Canonical main was checked live and remains
`e54523517d0f03e58352e647c403a5af3e525a57`.

The selected #7000 MOVE24472 recipe has two fixed nine-by-nine matrices:
right `[239,129,130,132,136,16,160,192,256]` and
left `[3,5,9,17,32,65,129,1,256]`. Both act independently on every one of f
columns. Target only those raw address permutations on the published
five-Gamma(f,r,P,S,w) packed ABI. Constant/linear/quadratic phases, the XOR
offset, positive C leaf, full MOVE, old codec/strided packing and global
admission remain separate. Both high-control and low-control directions are
required. All raw coefficient bits, including arbitrary signed endpoints,
are merely moved and require no numerical headroom restriction.

## Overlap gate

- #3834 `controlled-block-shear` checks the controlled-reversal/XOR identity
  through dimension 16; it supplies no complete tape schedule or uniform
  encoded cost. Its credited predecessor is #3825.
- #5188 `literal-elementary-interchange` supplies a complete fixed local
  all-H block interchange on separate binary descriptors, with a complete
  `2^20(H+1)(V+1)(L+1)^2` bill. Its binary-alphabet successor is also read.
  This is a substantial predecessor, but not the two source matrices on the
  shared Gamma ABI at O(fV+E).
- #6992 `current-serial-monomial-leaf` already proves the all-column serial
  identity and repeated direct-leaf bill. Only its descriptor iterator is a
  literal graph; its numeric/movement provider remains structured source.
  O(fV) additionally uses its explicit R1>=A1^6 and metadata absorption
  hypotheses. Those algebraic and serialization results are credited, not
  re-proved as novel here.
- `fixed-tape-ordered-shear` (canonical last package change
  7de16285a02ebb45cf46e7501baa7eafa78335e3) and
  `fixed-tape-affine-shear` already give literal O(V) ordered modular-addition
  kernels with separate supplied LSB descriptors and protected output.
  At Q=2 a unit shear is a CNOT in one direction. At Q=2^f, modular addition
  is not independent bitwise XOR. These results leave reversed-field routing,
  full caller descriptor generation and selected owner installation outside
  their exact scope. They supply the split/merge and unary-clock methods.
- `physical-gaussian-monomial` explicitly does not expand its full structured
  provider to a complete transition table; `selected-monomial-tape-lift`
  supplies the record list under inherited compact-movement propositions.
- Live targeted open-PR searches are retained in OPEN-OVERLAP.json. No exact
  encoded two-matrix packed join was located in this bounded search; this is
  not an exhaustive archival absence theorem. Root owns active allocation.

The proposed novelty is the source-bound, literal, all-column join with actual
header-derived geometry and same-owner lifecycle, without long-record
absorption conditions. No new CNOT, GF(2) elimination, or tensor identity is
claimed.

## Optimistic complete bill

Use fixed CNOT decompositions obtained by exact row elimination (forward
order gives 19 gates for the right matrix; reverse pivot order gives 27 for
the left). Fixed gate count is independent of f, payload and address size.
Validate the exact matrix products and every one of 512 source addresses.

For one gate between logical coordinates h<l and column j, use

- A_j=P*2^((h+1)f-j-1) prefixes;
- M=2^((l-h)f-1) middle positions;
- B_j=2wrS*2^((8-l)f+j) opaque bits per chunk.

Then V=4 A_j M B_j. The program derives all three unary guides from the five
encoded fields. It advances j using an actual F tape, halves A and doubles B,
and keeps M unchanged. All setup intermediates have length O(V), with
geometric sums O(V) per fixed gate. Header acquisition is O(E+V).

Per prefix it stages the two high-bit halves, reads four B-bit chunks at each
middle position, emits source chunks [0,1,3,2] for high-control CNOT or
[0,3,2,1] for low-control CNOT, then restores high-half order. Every bit is
copied/returned/erased constantly many times. Each pass is O(V), hence one
fixed matrix costs O(fV+E), including full source clone, all gate-column
passes, fixed-bank alternation, final original-owner commit, descriptor
retirement and head return. Private history increases by O(V+E) per call;
repeated calls retain actual per-role maxima/unions. Original public DATA
stays untouched until the complete permutation succeeds. Failure private
cleanup is not promised.

No free transpose, arbitrary address lookup, callback payload source,
unpriced supplied unary sizes, variable-size program or input-sized RAM is
needed. This bill fits the assigned direct-leaf tariff but proves no faster
nonleaf rate or full assumption discharge.

Stopping rule: stop if the exact complete literal join is found in a later
predecessor, if generated geometry cannot maintain V=4AMB with paid resets,
or if the fixed graph cannot meet the complete O(fV+E) and history bill.
Verification: exact GF(2) products, independent direct-XOR address oracle,
actual emitted-graph replay, both CNOT directions, multiple coefficient and
spectator extents, complete f=1 and at least one actual complete f=2 fixture,
header/exterior/head/history checks, and changed-order/one-column/commit
controls. Root and another worker independently review before publication.
