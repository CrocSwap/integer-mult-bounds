# Source-bound global input rechart

The source is the complete frozen #7121 export identified by `INPUTS.json`.
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
in the original order. It changes only the declared charts of 22 public
scalar contacts and the input charts of seven independent public helpers.
It removes the old public transport schedule and reconstructs the required
transport immediately before each scalar contact and at the final boundary.
Every emitted public MOVE is checked to be strictly nested and increasing.
Unchanged transports need not retain their former timestamp: in normalized
coordinates they are identities and the scalar chronology is identical.

Main input/output charts stay fixed. Each affected helper now promises
C_final C_new-input⁻¹ on its arbitrary independent input, and its productive
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
ΔT = {4: -2, 5: +2, 7: -1, 8: -3, 9: +4}
ΔP = {1: -6, 2: +1, 3: +1, 4: -8, 5: +8}.
```

Both target rank mass and paid rank mass increase by seven. Productive
field count is unchanged and the paid field count decreases by four.
The unchanged literal 17-stage caller multiplies both changes by 17;
its own targets and paid operations are retained. The full rank surplus
therefore remains 1,424 and no empty-root credit is introduced.

For p=1−κ, the native signed-moment improvement is

```
6 H1 − H2 − H3 + 6 H4 − 6 H5 − H7 − 3 H8 + 4 H9,
Hr = r^p.
```

At the source crossing this is positive. Both retained directed engines
independently bracket the new complete invoice crossing in
`(0.0036407613741422058608084968767767,
  0.0036407613741422058608084968767768)` and reject the source invoice at
the claimed rational κ=0.003640761374142. The strict compiler probe is
chosen below the lower endpoint and all compiler/outer inequalities are
recomputed. This is an invoice-specific crossing, not a global optimum.

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
