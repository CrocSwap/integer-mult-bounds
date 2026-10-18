# Eight source XORs are necessary at the six-query endpoint

**Scoped exact obstruction; no new multiplication bound.** In the five-source
common-B mutable-source connector of Arham Tahir's [PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898),
every correct restored word with exactly six queries needs **at least eight
source XORs**, even if its readout count is unrestricted. The predecessor's
`6 Q / 96 R / 8 X` construction therefore has the exact minimum complete-call
tariff **`6b + 96a + 8x` among six-query words**, for positive uniform prices.
At its abstract `(b,a,x)=(38,2,2)` tariff the optimum is 436.

PR1898 already proves the minimum six-query count, the minimum 96 readouts at
that count, and supplies the eight-XOR construction. Its README and
[Discussion 1579](https://github.com/CrocSwap/integer-mult-bounds/discussions/1579)
explicitly leave XOR optimality open. This package closes that one obligation.
It does not improve the attained word or determine the global unequal-price
optimum over other query counts.

## Contract and priced boundary

Retain five distinct arbitrary dirty F2 source rows `x_0,...,x_4`, 31 distinct
arbitrary dirty output rows `y_m` (one per nonzero five-bit mask), a distinct
dirty connector `z`, and private scratch. B is a common exact linear map and
each A_m is an arbitrary exact linear map; neither invertibility nor commuting
maps is assumed. The only complete calls are

- `Q_j: z += B x_j`;
- `R_m: y_m += A_m z`;
- `X_(s,t): x_t += x_s`, with distinct s,t.

The target is `y_m += A_m B(sum_j bit_j(m) x_j_initial)`, with every source,
connector and private scratch row restored. Calls preserve other rows, restore
private scratch, return heads, and behave additively independently of their old
targets. Straight-line words are data independent. Source/output observation
before exit, extra root connectors, clean full rows, output mixing, direct AB
calls, free copies, source-specific B maps and other data operations are excluded.

The paid source-XOR alphabet is inherited from PR1340; it is the changed
premise relative to PR943's read-only alphabet. This result refines an existing
extension rather than inventing another operation. Every X costs x. Complete
prices b,a,x must include actual ports, source/coefficient access, restoration,
head returns, frames, precision and dispatch. Shared admission/preparation and
any residual word-dependent program cost must be added separately. No physical
implementation with these prices or selected-supplier adoption is asserted.

## Reduction to connected restored shear words

Specialize generic correctness to length one and identity A_m and B, with all
incoming bits independent. At all times, each source is a row of an invertible
5-by-5 binary matrix applied to the original sources. The X-only projection
must end at the identity, because Q and R never change sources.

Build the undirected **interaction graph** on source labels: every X_(s,t)
adds edge {s,t}. This graph records every used edge, including ones whose
matrix effects later cancel. If it has c components C_i of sizes n_i, each
query increment belongs to the coordinate subspace on its source's component.
Let t_i count those queries. All source frames stay block diagonal across
these components. Connector restoration says that the sum of increments in
each component is zero. Their rank is consequently at most t_i-1 whenever
the component is queried.

All five singleton output masks must lie in the span of query increments:
readouts only combine connector prefixes. Thus the increments in C_i span
dimension n_i; every component is queried and `t_i >= n_i+1`. Summing gives

    number of Q calls >= 5 + c.

Exactly six Q therefore forces **c=1**. This proof permits arbitrarily many
readouts, arbitrary X interleavings, and all exact admissible maps through the
generic scalar specialization. It does not require paired readouts.

It remains to exclude connected interaction graphs among all restored source
words of X-length at most seven. There are exactly 20 directed elementary
shears X_(s,t) on five sources. The following finite census exhausts this domain.

## Exhaustive finite exclusion

For every half-length k=0,...,4, compute every possible pair
`(source matrix, all-used-edge graph)`. The initial pair is `(I, empty)`.
Extending by X_(s,t) XORs matrix row s into row t and unions edge {s,t} into
the graph. Retaining all different graphs for each matrix is essential:
the endpoint matrix alone forgets cancelled interactions. Induction on k
proves that this state recurrence includes every word and no fictitious state.

For a full length l<=7 split at `a=floor(l/2)`, `b=ceil(l/2)`.
Every generator is its own inverse. Thus a word `u reverse(v)` restores
sources exactly when `M(u)=M(v)`; its interaction graph is `G(u) union G(v)`.
Joining equal matrices in half-layers a and b therefore enumerates every
possible restored interaction graph of length l. No heuristic pruning,
symmetry quotient or sampled source state is used.

| Half-length | Raw words | Distinct matrices | Matrix/graph states |
|---:|---:|---:|---:|
| 0 | 1 | 1 | 1 |
| 1 | 20 | 20 | 20 |
| 2 | 400 | 261 | 270 |
| 3 | 8,000 | 2,770 | 3,130 |
| 4 | 160,000 | 22,401 | 32,595 |

| Full X-length | Restored graphs | Connected restored graphs | Fewest components |
|---:|---:|---:|---:|
| 0 | 1 | 0 | 5 |
| 1 | 0 | 0 | none |
| 2 | 10 | 0 | 4 |
| 3 | 0 | 0 | none |
| 4 | 55 | 0 | 3 |
| 5 | 10 | 0 | 3 |
| 6 | 175 | 0 | 2 |
| 7 | 80 | 0 | 2 |

The finite exclusion plus the component lemma proves X>=8 at six queries.
This is a complete computational certificate in the specified finite source
model, accompanied by a reduction from unbounded readout interleavings. It is
not a proof-assistant theorem or an all-source-count connected-word theorem.
Odd restored source words do exist (lengths five and seven appear above), so
source-XOR parity cannot replace this exclusion.

## Attainment and completed six-query tariff

Reconstruct PR1898's word: query the original sources in order, giving the
six prefix points `0,1,3,7,15,31`. At each point read each output belonging to
its unique even-subset representation. XOR sources 1,...,4 into x0, query x0,
then undo those four XORs in reverse order. Common-B linearity restores z;
the compute/uncompute restores every source. Every output's even number of
reads cancels dirty z and realizes its target.

The 31 nonzero masks correspond to the nonempty even subsets of the six
affinely independent prefix points. Each point occurs in 16 subsets, giving
96 total readouts. This is the predecessor's readout lower bound as well as
its attained count; extra occurrences cannot reduce any subset's cardinality.
The known word simultaneously attains Q=6, R=96 and X=8. Positivity of a and
x therefore proves the displayed exact fixed-Q tariff. This strengthens its
optimality status without changing the predecessor's invoice or construction.

## Reproduce and verification limits

Python 3.12+, standard library, from the repository root:

```sh
python3 -I -B scripts/research_package.py --package research/mutable-source-six-query-xor
```

The default commands are read-only. `verify.py` replays the exact census and
checks all formal incoming rows of the known word and its reversed inverse
in a free noncommutative operator module. It matches predecessor prefix/readout
data and live source hashes. `check_columns.py` imports no primary code:
it directly enumerates all 168,421 half-words using column images, builds
graphs as edge sets, and independently joins equal matrices and traverses
components. It agrees on every restored-graph count/digest and every layer's
matrix/state count. Its 900 dense executions cover all dirty basis inputs
and mixed states, both orientations, at dimensions 1,2,3 with two banks each.
The dense fixtures are corroboration; the formal replay and written algebra
supply the arbitrary-map argument. Both implementations were written by the
same assisted contributor, not independently reviewed by a human.

Controls distinguish a connected nonrestored four-X word from a restored
disconnected two-X word, and accept the connected restored eight-X witness.
They reject missing readouts, omitted source work, and a missing final source
uncompute that leaves every output correct. CLI checks cover receipt corruption,
source drift, optimized Python and relocation. [RESULT.json](RESULT.json)
contains all census digests and the literal root witness.

The exact entry base is `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision
4, selected conditional kappa `0.001672660197076918`.
[SOURCES.json](SOURCES.json) records Git blobs and SHA256 source pins.
[TASK.json](TASK.json) records the assignment/refinement and checkpoint;
[OVERLAP.json](OVERLAP.json) records live-search coverage and nearest work.
The guides and selected record are provenance, not modified scientific inputs.
No selected cold replay, native compiler/owner/hosting, precision/tape or
all-size outer admission, new moment/kappa, or global unequal-price optimum
is claimed. This result does not alter frozen predecessor packages.

## Open next questions

1. Bound attainable R/X bills at seven, eight and nine queries for one explicit
   unequal complete-price ratio. This would identify which intermediate words
   can beat the now-sharp six-query endpoint. First use the ratio to bound
   candidate counts; current endpoint optimality gives no global answer.
2. Determine whether a general connected restored source-shear word on n
   labels requires `2(n-1)` XORs. The present finite five-label census does
   not prove it. Start with a proof that handles overlapping interactions and
   odd-length identities; a graph edge-count or parity argument alone is
   insufficient. An all-n result would settle PR1898's entire minimum-query
   XOR question, while physical common-B source access would remain separate.

## Credit and license

Prepared for **ywz65**, with substantial **OpenAI Codex assistance** in proof,
implementation, checking and writing. No independent human review is claimed.
Credit **Arham Tahir** for PR1898's endpoint construction and explicit handoff,
PR1340's mutable-source alphabet, and PR1370's ten-query source-XOR theorem;
**TennisBowling** for PR1524's equal-price theorem/unequal-price handoff;
**Ross Richardson** for PR943/934's prefix framework and read-only repairs;
**shhxera/CubeJerry** and **Chafik Boukhalfa** for the inherited batching and
dirty-commutator lineage. PR1898 is pinned at
`5eb741129477f627f79ca5dc7d7d9eeabded1bed`; its retained main files are unchanged.
The selected construction's cumulative contributor credit remains intact.
New material is Apache-2.0 under the repository LICENSE.
