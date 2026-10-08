# Saturated dual-frame delivery continuations

This working extension adds dual-to-dual links to the
[saturated source-frame stream compiler](ternary-stream-saturated.md).
Its separate implementation is
`scripts/experiments/ternary_stream_bilateral_scratch.cpp`, with independent
Fraction controls in `scripts/experiments/ternary_stream_bilateral_scratch.py`.
The scalar invertible gates, matching capacities, physical register allocator,
dirty-scratch wrapper, protected outputs, and D0/D1 endpoint interfaces remain
unchanged.

For a dual node n, let V(n) be the span of its exact reachable side-target
indicators, with common target core C(n) and target union U(n). Its assigned
frame is `V(n)^perp`. The same geometric envelope and exact modular saturation
test used on source families apply to these original five-set target rows.
Every matrix minor is bounded by `5^14 < 2^61-1`; hashes or floating-point
ranks do not enter the decision.

For two dual gates b and c consuming the same scalar value, suppose V(b) is
saturated and

    U(c) subset U(b),       C(b) subset C(c).

Every target row of c lies in b's envelope, hence `V(c) subset V(b)` and
`V(b)^perp subset V(c)^perp`. This is the required forward frame inclusion.
The singleton-envelope case causes no exception: a five-set indicator
supported on the same five points must be that same indicator. An empty core
has envelope Q^U and requires only the union containment.

Let d(n) be the target-envelope dimension, e(n) its saturation flag, and t(n)
its target-family cardinality. After all source gates, order dual nodes by

    (-d(n), -e(n), -t(n), node_id).

On an ordinary dual DAG edge b to c, the reachable target family of c is a
subset of b's. Its union shrinks, its common core grows, and its envelope
dimension cannot increase. If dimensions agree, signatures agree; a
saturated child forces a saturated parent in that envelope. If dimensions
and flags agree, target-family cardinality cannot increase. Equality of all
three quantities leaves the original topological node order. Thus this key
orders every original dual edge correctly. Additional dual continuations are
explicitly required to go forward in this same order. Source-to-dual links
respect the unchanged source-first phase boundary. The combined schedule is
acyclic.

The matching may now have earlier gates in either region, but still permits
at most one continuing input per gate. Every gate therefore has a final-use
input it may overwrite with its sum. Every selected continuation saves one
physical role, with the same formula `R=A+q-matching_size`. The complete physical
allocator checks every incoming role transition against its ordinary DAG
edge or selected continuation, and verifies protected outputs and the role
count independently. No new downward rank occurs. Every auxiliary role still
enters at D0 and exits at D1 in both orientations; interstage endpoints,
partner permutations, and data-bank entrance/exit labels are unchanged.

A positive exact control uses ambient h=28. Earlier gate b has four distinct
designated target uses whose five-set indicators span a saturated dimension-four
space; later gate c has a different designated target in that same span. Their
assigned dual frames have dimensions 24 and 27. Three source indicators give
b and c common source cores of size one, so the actual source/dual rule puts
both gates in the dual region. The independent candidate builder selects the
strict dual-frame continuation. Roles decrease from seven to six. Every one
of the 22 data/scratch basis symbols passes the forward/inverse nonidentity
wrapper, with rank sum 600 and zero downward rank in both orientations.
The full direct h=10 control also passes all coefficients, dirty bases, and
both physical orientations; it has no additional dual continuation at that
size, so the strict control is essential.

On the exact h=28 selected 16+12 split plus star DAG, depth four with both
extensions finds 983,670 matches, including 20,337 dual-to-dual and 36,945
source-to-dual links. The 9,755,066 raw roles become 8,771,396 physical roles.
The complete schedule checks 18,329,146 ordinary and 983,670 reused transitions,
with protected outputs, unchanged downward rank 9,828, and total physical rank
250,925,864 per orientation. These are finite compiler results for that exact
DAG, not an independent multiplication assembly certificate.

The command line is the same as the source-only extension:

```sh
c++ -std=c++17 -O3 scripts/experiments/ternary_stream_bilateral_scratch.cpp -o /tmp/stream-bilateral
/tmp/stream-bilateral DAG.bin TARGETS.bin 4 LINKS.bin mixed
python3 -m unittest discover -s tests -p test_ternary_stream_bilateral_scratch.py -v
```

The exact producer/rewrite and complete frame audit must certify the input
DAG and target export. The integrated driver must bind those artifacts and
the imported modular elimination code to the result before promotion.
