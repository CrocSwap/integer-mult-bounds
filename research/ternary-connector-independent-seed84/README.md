# The signed connector obstruction costs thirteen queries over F3

**Independent verification and a finite-characteristic construction. No new
kappa.** Ross Richardson's [PR944](https://github.com/CrocSwap/integer-mult-bounds/pull/944)
classifies 288 signed three-by-three connector patterns whose characteristic-zero
query minimum is fourteen. That theorem explicitly excludes finite
characteristic. A separate implementation shows that every one of these
patterns has minimum **thirteen over F3**. Every operator can carry the single
extra call, so the exact weighted optimum is

```
2 (c_A0 + c_A1 + c_A2 + c_B0 + c_B1 + c_B2) + min_F c_F.
```

Prices are positive complete-query charges, equal between signs and independent
of incoming data, at fixed ports. This is a minimum in the query alphabet below.
It does not change the characteristic-zero result or admit a supplier.

From the repository root, with Python 3.10+ and no third-party dependencies:

```sh
python3 -I -O -B research/ternary-connector-independent-seed84/verify.py
```

Expected output:

```
PASS_TERNARY_CONNECTOR_INDEPENDENT matrices=19683 obstructed_minimum=13 orbit_replays=1728 source_paths=5760 leaf_replays=12 controls=170
```

The deterministic receipt is [CERTIFICATE.json](CERTIFICATE.json). `--emit`
recomputes it and prints JSON without writing files. Exact base and eight source
hashes are in [SOURCES.json](SOURCES.json). Five source files are live inputs;
three selected-context hashes record historical base-commit provenance only.
The assignment seed is 84, from OS randomness. It selects orbit fixture 84,
not a stochastic search. All declared
domains are completed; the stopping rule is their exhaustion.

## Interface and relevance

Take distinct arbitrarily dirty arrays x0,x1,x2,y0,y1,y2,z over F3. The fixed
F3-linear maps A_i and B_j may be noncommuting, noninvertible, and of any common
array dimension. The only queries are

```
B_j^s: z   += s B_j x_j
A_i^s: y_i += s A_i z                 s in {-1,+1}.
```

Each complete query preserves its source and every other row, restores all
private scratch, and returns tape heads to their prescribed entry positions.
Its increment is independent of the old target. All seven arrays stay reserved
from child scratch. Outputs can be observed only at completion. The requested
map restores x and z and adds `sum_j M_ij A_i B_j x_j` to y_i. Negative queries
subtract an increment; they do not invert A_i or B_j.

The word can depend on M, but cannot branch on data. Additional root connectors,
combined queries, direct product calls, copies, role changes, frame changes and
other data operations are excluded. A specialized operator identity may permit
fewer queries; the minimum concerns uniform correctness for arbitrary maps and
inputs. F3 here is the exact field of three elements, not rounded arithmetic.

This checks the coefficient-field hypothesis of an existing recursive interface.
The historical ternary bit machinery makes that boundary worth recording, but
no implementation of its ports, layout or storage by that machinery is supplied.
The selected PR1094 result stays at conditional kappa
`836330098538459/500000000000000000`. Its complex moment remains binding in the
baseline check. The query saving is not propagated into that construction.

## Why the complete finite search suffices

Specialize all maps to scalar identities and keep the seven initial values
independent. Restoring z forces each B_j's signed occurrence count to be zero
modulo three. Canceling initial z in output i imposes the same condition on A_i.
Every active row and column needs its operator at least twice. Hence the support
lower bound is twice the number of active rows plus active columns.

At twelve calls on a full-support matrix, each of the six operators occurs
exactly twice, once with each sign. Project onto source calls. Every source word
is one permutation of the six distinct tokens B0-,B0+,B1-,B1+,B2-,B2+. There are
720. At a source boundary t write

```
z = z_initial + sum_j q_t[j] B_j x_j,       q_t in F3^3.
```

Two opposite reads of A_i give the row `q_a - q_b`. Conversely, when all rows
are differences of visited vertices, insert each positive/negative read at its
chosen boundaries. Different outputs do not interfere. This proves necessity
and sufficiency without assuming that the operators commute.

The verifier forms all ordered differences at every path, then the Cartesian
cube of those row sets. Across all 19,683 matrices over F3 it obtains 19,395
attainable patterns. The other 288 equal both the independently reconstructed
signed/permuted orbit of

```
M = [ 1  1  1 ]
    [ 1  1 -1 ]
    [ 1 -1  0 ].
```

and the predecessor's recorded obstruction set. Source comparison occurs only
after reconstruction. All 288 have full support. For a degenerate attainable
matrix, omit zero-row readouts and source queries in zero columns. Deleting
these source coordinates leaves every required row difference unchanged. Thus
the other 19,395 patterns attain their individual support lower bounds too.

At thirteen calls exactly one operator occurs three times and the other five
occur twice. The three signs must all agree, since only signed sums +3 and -3
vanish in F3. This exhausts the two cases:

- An A_i has three reads. The source path is one of the same 720 paths. Its row
  must be a signed sum of three visited vertices, with repetition allowed.
  Nondecreasing triples of boundary indices and both signs cover every ordering.
  The other two rows remain differences.
- A B_j occurs three times. Choose its common sign, three positions among seven,
  and a permutation of the four distinct remaining signed tokens. This gives
  `2 * binomial(7,3) * 4! = 1680` source words for each j, or 5040 overall.
  All three output rows must be differences of visited vertices.

No source path or readout class is sampled. The following counts are numbers
of feasible source paths for the canonical matrix, not numbers of full query
words:

| Tripled operator | A0 | A1 | A2 | B0 | B1 | B2 |
|---|---:|---:|---:|---:|---:|---:|
| Feasible source paths | 84 | 84 | 48 | 280 | 280 | 224 |

The certificate gives one full word for each column. Row permutations/signs
relabel or negate A calls; column permutations/signs do the same to B calls.
Applying these transformations produces six words for each of the 288 matrices.
A separate dense 7-by-7 row-operation interpreter checks all 1,728 words,
their occurrence counts, and their literal inverses. Within this fixed alphabet,
its scalar identity-map specialization is faithful to all coefficient equations:
the only possible added terms are A_i z_initial and A_i B_j x_j. Thus the written
lifting argument applies to arbitrary dimensions and noncommuting maps.

The twelve-call exclusion plus these words proves minimum thirteen. Every valid
word has at least two of each operator and at least one extra call, giving the
weighted lower bound `2 sum_F c_F + min_F c_F`. Because each operator has a
thirteen-call repair, placing the extra call on a cheapest operator attains it.
This conclusion does not require an even-length argument.

## Literal word and complete recursive bill

The canonical word that triples B0 is

```
B0- A1- A2+ B0- B1+ A0+ A2- B0- B2- A1+ B1- A0- B2+
```

It adds the displayed M and restores the connector over F3. Over the integers
or F5 it leaves `-3 B0 x0` in z, so reusing it there fails. For the A-tripled
words the uncanceled term instead includes `+3 A_i z_initial` or its negative.
These are concrete failed identities outside the field hypothesis, not
counterexamples to PR944's explicitly scoped theorem.

For application-order factor lists, retain the predecessor's balanced product
echo. Split F into right prefix R and left suffix L, borrow a fresh dirty row w,
and execute `R(x,w); L(w,y); inverse(R)(x,w); inverse(L)(w,y)`. The inverse of an
expanded word reverses its instructions and negates their signs. Every child
must satisfy the complete interface above. With disjoint private child pools,

```
C([f]) = c_f + dispatch_leaf
C(F)   = 2 C(R) + 2 C(L) + dispatch_node
h([f]) = 0;                 h(F) = 1 + max(h(R),h(L)).
```

At the root the bill is

```
I + sum_F P_F + 2 sum_F c_F + min_F c_F + D_root.
```

I pays role/layout admission, P_F pays coefficient preparation, and each c_F
includes every child, source/coefficient access, routing, frame adapter, private
restoration, head return and per-call dispatch. D_root pays word selection,
instruction storage and root control not already charged per query. The optimum
formula concerns query charges; different root costs need separate comparison.
No input-access volume or restoration cost is divided by the number of outputs.

For the retained factor lengths `B0,B1,B2,A0,A1,A2 = 2,3,4,5,6,7`, unit leaf
prices under balanced lowering are `4,10,16,28,40,52`. The six full expansions
have leaf counts `304,310,316,328,340,352` in that order. Tripling B0 attains 304,
compared with the predecessor's 308-call characteristic-zero word on those same
factor lengths. This compares exact operation invoices in different coefficient
fields, not measured runtimes. The root connector plus three reusable private
rows requires four dirty rows, ten mutable rows including all sources and
outputs. No clean row is assumed. Controllers, coefficients and scalar registers
require additional storage and work.

A sparse free noncommutative module interpreter checks the entire leaf words
for all six canonical repairs and all six repairs of seed fixture 84. Every
initial data and private-dirt symbol remains independent, and product factors
retain their order. These twelve checks verify identities and restoration at
the abstract leaf interface; they are not a physical tape or compiler replay.

## Evidence, independence and limits

The verifier imports no predecessor executable code. It reconstructs the source
domain from signed-token permutations and compares the predecessor receipt only
after computing its own missing set. Query-word checking uses dense matrices;
leaf checking uses sparse noncommutative expressions. These are independent
representations, but share the stated query interface and finite-reduction proof.
There is no independent human review or proof-assistant formalization claim.

The 170 embedded negative controls include all 78 single-query omissions, all
78 sign flips, six integer-field failures, six F5 failures, one omitted leaf,
and one deliberately reversed factor chain. All are checked with explicit
exceptions, including under optimized Python. Source hashes, full path trace
digests, canonical words and the missing-set digest are compared to the receipt.
External package checks and environment details are in [VALIDATION.md](VALIDATION.md).

No full selected cold replay, physical supplier admission, machine runtime
benchmark or full multiplication proof is supplied. All existing selected
all-size/compiler, common-label/mutable-source, hosting, precision/tape, analytic
and bit-interface assumptions remain unchanged. Finite replay is not a formal
proof of that theorem.

## Open next questions

- Can an active F3 supplier expose these exact six fixed ports and complete
  child interfaces? Start by mapping one thirteen-call word into an existing
  supplier, then price source access, frames, restoration and root control.
  No such caller is included here.
- Does a larger ternary connector family admit similarly sharp extra-call
  prices? Start with one four-source full-support matrix and derive a complete
  short-word reduction before increasing the search. The 3-by-3 classification
  does not establish that claim.
- A proof-assistant version could certify the two finite reductions and literal
  F3 words. The present proof and Python receipt do not discharge that obligation.

## Credit and license

Prepared by Sagar Thakrar (@thakrarsagar), with substantial OpenAI Codex
assistance in research, implementation, verification and writing. New material
is under the repository's Apache-2.0 license. No predecessor source is modified.

Ross Richardson's PR944 supplies the exact interface, obstruction orbit,
characteristic-zero result and literal recursive cost model. His PR934 supplies
the binary connector predecessor. @martinxxx9's
[PR1088](https://github.com/CrocSwap/integer-mult-bounds/pull/1088) supplies the
six-operator weighted characteristic-zero repair and motivates checking all six
operators here. Its formula remains distinct, with `2 min_F c_F` in place of
`min_F c_F`. PR889 by CubeJerry supplies the signed fanout contract; Chafik
Boukhalfa's PR628 supplies the dirty product commutator and literal inverse
convention. Their retained notices and the wider selected construction's
attribution remain authoritative. This package claims no priority for modular
cancellation, commutators or exhaustive finite scheduling.
