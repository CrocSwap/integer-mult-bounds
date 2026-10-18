# Sixth-root query phases retain the signed connector surcharge

**Scoped negative result; no new kappa.** Allowing all six Eisenstein units as
query coefficients does not reduce PR944/PR1088's signed three-by-three
connector below **14 complete queries**. This includes the 288 signed/permuted
versions of its target. For positive fixed complete prices, equal across the
six phases of each operator, the exact optimum remains

```text
2 sum_F c_F + 2 min_F c_F.
```

The enlargement matters: three sixth roots can sum to zero, so the signed
alphabet's even-occurrence argument no longer excludes thirteen calls.
We cover that gap by a complete finite reduction and two exact implementations.
All **291,600 source paths** are checked; none supports the target in twelve
or thirteen calls. The predecessor's six fourteen-call repairs attain the
bound. This is a written reduction plus finite certificates, not a formal
proof of the multiplication theorem or an adopted supplier.

## Reproduce

From the repository root, with Python 3.12 and the standard library:

```sh
python3.12 scripts/research_package.py --package research/sixth-root-connector-seed29
```

The registered replay runs these three checks, each with a 120-second cap:

```text
PASS_SIXTH_ROOT_CONNECTOR source_paths=291600 minimum=14 orbit=288 free_maps=6912 controls=507 no_new_kappa
PASS_INDEPENDENT_SIXTH_ROOT_CONNECTOR source_paths=291600 histograms=4 rational_basis_inputs=28 dense_maps=24
PASS_SIXTH_ROOT_PACKAGE_CONTROLS receipt_rejections=2 source_rejections=2 read_only_replays=2 files_unchanged
```

For a direct standalone check, use
`python3 -I -O -B research/sixth-root-connector-seed29/verify.py`.
It reads the pinned predecessor files and compares every field of
[CERTIFICATE.json](CERTIFICATE.json); it does not regenerate them.
[SOURCES.json](SOURCES.json) records exact base, Git blobs and SHA256 hashes.

## Interface and statement

Let `omega^2 + omega + 1 = 0` in characteristic zero and
`U = {1,-1,omega,-omega,omega^2,-omega^2}`. There are seven distinct length-L
arrays `x0,x1,x2,y0,y1,y2,z`, with arbitrary initial contents. The sources x
are read-only. Each A_i and B_j is a fixed **Q(omega)-linear** operator of
compatible dimension; they need not commute or be invertible. Complex-linear
operators also satisfy the algebraic contract. Real linearity alone does not
justify moving a nonreal phase through a reader.

The required endpoint is

```text
x_j and z unchanged;
y_i += sum_j M_ij A_i B_j x_j;
M = [[1,1,1], [1,1,-1], [1,-1,0]].
```

The only permitted queries are

```text
B_j^u: z   += u B_j x_j;
A_i^u: y_i += u A_i z;       u in U.
```

Each complete query preserves its source and other data, restores private
scratch and tape heads, and has an increment independent of its old target.
All seven data arrays remain reserved during children. The word may depend
on M, but not on input values. Outputs are observed only after completion.
There are no extra root connectors, root scalings, combined queries, direct
product calls, overwrites, copies, mutable sources or free frame changes.
The minimum concerns uniform correctness for arbitrary admissible operators
and inputs, not special algebraic relations or zero maps.

## Complete reduction to the finite census

**1. At least two occurrences per operator.** Specialize the operators to
identity maps and vary the independent sources and initial connector dirt.
Restoring z forces the sum of B_j phases to be zero for each j. Removing
A_i z_initial forces the sum of A_i phases to be zero for each i. Every
column and row of M is active, so all six operators must occur. A single
unit is nonzero; hence every count is at least two. Fewer than twelve total
calls are impossible.

**2. The short zero-sum multisets are complete.** Let R, W and V be the
signed occurrence imbalances for the pairs `{1,-1}`, `{omega,-omega}` and
`{omega^2,-omega^2}`. A zero sum is equivalent to `R=W=V`, because its
coordinates on the rational basis `(1,omega)` are `(R-V,W-V)`.
For two occurrences this forces an opposite pair. For three occurrences,
zero imbalances would require an even total, while a nonzero common imbalance
requires at least three occurrences. Thus the only triples are
`{1,omega,omega^2}` and its negative. Both programs also enumerate the small
phase domains directly, including repeated phases.

**3. Paired output calls are phase-scaled prefix differences.** Project a
query word onto its B calls. At each boundary t, write

```text
z = z_initial + sum_j (q_t)_j B_j x_j.
```

Two calls of A_i have opposite phases. They produce row M_i exactly when
`M_i = u (q_t-q_s)` for some visited boundaries s,t and `u in U`.
This is both necessary and sufficient when all outputs have two calls.
The A queries neither change z nor each other's targets, so all independently
chosen pairs can be inserted into the same source word. Both signs and all
phases are allowed, so using a set of visited vertices loses no orientation
or chronology condition.

**4. Enumerate all twelve-call source paths.** Every operator has two calls.
Each of the three B operators chooses one of three opposite phase pairs.
Its two phase-labelled tokens are distinct. All `3^3 * 6! = 19,440` orders
are checked against the prefix criterion, with every output phase allowed.
None supports all three rows.

**5. Enumerate every thirteen-call multiplicity profile.** Exactly one
operator has three calls; all others have two. If it is B_j, choose one of
the two zero-sum triples and one of three opposite pairs for each other B.
There are `2 * 3^2 * 7! = 90,720` orders for each j, with no quotienting or
random pruning. None supports all three target rows.

If the tripled operator is A_i, reverse chronology and exchange A/B roles.
Each old B-before-A pair becomes a new B-before-A pair with the indices
transposed and the same scalar coefficient product. The zero-sum conditions
are preserved, so the target is `M^transpose=M`. This converts every missing
case into one of the enumerated source-tripled cases. It is a transformation
of the abstract query problem, not a free operation on a physical circuit.
No commutation of the underlying operators is used.

| Source case | Paths | Supporting all three rows |
|---|---:|---:|
| Two calls per source | 19,440 | 0 |
| B0 tripled | 90,720 | 0 |
| B1 tripled | 90,720 | 0 |
| B2 tripled | 90,720 | 0 |

The certificate includes the entire eight-bin row-coverage histogram for
each case, not just the zero in its final bin. This proves the exclusion
within the stated finite alphabet; it is not an unsuccessful heuristic search.

**6. Attainment and weights.** PR1088 supplies six signed fourteen-call words,
one repeating each operator four times and using the other five twice.
Signs are sixth roots, so these remain legal. We read those words as pinned
data and recheck their complete free-operator maps, dirty state and inverses.
All 288 row/column signed permutations are covered. A common nonreal phase
on B and its reciprocal on A supplies another positive fixture for each word.
Relabelling sources/outputs and multiplying their query phases by the
corresponding row/column signs is a bijection on this alphabet. It transfers
both the exclusion and the attaining words to all 288 targets.

For any longer correct word, each occurrence costs its positive operator
tariff c_F. There are at least two occurrences of each operator and at least
two extra occurrences in total. Its price is therefore at least
`2 sum_F c_F + 2 min_F c_F`. Repeating a cheapest operator in the appropriate
predecessor word attains that bound. This argument covers arbitrary word
length, not only words of length fourteen.

## Complete cost boundary and stopping decision

The fixed c_F includes the actual phase multiplication, coefficient/source
access, child execution, target update, private restoration, fixed-port/frame
admission, head return and per-query dispatch. Let I pay initial layout and
admission, P_F pay reusable preparation once, and E pay instruction selection,
emission/storage and any control work not already in c_F. Under these stated
uniform tariffs the batch invoice is

```text
I + sum_F P_F + E + 2 sum_F c_F + 2 min_F c_F.
```

The theorem optimizes query charges. I, P_F and E are the additional charges
of the chosen word; if a backend makes them word-dependent, this expression
does not assert a global optimum for its total runtime.

There is one root dirty connector plus the maximum private workspace of an
invoked child; private workspace may be reused only after restoration.
For a product child with exact additive factors, the retained signed balanced
lowering has `C(F)=2 C(R)+2 C(S)+d_node` and
`h(F)=1+max(h(R),h(S))`, with `C([f])=c_f+d_leaf`, `h([f])=0`.
Its inverses reverse the literal word and negate the shear coefficients.
This recurrence concerns the attaining signed words; no unpriced nonreal
phase compiler is assumed.

The optimistic experiment admitted phase-weighted complete queries at the
same c_F, with no extra root surcharge. Even this model cannot save a child
call. The inherited factor-count fixture `(16,28,40,52,4,10)` still has
minimum 308; uniform unit tariffs give 14. These are abstract invoices, not
runtime measurements. Eight exact price/tie fixtures corroborate the written
weighted argument. Phase- or state-dependent prices require a different
optimization. Extra nonnegative costs cannot improve this favorable budget.
We therefore stopped this mechanism before implementing a physical supplier.

## Independent evidence and failure controls

The primary checker permutes distinct phase-labelled tokens and packs six
integer coordinates in base 32. In a tested equality each digit has magnitude
at most seven, so highest-digit dominance proves that the packing cannot
identify different vectors. It never performs floating-point complex arithmetic.

The second checker instead enumerates ordered local zero-sum phase sequences
and recursively enumerates source-label interleavings. It uses explicit six
integer coordinates and pairwise boundary differences. It imports neither
the primary checker nor predecessor code. All four histograms agree. A
separate rational 2-by-2 representation of Eisenstein multiplication checks
the signed and nonreal words on 28 independent rational basis inputs, with
noncommuting length-two operators and literal inverses (24 dense maps).

The primary replay checks 6,912 forward/inverse free-operator maps and 507
semantic controls: 504 single-query deletions/phase substitutions, an odd
five-call restored map and its inverse, and an incorrect inverse convention
on that nonreal-output map. The odd fixture prevents accidentally imposing
signed parity. The package checks also reject a count-preserving histogram
mutation and changed source bytes in both programs, then run both from a
read-only relocated tree and verify that no files changed.

These are two independently implemented methods in one AI-assisted session.
They do not constitute independent human review or proof-assistant checking.
Selected-supplier realization, hosting, precision/tape compilation, the
selected cold replay, bit H1-H5 and analytic assembly are not discharged.
No selected record, frozen package or upstream source is modified.

## Provenance, overlap and credit

Base: `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. The selected record at
this base is PR1094, conditional kappa `0.001672660197076918`, with the complex
side binding. This package does not change that record. OS assignment seed
**29** selects the complex-supplier track; it chooses B2 first in the census,
orbit representative 29 and a nonreal positive-control gauge. Every case is
completed; a different seed is not the mathematical novelty.

The three candidate tasks and the bounded stopping rule are in
[TASK.json](TASK.json). The scope changes the coefficient alphabet, unlike
another signed search. The live claim is
[discussion #1539](https://github.com/CrocSwap/integer-mult-bounds/discussions/1539).
No pinned sprint issue existed. The remote overlap search covered all open
PR bodies and paginated discussions; timestamps and limitations are recorded
in the task metadata. It did not search every code diff or prove novelty.

- **Ross Richardson, PR944**, head
  `5dbcfbc63f646de5a1354f6b9760ec03837233f0`: target, signed obstruction,
  query contract and original accounting. The main ledger records incorporation.
- **@martinxxx9, PR1088**, head
  `b0396aad724fec58630fbd4d13a809c562f18d9e`: six attaining repairs and the
  signed weighted optimum. Their exact committed certificate is a live input;
  all source notices remain in place. The main ledger records incorporation.
- **Sagar Thakrar, PR1349**, inspected at
  `8adb25ce6d2090de170e241a170668e8fd7cf5a2`: thirteen calls in F3.
  Here `3 != 0`; this is a different algebra, with nonreal cancelling triples.
- **Hanson Sun, PR1526**, inspected at
  `1fb85dc6813b88483f4f0a359ccd722376acd292`: paid root doubling/halving.
  That operation is excluded here. No pending implementation is imported.
- **CubeJerry / PR889, Chafik Boukhalfa / PR628, Ross Richardson / PR934**:
  retained common-factor, dirty-commutator and connector foundations.
  Rohan Arun, Jeremy Kothe, Hao Yan and the retained community keep credit
  for the selected supplier lineage.

Prepared by **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex
assistance** in reasoning, implementation, experiments, verification and prose.
New material is Apache-2.0 under the repository license. No literature-priority
claim or independent human review is asserted.

## Open next questions

Would **arbitrary complex unit-modulus coefficients**, instead of the six
Eisenstein units, change this target's optimum? The finite phase census does
not settle it. A first step is to use the equilateral-triangle characterization
of three unit complex numbers summing to zero and eliminate continuous phase
parameters from the same thirteen-call profiles. The blocker is a complete
symbolic phase reduction and a fully priced coefficient implementation, not
more sampling of this already closed six-unit domain. This question is also
recorded in TASK.json; no answer is claimed here.
