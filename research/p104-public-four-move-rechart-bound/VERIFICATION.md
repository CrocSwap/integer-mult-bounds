# Verification and exact sources

The exact compressed #7334 word has SHA-256
`4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a`.
The exact compressed #7277 predecessor has SHA-256
`2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756`.
The exact historical support and helper cohort payloads are matched to
the public #7312 and #7319 replay hash manifests. [PROVENANCE.json](PROVENANCE.json)
records the exact commit and path for each and the Git blobs for the
vendored word, tariff and changed-role sources. [LOCAL-PINS.json](LOCAL-PINS.json)
pins every scientific input, engine and receipt by package-relative path.
The prior #7334 admission and full signed price readback are included as
immutable comparison receipts. The present replay checks the new
preprice and finite geometry, using that prior admitted comparator.

The original source-bound price took 0.30 s. The forward and reverse
literal runs took 0.10 s and 0.11 s under a nine-case and 20-second cap.
The relocated replays took 0.12 s and 0.09 s and matched byte for byte.
Both replays use CPython 3.12.14, isolated mode and assertions. The
standalone runner regenerates the price, forward, reverse and
comparison receipts from clean relative inputs. It rejects a changed
byte in the price, current word and ancestor word separately.
Synthetic controls cover an expanded intersection, a saturated
intersection, a low-union obstruction, an abstract new descriptor,
and an intervening source read.

A changed native word, signed chart supplier, precision/tape and
outer recurrence replay were not needed because every case was
excluded at geometry. Hosted checks are separate.
