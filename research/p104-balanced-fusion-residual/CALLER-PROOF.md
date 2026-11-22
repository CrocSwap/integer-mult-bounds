# The 36-call effect of the two-hop balanced fusion

The literal #8027 candidate in `pinned/ONE-RESIDUAL.json.gz` changes the rank-four contacts at clocks 7112 and 7210 into one rank-eight contact. Its source-local normalized map equals the native map on 629 of 630 output rows; row 130 instead contains the required value plus input 38. The changed source remains a rank-630 map. This result concerns the **constructed tape with its chart-1 SWAP and six ADD repairs**, not an assumed free or hypothetical terminal decoder.

For the pinned complete paired BIT word, none of the 36 LOCAL placements works by itself, and **no nonempty subset of these same literal replacements cancels** on the arbitrary-field source contract. In particular, seven or more uses cannot be admitted by relying on cancellation. The proof uses binary constant address fields, which are a subset of the source's permitted arbitrary whole fields. It does not assert that every such source assignment is reachable from a particular pair of top-level integer operands.

## Exact diagonal witness

There are 18 stages and two root-role lanes. Number stages `s=1,...,18` and set lane base `b=0` or `19`. The local extra term reads the first local role's port 38 and XORs it into the second local role's output port 19. The unmodified caller operates identically and independently on every port when the fields are binary constants. A forward caller-prefix pass shows that the source is the role form `e_b + e_(b+s)`; an independent reverse caller-suffix pass shows that the output response is the same form. The entire error matrix for this placement is therefore

```
(e_b + e_(b+s)) (e_b + e_(b+s))^T,
```

from port-38 source roles to port-19 destination roles. These cross-port errors superpose across placements: a changed call does not modify port 38, and the rest of the caller never couples ports 19 and 38. For any nonempty selected subset, take any selected `(b,s)`, set only source owner `(root,b+s,38)` to constant one, and set every other source field to zero. The output `(root,b+s,19)` is wrong. Its diagonal coefficient occurs in no other placement, so this witness survives all other choices in the subset. The 36 placement matrices consequently have rank 36.

For the 268-factor, floor-15 source choose all other 267 factors to be the `(root,0,0)` target of rank 127. Every first-factor target is retained because `4*127^267 > 15^268`. The explicit single- and multiple-placement witnesses are therefore inside that source-service domain, rather than a hyperplane of fresh-zero helper banks. The source-service argument does not prove higher-level operand reachability.

## Independent checks and debt

`constant_composition.py` verifies the graph and caller hashes, the full native and fused 630-row normalized maps, an independent reverse-mode transpose of both, source chart and owner lifetimes, the exact paid-rank change, and all 3,433 private clears. It replays all 4,218 independent root variables forward and in a separate reverse-mode pass for each of 36 placements; all 14,688 helper outputs form unchanged identity blocks because they do so in the checked local map. It verifies the explicit placement matrices and four multi-placement controls.

`caller_dual_check.py` is independent of that checker: its caller-prefix and reverse-suffix passes separately derive all 36 source/response pairs, verify the unique diagonals and retained-suffix inequality, and reject a changed-caller control. `candidate.py` rebuilds the literal source from the original graph and checks its normalized operator, transpose, private clears, and a corrupted-instruction control.

All 3,433 native and candidate private clear payloads are symbolically nonzero on arbitrary inputs. Seven clear owners change their symbolic data while remaining at their original clear charts: `2241, 2242, 2252, 2477, 2898, 3317, 3318`. Their original and changed supports are in `constant_composition.json`. Their erasure remains a physical debt; matching normalized rows or counting dirty clears is not a physical owner/erasure replay. The checked reverse passes give the **algebraic transpose of the normalized linear map**; they do not execute a physical reverse program through dirty clears.

## Replay

```sh
python3.12 -IB constant_composition.py > result.json
cmp result.json constant_composition.json
python3.12 -IB caller_dual_check.py > dual.json
cmp dual.json caller_dual_check.json
python3.12 -IB candidate.py pinned/strong-bit.json.gz rebuilt.json.gz
python3.12 -c 'import gzip; from pathlib import Path; assert gzip.decompress(Path("rebuilt.json.gz").read_bytes()) == gzip.decompress(Path("pinned/ONE-RESIDUAL.json.gz").read_bytes())'
```

The reconstructed uncompressed word is compared to the authenticated retained word; gzip bytes can differ with the compression implementation.

The source graph is SHA-256 `74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326`, the paired caller `757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b`, and the compressed candidate `7fa5589301124788237a569c3c0bbc0783f70efd840b15238300b8a2d5ab1cd7`. The candidate was built by the joint architect; the complete-caller and independent prefix/suffix checks here use that exact source. No publication, actual complete physical supplier, or κ gain is claimed.
