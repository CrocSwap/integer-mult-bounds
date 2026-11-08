# Connect actual Toeplitz programs to rounded native calls

**Scoped written theorem and source-bound implementation. No new κ.**

The actual Full Toeplitz lowering in #4253 budgets coefficient/data rounding
but executes exact H/2 stages. Its last proof paragraph leaves additional
native error unfunded, and its data can exceed a unit-disk native service's
input domain. This package derives requests from the real source word and
executes it through a concrete rounded Gaussian backend with a complete
range and error contract.

## Result

For every admitted rational Toeplitz root of dyadic size N, either source
direction, input Euclidean radius R, incoming width F0 and target 2^-t, we prove:

* every actual native entrance is within the complex unit disk;
* forward or stored-inverse output error is strictly below 2^-t;
* online coefficients, data and arithmetic temporaries have width
  `O(F0+t+log N+log lambda+log Q+log R)`;
* all original pages, matching/routing order, inactive coordinates and host
  rounding sites are retained.

[PROOF.md](PROOF.md) states the precise inherited leading-section, coefficient
and linear-prefix contracts. The service may be nonlinear on actual stored
inputs. A zero-defect service exactly reproduces the original rounded source
trajectory.

For source prefix/endpoint bounds C,E0, actual H count h, original complete
error budget B0 and Delta=2^-t-B0, choose a power of two S>=8 C(R+1), retain
the extra incoming bits F'=F+log2 S, and request whole-field tolerance

```
sigma <= min(Delta/(4 E0 C h S), 1/(8 C^2 h)).
```

The complete normalized vector remains within norm 3/4. Final error is at most
B0+Delta/2. H-free and empty words bypass requests. The proof propagates realized
residuals through linear stored-coefficient segments; it does not assume a
nonlinear rounder is Lipschitz.

The concrete service invokes the unchanged #5485 integer C0 butterfly using
`H/2=((1-i)/2) diag(1,i) C0 diag(1,i)`. It batches at most four physical pairs
into one eight-slot local call, charging padding for N=2 or4. Kernel rounding
remains nearest-even; host rounding remains the source's nearest/upward rule.
This is a direct implementation with explicit arithmetic and buffer costs,
not the selected accelerated supplier.

## Novelty and prior coverage

#4205's later full proof substantially covers the older #1797 accretive Schur
question. #4755/#4976 audit physical/matching cuts; #4852/#4977 refine the
downset bound and allocation. We did not repeat those lemmas or infer a proof
gap from an unmaterialized circuit.

#4178 supplies a tensor scan with an exact C/H interface. #4253 stops before
funding imperfect physical H calls. #5485 implements rounded C for another
port. The new result connects the actual Full stage producer to that concrete
backend, proves the whole-program domain invariant and pays every introduced
defect and normalization.

## Evidence and reproduction

From the repository root, CPython3.12 and standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/full-native-domain-adapter
```

Registered normal and optimized runs print `PASS_FULL_NATIVE_DOMAIN_ADAPTER`
and compare the complete [RESULT.json](RESULT.json). Exact pins and replay
inputs are in [SOURCES.json](SOURCES.json) and [VERIFY.json](VERIFY.json).
Base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision8.

The 17 trajectories use seven actual Full roots in both directions and three
generic edge programs. They execute 8,154 native calls, 32,616 Gaussian
butterflies, 1,836 nonzero internal roundings, 62,319 host complex roundings
and 128,220 real diagonal products. Cases include complex/non-Hermitian/
indefinite matrices, tiny and large scalars, reversed wires, 512-bit incoming
data and zero-layer shears. Separate exact matrix elimination checks root
and inverse endpoints; direct pair formulas check each actual native defect.

Thirteen control groups address actual unscaled domain failure, normalization,
coordinate versus whole-field tolerance, native bit selection, incoming-height
loss, host ties, internal overflow, malformed requests and changed source,
pages or allocation. Three additional bounded nonlinear probes test robustness
to input-dependent defects; they are not claimed Gaussian fault patterns.
Finite evidence corroborates source binding, not the universal theorem alone.

## Scope and costs

The adapter retains 4MN real diagonal products, JN complex host roundings and h
native calls, adding two rescaling visits and a separately counted input check.
The direct backend pays phases, lifts, normalization, local padding and owned
packing-buffer writes. The optional exact observer is outside production cost
and space. [PROOF.md](PROOF.md) gives the complete arithmetic budget.

No faster multiplier, selected-rate physical callee, fixed-tape realization,
coefficient delivery, full Gaussian/core/halo assembly or discharge of all five
assumptions is claimed. The global #3627 backend assumes
log(global field size)=Theta(precision). Local tiles with log N=O(log p) and
precision Theta(p) do not inherit that rate through isolated invocations.
The selected conditional κ remains 0.003125804.

## Open next questions

1. Connect the request to a complete global tensor/direct-sum caller satisfying
   an accelerated service's field-size, stock, spectator and ownership contract.
   Start with one actual global H event and its adjacent nonconstant diagonals;
   complete export and selected-rate service contracts remain blockers.
2. Price preparation/delivery of the unchanged coefficient pages on the enlarged
   common grid. Begin with an explicit physical record layout. O(p) numeric
   widths do not prove a tape tariff.
3. Carry one fixed reference/error contract through the complete Gaussian outer
   to exact integer recovery. Start with the existing core/halo ownership
   interface; global analytic composition and physical costs remain open.

[TASK.json](TASK.json) records the task refinement and bounded overlap coverage.

## Attribution

Prepared for **@CubeJerry**, with substantial OpenAI Codex assistance in source
analysis, mathematics, implementation, exact checks and writing. Coordinated
AI review belongs to that author process; independent human and formal-kernel
acceptance are not claimed.

Credit Jose Manuel/jmbarrancoml for #4205/#4253/#4178 and the Full numerical
compiler; Vlado Vojdanovski/#1673 for the underlying circuits, routing words
and Toeplitz structure; Chafik Boukhalfa/#628 for retained certified phases;
JoyboyBrian/#5485 for the fixed-grid C0/C2 implementation; and the classical
perturbation and Schur/LDU methods in those sources. Frozen source bytes and
license notices remain untouched. New work is Apache-2.0.
