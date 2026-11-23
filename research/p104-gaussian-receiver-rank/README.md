# Gaussian receiver ranks and chronological reroutes

This is a finite certificate for the exact normalized Gaussian word used by
[ToikY's #8072](https://github.com/CrocSwap/integer-mult-bounds/pull/8072),
head `75f7e1c44f48c43983016bcf8878c4d9e5e87c62`. It concerns one pinned
1,291-input, 5,674-transfer graph; it does not supply a replacement multiplier,
an improved price, a new κ, or a global impossibility result. The sender-space extension builds
on the original [#8074 certificate at head
`327e55157afb3a7a13e7ecb2b2cef20097d7feac`](https://github.com/CrocSwap/integer-mult-bounds/commit/327e55157afb3a7a13e7ecb2b2cef20097d7feac).

| Checked statement | Result |
| --- | ---: |
| Arrivals independent of all other arrivals and initial inputs at each destination | 5,674 arrivals on 977 receiving charts |
| Sum of ranks of the fixed local demand matrices | 5,660 |
| One-dimensional rational local demand nullspaces | 14 charts |
| Chart 595: minimum arrivals from its two unchanged sender stocks, even with receiver recoding | 8 |
| Deficient receivers where one port cannot be deleted under original sender-stock and per-sender port caps | 12 of 14 |
| Of those, receivers also excluded with unrestricted reallocation among the original senders | 8 |
| Directed depth-cut rank lower bound versus the graph's total transfer grade | 9,527 versus 9,639 |
| Strictly cheaper nested alternate senders with nonempty original stock | 140,277 cases |
| Screening survivors, all requiring an original descendant of the replaced transfer | 171 |
| Original-sender two-receiver shared-packet incidences excluded with a cheaper relay | 58 of 58 |

The single-link screen rules out only a **same-value** reroute while the
other donor functions and their dependency graph remain fixed. We give each
alternate sender its entire original stock, even values produced later in the
original schedule. For the 171 survivors, the unique full-stock coordinates
need a descendant of the transfer, which would create a cycle; simply reordering
independent later work cannot fix that. Empty-stock charts cannot send the
nonzero target by a linear combination. Changed transported values, receiver
recoding, multiple edits and redesigned donor graphs remain open outside the
following limited broadcast screen.

The 14 nullspaces concern **local downstream demand**, not dependence among
the delivered values. Their existence does not construct 14 removable links.
For chart 595, a separate sender-space certificate strengthens the local rank-7
bound: seven arrivals cannot reproduce its fixed demands using its two original
sender stocks, even if their values and the receiver basis are changed and all
stock is available acausally. The existing eight arrivals attain this count.
This sharper result does not cover new sender stocks, other routes or nonlinear
communication.

A separate sender-space calculation now covers 12 of the 14 deficient charts,
including 11 charts beyond 595. For each it excludes deleting one arrival when
each original sender's stock and per-sender port cap are fixed, even granting
all stock acausally and allowing arbitrary linear transmitted values and
receiver decoding. At eight of these charts the same bounds also exclude any
reallocation of the remaining ports among the original senders. The other
four exclusions require their original per-sender port caps. Charts 470 and 599
remain inconclusive. New routes or stock and changed downstream demands remain
outside the results. The separate exact chart-595 proof independently permits
reallocation between its two unchanged senders. See the detailed
[sender-space receipt](sender-space-result.json) and [proof](PROOF.md).
A [two-receiver addendum](BROADCAST.md) allows an arbitrary changed packet
from the original sender and arbitrary linear decoders at both receivers,
with the other original stocks granted acausally. It tests all 11,819 actual
`u: a -> b` read by `v: b -> d` incidences and every properly nested relay
for the cases where the source and second receiver are different. Of 58
incidences with a strictly lower raw-grade route, 47 have no nonzero
common packet over Q and 11 can share only a multiple of `u`, which cannot
decode the removed `v`. Eight cases where the sender is the second receiver
also cannot introduce that missing information. This supplies no price or κ.
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
and an acyclic later sender that requires rescheduling. The second registered
command recomputes the 12-chart sender-space bounds and the nonzero modular
minor for every receiver–sender pair. Its deliberate corrupt-minor control must
fail with a nonzero exit status:

```sh
python3.12 -I -B research/p104-gaussian-receiver-rank/sender_space.py
python3.12 -I -B research/p104-gaussian-receiver-rank/sender_space.py --corrupt-minor
```

The first sender-space command must pass; the second zeroes a row of the actual
chart-477, sender-288 minor and must reject it.

The third registered command runs the shared-packet census, exact rational
identities and positive/negative toy controls. Its separate mutation option
changes one actual rational coordinate and must exit nonzero:

```sh
python3.12 -I -B research/p104-gaussian-receiver-rank/broadcast.py
python3.12 -I -B research/p104-gaussian-receiver-rank/broadcast.py --corrupt-coordinate
```

The baseline verifier can additionally
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

- Can charts 470 and 599 be resolved with stronger source-space bounds, or can
  another sender allocation or changed stock exploit a null direction while
  preserving a legal chronological graph and all owner returns?
- Can any such executable redesign improve the complete, directed signed price
  after the actual 48-call supplier, physical costs and other obligations are
  included? No changed invoice is supplied here.
