# Two interacting shears cannot lower the paired-Dn COPY floor

For every paired root graph, every product of two rational elementary basis
shears and every common directed fitting binary pairing, the complete algebraic
COPY bill is at least the number of live roots. This closes PR5176's explicit
two-changing-split question. Chains need an edgewise argument after the middle
column loses its coordinate anchor; opposite shears follow from a stronger
arbitrary two-coordinate GL2 lemma, including zero-product cancellation cases.

The joint minimum over the entire family is the coordinate bill. We do not
claim that each fixed nonzero two-shear basis attains that minimum. On the actual
12-root D5 predecessor graph, the complete common edge-pairing bills are13 for
a chain,15 for an opposite pair, and12 on an opposite cancellation locus.
All144 rational Gram entries are checked in each fixture.

The written proof gives the universal quantifiers. Bounded controls cover2268
factorizations on all nonempty three-coordinate paired graphs,40176 complete
common-pairing bills,10044 independent span-oracle comparisons,48 invertible
GL2 blocks and144 additional rational cancellation cases. Tests preserve one
pairing across all factor terms; they do not optimize each term separately.

Run from the repository root with Python3.12:

```
python3.12 -I -Werror -B research/dn-two-shear-pairing-floor/verify.py
python3.12 -I -O -Werror -B research/dn-two-shear-pairing-floor/verify.py
```

Both commands require RESULT.json and SOURCES.json. Complete receipt comparison
uses canonical JSON, including numeric types. `--check-only` checks source pins
and cheap rejection controls; `--emit` is explicit author-only output and is not
a registered acceptance command. No scientific evidence is silently regenerated.

Credit Nick Petalas PR5176 (e2adbcd3ea362cf3da3548c6982af1c8ce17915e),
ywz65 PR2536/2719, DreamingOfClouds PR3045 and the root-code/decoder lineage
credited in those sources. The exact predecessor proof and checker are pinned
as inputs for source attribution and the actual D5 fixture; its verifier is not
imported or replayed. New proof and checker: JoyboyBrian with substantial OpenAI
assistance, Apache-2.0. Independent AI review does not imply human or kernel
acceptance. No physical supplier, exponent or selected-frontier change is claimed.

## Open next questions

Three interacting shears on three coordinates may lose the edgewise support
condition. A useful next step must give an exact complete factorization and one
common fitting pairing with a favorable full bill. A lost minor is insufficient.
Single-sign deletions and general larger-block bases also remain open. Physical
producer/consumer, coefficient work, dirty return, frames, storage, movement and
outer multiplication costs are not supplied by this algebraic obstruction.
