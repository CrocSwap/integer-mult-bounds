# Exclude 126 fixed-port two-ingress repairs at adjoint chart 3

All 126 shortlisted paid ingresses fail to recover the chart-3 payload on the pinned #7786 word. For 76, the allowed causal producer stock lacks a row that gives equal nonzero responses to the two signed probes. The remaining 50 admit such a row, and the proposed deliveries still span at most two of the three required quotient directions. Two independent exact checks reproduce the exclusion. [Pinned native source](https://github.com/CrocSwap/integer-mult-bounds/tree/89a67c404226d51028e135de2b9169e9020d57af/research/p104-iterated-returns/continuation) · [Prior public shortlist](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19749615) · [R16 claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19754206)

The exact source is #7786 at `89a67c404226d51028e135de2b9169e9020d57af`, with word SHA-256 `c447b6d5ba956fbe40834fe3c1bc69af2f225736f1b97ecd84b57bab9dd283cb` and layout SHA-256 `f7de788c4a559282d35a9fce42f841a0e8de5a4015db871e718f9245569b0aa7`. The paid path `768 → 508 → 3` consists of rank-three slots `97760` and `95681`. The proposed direct rank-six send, the recoded grade-preserving `99128` from chart 508 and one other recoded paid ingress must restore three directions while the other 905 receiver rows stay fixed. The tested producers use the original stocks independent of the removed and recoded legs. [Exact archive inventory](ARCHIVE-SOURCES.json) · [Source-bound screen](evidence/SCREEN.json)

## Exact quotient obstruction

Let $A$ be the span of the 907 original arbitrary chart-3 rows retained after deleting `95681`. They are independent. Each probe annihilates $A$ and gives $-960$ on the old `95681` payload, so that payload lies outside $A$. Modulo the 905 fixed rows, the three directions to recover are old `99128`, the old second ingress, and old `95681`. Three new scalar arrivals can recover them only by spanning the same three-dimensional quotient. Every new row must therefore lie in $A$ plus the line of old `95681`.

The first probe annihilates the whole chart-768 stock, and the second annihilates the whole chart-508 stock. Any replacement from those charts inside the required span must consequently belong to $A$. The exact chart-768 intersection with $A$ is the line of `99128`. The chart-508 intersection is supported on `88611`, `88615`, `88979`, `88990` and `99128` in the independent receiver basis. [Adjoint certificate replay](evidence/VERIFIED.json) · [Independent primal certificate replay](evidence/REVIEW-PRIMAL.json)

| Chart-508 row | Exact expression in the receiver basis |
| --- | --- |
| `99131` | `99128` |
| `99134` | `−99128 + (88979 + 88990)/2` |
| `89158` | `(88611 + 88615 − 88979 − 88990)/2` |

The rank of $A$ pooled with the chart-768 and chart-508 stocks is 910 and 909, respectively. The rational identities provide the upper ranks. Nonzero finite-field minors modulo 1,000,000,007 and 65,521 establish the lower ranks. One shortlisted row, `88611`, belongs to the displayed chart-508 support. It fails the probe test. Every one of the 50 probe survivors has its old payload outside the chart-508 support, leaving the chart-768 and chart-508 deliveries on the same `99128` line modulo the 905 fixed rows. One further arrival adds at most one quotient direction.

Removing the two old legs and paying for one rank-six send would save about `0.770182622274303245` signed units across 48 calls. Free restoration at the original ingress prices would give a hypothetical complete margin of `+0.390740452858222244`. The exact realizable credit for this domain is zero. The inherited conditional finite lower is `0.00387944011068`, and the target `0.00387981257853` still needs `0.379442169416081001142560` signed units from the rational side. [Published invoice](https://github.com/CrocSwap/integer-mult-bounds/blob/89a67c404226d51028e135de2b9169e9020d57af/research/p104-iterated-returns/continuation/evidence/application.json) · [Frozen target price receipt](evidence/R16-SERVER.json)

## Reproduce

From this package directory, run the three checks with standard-library CPython 3.12. Each uses the packaged immutable inputs and writes only to stdout.

```sh
python3.12 -IB verify_pulses.py
python3.12 -IB verify_certificate.py
python3.12 -IB verify_primal.py
```

The first command reproduces both signed pulse controls and all 126 original causal candidates. Retiring the old legs changes 165 required terminals in each probe, first at terminal 3. The second checks every reported exact two-probe row and the doubled-restoration rejection. The third independently regenerates the adjoint values by reverse accumulation in the original primal graph. It checks the alternate lower ranks, all spanning identities and the complete 76/50 classification. The Git-based registry check is optional for running the package. [Frozen probe data](WITNESSES.json) · [Complete shortlist](evidence/FUTURE-ROSTER.json)

From the repository root, run the registered replay.

```sh
python3.12 -IB scripts/research_package.py --package research/p104-chart3-two-ingress
```

## Open next questions

Can relocating a same-grade ingress change the chart-508 intersection and carry the missing required direction without an additional paid leg? For one literal candidate, derive its available stock in schedule order and recompute the quotient for all affected readers before attempting either operator replay. The proof here assumes the original paid ports and their ancestor restrictions. The changed geometry requires a fresh full signed price and physical and ordinary checks.

## Credit

Clear1nsight prepared the source-bound screen and separate exact replays with substantial OpenAI Codex assistance. The proof builds on the #7786/#7781 succession, Ali Romman's #7776 signed P104 framework, the restored-chain work in #7774, and the earlier #7795 paid-slot source reconstruction. [Detailed attribution](NOTICE)
