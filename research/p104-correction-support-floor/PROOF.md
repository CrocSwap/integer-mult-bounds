# A 38-ADD floor for the sparse P104 correction

This contribution was produced by Nick Petalas. Apache-2.0.

## Model and result

Let C be the exact 799-coordinate rational operator defined by the 74 ADDs in
Ali Romman's PR6537, head `8bc9f991afe9fde83700ff86e520230eaa4595e7`.
The original RESULT.json is retained byte for byte in `inputs/`. Its construction,
factorization, upper bound and relationship to PR6529 are credited premises.
This package does not replay the old correction or the whole supplier.

Registers initially contain independent scalar inputs. A circuit uses
`r_i <- r_i + c*r_j`, with i distinct from j, and nonzero scalar SCALEs.
The ADD coefficient may be any rational number. SCALEs are free for this lower
bound. The circuit must finish with C on the original coordinates and restore
every additional dirty register. Any finite number of additional dirty or
zero-initialized registers is permitted. They initially contain no precomputed
linear combinations of the original inputs. Register names are fixed.

**Theorem.** Every such circuit uses at least 38 ADDs.

Thus the predecessor's 28 to 74 ADD gap becomes 38 to 74. This does not prove
that 38 or 74 is the optimum. It does not lower the source's scalar allowance
or change any productive or paid recursive rank.

## General first-final-ADD lemma

Suppose B specified output registers each have final coefficient support at
least s, where B is positive and s is at least two. Support means the number
of independent initial input coordinates with nonzero coefficient. Then any
circuit in the model above uses at least

`B + s - 2`

ADDs. No restrictions on cancellation, feedback, coefficient magnitudes,
interleaving or workspace size are needed.

Each specified register must receive an ADD: its initial support is at most
one, and SCALE cannot increase support. For each, mark its last ADD. These B
marked events are distinct because an ADD changes only its destination.
Let t be the earliest marked event. Subsequent SCALEs of its destination
have nonzero coefficients and preserve its support. Its row immediately
after t therefore already has support at least s.

Consider the arithmetic dependency graph of that row at this prefix. Give
each initial scalar coordinate one leaf, each SCALE one unary vertex, and
each ADD one binary vertex. Retain only ancestors of the row. The underlying
undirected graph is connected. If it has L input leaves, U unary vertices and
A binary vertices, it has at most U+2A edges and L+U+A vertices. Connectedness
gives `U+2A >= L+U+A-1`, hence `A >= L-1`. At least s distinct input leaves
occur because the row has s nonzero coefficients. Cancellation can introduce
additional leaves but cannot remove this requirement. Thus the prefix through
t contains at least s-1 ADDs.

The other B-1 marked events lie strictly after t. They are not among those
prefix ADDs. The total is at least `(s-1)+(B-1)=B+s-2`.

The argument includes workspace leaves, even if their final coefficients
cancel. It actually does not need workspace restoration, so imposing that
requirement cannot weaken the bound. Clean registers contribute zero-valued
leaves and do not reduce the number of independent leaves needed by the row.

As a function of B and s alone the lemma is sharp. Form a sum of s inputs
in one of those input registers using s-1 ADDs. Add that register to each of
B-1 other input registers. Exactly B outputs have support at least s; their
support sizes are s and s+1. The circuit uses B+s-2 ADDs. This is a generic
attainment example, not an implementation of C.

## Exact specialization

The verifier reads only the `correction` array of the retained source result.
It extracts its rational rows in two ways: forward row operations and backward
propagation of one output covector. It compares all 799 rows. This computes
the new support statistic; it does not check the predecessor's supplier claims.

There are 28 rows different from the corresponding identity row. Their complete
support histogram is `{12:3, 13:19, 25:6}`. Rows 3, 372 and 382 have support 12.
The verifier prints every changed row and its support. Hence B=28 and s=12,
giving `28+12-2=38`.

The written argument proves the lower bound for every permitted circuit.
The finite replay corroborates the specialization and checks the lemma on
all 9,331 three-register binary ADD words of lengths zero through five and
56 attaining examples. Six malformed-support controls and three source-byte
corruption controls reject. These finite checks are not an exhaustive search
for rational circuits implementing C.

## Boundaries

Free register permutations, multi-target operations, COPY, INIT/CLEAR inside
the circuit, native maps, nonlinear operations, precomputed input encodings
and approximate or rounded implementation are outside this model. A circuit
with such operations needs a separate lower-bound argument. SCALEs are
nonzero; every actual scalar and routing cost remains payable by a consumer.
The theorem requires the complete operator C on independent coordinates.
Matching C only on states reachable from a particular preceding supplier
word is a different problem and is not covered by this bound.

This local arithmetic floor does not prove supplier admission, a complete
multiplication theorem or a new kappa. All five selected framework assumptions
remain. Independent human and formal proof-kernel review are unclaimed.
