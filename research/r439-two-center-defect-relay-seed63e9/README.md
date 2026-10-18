# Two-center in-flight defect relay: scoped obstruction

This package tests one concrete way to reduce the scalar cost of the pinned
R439 helper-star word: remove one terminal `D` restoration at each of a
reciprocal pair of helper centers, then repair the resulting coupled defect by
editing one `A` source tap at each of two distinct gates. It finds no repair
with a strict scalar `ADD` saving in this finite domain. This is a scoped
negative result; it does not bound larger edits or other words.

## Exact scope and result

The source is the PR #1062 11,500-`ADD` word
`research/r439-bsection-stars-seed01/candidate.json.gz`, pinned by SHA-256
`b452d2c2b0b2a546d1105b1da9769aa78e5c54d6f00e97b30c77e3f54ce445ee`. The
experiment covers all three reciprocal singleton first-read center pairs in
that word:

| Centers | First `A` reads | Terminal `D` leaves | Omission cases |
| --- | --- | --- | ---: |
| `(643, 525)` | `(1517, 1525)` | `(594, 287)` | 1 |
| `(648, 526)` | `(1496, 1502)` | `(589, 543)` | 1 |
| `(650, 534)` | `(1576, 1583)` | `(602, 570)` or `(372, 570)` | 2 |

For each of the four two-restoration omissions, the verifier computes the
complete `F_2` state map and its reverse over all 661 formal columns. The
forward omission residual has rank 2. Its output-column support is contained
in the span of the perturbation supports of six `A` gates, with two distinct
supports. Consequently there are five distinct-support gate pairs per case.
For every gate pair, both possible interaction orientations are solved
exactly, giving 20 gate pairs and 40 factorizations total.

The factorization solves for the two source-state masks that the tap edits
must introduce. It also accounts for the first edit changing a donor read at
the later gate. For each factorization, the verifier inventories tap removal,
addition, and replacement actions across every register label. This relaxes
the frame rule by allowing even labels unavailable at the gate. No action pair
meets the map equations and scalar budget.

The scalar charge is explicit: two omitted `D` taps save 2 `ADD`s, so a strict
net saving requires the two `A` edits together to cost at most +1 `ADD`:

```text
delta_ADD = -2 + delta_A_taps <= -1
```

Because no pair restores the complete boundary even under the relaxed
all-register donor inventory, frame legality, frame-path equality, paid
profile, and the remaining recursive assembly costs cannot admit a candidate
within this domain. No value of `kappa` or supplier improvement is claimed.

The pinned parent word costs 11,500 native `ADD`s, has paid profile
`{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}` with mass 5,129, and has
integer bounds `F=25,717`, `B=5,911,840`. Its local and nine-stage precision
guards use 95 and 182 bits, respectively. These are source-word values, not a
cost claim for an accepted two-center construction.

## Controls

The positive control replays the known one-edge absorption from PR #1937:
omit `514 ^= 367` and change the source of `A[304]` to `[360]`. The exact
forward and reverse maps, frame paths, and paid profile match the parent;
native `ADD`s fall from 11,500 to 11,499 and `D` `ADD`s from 5,548 to 5,547.
Its `F/B` bounds are `25,717 / 5,874,310`, with the same 95/182-bit guards and
paid mass 5,129. The negative control changes that source to `[361]` and checks
that the forward map changes.

These controls show that the replay accepts a known valid absorption and
rejects a wrong donor. They are finite checks of this word, not a theorem about
all helper circuits.

## Provenance and overlap

- Track: `bit-mechanisms`; task: `bit-helper-contract`; priority revision 4.
- Seed: `63e9ed039147038f4e817746114c150d`.
- Base commit: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
- Task catalogue SHA-256: `d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`.
- Selected record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Selected review, source manifest, and assembly are pinned in `SOURCES.json`;
  their SHA-256 values are `7e76d2c38e5fce30587835b7251df1430488ae4dd372611ef69a3f03f476b6cb`,
  `79b3de5db3dbcb9829789ba58e9e45758926031e2a7d80667a08429d369be53b`, and
  `1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045`.
- Parent word: [PR #1062](https://github.com/CrocSwap/integer-mult-bounds/pull/1062),
  head `cd016e5dcd5ba28dafa3f3b4eeef003a38e6a11b`, by Sagar Thakrar.
- Nearest overlapping work: [PR #1937](https://github.com/CrocSwap/integer-mult-bounds/pull/1937),
  head `8b4a4d59eb5df9971d44587d9980c3dd0b18fc96`, by Aaron Wang. That package
  includes the positive control and explicitly leaves in-flight intermediate
  defect-vector injection unmodeled; this result covers only the four pinned
  reciprocal-pair omission cases and the stated two-tap budget.
- A completed one-restoration post-read study was found in [Discussion #1166,
  comment 18930632](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18930632).
  That single-restoration scope was retired before this experiment.
- No advance claim was posted for the changed scope. Report this package as a
  `FINDING`/`DONE` result, not a maintainer-reviewed conclusion.

## Reproduce

Run the registered replay with Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/r439-two-center-defect-relay-seed63e9 --check-only
python3.12 scripts/research_package.py --package research/r439-two-center-defect-relay-seed63e9
```

The registered metadata check pins the full provenance chain and live inputs;
the verifier rechecks the candidate and checker hashes, the selected record and
catalogue at the pinned base commit, parent maps in both directions, all four
omission residuals, rank/support factorizations, all-register tap action
inventory, scalar budget, integer precision guards, profile, controls, and
deterministic certificate equality. The initial package replay was run locally
with Python 3.14.7; the repository's generic replay uses Python 3.12.

## Open next questions

Can three or more `A` tap edits, or a nonreciprocal center pair, create a fully
charged multi-center defect relay? This matters because the current obstruction
does not eliminate larger correction sets, and those could supply a further
scalar saving before recursive assembly. For a fresh investigation, derive the
rank-three residual factorization and its fully charged tap budget before
expanding the search. This package does not cover three or more edits,
nonreciprocal centers, other source words, `B/C` changes, or supplier
re-evaluation.

## Credit

The parent word and known absorption control are attributed to Sagar Thakrar
(PR #1062) and Aaron Wang (PR #1937). This package was prepared with substantial
OpenAI Codex assistance; no independent human review is claimed.
