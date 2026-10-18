# Native terminal source-response factorization

The selected F0→F2 two-centre-ablation terminal residual factors through the
first eight **complete native centre fields**, conditional on the retained
native common-frame and cover/local-view contracts. This supplies the native
upper-factorization left open by [PR #2564](https://github.com/CrocSwap/integer-mult-bounds/pull/2564)
and its [scalar terminal quotient](../centre-terminal-source-quotient/README.md).
It does **not** transfer that package's sharp scalar rank or scalar decoder to
the native space. There is no new supplier, saved child, cost profile or κ.

The scientific baseline is canonical main
`a1bfbc677fdcbc2a27a9b3bf6c78cac8fd6da9e2` (priority revision 5).
[SOURCES.json](SOURCES.json) pins every live proof input and selected archive
member. The selected dimensions are 112 ports, 480 helpers, 704 ordinary local
roles, 73 axes and 144 calls. Historical geometry notes describe 120 ports;
the executable evidence uses the selected 112-port data throughout.

## Exact claim

Fix an admitted common native payload depth, all cover owners and arbitrary
spectator indices. Let `F` be the selected chronological prefix ending after
the **complete** time-10 call. It contains 11 local sweeps, four idle sweeps and
four bridges. Let `A` be the same prefix with the eight private centre values
replaced by zero immediately before their centre transports in each of calls
0 and 10 (both forward). Keep every other preparation, scatter, continuation
and cleanup. This ablation is a diagnostic linear map, not a free legal child.

Vary only the original 112 X0 source families `d`; hold all other ordinary
and private initial contents `h` fixed (the same `h` in both executions),
allowing arbitrary correlated dirt.
Define

```
E_D d = (F-A)(d,h) - (F-A)(0,h).
P_D d = first eight pre-transport centre-field responses to (d,0).
```

Any fixed invertible normalization of each first field gives the same claim.
Under the inherited contracts identified below,

```
ker(P_D) ⊆ ker(E_D),   hence E_D = L_native P_D.
```

This is a statement about eight full fields indexed by cover owner, payload
and spectators, not eight scalars or eight paid recursive children. `L_native`
is an unpriced linear map on `image(P_D)`. Its definition does not provide
`(F-A)(0,h)` or subtract the dirt contribution in an actually saved transcript.
It asserts no sharp native rank or injectivity of the ablated continuation.

## Proof

### 1. Exact local endpoints and the inherited view contract

The [whole-payload audit](../centre-native-observation-dimension/PROOF.md)
establishes native common-frame conjugation of the selected local word:
`diag(L_final) (S ⊗ I) diag(L_initial^-1)`. Every scalar operation is in a
common frame, with conversions and endpoint/residual adapters explicitly
included. The ordinary scalar endpoints are

```
S_forward(D,T,H)  = (D,T+D,H),
S_backward(D,T,H) = (D-T,T,H).
```

In particular, complete helper endpoint blocks are diagonal: helpers neither
receive source response nor feed it into data or another helper. A helper's
physical endpoint frame may change; we never assume its payload is unchanged.
`verify.py` rechecks both 24,767-event words, all 704 ordinary columns, all
2,896 native conversion recipes, 224 endpoint adapters and 36 residual wrappers.
It uses the authenticated retained audit and credited exact Clifford kernel.

The global step inherits the declared complete native local-view/cover
covariance and common exterior embedding from the pinned native-lift,
whole-payload and hosting proofs. The Lean `Stream.lean` conjugation and unit-row
identities explain the zero-block inference; Lean is not newly built here.
This package does not independently rebuild the physical stream compiler.
All statements below are conditional on that explicitly retained interface.

### 2. Native F0/B1 cancellation at every physical owner

Write `C_a` for the translation root with Fourier multiplier
`i^parity(a·u)` and `T_b` for translation with multiplier
`i^(2 parity(b·u))`. For port normal `q`, define

```
X_-1 = C_q,             Y_-1 = I,
X_s = product(i=0..8+8s) C_ei,
Y_s = X_s C_q^-1,       E_s = product(i=9..8+8s) C_ei.
```

The actual route `rho_s` exchanges the port's eight q-perpendicular chart
axes with exterior block s, fixes q, and is an orthogonal involution; `rho_0=I`.
Stored entry/exit translations are in the routed physical owner's coordinates.
If these are `a_X,a_Y,b_X,b_Y`, their local vectors are therefore `rho_s a`
and `rho_s b`. The exact selected identities are

```
T_(rho a_X) rho(X_(s-1)) = C_q E_s,
T_(rho a_Y) rho(Y_(s-1)) = E_s,
T_(rho b_X) (F9 E_s) = rho(X_s),
T_(rho b_Y) (F9 C_q^-1 E_s) = rho(Y_s).
```

Here `rho(B)` means conjugation by the coordinate permutation. The local
endpoint labels are exactly `(C_q,I)` on input and `(F9,F9 C_q^-1)` on output.
Thus the physical data matrices before the exterior factor is attached are

```
forward  = [[F9 C_q^-1, 0], [F9 C_q^-2, F9 C_q^-1]],
backward = [[F9 C_q^-1, -F9], [0, F9 C_q^-1]].
```

They are not bare scalar shears. `native_boundary.py` proves the displayed
translation identities by equality of every coefficient of their degree-at-most-2
Fourier phase polynomials over Z/4, for all 112 ports and nine stages. Literal
parity evaluation on zero, singleton and pair characters separately checks the
polynomial implementation at stages 0/1. The check binds all four local labels
by exact 512-column operator comparisons, including global phase.

For physical owner `g`, put `G_Xs(g)=P_g X_s P_g^-1` and similarly `G_Ys(g)`.
Encode arbitrary normalized fields `(u,v)` as
`(G_Xprev(g)u,G_Yprev(g)v)`. Both data sides of a port read the same physical
owner `g=d rho_s(p)`. The four identities and local common-frame theorem give

```
forward:  (G_Xs(g)u,       G_Ys(g)(v+u)),
backward: (G_Xs(g)(u-v),   G_Ys(g)v).
```

Each route is bijective. This argument is per physical owner and does not
commute maps at different owners. All equalities tensor with the common
exterior factor and spectators, so they hold for arbitrary admitted payloads.
Initially a source-only difference has `(u,0)`, since `C_q` is invertible.
F0 leaves `(u,u)` in these normalized frames; B1 leaves `(0,u)`. Therefore
**every X0 source response vanishes after B1**, not merely constant payloads.

### 3. The complete chronology makes the normal F2 centre response zero

The source-bound 19-event prefix is recorded in [RESULT.json](RESULT.json).
After F0 the possible live source-response families are X0=`0..111` and
Y0=`112..223`. Calls 1–3 touch neither as data or helpers. After complete B1
(time 4), only Y0 is live. The actual replica-zero bridge
`X0 += X1; Y1 -= Y0` adds possible response on Y1=`336..447`; its X inputs
are zero. Idle sweeps transform payloads within each family and preserve this
support upper bound. The other three bridges touch other replicas.

Calls 5–9 have no live data inputs. Time 8 touches 15 live Y1 families as
helpers; its diagonal helper endpoint can change their native frames but
cannot spread response to another family. At F2 the live input roles are
all 112 Y0 targets and exactly 99 Y1 helpers. Each of the eight forward
pre-centre rows has coefficient **zero on every one of these 211 roles**.
The primary checks all 1,688 coefficients. The independent checker derives
the rows backwards through literal events, rather than propagating them forward.

Under common-frame conjugation a role contributes a block of the form
`L_cut [a_(k,r) L_start(r)^-1 W_r input_r]`, with entry wrappers and local-view
maps absorbed in `W_r`. An exact scalar coefficient `a_(k,r)=0` kills the whole
native block, whatever that helper's current payload or frame. No equality of
nonzero scalar rows across distinct charts is inferred. Hence the original
F2 pre-transport source response is identically zero on all eight fields.

### 4. Kernel inclusion concerns complete terminal outputs

For a source difference `d` with `P_D d=0`, the first ablation changes no
centre response. The full and ablated source-response runs therefore agree
through all first-call continuations and intervening events. At F2 the full
run's centre response is zero by step 3, so the second ablation changes
nothing either. Every remaining continuation and cleanup agrees. Thus
`E_D d=0`. We compare complete chronological maps, not a sum of instantaneous
scatter increments.

All operations are linear, so fixed arbitrary dirt cancels in the difference
used to define `E_D`. Kernel inclusion defines `L_native` on `image(P_D)` by
`L_native(P_D d)=E_D d`; it is well-defined. Finite-dimensional linear algebra
can extend it outside that image if desired. The first-cut scalar minor at
ports `[0,1,2,3,4,5,6,12]` has determinant 32 (recorded exactly); invertible
input/carrier frames give an abstract right inverse per owner. This is an
existence construction, with no implementation or cost claim.

## Evidence and reproduction

From the repository root, using Python 3.12 and its standard library:

```sh
python3 scripts/research_package.py --package research/centre-native-terminal-factor --check-only
python3.12 scripts/research_package.py --package research/centre-native-terminal-factor
```

The three registered commands compare their entire deterministic typed JSON
receipts, fail on source drift, and use explicit `-I -O -B`. Proof checks use
exceptions rather than removable assertions. The primary compiles authenticated
predecessor source directly. [VALIDATION.md](VALIDATION.md) records actual runs,
controls, portable replay, review findings and unrun obligations.

`independent_terminal.py` was written by a separate Codex agent without reading
the primary implementation. It imports no predecessor checker or Clifford
kernel: it independently derives 1,408 ordinary endpoint rows and eight
centre rows by reverse adjoints, verifies the literal chronology, routes and
common frames, and checks exact Gaussian-dyadic boundary primitives. It shares
the selected archive and written native-view premise. `native_boundary.py`
has a separately derived 73-axis phase evaluator but shares the credited
Clifford kernel for its local-label comparisons. This is independent AI
checking with declared shared assumptions, not independent human review or a
formal verification of the global compiler.

Controls break B1 cancellation, introduce a legal same-frame live-helper ADD,
omit bridges, corrupt common frames or adapter phases, and omit/misroute native
boundary translations. Support controls demonstrate failure of the sufficient
zero-demand criterion, not full native terminal counterexamples for mutated
programs. Receipt and source-byte controls address reproduction separately.

## Open next questions

The selected two-call centre bill remains 16 H8 children (rank mass 128), plus the
original COPY/ADD/CLEAR and all other charges. Eight complete saved fields do
not imply eight children, a cheap residual consumer, restored dirty storage,
free catch-up or an improved precision envelope. PR #2895's retained-array
catch-up analysis is relevant navigation, not a premise invalidated here.
The family expansion gate permits retaining this scoped information lemma;
it does not authorize another unpriced construction search.

The next useful question is an **actual paid decoder for the dirty terminal
residual**. First specify a legal consumer of the saved fields, its dirty
offset and restoration path, and cancel common work against the original
invoice before evaluating any saving. Observation, transport, return,
precision and storage remain payable. A sharp native quotient would be useful
only if a concrete consumer needs it. [TASK.json](TASK.json) records this
handoff and the bounded task refinement.

## Credit and coordination

Direct predecessor: ywz65, PR #2564, scalar terminal source quotient. This
work relies on the retained whole-payload observation audit; the selected
chronological census of Sagar Thakrar (PR #2199); commdata2338's native lift
(PR #2048); Aaron Wang/navinor's native quarter-query control (PR #2391);
ywz65's owner observation floor (PR #2461); and the selected word, native
recipes, hosting and geometry lineage credited in those packages. Sagar
Thakrar's exact Clifford code is reused unchanged and source-authenticated.
Adam Gall's earlier dirty-centre work (#1918), DreamingOfClouds' common-frame
proof, icekylinx's compiler work, and the selected construction/replay work of
Rohan Arun, Jeremy Kothe and Hao Yan provide context; their claims are not
reassigned to this package. Existing source notices and licenses are retained.

The canonical [reservation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1884#discussioncomment-18967805) was posted by DLamdata in Discussion #1884.
The lead's earlier API attempt was denied write access and created no post.
PR #2880 was read for continuity and preserved unchanged; its encoded-bank
audit is not a dependency of this contribution. Overlap searches cover PR
bodies and Discussion text, not all diffs, and cannot prove novelty.

New package: DLamdata with substantial OpenAI Codex assistance, including the
lead and two bounded native agents. Apache-2.0. No external Claude or human
review is claimed.
