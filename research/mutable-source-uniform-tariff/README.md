# Global uniform tariff for the mutable-source connector

**Scoped theorem, no new multiplication bound.** In the generic five-source
common-B interface of PR1340 and PR1370, let every complete query and readout
cost the same `c > 0`, and every complete source XOR cost `x > 0`. Among **all
finite correct restored root words**, allowing arbitrary query counts, readout
counts and source-mutation counts, the exact schedule tariff is

\[
\boxed{\min\{72c+4x,\;74c\}.}
\]

Thus the known four-XOR word is optimal for `x <= c/2`; the known read-only
repairs are optimal for `x >= c/2`. At `x=c/2` both are optimal. This is a
statement about the minimum **value**, not uniqueness or a full `(Q,R,X)` Pareto
frontier. At PR1370's abstract five-factor tariff `c=38, x=2`, the global
minimum is **2744**, not just a minimum at fixed query/readout counts.

The new contribution is removal of that fixed-count restriction on the
**equal-Q/R-price slice**. Arham Tahir's [PR1370](https://github.com/CrocSwap/integer-mult-bounds/pull/1370)
already supplies the four-XOR construction and its sharp fixed-count theorem;
[PR1340](https://github.com/CrocSwap/integer-mult-bounds/pull/1340) supplies the
changed alphabet and the paired-readout query minimum. Ross Richardson's
[PR943](https://github.com/CrocSwap/integer-mult-bounds/pull/943) supplies the
read-only obstruction and repairs. Those are dependencies, not new inventions.

## Contract and complete-price boundary

There are five distinct dirty source rows `x_0,...,x_4`, 31 distinct dirty
outputs `y_m` for `1 <= m < 32`, a distinct dirty connector `z`, and distinct
private scratch. All rows have positive length `L >= 1` over F2 with arbitrary incoming
values. B is one common exact F2-linear map, and the A_m are arbitrary fixed
exact F2-linear maps; none need commute or be invertible. The allowed calls are

- `Q_j: z += B x_j`;
- `R_m: y_m += A_m z`;
- `X_(s,t): x_t += x_s`, `s != t`.

Each complete call preserves every other row, restores its private scratch,
returns its heads, and has additive behavior independent of its old target.
Sources and outputs cannot be observed externally during the batch. The
straight-line word is data-independent, and must realize, for **every**
admissible map and dirty input,

`y_m += A_m B(sum_j bit_j(m) x_j_initial)` for all 31 masks,

restoring every source, connector and scratch row. No other data operation,
extra connector, alias, direct AB call, unpriced copy or free combined query is
allowed. Common B and temporarily writable sources are changes from PR943's
read-only interface, explicitly inherited from PR1340.

For counts `(t,r,s)=(#Q,#R,#X)`, optimize exactly `c(t+r)+xs`. The prices include
all per-call obligations and dispatch. Shared, word-independent admission and
preparation `I+P` can be added to both sides. Unequal Q/R prices, port-dependent
routing, word-dependent preparation or residual program overhead, cross-call
fusion, alternative leaf lowerings and specialized maps are **not** covered.
A physical supplier must justify these complete prices; this theorem supplies
no such supplier or physical speedup.

## Proof over arbitrary finite words

### 1. Readout parity and pair capacity

Necessity can be tested at `L=1, B=A_m=identity` on independent incoming bits.
For any fixed `L>=1`, embed the same test in one coordinate using identity maps.
At any time the connector has the form `z_in + q dot x_in`, `q in F2^5`.
Source XORs and readouts do not change q. Every output's readout count is even,
to cancel its incoming-z coefficient, and at least two, to obtain its nonzero
target mask. Therefore `r >= 62` and r is even. This uses generic correctness;
zero or specially related maps cannot be used to avoid the lower bound.

With `t>0` queries, connector restoration makes a closed t-edge walk with at
most t distinct coefficient points: the final zero repeats the initial zero.
Let p be the number of outputs with exactly two reads. Their distinct nonzero
target masks must be differences of pairs of distinct points, so

`p <= min(31, binomial(t,2))`.

Every remaining output has at least four reads. Consequently

`r >= 124 - 2 min(31, binomial(t,2))`.                     (1)

Repeated points, repeated reads or intervening source mutations cannot increase
this capacity. For `t=0` no nonzero output is possible; the weaker bound in (1)
is harmless. For integers `0 <= t <= 8`, (1) gives `t+r >= 76` (the minimum is
at t=8). This is a necessary-count argument, **not** a claim that all allowed
count vectors are achievable.

### 2. The only at-most-72-map-call case

Write `n=t+r`. If `n<=72`, then `r>=62` gives `t<=10`. Section 1 excludes
`t<=8`. For t=9, even r and `n<=72` force `r=62`, so every output is paired.
PR1340's nine-point exclusion applies even with arbitrarily many source XORs:

A full difference cover containing zero must span F2^5. Choose five independent
members and apply an invertible linear map taking them to `1,2,4,8,16`.
For a nine-point set, its other three members are among the remaining 26
points. All `binomial(26,3)=2600` normalized sets have at most **29**, not 32,
differences, counting zero. Smaller sets either fail the span condition or can
be enlarged to nine without reducing coverage. The complete histogram is
`{22:60, 23:60, 24:810, 26:660, 28:750, 29:260}`.

Thus `n<=72` forces **t=10, r=62, n=72**. The following credited PR1370
fixed-count argument then forces **s>=4**; its finite dependencies are freshly
replayed here, not assumed from a pending PR's status.

The source-only projection must restore. Among all
`1+20+400+8000=8421` words of zero through three elementary source XORs, the
identity counts are `1,0,20,0`; each two-X identity repeats the same XOR.
Queries/readouts never modify a source, so this projection applies to every
interleaving, without a length bound on gaps.

With no X, ten restoring queries spanning all five directions use each basis
direction twice. With two X, rename their donor and target to 0 and 1. Let c_j
be the total queries to label j and p the queries to label 1 between the Xs.
Connector restoration is

`sum_j (c_j mod 2) e_j + (p mod 2) e_0 = 0`.

Because `sum c_j=10` is even, all c_j and p are even. Five-dimensional span
has only two possibilities: all five labels twice, with p=0 or 2; or donor
label 0 absent, target label 1 queried four times with p=2, and each other
label twice. Fewer labels cannot span five dimensions, since only label 1
can contribute a second direction. In either case the effective directions
are an independent basis, each used twice. The executable multiplicity check
corroborates this short classification; it is not a search over interleavings.

Renaming directions by first occurrence reduces to the **945** pairings of ten
positions. Their maximum difference coverage is **31**, not 32, by PR943's
complete obstruction. The histogram is
`{16:42,19:120,21:180,22:56,23:45,24:220,26:110,28:150,31:22}`.
Hence fewer than four Xs cannot realize this fixed-count case. Its price is
at least `72c+4x`.

### 3. The previously unbounded remaining counts

For `n=73`, even r makes t odd. With s=0, sources never change, and connector
restoration forces every query-label count even, contradicting odd t. With
s=1, a single nontrivial elementary source XOR cannot restore sources; Q/R
cannot undo it. Thus **s>=2**, independently of where the queries and readouts
are placed. The midpoint control below also attains this count bound.

The price in this case is at least

`73c+2x = ((72c+4x)+74c)/2 >= min(72c+4x,74c)`.

For **every n>=74**, however large, positive prices and s>=0 give price
`>=74c`. Sections 1–3 exhaust all finite n and prove the lower envelope. The
last implication is the reason no longer-word circuit search is needed.

### 4. Attainment and invoices

PR1370's closed path `0,4,5,1,3,7,6,14,28,16,0` covers all masks by differences.
Its edge masks 18 and 12 each use one source compute/query/uncompute pair;
all other edges are singleton queries. At lexicographically chosen two
boundaries for each mask, the two R calls cancel connector dirt. This yields
`(t,r,s)=(10,62,4)` and price `72c+4x`.

Both retained PR943 repair words work with the same common B: one has
`(12,62,0)`, the other `(10,64,0)`. Both cost `74c`. They are parsed from the
exact hash-pinned main certificate, not its older heterogeneous leaf invoices.
These witnesses attain the lower envelope and finish the proof.

A useful sharp positive control inserts boundary 24 into PR1370's path:
`0,4,5,1,3,7,6,14,28,24,16,0`. This splits its compound increment 12 into
singleton increments 4 and 8, retaining every old cover point. Only increment
18 still needs a compute/query/uncompute pair. The resulting word has
`(11,62,2)` and costs exactly the middle face `73c+2x`; at `x=c/2` it is another
optimum. This elementary adaptation is checked here, not attributed as an
invention of a new path mechanism. It also rejects the false extension of the
ten-query even-multiplicity conclusion to odd query counts.

For the five-factor fixture, each Q/R is separately lowered by the complete
balanced dirty echo, with inverse child words reversed literally. It executes
28 map leaves and nine internal nodes, plus one root dispatch. Thus c=38.
Each source XOR costs one complete row XOR plus one dispatch, so x=2. The
invoices reproduced here are:

| Credited witness | Q / R / X | Map leaves | Internal nodes | Root instructions | Tariff |
|---|---:|---:|---:|---:|---:|
| PR1370 four-X | 10 / 62 / 4 | 2016 | 648 | 76 | 2744 |
| PR1340 twelve-X | 10 / 62 / 12 | 2016 | 648 | 84 | 2760 |
| PR943 source repair | 12 / 62 / 0 | 2072 | 666 | 74 | 2812 |
| PR943 output repair | 10 / 64 / 0 | 2072 | 666 | 74 | 2812 |
| Split-edge midpoint control | 11 / 62 / 2 | 2044 | 657 | 75 | 2778 |

Four borrowed dirty rows (one root, three private) suffice for these literal
lowerings. Source XORs are counted separately from map leaves; their dispatch
is included in root instructions. Fixed shared admission/preparation is still
additional. No primitive-level or alternative-lowering optimality is claimed.

## Reproduction and evidence

From the repository root, Python 3.12, standard library only:

```sh
python3 -B scripts/research_package.py --package research/mutable-source-uniform-tariff
```

`verify.py` does not import any predecessor executable. It replays the three
finite exclusions by direct sets/row images, checks the two-X multiplicity
reduction and exact count/coefficient identities, and verifies all five root
words on the free noncommutative module of all 37 incoming data rows. It also
expands each five-factor word and checks all **40** incoming dirty rows,
including private scratch. Formal polynomial cancellation has an algebraic
interpretation for arbitrary exact maps and L; it is not just testing a
small random matrix. These executable checks accompany the written proof;
there is no proof-assistant claim.

`independent.py` was written by an isolated subagent without reading or importing
the primary implementation or predecessor executables. It uses integer Walsh
autocorrelation, endpoint matchings, source-column images and six-direction
multisets. It compares all substantive receipt fields, all five reconstructed
root words and invoices, then checks **7,400** forward/reversed full dirty-basis
executions plus **240** dense fixtures across two scalar and six noncommuting
binary-matrix banks at L=2,3,4. Its negative controls include a missing source
uncompute that leaves outputs correct but violates source restoration. These
matrix banks corroborate instantiated maps, not arbitrary matrices; the primary
free-module check and written algebra are the universal argument.

`INDEPENDENT.json` binds the independent results and Walsh records. The two
primary representation-specific record digests are only shape-checked by the
independent checker, not recomputed in the other representation. Histograms,
maxima, multiplicities, root words and prices are fully compared. The independent
checker validates root maps and invoice recurrences, **not** expanded primitive
lowerings. Its 38 CLI controls include strict type/duplicate-key/corruption tests
and relocated read-only inputs under normal and optimized Python. Test scratch
is outside the repository; both verifier defaults are read-only.

`RESULT.json` is deterministic. Normal commands compare it without writing.
An explicit `--write-receipt /outside/the/checkout/result.json` supports audit
regeneration. `SOURCES.json` binds the live main certificate and historical
assignment. Pending predecessor identities are in `PREDECESSORS.json`; no
pending package needs to be installed or executed. `VALIDATION.md` distinguishes
actually run checks from unrun obligations. `test_verify.py` covers semantic
mutations and source/receipt/relocation failures, including optimized Python.

## Scope and coordination

Base at scope selection: `410026dc5513b87db92ae98571d1d5984c69a983`; submission
was fast-forwarded to current main `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`.
The root guides, revision-2 catalogue, selected record, replay helper and pinned
live input were byte-identical across that update. The revision-2 selector
seed `a5233575a2c1e99c2506293e5c2388a4` selected recursive interfaces; it was not
rerolled. [TASK.json](TASK.json) records the refinement of
`connector-alphabet-change`, initial bounded plan, and overlap limitations.
The [scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18912472)
precedes implementation. Existing source-shear invention, four-X optimality
at fixed counts, DUO queries and second-root work were not treated as unoccupied
scopes. The selected record, frozen packages and predecessor files are unchanged.

## Open next questions

Unequal complete Q/R prices remain outside this theorem.
A useful first step is to identify a price ratio where a genuine competitor
escapes the 72/73/74-total-call argument before launching a new search. A
physical common-B supplier with temporary exclusive source access is also
unestablished: trace one real typed boundary and charge its actual ports,
routing, precision, admission, preparation and dispatch before adopting any
of these words. The structured questions and blockers are in TASK.json. Neither
question is a claim to additional work by this contribution.

No selected-supplier admission, selected cold replay, native owner/compiler or
precision/tape validation, formal multiplication proof, all-size outer transfer,
new moment, new kappa, maintainer approval or independent human review is claimed.

## Credit and license

Published for **tennisbowling <tennisbowling@tennisbowling.com>**. Entirely
prepared by an **OpenAI assistant and isolated subagents**, including the proof,
code, review and writing. Isolation is not independent human review.

Credit **Arham Tahir** (with disclosed OpenAI Codex assistance) for PR1340's
common-B mutable-source extension and PR1370's four-X witness/fixed-count theorem;
**Ross Richardson** for PR943/934's read-only obstruction, repairs and recursive
dirty lowering; **shhxera/CubeJerry** for PR889's common-factor batching; and
**Chafik Boukhalfa** for PR628's dirty commutator lineage. Douglas Colkitt and the
selected Rohan Arun/Jeremy Kothe construction's cumulative community attribution
remain unchanged. The path constants are attributed adaptations, not a new path
search. New material is Apache-2.0 under the repository LICENSE; retained input
and predecessor attribution are preserved.
