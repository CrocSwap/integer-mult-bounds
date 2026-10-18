# Paid dyadic scaling breaks the fourteen-query signed-connector barrier

**Scoped complex circuit and exact fixed-price optimum; no new kappa.**
Allowing two paid operations on the dirty root, `z *= 2` and `z /= 2`, changes
the signed three-by-three connector of Ross Richardson's
[PR944](https://github.com/CrocSwap/integer-mult-bounds/pull/944).
Every one of its 288 obstructed signed/permuted matrices has a construction
with **13 ordinary queries and two root scaling passes**, instead of 14
ordinary queries. All sources and borrowed dirty arrays are restored.

For positive complete ordinary-query prices `c_F`, equal between signs, and
positive scaling prices `d` (double) and `h` (halve), the exact optimum in this
extended alphabet is

```
2 sum_F c_F + min(2 c_min, c_min + d + h),     c_min = min_F c_F.
```

Thus scaling helps exactly when `d + h < c_min`. No scaling, frame change,
source access or restoration is declared free. This extends the six repairs
in [PR1088](../weighted-signed-connector-seed58/README.md), by @martinxxx9.
It does not contradict either predecessor's fixed-alphabet result.

## Reproduction and evidence

From the repository root, Python 3.10+ with only the standard library:

```sh
python3 -I -O -B research/complex-dyadic-connector-seed30/verify.py
```

Expected final line:

```text
PASS_COMPLEX_DYADIC_CONNECTOR paths=720 orbit=288 query_maps=3456 leaf_maps=24 dense_maps=240 old_leaves=308 new_leaves=304 scales=2 controls=191 no_new_kappa
```

[CERTIFICATE.json](CERTIFICATE.json) contains all six short words, the full
304-factor-call example with both scaling passes, hashes of the other expanded
words, the complete 720-path census, exact prices and five dense tape invoices.
`verify.py --write` explicitly regenerates it; ordinary replay is read-only.
The verifier imports no predecessor implementation. It reads the pinned six
predecessor witnesses as data, then checks their original and transformed maps.

The checks cover 288 matrices times six repairs in both orientations, 24 free
noncommutative factor maps (old/new, six repairs, forward/inverse), and all 20
independent dirty basis inputs for six new words and their inverses using a
separate dense 2-by-2 interpreter. The 191 failure controls delete every query
or scaling, flip every query sign, reverse the conjugation, corrupt recursive
factors/restoration, and reject missing or invalid prices. These are exact
finite checks plus the written reduction below, not proof-assistant verification.

Package corruption, source drift and relocation checks:

```sh
python3 -I -O -B research/complex-dyadic-connector-seed30/test_package.py
python3.12 scripts/research_package.py --package research/complex-dyadic-connector-seed30
```

## Interface and the changed operation

There are seven distinct length-L arrays `x0,x1,x2,y0,y1,y2,z` over Q or C,
all initially arbitrary. Fixed linear maps `A_i,B_j` need not commute or be
invertible. The required final map is

```
x_j unchanged; z unchanged;
y_i += sum_j M_ij A_i B_j x_j,
M = [[1,1,1], [1,1,-1], [1,-1,0]].
```

Ordinary queries remain exactly `B_j^s: z += s B_j x_j` and
`A_i^s: y_i += s A_i z`, for `s = +1` or `-1`. Each preserves its source,
other data, private scratch and required head positions. Its additive increment
is independent of the old target. The new complete operations are
`D: z *= 2` and `H: z /= 2`; neither allocates a clean row. Every operation is
charged at its fixed ports, including any needed implementation and frame work.
Data and root rows stay excluded from recursive scratch. Sources and operator
coefficients are read-only, and outputs are observed only at the end.

No extra root, combined query, direct product query, overwrite, input mutation,
output scaling or other operation is admitted. Exact dyadic division is part
of this new interface; ordinary truncating integer division is invalid.
The theorem requires a word that works for arbitrary permitted operators and
inputs, not a word exploiting a special zero map or algebraic relation.

Two identical adjacent queries can be replaced, chronologically, by

```
B_j^s B_j^s  ->  H B_j^s D,
A_i^s A_i^s  ->  D A_i^s H.
```

The first maps `z` to `z + 2s B_j x_j`. The second restores `z` and adds
`2s A_i z` to the output. Both identities hold for arbitrary dirty `z` by
linearity. Each of PR1088's six witnesses has exactly one such adjacent pair,
for its designated repeated operator. Replacing that pair gives two calls to
each of the other five operators, three to that operator, and one `D` and `H`.
For example the B0 repair becomes

```
B0- A1- H B0+ D A2+ B1+ A0+ B0- A2- B2- A1+ B1- A0- B2+.
```

Row/column permutations and sign changes transport these words to all 288
matrices without changing the scaling operations. In particular, any one of
the six operators can be the cheapest operator in the price formula.

## Why twelve queries remain impossible

This reduction permits arbitrarily many root doublings and halvings; there is
no finite bound on their number or on their intermediate exponent.
At each boundary write

```
z = g (z_initial + sum_j q_j B_j x_j),     g = 2^k > 0.
```

A scaling changes `g` and leaves `q` fixed. A source query of sign `s` changes
`q_j` by `s/g`; an output query contributes `s g` times the current normalized
root to `y_i`. Restoration forces final `g=1` and final `q=0`. Dirty-root
cancellation forces the sum of `s g` at each output to vanish. These necessary
conditions already follow by specializing all operators to scalar identities
and varying the seven inputs independently.

Every nonzero column therefore needs at least two B queries, and every
nonzero row at least two A queries. With only 12 queries, every operator occurs
exactly twice. Each B pair must have opposite signs at equal scales; hence
its normalized coordinate only takes values `0` and `+a_j` or `-a_j`, with
`a_j>0`. Each A pair likewise has opposite signs at equal scales `b_i>0`.
Its output row is a signed difference of two visited normalized prefixes,
multiplied by `b_i`. A nonzero entry of M has absolute value one, so

```
b_i a_j = 1     whenever M_ij != 0.
```

The support graph of M is connected. Equivalently, its first row meets every
column and its first column meets every row. Thus all `a_j` equal a common
`a`, and all `b_i=1/a`. Dividing the normalized source path by `a` leaves one
`+e_j` and one `-e_j` for each coordinate. Each desired row must be a difference
of two of its visited vertices. Additional scale-only boundaries add no
vertices to this normalized path.

There are exactly `6! = 720` orders of those six distinct signed moves. The
independent enumeration finds 72 paths covering none of the three required
rows, 432 covering one, 216 covering two, and **zero covering all three**.
Both orientations of every prefix difference are included. This proves the
12-query exclusion after the reduction; it is not a search over a bounded
set of dyadic exponents. Permuting/signing coordinates and rows preserves the
criterion, giving the same exclusion throughout the 288-matrix orbit.

Without scaling, all individual query counts are even, so at least 14 queries
are needed. If any scaling is used, preserving the coefficient of arbitrary
`z_initial` requires equally many `D` and `H`, at least one of each. At least
13 ordinary queries are still needed. Every operator already costs two calls,
so the extra cost is at least `2 c_min` without scaling, or `c_min+d+h` with
scaling. The twelve old/new witnesses attain these two alternatives. This
establishes the stated optimum for every positive fixed price vector, even
among words of unbounded length. Prices depending on intermediate state,
sign, schedule or frame require a different optimization.

## Complete recursive bill and a paid dense instance

For a product F of factors in application order, split into a right prefix R
and left suffix S. With one disjoint dirty child connector w, the complete word
is `R(x,w); S(w,y); inverse(R)(x,w); inverse(S)(w,y)`. The inverse reverses the
entire literal word and negates all additive signs. Hence

```
C([f]) = c_f + dispatch_leaf,
C(F)   = 2 C(R) + 2 C(S) + dispatch_node,
height([f]) = 0; height(F) = 1 + max(height(R), height(S)).
```

Each leaf price includes coefficient/source access, arithmetic, target updates,
private restoration, routing, frame admission and head return. Batch admission
`I` and coefficient preparation `sum P_F` are additional common charges. The
fixed query prices include their dispatch and instruction work; root scaling
prices include full-row reads/writes, exact scalar work, routing and head
return. If selector or code-generation costs differ between schedules, add
those actual differences before inferring a saving. No whole-row cost is
divided by the number of outputs.

Seed `30 mod 6 = 0` places the two-factor child at B0. Factor lengths in
`B0,B1,B2,A0,A1,A2` order are `2,3,4,5,6,7`; balanced complete leaf counts are
`4,10,16,28,40,52`. The original cheapest repair has 308 factor calls. The
new word has **304 factor calls and two root passes**, borrowing the same four
dirty rows (root plus three child rows). With a *declared* unit tariff for each
factor call and each whole scaling pass its bill is 306 versus 308. This unit
tariff is illustrative; the general criterion remains `d+h<c_min`.

A concrete dense realization uses ten length-L mutable rows followed by 27
read-only L-by-L coefficient matrices. Each dot-product term visits its
coefficient and source word, then the row's target is updated. Each complete
leaf returns the data head to cell zero. A scaling visits all L root words,
updates each, and also returns to zero. No gather or root scan is free.
The two root scans cost exactly `28L-4` word-cell moves in this layout.
The verifier traces the full old/new words for L=1,...,5 and checks the delta
against one removed complete B0 call plus both scans. For L=3:

| Charged item | Old word | New word |
| --- | ---: | ---: |
| General scalar multiplications | 2,772 | 2,736 |
| Additional dyadic scalar operations | 0 | 6 |
| Coefficient reads | 2,772 | 2,736 |
| Source reads | 2,772 | 2,736 |
| Target reads / writes, each | 924 | 918 |
| Additions | 3,696 | 3,648 |
| Sign negations | 462 | 456 |
| Accumulator resets | 924 | 912 |
| Data head moves | 837,128 | 835,044 |
| Literal instructions | 308 | 306 |

Both layouts have 30 mutable and 243 coefficient words, with 273 initial
admission reads. Coefficient generation remains additional preparation work.
Loop work is recorded as dot terms and row iterations. An instruction can
use 15 fixed bits: kind, five-bit factor/scale code, two four-bit ports and
sign. Using that common encoding for both programs gives 4,620 versus 4,590
instruction payload bits. This is not a comparison against PR944's narrower
14-bit encoding, which did not include root scalings. Stored program
fetch/return, dispatch and index arithmetic are charged by their
instruction/loop counts; the new word reduces those counts in this common
encoding too.
These are exact operation invoices, not wall-clock measurements or a native
selected-supplier implementation.

For an exact integer-input dense instance with integer coefficient magnitude
at most H0 and input magnitude at most D0, a common safe bound on every data
and dot-product intermediate is `2 max(1,D0) (1+L H0)^308`. One fractional bit
suffices for the new word: only one halving occurs, and all other factors are
integral. A common fixed-denominator representation therefore bounds stored
integer magnitudes by `4 max(1,D0) (1+L H0)^308`. Choose signed word width from
that bound, also covering H0 and loop addresses. Charge reads, writes and head
moves at that width, plus the actual integer arithmetic costs and controller
work. Doubling/halving are exact shifts in this representation. This supplies
a fully paid rational instance; it is not a stability theorem for rounded
complex children. General exact complex correctness follows from the linear
identities, independently of this illustrative integer/dyadic realization.

## Scope, provenance and overlap

Base: `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. The selected record at that
base is PR1094/PR589, conditional kappa `0.001672660197076918`; the complex
side binds. Its source manifest, assembly and maintainer review were followed,
and the source-bound baseline check passed. No selected artifact is changed.
This local circuit has not been located in the selected supplier's actual
word, assigned physical owners, or substituted into its recursive histogram.
Native/whole-call admission, compiler/realization, precision, tape and outer
analytic obligations remain unresolved or inherited. The selected cold replay
and a full multiplication theorem are outside this package's claim.

OS assignment seed **30**, complex-supplier track. This is a scoped circuit
side result using the repository's connector-alphabet card. The alternatives
considered were an extra masked root-star term (already covered by PR1236's
COPY64 result) and an L284 temporal gauge (overlapping PR1398/PR1369). The new
mechanism changes PR944's expressly fixed operation alphabet. It does not
reopen an excluded search by increasing its budget. There was no pinned
coordination issue; the claim is recorded in [TASK.json](TASK.json).

Concurrent [PR1349](https://github.com/CrocSwap/integer-mult-bounds/pull/1349),
head `8adb25ce6d2090de170e241a170668e8fd7cf5a2`, gives thirteen signed queries
over F3 with no extra operation. This result instead stays in characteristic
zero and pays for changed root operations. No code or certificate from PR1349
is imported. Live overlap-search coverage and its limits are recorded in TASK.

The finite stopping rule was to check all 720 reduced paths, all 288 orbit
matrices with all six repairs, the six recursive words and the declared five
dense lengths. The theorem for unbounded scale histories comes from the
written normalization reduction, not an extrapolation of finite samples.

## Open next questions

1. Does the selected complex word contain a compatible signed connector batch
   with an ordinary child costing more than two complete root scans? First
   identify one actual batch and its exact source/frame/owner boundaries, then
   price the substitution. No such occurrence or physical admission is supplied
   here; this blocks any claim about the selected moment or kappa.
2. Can its approximate child interface support the `H B D` and `D A H`
   conjugations at the currently charged precision? Start with the actual
   rounding convention and transport each error through both scales. Exact
   cancellation alone does not answer this; no rounded interface is proved.

## Credit and license

Prepared by **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex assistance**
in reasoning, code, verification and writing. New material is Apache-2.0 under
the repository license. No independent human or proof-assistant review is claimed.

Ross Richardson's PR944 at `5dbcfbc63f646de5a1354f6b9760ec03837233f0` supplies
the canonical matrix, original alphabet, obstruction and cost framework.
@martinxxx9's PR1088 at `b0396aad724fec58630fbd4d13a809c562f18d9e` supplies the
six literal repairs reused as pinned data. Their antecedents include @CubeJerry's
PR889 signed fanout, Ross Richardson's PR934/PR943 binary connector results,
and Chafik Boukhalfa's PR628 dirty commutator/literal-inverse convention.
The selected supplier authors retain all credit for their separate construction.
[SOURCES.json](SOURCES.json) records exact Git blobs and SHA256 pins.
