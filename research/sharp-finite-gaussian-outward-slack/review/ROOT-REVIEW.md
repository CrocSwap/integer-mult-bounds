# Independent finite optimum and compact Hall review

Base: `e54523517d0f03e58352e647c403a5af3e525a57`.
This is independent AI-assisted mathematical and implementation review,
not human review or formal-kernel acceptance.

## Exact finite theorem

The original candidate generator and the independent certificate checker
use different comparison and enumeration methods. The generator orders
radical gaps by128-bit rational square-root enclosures; the independent
checker uses sign-aware integer squaring. Its full matching covers all 3,121
points of the complete radius-five integer ball, has distinct outputs,
error at most one, and maximum outward increment sqrt(21)-sqrt(19).
The 58 attaining edges have squared input/output norms19 and21. The
1,692/1,691 strict-threshold Hall certificate proves the matching is optimal.
Integer coordinate boxes enumerate every possible error-one neighbor;
checking only the declared neighbor list would not suffice.

The left/right signed-permutation identity H4=L(2C+)R was checked directly.
Both maps preserve the integer lattice, the full ball and the two norms.
The converse uses L inverse, not L. Conjugation gives C-. Consequently the
finite obstruction is a necessary lower bound for unrestricted global
injections with error at most one. It does not give a global construction,
unit-ball escape, or a selected physical caller.

## Independent full-vertex cross-check of the short witness

`check_full_matching.py` does not import the author search, certificate,
checker or orbit-flow implementation. It forms the ball by combining two
two-coordinate sums of squares, generates the complete error-one graph by
integer/half-integer parity, and compares gaps using rational square-root
enclosures. It solves the full vertex graph by augmenting paths and obtains
maximum strict matching size 3,089 and an alternating cut 1,801/1,769.
There are 39,681 error-one edges and 23,137 strict-beta edges. The paired
signed-permutation group is independently reconstructed and verified to be
the 192 even-sign permutations. The cut is invariant under every paired action.

The independent orbit-capacity flow finds the same optimum and extends the
cut by the balanced negative-product (2,2,2,2) orbit. This gives the compact
1,809/1,777 witness. Its two exclusions and one added positive-product orbit
were checked against both full graph data and exact formula membership.
The compact standalone checker needs no matching/Hall list:38 representatives
cover its entire input set, and the paired group maps each allowed neighbor
into the declared output container. The elementary generating polynomial
counts B19 as 1,897; orbit multiplicities include the zero-coordinate factorial.

Group adjacency means the neighborhood of an entire input orbit is a union
of output orbits. It does not assert a complete bipartite graph between the
two orbits. The final proof and code preserve this distinction.

Including equality at beta restores a full 3,121 matching in the independent
full-vertex code. The primary checker also detects certificate corruption,
duplicate outputs, an omitted neighbor, a strict-error mutant, and a wrong
threshold tie rule. The full comparison and Hall counts use exact integers.

From the repository root:

```sh
python3 -I -W error -B research/sharp-finite-gaussian-outward-slack/review/check_full_matching.py
```

Expected marker: `PASS_FULL_GRAPH_ALTERNATING_HALL_CUT`.
Default output omits the long point lists; `--full-points` reproduces them.
The compact receipt is `review/RESULT.json`. The publication replay additionally generates the two-exclusion witness
directly, checks its complete neighborhood, and detects the erroneous
inclusive tie rule without importing the compact checker.

## Limits

The exact finite claim is at radius 5 and error cap 1. No search outside its
recorded domain is implied. The inherited #6509 global construction gives
upper bound 1, leaving the global infimum in [sqrt(21)-sqrt(19),1]. The
selected multiplication argument retains all five assumptions and its
unchanged kappa. The obstruction concerns a possible rounding contract;
it is not a contradiction of the selected exact-layer route.
