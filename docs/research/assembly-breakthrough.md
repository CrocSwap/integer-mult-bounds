# Dependency paths remove the large complex guard exponent

October 7, 2026. Research refinement prepared with assistance from OpenAI
Codex. Conditional on the existing compressed complex circuit, its nested
binary frames and the retained recursive layer interface. This is not
independent review or formal verification, and it announces no new kappa.

The current guard bounds coefficient dependency depth by concatenating all
`s_c = 27,215,641,140,750,000` recursive calls. The network's dependency
graph gives a much smaller factor: `q = m + 6h = 15,775` at `h = 25`.
Consequently the stopped guard may use

    C1 = beta + rho(1-beta) + zeta,   rho = 1001/1000,

in place of `5 - 4 beta + zeta`. The old large constants remain sufficient.
At `beta = 1/1000`, `zeta = 1/10000`, this gives `C1 = 1.001099`.
With `epsilon = 0.49999`, the guard condition has nearly one half of slack.

This permits a small stopping exponent without weakening the guard. The
existing complex leaf saving becomes `(1-beta) a_c = 1.3986e-8`, versus
`3.36e-9` at `beta = 19/25`. That is useful room for a better bit circuit;
it does not itself change the current bit-limited multiplication exponent.

## 1. Count recursive calls on a dependency path

Consider one invocation of the finite complex network that reduces an
`e`-axis layer to children on `e/m` axes. Each edge has nested labels `U,V`.
Its operator is a product of exactly

    r(edge) = abs(dim V - dim U)

recursive child kernels, with only the retained phase and coordinate
operations around them. The direction changes whether a child is forward
or inverse, but does not change its coefficient-depth bound.

Evaluate each fixed scalar gate from saved inputs, as in the existing guard
argument. A dependency path through that gate enters at an input and exits
at an output. All its incidences have the same frame. Therefore a path
through the network selects a directed path of labeled edges even when it
switches roles at a gate. Using all-to-all dependencies at each gate is a
safe overestimate; zero scalar coefficients need not be exploited.

Write `D(path)` for the sum of the downward dimension changes along this
path. Cancellation of consecutive signed changes gives the exact identity

    sum r(edge) = dim(last frame) - dim(first frame) + 2 D(path).

The same bound covers a path ending partway through an edge. Insert one
intermediate label for each orthonormal residual vector; these dimensions
are monotone between the original endpoints. It also covers intermediate
values inside a scalar gate because the gate adds no further child call.

Every frame dimension is between zero and `m`. Thus, if `D(path) <= D_*`
for every dependency path, at most `m + 2 D_*` recursive child calls lie
on any one path. Let `A(e)` bound coefficient dependency depth. With the
same additive charge `E = 64(W+m+1)^3` for fixed scalar arithmetic and phase
corrections as in the current proof, we obtain

    A(e) <= (m + 2 D_*) A(e/m) + E.

This changes the guard recurrence only. The *time* recurrence still uses
the total `s/W`; calls on different branches still take time. Copying,
parking, swaps, compact controls and exceptional repair permute whole
coefficient encodings, so they do not introduce coefficient arithmetic.

## 2. The existing circuit has `D_* <= 3h`

For a stage `j`, write `a = h^(j-1)` and suppress the future line factor.
The usual labels have

    dim D0 = h^j - h,      dim D1 = h^j,
    dim D_U = h^j - h + dim U.

Each physical X data role moves from dimension `a` to `h^j`; each physical
Y role moves from `a-1` to `h^j-1`. Their intermediate labels are monotone.
Side roles use the monotone compiled labels in the forward stage and their
reverse complements in the inverse stage. Their initial and final
connections are monotone as well. These are the existing frame obligations,
not new assumptions that arbitrary side circuits automatically satisfy.

The only downward edges are the `h+1` central returns. Every such edge goes
from `D1` to `D0`, losing `h` dimensions. They occur between the same two
central gate times. A directed dependency path can cross at most one of
them in an invocation: it cannot return to an earlier gate time, and it
chooses only one operand on entry to a later gate. The fact that there are
`h+1` central wires does not multiply the loss on one path.

Invocations within a stage have disjoint data and scratch roles. A path
therefore visits at most one invocation in each stage. A data role can carry
the path to the next stage, while a scratch role has only its own invocation
and then its terminal connection. The compressed complex construction uses
separate scratch roles in the three stages. It follows that a whole-network
path crosses at most three central returns, so

    D_* <= 3h,       q := m + 2 D_* <= m + 6h.

This stage argument must be revisited if a future complex construction
shares scratch between stages or introduces a new decreasing frame edge.
The [ternary follow-up](ternary-direction.md) performs that check for PR #7:
its chronological stage-1/stage-3 joins are monotone and there is no sharing
within a stage, so the same bound holds. It does not automatically apply to
other sharing schedules.

## 3. An explicit stopped guard

At `h=25`, `m=15625` and `q=15775`. The integer comparison

    15775^1000 < 15625^1001

certifies `q < m^rho` with `rho=1001/1000`, without floating-point logarithms.
Stop at `e < d^beta`, as before. The number of internal levels is at most
`j <= (1-beta) log_m d + 1`, and the leaf depth is at most `8 d^beta`.
Unrolling the new recurrence gives

    A(e) <= (8 d^beta + E) q^j
         <= q(8+E) d^[beta + rho(1-beta)].

Keep the existing `B=s+E` and

    C0 = ceil(max(128 m B^2, 18 m B^2(1+1/zeta))).

Since `q<=s`, the existing exact comparison
`s(8+E)<=9B^2` also bounds `q(8+E)`. There are at most
`m(1+1/zeta)d^zeta` base-m pieces. Reserved axes, outer phases and the final
denominator shift have the same `18d` allowance as before. Consequently

    A_layer <= 9mB^2(1+1/zeta) d^[beta+rho(1-beta)+zeta] + 18d
            <= C0 d^C1,

where `C1=beta+rho(1-beta)+zeta > 1`. The original magnitude and denominator
induction then applies unchanged: `Delta=ceil(C0 d^C1)` guard bits suffice,
and `epsilon C1 < 1` keeps the coefficient widths `O(p)`.

In particular, no norm bound for intermediate circuits and no intermediate
rounding is being substituted for the existing exact arithmetic argument.

## 4. Exact controls

Run:

```sh
python3 scripts/experiments/assembly_breakthrough_guard.py \
  --output certificates/assembly-breakthrough-guard.json
```

The checker uses the actual compiled side roles and label dimensions at
`h=8,10,12,25`. For each of the three stage directions it executes the full
early/middle/late frame schedule on the X, Y, side and central roles. Every
gate is conservatively treated as all-to-all. At `h=25`, each invocation has
112,821 roles. The checker finds exactly 26 decreasing edges, all central
returns of rank 25; the maximum downward weight of a dependency path is
25, and its maximum edge-rank weight is 15,675. The latter includes direct
scratch-terminal connections to the full ambient space. Composition of the
three stages uses the structural argument above, rather than materializing
the full network's trillions of wires.

The certificate also checks the integer-power comparison and 81 finite
unrollings of the recurrence, including large additive charges. It computes
the existing `C0` and checks `q<=s`, `q(8+E)<=9B^2`, and the final whole-layer
constant comparison with exact integers and rationals. These
controls validate the finite frame accounting and arithmetic; they do not
mechanically verify the underlying subspace inclusions, the stream machine,
or the asymptotic proof.

An alternate witness in the same research certificate retains the aligned
bit parameters, including `kappa=1624/10^12`, while setting `beta=1/1000`
and `C1=1001099/10^6`. It checks every `fast_constraints` slack, the complete
compact-control layer exponents, and all seven `fast_margins`. The minimum
remains `g3=162446751/10^17`, with absorption gap `46751/10^17`. This is a
concrete way to review the guard change without treating it as a new
headline or modifying the published certificates. It is additionally
conditional on this note's dependency-path argument.

The focused regression checks are in `tests/test_dependency_guard.py`.
They distinguish a dependency path from chronological execution, check a
path ending partway through a decreasing edge, verify that sequential
decreases cannot be treated as parallel, and exercise the compiled forward
and inverse schedules, constant comparisons and alternate witness.

## 5. What assembly and bootstrap alone cannot amplify

With bit saving `a_b`, the present completed layer has exponent at least
`1-a_b`, giving `kappa < epsilon a_b`. Transform layout costs
`p K^(-a_b)` and the size constraint requires `K=o(ell)`, where
`ell=Theta(p^(1-epsilon))`; hence this layout also allows at most
`a_b(1-epsilon)`. The independent CRT/layout row has that same margin.
Together they imply `kappa < a_b/2` within this architecture.

Recursively using an improved integer multiplier for the packed polynomial
products improves only the already generous product margin. If its saving
is `kappa_0`, then that row changes from margin `epsilon` to
`epsilon+(1-epsilon)kappa_0`. The layer and movement rows remain unchanged.
Thus that bootstrap does not amplify the bottleneck saving.

Tensoring a completed primitive by ordinary recursive composition also
preserves its exponent: arity `m^t` with normalized branching `(s/W)^t`
has logarithmic exponent `log_m(s/W)`. It does not supply a stronger bit
primitive. Any many-order improvement must improve that primitive or prove
a different layout/whole-transform algorithm that bypasses these rows.

The one-stage scalar identity `SWAP = I + [I;I][I I]` in characteristic two
is a possible different architecture. Its transparent evaluation can
restore dirty scratch because equal additions to both banks preserve
`X+Y`. However the obvious frame assignment makes an early X injection
raise a scratch role to its target line, followed by a Y source-copy visit
at the zero frame. This introduces downward losses for side roles that were
monotone in the three-stage construction. No valid low-loss one-stage
assignment is proved here; correct scalar algebra alone does not establish
the required rank deficit.
