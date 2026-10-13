# Exhaustive binary residual and phase-interface verification

**Independent finite verification; no new κ.** For the historical binary-frame
compiler and parity-side repair, a vector-set oracle checks all subspaces of
F₂ⁿ for **0 ≤ n ≤ 6**, all nondegenerate nested endpoint pairs, the exact
residual span, characteristic-vector criterion, and returned orthonormal bases.
For every admissible pair it checks the signed Hamming-weight phase identity on
every ambient input. No predecessor arithmetic is used as the oracle.

The exact base is `f567884aeb8851b6e794af1184119a3bfbe1e631`. The selected
conditional saving at that base remains `1661634653669567/10^18`; the selected
certificate, construction and maintainer review are pinned as context, not
replayed by this package. `upstream/` and all existing sources are unchanged.

## Reproduce

From the repository root, with **Python 3.10+**, standard library only:

```sh
python3 -I -B research/binary-residual-exhaustive/verify.py
python3 -I -B research/binary-residual-exhaustive/test_verify.py
```

Expected main output:

```text
PASS_BINARY_RESIDUAL_EXHAUSTIVE subspaces=3290 nested_pairs=29899 phase_inputs=1634803 controls=10 kappa=unchanged
```

The seven test groups also run under `-I -O -B`. The predecessor's assertion
preconditions are preserved by compiling its unchanged pinned source with
`optimize=0`, even when the independent checker runs under `-O`. This does not
assert that running the historical modules directly under `-O` is supported.
The independent checks use explicit exceptions, not assertions.

`--output /tmp/binary-residual-result.json` optionally writes the verified
receipt to a **new** file. It refuses to overwrite an existing output and never
writes on a failed source or receipt check. Default execution changes no files.

## Completed coverage

| Ambient n | All subspaces | Nondegenerate nested pairs | Nonzero alternating residuals | Admissible phase inputs |
|---:|---:|---:|---:|---:|
| 0 | 1 | 1 | 0 | 1 |
| 1 | 2 | 3 | 0 | 6 |
| 2 | 5 | 9 | 0 | 36 |
| 3 | 16 | 33 | 2 | 248 |
| 4 | 67 | 207 | 16 | 3,056 |
| 5 | 374 | 1,899 | 202 | 54,304 |
| 6 | 2,825 | 27,747 | 3,104 | 1,577,152 |
| **Total** | **3,290** | **29,899** | **3,324** | **1,634,803** |

Each space is presented twice: a canonical greedy set basis and its complete
vector list shuffled by seed 83, including zero and redundant generators.
The checker validates **6,580** classifications, **3,254** characteristic-vector
presentations and **3,010** accepted basis presentations; **3,570** inadmissible
presentations are rejected. All **1,627** equal nondegenerate endpoint pairs
correctly admit a zero residual, including alternating endpoints.

The enumerator adjoins every outside vector and deduplicates the resulting full
vector sets. Its dimension census matches the independent Gaussian-binomial
integer recurrence. A second, powerset-based test examines all 32,768 subsets
of the 15 nonzero vectors of F₂⁴ and recovers precisely the same 67 subspaces.
[EXPECTED.json](EXPECTED.json) freezes the full typed receipt;
[SOURCES.json](SOURCES.json) binds every predecessor executable input and cited proof/context file
by SHA256 and its exact base Git blob. Runtime does not require Git or network.

## What the result adds

The predecessor tests cover selected frame examples and one characteristic
example. This package covers every embedded subspace and nested nondegenerate
pair in the declared finite domain, including degenerate spaces, nonzero
alternating residuals, alternating endpoints and basis-presentation changes.
The direct radical, characteristic and projector calculations use coordinate
pairings and full vector sets, with no row elimination or predecessor imports.

Ten explicit controls distinguish rank from exact span, unit norms from mutual
orthogonality, weight-three phases from unit phases, and increasing from
decreasing edges. Test mutations also replace each of the classification,
characteristic, residual and orthonormal-output functions with faulty versions;
the checker detects them. Source drift, missing inputs, digest drift, incomplete
inventories, receipt-value/type corruption and failed-output preservation are
tested. The optimized minimal-closure replay runs in a path containing spaces.

[PROOF.md](PROOF.md) gives the mathematical dependencies and explains why the
criterion applies in all dimensions; that written argument is separate from
the finite replay and is not a Lean proof. No source defect was found in this
domain. This is neither a frame-search optimum nor an alternative kernel for
alternating residuals, and it does not validate the complete historical repair
cost, a selected supplier, a whole multiplication machine, or any new bound.
All inherited all-size/compiler, realization, hosting, precision/tape and
analytic assumptions remain.

The OS-random assignment seed is **83** (independent verification track).
[CLAIM.json](CLAIM.json) records the three candidates, local coordination claim,
domain, stopping rule and overlap check. PR771 checks full-space isometry-group
orders and invoices; PR831 studies F4 alternating phase interfaces; PR712
checks a single cold-wrapper phase certificate. This all-subspace residual
census is distinct and consumes none of their pending code. Credit Douglas R.
Colkitt and the original OpenAI manuscript; see [NOTICE.md](NOTICE.md) for
predecessor credit, Apache-2.0 licensing and substantial AI-assistance disclosure.
