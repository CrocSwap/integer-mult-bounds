# One P112 tetrad block: exact port coefficients and a dirty-helper control

**Scoped audit, no new κ or supplier.** This checks one eight-port contribution in Gonzalo Mier's open PR #3566, which binds the P112 tetrad decoder to the selected complex provider ports. It complements the fixed-alphabet rank screen in PR #3567 by checking what the port identity does and does not imply about a separate dirty helper register.

## Question and result

For the first mapped tetrad block at PR #3566 head `ebd6b92c43239d76b1a59e29f574563494388f6a`, does its four-term identity hold coefficient by coefficient for arbitrary values on the full 112-port input? Does that certificate also prove independence from arbitrary values in the provider's separate dirty helper registers?

**Port result: yes, on the stated 112-port domain.** From the exact predecessor root/frame construction, the block has root indices `[24, 25, 34, 35, 100, 101, 110, 111]`, four frame coordinates `[0, 1, 2, 3]`, and mapped selected-provider ports `[20, 21, 36, 37, 46, 47, 110, 111]`. The mapping agrees with PR #3566's first receipt group and its published map digest.

For its signed-coordinate matrix `E` (recorded in `RESULT.json`), the four terms are `(d_k,d_k)` where `d_k` is column `k` of `E`, extended by zero to the other 104 ports. The output is the exact linear map

    y_i = sum_j (sum_k E[i,k] E[j,k]) x_j.

The verifier extracts every coefficient of every formal port variable: all 64 within-block coefficients equal `2 G[i,j]`; the 832 coefficients from other port inputs into these eight outputs are zero; and the 11,648 coefficients into the other 104 outputs are zero. That is 12,544 exact integer coefficients, so the four-term contribution is valid for arbitrary values on the 112 modeled ports. On the selected block it reproduces the full Gram matrix, stronger than checking only the diagonal and orthogonal pairs.

**Separate helper result: not implied by that matrix.** The PR identity has no coordinate for the provider's 480 dirty helpers, and PR #3566 explicitly leaves a source-bound dirty-input implementation open. The corruption control appends a formal helper variable `h` to the first term's input factor. It leaves all 12,544 selected-port coefficients unchanged but changes the helper coefficient vector from zero to the nonzero first term output vector. Setting `h=1` and all ports to zero therefore changes the output. This proves that a port projection alone cannot establish dirty-helper independence.

This control is **not a counterexample to PR #3566's stated identity**: that result claims a coefficient identity on selected ports and explicitly disclaims a physical dirty-input endpoint. It makes the missing interface lemma concrete. A compiled block must show, for each of the 480 arbitrary helper inputs, the exact output coefficient and any required restoration cost. PR #3567's rank bound does not cover that obligation.

## Scope and limits

- The first block is selected by the pinned P112 geometry and matched to PR #3566's published port group. The full 112-root-to-port isomorphism is inherited from PR #3566; this audit checks the exact map digest and selected group, not all 12,544 pairing comparisons again.
- The predecessor `verify.py` is pinned by Git blob and SHA-256 in `SOURCES.json`; exact live PR heads and their source/result hashes are recorded in `REMOTE-PINS.json`.
- The checker does not construct a physical word, infer hidden helper coefficients, verify the 14-block assembly, price frames/restoration/consumers, or change the selected frontier. There is no κ consequence.

## Reproduce

From the repository root, Python standard library only:

```sh
python3 -B research/p112-tetrad-dirty-coefficient-audit-laptop04/verify.py
python3 scripts/research_package.py --package research/p112-tetrad-dirty-coefficient-audit-laptop04 --check-only
python3.12 scripts/research_package.py --package research/p112-tetrad-dirty-coefficient-audit-laptop04
```

Expected final line:

```text
PASS_P112_TETRAD_DIRTY_COEFFICIENT_AUDIT coefficients=12544 helper_corruption_detected=true no_new_kappa
```

## Open next questions

What source-bound eight-port physical word realizes one mapped tetrad block while handling all 480 arbitrary dirty helper inputs and restoring every helper? First step: obtain its complete input/output matrix and extract the 480 helper coefficients at every claimed output. The current identity package contains no such word or helper-register map.

## Credit

The P112 tetrad identity and support model are credited to the authors of [p112-tetrad-local-decoder](../p112-tetrad-local-decoder/README.md). The selected-port binding and conditional budget are Gonzalo Mier's PR #3566; the one-sided effective-rank result is jwr's PR #3567. This audit adds one exact coefficient extraction and one appended-helper corruption control. Prepared by Codex2 laptop-04 with substantial GPT-6 Luna xhigh assistance; no independent human or formal-kernel review is claimed. Apache-2.0.
