# Paid compressed returns for infinite-order shear frames

**Recursive-interface construction and a scoped obstruction; no new kappa.**
For 53 fixed equivariant children with five workspace shear blocks, a complete
dirty echo costs **2,234 instructions instead of 2,494**. The candidate removes
380 ADDs and adds 120 doubling/halving operations. Both words restore every
dirty workspace coordinate and implement the same source-only output shear.

The price matters. The maximum forward prefix row-L1 norm increases from
**87 to 4,195**, so this witness needs six additional magnitude bits under that
bound. This is not a runtime improvement or an admitted supplier. It exhibits
an infinite-order interface mechanism with an explicit arithmetic and width
tradeoff. The accepted conditional kappa remains
`836330098538459/500000000000000000`.

## Contract and instruction prices

Work over the rationals, or exact complex components. Put

    J = [[0,1],[0,0]],   Q = I+J,
    P = diag(Q,...,Q) with m blocks,   N=2m,   d=2.

Every child is fixed and includes its trailing drift:

    C_i(D,W) = (D + R_i W, P W),    R_i P = Q R_i.

All other child scratch is arbitrary on entry and restored on return. The
source and output registers are disjoint; descendants may reuse scratch only
after it is restored. The emitter realizes leaves with blocks `a I+b J`, with
integer coefficients `a,b` in {-1,0,1}, then applies P. Its internal children
recursively obey exactly the same contract. No clean accumulator is assumed.

The compared words use the same instruction alphabet: `u += v`, `u -= v`,
`v *= 2`, and `v *= 1/2`. An ADD costs alpha and a SCALE costs sigma. The headline
counts set alpha=sigma=1. All source reads, writes, copy/unload operations,
inverses, child work and temporary scaling are included. There are no arbitrary
coefficient gates or free calls to a power oracle.

This is a fixed-child wrapper comparison. If an actual implementation can
delete its trailing P at no other cost, restoring or carrying that artificial
drift is unnecessary. No selected supplier with an indivisible contract of
this kind has been identified.

## Why unit-power transport alone cannot help

In characteristic zero, P has infinite order. Restrict boundary operations to
powers of P on the workspace and powers of Q on the output, pricing `P^u` as
`m |u|` unit ADDs and `Q^v` as `|v|` unit ADDs. After k fixed forward children,
workspace restoration forces

    k + sum_j u_j = 0.

Consequently its boundary cost is at least
`m sum_j |u_j| >= m k`; output work is nonnegative. Restoring P after every
child attains `m k`. This proves the exact boundary minimum for this stated
power-only tariff, for every positive k,m, irrespective of how output phases
are chosen. It is not a lower bound for arbitrary linear circuits, scaled
power implementations, interleaved inverse children or finite characteristic.

The verifier independently checks 180 finite shortest-path instances, k=1..12,
m=1..5 and output unit price 1..3, with phases restricted to [-k,k]. Its
transition cost is `m |s-t-1| + b |s-t|`, with entrance price
`(m+b)|t|` and final phase zero. These finite checks support the implementation;
the triangle-inequality argument above proves the all-integer statement.

## The changed mechanism: lower every terminal power

For a single pair `(u,v)` and integer t, scan the binary digits of |t| from
least to most significant. Double v before each later digit, add or subtract
v into u at every set digit, then undo every doubling by halving v. This maps
`(u,v)` to `(u+t v,v)`, including arbitrary initial u and v. For t nonzero its
exact bill is

    a(t) = popcount(|t|) ADDs,
    s(t) = 2 floor(log2 |t|) SCALEs.

Set both counts to zero for t=0. These are prices of this particular recipe,
not minimum synthesis lengths. A power of two can, for example, be cheaper
with repeated ADDs when it is small. Each pair's source is restored before
another pair is processed. Every halving divides a value whose factor of two
was introduced by this same ladder, so integer-grid inputs remain integral at
every prefix. No pre-existing zero low bits are required. The same argument
applies to the literal inverse ladder.

The canonical group G calls child one directly and applies Q to D before each
remaining child. Immediately before child i, indexed from zero, its workspace
and output phases both equal i. Intertwining gives

    Q^(-i) R_i P^i = R_i.

After the k children, apply the paid compressed `P^(-k)` and `Q^(-(k-1))`.
These operations act on disjoint registers. This proves

    G(D,W) = (D + (sum_i R_i) W, W).

The complete boundary vector is

    b_ADD(k,m)   = (k-1) + m a(k) + a(k-1),
    b_SCALE(k,m) =         m s(k) + s(k-1).

At k=53,m=5 it is **75 ADDs + 60 SCALEs**, versus 265 ADDs eagerly.
Under equal prices the boundary costs 135, saving 130. The full echo saves
`380 alpha - 120 sigma`, which is positive exactly when `sigma/alpha < 19/6`
at a common admissible arithmetic width. Width-dependent prices need their
own complete comparison.

This differs from a free-power assumption: the unit-tariff obstruction still
holds, and every operation that escapes its premise is in the emitted word.
For fixed m, the boundary is `(k-1) alpha + O(m (alpha+sigma) log k)` under
these instruction prices. This is a boundary estimate, not a multiplication
complexity claim.

## Complete dirty echo and recursive invoice

Let X be the preserved external source and U an arbitrary dirty workspace.
Execute in this order:

    U += X;  G(D,U);  U -= X;  G^(-1)(D,U).

The output changes by `R(U+X)-R U=R X`, with `R=sum_i R_i`.
The literal reversed/inverted G is used; a forward child is not substituted
for its inverse. U and all descendants return to their initial dirty values.
Appending P on X turns this echo into another child with the required type.
Thus induction proves legal composition at every finite depth.

Write `(A_v,S_v)` for the complete ADD/SCALE invoice, including descendants.
For a leaf reader matrix R and an internal node with k children:

    leaf:     A_v = sum |R_ij| + m,     S_v = 0,
    internal: A_v = 2 sum_i A_i + 2N + 2 b_ADD(k,m) + m,
              S_v = 2 sum_i S_i      + 2 b_SCALE(k,m).

Omit the final `+m` at the root echo. Eager execution substitutes `(k m,0)`
for the boundary vector. Copies cost exactly 2N ADDs per internal echo. At
height h, with leaf height zero, storage is `d+(h+1)N` data coordinates,
including the output, preserved source and one dirty N-block per internal
level. No extra data coordinate is used by power compression.

With uniform arity k and tariff `T=alpha A+sigma S`, the nonroot recurrence is

    T_h = 2k T_(h-1) + alpha(2N+m+2 b_ADD) + 2 sigma b_SCALE.

Its exact solution is `(2k)^h T_0 + g ((2k)^h-1)/(2k-1)`, where g is the
displayed nonrecursive cost; the root omits `m alpha`. This is a complete
finite depth recurrence. It makes no unstated identification of h, k or N
with the input size of the selected multiplication algorithm.

Preparation is separate. For M supplied leaf coefficients, emitted length L
and height h, this simple materializing emitter uses at most O(M+(h+1)L)
construction work and O(M+L+h) live compiler storage. The execution reads L
instruction records; every ADD reads two data coordinates and every SCALE
reads one, and each writes one coordinate. The certificate lists these totals
and a deterministic source-then-destination address travel score from head 0.
That score is not a tape-machine construction. A physical implementation must
also price instruction/descriptor access, routing, local arithmetic, storage
width and hosting; none is certified by the scalar instruction count.

## Exact evidence and limitations

| Complete echo | Eager ADD / SCALE | Carried ADD / SCALE | Equal-price saving |
| --- | --- | --- | --- |
| 53 leaves, five workspace pairs | 2494 / 0 | 2114 / 120 | 260 |
| Three internal children, each with 17 leaves | 4960 / 0 | 4260 / 600 | 100 |

The nested fixture pays the more expensive carried boundary at its arity-three
root. It is a composition check, not an optimized tree schedule.

For the first fixture the forward prefix row-L1 peaks are 87 and 4195;
the carried inverse peak is 2391. The nested forward peaks are 85 and 1460,
and its carried inverse peak is 1187. All prefix matrices are integral in both
directions. Each saved forward maximum includes its exact row and instruction
position, and a separate scalar execution of a sign input attains the claimed
maximum. For inputs bounded in magnitude by M, a prefix with row sum F is
bounded by F M. The first fixture fits within b+13 magnitude bits when
all input magnitudes are below `2^b`; eager execution needs only b+7 by the
same bound. These are exact-word bounds, not a rounded supplier admission.

The reproducible finite domain is:

- 161 signed powers, exponents -80 through 80, including zero and powers of two.
- All 6,561 ternary 2-by-4 readers; precisely 81 satisfy `RP=QR`, and all 81
  receive a complete three-child dirty echo replay.
- The 180 finite unit-tariff cases described above.
- Both complete fixture words, their literal inverses and internal source-drift
  contracts, on every dirty basis column, with independent semantic matrices,
  exact invoices, prefix growth and rational scalar probes.
- Eight rejecting controls: workspace return, output return, alignment,
  halving, nonintertwining reader at a nonzero phase, forward-as-inverse,
  source unload, and omitted SCALE charges.

The census, source SHA256/Git-blob pins and exact receipts are in
[RESULT.json](RESULT.json) and [SOURCES.json](SOURCES.json). No solver, random
search, optimum claim, probability estimate or stopping-by-discovery is used.
Seed 53 fixes k and m and deterministically selects the displayed leaf readers.
Verification does not import predecessor executable code. The matrix checker
and scalar interpreter are separately represented, but both were written with
the same AI assistance; this is not independent human review or formal proof.

## Reproduce

From the repository root, Python 3.12 and its standard library suffice:

    python3.12 -B scripts/research_package.py --package research/unipotent-return-seed53

Expected result includes:

    PASS_UNIPOTENT_RETURN seed=53 boundary=265->135 total=2494->2234 powers=161 admitted=81/6561 unit_cases=180 controls=8 no_new_kappa
    PASS_REGISTERED_RESEARCH_PACKAGE research/unipotent-return-seed53 outcome=completed

For a relocated standalone package, run `python3 -I -O -B verify.py`.
The registered command additionally authenticates historical repository
provenance against the exact base commit. `verify.py --emit` prints the
canonical mathematical receipt without editing files. It must agree with
RESULT.json. See [VALIDATION.md](VALIDATION.md) for executed checks and omissions.

## Provenance and credit

Exact base: `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. Track: recursive
interfaces, seed 53. [CLAIM.md](CLAIM.md) records the three candidates and
overlap check; [TASK.json](TASK.json) records the refined persistent-boundary
card and stopping rule. The actual selected PR1094 construction, source
manifest, assembly and review were inspected. Its complex side binds; the
PR589 bit supplier remains unchanged. No selected record, upstream file or
frozen package is modified.

Ross Richardson's [PR1287](https://github.com/CrocSwap/integer-mult-bounds/pull/1287),
pinned at `8606df05eca3c65032361c74ee3dbc2630b0cdc4`, supplies the cyclic
output-frame/dirty-echo framework and its explicit fixed-child limitation.
Its original README is retained in sources/ with exact byte and Git-blob pins.
Sagar Thakrar's PR1227 supplies the earlier sign-frame construction; the
PR889 dirty-batch lineage and PR1203 reader contracts are retained predecessor
credit. Infinite-order drift, its unit-power obstruction, and the completely
lowered binary return are the contribution here, not the output-frame idea.

Concurrent PR1391/1410/1499 concern finite-order cyclic frames; PR1488 concerns
noncommuting S3 transport. PR1439 and PR1506 concern source/operator repair,
which this package does not investigate. Native BIT address-shear PR521/677/840
use another contract. Their numerical gains are not composed with this one.
The local and remote searches are overlap checks, not evidence of priority.

The submission refresh also found Hanson Sun's PR1526, which trades a signed
connector query for two paid root scaling passes, and PR1522, which shares a
dyadic BIT source tour. Sricharan Vagvala's PR1532 repairs quadratic readers.
These contemporaneous results are credited as distinct paid-interface work.
This package concerns linear equivariant children with infinite-order drift
and a binary terminal return; it claims no priority for paid scaling itself.

Prepared by **Sagar Thakrar**, with substantial **OpenAI Codex assistance** in
derivation, code, checking and prose. One agent. New material is Apache-2.0;
the predecessor retains its original attribution. No human mathematical review,
full multiplication theorem, physical supplier or new kappa is claimed.

## Open next questions

First, inspect one real indivisible child for `RP=QR` and determine whether its
drift can simply be removed internally. A positive, fully priced example is
needed before this wrapper has an algorithmic application. No such selected
child is currently supplied.

Second, compare a few explicit intermediate reset cuts at the same k=53,m=5
to reduce the observed prefix growth while preserving an operation saving.
Keep complete ADD/SCALE/width invoices at common admitted precision. This
would address the main cost exposed by the present witness, but an optimum
schedule and physical precision contract remain open. Structured follow-ups
are recorded in TASK.json.
