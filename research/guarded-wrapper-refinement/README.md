# Run dense native wrappers directly on their invariant lattice

The original paired P104 collector needs **104 wrapper-level lifting calls
instead of 416**. Keep one guard across each complete native monomial wrapper
and execute its reversible address word directly, eliminating the enclosing
protected-XOR-oracle conversion. The query, adaptive grid and private-zero
return are identical to pinned [PR3131](https://github.com/CrocSwap/integer-mult-bounds/pull/3131).
This is a scoped implementation simplification, with no new kappa.

The key is that the credited address word already preserves a known scaled
Gaussian integer lattice. Its output can be contracted directly; it does not
need a second copy of the input and a replay merely to become in-place.
The backend's **internal** history, source preservation and cleanup remain
paid. [PROOF.md](PROOF.md) states the invariant, signed backing, complete
local invoice and inherited physical premises.

| Actual paired-collector wrapper work | PR3131 | This refinement |
|---|---:|---:|
| Field gates | 52 | 52 |
| Inner lifting calls | 416 | 104 |
| Enclosing address-oracle calls | 104 | 0 |
| Guard embeddings / contractions | 104 / 104 | 4 / 4 |

On four same-input N=512 **Python semantic collectors**, three timed runs
after warmup give median speedups of **2.62–2.66x** on the recorded Linux/Python
3.12.14 environment. [BENCHMARK.json](BENCHMARK.json) records all samples,
input/output hashes and environment. These timings do not execute or measure
the fast physical C machine. The conditional time and clean-space exponents
from PR3131 remain unchanged, as does the supplier's rank invoice.

## Reproduce

Python 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/guarded-wrapper-refinement
```

Expected: `PASS_GUARDED_WRAPPER_REFINEMENT wrapper_lifts=416->104 collector_cases=4`,
then `PASS_REGISTERED_RESEARCH_PACKAGE` with `outcome=completed`.
The verifier compares its deterministic output with [RESULT.json](RESULT.json).
For a separate timing run:

```sh
python3.12 -B research/guarded-wrapper-refinement/benchmark.py --runs 3 --output /tmp/guarded-wrapper-benchmark.json
```

All paired output hashes must agree; timings vary. The benchmark preserves the
same inputs, 512-bit working width and backend plan for both implementations.

## Coverage and independence

The package includes a separately written guarded wrapper, symbolic affine-word
validator, exact Q(i) identity checks, parity-formula lift interpreter and
tensor address oracle. It checks 1,250 signed pair cases, 13,122 exhaustive
two-axis gate cases, sixteen actual-wrapper cases, sixteen synthetic tensor
cases and four complete collectors, including large cancellation and zero sums.
The bit-boundary check covers 9,144 signed embeddings/contractions and 196
phase-changing outputs, returning actual low/high ancilla bits to zero.

Controls cover incorrect compiled words, omitted phases, unguarded wrong
endpoints, invalid layouts/types, overflow, dirty low bits, corrupted sign
extension, inverse faults and changed source bytes. A wrong phase can preserve
the lattice, so zero guards alone are deliberately insufficient for acceptance.

PR3131's compiler, core/backend and collector are frozen and reused for
differential comparison. Calling that code is **not** an independent audit of
those components. The executable is a semantic model, not an all-size
physical trace. Parameterized correctness follows from the written argument
under the scalar-period and backend hypotheses. Clean-stock hosting, physical
routing/history, source/compiler/precision refinement, full P104 supplier
admission and the multiplication theorem remain separate.

## Pins, scope and credit

- Base main: `997e6a9ca7b4f95d50e366f61412fd640d72a88a`, priority revision 6.
- PR3131: `0c9e344d5a5295a218558fa4a51d867f39ff5311`.
- Its frozen PR3109 backend: `15eac811648182bdac7254a91fd9b841b1414ebc`.
- Selected accepted conditional kappa: **0.001672660197076918**, PR1094.

[PREDECESSOR.json](PREDECESSOR.json) authenticates every byte and Git blob of
the unmodified eleven-file PR3131 archive. [SOURCES.json](SOURCES.json) pins all
eleven external replay inputs, plus catalogue and selected-record provenance.
Original source documents and credits remain inside the archive. The verifier
compiles authenticated archive bytes directly; it does not extract or import
cached predecessor bytecode.

Credit Jose Manuel (`jmbarrancoml`)'s dense collector and PR3109/2287/2250/2899
implementation chain; Tekalign's PR3025/3033 pair and scalar-period identity;
Ross Richardson's PR3072 block evaluation; Douglas Colkitt's character
conjugation; ywz65's native recipes; Vasek/flyingviper's frozen-consumer audit;
and the retained source lineage, including Nick Petalas and David Arias.
PR3122/3129's checkpoint history work is complementary and is not composed here.
The elementary invariant-lattice restriction is not claimed as a new general
algorithm. Earlier affine/phase certificates, including PR712, have a different
scope from this changed execution boundary.

Prepared by **Tekalign, with substantial OpenAI Codex assistance** in analysis,
implementation, testing and writing. Apache-2.0. No independent human review
or proof-kernel verification is claimed.

## Open next questions

- Lower one direct guarded wrapper to the actual fast physical backend, with
  literal sign/guard backing and private-history return. The first step is a
  complete execution trace; physical C/compiler realization remains a blocker.
- Find a changed complete producer/consumer profile that can afford the
  correction and its clean stock. The frozen consumer's `599/584` zero-saving
  obstruction is unaffected. First price that full contract, rather than
  interpreting fewer wrapper calls as a new supplier exponent.

[TASK.json](TASK.json) records the seed-78 selection, alternative tasks,
changed card scope, stopping rule and structured handoff questions.
