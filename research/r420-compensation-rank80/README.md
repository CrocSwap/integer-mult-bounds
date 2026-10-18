# Exact rank and minimum-weight kernel of R420 dirty compensation

**Independent verification; no new kappa or circuit.** The selected PR543
R420 word has a dirty-helper correction matrix `K` of size 120 by 420 over
F2. This package certifies **rank(K) = 120**, **nullity(K) = 300**, and
**minimum nonzero kernel weight 4**. There are exactly **18** weight-four
kernel vectors. All 420 columns are distinct and nonzero.

The source is eumemic's PR543 at
`2065fe4f72a914d907f1046603f5a36f17018535`, unchanged in base
`66849e1475c930fd7732b1a0067ffee7e1e95f60`. The selected construction is
PR626 (`660de893d27bb7abd1d5b01b1640207528a5c851`) with PR543,
conditional kappa `51110230636731/31250000000000000`.
[SOURCES.json](SOURCES.json) records archive/payload SHA-256, Git blob IDs,
and the selected record, manifest, construction, checker and review pins.

From the repository root, with Python 3.10+ and no external dependencies:

```sh
python3 -I -B research/r420-compensation-rank80/verify.py
```

Expected:

```text
PASS_R420_DIRTY_RANK rank=120 nullity=300 distance=4 pairs=87990 isolated_errors=120 controls=10
```

The additional independent scalar tests run with:

```sh
python3 -I -O -B research/r420-compensation-rank80/test_verify.py
```

Expected: seven tests pass. `verify.py --write /tmp/new-certificate.json`
reconstructs the complete certificate and refuses to overwrite an existing
file. Normal and optimized Python execute the same explicit checks.
[VALIDATION.json](VALIDATION.json) records the Linux checks, including a
minimal clean export containing only this package and its pinned inputs.

## What is checked

Registers 0–119 are sources `x`, 120–239 are targets `y`, and 240–659 are
arbitrary helper inputs `s`. For `W0 = A; scatter; B`, the existing PR543
interface states

`W0(x,s,y) = (U(x,s), y + Jx + Ks)`.

The original `xcheck.py` already checks `J=I`, `V=I`, and `K=D` by forward
symbolic register propagation. That identity is predecessor work. This
implementation imports no supplier code: it **pulls target observables
backward** through the actual gate order. For a gate `r_d += sum r_s`, a
covector changes by `q_s += q_d` for each source, with `q_d` unchanged.
This is its exact transpose action, since

`q · G r = (G^T q) · r`.

Reversing all 3,021 A/scatter/B gates (4,021 binary additions) yields all
120 target observables simultaneously. Their source and target blocks are
each the identity, and their helper block equals the literal frame-zero D
matrix. The retained-total scatter is read directly from `ret` and
`scatter`; its retained registers are never modified during scatter.

A separate backward pass through D/A/scatter/B/C verifies the entire
660-column scalar endpoint: `x` and arbitrary `s` are restored, and
`y -> y+x`. This is a scalar obligation; it does not recheck physical frame
transport or the COPY/ERASE realization of scatter.

## Rank, diagnostic inputs, and a complete kernel basis

[EXPECTED.json](EXPECTED.json) contains every row of K, 120 selected helper
indices, and the exact inverse of their 120-by-120 column minor `M`.
Bit j of a hexadecimal integer denotes coordinate j; K rows use
helper-relative indices 0–419, while lists explicitly marked `absolute`
use registers 240–659. Inverse row j corresponds to pivot position j.

The verifier checks **both** `M M^-1 = I` and `M^-1 M = I` by exact products.
Nomination and Gaussian elimination are not accepted as rank evidence on
their own. Embedding the rows of `M^-1` in the chosen helper positions gives
a 420-by-120 right inverse `H` with `KH=I`. In particular, helper input
`H e_t` causes exactly target error `e_t` if D is omitted. These **120
isolated-error inputs** are reproducible diagnostics for future correction
circuits. They distinguish every target error direction, whereas testing
only clean helpers cannot detect an omitted D at all.

For each nonpivot helper coordinate f, define

`n_f = e_f + H K e_f`.

Then `K n_f = 0`. Each of the 300 vectors has a unique unit coordinate
among the free positions, so they are independent. Rank-nullity proves
they span the full kernel. The verifier checks annihilation and the entire
free-coordinate identity. The exact minor plus this formula is the compact
kernel certificate; hashes of the generated kernel and H columns are also
recorded. The 120 H columns together with these 300 kernel vectors form a
basis of all helper inputs. A separate ordinary Boolean interpreter tests
all 420 directions through both the raw and complete circuits.

**Scoped consequence.** Any linear factorization `K = A B` with
`B : F2^420 -> F2^r` needs `r >= 120`. Thus this fixed correction cannot
factor through fewer than 120 linear summaries. This is not a lower bound
on simultaneous physical scratch, XOR count, recursive cost, or an altered
supplier. Summaries can be produced sequentially; the recent basis-changing
circuits are fully compatible with this rank.

## Exact minimum weight and a concrete cancellation

A kernel vector of weight one would be a zero column of K; a weight-two
vector would be two equal columns. Neither exists. A weight-three vector
would satisfy `K_a + K_b = K_c`. All **87,990 unordered column pairs** are
checked against the complete column set, excluding that possibility.

Equal XORs of two disjoint pairs yield weight-four vectors. The census
retains all pairs per XOR value, not just one representative, and deduplicates
sorted supports. Every weight-four vector has three such pair partitions,
so this exhausts the domain. All 18 supports are in the certificate.
Seed `80 % 18` selects the example

**absolute helper registers `{284, 296, 521, 623}`**.

Setting those four helper bits to one and all other inputs to zero gives no
target error in W0. Each of their 14 nonempty proper subsets gives a nonzero
target error. The separate scalar interpreter checks all 15 subsets for all
18 supports. Together with the exhaustive lower-weight exclusions this
establishes minimum weight exactly 4 for this finite linear map. In coding
notation its kernel is a binary `[420,300,4]` code. This does not identify
removable helper registers: each individual helper affects the correction.

## Controls, scope, and provenance

Ten controls cover omitted D, one missing D operand, swapped D rows
(**rank preserved but compensation wrong**), incorrect backward order,
corrupted inverse, corrupted kernel vector, dependent kernel basis, and
injected dependencies of weights one, two and three. Additional tests check
the adjoint identity on all 16 inputs and 16 observables for each of 40
seeded four-register circuits, both dense inverse products, cleanup damage
with K unchanged, corrupted source/certificate rejection, and gzip
recompression acceptance. All proof-relevant input bytes are pinned;
recompressed containers are compared by their complete decoded payload.

This is a complete finite calculation on the pinned word, not an empirical
search for a stronger bound or a formal proof in a proof assistant. Pivot
nomination uses helper order 80–419, then 0–79, and stops at 120 independent
columns. The distance census completes all 87,990 pairs and retains every
collision. No solver, probabilistic acceptance or floating arithmetic is
used. All-size/compiler, common-label/mutable-basis, physical/hosting,
precision/tape and analytic obligations remain inherited. No new invoice,
hosted construction, supplier optimum or full multiplication theorem follows.

The reviewed PR543 checker and interleaved-interface argument belong to
**eumemic**, with their Anthropic Claude disclosure retained in the
[original notice](../e8-bit-r420/NOTICE.md). Credit also remains with the
PR493/370/425/472/510 lineage identified there and in the pinned README.
The current construction/review credit remains with Jeremy Kothe, Chafik
Boukhalfa and the full selected dependency chain.

Concurrent #686/#694 optimize helper columns, #713/#716 optimize target
rows, and #612 supplies scoped Lean boundary/B facts. This package imports
none of those changes and does not certify their implementations; it adds a
transpose-based check and explicit rank/kernel evidence for their common
accepted baseline. [CLAIM.md](CLAIM.md) records task selection and overlap.

Prepared by **Joshua Snider**, with substantial **OpenAI Codex assistance**
in research, mathematics, implementation, testing and writing. Independent
implementation does not mean independent human review. New material is
under the repository's [Apache-2.0 license](../../LICENSE).
