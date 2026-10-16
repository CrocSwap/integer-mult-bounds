# Five-dimensional port decoder for selected P112

**Exact local algebraic construction; no new supplier or kappa.** This package constructs a five-dimensional port cover of the selected 112 labels in `F2^9`, solves the exact block identity, factors it into charged support terms, and verifies the dirty local endpoint.

The cover has 22 pairwise-orthogonal five-frames and one orthogonal pair. The deterministic block solve gives

```text
I_9 = sum_g A_g M_g A_g^T over F2
```

and the 23 matrices factor into 16 rank-one terms. Their exact B14 support-pairing invoice is 10 terms of rank 7 and 6 terms of rank 8, total charge **118**. For any two selected port labels `q_i,q_j`, the resulting full decoder entry is `q_i^T I_9 q_j = q_i dot q_j`.

## Construction and search scope

The verifier reconstructs all 161,280 pairwise-orthogonal five-frames from the pinned selected-label set. A seed-fixed randomized greedy cover selects the first complete cover at attempt 365 after 7,438 greedy steps. It has a 10,000-attempt cap. This is a reproducible construction, not an optimum search or a universal statement about all covers.

For each block `g`, its columns form `A_g`. The exact 81-equation F2 solve determines `M_g`; a canonical rank factorization gives source and target labels for every term. Each term is charged by the F2 rank of the selected label-pairing submatrix on its actual source and target supports. All 16 charges are positive.

For a block `E`, define `C_E = product_{q in E} C_q`, where `C_q=((1+i)I+(1-i)X_q)/2`. Orthogonality makes the factors commute, and `C_q^2=X_q`; hence `C_E^2=X_(xor q in E)`. Exact Gaussian-dyadic replay checks this identity on all 512 address basis states for all 23 blocks. A separate dirty-input replay checks 672 source/target cases.

## Cost ledger

| Expense | Evidence or price | Limit |
|---|---|---|
| Source labels | 112 pinned `F2^9` labels read from the selected replay archive | Physical owner access is not mapped; include it in the overhead cap below. |
| Decoder copies / recursive ranks | 16 terms, rank histogram `{7:10,8:6}`, total 118 | Exact local support-rank invoice. |
| Helper state | No additional full-length helper is introduced by the algebraic identity | A physical schedule and its scratch restoration are not supplied. |
| Frame and interface transitions | Five-dimensional source and target port contract is explicit | Native chart changes and role transitions must fit the overhead cap. |
| Aggregate endpoint corrections | 23 exact translations `X_(xor q)` | One rank-one-equivalent unit per translation is provisional; then 134 units remain. |
| Hosting and dispatch | No owner placement or instruction schedule is claimed | Must fit the same remaining allowance. |
| Precision | Local correction numerators are exact Gaussian integers over denominator at most `2^10` | Global precision and tape costs are not priced. |
| Total additional costs | At most 157 rank-one-equivalent units beyond copy charge 118 | Exact `a=1/99` threshold; charge 275 passes and 276 fails. |

## Favorable local cost screen

Replacing the selected word's eight rank-8 centre children (64 mass) with the 16 terms (118 mass) gives the per-call profile

```text
{1:2412, 2:418, 3:432, 4:142, 5:82, 7:10, 8:6}
```

with local mass 5,640. Applying the repository's exact relaxation with width 73, `w=896/9`, nine stages and `unpaid=5` gives a moment upper bound of `0.9774210973077914` at `a=1/99`; its certified ceiling is `0.017542237243537`.

The exact profile leaves at most **157 additional rank-one-equivalent units** per call: total charge 275 still gives a moment upper bound `0.9999807669205109`, while 276 gives a lower bound `1.000124459083649`. The 23 exact aggregate translations `X_(xor q)` are identified. If each is provisionally priced at one rank-one-equivalent unit, 23 units are consumed and **134** remain for every other route, chart, hosting, restoration and precision cost. That unit price is a screening convention, not a realized native invoice.

This is a local replacement-law screen. The five-unpaid endpoint contract, selected native owner placement, chart transitions, physical translation implementation, hosting, complete restoration and precision are not integrated. No selected exponent or kappa changes.

## Reproduce

From the repository root:

```sh
python3 -I -O -B research/five-plane-port-p112-seed1f7fdfe4/verify.py
python3 research/five-plane-port-p112-seed1f7fdfe4/search.py --attempt-cap 10000
python3 scripts/research_package.py --package research/five-plane-port-p112-seed1f7fdfe4 --check-only
```

The verifier prints `PASS_P112_FIVE_PLANE_PORT_DECODER`. Package replay targets Python 3.12; this session's direct replay used Python 3.14.7. The search writes `CANDIDATE.json` deterministically for the pinned seed and Python standard library.

## Provenance and limits

Base commit: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. Selected-record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`. Catalogue revision 4 SHA-256: `d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`. Source archive and all live input hashes are pinned in [SOURCES.json](SOURCES.json).

Discussion #1587 supplies the lower-dimensional plane-port endpoint; PR #1825 supplies the matched paired-plane cover. Discussion #2024 / PR #2041 studies three-plane P112 blocks and reports a bounded candidate that misses `a=1/99`. This work changes the block dimension to five and uses a seeded greedy incidence construction. Merged PR #1909 studies tetrad-local E8-root supports, a different support object.

Prepared by Cinna Davis with substantial OpenAI Codex assistance in the formulation, search, implementation and exact replay. No independent human review is claimed. Apache-2.0.

## Open next questions

Can one selected native port route realize the five-frame interface within the remaining 134 rank-one-equivalent units after the provisional aggregate-translation charge? The next step is to map one block through its native chart and charge source access, frame changes, restoration and precision before extending to all 23 blocks. The current evidence is algebraic and does not establish that physical cost.
