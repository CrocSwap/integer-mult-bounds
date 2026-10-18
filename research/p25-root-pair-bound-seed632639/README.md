# The p=25 root-pair support boundary misses the local-word gate

**Scoped structural obstruction; no supplier or new κ.** For eight-term exact
all-pairs decoders whose row and column normals are E8 roots, an exact 25-line
puncture can lower at most one root-normal support to a seven-dimensional
label span. The resulting separate-copy bill is at least **54**. Its most
favorable profile under the pinned selected-word relaxation has ceiling
`a < 0.001538546310036`, about **8.965% below** the selected local-word ceiling.
The support transition at the first puncture beyond the p≤24 floor is exact,
but it cannot supply the task's 5% gain inside this root-pair family.

## Exact support result

Use the 120 E8 root lines and the binary pairing

```text
B[i,j] = ( <r_i,r_j> + 1 ) mod 2.
```

For a root normal `a`, let `C(a)` be the lines with nonzero real inner product
with `a`. The live support label span drops to dimension at most seven exactly
when two independent functionals of the nine-dimensional label space vanish
on every live label. The corresponding puncture mask is the union of their
violators, intersected with `C(a)`.

The exact enumeration checks all 130,305 distinct functional pairs for each of
the 120 root normals. For every root, the least such union has 25 lines. There
are 189 pair representatives and 63 distinct masks of that size per root; each
mask has three pair representatives and leaves span exactly seven. Across all
roots, the 7,560 masks are distinct: one mask never lowers two root-normal
supports. Reinstating any one punctured line in a positive fixture returns its
support span to eight.

For a root-pair decoder, the row and column normals in each term are roots and
the two eight-element normal lists are dual bases. The F2 rank inequality gives

```text
copy(term) >= dim(row labels) + dim(column labels) - 9.
```

Every term without the unique seven-span root has bill at least seven. Duality
forces the unique exceptional root, if used on both sides, to occur in the same
term. That term costs at least five when used on both sides, or six when used
on only one. Thus the total copy bill is at least `5 + 7*7 = 54` (and at
least 55 if the exceptional root is used on only one side). If no support drops,
the total is at least 56. The bound covers every 25-line puncture in this
root-pair family. It does not cover arbitrary real or complex dual bases,
masked identities, or nine or more terms.

## Optimistic price

The selected #1094 local profile and ceiling calculator are pinned in
[SOURCES.json](SOURCES.json). Moving from its 112 ports to 95 ports removes 17
ports under PR717's favorable per-port model. The support floor 54 is priced
with the most favorable compatible rank histogram, one rank-five center child
and seven rank-seven center children. Added setup, frame, hosting, precision,
transition, and restoration costs are all set to zero. Raising any one center
rank raises its child moment and its center charge by the same amount, leaving
idle mass fixed; therefore this minimum rank vector upper-bounds the ceiling
of every more expensive root-pair invoice. The verifier also screens two
one-unit rank increases as controls.

| Quantity | Value |
|---|---:|
| Total punctures / live ports | 25 / 95 |
| Added port reductions from P112 | 17 |
| Separate-copy floor | 54 |
| Per-call local profile | `{1:2293, 2:418, 3:432, 4:125, 5:66, 7:7}` |
| Families / stages / center charge | `760 / 9 / 54` |
| Idle rank cap / idle mass | `51 / 830` |
| Certified `a` interval | `[0.001538546310035, 0.001538546310036]` |
| Selected `a` ceiling upper endpoint | `0.001690054109089` |
| Five-percent gate | `0.00177455681454345` |

The exact upper endpoint is below the selected ceiling itself, so no allocation
of idle work or additional physical overhead can make this p=25 root-pair route
pass the card's gate under the stated coverage law and halving guard. The
`kappa` translation recorded in [CERTIFICATE.json](CERTIFICATE.json) is only a
planning cap; it is not a new supplier or exponent result.

## Provenance and overlap

- Exact base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
- Accepted assignment: seed `632639f1d387026a8b953fa82c286d82`,
  `complex-mechanisms / complex-rank-shape-decoder`, priority revision 4.
- Catalogue SHA-256: `d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`.
- Selected-record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Selected certificate SHA-256: `1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045`.
- Selected review SHA-256: `7e76d2c38e5fce30587835b7251df1430488ae4dd372611ef69a3f03f476b6cb`.
- Selected source-manifest SHA-256: `79b3de5db3dbcb9829789ba58e9e45758926031e2a7d80667a08429d369be53b`.
- The selected-record reproduction command is `make frontier1094-verify`; it was not rerun because this package does not alter the selected source chain.

PR717 head `4a97676294f9fa413b65986e9984fddeda71e4cc` and PR968 head
`6a99e7240b961ac5e115ae6aa0301ec7c4a45d77` establish the exact eight-term
copy-floor lineage through 24 punctures, retained in
[the frame-pair package](../complex-frame-pair-decoders/PROOF.md). PR1619 head
`6c96bc1a0e374a713e9ae493228247f49be49dd5` prices that range. PR1624 head
`712a9b9aa8802d0135a578c0debee7b56c8e492f` and
[Discussion #1570](https://github.com/CrocSwap/integer-mult-bounds/discussions/1570)
handle one fixed p=26 paired-normal object, with PR1020 head
`bf4ee95df4ee6e3101a88f5d015c8aa85b688b6d` credited for its puncture and
baseline decoder. This result covers the p=25 root-pair family as a whole; it
does not audit or extend that fixed p=26 completion. The pre-submission refresh
also found open PR #2232 (head `3391f27dd0f226f0e1ead8b2b829eb6d3ec567d3`), an
E6 rank-four projected-Gram screen with an adapted pairing. It uses 36 E6 lines
and four-term projections, not the E8 p=25 root-pair support family here. Open
PR #2228 (head `ad1757e319225f3a5b86e3d3fa72897bd9f6db40`) gives a general dense
root-code floor and lists E8, P112 and P104 cases; its broader framework is
adjacent, while this package contributes the exact p=25 extremal-mask census
and an eight-term dual-root COPY bound. No claim is made that this result
exceeds the broader root-code theorem. The active ten-term P112 gauge, cyclic
mask and rank-six schedule claims use different objects.

The scope claim and handoff are tracked at
[Discussion #1167 comment 18937692](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18937692).
The focused package is submitted for review as
[PR #2237](https://github.com/CrocSwap/integer-mult-bounds/pull/2237).

## Reproduce

From the repository root:

```sh
python3 -I -B research/p25-root-pair-bound-seed632639/verify.py
python3 scripts/research_package.py --package research/p25-root-pair-bound-seed632639 --check-only
python3.12 scripts/research_package.py --package research/p25-root-pair-bound-seed632639
```

To regenerate the deterministic certificate, run the verifier with `--write`.
The implementation uses exact integer and rational arithmetic, checks input
hashes and Git object pins, enumerates the complete functional-pair domain, and
recomputes the moment bracket with the pinned standard-library ceiling engine.

## Open next questions

Can a non-root dual basis or an overcomplete/masked decoder at p=25 avoid the
one-exceptional-root restriction and pass the fully charged local moment gate?
That would test a genuinely broader support mechanism. The first step is to
choose one explicit non-root support alphabet, derive its exact support-rank
floor, and screen the complete profile before building a local network. No
source-aligned frame, hosting, precision, or restoration invoice for such a
family is presently identified.

## Credit

The E8 root and label model, p≤24 argument, selected ceiling, and p=26 fixed
completion retain their original PR and author credit in the pinned sources.
Prepared by Cinna Davis with substantial OpenAI Codex assistance in scope
selection, exact enumeration, cost screening, verifier implementation, and
writing. No independent human or proof-assistant review is claimed. New work
is Apache-2.0.

Maintainer integration note: exact originating guidance bytes are retained under `provenance/`; their original SHA-256 and base Git blobs are still checked. Live research priorities may advance independently. Mathematical inputs remain live-pinned.
