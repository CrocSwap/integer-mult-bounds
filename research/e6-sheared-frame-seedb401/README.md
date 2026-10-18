# E6 sheared base factorization with one extra frame

**Scoped negative result; no new κ.** For the 60 signed elementary transvections of the pinned six-coordinate E6 Gram factorization, the exact one-extra rank-one frame construction has minimum raw pairing cost **37** and minimum fully charged Theorem C cost **37**. The census covers **330,486** rational support cells across the 60 transvections and the union of 36 root directions with 364 projective ternary directions. No seven-active decoder reaches cost 35.

The least-cost cell is degenerate to six active totals: its rank profile is `(6,0,6,6,6,6,7)`, at `A=I+E_{2,3}`, `a=(1,-1,1,0,0,1)`, `lambda=1/2`. Its charged cost 37 is still above the square-decoder benchmark 36 in the open request. The finite result does not settle arbitrary rational basis changes, other seven-term identities, sparse pairings, or the unrestricted E6 question.

## Construction

Let `X` be the exact 36-by-6 E6 root-coordinate matrix and `H` the Gram matrix of its pinned basis, so `G=X H X^T`. For a signed transvection `A=I+epsilon E_ij`, define `c=A^{-1}a`. For each nonzero projective direction `a` and `lambda != 0`, use

```text
p_j = X A e_j
q_j = X(H A^{-T} e_j - lambda c_j a),  j=1,...,6
p_7 = X a
q_7 = lambda X a.
```

Since `A c=a`, the six correction terms sum to `-lambda X a a^T X^T`, which the seventh term restores. Hence the decoder is exactly `G`. The dense pairing `B0` stays fixed: diagonal one and off-diagonal one exactly on orthogonal root pairs.

The direction set is the union of all 36 E6 root-line directions and all 364 projective vectors in `{-1,0,1}^6` in the pinned basis. For each transvection and direction, every rational breakpoint where a coordinate of `q_1,...,q_6` becomes zero is included, as is one exact rational representative from each complementary interval. Zero lambda is excluded. The census records degenerate terms and charges only active totals.

The full cost histogram is `37:6, 38:12, 39:18, 40:131, 41:369, 42:1397, 43:29259, 44:117297, 45:181997`. There are 26 cells with six active totals and 330,460 with seven. The exact per-transvection records, witness, support-cell counts and root pins are in [CERTIFICATE.json](CERTIFICATE.json); the two shards are in [SHARD-0.json](SHARD-0.json) and [SHARD-1.json](SHARD-1.json).

A hypothetical seven-active win has optimistic floor `7*5=35`, one below the square benchmark 36. The tested family’s minimum is 37 even when degenerate cells are included. This is only an algebraic root-unit cost. No supplier implementation, per-call paid profile, source/copy/frame/hosting/restoration/precision charge, or κ improvement is established.

## Reproduce

From repository root, with Python 3.12 and only the standard library:

```sh
python3 scripts/research_package.py --package research/e6-sheared-frame-seedb401 --check-only
python3 scripts/research_package.py --package research/e6-sheared-frame-seedb401
```

The registered replay exhausts two shards of 30 transvections each and checks their saved results plus the combined certificate. The exact verifier can also run a quick identity-control smoke check with `python3 -B research/e6-sheared-frame-seedb401/verify.py --smoke`.

## Overlap and attribution

The current open request is [Discussion #1166, comment #18936173](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18936173). The completed Cycle30 [PR #2240](https://github.com/CrocSwap/integer-mult-bounds/pull/2240), head `c8a2b37056e766715c457f56e2dd8172f5bdbccd`, fixes `A=I`; this contribution changes the six-term base factorization by signed elementary transvections. Merged [PR #1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590), head `08e134b4a0c7f04869dae703f2a2e688e53c44f0`, supplies the root-unit model and Theorem C context. Open [PR #2228](https://github.com/CrocSwap/integer-mult-bounds/pull/2228) leaves overcomplete E6 at seven terms open. Open [PR #2137](https://github.com/CrocSwap/integer-mult-bounds/pull/2137) and [PR #2232](https://github.com/CrocSwap/integer-mult-bounds/pull/2232) are different rank-four families.

The exact root ordering follows the pinned `research/root-unit-decoder-lemmas/lib/ade.py` input in [SOURCES.json](SOURCES.json). Credit the authors of PR #1590 and the cited E6 decoder work for the model and predecessors. Prepared by OpenAI Codex with substantial GPT-6 assistance in research, exact derivation, implementation, verification and writing. No independent human review is claimed. Apache-2.0.

## Open next questions

Can a seven-term E6 decoder outside the elementary-transvection family attain fully charged cost 35? A next step is to test one structurally different basis family, such as a two-coordinate or two-shear composition, after screening its optimistic charge. Arbitrary `GL_6(Q)` changes are unbounded, and this package supplies no physical supplier mapping.
