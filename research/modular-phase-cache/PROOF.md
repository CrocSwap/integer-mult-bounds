# Exact persistent memory for a modular phase cache

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and theorem

Fix integers t>=0 and b>=1. A source x has one coefficient x_a in
Z/(2^b) for each a in F2^t. After loading x, a cache has no further access
to it. An external command i replaces the logical source coefficient x_a
by (-1)^(a_i) x_a. A read returns the sum of the current logical source,
modulo 2^b. Commands and reads can occur in any finite order, including
repetitions. Every source and every such history must be handled exactly.
The original source need not be recoverable from the cache.

Count only the cache states that can depend on x. Program constants and
externally supplied commands are not charged as source memory. Every
source-dependent header, retained output, random seed or control state is
part of that cache. There is no uncharged source-dependent transcript.
The construction below needs no history cursor. Its read leaves the state
unchanged. Temporary arithmetic and source preparation are separate costs.

Define

```text
B(t,b) = sum_{j=0}^t binom(t,j) max(b-j,0).
```

The minimum number of persistent states is exactly 2^B(t,b). Thus the
minimum fixed binary packet width is B(t,b), even for arbitrary nonlinear
encoding and state transitions. Zero-error randomized encoding or updates
cannot reduce this state count. Here zero error means correctness with
probability one for every source and every finite history, with random
coins independent of the source before loading.

This is a finite-ring observation theorem. It does not assert a smaller
cache for exact complex or unbounded integer outputs.

## A complete family of observations

Starting at x, apply exactly the commands indicated by a bit vector s
and then read. The response is

```text
f_x(s) = sum_a (-1)^(a dot s) x_a mod 2^b.
```

After every later history, the logical source is again an updated x of
this form. Two sources are observationally equivalent exactly when their
complete tables f_x agree. An exact cache may merge equivalent sources;
it cannot merge sources with different tables, since one fixed command
sequence and read separates them.

For each subset S of {0,...,t-1}, put

```text
z_S(x) = sum_{a: S subset supp(a)} x_a.
```

For Boolean s, ordinary integer expansion gives

```text
(-1)^(a dot s) = product_i (1-2 a_i s_i),
f_x(s) = sum_{S subset supp(s)} (-2)^|S| z_S(x) mod 2^b.
```

Evaluation of a multilinear polynomial on the Boolean cube is the
subset-zeta transform. Its matrix is triangular with diagonal one when
subsets are ordered by inclusion. Integer Mobius inversion gives its
inverse, so it remains invertible over Z/(2^b). Consequently two tables
agree if and only if every coefficient (-2)^|S| z_S agrees modulo 2^b.
For |S|<b this is equivalent to agreement of

```text
c_S = z_S mod 2^(b-|S|).
```

For |S|>=b the coefficient vanishes identically. Thus the vector of c_S
is exactly the observational equivalence class, not merely a sufficient
list of cached statistics.

## Every packed state is attainable

The full map x -> (z_S)_S is another subset-zeta transform: it sums over
supersets instead of subsets. It too is unimodular over the integers and
invertible modulo 2^b.

Prescribe each c_S independently in Z/(2^(b-|S|)) for |S|<b. Choose a
lift z_S modulo 2^b for each prescribed value and set the unused z_S to
zero. Invert the full zeta transform to obtain a source x. This source
attains all the prescribed residues simultaneously. Therefore the number
of distinct tables is exactly

```text
product_{|S|<b} 2^(b-|S|) = 2^B(t,b).
```

The nonlinearity-independent lower bound now follows by counting
distinguishable classes. This is the standard finite-state distinguishability
argument applied to the complete phase table. No rank claim over a field
is substituted for cardinality over this ring.

For randomized caches, concatenate a fixed finite distinguishing experiment:
visit each s, read f_x(s), and undo its commands before the next visit.
Conditional on any state immediately after loading, the future output law
depends only on that state and fresh source-independent coins. If the same
state had positive probability for two sources with different phase tables,
this common output law would have to equal two different deterministic
transcripts with probability one. That is impossible. The loading-state
supports for distinct tables are therefore disjoint. Each is nonempty,
so the same state-count lower bound follows. Any retained private randomness
or source-dependent random-tape position is included in the state, as the
contract requires. The upper construction is deterministic. Positive-error
randomized compression is not covered.

## Explicit updates, with no cursor

Pack c_S into disjoint fields of width b-|S| for |S|<b. The first field
c_empty has b bits and is the current readout. A command i has the
following simultaneous action, with each expression reduced at its own
destination modulus:

```text
i in S:      c'_S = -c_S,
i not in S:  c'_S = c_S - 2 c_(S union {i}).
```

An absent c_(S union {i}) contributes zero. If |S|=b-1, its unretained
integer value is multiplied by two at a one-bit destination and vanishes.
Otherwise the source field has one fewer bit than the destination, so
twice that residue is well-defined at the destination modulus.

The formulas follow by splitting the supersets of S according to a_i.
They can be executed in place. First update all fields with i not in S,
reading only fields with i in S. Those source fields remain untouched
throughout this pass. Then negate all fields with i in S. No copy of a
cache coefficient or stored phase cursor is required. Each command is
an involution, and different commands commute, because they realize the
literal source sign changes. Reads leave the cache unchanged.

This constructs an exact machine with all 2^B states. It is a logical
modular-arithmetic construction, without a native or fixed-tape tariff.
The Python implementation is functional and returns a packed integer;
it does not claim that Python's runtime allocates only B physical bits.

## Examples and limits

For b=1, B=1. For b=2, B=t+2. For t>=1 and b>=t,

```text
B(t,b) = b*2^t - t*2^(t-1).
```

This follows from the binomial sum and its first moment. At t=2,b=3,
the exact cache width is eight bits, versus twelve bits for the literal
four-coefficient source. At t=3,b=2 it is five bits, versus sixteen.
These comparisons price only persistent modular source information.

The modular quotient is essential. At t=1,b=2 the distinct sources
(0,0) and (2,2) have the same complete modular phase table, while their
unbounded integer sums differ. If a later caller needs source recovery,
discarded carries, exact Gaussian values or a changed query family, the
discarded information must be supplied and charged. This theorem does
not establish a saving under that stronger boundary.

## Predecessor boundary

Ali Romman's PR #4958 proves that the least invariant linear cache over
the complex numbers is the sum of the query ranks on joint diagonal
fibers. Its historical 56- and 112-row values are not recalculated here
and are not asserted over Z/(2^b). Its source and native lineage retain
their credit. The new step is a changed finite-ring contract, exact
observational class count allowing nonlinear states, and an attaining
variable-width cache with reversible generator updates.

Boolean zeta/Mobius transforms, Walsh interpolation, Smith normal forms
and finite-state distinguishability are classical. The same state count
can be read from the classical Walsh Smith diagonal, whose 2^j entries
have multiplicity binom(t,j). No new classical normal-form theorem or
literature-wide priority is claimed. The elementary proof above needs no
predecessor executable or spectral certificate.
