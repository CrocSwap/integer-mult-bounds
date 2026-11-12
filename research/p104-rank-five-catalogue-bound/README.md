# Catalogue and prefix bounds for rank-five P104 splits

**NO VERIFIED GAIN.** Exact Δκ = 0 relative to the independently
reproduced conditional κ = `0.00364665195644` on
[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
`aaeec8c0acf01e99a5f331ef363a698d9c084ace`, with signed
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
`07a76c5e2738882c0cb322278e56f6cae3c9885d`.

A fixed-paid rank-five productive split would replace one target
by ranks two and three. The largest exact endpoint group has nine
helpers on chart 1090→127. An independent GF(2) check excludes all
336 catalogue labels of its two required intermediate dimensions.
No support test is needed for that group.

Across all 80 eligible helpers in 28 endpoint cohorts, the literal
geometry has 68 raw bank representatives. The selected 3→241
cohort, roles 339 and 1101, has 19. Two prime-field engines agree
on 11 direct prefix exclusions. Eight proved same-bank signed ADD
transfers close the rest of that cohort. The other 49 representatives
are outside the selected support scope. [Selected-cohort agreement](receipts/R115-AGREEMENT.json).

## Replay

From a clean checkout with CPython 3.12 and assertions enabled:

```sh
python3.12 -I -B research/p104-rank-five-catalogue-bound/replay.py
```

The standard-library replay rebuilds both complete directed prices,
the two catalogue geometries, the independent GF(2) exclusion, and
both selected-cohort prefix and transfer certificates. It rejects
altered selection and alias inputs. Use `--out fresh-directory` to
retain all nine receipts. It requires only the included inputs and
works without Git metadata, network or prior temporary state.
[Proof and price](PROOF.md) · [Provenance](PROVENANCE.json) ·
[Path-keyed hashes](LOCAL-PINS.json).

## Open next questions

Use the regenerated R115 geometry to select one additional endpoint
group from the 49 untouched bank representatives. Keep its endpoint
cohort fixed and freeze its exact public banks before checking
prefix and suffix support. A different chart description or paid
itinerary requires its own directed price and signed verification.

## Credit

[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
and [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
supply the exact native word and signed caller.
[#7314](https://github.com/CrocSwap/integer-mult-bounds/pull/7314)
and [#7319](https://github.com/CrocSwap/integer-mult-bounds/pull/7319)
supply the inherited helper census, [#7338](https://github.com/CrocSwap/integer-mult-bounds/pull/7338)
the exact admission and price inputs, and
[#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)
the tariff. [#5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599)
supplies the paired split identity,
[#5994](https://github.com/CrocSwap/integer-mult-bounds/pull/5994)
the broad endpoint census precedent on an older word, and
[#7367](https://github.com/CrocSwap/integer-mult-bounds/pull/7367)
the same-word prefix and transfer method at a different productive
rank. OpenAI Codex and subagents materially assisted proof,
implementation, independent verification and packaging.
