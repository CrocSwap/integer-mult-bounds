# Packed source-assisted bit supplier

Pack PR187's completed rank-4/rank-24 scratch residuals and combine the
result with PR193's complex supplier:

| Construction | Conditional kappa |
|---|---:|
| PR194 as published | 0.0006674324 |
| PR193 complex + PR187 bit | 0.000670450176035363 |
| Same suppliers, with packing | **0.000676080316519385** |

Packing contributes **0.8398%**. The **1.2957%** gain over PR194 also includes
supplier and arithmetic choices. [PROOF.md](PROOF.md) gives the construction,
routing costs and inherited assumptions; [SOURCE.json](SOURCE.json) pins inputs.

## Reproduce

From the repository root, create the pinned dependency checkouts and run:

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds 201737a1ec4f936e166e2481fb9e88104cb2ccc7
git worktree add --detach ../packed-bit-pr187 201737a1ec4f936e166e2481fb9e88104cb2ccc7
git fetch https://github.com/CrocSwap/integer-mult-bounds 187e1010ac8b259af8e9b5166f68b64bc27b4b47
git worktree add --detach ../packed-complex-pr193 187e1010ac8b259af8e9b5166f68b64bc27b4b47
python3.13 -m pip install -r ../packed-complex-pr193/research/source-assisted/requirements-round13.txt
python3.13 -B research/packed-source-assisted-bit/verify.py --complex-root ../packed-complex-pr193 --bit-root ../packed-bit-pr187 --full
```

This runs both unchanged upstream verifiers, regenerates charts and incidence
assignments, and checks two exact moment engines, finite leaf composition,
all 47 assembly inequalities, seven margins and corruption controls. The
certificate stores the minimum constraint slack instead of all 47 slacks;
every inequality is still recomputed. Add `--write` to regenerate it.
Without `--full`, the checker uses the saved physical receipt and needs only
Python 3.11+ and its standard library. Full regeneration uses Python 3.13
to match the inherited complex verifier's gzip encoding.

## Credit and scope

Credit Avi Eisenberg for PR193; Rohan Arun for PR187; icekylinx for the
source-assisted method and paired-cube framework; eumemic for PR168;
and the preceding frame, reuse, balanced-layout and arithmetic contributors.
Finite leaf composition follows PR185/187. Related completed banks appear
in PR186; no new general packing mechanism is claimed. Original notices
remain in the pinned checkouts. The full multiplication theorem remains
conditional on the interfaces listed in the proof.

Prepared with substantial OpenAI Codex assistance. Apache-2.0.
