# Separate dyadic BIT outputs sharing one restored source

**Scoped recursive-interface construction; no new kappa.** Five distinct outputs
can share one temporarily permuted input row. The seed-55 schedule uses **13
ordinary recursive ADDRESS children instead of 40**, **78 affine events instead
of 240**, and the same **30 full XOR scans**, with no extra full private row.
Every source, output and arbitrary dirty spectator has its required endpoint.
Thirteen is optimal in the specified source-query alphabet, not among arbitrary
circuits or tape algorithms.

The changed permission matters: the common source is exclusively writable and
unobserved until the complete batch ends. PR953 keeps the source fixed while
batching terms on one target. Here each target receives its own sum; checking
only the aggregate of those outputs would not establish this interface.

## Reproduce and exact sources

From the repository root, with Python 3.12 and the standard library:

```sh
python3.12 scripts/research_package.py --package research/shared-dyadic-source
```

Expect `PASS_SHARED_DYADIC_SOURCE children=40->13 affine=240->78 XOR=30
patterns=768 no_new_kappa`, seven passing package tests, and
`PASS_REGISTERED_RESEARCH_PACKAGE research/shared-dyadic-source outcome=completed`.
Ordinary replay is read-only. For a source export, run
`python3 -I -O -B research/shared-dyadic-source/verify.py`, retaining the ten
input files in [SOURCES.json](SOURCES.json). The registered hook additionally
authenticates historical provenance against Git.

Base: `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. [TASK.json](TASK.json)
records the OS assignment draw, candidate tasks, bounded domain and claim.
[CERTIFICATE.json](CERTIFICATE.json) contains both complete words, their native
lowerings and coefficient-specific invoices. [EVIDENCE.json](EVIDENCE.json)
is recomputed field for field. The selected PR1094 record remains
`836330098538459/500000000000000000 = 0.001672660197076918`. Its binding-only
baseline identifies the complex supplier as binding; no supplier moment or
selected cold replay is supplied here.

## Interface and construction

Use equal-shaped F2 VALUE rows `y, x_1, ..., x_m`, with six physically ordered
equal-width ADDRESS fields over an odd prime-power ring. Additional fields
and dirty rows are spectators. Inherited from PR521/840, let `h` push addresses by

```
M(k) = I + (k/4) s r^T,
s = (1,0,1,-1,0,-1)^T,  r = (1,0,-1,-1,0,1)^T.
```

Since `r^T s=0`, `M(k)M(l)=M(k+l)` and `M(k)^-1=M(-k)`. For finite index sets
`J_i`, the required endpoint is

```
x_i <- x_i XOR sum_{j in J_i} (h^(2^j) + h^(-2^j)) y,
y <- y,                    every spectator <- itself.
```

All incoming rows are arbitrary. Distinct roles must not alias. Only `y`
receives ADDRESS queries in the construction; each XOR reads its current full
row into one specified output. The caller observes only the completed batch.
The source is restored, not disposable. Permission to query a DATA source is a
new caller contract, not a property established for the selected supplier.

For the witness, call `random.Random(55).sample(range(6), 3)` five times using
the same generator, sorting each sample:

| Output | Indices | PR953 separate-target children |
|---|---|---:|
| x1 | 0, 1, 4 | 8 |
| x2 | 0, 2, 5 | 9 |
| x3 | 1, 2, 5 | 8 |
| x4 | 0, 2, 3 | 8 |
| x5 | 3, 4, 5 | 7 |

The shared source follows these cumulative exponents:

```
0, -32, -16, -8, -4, -2, -1, 1, 2, 4, 8, 16, 32, 0.
```

At each vertex `+/-2^j`, XOR the source into exactly the outputs containing
index `j`. Every edge is dyadic. The final source return is included. The
comparison uses PR953's already optimized separate target batches, not the
weaker 45-child concatenation of fifteen independent PR840 pairs.

## Written uniform argument

At source prefix `p`, the source is `h^p y`. Each tap contributes exactly that
term to its designated output. The tour visits all required signed powers
with their separate incidences, and its total query power is zero. Therefore
all outputs have the claimed maps and all source/spectator dirt is restored.
The literal inverse reverses the events, negates query powers and keeps XORs.

For a general union `J = union_i J_i`, concatenate PR953's walk for every
maximal consecutive run `[l,u]`:

```
0, -2^u, ..., -2^l, +2^l, ..., +2^u, 0.
```

With `r=|J|`, `c` runs and `M=sum_i |J_i|`, this gives `2r+c` queries and
`2M` XOR scans. Empty masks and an empty union incur no special work. The
walk is inherited; the contribution is its legal use across distinct outputs
under the changed source permission.

For a nonempty consecutive union, **`2r+1` queries are necessary** in the
source-query/output-XOR alphabet. Restrict to a full-order orbit of `M(1)` and
represent the shift by `t`. Uniform correctness over arbitrarily large odd
prime powers implies the finite Laurent identity over `F2[t,t^-1]`: an orbit
longer than the exponent span separates its monomials. Restoring arbitrary
source input forces total integer exponent zero. Every required monomial
`t^(+/-2^j)` must occur at a visited source prefix in at least one output.
There are `2r` distinct required vertices, plus zero, so a closed walk needs
at least `2r+1` edges. The construction attains this. This is the elementary
source-visit argument, related to PR953's stronger run-component lemma; no
new general graph theorem is claimed. For nonconsecutive unions this note
needs only the stated upper bound.

Queries on outputs, other ADDRESS primitives, role mixing, non-dyadic queries,
clean storage and modulus-specific identities are outside that minimum theorem.
Small finite orbits can alias formal powers; a control demonstrates this.
The universal argument is written mathematics, not a proof-assistant theorem
or an extrapolation from the finite census.

## Native lowering and complete typed cost recurrence

For each signed dyadic query `k`, put `a=k/4`. PR840's seven chronological events are

```
z2 <- z2-z0
z3 <- z3+z0
z5 <- a*z5+(1+a)*z0-a*z2-a*z3
CHILD_C(0,5)
z2 <- z2+z0
z3 <- z3-z0
z5 <- -(1/a)*z5+(1/a-1)*z0+z2+z3.
```

The child is one full ordinary ADDRESS interchange with restored workspace,
not a free swap. Controls precede their target. Every diagonal and denominator
is a unit at every odd modulus. Substitution gives `M(k)`; reverse inverse
events give `M(-k)`. The package checks the rational and modular identities.
Its finite interpreters do not implement the physical tape algorithm.

Let each complete row have volume `U`, including spectators and VALUE records,
and each selected ADDRESS field width `b`. Define:

- `C_i(U,b)`: a complete restored ordinary child on row `i`.
- `L_{i,k}(U,b)`: all six affine events, including coefficient preparation/access,
  counters, temporary streams, source access, routing and head returns.
- `X_i(U)`: a complete aligned source-to-output XOR scan and its access/return.
- `R_B, R_F`: remaining schedule preparation, dispatch, row access, parking,
  routing, temporary-stream restoration and returns not already in `C,L,X`.

The coefficient-aware literal bills are

```
B(J;U,b) <= sum_{i,k} n^B_{i,k} [C_i(U,b)+L_{i,k}(U,b)]
             + sum_i 2|J_i| X_i(U) + R_B(J,U,b),
F(J;U,b) <= sum_k n^F_k [C_y(U,b)+L_{y,k}(U,b)]
             + sum_i 2|J_i| X_i(U) + R_F(J,U,b).
```

The words specify every multiplicity. No full-row copy, erase, initialization,
extra helper, restoration child or unlisted frame change is performed. All
source-return edges and both directions of each tested inverse are paid.
Any adapter required by a future caller would be additional work. Sequential
children give the safe peak bound

```
W_F <= (m+1+s) U + B_F(J,U,b) + W_C(U,b),
```

where `s` counts genuine spectator rows, `B_F` pays live descriptors,
coefficients, counters and nonchild primitive workspace, and `W_C` is the
maximum child workspace. Simulator storage is not a physical scratch bound.

For equal child and coefficient-specific tariffs on the equal-shaped rows,
the witness removes 27 children. The shared histogram is componentwise at
most the separate histogram: it introduces no new, potentially expensive
power. The receipt's `removed_queries_by_power` gives the exact difference:

```
B_bill - F_bill = 27 C + sum_k Delta n_k L_k + R_B - R_F,
Delta n_k >= 0,     sum_k Delta n_k = 27.
```

A total runtime saving still depends on actual routing, dispatch and caller
costs, including role-specific tariffs where appropriate. Neither `R_F=0` nor
`R_F=R_B` is assumed. For fixed masks under the inherited stream premises,
the form is `13 C(U,b)+O_J(U)` versus `40 C(U,b)+O_J(U)`. This is a **typed
interface recurrence**. Substituting the DATA batch `F` for ADDRESS child `C`
would be circular without a separate compiler. Growing index sets retain all
coefficient and program-size dependence; no uniform polynomial-in-index
stream bound is asserted.

## Evidence and limits

`oracle.py` imports no constructor or predecessor implementation.
`construct.py` supplies literal words and inherited native lowerings. The receipt covers:

- All 768 incidence patterns for two outputs/four indices and three outputs/three
  indices: exact Laurent endpoints/inverses, 25,088 cyclic dirty input columns
  per implementation, and simultaneous dirty fixtures.
- The selected witness on seven odd orbit sizes through 257: 2,667 dirty columns
  per implementation; six edge fixtures contribute 225 more.
- All thirteen native powers: 104 rational columns, 624 modular columns, and
  **850,408 complete ADDRESS inputs** with two interleaved binary spectators
  over moduli 3 and 5. Forward and literal inverse are checked throughout.
- Both complete words on the full six-field mod-3 BIT domain with four spectator
  assignments: **20,412 dirty columns per implementation**, plus sixteen
  simultaneous dirty-array fixtures.
- Twenty-four mathematical/admission controls, including seven native event
  omissions, missing source return, a wrong output, and a collapsed-output
  word that preserves the aggregate while violating the individual maps.
  Seven package tests cover source/certificate corruption, regeneration,
  overwrite rejection, missing child charges and scope admission.

These are exact finite checks, not a supplier or multiplication proof.
Domains and the stopping rule were fixed before replay; no heuristic search
or impossibility claim from failed search is used. No existing package,
selected frontier, frozen source or `upstream/` file is changed. Physical
mutable-source realization, labels, frames/owners, whole-call hosting,
arbitrary-width compilation, tape/precision, recovery and analytic transfer
remain separate obligations. Hosted CI and human review are separate from local replay.

## Open next questions

Find a concrete supplier caller that admits the shared writable source. First
trace every source read between its proposed cuts; an intermediate canonical
observation rejects this interface. Then price all adapters and full supplier
moments. No such caller or DATA-to-ADDRESS compiler is provided. Even adoption
on the BIT side alone would leave the selected complex bottleneck to address.

Allowing queries on both source and outputs changes the minimum-query problem.
A bounded starting instance is two distinct masks over indices 0 and 1, using
formal Laurent equality with all dirty roles retained. The source-visit proof
does not cover that alphabet. [TASK.json](TASK.json) records both questions,
their relevance, first steps and blockers.

## Credit and scope selection

Prepared for **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex** assistance
in derivation, implementation, verification and prose. No delegated agents,
independent human review or proof-assistant verification are claimed. New
material is Apache-2.0 under the repository license.

- **Ross Richardson, PR953**, reviewed head `5f052969846b0882ac4e22d9e818dd8ac05ea56f`:
  the retained single-target dyadic-run walk, restricted count and baseline.
- **Wentao Li / VictorLiwentao, PR840**, `da2cd0dd2229e08b61b174a8835a2c2bb99d2230`:
  signed-dyadic one-child lowering, centered pair and dirty-state contract.
- **Karl Appel / applecrusher, PR521**, `a190fdb39f31647fc6f651625353710624627348`:
  native unipotent ADDRESS map. **commdata2338, PR677**,
  `613c02b8b4411f991f108dcc1481b3f9100b996f`: completed DATA shears and workspace
  permissions, retaining eumemic/PR288 and Ali Romman/PR468 attribution.
- **Richard Hoekstra, PR1235**, inspected head `3941a3c63651d379feceb411019c30310e9e12d0`:
  related source-tour reasoning in a different phase/rank model. No priority
  for the general source-tour idea is claimed.
- **OpenAI's retained framework and Douglas Colkitt**: ordinary interchange,
  ordered streams, row volumes and tape contracts. Original notices and
  licenses remain source-pinned inputs.

PR1094's Rohan Arun/Jeremy Kothe construction and cumulative lineage provide
context only. Before [claiming Discussion1493](https://github.com/CrocSwap/integer-mult-bounds/discussions/1493),
noncommuting output frames were excluded for overlap with S3 work, and mutable
connector/operator repair for overlap with PR1439/Discussion1489. The distinct-output
source boundary was selected. The initial complete snapshot covered 745 open
PRs and 174 discussion/comment records plus local notes and the review ledger.
This is bounded overlap evidence, not a novelty certificate.
