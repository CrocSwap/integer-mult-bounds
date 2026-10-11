# R740 replicated idle hosting

Conditional κ = **0.001246073505487942**, about **0.6886% above PR442**.
Compose PR443's rank138, R740, 32-replica bit word with PR442's idle-data
hosting interface and freshly reconstructed hosted complex supplier.

| Quantity | Bit supplier | Complex supplier |
| --- | ---: | ---: |
| Certified saving | 1247628141860215921989 / 10^24 | 1267453159029119 / 10^18 |
| Live families | 37,464 | 8,400 |
| Physical families | 37,473 | 8,978 |
| Largest child | 8 | 8 |
| Hosted helper residuals | 159,168 | 34,560 |

The bit word, 16 residual isometries, all local instructions, compressed schedule,
bridges and scalar replay are unchanged from PR443. Hosting reduces its live
stock from 56,739 to 37,464. All 53,952 remaining helper residuals tile complete
width64 banks; no padding is introduced. The bit deficit is 9,984 for 32 replicas.
The complex supplier is reproduced unchanged from PR442, including its phases.

## Reproduce

Python 3.11+, a C++17 compiler and Boost headers are required. Install the pinned
parent requirements, then run from the repository root:

```sh
python -m pip install -r research/e8-r740-replica32/parent436/requirements.txt
python -B research/r740-idle-hosted-replicas/verify.py /tmp/r740-hosted-new
```

The output directory must not exist. Set `BOOST_INCLUDE` when Boost is installed
outside the compiler's default include path. `--quick` skips only the inherited
PR443 exhaustive mutation suite; it still reconstructs PR442 and performs every
new hosting check. SciPy is unnecessary for verification: the integer selection
is frozen, and all capacities and assignments are independently checked.

The wrapper verifies 234 pinned upstream files, freshly runs both complete parent
verifiers, emits all 288 bit calls, independently audits every owner/window/bank,
recomputes the 5,681,952-instruction ownership digest, rejects 14 corruptions,
checks both rational moment engines and finite invoices, and verifies six
bootstrap levels, 47 strict outer inequalities and four outer controls.
`EXPECTED.json` freezes exact results; `RECEIPT.json` records the run and sources.

## Scope

This is a finite conditional certificate under PR442's idle-data hosting
extension and the inherited all-size compiler, restored-work, common-grid,
precision and analytic interfaces. The hosting operator lemma is inherited and
explained in `PROOF.md`; the address spaces are not numerically enumerated.
This does not prove κ = 1, an unconditional multiplication theorem, or a Lean theorem.
