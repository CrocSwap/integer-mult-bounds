# One arithmetic circuit for all runtime residue pairs

One fixed reversible circuit implements a draw for all **144** nonzero
denominator-13 residue pairs supplied at runtime. It uses **14,022 gates**
and **2,146 clean work bits**, including parameter arithmetic and cleanup.
Both parameters and the coin remain unchanged. The original ordered
coin-to-label function and first stopping depth are preserved.

Read [the contract and proof](PROOF.md), [the circuit generator](parametric.py),
[the exact bill and pair certificates](RESULT.json), [the checker](verify.py),
[source pins](SOURCE-PINS.json) and [source credit](CREDITS.md).

The circuit computes four weight residues from one phase and two four-bit
parameters. It replaces transition-data lookup with arithmetic. This is a
larger input domain and a larger circuit than the fixed-pair predecessor;
no physical speedup or total-code-size saving is claimed.

Python 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/runtime-paired-ddg-arithmetic
```

Both registered commands print:

```text
PASS_RUNTIME_PAIRED_DDG_ARITHMETIC
144 runtime pairs; 89856 complete forward/inverse transitions
864 X; 10054 CNOT; 3104 Toffoli; 14022 gates
2135 temporary bits + 11 clean backing bits = 2146 clean work bits
```

All 89,856 reachable edges agree with the unchanged source constructor
and a separate integer-floor description. Every output and work wire is
checked in both directions. A scalar interpreter checks 288 cases in both
directions. All 28,561 subtraction inputs, four fault controls and the
unchanged fixed-pair verifier pass. No historical full catalogue, native,
selected cold, Lean or Docker replay is claimed.

No new kappa follows. Stopping time remains unbounded. Physical tape
movement, parameter loading, output retention, stopping storage, conditional
freshness and a reached nonadaptive caller remain separate obligations.
The selected frontier and all five framework assumptions remain unchanged.

## Open next questions

- Install this fixed circuit in a stated tape layout and charge access to
  all wires, parameters and consumed coins for a terminating path. Compare
  the counter and owned-delimiter boundaries before selecting one.
- Can a smaller exact circuit retain the same runtime input and ordered
  output contract? Start with the complete transition certificate and
  count preparation, inverse computation and cleanup together.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
