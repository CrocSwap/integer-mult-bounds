# E6 one-extra rank-one frame: exact bounded screen

**Scoped negative result; no new κ.** For one fixed six-term E6 Gram factorization and the dense pairing `B0`, the exact one-extra rank-one identity below has minimum raw pairing cost **40** over the union of all 36 E6 root-line directions and all 364 projective directions in `{-1,0,1}^6` in the pinned basis, with every rational support cell of `lambda != 0` exhausted. The corresponding minimum fully charged Theorem C cost is also **40**. Neither cost reaches 35.

This is a bounded result about one explicit seven-term family. It does not settle the open unrestricted question whether any seven-term E6 decoder can cost at most 35. It makes no claim about arbitrary rational directions, other decoder identities, sparse pairings, or a supplier for the selected multiplication construction.

## Construction and result

Let `X` be the exact 36-by-6 root-coordinate matrix in the pinned basis and `H` its basis Gram, so `G = X H X^T`. The fixed dense pairing has diagonal one and an off-diagonal one exactly when the corresponding E6 roots are orthogonal. For a nonzero direction `a` and rational `lambda != 0`, set

```text
p_i = X e_i                         q_i = X(H e_i - lambda a_i a), i=1,...,6
p_7 = X a                           q_7 = lambda X a.
```

The rank-one corrections cancel, giving `sum_j p_j q_j^T = G` exactly. The search uses the 36 projective root directions together with all 364 projective ternary coefficient directions in the pinned basis. For each direction it enumerates every nonzero rational breakpoint where a coordinate of `q_1,...,q_6` vanishes, evaluates the breakpoint itself, and one exact rational point in each complementary open interval. Supports, GF(2) block ranks and both cost models are therefore constant between the listed breakpoints.

The census covers **365 distinct directions and 4,672 lambda support cells**. The minimum raw cost is 40; the charged-cost histogram is 40:6, 41:6, 42:12, 43:143, 44:4505. The initial root-direction-only slice covered 566 cells and had minimum 42. The six-term reference factorization has ranks `(6,7,6,6,6,6)` and cost 37; the square-decoder floor 36 is the separate open-request benchmark, not the cost of this particular reference factorization.

Theorem C charges each active total `max(5,r_j)`, so seven active totals have an optimistic floor of 35. Every enumerated factor has seven nonzero terms, and this family’s minimum raw sum is already 40. Any source, copy, frame, hosting, restoration, precision or interface expense would add to that local cost. No selected-supplier mapping, paid recursive profile or κ improvement is established.

The exact proof and cell argument are in [PROOF.md](PROOF.md); all pins and results are recorded in [SOURCES.json](SOURCES.json) and [CERTIFICATE.json](CERTIFICATE.json). The original task, seed, scope change and stopping rule are in [TASK.json](TASK.json). The live overlap snapshot is in [OVERLAP.json](OVERLAP.json).

## Reproduce

From the repository root, with Python 3.12 or newer and only the standard library:

```sh
python3 scripts/research_package.py --package research/e6-one-extra-frame-seed4dd9 --check-only
python3 scripts/research_package.py --package research/e6-one-extra-frame-seed4dd9
```

The registered replay reconstructs the E6 roots and basis over exact rationals, verifies the Gram identity and pairing, runs the full support-cell census, checks the certificate, and exercises positive and negative controls. To regenerate the certificate after changing the search, run `python3 -B research/e6-one-extra-frame-seed4dd9/verify.py --emit`.

## Predecessors and attribution

The open decoder request is [Discussion #1166, comment #18936173](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18936173). Merged [PR #1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590), head `08e134b4a0c7f04869dae703f2a2e688e53c44f0`, supplies the root-unit model and Theorem C pricing context. Open [PR #2228](https://github.com/CrocSwap/integer-mult-bounds/pull/2228), head `ad1757e319225f3a5b86e3d3fa72897bd9f6db40`, develops dense-pairing root-code floors and leaves overcomplete E6 at seven terms open. Open [PR #2137](https://github.com/CrocSwap/integer-mult-bounds/pull/2137), head `6a022d50e21bdcf2014a26937a34d44eed3473f0`, studies a rank-four E6 coordinate-form family. The distinct rank-four projected-Gram/adapted-pairing screen is [PR #2232](https://github.com/CrocSwap/integer-mult-bounds/pull/2232), head `3391f27dd0f226f0e1ead8b2b829eb6d3ec567d3`. This package changes the term count and uses a redundant rank-one frame while holding the exact Gram matrix and `B0` fixed.

The exact E6 line order follows `research/root-unit-decoder-lemmas/lib/ade.py`, pinned in [SOURCES.json](SOURCES.json). Credit the authors of PR #1590 and the cited E6 decoder work for the model and predecessor results. Prepared by OpenAI Codex with substantial GPT-6 assistance in research, exact derivation, implementation, verification and writing. This is not independent human review. Apache-2.0.

## Open next questions

Can an E6 seven-term decoder outside this one-extra rank-one family attain fully charged cost at most 35? That is the direct way to settle the open overcomplete question. A next step is to change one structural premise, such as allowing two independent correction directions or a non-Gram base decoder, derive its fully charged floor before search, and compare against the 35 target. This package does not show that either larger family has headroom or a supplier mapping.
