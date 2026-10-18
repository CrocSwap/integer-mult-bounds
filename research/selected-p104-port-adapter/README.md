# An exact P104 decoder adapter for the selected 112-port labels

**Scoped construction: exact selected-port relabeling plus a P104 decoder. No new supplier or κ.**

The selected local word's 112 distinct port masks are linearly equivalent over F₂ to the 112 E8 labels in P112. The certificate gives an invertible 9×9 map on functionals and its inverse transpose on port labels. It therefore reindexes an exact eight-term P104 frame-pair decoder onto 104 of the selected word's actual port labels.

The chosen puncture removes selected port values `145, 161, 22, 38, 280, 296, 431, 415` (positions `18, 20, 26, 27, 60, 63, 104, 107`). The remaining 104 labels carry an exact decoder with eight terms, each of F₂ copy rank 7. Its exact decoder charge is 56, or `56/104 = 7/13`; adding back any one punctured frame line keeps the identity but raises the charge to 57.

## What the selected-profile price says

The verifier replays the PR717 per-port and copy-cost knob against the current selected T37 profile using the pinned moment and outer engines. It accounts for each removed port's source/target climb profile and nine rank-48 idle children per replica, changes eight rank-8 copy units to rank 7, checks the full coverage identity, and replays both exact moment engines.

In that favorable model the complex lower bound rises by 5.5311%, above the fixed bit primitive. The exact outer calculation is capped at κ = `0.001730427469823602`, 3.4536% above the selected κ. This is a budget for the mapped decoder mechanism, not a claim that the full P104 supplier is built.

The following implementation costs remain unresolved and are excluded from that price: asymmetric-centre reads/construction, phase-frame legality and restoration, PR717's unpaired-centre parity costs and pair-split conflicts, and integration into a complete replacement supplier with whole-call hosting. The selected record remains unchanged. No new κ is claimed.

## Reproduce

From the repository root, with Python 3.12+ and the standard library:

```sh
python3 -I -B research/selected-p104-port-adapter/verify.py
python3 scripts/research_package.py --package research/selected-p104-port-adapter --check-only
```

Expected verifier marker:

```text
PASS_SELECTED_P104_PORT_ADAPTER: 512 exact weights; 112-port GL adapter; P104 104 ports; 8 terms rank 7; exact selected-profile knob price; no full supplier or new kappa
```

The finite construction covers the fixed selected 112-mask set and one P104 frame pair. The exact map is checked on all 512 functionals; the decoder is checked entrywise on all 104² live pairs. Controls reject a corrupted adapter and decoder coefficient, and confirm the first restored port costs 57. No general classification of P104 adapters or other decoder classes is claimed.

## Open next questions

- Can this exact port adapter be compiled into a complete asymmetric-centre local word? The next step is to emit its full schedule, including phase frames and restoration, then recount the paid profile.
- Do the remaining extra construction costs keep the complex moment above the bit primitive? The favorable scenario has only about 2.0% complex-moment headroom over that primitive.

## Provenance and overlap

- Exact base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; selected-result SHA-256 is pinned in [SOURCES.json](SOURCES.json).
- The selected port source and E8 decoder model are pinned in [SOURCES.json](SOURCES.json), including their predecessor commits and payload hashes.
- PR717 and PR968 supply the abstract E8 model and P104 frame-pair decoder census. Open PR1619 prices the P104 puncture-depth knob but explicitly does not construct a selected-word decoder. This contribution supplies the selected 112-port adapter and one exact reindexed decoder; it leaves full supplier compilation and its extra costs open.
- Coordination claim: [CLAIM.md](CLAIM.md) and [Discussion #1163](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18919568).
- Submitted as [PR #1746](https://github.com/CrocSwap/integer-mult-bounds/pull/1746), open and mergeable at the recorded head; repository CI was pending at handoff.

Prepared with substantial OpenAI Codex assistance. Apache-2.0.
