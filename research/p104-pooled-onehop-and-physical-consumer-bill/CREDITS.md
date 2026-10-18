# Credits and Provenance

## Author

- **Author:** `dcharb78`, with AI assistance.
- **Verification:** All computations, algebraic proofs, flag censuses, subspace-memory propagation audits, and 9-stage consumer ceiling bills are deterministically reproduced from pinned repository inputs by `verify.py`.

## Pinned Upstream Inputs (`SOURCES.json`)

This package pins and authenticates 18 upstream repository files at `base_commit = 997e6a9ca7b4f95d50e366f61412fd640d72a88a`:

1. `certificates/selected-result.json` (`provenance`) and `docs/research/agent-task-catalog.json` (`provenance`) — Repository baseline benchmark ($\kappa_{\text{selected}} = 0.001672660197076918$) and priority card `p104-side-correction` (`complex-mechanisms`, weight `20`) from PRs `#845`, `#1012`, `#1094`, `#1098`, `#1659`, `#1708`, `#1712`, `#1748`, `#1791`, `#1829`, `#1918`, `#2048`, `#2199`, and `#2391`.
2. `research/p104-native-channel/inputs/LOWRANK-WITNESS.json`, `research/p104-native-channel/inputs/P104-FIXTURE.json`, and `research/p104-native-channel/verify.py` — PR `#1991` (with follow-up `#2675`), which reports (author-checked, `partially_reviewed`) the 4,058-step rank-2,368 native P104 channel word, its 104 prescribed $X_s$ ($1 \to 9$) and $Y_t$ ($0 \to 8$) frame chains, and the residual cross-Gram target $C = I_{104} - G_{104}/2$ (`4,992` nonzero off-diagonal entries of $\pm 1/2$).
3. `research/p104-joint-unit-flags/CERTIFICATE.json` and `research/p104-joint-unit-flags/verify.py` — PR `#2981`, which reports (author-checked, `merged_for_archive_only`) the static 208-flag departure/arrival cover (`forms` and `helpers`) and the `2,309`-edge compatibility graph $A_a \subseteq B_b$.
4. `research/p104-coherent-support-witness/CONTROL.json` and `research/p104-coherent-support-witness/WITNESS.json` — PRs `#3013` and `#3019` (building on `#2996`), which report (author-checked, `merged_for_archive_only`) the rematched 208-edge control pairing (`CONTROL.json`, `45` missing pairs on `Y40` under transitive connected components) and the swap-$[91, 189]$ witness (`WITNESS.json`, `0` missing pairs under transitive connected components).
5. `research/p104-fixed-matching-flag-consistency/verify.py` and `research/p104-fixed-matching-flag-consistency/RESULT.json` — PR `#3038`, which reports (author-checked, `merged_for_archive_only`) the literal quotient subspace enumeration in $B/A \cong \mathbb{F}_2^5$ (`[1, 31, 155, 155, 31, 1]`, `9,765` full flags) and the single-helper consistency rejection of helper `91` on PR `#3019`'s matching (`0 / 9,765` passing flags, minimum missing pairs `45`).
6. `research/complex-local-word-ceiling/ceiling.py` — PR `#2998`, which provides exact rational interval enclosures for the hosted 9-stage consumer coverage law ($m = 73$, $W = 832$, $N = 9$, $w = 832/9$, $R = 51$).
7. `research/p104-endpoint-geometric-budget/geometry.py` and `research/p104-endpoint-geometric-budget/RESULT.json` — PR `#2920`, which reports (author-checked, `merged_for_archive_only`) the `208` distinct departure planes and `208` distinct arrival hyperplanes of the static endpoint geometry.
8. `research/p104-two-history-lifetime-floor/RESULT.json` and `research/p104-joint-endpoint-obstruction/RESULT.json` — PRs `#2924` and `#2953`, which report (author-checked, `merged_for_archive_only`) the two-history lifetime floor (`216` units) and the selected independent endpoint cover (`423` units).
9. `research/p104-consumer-budget-audit/RESULT.json` and `research/p104-all-pair-consumer-budget/RESULT.json` — PRs `#2741` and `#2819` (alongside `#2586`, `#2662`, and `#2712`), which report (author-checked, `merged_for_archive_only`) the 9-stage consumer budget and dual-endpoint boundary conversion rank-unit bills (`260` $H_1$ for 5 fused boundaries, `416` $H_1$ for all 8 boundaries, plus `8` $H_7$ private zero/erasure per reverse-adjoint call).

## External Comparator (Not Read at Runtime)

- Open PR `#3124` (`p104-cycle4-unit-flags-seed6501` / `p104-alternating-cycle-neighborhood`) is cited strictly as an external comparator (`report (author-checked)`, not read at runtime). Its two 4-cycle modifications of `CONTROL.json` (`[13, 203, 191, 63]` and `[39, 154, 139, 134]`) are reconstructed directly in `verify.py` from pinned `research/p104-coherent-support-witness/CONTROL.json`.
