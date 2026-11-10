# Source-bound nonunit split and output rechart composition

The source is the complete frozen #7130 export identified by `INPUTS.json`.
The construction is the finite specification in `CHANGES.json`, interpreted
by `construct.py`. The discovery heuristic is not a proof premise.

## Normalized-coordinate identity

For a field in chart F, write its physical value as C_F z. A legal MOVE from
F to G applies C_G C_F⁻¹, leaving z unchanged. When two fields share F,
ADD(r,s,q) sends z_r to z_r+q z_s. SCALE and COPY have the corresponding
chart-independent normalized actions. Consequently a chronological scalar
program has the same normalized linear operator whenever each scalar's
operands share its declared chart and every intervening MOVE is legal.

The generator retains every scalar opcode, operand and rational coefficient
in the original order. It changes only the declared charts of 129 public
scalar contacts and the output charts of 21 independent public helpers.
It removes the old public transport schedule and reconstructs the required
transport immediately before each scalar contact and at the final boundary.
Every emitted public MOVE is checked to be strictly nested and increasing.
Unchanged transports need not retain their former timestamp: in normalized
coordinates they are identities and the scalar chronology is identical.

Main input/output charts stay fixed. Each affected helper now promises
C_new-final C_initial⁻¹ on its arbitrary independent input, and its productive
rank is changed accordingly. No old helper credit is retained for a changed
boundary. All independent helper coefficients and every main output are
checked by the complete reverse adjoint; a separate integer forward replay
checks the full endpoint matrix.

Owned INIT/CLEAR operations, scalar contacts involving owned fields, and
owned MOVEs retain their source order and charts. The verifier separately
checks all lifetimes, peak live allocation and upward rank mass. This is
under the inherited owned-erasure contract, not a new zero-erasure theorem.

## Complete invoice

The exact per-native changes are

```
ΔT = {1: -2, 2: +2, 5: -1, 6: +1, 8: -18, 9: +18}
ΔP = {1: -35, 2: +12, 3: +8, 4: -8, 5: +8}.
```

Both rank masses increase by 21. Productive field count is unchanged and paid
positions decrease by 15 per native invocation. The unchanged 17-stage caller
multiplies both changes by 17, preserving full rank surplus 1,424 and zero
empty-root credit. Every target uses its actual changed output boundary.

For p=1−κ, the native signed-moment improvement is

```
33 H1 − 10 H2 − 8 H3 + 8 H4 − 9 H5 + H6 − 18 H8 + 18 H9,
Hr = r^p.
```

Both retained directed engines bracket the new complete crossing. The narrower
independent interval is `(0.00364240849686931699339641963661833,
0.00364240849686931699339641963661834)`. Both reject the predecessor invoice at
κ=0.003642408496869. A strict compiler probe stays below the lower crossing;
all compiler/outer inequalities are recomputed. This is an invoice-specific
bound, not a global optimum.

## Scope of acceptance

The full application additionally requires legal physical chart maps,
absolute phase, native and caller integer grids, precision/error envelopes,
ordinary work and fixed-tape substitution. Their executable checks and
receipts are separate from the early price receipt. See `APPLICATION.md`
for the current completion state. Five inherited assumptions and independent
human/formal review remain; a successful finite replay does not remove them.

## Attribution

The global assignment was nominated using **1337isnot1337/OpenAI Codex**'s
`fresh-helper-boundary/discover-cut.cpp` alpha-expansion method, with its
tariff parameter exposed rather than frozen. Ali Romman, CubeJerry, ToikY,
dillona, Matarener, DreamingOfClouds, the #7000 reviewers and Rohan Arun's
caller retain their respective source credit. All nested notices remain
in the authenticated source export. Rohan Arun with OpenAI Codex assistance;
Apache-2.0.

## Precision inherited from the split

PR7130 requires native odd scale 1125 and fractional height 25. The rechart
preserves its scalar coefficients/order. A fresh rational derivation is compared
with independent integer forward replay at that source-pinned grid, including
scaled maximum mass. Both native and complete caller precision paths explicitly
request that height from the authenticated grid engine; the F24 negative control
remains. Fresh envelopes and all precision charges are recomputed.

The F25 integration follows dillona/OpenAI Codex's PR7130 adapters. It changes
only temporary authenticated source copies; no frozen source or divisibility
check is changed or disabled.
