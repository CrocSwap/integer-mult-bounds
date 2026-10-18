Retained source report SHA256: `f853e2471eb018f07b21ed7a926d7442233c54abb944a0334602ed3046810a18`. Local path prefixes are redacted; this is a review derivative.

# Integrated independent-controls source review

Read-only review by `/root/completion_evidence_audit`, 2026-10-13. No module was imported or executed; no benchmark, mathematical job, or source edit was performed. This is a hash-bound source review, not a certification of a control/replay run. The coordinator owns actual execution and its receipts.

At checkout `kappa-phase-reuse-20261013`, source base `8bddbee377e2f3ce1f1247196c4b290d55767d20`, reviewed current files are:

| Repository-relative file | SHA256 |
|---|---|
| `research/clifford-state-reuse/verify.py` | `dda9bbc5e31f66fb66e10efd43aa04009754f14db6ba7f340f7af36d4bf47b99` |
| `research/clifford-state-reuse/semantic_controls.py` | `c7f1b612c720904448d2112721d56bd130ed393ae460a7b30a8a5852c76646e6` |
| `research/clifford-state-reuse/controls.py` | `789ed44f24c9cf863e8e190b641ae3ab61f3a8bb51ca1573b8e9195f4dcb88fc` |
| `research/clifford-state-reuse/probe.py` | `903565d1db5ac8acc83539d63fea9b884802c93cbfc474cc6f79a0da146b5a88` |

The retained compiler and sole transformed candidate remain bound to SHA256 `2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962` and `6fac2848d3a0c0dfa92f83c8636beb903083cce1b01bda8ef582514071429221`. Their exact gate/monomial source was inspected alongside the independent oracle.

## Findings

No remaining source-level correctness blocker was found in the reviewed versions. The one reproducibility issue raised during this review was fixed before the final pins above: the oracle's three CLI guard children initially omitted isolated Python flags. The earlier oracle SHA was `a20b09aefadcc02d2d7aed345579bac3e1e5644b88e796314b8c00ecb298476d`, with integrated verifier SHA `9138d85713d407bbc6f82e1891b54d1e9ec1efef8c117c092e61222bd97abe7a`. Under inherited `PYTHONOPTIMIZE`, a source-mutation child could stop at the assertion-mode guard rather than its intended source guard. Current `semantic_controls.py:299-304` uses `-I -B` for all children and adds explicit `-O` only for the assertion-off child. Current `verify.py` pins that corrected oracle. Earlier execution receipts must keep their earlier hashes; this source review does not relabel them.

## Independent circuit semantics

The oracle evaluates each declared literal circuit on every basis column using pairs of exact `Fraction` values. It does not call the supplier's rank, matrix/vector, phase, or state evaluator to establish the expected matrix. Supplier constructors and lowering are the objects under test.

The gate formulas match the pinned compiler:

* `P`: explicit GF(2) row dot products map each basis index to its image; an independent collision check verifies invertibility. This matches the compiler's row representation and `mv` action without using that helper.
* `X`: the vector permutation is `state[x ^ offset]`.
* `D`: the independent exponent is the linear Z4 term plus twice the upper-triangular quadratic bit sum, modulo 4. The compiler uses parity for that quadratic sum; twice either expression agrees modulo 4.
* `phase`: literal multiplication by the specified power of `i` is retained.
* `C`: the oracle applies `(1 + sign*i)/2` on the current amplitude and `(1 - sign*i)/2` on the shifted amplitude. Expanding these Gaussian products gives the compiler's exact integer-numerator update divided by 2, for both signs.

Each input constructor must preserve the literal declared word. For both engines, the independent expected matrix is compared with the input circuit and the compiled circuit on all basis inputs; input immutability and exact recipe/tableau/circuit equality across engines are checked separately. The `n=0` phase-only cases exercise the empty-register boundary.

## Coverage arithmetic and guard reachability

The fixture inventory follows directly from `fixtures()`:

| Dimension | Cases | Basis columns summed |
|---:|---:|---:|
| 0 | 4 | 4 |
| 1 | 24 | 48 |
| 2 | 33 | 132 |
| 3 | 46 | 368 |
| Total | 107 | 552 |

There are 36 seeded five-gate compositions, 214 input-matrix comparisons, 214 compiled-matrix comparisons, 107 exact cross-engine output pairs and 214 input-immutability checks. Four full matrix comparisons per fixture give `4*(4 + 24*4 + 33*16 + 46*64) = 14,288` matrix entries. The rank histogram is obtained from the lowering outputs; ranks are independently constrained by declared expected ranks for the named phase/translation/permutation/diagonal/C/full-rank fixtures. The random compositions receive full matrix checks but no separately recomputed GF(2) rank claim.

`monomial_control()` instruments actual methods while retaining the checked compiler source, and restores both methods in `finally`. It checks the deepest caught frame is `monomial` and requires concrete state/output events to distinguish the intended guards:

* The phase fault changes the compiled circuit's final phase while preserving its entire Pauli tableau. Canonical denominator and support pass, the final output state is evaluated, and it differs from the input state. Rejection therefore reaches the final phase equality rather than an earlier tableau guard.
* The support fault supplies a literal `X` circuit with the identity tableau, producing normalized support off the asserted offset. No phase-output object or output-state evaluation may occur. The independent oracle confirms the observed input column, isolating the retained support guard.
* The denominator fault doubles both Gaussian numerators and raises the denominator by one. Exact rational amplitudes remain unchanged, verified against the independent oracle; the noncanonical denominator alone violates the normalization guard before phase construction.

Each engine has three positive guard invocations and three negative invocations, totaling six of each. The three positive invocations deliberately use the same valid phase circuit; they are six guard-reaching runs, not six distinct circuit fixtures. The separate CLI controls require specific rejection text, nonzero exit and absence of a success receipt for wrong baseline bytes, wrong candidate bytes and optimized Python. Both source hashes are checked before either compiler is loaded, and `load_bound()` executes the already checked bytes rather than rereading them through the loader.

## Preflight integration, source and budget checks

`verify.py:113-164` hashes the independent control source against its exact pin, copies it to fresh external work, and invokes that copy with `-I -B`. It requires a successful fresh semantic receipt with the exact baseline/candidate/control hashes, 107 fixtures, 552 columns, 12 mathematical guard invocations with six rejections, and three CLI rejections. Because the complete control source itself is pinned and freshly executed, these counts supplement rather than substitute for the mathematical checks inside it. Original/copied control bytes and generated compiler/driver bytes are rechecked after preflight. The semantic receipt and actual command/log are separately bound by `SEMANTIC-RUN.json`.

The preflight is mandatory before any full phase subprocess. Its subprocess cap is `min(120, remaining allocation)`, with timeout logging and incomplete status. The full allocation clock starts before preparation and includes preflight; remaining phase-child budgets and final acceptance checks are retained. A preflight failure cannot produce a complete phase PASS. The prior review's distinction still applies: an external whole-command supervisor is needed to interrupt blocking preparation, terminal writes or in-process probe work; internal acceptance checks are not a universal I/O interrupt.

The supplementary driver still checks every actual U8 edge/adapter and exact full recipe bytes after successful preflight. Complete phase coverage, the benchmark timing pairs and any speedup are separate execution obligations. These finite oracle controls do not establish complete U8 coverage, all Clifford algebra, any changed-word transport, supplier hosting or a multiplication theorem by themselves.

## Additional driver-controls source review

`controls.py` contains nine rejection cases: optimized Python, input container pin, retained compiler pin, retained driver pin, existing-work preservation, inside-checkout output, generated compiler pin, independent oracle pin, and an actual one-second phase-child timeout. The timeout case requires a terminal `FAILED_OR_INCOMPLETE` result with exactly one phase job marked `ALLOCATED_HARD_TIMEOUT`; a failure before reaching that child does not count as success. Existing-work and inside-checkout cases check preservation/absence of their sentinels. Positive integrated preflight and isolated hostile-environment execution are separate cases. Retained source/input bytes are checked again at the end. This source supports the reported case names/counts; actual outcomes and outer-controller enforcement were not independently inspected here.

The integrated code is suitable for the coordinator's allocated full verification, subject to the already stated outer resource cap, fresh work and execution evidence. This review authorizes no job and certifies no performance result.
