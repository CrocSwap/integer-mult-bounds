# Paired-plane two-edge switch: exact 30-unit copy reduction

## Result

For the selected 112-port family pinned below, release the exact deterministic matching used by the predecessor and replace two of its edges. The predecessor's slots 31 and 32 are `(90,42)` and `(87,44)`; the new edges are `(87,90)` and `(42,44)`. With the same zero-dot edge rule, this changes the exact B14 support-pairing invoice of the paired-plane factorization from 126 to 96.

This is a completed local construction optimization. It does not establish a new supplier, a scalar masked-plane decoder, a new selected record, or a new `kappa`.

## Construction and exact accounting

The port labels are the 112 vectors `q_i` in the selected replay's `DATA-PHASES.json`. An edge joins distinct labels with `q_i dot q_j = 0` over F2. For each matching edge `(i,j)`, use the two-column matrix `A_k = [q_i q_j]`. The deterministic zero-free-variable solution gives

```text
sum_k A_k M_k A_k^T = I_9 over F2.
```

The candidate's 56 matrices have ranks `{0:44, 1:7, 2:5}`, so 12 are active. Decomposing those active terms into their supported query columns and computing each exact B14 rectangle rank gives `{7:5, 8:2, 9:5}`, totaling `5*7 + 2*8 + 5*9 = 96`. The predecessor matching's corresponding total is 126. The saving is 30 units, or `5/21` of that predecessor invoice.

The verifier exhausts the full two-edge-switch neighborhood of this pinned matching: `2 * binom(56,2) = 3,080` possible reconnections. The edge predicate rejects 2,414. Every one of the remaining 666 matchings has a consistent 81-by-224 factorization system; all are solved, checked against the exact local identity, and priced. The 96-cost candidate is the unique minimum in this finite neighborhood. This is not an optimum over other matchings, other switch depths, or other factorization models.

For each candidate paired edge, the exact Gaussian-integer operator replay checks `C_qi C_qj C_qi C_qj = X_(qi+qj)` on every one of the 512 dirty 9-bit basis states. This gives 28,672 endpoint checks for the 56 candidate planes. The full-port matrix identity is also reconstructed from the candidate's query columns. As shown by the pinned scalar-mask obstruction, that full F2 factorization alone is not a scalar decoder and cannot be priced as a hosted scalar route.

## Screening implication

Splicing the exact candidate query-rank profile into the selected local-word profile and running the pinned `complex-local-word-ceiling/ceiling.py` gives the exact grid bracket

```text
a in [4864733253/10^12, 2432366627/500000000000]
planning kappa cap = 2432366627/502432366627 ~= 0.004841182193992213
```

This is only a favorable selected-complex-side relaxation with two unpaid coordinates. At the selected complex lower endpoint, adding 67 rank-one-equivalent profile units together with the same 67 units of centre charge remains below one; 68 crosses above one. This records a conditional screening margin for future route work. It does not include or establish the scalar decoder, its interface transitions, a supplier, outer assembly, or a selected-bound improvement. The bit-side lower bound remains a separate constraint.

## Reproduction and pins

At repository root, run:

```sh
python3.12 -B research/paired-plane-local-swap-seed9c65a5/verify.py
```

Expected first line:

```text
PASS_PAIRED_PLANE_LOCAL_TWO_EDGE_SWITCH
```

The exact accepted seed is `9c65a5d9c501b3f5185d52cd340a9579`, track `recursive-interfaces`, task card `coverage-law-change`, priority revision 4. The base commit is `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`; the selected-record SHA256 is `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`. `SOURCES.json` pins the complete input set, including the task catalogue, review/source manifest, selected replay archive, local ceiling, and predecessor artifacts. The verifier rechecks all input hashes before reconstructing the search.

Predecessor attribution: [paired-plane-port-matching-seed6c563a](../paired-plane-port-matching-seed6c563a/README.md) supplied the selected-family paired-plane factorization and endpoint framework. The present result changes the matching and reoptimizes the exact copy invoice over one complete two-edge neighborhood. [PR #1889](https://github.com/CrocSwap/integer-mult-bounds/pull/1889) and its pinned scalar-mask obstruction delimit what the factorization does not prove. Substantial OpenAI Codex assistance was used; no independent human review or formal proof assistant is claimed.

## Known controls

The package checks that a non-edge is rejected, omitting an active factorization term breaks the full-port identity, mutating an active matrix breaks the local tensor identity, and omitting the plane translation breaks the dirty-state endpoint. It also checks the prior 126 invoice against the new 96 invoice and the exact 67/68 screening threshold.

## Open next questions

- Can this changed matching be integrated into a scalar masked-plane decoder and a fully charged hosted route? This determines whether the 30-unit local saving can reach a supplier-level cost. First step: derive the decoder's scalar query map for the candidate's 12 active terms and charge each interface transition against the existing route budget. Blocked by the known gap between the F2 factorization and a scalar decoder.
- Does a larger matching neighborhood contain a lower B14 invoice? This would test whether the local improvement is robust beyond one two-edge switch. First step: compare a bounded three-edge-switch neighborhood against the 96-cost candidate using the same exact factorization solver and charge. Blocked by the current package's intentionally finite 3,080-switch scope.
