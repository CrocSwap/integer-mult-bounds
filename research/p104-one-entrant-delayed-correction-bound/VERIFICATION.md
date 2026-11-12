# Verification

Run the command in the README with CPython 3.12. The launcher checks path-keyed SHA-256 input and engine hashes in `PINS.txt`, rejects duplicate paths, expands the bundled Stage 1 receipt, and reconstructs the following outputs. The embedded hashes bind exact receipts, including test keys and rational covectors.

| Receipt | SHA-256 |
| --- | --- |
| 119-case scan and three exact spans | `a5ad6b1d6a0aeb376ca9b945de03f44e40fb177225133b0fdd3a6466313b2fa3` |
| Independent 12 entrant tests and one augmented span | `1c2193b302e6ec8e26d755c03e6c7e462cd3fb44af9d73dad438834a0a900ac6` |
| Lead 12 entrant tests | `f2af3d476dd24e49653b7bff45276d308a3067aa2bfc86cdef7c24bcff79d2a3` |
| Lead rank-203 augmented span | `125ee63c390ec7a62bce9d14181bd4b66cfc0fcd89e1d48ef396cc7a93ec3ef2` |
| Lead alternate separating input | `72d244dc76debc2fd46f1b8d1c205a4b1179daa3d2c2bd463d2177b1d0544dbd` |

Each completed scientific runner exits zero. The 119-case survey, three-case first span scope, and 12-case entrant gate exhausted their frozen scopes before their time limits. The single augmented solve exhausted its one-case scope. Four other augmented spans were outside the case cap. The replay also requires rejection of a deliberately changed frozen cut receipt.

The older exclusions are authenticated predecessor inputs. Their full recomputation belongs to the independently runnable #7434 and #7436 predecessor packages. Hosted checks are tracked on the exact PR head when opened. Full candidate verification does not apply because the tests produced no candidate.
