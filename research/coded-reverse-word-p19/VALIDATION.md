# Validation

| Command | Result |
|---|---|
| `python3 -B research/coded-reverse-word-p19/p19_plain.py` | PASS: p=2/3/19 trace identity against `controller()`, p=19 diagonalisation with denominators `[1]`, census (36 retained idles, 198 rank), root 0.007578535, zero recodings |
| `python3 -B research/coded-reverse-word-p19/p19_claim.py` | PASS: prefix bounds, raw moment sign in two engines, charged tail ratios, shape-correct compiler ranks `H0 = 5170423668736`, BIT chain, budgets, outer ledger, three rejection controls |
| `python3 -B research/coded-reverse-word-p19/verify.py` | PASS: formal controller, word receipt, claim receipt |
| `python3 -B research/coded-reverse-word-p19/p19_word.py` | PASS: the coded overlay record (259 gates, 77 recodings, replay exact) |
| `python3 -B scripts/research_package.py --package research/coded-reverse-word-p19 --check-only` | PASS_PACKAGE_METADATA_AND_PINS |
| `python3.12 -B scripts/research_package.py --package research/coded-reverse-word-p19` | registered replay, Python 3.12 |

The long command is the p=19 trace (several minutes); the coded overlay replay is kept
as a record and is not part of the claim. No command performs a git write.

Open obligations carried by the claim: the 7,752 inherited helper units, the `0.97`
tail limit re-derivation, field-bill admission under the fixed-tape/precision ABI,
precision/tape/hosting, ambient-rank-153 replay, hosted CI and kernel review.
