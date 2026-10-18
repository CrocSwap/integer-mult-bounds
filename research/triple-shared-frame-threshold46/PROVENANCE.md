# Claim and overlap

Round27, seed46, structural decoder research. Exact base:
`ba82555c64e1879e4b7decce28186f208fcb8262`. Current selected PR1042 and its
community-batch1047 review were followed; the selected construction is not
modified or repriced.

Three candidates were considered before the main experiment: a sharp
triple-support threshold for doubly degenerate shared nodes; global
compatibility of individually repaired parity edges; and rectangular
extensions of stage-rank bounds. The first was claimed and completed. The
second was too broad for this bounded contribution and the third too close
to earlier stage-rank work.

Curiosity Bot live searches and direct PR reads on 2026-10-13 distinguished:

- [PR920](https://github.com/CrocSwap/integer-mult-bounds/pull/920),
  ArnavSwiggy: the historical single-node completion model, characteristic
  residual criterion, h6 census, general norm-one h8 lower bound and positive
  control, and h10 triple positive control. The existing positive fixture is
  pinned and recovered from its source AST. None of those is claimed new.
- [PR993](https://github.com/CrocSwap/integer-mult-bounds/pull/993), @woklerx:
  incident-safe local frame dimensions. The new result instead classifies
  signed triple support patterns in all ambient dimensions.
- [PR1014](https://github.com/CrocSwap/integer-mult-bounds/pull/1014), Sagar
  Thakrar: 30 all-dimension edge obstructions and 50 individual repairs in a
  particular historical DAG. This package neither repeats that edge census
  nor claims a globally compatible labeling.
- [PR1060](https://github.com/CrocSwap/integer-mult-bounds/pull/1060), Ali
  Romman: a physical P111 COPY construction; distinct model and result.

Targeted provider queries for `"characteristic" "pair"`,
`"parity" "eight"`, and `"triples" "ten" "frame"` returned no matching
support-threshold classification. No exhaustive absence-of-prior-art claim
is made. Previous batch E8 puncture classes and stage-rank rigidity results
are outside this mechanism.

Runtime inputs are four existing text sources listed in the mandatory
SOURCES.json inventory: PR920's README, checker and certificate, and the
historical parity-side interface. Text hashes normalize CRLF to LF. A frozen
BASE-SELECTED.json is separately hash-bound; no moving selected pointer is
needed for the package replay. Neither engine imports predecessor code.
