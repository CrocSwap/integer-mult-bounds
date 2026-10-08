# Typed exact-matrix synthesis catalogue

This local standard-library prototype turns the personal July/October matrix composition interface into a domain- and model-aware finite catalogue. It admits actual coefficient/leaf recipes, records denominator recovery and rejects product counts promoted to tensor rank or recursive outer validity without the required identities.

Run from this directory:

```
python catalogue.py --order 16 --domain Q
python catalogue.py --order 16 --domain GF2 --model native_field_products
python catalogue.py --order 16 --domain GF2 --allow-charged-lift
python catalogue.py --order 17 --domain Z
python audit_catalogue.py new-audit-receipt.json
```

The audit refuses to replace an existing receipt. The current completed receipt is `audit-receipt-pr48-current.json`. Its 15 groups replay actual ordered coefficients, complete mixed-input polynomial leaves, model/domain rejections, signed modular quotients, fringe/padding charges and 16 concrete hierarchical matrix executions. This new Python tool is not formally verified in Lean.

## Admitted ingredients

| Ingredient | Evidence and permitted role |
|---|---|
| DPS order-four outer, 48 products | Pinned actual integer tables; all 4096 ordered coefficients replayed; denominator eight. Block-stable outer in compatible realization. |
| Strassen order-two outer, seven products | Explicit adapter and all 64 ordered coefficients replayed. Integer-coefficient block-stable outer. |
| Rosowski even-order scalar leaf | Actual division-free P/R/Q/M recipe; complete polynomial replay at orders 2, 4, 6, 8 and 16; general source identity. Commutative terminal only. |
| Personal order-16 circuit, 2208 products | Actual source composition and integer late-division proofs. Mixed-input terminal only; numerator eight times the matrix product. |

The stored personal package is pinned at `7203497dc990e47c2391bff1b9863408d817faeb`, with proof edition `9e13c89a51a62958ced9ebdf16da31f5e2fb3cdd`. Its source inventory checked 95 files and all 11 Lean module hashes. DPS and Rosowski remain credited known components. Historical order-nine counts, the disputed order-27 advertised count, odd-leaf formulas and the third-party Chandra family are clearly marked unimported; their numerical counts are not automatically admitted.

## Domains and costs

The selected construction has 2208 scheduled variable products and 256 fixed final divisions over integers. Those counts exclude additions, fixed coefficient scales and movement. They do not assert bit complexity or measured runtime.

In GF2, direct division by eight is rejected: the scaled outputs for zero and one both reduce to zero. The optional charged route evaluates the integral numerator modulo 16, retains four-bit residues rather than one-bit GF2 values, then performs 256 exact quotients and 256 target reductions. It also records 512 input representative lifts. These are lifted-ring products, not 2208 native GF2 field multiplications or a GF2 tensor-rank claim. The `native_field_products` model rejects that route.

The finite supplied catalogue constructs a native GF2 order-16 route with 2212 products: the explicit seven-product Strassen outer with the executable order-eight Rosowski leaf of 316 products. This is checked by both its component identities and fresh matrix execution. It is a minimum within this supplied finite catalogue, not a strongest-known algorithm. The rational bilinear model separately produces a 2304-product upper bound from two actual 48-product outers; it excludes all mixed leaves.

Exact factor chains use block-stable outers and a scalar terminal. A fixed terminal changes the constant in `C_t=46*48^t`, `n_t=4*4^t`; its exponent is `log(48)/log(4)`, not `log(2208)/log(16)`. The audit includes the actual noncommuting block counterexample: with all B blocks zero, the Rosowski P/R pair returns `UV-VU`, which is nonzero over both integers and GF2.

For arbitrary order, the fringe route pays `n^3-floor(n/p)^3*(p^3-Cp)` products and retains all kernel recovery operations. Padding pays every padded slot unless an actual zero-pruning adapter is supplied. At order 17 the order-16 fringe gives 3025 products; the cited odd-order direct formula gives 2737 but its executable odd leaf is not imported here. No global comparison follows from the catalogue result.

## Integer-multiplication search boundary

The exact community eligibility gate is pinned to PR48, `b7194b8586844956904b33e9fe18f0c75606c11b`. Its bit saving is smaller than its complex saving, and the bit/assembly margin binds. A matrix product count or improved complex precision does not supply a new bit-interchange child profile or new kappa. The gate lists the missing physical, moment, analytic and assembly obligations.

The separate metadata snapshot of PR49 at `f95d2910e027495983b53cae1693cf535abf2569` reports conditional kappa `4.123863984e-5`, updated October 8 at 15:45:26 UTC. Its title/body are submitted claims, not independent mathematical acceptance. They supersede the PR48 numerical checkpoint and the local 48/47 composition comparison. The catalogue retains the clearly scoped PR48 gate; it makes no global record claim.
