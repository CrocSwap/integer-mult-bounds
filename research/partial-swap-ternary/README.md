# Partial swaps on the ternary geometric network

**Conditional κ = 2093495/10^12 = 2.093495e-6 > 2^-19.**
This is about 11.09% above [PR #18](https://github.com/CrocSwap/integer-mult-bounds/pull/18)'s
1.884586e-6 in exponent saving, not practical runtime.

Apply icekylinx's PR #18 partial-swap frames to our PR #17 ternary network.
The source correction disappears, removing exactly N singleton calls,
while all six recursive blocks remain unchanged. The resulting rank sum is
`Wm - 2N + 2L`. The existing h30 producer, role allocation, matching, and
nested basis are retained. The circuit now directly performs the address
interchange: the old outer shear-conversion passes must be omitted.

The bit saving is 4187/10^9. The unchanged h28 complex network uses its
stronger certified saving 4191487/10^12, with beta=1/1000 and
C1=3749/2500. All 29 constraints and seven final margins are strict.
The exact final absorption gap is
1542391935523399/2500000000000000000000000000.

[Written transfer proof](proof.tex) · [Exact certificate](certificate.json) ·
[Complete manuscript patch](../../patches/partial-swap-ternary.patch) ·
[Compiled manuscript](../../artifacts/partial-swap-ternary.pdf)

## Reproduction and scope

Use Python 3.11 or newer. From the repository root:

```sh
python3 research/partial-swap-ternary/witness.py --full
python3 -m unittest discover -s tests -p test_partial_swap_ternary.py -v
python3 research/partial-swap-ternary/make_patch.py
make verify
```

The h30 physical producer was freshly rebuilt for PR #17 and its source
hashes are rechecked here. The four new regression tests check exact rational
partial-swap identities and lower-triangular conjugation on 54 projectors,
including 30 nonsymmetric ones; nested-frame and complement identities;
and the complete small framed ternary network on 2,500 independent input
symbols. Ordinary and source-relocated dirty auxiliaries are covered.
Negative controls reject missing conjugation terms, nonnested edges, missing
cleanup, wrong endpoints and an extra legacy outer shear.

The new full certificate includes those controls, both exact moments, the
precision guard and final assembly. The full manuscript appends the new
interface, updates the active layer/transform consumers and regenerates
every displayed parameter slack and margin. Earlier interfaces are retained
as historical dependencies. The repository-wide rerun status is reported
in the PR; it is distinct from these completed candidate-specific checks.

Finite checks do not establish the general simultaneous-basis, arbitrary-width
tape, precision or multiplication arguments. This is a conditional research
composition requiring independent mathematical review, not formal verification
or an OpenAI-endorsed result. No claim of global optimality is made.

## Attribution

The partial-swap frame and triangular-conjugation identity are due to
icekylinx, PR #18 at f2ab41aebad47861caf6316282c1793e5513845e. Its sources,
license, NOTICE and hashes are pinned in `references/pr18/`.

The retained producer and all-complex batching are eumemic's PR #15;
source relocation is eumemic's PR #13. The data corners are from Rohan
Arun's PR #14 and independently Zhihao Chen's PR #16; the nested basis is
Zhihao Chen's PR #16. We retain icekylinx's PR #10 tape/batching interfaces,
and the earlier contributions of Zhihao Chen, Douglas Colkitt, OpenAI and
others. This composition and independent controls are by Rohan Arun with
substantial OpenAI Codex assistance, including parallel proof/test reviews.
