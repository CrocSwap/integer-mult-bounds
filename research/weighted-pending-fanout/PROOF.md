# Exact weighted pending-capacity tariff

This scoped written proof was produced by Nick Petalas. Apache-2.0.

## Contract

Retain Sagar Thakrar's PR1168 common-source fanout alphabet. Arrays
`x,z,y_1,...,y_k` start arbitrarily and are distinct. Exact characteristic-zero
linear maps `B,A_1,...,A_k` need not commute. A fixed word must universally
realize

```text
x unchanged, z unchanged, y_i += A_i B x for every i.
```

The only paid root queries, with `s` equal to `+1` or `-1`, are

```text
B^s:   z += s B x
A_i^s: y_i += s A_i z.
```

Each is a complete source-preserving, spectator-preserving, private-work
restoring, head-returning query. Their implementations and complete prices
are premises. Inverse queries have the same positive fixed price as forward
queries. There is no direct product query, combined output query, free copy,
output-to-output query, changing source, frame change or overwritten helper.
Universality over the admissible maps is essential to the lower bound.
Special zero maps or relations among maps can admit shorter words.

An output is unfinished from its first readout query until its permanent
commit. Commit requires the correct all-input value. No later query may
touch it. Unstarted and committed outputs do not count toward the pending
capacity; they remain reserved arrays and are not reusable child scratch.

The new hypothesis is that output i has positive integer reservation weight
`w_i`, and at every query boundary

```text
sum_(i unfinished) w_i <= C,
```

where C is a positive integer. A commit can occur at a complete-query return.
Weights are declared lifetime reservations. Unequal physical payload widths
or a memory-saving theorem do not follow from this abstract contract.

## Theorem

Let `b(w,C)` be the smallest number of bins partitioning the outputs, with
total weight at most C in each bin; put `b(empty,C)=0`. If every `w_i<=C`,
the coordinatewise simultaneous minimum query counts are

```text
N_Ai = 2 for every i,
N_B  = 2 ceil(b(w,C)/2).
```

Consequently every positive fixed sign-symmetric complete query price gives

```text
Q_min = 2 sum_i c_Ai + 2 ceil(b(w,C)/2) c_B.
```

If an output has `w_i>C`, no universally correct word exists: it cannot even
be opened. The empty problem has the empty optimum. The theorem is uncapped;
the reference implementation deliberately accepts at most ten outputs.

## Lower bound for arbitrary words

Use Ross Richardson's PR938 coefficient state, as retained by PR1168:

```text
z   = z_initial + q B x,
y_i = y_i_initial + e_i A_i z_initial + f_i A_i B x.
```

Initially `q=e_i=f_i=0`. A signed B query changes q by s. A signed A_i query
changes `(e_i,f_i)` by `(s,s*q)`. Universal correctness implies final
`q=0,e_i=0,f_i=1`. Necessity already follows by specializing all maps to the
scalar identity and varying initial x and z independently. These coefficient
facts and summation by parts are credited premises, not new audit claims.

Since each readout changes e_i by a unit, and f_i must change, at least two
readouts of each output are necessary. Since q starts and ends at zero,
the number of B queries is even.

The discrete product rule gives, for each output,

```text
1 = f_i(final) = - sum_(B queries) e_i(before query) * delta(q).
```

Indeed, an A_i query contributes `q delta(e_i)` both to `delta(e_i q)` and
to `delta(f_i)`, while a B query contributes `e_i delta(q)` only to the
former. The endpoint product is zero. Thus every output has nonzero e_i
immediately before at least one B query. Such an output is unfinished:
before its first readout e_i is zero, and a correct permanent commit has
e_i zero with no later changes.

Assign each output to one such B query, for example the earliest one. The
outputs assigned to a single event are a subset of its unfinished outputs,
so their total weight is at most C. Nonempty assigned sets partition all
outputs into at most N_B feasible bins. Hence `b(w,C)<=N_B`. Combining this
with evenness gives the stated B lower bound. This argument permits extra
readouts, arbitrary integer excursions of q and e_i, overlapping lifetimes,
idle intervals and any commit order. It does not assume the emitted word.

## Attainment

Choose any optimal bin partition `G_0,...,G_(b-1)`. Start with q=0 and, for
bin j, set `s=(-1)^j` and emit

```text
for i in G_j: A_i^(-s)
B^s
for i in G_j: A_i^s; commit i
```

Let z_before be the connector immediately before the B query. Output i
receives exactly

```text
-s A_i z_before + s A_i(z_before+s Bx) = A_i Bx.
```

Only that bin's outputs are unfinished during this block. Every one commits
before the next bin opens. The capacity is legal, all readout counts equal
two, and q alternates between zero and one. If b is odd, append one B^(-1)
after all commits. Otherwise nothing is appended. The connector returns
exactly and the B count is `b+(b mod 2)`. This attains every lower bound
simultaneously, and therefore every declared positive complete price.

## A strict obstruction to total-weight pricing

Take `w=(3,3,3,3,3,1)` and `C=5`. The five weight-three outputs must occupy
different bins, and the weight-one output can join any one. Therefore b=5
and exactly six B calls are needed, together with twelve readouts. The
total-weight relaxation gives only four B calls, since total weight is 16
and `2 ceil(ceil(16/5)/2)=4`.

For declared complete prices `c_B=52` and `c_Ai=1`, the correct optimum is
324, whereas that relaxation prices only 220. These are abstract query
prices. They are not the physical primitive prices of a selected supplier.
The new result is the exact packing obstruction and its matching scheduler.
No optimality claim is made over larger query alphabets.

## Algorithms and finite evidence

The subset dynamic program stores `d[mask]`, the minimum bins covering that
mask. The bin containing its least item is some feasible submask S containing
that item; remove S and use `1+d[mask xor S]`. Enumerating all such S is exact
and reconstructs an attaining partition. There are O(3^k) arithmetic checks
and O(2^k) table entries. This is exponential in output count, not a claimed
polynomial optimization algorithm.

An independent oracle successively puts each weight into every feasible
existing bin or a new bin and keeps all distinct sorted load tuples. Labels
of bins can be forgotten because all later feasibility decisions depend
only on loads. This enumerates every feasible packing up to identical loads.
The two methods agree on the fixed multiset domain recorded in the receipt.

Every emitted schedule in that domain is also executed by ordinary integer
matrix arithmetic on all basis columns of every arbitrary initial row.
Each A_i and B is a literal two-by-two matrix; a checked pair does not
commute. The interpreter checks every commit, every pending-weight boundary,
both unchanged source rows and all outputs. It does not use the coefficient
state to compute its endpoint.

A separate breadth-first word search checks four weighted three-output
contracts. It considers both signed B queries and every legal signed readout,
without a packing bound, proposed tariff or restrictions on extra readouts.
It searches increasing unit-query lengths through ten. Complete shortest
layers and total distinct state counts appear in the generated receipt.

Two exact quotients keep that search finite without discarding a better
word. Simultaneously negating q and every e_i, while preserving f_i, is a
sign symmetry of its queries and endpoint. Also, an output reaching
`(e_i,f_i)=(0,1)` can commit immediately: delete all its later readouts from
any successful continuation. Other outputs and the connector do not read
it, its own correct final value remains correct, and reserved pending
capacity only decreases. Thus an optimum exists with these greedy commits.
This proves the search covers a shortest word, even though it does not count
all words or all commit annotations.

## Remaining obligations

Predecessor private-work, coefficient preparation and fixed-tape routines
are cited contracts, not executed or admitted here. If I denotes admission,
P denotes reusable preparation and D denotes schedule construction, control
and program access not already included in complete query prices, the full
declared bill is `I+P+D+Q_min`. Packing computation belongs in D when needed;
an optimal packing is not a free runtime oracle.

This result supplies neither a physical reservation assignment nor an
actual selected producer/consumer. Nonlinear operations, finite-field
torsion, free output mixing, state-dependent prices, release of output
storage, coefficient traffic, native frames, precision, owned erasure,
stock, compiler closure and outer transfer need separate contracts. All five
selected framework assumptions remain. No kappa, selected-frontier update
or complete multiplication theorem follows. Independent human and formal
proof-kernel review are unclaimed.
