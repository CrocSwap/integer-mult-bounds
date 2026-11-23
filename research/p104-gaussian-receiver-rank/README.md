# Gaussian receiver ranks and chronological reroutes

This is a finite certificate for the exact normalized Gaussian word used by
[ToikY's #8072](https://github.com/CrocSwap/integer-mult-bounds/pull/8072),
head `75f7e1c44f48c43983016bcf8878c4d9e5e87c62`. It concerns one pinned
1,291-input, 5,674-transfer graph; it does not supply a replacement multiplier,
an improved price, a new κ, or a global impossibility result.

| Checked statement | Result |
| --- | ---: |
| Arrivals independent of all other arrivals and initial inputs at each destination | 5,674 arrivals on 977 receiving charts |
| Sum of ranks of the fixed local demand matrices | 5,660 |
| One-dimensional rational local demand nullspaces | 14 charts |
| Chart 595: minimum arrivals from its two unchanged sender stocks, even with receiver recoding | 8 |
| Directed depth-cut rank lower bound versus the graph's total transfer grade | 9,527 versus 9,639 |
| Strictly cheaper nested alternate senders with nonempty original stock | 140,277 cases |
| Screening survivors, all requiring an original descendant of the replaced transfer | 171 |

The final row rules out only a **single-link, same-value** reroute while the
other donor functions and their dependency graph remain fixed. We give each
alternate sender its entire original stock, even values produced later in the
original schedule. For the 171 survivors, the unique full-stock coordinates
need a descendant of the transfer, which would create a cycle; simply reordering
independent later work cannot fix that. Empty-stock charts cannot send the
nonzero target by a linear combination. Changed transported values, receiver
recoding, multiple edits and redesigned donor graphs remain open.

The 14 nullspaces concern **local downstream demand**, not dependence among
the delivered values. Their existence does not construct 14 removable links.
For chart 595, a separate sender-space certificate strengthens the local rank-7
bound: seven arrivals cannot reproduce its fixed demands using its two original
sender stocks, even if their values and the receiver basis are changed and all
stock is available acausally. The existing eight arrivals attain this count.
This sharper result does not cover new sender stocks, other routes or nonlinear
communication.
The cut ranks lower-bound scalar communication under the specified fixed linear
input/output and endpoint contract; the gap of 112 grade units is not a
realizable saving. See [PROOF.md](PROOF.md), the full [RESULT.json](RESULT.json)
and the [exact rational null witnesses](null-sources.json).

## Reproduce

With CPython 3.12 and `numpy==1.26.4`:

```sh
python3.12 -I -B research/p104-gaussian-receiver-rank/verify.py
# Or, in the repository's registered package runner:
python3.12 -I -B scripts/research_package.py --package research/p104-gaussian-receiver-rank
```

`verify.py` authenticates both the compressed bytes and the canonical full
uncompressed graph before computing all results. It checks each rational null
vector with `fractions.Fraction`, proves the finite-field arithmetic bounds,
checks the chart-595 sender obstruction and all 171 modular coordinate
witnesses, and exercises a signed-rational
example over a second prime with an available sender, a forbidden descendant,
and an acyclic later sender that requires rescheduling. It can additionally
compare a previously installed, source-pinned runtime:

```sh
python3.12 -I -B research/p104-gaussian-receiver-rank/verify.py --runtime /path/to/installed-8072/runtime
```

For the independent source reconstruction, obtain the exact #8072 package at
head `75f7e1c44f48c43983016bcf8878c4d9e5e87c62`, including its archive, and run:

```sh
python3.12 -I -B research/p104-gaussian-receiver-rank/rebuild.py \
  /path/to/research/p104-weighted-capped-allocation-490950
```

The optional rebuild checks the exact #8072 `verify.py` and `prepare.py` bytes,
uses their own authenticated #8057 archive restoration and bootstrap, and
compares the whole rebuilt normalized graph and layout to the frozen input. It
uses a temporary directory and requires `git`; the archive need not be copied
into this package or fetched by the normal replay. The pinned source drivers are
[#8072 verify.py](https://github.com/ToikY/integer-mult-bounds/blob/75f7e1c44f48c43983016bcf8878c4d9e5e87c62/research/p104-weighted-capped-allocation-490950/verify.py)
and [prepare.py](https://github.com/ToikY/integer-mult-bounds/blob/75f7e1c44f48c43983016bcf8878c4d9e5e87c62/research/p104-weighted-capped-allocation-490950/prepare.py).
The source's `strong_complex.load_changed` rebuilds the journals, verifies their
input hashes, and checks the graph and layout digests. The canonical word digest
is `38d2b3a2311a9ba5fee091cc7aa204c7ed95651aec95d75184b2391df090cbfb`;
the compressed-file digest is
`e5c1477c1b33c5cfe112fc0fd503f7dd01d1ccc556d229e76c11b1fbb7d01bb4`.

This is an author-side computational certificate, not a claim of independent
scientific acceptance. The pinned archive and predecessor notices identify the
source history; [NOTICE.md](NOTICE.md) and [PARENT-NOTICE](PARENT-NOTICE) retain
the relevant credits. The generic package metadata pins the historical task
catalogue at base `0618e75a22cec54d1651394ef83d088551b7f026`; that provenance
base is distinct from the #8072 graph source head.

## Open next questions

- Can changed transported values and receiver-side decoding exploit one of the
  14 rational null directions while preserving a legal chronological graph and
  all owner returns?
- Can any such executable redesign improve the complete, directed signed price
  after the actual 48-call supplier, physical costs and other obligations are
  included? No changed invoice is supplied here.
