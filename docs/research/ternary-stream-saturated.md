# Saturated source-frame continuations

This working extension of [the stream compiler](ternary-stream.md) enlarges
its candidate matching graph. The local invertible gates, physical channel
allocation, protected outputs, transparent dirty-scratch wrapper, and physical
rank accounting are unchanged. The implementation is
`scripts/experiments/ternary_stream_saturated_scratch.cpp`; independent exact-Q
controls are in `scripts/experiments/ternary_stream_saturated_scratch.py`.

## Exact geometric envelope

For a nonempty family of five-set indicators, let C be their common
intersection and U their union. When C is nonempty and C differs from U,
every row belongs to

    E(C,U) = { z : support(z) subset U,
                    z_i=t for every i in C, and sum_i z_i=5t }.

This space has dimension `|U|-|C|`: outside C there is at least one coordinate,
and the common-coordinate equations plus the sum equation impose |C|
independent constraints on Q^U. If C is empty, the envelope is Q^U. If C=U,
the family is the singleton five-set C and its span has dimension one.

A source node is called saturated when its actual rational source span attains
the envelope dimension. Because the source span is contained in the envelope,
saturation certifies equality with E(C,U). The implementation tests this using
canonical elimination modulo p=2^61-1 on original five-set indicators. Every
square minor in dimension at most 28 has absolute value at most 5^14<p by
Hadamard's inequality, so every modular rank equals the rational rank. It can
stop enumeration when the envelope dimension is reached; otherwise it visits
the complete source support. Four-point common cores require no elimination:
the distinct outside-coordinate unit entries make all their rows independent.
A five-point core is a single input line. There are no guessed saturation
flags or probabilistic span comparisons.

Suppose source gates b and c both consume the same scalar value, c is
saturated, and

    U_b subset U_c,       C_c subset C_b.

Every original indicator in the source support of b obeys c's envelope
constraints. Consequently `S(b) subset E(C_c,U_c)=S(c)`. This proves the frame
inclusion required to continue a preserved input wire from b to c, even when
their source supports have no ancestor relation in the chosen scalar DAG.
The implementation currently uses this rule only when C_c is nonempty; all
ordinary ancestor-based source and source-to-dual candidates are retained
when they respect the new order.

## A common schedule for all selected links

Write d(n) for the envelope dimension, e(n) for the saturation flag (zero or
one), and s(n) for the source-support cardinality. Source nodes are ordered by

    (d(n), e(n), s(n), node_id).

They precede every dual node, which retains its original topological order.
Every ordinary source DAG edge has U increasing and C decreasing, hence d
cannot decrease. If d stays equal, its two signatures C,U agree. A saturated
parent in that same envelope forces its child to be saturated too; thus e
cannot decrease on an equal-dimension edge. If d and e are equal, strict
source-support inclusion makes s increase. The original scalar source DAG is
therefore topologically ordered by this key. The singleton-line case has
dimension one and an actual addition necessarily enlarges its envelope.

Each additional saturated-frame candidate is explicitly oriented from the
earlier node to the later node in this same order. The signature inclusions
already force nondecreasing d. For equal d they force equal signatures; if the
earlier frame is nonsaturated it precedes the saturated destination by e, and
if both are saturated they have exactly the same frame and may be ordered by
s and node ID. Ancestor-based source-to-source candidates inconsistent with
the new key are discarded. Source-to-dual candidates always respect the phase
boundary, since the source region is ancestor-closed. This gives one global
acyclic schedule for ordinary producer edges and every chosen continuation.

## Inherited physical and algebraic checks

The matching still has capacity one per earlier gate and per later delivery.
Thus each gate has a last-used input to overwrite, all selected continuations
form channels, and each matched link saves exactly one physical register.
Every physical register is explicitly allocated. Every incoming register
transition is checked against an original producer edge or its selected
continuation. The new continuation proof is the exact envelope inclusion
above; both assigned frames were already certified nondegenerate by the
source/dual cut audit. Designated side and center outputs are still protected.

All operations remain invertible for arbitrary initial scratch. No garbage
register is treated as zero or silently reassigned. The exact scalar signal
map remains JLV, so the original transparent wrapper and three-shear exchange
apply unchanged. Both complementary invocation orientations have downward
rank `C(h,2)(h-2)` and exact physical rank sum

    (2v+R)h - 2v + 2 C(h,2)(h-2).

Every one of the R physical auxiliary registers still enters an invocation
with the zero frame D0 and exits with the full frame D1, in both orientations.
The data-bank entrance and exit labels are unchanged. Producer register
allocation does not combine, delete, or retime any interstage endpoint or
partner-permutation edge. The stage-one/stage-three auxiliary reuse uses the
same permutation of `(physical_role_id, partner_index)` with the new role
range. Hence an endpoint-only rank moment or batch multiplicity expressed as
`v^2 R` uses the new R without any other change. Applicability of a separate
batched transfer theorem remains the responsibility of its own interface
audit; this compiler preserves those endpoint hypotheses.

## Exact controls

For the direct h=10 producer, the independent Python control derives every
frame with Fraction arithmetic, checks every candidate inclusion over Q,
constructs its own maximum matching, materializes the full invertible
producer, and checks every input/dirty basis through both invocation
orientations and the full exchange. At depth four with source-to-dual links,
7,642 original roles become 6,827: 815 matched continuations. Both orientations
have rank sum 73,526 and downward rank 360; all 7,331 data/scratch basis symbols
pass the complete wrapper.

The C++ checker accepts the same arguments as the ancestry-only compiler:

```sh
c++ -std=c++17 -O3 scripts/experiments/ternary_stream_saturated_scratch.cpp -o /tmp/stream-saturated
/tmp/stream-saturated DAG.bin TARGETS.bin 4 LINKS.bin mixed
python3 scripts/experiments/ternary_stream_saturated_scratch.py --h 10 --depth 4
```

It depends on `ternary_target_span_classes.cpp` for the exact modular
elimination routine and on the certified DAG and source/dual target export.
The integrated driver must bind those inputs to their independently checked
support and frame certificates. Counts from different scalar DAGs must be
recomputed rather than added together.
