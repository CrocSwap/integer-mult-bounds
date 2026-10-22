# A cheaper kernel with an explicit caller-supplied cache

The second construction removes the eight center transports entirely, while
retaining all other emitted native events. This has an exact independent-input
ABI; its cache is not silently initialized with the desired answer.

Give the kernel eight independent inputs c at the **empty** chart. Delete the
eight source-to-center additions and their eight paid rank-eight transports.
The resulting reversible word has 640-column operator

```
N = [[A-BR, B], [0,I_8]],
paid(N) = {1:2201,2:412,3:510,4:127,5:40}.
```

The verifier emits this word independently, checks its actual scalar/transport
charts, replays all 640 columns, and reconstructs its true raw inverse
transpose. Here `(N-I)^2=0`. The raw dual uses the dual empty center charts;
it is not a claim that the same precomputed-cache caller can be run backward
without transposing its whole data-acquisition and cleanup protocol.

If the caller supplies **c=Rx**, then the original 632 output fields are

```
(A-BR)x+B(Rx) = Ax.
```

This is an exact conditional cache contract, saving eight rank-eight calls
inside the kernel. The caller must supply the actual physical empty-chart
array `R C_start^-1 x_physical`. There is no cache target credit and no
assertion that the external relation is free or independently arbitrary.

The source-specific useful fact is that **all 106 helper inputs occurring in
R start at the empty chart**. Their contribution can therefore be assembled
with finite pointwise scalar work and owned storage. The remaining input
contribution uses all 112 main X fields, whose entrance charts are lines.
One direct caller applies each line inverse to a copy of its main X input,
accumulates the eight combinations with their actual coefficients, adds the
cold-helper terms, and invokes the kernel. Each line inverse has rank one
under the retained monomial/phase normalization. At most one decoded main
temporary and eight accumulator fields need be live at once. All copied or
accumulated fields are owned, receive no productive input credit and are
erased under the retained owned-erasure contract after use.

That caller has complete recursive profile

```
paid(N) + 112 H1 = paid(source) - 8 H8 + 112 H1.
```

At t=1-C in (0,1], its surcharge over the source is
`112 - 8*8^t >= 48`. Thus this particular direct acquisition does not improve
the native price. This compares the **specified direct caller**, rather than
lower-bounding every cache acquisition, coded gather or shared consumer.
It does not reuse the eight cached fields as independent productive jobs.

The constructive question is whether **already paid** work can supply the
required cache at lower incremental cost. Cache retention, the timing and
orientation of acquisition, helper input ownership, all monomial charts and
any Gaussian cache updates must be specified. Updating eight cache channels
through a new eight-axis Gaussian itself costs eight rank-eight requests;
that update cannot be omitted from the proposed saving.

## First bounded recycling test

`cache_span.py` tests one scalar-bundle model of the selected p16 controller.
It represents all main data as exact rational Laurent polynomials in Q and
the independent stage variables. At each query stage it asks whether the
query demand lies in the rational scalar span of every earlier query demand
and every earlier external main snapshot. This allows retention of those
computed values, but no additional Gaussian multiplication of a cache.

None of the 18 full-stage query demands is in that causal span. The exact
stage-by-stage receipt is CACHE-SPAN.json. This finite result closes this
specific scalar reconstruction attempt; it does not exclude a changed
controller, physical port-dependent projections, a different cache basis,
additional funded cache transforms, or a joint consumer of the 640-field
extension. This model does not incorporate the full B/R/Clifford operators
and is not a proof that every physical cache consumer fails.

```sh
python3.12 -B research/retained-center-extension/cache_span.py
```

The next construction must change one of those premises and emit its actual
cache acquisition and independent-output program before repricing K.
