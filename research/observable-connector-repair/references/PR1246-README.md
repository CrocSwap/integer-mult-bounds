# Pay for nonzero reader defects instead of restoring every child

**Recursive-interface construction and partition planner; no new kappa.**
For the fixed five-child example below, a complete dirty-workspace echo costs
**244 scalar instructions instead of 380**. Readers do not cancel their drift
errors. The parent restores the workspace and pays for an explicit output
correction. Both source-copy passes, both directions of every child, all
private scratch and the correction are included.

The contribution extends the zero-defect cut rule in Sagar Thakrar's
[PR1199](https://github.com/CrocSwap/integer-mult-bounds/pull/1199) and the
observer criterion independently developed by mightyOil in
[PR1203](https://github.com/CrocSwap/integer-mult-bounds/pull/1203) and Adam Gall in
[PR1205](https://github.com/CrocSwap/integer-mult-bounds/pull/1205). Their defect
identity is reused and credited, not claimed as new. The added operation is a
**paid output shear with a nonzero defect**, together with a minimum-cost
partition over a specified implementation of that operation. The selected
example uses a noncentral cyclic workspace permutation, outside the fixed
workspace-negation alphabet of Thakrar's
[PR1227](https://github.com/CrocSwap/integer-mult-bounds/pull/1227).

This is an interface result with indivisible children. If a compiler may open
these particular leaves, their final map is just a five-ADD signed dot product;
direct evaluation is much cheaper than either echo. No supported supplier
requiring this indivisible boundary has been identified. The result supplies
a checked option for such a boundary, not an optimized matrix algorithm,
physical supplier, runtime speedup or change to the selected exponent.

## Exact terminal repair

Let `D` be data and `W` arbitrary dirty workspace. Fixed linear children satisfy

```
C_i(D,W) = (D + B_i W, G_i W),     G_i invertible.
```

Each child's private scratch is arbitrary and restored. The matrices do not
depend on intermediate data, and there is no data-to-workspace feedback.
Eager execution follows every child by its workspace inverse. Its desired
return map is `(D + sum_i B_i W, W)`.

Write `P_0=I`, `P_i=G_i ... G_1` and

```
E = sum_i B_i (P_(i-1) - I).
```

The cited predecessor criterion admits uncorrected deferral exactly when
`E=0`. For arbitrary `E`, the following enlarged boundary is exact:

1. Execute each unchanged child once in its fixed order.
2. Apply `P_k^-1` to workspace.
3. Apply `D <- D - E W`, now using restored entry-coordinate workspace.

**Proof.** Before child `i`, deferred workspace is `P_(i-1) W_entry`. The raw
data return is therefore `D_entry + (sum_i B_i + E) W_entry`. Step 2 returns
`W_entry`; step 3 subtracts exactly the unwanted term. Every private scratch
port has its original value. This proves the identity for arbitrary dirty
inputs and dimensions over any field with these exact operations. It does
not infer a universal theorem from finite samples.

Restoration must precede the stated correction. Correcting against `P_k W`
instead would require a different matrix, `E P_k^-1`. A noncommuting example
in the controls detects this order error. An intermediate observer or adaptive
child cannot use the uncorrected output as if it were canonical. Such a point
must be a required cut, with its entire restoration and correction paid first.

## Declared operation alphabet and partition optimum

The executable specialization has one output coordinate, an integer row
`B_i`, and a signed permutation `G_i` on `N` workspace coordinates. There are
only two scalar instructions: `target += sign * source` for distinct ports,
where `sign` is `+1` or `-1`, and unary `NEG`. Registers are addressed exactly;
no clean scratch or implicit source copy is available.

Canonical signed-permutation synthesis first permutes absolute indices using
`N-cycles` swaps, then negates negative coordinates. A swap uses three ADDs
and one NEG, with no temporary. Inversion has the same number of cycles and
negative coordinates. The correction repeats a unit signed ADD `|E_j|` times
for each coefficient. A coefficient of magnitude four costs four ADDs, not
one. These are implementations with a known price, not globally shortest
linear circuits.

For a segment `[a,b)`, its boundary cost is thus

```
b(a,b) = 4 (N - cycles(abs(P))) + negative_signs(P) + sum_j |E_j|.
```

The child words are common to every partition. With `F(0)=0`, the planner uses

```
F(t) = min_{0 <= s < t} { F(s) + b(s,t) },
```

excluding intervals that cross a required observation cut. Each chosen segment
returns the same data and workspace as eager execution, so legal segments
compose. Conversely, every partition in this alphabet has a last segment;
removing it gives the displayed recurrence. Induction proves the minimum over
these partitions. This is not an optimum over arbitrary repairs, edits inside
children, interleaved adapters, or a different operation alphabet. The
`zero_defect_only` comparison additionally requires `E=0` on every segment.

## Seed-selected example and actual eliminated work

OS assignment seed **58** selected recursive interfaces. It also selects
`N=3+(58 mod 4)=5`, then the following row and signs using the documented
`random.Random(58)` calls in `selected()`:

```
R = (1,-1,-1,1,1)
s = (1,-1,-1,1,1),       sum s_i = 1
B_i = s_i R
G(W_0,W_1,W_2,W_3,W_4) = (W_1,W_2,W_3,W_4,W_0).
```

Each child reader costs five ADDs. Its workspace cycle costs twelve ADDs and
four NEGs. On the full five-child batch, `P=I` and

```
E = (-4,-2,2,4,0).
```

The raw batch is wrong: on `W=e_0` it adds `-3` instead of `1`. The completed
one-block repair costs twelve ADDs. The best zero-defect partition is all five
singletons, costing **80 boundary instructions**. The repaired optimum is
the full batch at **12**, as checked against all sixteen partitions. It removes
five workspace inverses, pays twelve correction ADDs, and preserves the child
word. If every interior child boundary must be observed, the optimum returns
to 80; the observation restriction is material.

The transparent source echo uses a separate arbitrary dirty `W` and preserved
source `X`:

```
W += X;  B(D,W);  W -= X;  B^-1(D,W).
```

Since the completed batch is `B(D,W)=(D+R W,W)`, the two passes add
`R(W_initial+X)-R W_initial = R X`. The inverse is the literal reversed
instruction word, not a free inverse query. At depth one the complete echo is:

| Schedule | ADD | NEG | Total | Reads | Writes | Descriptor fields |
|---|---:|---:|---:|---:|---:|---:|
| Eager / zero-defect cuts | 300 | 80 | 380 | 680 | 380 | 1,360 |
| Paid defect repair | 204 | 40 | 244 | 448 | 244 | 896 |

## Complete recursion, storage and arithmetic scope

`recursive_word` realizes an actual tree. A leaf adds its signed row to `D`
and applies `G` to its source. An interior reader executes the above echo using
five depth-`h-1` readers with rows `s_i R`, then applies `G` to its own source.
Because the signs sum to one, the reader at every depth returns
`(D+R X,G X)`. Negative rows use the same construction with all reader
coefficients negated. Children restore their private scratch, so siblings and
both echo passes reuse one dirty block per active level. An induction on depth
proves the stated map for all incoming values.

Let `A_h,Q_h` count ADD and NEG instructions of an interior **reader**, including
all descendants and inverses. For this selected family the complete recurrences
are:

```
A_0 = 17, Q_0 = 4
eager: A_h = 10 A_(h-1) + 142; Q_h = 10 Q_(h-1) + 44
repair: A_h = 10 A_(h-1) + 46; Q_h = 10 Q_(h-1) + 4.
```

The factor ten pays both directions of all five children. The additive terms
include ten source-copy ADDs, both boundary bills, and the final source cycle.
A root echo omits that last cycle: subtract twelve ADDs and four NEGs. Thus
the depth-`h` saving is `136*(10^h-1)/9` instructions. This is tree depth at
fixed port width, not an input-size recurrence or a primitive exponent.

| Echo depth | Eager total | Repaired total | Data registers | Eager peak | Repaired peak |
|---|---:|---:|---:|---:|---:|
| 1 | 380 | 244 | 11 | 11 | 27 |
| 2 | 4,130 | 2,634 | 16 | 26 | 52 |
| 3 | 41,630 | 26,534 | 21 | 46 | 71 |

The data allocation is `1+(h+1)N` scalars: output, source and dirty blocks.
For `A` ADDs and `Q` NEGs, every emitted instruction incurs one dispatch,
`2A+Q` data reads, `A+Q` writes and `4A+2Q` instruction-field reads, including
signs and addresses. On the declared addressed machine, arbitrary prices for
arithmetic, these accesses and dispatch can be substituted into those counts.
All recursive calls are expanded into this instruction word; there is no
omitted runtime call dispatcher or coefficient multiplication. No frame change
is a free relabeling: each signed permutation is physically emitted.

Program preparation is separate work. For fixed `N`, arity and bounded row,
the supplied compiler conservatively takes `O((h+1)P_h)` list work and storage,
where `P_h=A_h+Q_h`, including its repeated planning and word reversal/copying.
The materialized program contains exactly the tabulated descriptor fields.
An end-to-end bill must add this preparation to execution; the counts do not
claim faster compilation or an amortization schedule. No streaming compiler,
tape routing, address-bit cost or physical hosting theorem is supplied.

The peaks in the table are exact maximum row one-norms over **every instruction
prefix**, on the complete original-input basis, including private dirt. If
initial integers have magnitude at most `M`, every intermediate magnitude is
at most `peak*M`. The repaired schedule therefore needs a larger magnitude
bound in these examples. The verifier uses unbounded integers and rationals;
unit instruction counts alone do not price arbitrary-precision bit arithmetic.
For general emitted words, the elementary bound `2^A M` also suffices. Neither
these bounds nor finite replay establishes a rounded or fixed-tape interface.

## Reproduce and inspect the evidence

Python 3.10+; standard library only. From the repository root:

```sh
python3 -I -O -B research/paid-reader-defect-seed58/test_package.py
```

Expected markers:

```
PASS_PAID_READER_DEFECT batches=5256 seeded=160 echo=380->244 controls=9 kappa=unchanged
PASS_PAID_READER_PACKAGE relocation=1 corruptions=5
```

`verify.py` checks the retained source-note SHA256 and Git blob identities,
recomputes every field of `CERTIFICATE.json`, and compares the result exactly.
`--emit` prints the recomputed certificate without changing files. Checks use
explicit exceptions and remain active with Python's `-O` flag.

The independent oracle composes complete state matrices and exhausts all cut
sets. It does not call the production defect routine or planner to derive
its costs. The bounded domain is all 72 single children and 5,184 ordered pairs
at width two: eight signed permutations and nine rows in `{-1,0,1}^2` per
child. This covers **5,256 batches and 10,440 partitions per policy**; 1,116
batches strictly improve over zero-defect cuts. An additional 160 deterministic
seed-58 cases have widths 3..6, arities 3..7 and row entries -2..2. All contain
noncommuting adjacent drifts; 54 impose interior observation cuts. Their 152
improvements are finite evidence, not an impossibility or optimality theorem
outside the stated domain. The stopping rule is completion of these domains.

The recursive census checks 120 generic reader/echo cases on all 1,044 original
basis columns, literal inverses and rational dirty probes, plus nine selected
depth/schedule cases. Every selected partition is also replayed. Nine controls
cover omitted/wrong-sign correction, wrong repair coordinates, missing cleanup,
noncommuting inverse order, omitted source uncopy, a missing second pass,
premature output observation, and nonunit coefficient cost. Eight invalid
inputs are rejected. The package test runs from outside the repository and
rejects five real file corruptions: retained source bytes, source-commit label,
certificate price, omitted correction, and treating a nonunit coefficient as a
single ADD. Source labels are recorded fetch pins; this is not a cryptographic
proof of GitHub publication or a fresh replay of predecessor packages.

## Provenance, scope and open next questions

Investigation base: `49b3157d1d89adcef16df8be98445451672be5ba`. The selected
certificate at that base is PR1094, conditional
`kappa=836330098538459/500000000000000000`. Its actual construction, source
manifest and review were followed; `SOURCE-PINS.json` records their hashes as
context. The source-binding baseline check passed. The selected cold replay,
native supplier admission, Linux CI, independent human review and a formal
multiplication proof were not run. Selected compiler/all-size, realization,
hosting, precision/tape, analytic and bit-interface obligations remain open.

`CLAIM.json` records the three considered tasks, scope, seed and bounded
domain. No pinned sprint issue was present, so the donor's local-claim fallback
was used. Open PR bodies and current discussions were checked; overlap evidence
is bounded and is not proof of novelty. This package changes no predecessor,
selected record, review ledger or upstream source.

**Open next questions.** Does a supported supplier expose indivisible drifting
readers whose defect is cheap to apply? Trace one concrete child return map and
price its composed inverse and correction before implementing this wrapper.
The blockers are a real child contract, routing and precision; transparent
leaves that can simply be rewritten do not qualify. Within the declared model,
a correction circuit with sharing could reduce the twelve-ADD bill further,
but it would need a different cost function and a newly checked partition
comparison. No global shortest-circuit claim is made here.

Credit Aaron Wang / Navinor's PR1155 for restoration coalescing; Sagar Thakrar's
PR1199 and PR1227 for the cut and output-sign interfaces; mightyOil's PR1203 and
Adam Gall's PR1205 for independent observer/dirty-reader treatments; and Ross
Richardson / CubeJerry's PR889 for prior common-factor dirty echo work. PR1012
and PR974 address hosted restoration mass, a different cost model. The selected
Rohan Arun / Jeremy Kothe construction and its contributor lineage are unchanged.
Three predecessor notes are retained byte-for-byte with their notices and exact
heads in `SOURCE-PINS.json`; no predecessor executable is imported.

Prepared by **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex assistance**
in algebra, implementation, verification and writing. New material is Apache-2.0
under the retained repository license. This is a written scoped proof with exact
finite implementation evidence, not independent human or proof-assistant review.
