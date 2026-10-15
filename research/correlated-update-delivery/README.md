# Correlated source updates remove connector repairs under delivery cuts

**Exact declared-query optimum and source-bound local construction; no new
supplier or kappa.** PR1780 prices a persistent dirty connector when successive
source updates have independent inputs. Known dependencies change that optimum:
repairs can cancel at the final boundary even though the connector is not
coherent with the current source at intermediate deliveries.

For four requests using the retained PR1439/PR1780 maps, one repeatedly used
update row gives **59 scalar XORs**, versus **63** for the best coherent
persistent schedule and **87** for separately closed requests. Every imposed
source update and every output delivery remains present. The four-request word
uses the absolute minimum of one source query and two reader queries per
request, with **zero correction queries**, for any positive complete tariffs.
This is not just a different state representation of an unchanged recurrence.

The contribution is an arbitrary-length theorem for a **known binary update
dependence matrix**, with an attaining word and an independent unrestricted-query
oracle. It does not assert that independent dirty updates are dependent. No
admitted selected-supplier caller with these dependencies is identified.
Opening the pilot's fixed maps permits direct product fusion in **31 XORs**;
that cheaper legal comparator explicitly prevents an unrestricted circuit or
physical speedup claim.

## Exact contract

Work over F2, coordinatewise for arbitrary stream lengths. There are distinct,
arbitrarily dirty source `x`, connector `z`, read-only update rows
`u_0,...,u_(d-1)`, and outputs `y_1,...,y_k`. The update rows are independent;
**their prescribed uses** may be dependent. Let `U v` mean the XOR of update
rows selected by the known vector `v in F2^d`. Fixed maps `C`, `B`, `A_i` are
compatible linear maps; no commutativity or invertibility is assumed. Set

```
s_1 = 0,     s_i = v_1 + ... + v_(i-1),
x_i = x_0 + C U s_i.
```

Request i must deliver `y_i += A_i B x_i`. Its output cannot be written before
its request or after delivery, and request intervals do not overlap. The only
permitted data operations are complete calls:

- `B_i: z += B x_i`, inside request i, price `b_i > 0`;
- `A_i: y_i += A_i z`, inside request i, price `a_i > 0`;
- the mandatory update `M_i: x += C U v_i` after delivery i, price `m_i`;
- `D_i: z += B C U v_i`, only at that update cut and before the next request,
  price `d_i > 0`.

Arbitrary numbers and orders of A/B queries are allowed inside requests, and
arbitrary numbers of D queries at their cuts. The connector is hidden and
reserved through the batch and must return to its arbitrary initial value.
Update rows are never written. The final source has the imposed cumulative
update; source restoration is **not** silently required or claimed. Each complete
query's fixed tariff includes its scratch restoration, access, frame/routing,
head returns and dispatch for the chosen implementation. No source mixing,
combined query, output cross-write, extra connector, free copy or changed frame
is in this alphabet.

This is a universal-word optimum for these maps: the word must be valid for
all compatible A/B/C and dirty inputs, and each named query has a fixed price.
For a specially degenerate fixed map, such as `A_i B=0`, a cheaper word may
exist. The concrete nondegenerate pilot below also has the stated sharp optimum.

## Exact theorem and proof

Choose query and correction parities `q_i,t_j in F2`. Define the feasible set
by the **two final restoration conditions**

```
XOR_i q_i = 0,
XOR_i (q_i s_i) XOR XOR_j (t_j v_j) = 0 in F2^d.             (1)
```

The exact query price is

```
Q = 2 sum_i a_i + min_(q,t satisfying (1))
        [ sum_i b_i (2-q_i) + sum_j d_j t_j ].              (2)
```

Add all mandatory `sum_j m_j` and the caller's actual admission, reserved
storage/lifetime, coefficient/program preparation and any other costs outside
the complete tariffs. These additions need not be equal for different physical
callers; the theorem does not waive them or infer a recursive rank invoice.

### Lower bound without a two-read or coherent-state assumption

Specialize the universal word to scalar identity maps with independent bits
`x_0,u_0,...,u_(d-1),z_0`. Let `n_i` count B queries, `r_i` count A queries,
and `h_j` count D queries.

1. Only A_i can change output i. Every read carries the same incoming `z_0`
   coefficient one, so `r_i` is even. It cannot be zero because the requested
   output has coefficient one on `x_0`. Therefore `r_i >= 2`.
2. If no B query occurs during request i, the connector coefficient of `x_0`
   is constant throughout that request. Even arbitrarily many A reads cancel
   it. D queries have no `x_0` coefficient (and here occur only between
   requests). Thus `n_i >= 1`.
3. Write `q_i=n_i mod 2`, `t_j=h_j mod 2`. Final connector restoration, using
   independent `x_0` and update bits, gives exactly (1). Positivity gives
   `n_i >= 2-q_i`, `h_j >= t_j`. This proves (2) as a lower bound for **every**
   allowed word, including extra/interleaved readouts and incoherent states.

Scalar specialization proves necessity for a universal word, not necessity
for each zero or singular fixed instance. It makes no unsupported claim that
finite checks establish the unbounded theorem.

### Attainment for arbitrary compatible maps

For every feasible q/t, execute chronologically in request i:

```
A_i; B_i; A_i; [B_i if q_i=0]; deliver i;
[M_i; D_i if t_i=1] at a nonfinal cut.
```

The two reads differ by exactly `A_i B x_i`, whatever dirt or stale offset is
carried in z. No map order is exchanged. The final connector change is

```
B ((XOR_i q_i) x_0 + C U (XOR_i q_i s_i + XOR_j t_j v_j)),
```

which vanishes by (1). Every source update occurs once; update inputs are
untouched; no future or delivered output is written. The word attains every
term of (2), proving the exact result for every k, d and stream length.

### Computation and the independent-update specialization

A connector boundary is represented relative to the **initial** source by
`z=z_0+p B x_0+B C U h`. Start `(p,h)=(0,0)`. Choosing q_i toggles
`(p,h)` by `q_i(1,s_i)` at cost `b_i(2-q_i)`; choosing t_j toggles it by
`t_j(0,v_j)` at cost `d_j t_j`. End at `(0,0)` and add `2 sum a_i`.
There are at most `2^(d+1)` states; the numeric recurrence needs
`O(k 2^d)` arithmetic operations. The reference implementation also stores
path tuples for deterministic witnesses and does not claim that bound for
its tuple copying or arbitrary-precision bit complexity.

If `v_j=e_j` are independent, (1) forces
`t_j=XOR_(i>j) q_i=XOR_(i<=j) q_i`. Substituting cumulative parity `p_j`
recovers PR1780's exact two-state formula. That predecessor remains correct
under its stated independent-input hypothesis. If all `v_j=1`, however, only
one aggregate update equation remains; requiring every intermediate repair
is stronger than final restoration plus the actual delivery contract.

## Literal repeated-row pilot and full local bill

Reuse PR1439/PR1780's maps, written as row bitmasks:

```
B = (3,6,7),    C = (1,0,0),
A_1=A_3=(2,4,1),    A_2=A_4=(3,2,4),
v_1=v_2=v_3=1.
```

Thus `x_1,x_2,x_3,x_4` are `x_0,x_0+Cu,x_0,x_0+Cu`.
Take `q=(1,1,1,1)`, `t=(0,0,0)`. After each request, the connector is

| Delivered request | Connector |
|---|---|
| 1 | `z_0+B x_0` |
| 2 | `z_0+B C u` |
| 3 | `z_0+B x_0+B C u` |
| 4 | `z_0` |

The stale offset at request 2 is legal: the paired reads cancel it. Both
`A_i B` and `B C` are nonzero, so the same dirty-parity and missing-source
arguments apply to these fixed maps, not just to the universal family. No
word in the stated alphabet can use fewer than four B and eight A calls.
Our word reaches those componentwise floors with no D calls, so it is optimal
for **any positive fixed complete prices** on this four-request instance.

Each matrix one is one scalar XOR. Prices are `b_i=7`, alternating `a_i=3,4`,
`d_j=2`, and `m_j=1`. The coherent comparator minimizes over all open/closed
choices; it is not the weak baseline of four individually closed calls.

| Charged work | Correlated | Best coherent | Separately closed |
|---|---:|---:|---:|
| B calls / scalar XORs | 4 / 28 | 4 / 28 | 8 / 56 |
| A calls / scalar XORs | 8 / 28 | 8 / 28 | 8 / 28 |
| D calls / scalar XORs | 0 / 0 | 2 / 4 | 0 / 0 |
| Mandatory mutations / XORs | 3 / 3 | 3 / 3 | 3 / 3 |
| Total XORs, writes and instruction records | **59** | **63** | **87** |
| Data reads | 118 | 126 | 174 |
| Return-to-origin head steps | 1,128 | 1,176 | 1,472 |
| Unit local backend total (head + five units/gate) | 1,423 | 1,491 | 1,907 |

All three programs use the same **19 data bits**: three source, one update,
three arbitrary dirty connector, and twelve arbitrary dirty output bits. No
clean full row or extra ancilla is introduced. The literal source-target-origin
head walk uses consecutive one-based addresses, returning to zero after every
XOR; its cost is `2 max(source_address,target_address)`. The receipt retains
the actual word, all delivery offsets, all 19 formal endpoint columns, and the
separately recomputed movement bill. `unit_backend_total` adds those movements
to five units per gate (two reads, one write, one XOR, one dispatch). A common
fixed one-bit latch admission, if needed, is not an additional saving. The
program is a compiled constant; general coefficient/plan preparation is not
being hidden inside these fixed-fixture counts.

This is a declared finite local backend, not a native fixed-tape supplier
implementation or measured runtime. Directly compiling `A_i B` gives **31**
XORs including all mutations, with the same delivery policy and exact endpoint.
The optimum above must therefore remain explicitly restricted to indivisible
queries. The common connector lineage and fixed-query research model are the
source of the candidate, not evidence of a selected physical occurrence.

For every `k=0 mod 4`, the same repeated-row pattern permits one B and two A
calls per request with no D correction. More generally, forbidding corrections
requires an even number of odd-query choices separately in the two source
states, so the exact B count is
`k + (ceil(k/2) mod 2) + (floor(k/2) mod 2)`.
This is a written unbounded corollary, not an extrapolation from the 24 checked
examples. The k=0 case is the empty word; the general theorem assumes k>=1.

## Evidence and reproduction

Python 3.12, standard library only; from the repository root:

```sh
uv run --python 3.12 --no-project python -I -O -B research/correlated-update-delivery/verify.py
uv run --python 3.12 --no-project python -I -O -B research/correlated-update-delivery/test_package.py
uv run --python 3.12 --no-project python scripts/research_package.py --package research/correlated-update-delivery
```

The verifier reconstructs [RESULT.json](RESULT.json) read-only and checks:

- all **300** cases with d=1,2, k=1..4, every update vector sequence, and three
  fixed positive tariffs including exact fractions;
- a separately implemented Dijkstra oracle on literal connector and current
  output coefficient vectors, including incoming connector dirt and arbitrary
  A/B/D multiplicities; a third exhaustive parity enumeration agrees as well;
- all 300 attaining words at every delivery, update-coordinate renaming,
  16 independent-update specializations and 24 periodic examples;
- **4,096** triples of arbitrary two-by-two B/C/reader matrices, including
  singular and noncommuting maps, on all **16** dirty input columns per case;
- all **19** basis columns of each real pilot word and **384** exhaustive
  dirty scalar-identity executions (128 states for each of three words);
- eleven semantic controls: falsely independent last update, omitted final
  query, omitted old-dirt read, future/late writes, omitted mutation, omitted
  repair, repair moved past its cut, an underpriced invoice, negative tariff,
  and an unregistered update coordinate.

The observed census has **72** strict savings over its coherent comparator.
The independent Dijkstra settles **21,070** states; the canonical row digest
is retained in the receipt. These are checks of a finite domain, not the proof
of the arbitrary-length claim. The actual pilot maps are parsed from the pinned
PR1780 note before lowering; no predecessor solver is imported.

The five package controls exercise optimized execution in a relocated source
export from an unrelated directory, source drift, a corrupted undercharged
receipt, refusal to overwrite an occupied output, and canonical regenerated
payload equality. Checks use explicit exceptions and remain active with `-O`.
`--write-result NEW_PATH` generates evidence exclusively into a new path.
The independent implementations are by the same assisted author, not
independent human review. No full repository suite or CI investigation is part
of this package. The selected cold replay is not required for, or supplied by,
this non-supplier theorem.

Observed local validation: CPython **3.12.12**, Darwin arm64, through uv.
The optimized focused evidence command passed, followed by the registered
replay, including all semantic and five file/portability controls. No hosted
CI status or selected supplier cold replay is claimed.

## Scope, provenance and credit

The one OS-random draw is retained in full in [SELECTION.json](SELECTION.json):
seed `829a355b1cafac3569bc060e0062cf20`, recursive-interfaces, revision 3,
base `e112d71c8d7bb32435debcc54df932593dd8223a`. The pre-computation
[TASK.json](TASK.json) declares the changed independence premise, all costs,
stopping domain and limits. [SOURCES.json](SOURCES.json) binds actual local
predecessor bytes by SHA256 and Git blob at that base; the registered replay
also checks historical task/selected provenance. No predecessor executable is
imported. The selected record remains
`836330098538459/500000000000000000`, complex-binding.

Credit **Ross Richardson** for PR1780, exact head
`15a91b5d634023a3a14129cbb240854c4b188111`, and PR934/943's dirty-connector
lineage; **woklerx** for PR1439 (`3852c2d03044895cebdc9b31b0c7131a617774d2`)
and PR1442 (`7c573bc769798ce4e336fd5be630060bd9d69a71`), their mutable-source
identity, exact delivery-cut lower bounds and literal pilot; **Hanson Sun** for
`observable-connector-repair`, which uses a repeated update row but fixes two B
queries and permits future-output prewrites. Its quotient-repair optimizer does
not cover the present online output cuts and arbitrary source-query count.
No priority is claimed for dirty cancellation, binary codes or shortest paths.

Entry overlap used the shared complete snapshot of 329 open PRs (including
drafts, 2026-10-14T18:11:09Z) and 692 discussions including comments/replies
(18:12:32Z), local packages and merged predecessors. Targeted live PR1780 and
PR1439 heads were checked; both are merged. Exact dependency/repeated-update
searches found PR1780's independent scope, not this result. This is not a
novelty certificate and does not cover every diff. The advisory claim is
[Discussion2049, comment18931231](https://github.com/CrocSwap/integer-mult-bounds/discussions/2049#discussioncomment-18931231).

Prepared for **Adam Gall (@adamgall)** with substantial **OpenAI Codex
(GPT-6 Astra)** assistance in algebra, implementation, exact checks and prose.
New material is **Apache-2.0**, under the repository LICENSE. No formal-kernel,
independent human, hosted-CI, all-size compiler, common-label/hosting, precision,
physical tape, contracting recurrence or multiplication-exponent claim is made.

## Open next questions

Does a real admitted caller supply this known update-dependence matrix while
keeping individual output deliveries and a hidden reserved connector? Extract
its complete port-specific A/B/D tariffs, mutation relation and frame/owner
lifetimes, then price the emitted optimum against an equally fused baseline.
The absence of that caller and its routing/precision/tape obligations, not a
missing local query optimum, blocks adoption. See the structured question in
[TASK.json](TASK.json). Extending a toy finite search alone would not resolve it.
