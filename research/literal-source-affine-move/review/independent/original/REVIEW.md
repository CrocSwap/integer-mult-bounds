# Independent review: source-bound affine MOVE24476

## Decision

**Pass for the scoped source, phase, affine-order, and one-column kernel claims.** I found no mathematical mismatch between the authenticated source MOVE and the frozen (M_L C^{\otimes3}M_R) recipe. The result does not validate the selected caller's numerical promises or add a caller/nonleaf tariff.

## Pins and method

The reviewed package is `worker-a/research/source-bound-affine-move-join`, frozen at `FREEZE.json` SHA-256 `9645d873c995412d0ef6ab8287ae10eb63350add45263883c3cd574b4e1a1bde`. Relevant exact file hashes are:

| File | SHA-256 |
|---|---|
| `PROOF.md` | `30eb220651420201a57a089b34f6b54b55f995dfc7b6758910da10d87c15e86e` |
| `move.py` | `b213325a652dc91630a50fb63d573108a04a2b7a07e587f25b0ecf0db8ffd668` |
| `RECIPE.json` | `8303e04baa838553257773a6d0e7d9b57389f2f9adf0de183a6d6c644d243a79` |
| `bind_source.py` | `0ceaa9f378eb17743aff2ba71b86be163cf841cf97609f90eb2aed77e9a10f34` |
| `oracle.py` | `762847697ca3fa50e69eb146c157fa888a3687dd552c5b75bccb917f1a65b17a` |
| `SOURCE-BINDING.json` | `2e5c028dde3da98aabd5ebe2daa9bd53effca33e2157a2954b893db36ce0ef83` |
| `GRAPH.json` | `91b207a27c0d9d16cfff8e42332e04126d73a9797fc312f19762297fde04cd8b` |

The independent checker is [`kernel_check.py`](kernel_check.py), with the frozen receipt in [`RESULT.normal.json`](RESULT.normal.json) (normal and `-O` outputs are byte-identical; SHA-256 `219c61bfb47f48d9e63012fae2bd0000f37dcb8720db8e9090c5b4b5eb62662e`). It reads the pinned Git blob directly, authenticates the compressed and canonical-word hashes, and binds event24476 and its two complete frames. It does not import A's compiler, tape emitter, or source oracle.

Reproduce from the workspace root:

```sh
python3 -I -B worker-c/research/source-affine-move-review/kernel_check.py /workspace/scratch/92c9920affc2/repo
python3 -O -I -B worker-c/research/source-affine-move-review/kernel_check.py /workspace/scratch/92c9920affc2/repo
```

Both commands return the same exact result.

## Findings

The source object is canonical main `e54523517d0f03e58352e647c403a5af3e525a57`, archive path `research/shared-wire-split-composition/data/final.json.gz`, Git blob `74563a7867d9d762b6588f65362369668841bb3e`. Its compressed SHA-256 is `2b94953dc14a122e3ef089633f05b58ec689ec5156feb7c784ed3e137dc01883`; canonical word SHA-256 is `91429a6b96729292a8764836e00c87a6f7cd3b76f05159033f4867f69a98d097`. Direct extraction gives event24476 `[MOVE,727,3,470,false]`, frame3 `[]`, and frame470 `[75,137,265]`. The `false` field is the source's private/ownership flag; it does not reverse the ordered frame map.

For the target frame, extend the ordered basis columns `(75,137,265)` by standard basis vectors to form the source chart (G), and let (K=D_QP_G) be its phase/permutation chart. The pinned frame rule gives (T_{470}=K C^{\otimes3}K^{-1}), where

\[
C=\frac12\begin{pmatrix}1+i&1-i\\1-i&1+i\end{pmatrix}.
\]

I evaluated that kernel directly: for each of the 512 input basis addresses, apply (K^{-1}), expand the first three bits with exact (C) entries, and apply (K). All 4,096 resulting nonzero Gaussian amplitudes (common denominator 8) match the recipe's (M_L C^{\otimes3}M_R) action. The check confirms factor order: runtime applies right monomial, then the three positive (C) leaves, then left monomial. Five controls fail as expected: inverse frame orientation, reversed monomial order, wrong absolute phase, moving the offset before its linear map, and (C^\dagger) in place of (C).

The fixed monomial convention is 
\[
|x\rangle\longmapsto i^{a+q(x)}|Gx\oplus b\rangle,
\qquad q(x)=\sum_i\alpha_i x_i+2\sum_{i<j}Q_{ij}x_ix_j\pmod4.
\]
In `move.py`, each monomial's phase component is emitted before its CNOT matrix word and affine component. The latter realizes (X_b) after (G), by the fixed (H^{-1},X_0,H) sequence with (He_0=b). For the selected right factor, (b=5) (bits 0 and 2), (a=2); left has (b=a=0). The checker specifically rejects treating the offset as (G(x\oplus b)).

For (f) independent columns, the scalar factor is ((i^a)^f=i^{af}), while the polynomial term is ∑\(_\ell q(x_\ell)\). The phase engine's initializer scans all (f) columns and increments its four-state mode by the fixed constant (a) per column; its synchronized counters then accumulate the per-column (q). Thus the selected right scalar is (i^{2f}), with residues (2,0,2,0,\ldots\). The argument is tensor-product algebra and the inspected initializer, not an all-(f) tape execution. The source join keeps each phase before that factor's (G)/(X), right factor before (C^{\otimes3}), and left factor after it.

The complete-root prefix bridge reviewed separately in [`common-grid-prefix-bridge-review.md`](common-grid-prefix-bridge-review.md) is valid only for completed, committed components acting on the injective view while retaining complementary root coordinates. It does not establish that a selected producer supplies those numerical premises.

## Limits

This cross-review does not independently execute the full literal graph; root has a separate physical run. The checker proves a one-column exact source-kernel identity and validates the source recipe's mathematical phase/G/X order. The all-(f) phase lift follows from tensorization and the phase engine's column initializer. It does not prove that a caller meets the stated integrality, prefix-fit, or phase-negation promises; nor does it establish source job production, cutoff supply, global ownership closure, faster recursive supply, or a selected κ change. Those remain outside this review.
