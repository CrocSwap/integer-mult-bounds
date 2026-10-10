# Gen5b donor-rank-weighted compensated matching

This package rebuilds compensated reuse after the producer's endpoint descent,
choosing donors by their actual final-frame ranks. It composes the resulting word
with all 1,720 PR299 kernel entries, 440 early restorations and seven terminal sinks.
The exact conditional finite bound is

**κ = 375528459906701 / 500000000000000000 = 0.000751056919813402.**

This is about **0.15438% above independently reproduced PR299**, whose bound is
0.000749899215319498. The improvement is a matching and composition result;
all inherited all-size hypotheses remain conditional. No global-optimality or
practical runtime claim is made.

## What changes

The exact post-descent donor graph contains 65,920 eligible edges. Rebuilding
matching there admits 1,728 reuse pairs instead of 1,726. Among maximum-cardinality
matchings, the donor-rank rule selects 878 rank-21 donors instead of 706. Higher
rank donors give a larger donor-only concave splice benefit for every fixed
exponent between zero and one. The proof is scoped to this fixed graph and
objective, not the whole construction; see [MATCHING-PROOF.md](MATCHING-PROOF.md).

All 904 scalar retimings and 220 target groups are rebound to the changed word.
Kernel entries are mapped through logical roles to the new indices and rechecked;
restorations and sinks are freshly screened. The original kernel, restoration,
sink, bank-checking, prime, moment, outer, mathematical and finite checker cores
remain unchanged. Exact initial counts, the global namespace, residual census
and expected derived values are specialized to the new word, retaining assertions.

| Quantity | PR299 | Weighted matching |
| --- | ---: | ---: |
| Reuse pairs | 1726 | 1728 |
| Final independent dirty registers | 15427 | 15425 |
| Literal stock, 60 replicas | 1229750 | 1229735 |
| Kernel entries | 1720 | 1720 |
| Early restorations | 440 | 440 |
| Terminal sinks | 7 | 7 |

The final invoice charges 913 endpoint charts, the conservative normalizer 815,
and 905,876,840,400 selector calls. Both cleanup and dirty old-value return remain
paid. The exact checks bind these costs to the actual emitted word and bank
assignments. The signed decoder is checked over the integers; only its F2
reduction is asserted to equal the identity target contract.

## Reproduce

Use Python 3.11 or later, SymPy 1.14.0 and a new output directory outside the
package. Each command is network-free after dependency installation.

```sh
python -m pip install -r research/gen5b-weighted-matching/requirements.txt
python -B research/gen5b-weighted-matching/verify.py \
  --output /tmp/gen5b-weighted-verification
python -B research/gen5b-weighted-matching/gen5bit/producer/regenerate.py \
  --work /tmp/gen5b-weighted-regeneration
```

`verify.py` freshly runs twelve stages: virtual, raw, bit, kernel, restoration,
sink, scalar, primes, banks, complex, mathematics and finite admission. It rejects
pin-recording mode, runs all retained negative controls, rejects missing stages,
and verifies the complete source manifest before and after execution. The result
is `verification.json` with detailed receipts beside it.

`regenerate.py` starts with the inherited module data and producers, rebuilds the
original word and endpoint descent, then executes the new weighted matching
producer. It cross-checks maximum cardinality using Hopcroft-Karp and checks all
local F2 and defining-integer-decoder columns. All five resulting bit files must
match the pinned submission, with gzip members compared after decompression.
Its matching receipt is `matching.json`. The dedicated workflow runs full
verification on Python 3.11 and 3.13, plus regeneration on Python 3.13.

The final virtual-word SHA-256 after decompression is
`9144bc371104df43abf65f8fcff7a0f195301118ccb4c37b02799799d9f2eec1`.
`SOURCE.json` records the exact PR299 commit and original-file differences;
`MANIFEST.json` hashes every packaged file. The original PR299 README and notice
are preserved as README-PR299.md and NOTICE-PR299.md. Other inherited discovery
scripts document upstream searches; the commands above reproduce and verify this
submitted construction.

The all-size compiler, common chart, restored rows, selectors, routing, prime
supply, precision/recovery, complex correctness and analytic interfaces remain
assumptions. Finite success does not certify the entire multiplication theorem.
