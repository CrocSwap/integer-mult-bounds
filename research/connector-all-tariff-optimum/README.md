# All positive tariffs for the five-source dirty connector

**Exact abstract interface optimum and complete call-profile frontier; no new
supplier or kappa.** For the generic immutable-source connector below, let
`b_j > 0` be the five complete source-call prices and `a_m > 0` the 31 complete
readout prices. They are independent, not required to be equal or integral.
Define

```
H = {7,11,13,14,19,21,22,25,26,28,31},
    the five-bit masks of weight three or five.

OPT(b,a) = 2 sum_j b_j + 2 sum_(m=1..31) a_m
           + 2 min({b_0,...,b_4} union {a_m : m in H}).
```

This is the optimum over **all finite legal words**, with no query-count or
readout-count cutoff. Exactly **16 componentwise minimal call-count vectors**
exist: start with two uses of every map, and add two uses of one of the five
sources or one of the eleven readouts in H. Every vector has an explicit
74-call attaining word in [RESULT.json](RESULT.json). Every vector is uniquely
optimal for some strictly positive price vector.

Cheap readouts for masks of weight one, two or four cannot absorb the necessary
surcharge on their own. For example, take every price to be 10 except `a_3=1`.
The optimum is **722**, not the naive `2 sum(prices)+2 min(prices)=704`.
Changing the cheap output to `a_31=1` makes **704 attainable**. The old PR1770
fixture `(b_0,...,b_4)=(1,4,10,16,28)`, all `a_m=1`, still has optimum 182.

## Exact interface and what is new

Reuse Ross Richardson's [PR943/PR934 contract](../universal-connector-boundary/README.md).
There are five distinct immutable length-L source rows `x_j`, a dirty connector
`z`, and 31 distinct dirty output rows `y_m`. For arbitrary fixed F2-linear
maps `B_j,A_m`, the requested map is

```
y_m += A_m sum_(j in m) B_j x_j;    x_j and z unchanged.
```

The only complete operations are `B_j: z += B_j x_j` and
`A_m: y_m += A_m z`. Maps may be singular or noncommuting. Each operation
preserves other rows and restores its private scratch and agreed head positions.
All public rows are excluded from private scratch. The straight-line word may
depend on the prices and masks, not on data or special relations between maps;
it must work for every admissible map assignment. Intermediate outputs are not
observed. There are no source mutations, extra connectors, frame changes,
combined queries, direct products, output mixing, overwrites or free copies.

PR1770 by Cinna Davis proves the 182 optimum at the one price vector above;
PR1811 proves the ten-toggle obstruction for the odd parity-hyperplane output
family. Those are credited ingredients, not new results here. The contribution
is the **complete 36-variable tariff theorem**, its irredundant Pareto frontier,
and witnesses for every exposed region. It also proves that no longer legal
word can improve a positive-price optimum. This is not merely a larger search
range or the old 74-query bound with prices attached.

The emitted card was `connector-alphabet-change`. [TASK.json](TASK.json) declares
**scope_status=changed**: no alphabet extension is made, so this is not a
successful new-operation mechanism under that card's original acceptance gate.
It is an exact caller-tariff oracle, useful before assuming that an expensive
operator must be repeated. No selected-supplier caller is supplied.

## Proof of the unrestricted optimum

### 1. Every active operator occurs an even number of times, at least twice

Specialize to L=1 and all maps equal to identity, with independently arbitrary
source bits and connector dirt. Restoring z forces each B count even. Removing
the initial connector bit from each output forces that A count even. A missing
source cannot produce its singleton output; a missing output map cannot update
that target. Thus every count is at least two. This is a necessary condition
for the generic contract; it need not hold for specialized zero operators.

Let `v0=(2,...,2)` in the order `B0..B4,A1..A31`.

### 2. Twelve or more source events are componentwise dominated

The total source count is even. If it is at least twelve, some source j has
count at least four. The complete count vector therefore dominates
`v0+2e_Bj`. Richardson's twelve-event universal path, relabeled to repeat j,
attains exactly that vector, with every readout used twice. In particular,
there is an attaining word costing the base bill plus twice the cheapest B.

This is a componentwise argument, not a cutoff justified by sampled prices.
It covers arbitrarily many source and readout events, including words which
repeat several different cheap operators.

### 3. Ten source events always miss a heavy odd mask

If there are ten source events, each source occurs twice. Write q_t for the
parity mask of sources inserted by boundary t. Two readouts at boundaries s,t
cancel arbitrary connector dirt and contribute exactly `q_s XOR q_t`.
Consequently a row outside

```
D(w) = {q_s XOR q_t : s,t are source boundaries}
```

needs at least four readouts (counts remain even). Interleaving other outputs
does not change these prefixes or repair that row because outputs are distinct
and are never read as sources.

The inherited odd-family obstruction is re-established independently here:
every ten-event paired source path misses a mask in H. It suffices to check
**945 canonical pairings of ten positions**. Pair the first unpaired position
with each possible later position, then recurse; the count is
`9*7*5*3*1=945`. Label each pair by order of its first occurrence. Every labeled
word is a unique canonical word followed by one of 5! coordinate permutations.
Permutations preserve H, so this proves coverage of all 113,400 labeled words.
Every weight-one mask is already a difference across a source event. Therefore
missing an odd mask means missing a weight-three or weight-five mask.

The exact census is:

| Missing masks in H | Canonical paths |
| ---: | ---: |
| 1 | 22 |
| 2 | 170 |
| 3 | 90 |
| 4 | 255 |
| 5 | 166 |
| 6 | 180 |
| 7 | 20 |
| 8 | 40 |
| 11 | 2 |

There is no zero-missing case. Thus every ten-event word's complete count
vector dominates `v0+2e_Am` for some m in H. This is the only finite exclusion
used in the unbounded theorem, not an extrapolation from a length-limited search.
The enumeration is exact but is not a proof-assistant certificate.

### 4. All eleven output surcharge vectors are attained

These two ten-event words have precisely one missing nonzero difference:

```
missing21: 0 1 2 0 3 1 4 2 3 4
missing31: 0 1 2 0 3 2 4 3 1 4
```

The first is Richardson's existing source word. Coordinate permutations give
all ten weight-three masks from 21; the second covers the weight-five orbit.
Every other output uses two readouts. The missing row has a four-readout
representation, exhibited in each certificate word; equivalently, it is the
XOR of two achieved differences. If those two pairs shared a prefix value,
the missing row would itself be a two-prefix difference, so the four values
are distinct. Every source still occurs twice. Thus `v0+2e_Am` is attainable
for every m in H, with no hidden connector cleanup.

Steps 2 and 3 show that **every** legal count vector dominates one of the 16
attaining vectors. The 16 vectors are pairwise incomparable. They are therefore
exactly the componentwise Pareto frontier, establishing the displayed formula
for every positive real price vector. Set one eligible price to 1/5 and all
others to 7/3 to expose that vector uniquely; the verifier checks all 16 such
exact rational fixtures. More generally, minimizers are exactly the frontier
vectors whose eligible surcharge price is least. Strict positivity excludes
strictly dominated vectors from a weighted optimum.

### 5. Why exact readout minimization is independently checked

The verifier also computes the complete 31-entry minimum-readout vector for
every canonical path, rather than examining only the 22 maximum-coverage paths.
One engine uses shortest paths on `(dirty_parity, source_mask)`, a 64-state graph.
A readout at prefix q toggles `(1,q)`. All even-parity targets are reached.
A separately implemented engine pairs endpoints, derives active source
intervals at each cut, and exhausts subsets of **distinct** prefix values.
Using a prefix value twice cancels both dirt and its contribution, so a shortest
word never needs a repeated value; this subset oracle is exact without a cutoff.

The engines agree on all **29,295 costs**: 21,076 are two readouts, 8,177 are
four and **42 are six**. Those six-readout cases are included in the reduction;
they are not silently priced at four. A SHA256 binds the canonical ordered
cost rows, while replay reconstructs every entry instead of trusting the hash.

## Complete invoice, implementation and limits

For a caller with fixed complete prices, including each call's arithmetic,
source/coefficient access, target update, private scratch restoration, internal
dispatch and head return, the word has bill

```
I(W) + P(W) + D(W) + OPT(b,a).
```

I pays admission and layout, P coefficient preparation, and D root program
construction/storage/reads/dispatch. The theorem optimizes the **map portion**;
if these extra terms depend on the chosen word, they must be evaluated separately
and can change the best total physical schedule. No routing or setup work is
silently declared free. If root dispatch has one common charge per call, every
frontier word has 74 calls, so that charge is the same for all 16.

The exact optimizer compares 16 eligible prices, selects the minimum and emits
its fixed 74-call witness. The package's finite lookup construction is part of
its explicit preparation, not a data-dependent oracle. There are always the
same 37 public rows: five sources, one borrowed arbitrary-dirty connector and
31 outputs. No clean full row is introduced. Any recursive implementation of
A or B retains its own additional private scratch and costs; the inherited
balanced lowering is not rerun or improved here.

The written prefix identity proves the endpoint for arbitrary L and maps.
Finite evidence separately replays all 16 complete words and literal inverses
on all 37L dirty basis columns for L=1,2,3: **3,552 forward/inverse case pairs**.
The width-two/three fixtures include singular and noncommuting maps. Exact
formal source/dirt coefficients are checked as well. These checks do not prove
a physical supplier, common-label/owner interface, contracting moment,
precision/tape implementation, all-size compiler or multiplication theorem.
The selected `kappa=836330098538459/500000000000000000` is unchanged;
its actual cold command remains `make frontier1094-verify`, not this replay.

## Reproduce

From the repository root, standard-library CPython 3.12:

```sh
uv run --python 3.12 --no-project python -I -O -B research/connector-all-tariff-optimum/verify.py
uv run --python 3.12 --no-project python scripts/research_package.py --package research/connector-all-tariff-optimum
```

The focused verifier prints

```
PASS_CONNECTOR_ALL_TARIFF_OPTIMUM pairings=945 pareto_profiles=16 all_positive_prices=36 dirty_basis_cases=3552 controls=9 no_new_kappa
```

The registered command also runs four behavioral test groups. Nine semantic
controls reject missing restoration, an under-read output, wrong destination,
a four-readout cap, treating an even mask as surcharge-eligible, excluding the
weight-five mask, unpaid calls, a zero price outside the declared API domain,
and a clean-connector false positive. Package tests exercise live-source and
receipt corruption, exclusive receipt creation, and optimized read-only replay
from an unrelated directory without Git or network. `--write-result NEW_PATH`
creates a receipt exclusively; ordinary replay never regenerates evidence.
No compressed artifact is generated. The finite results use integers/Fractions,
not floating-point acceptance, and checks remain active under `-O`.

Observed on 2026-10-14, CPython 3.12.12 / Darwin arm64: the isolated optimized
focused replay passed, and the registered replay passed both the mathematical
check and all four behavioral tests (2.33 seconds wall, one local observation,
not a benchmark). The parent independently reviewed the unrestricted-word proof
and replayed the registered package successfully before authorizing publication.
This is separate agent review, not independent human review.

## Sources, overlap and credit

Base: `e112d71c8d7bb32435debcc54df932593dd8223a`. Complete chooser JSON is in
[SELECTION.json](SELECTION.json), seed `9c083f6b391fc18192cb0990085ca4ed`.
[SOURCES.json](SOURCES.json) binds predecessor inputs by Git blob and SHA256,
with original heads and attribution. No frozen input or shared index is changed.

- **Ross Richardson**, PR943 `cf360b4b09b7d0419decdd6ac85421fefed55bdd` and
  PR934 lineage: exact generic contract, source-prefix criterion, universal
  twelve-event construction and five-source boundary. The retained NOTICE
  credits @shhxera/@CubeJerry for common-factor fanout and Chafik Boukhalfa for
  the dirty-product commutator. No priority is claimed for these mechanisms.
- **Cinna Davis /1337isnot1337**, PR1770
  `caae2d1a0b4497fbd5a7cd2d057d9a9b099f8873`: one-vector weighted optimum;
  PR1811 `7ac80c37c843cdb48f48772dc46817d5f591fd3e`: parity-hyperplane
  family and the odd-mask obstruction. Those heads were checked merged.
- The generic paid-frame exclusion (`connector-frame-73-exclusion`) changes
  the alphabet and proves a map-call floor, not this arbitrary-price theorem.
  PR1898 has mutable sources and a common B, also a different contract.

Entry overlap used the shared complete snapshot of 329 open PRs including drafts
(2026-10-14T18:11:09.770757Z) and 692 Discussions including comments/replies
(18:12:32.610168Z), cached offline, plus targeted current PR heads and local
merged packages. It is not an exhaustive all-diff or unpublished-work novelty
certificate. An initially considered 2-integral plane-decoder floor was discarded
before implementation because Philippe Van Velzen already proved it in
Discussion1587 comment18927273. That result is not resubmitted here.
[Scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2049#discussioncomment-18931281).

Immediately before publication, the three predecessor heads above were unchanged.
Targeted live reads found two adjacent new PRs: PR2056
`c713ff9eff95446508aeb865a9f58b1758b2a00a` adds combined pair-source calls,
outside this alphabet; PR2050 `a86b65e648f5b004f4aa68b3ed2c7975e8ca0163`
erases generic output-bank mixing while preserving per-map counts, but does not
derive this 36-price frontier. Their complete PR bodies were inspected; neither
is an implementation dependency. The targeted search was not a second full-board
refresh and is not claimed to cover every closed PR or code diff.

Prepared for **adamgall** with substantial **OpenAI Codex assistance** in
research, proof, implementation, experiments and writing. New work is
**Apache-2.0**. The two algorithms are separate implementations, not independent
human review. No Lean/kernel acceptance, hosted CI pass or selected cold replay
is claimed.

## Open next questions

Does an admitted supplier expose this generic all-mask interface and known
heterogeneous complete tariffs? Identify one exact caller, verify immutable
source/readout ports and absence of intermediate observers, then apply the
formula and add its actual setup, dispatch, routing and restoration bills.
The missing selected caller and native prices block any supplier conclusion.
The structured question, relevance and first step are in TASK.json. Changing
the operation alphabet, allowing source mutation or checkpoint observers requires
a new theorem; the present result is complete only within its stated contract.
