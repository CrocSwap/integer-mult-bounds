# An exact complex decoder climbs from two E8 roots to rank 16

**Scoped partial result.** The exact tensor decoder and support/COPY ledger are
verified. Its copy-only profile clears the selected model's five-percent
ceiling screen, while one explicit frame-slot tariff sensitivity falls below
the selected endpoint. No physical tariff, selected supplier, new κ, or
frontier change is established.

## Question and result

Can a small complex decoder start from actual E8 roots, climb through block
ranks 2, 4, 8 and 16, and fit the selected call's full copy/frame ledger?

The exact identity exists, and its support-pairing matrix has full rank at each
level. The rank-16 block has 16 full-support terms of copy rank 16, so its COPY
mass is 256. The selected model has 896 live families over nine stages. The
rank-16 construction therefore uses 56 blocks per nine-stage replica, or an
average `56/9` blocks per call. Keeping the selected eight rank-8 local terms,
the per-call profile is `{16:896/9, 8:8}` with local COPY mass `14912/9`.

Under the pinned parent relaxation, that copy-only profile has ceiling bracket
`[1942057021/250000000000, 1553645617/200000000000]`, whose upper endpoint is
about `0.007768228085`. This exceeds the five-percent target
`0.00177455681454345`. The result is only an ideal profile screen: product
levels 2–4 use a new label form, and the frame ledger has no established tariff
in the parent model. Charging one rank-1 unit for each listed per-block frame,
embedding, restoration-read and scalar-add slot gives `12824/3` extra units per
call and a sensitivity ceiling near `0.001658774411`, below the selected
`0.001690054109089` endpoint. The physical tariff and a selected-code embedding
remain open.

## Exact decoder identity

Take the two E8 roots

```text
r0 = (1,1,0,0,0,0,0,0)
r1 = (1,0,1,0,0,0,0,0)
```

Both have norm squared 2 and dot product 1, so their Gram matrix is

```text
G0 = [[2,1], [1,2]].
```

Over `Q(i)`, with **ordinary transpose**, set

```text
D0 = [[1, 1], [1, i]]
T0 = [[3-i, 1+i], [3+i, -1-i]].
```

Direct multiplication gives `D0 T0^T = [[4,2],[2,4]] = 2 G0`. Every entry of
both frames is nonzero. The two E8 support labels pair by
`(<r_i,r_j> + 1) mod 2`, giving `B0 = I2`; each of the two terms therefore has
support-pairing rank 2 and the base copy mass is 4. Using conjugate transpose
does not give this identity (checked as a negative control).

For `s=1,2,3,4`, let `n=2^s`, `Rs=R0^tensor_s`,
`Gs=G0^tensor_s`, `Ds=2^(1-s) D0^tensor_s`, and `Ts=T0^tensor_s`. Then

```text
Ds Ts^T = 2 Gs = 2 Rs Rs^T.
```

The verifier checks every matrix entry. The block-climbing frame itinerary is
the repeated tensor step `s -> s+1`: the product-root frame has `n` rows in
ambient dimension `8^s`; the decoder and reader frames have shape `n x n`;
their ranks are `n`; and their exact inverses are checked. The product-root
embedding has `n²` nonzero coefficients. The left inverse `Ls=L0^tensor_s`,
where `L0` selects coordinates 2 and 3 of each base root, satisfies
`Ls Rs^T=I_n`; it uses `n` coordinate reads and restores every coefficient
vector in the product-root span. This does not restore arbitrary ambient state
outside that span.

The binary support pairing at level `s` is `Bs=(Gs + J_n) mod 2`, where `J_n`
is the all-ones matrix. Modulo 2, `G0=[[0,1],[1,0]]`, so `Gs` is a permutation
matrix `Ps`. Since `n` is even, `Bs=Ps(I+J_n)` is nonsingular: over F2,
`det(I+J_n)=1+n=1`. The verifier independently computes all four ranks. For
`s>=2`, these are product roots in `R^(8^s)` and a new `n`-bit label form
`Bs`; they are not the selected 9-bit E8 port code.

## Full block and per-call ledger

| Tensor factors | Product lines | Terms | COPY rank per term | COPY mass | Forward D/T frame coefficients | Root embedding coefficients | Root-span restoration reads |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2 | 2 | 2 | 4 | 8 | 4 | 2 |
| 2 | 4 | 4 | 4 | 16 | 32 | 16 | 4 |
| 3 | 8 | 8 | 8 | 64 | 128 | 64 | 8 |
| 4 | 16 | 16 | 16 | 256 | 512 | 256 | 16 |

At level 4, both forward `16 x 16` frames are dense. Their four-stage `2 x 2`
tensor application takes 272 constant-multiplication slots (including the
`1/8` normalization on D) and 128 additions for the two input frames. If a
consumer needs vector outputs returned to the original coefficient frames,
the two inverse frames are also dense, another 512 coefficient slots per
block. The scalar bilinear decoder returns a scalar and does not itself need
that output-vector restoration. Each block also uses 16 rank-16 bilinear child
products and 15 scalar accumulation additions.

| Per-call quantity | Candidate profile | Selected model |
|---|---:|---:|
| Live families | `896/9` | `896/9` |
| Average rank-16 blocks / children | `56/9` / `896/9` | — |
| Retained rank-8 local terms | 8 | 8 |
| Decoder COPY mass | `14336/9` | — |
| Total local profile mass including retained rank-8 terms | `14912/9` | 5,586 |
| Full local-plus-centre coverage mass available | — | 7,232 |

The ratio of candidate to selected local mass is `7456/25137`. The 7,232
coverage allowance follows the pinned model's `72*(896/9)+64` identity; its
separate centre charge is retained. Under the parent ideal relaxation the
candidate profile's ceiling is above the five-percent target. The ceiling
assumes fractional idle counts and unconstrained repacking; it does not prove a
physically realizable supplier.

The level-4 per-call frame ledger over the average `56/9` blocks is:

| Item | Slots or coefficients per call |
|---|---:|
| Forward D/T dense coefficients | `28672/9` |
| Inverse D/T coefficients if vector outputs are required | `28672/9` |
| Staged D/T constant multiplications | `15232/9` |
| Staged D/T additions | `7168/9` |
| Product-root embedding coefficients | `14336/9` |
| Root-span restoration reads | `896/9` |
| Scalar output accumulation additions | `280/3` |

For a tariff sensitivity only, charge one rank-1 unit per staged multiply,
addition, embedding coefficient, restoration read and scalar accumulation
addition. This is `687` units per block and `12824/3` units per call. The parent
profile can absorb at most 3,919 extra integer rank-1 units while clearing the
five-percent target; 3,920 fails. The sensitivity ceiling is therefore below
the selected endpoint. This unit tariff is not asserted to be the physical
cost, and the dense inverse is excluded unless vector restoration is needed.

## Relation to retained work and credit

The selected baseline is pinned through `certificates/selected-result.json`,
its manifest `research/community-frontier1094-audit/SELECTED-SOURCE.json`, its
assembly `research/community-frontier1094-audit/ASSEMBLY.json`, and the exact
review `docs/research/community-batch1099-review.md`. The selected assembly
SHA256 is `1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045`.
The selected conditional κ is `0.001672660197076918`; the selected local-word
ceiling is `0.001690054109089`. The first-step rank-16 ideal is a 2.31x
relaxation and omits realization costs.

Overlap checked live Start-here discussion #1163, handoff #1166, and relevant
PRs. PR #3039 has a charged-group block-climb obstruction, while #3066 corrects
its mixed-profile inference. PR #1633 bounds excess rank for all-pairs E8
decoders and gives a ten-term normal form; #3566 binds a different masked P112
tetrad decoder to selected ports. PRs #3701, #3805, #3811 and #3874 remain
rank-cap and ideal-budget screens. This package contributes the explicit
complex factorization on an actual E8 root pair, its four-level tensor
support/COPY ledger, and an exact frame-slot tariff sensitivity. It does not
duplicate the fixed-alphabet effective-rank result assigned to macbook-05 or
claim the product roots embed in the selected ports. Credit prior proofs and
source authors listed in `docs/research/complex-decoder-scope-map.md`,
including PR717, PR968 and PR1077.

## Reproduce

From the repository root, Python 3.12 and the standard library:

```sh
python3 -I -B research/complex-e8-pair-block-climb/verify.py
python3 scripts/research_package.py --package research/complex-e8-pair-block-climb
```

Expected direct replay:
`PASS_COMPLEX_E8_PAIR_BLOCK_CLIMB levels=4 rank16_block_copy_mass=256 average_profile_mass=14912/9 ideal_a=0.007768228085 frame_proxy_a=0.001658774411`.
The package replay checks the source pins and runs the explicit verifier command
recorded in `VERIFY.json`.

## Open next questions

After the companion fixed-alphabet effective-rank result is available, does
its surviving support class embed this factorization into the selected 9-bit,
112-port pairing code, and what established physical tariff applies to the
complete frame ledger? Until then, stop; a copy-only ceiling pass does not
justify another construction round under the family-level expansion gate.

Prepared with substantial OpenAI Codex assistance by homelab-05. No independent
human review or formal proof-assistant verification is claimed. New material
is Apache-2.0.
