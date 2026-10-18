# Seven-source 16-event connector: exact 60-mask maximum and 142-call obstruction

**Scoped construction and lower bound; no new κ.** For the original one-root
F2 dirty connector, exhaust the 18,918,900 normalized source paths where one of
seven sources is toggled four times and the other six twice. The outputs are all
63 masks of weights 1, 2, and 3. No path covers all 63. The exact maximum is 60,
attained by eight canonical words. One maximum path constructs a 60-output batch
at 136 complete map calls, saving 274 source-map calls against independent
per-output stars. The exact source path class is a scoped negative result; the
60-mask witness is a positive construction.

Together with the independently replayed 14-toggle predecessor census, the
result excludes full batches at both 140 and 142 complete map calls in this
event alphabet. Thus a full 63-mask batch needs at least 144 complete map calls
here. No 144-call construction is given or excluded.

## Best 16-event witness

Bit `j` denotes source `B_j`; mask decimals use the same convention. The best
canonical source word is

```text
0 1 2 0 3 1 4 3 0 5 4 0 6 5 2 6
```

Its prefix parity states are

```text
0 1 3 7 6 14 12 28 20 21 53 37 36 100 68 64 0
```

It covers all seven singleton and 21 pair masks, plus 32 of the 35 triples.
The missing masks are

```text
44 73 82
```

`RESULT.json` gives one valid pair of prefix boundaries for each of the 60
supported masks. The full histogram records eight maximum-coverage words and no
full-cover word. Relabeling the six twice-used sources is quotiented by assigning
their labels in first-appearance order; the four-use source is distinguished.

At boundary `t`, write `q_t` for the seven-bit parity vector of the source
toggles already called. For arbitrary dirty connector `z_0`, arbitrary F2-linear
maps `B_j`, and arbitrary inputs `x_j`,

```text
z_t = z_0 + sum_j q_t[j] B_j x_j.
```

For a supported output mask `M`, invoke its arbitrary map `A_M` at boundaries
`s,t` with `q_s XOR q_t = M`. The dirty term cancels:

```text
A_M(z_s) + A_M(z_t) = A_M(sum_{j in M} B_j x_j).
```

Each target's arbitrary dirty value also cancels because its map is called
twice. The source word uses multiplicities `(4,2,2,2,2,2,2)`, so it restores the
dirty connector. This proves the 60-output construction at every vector
dimension; the finite simulations in `verify.py` are controls, not the general
argument.

## Fully charged 60-output invoice

The supported 60 masks contain 145 source/output incidences. Their independent
stars use 290 complete `B` calls and 120 complete `A` calls: 410 total. The
shared path uses 16 complete `B` calls and the same 120 complete `A` calls: 136
total. The source-call savings per map are `[38, 40, 40, 38, 40, 40, 38]` for
this labeling.

Encode each event with one opcode bit, a three-bit `B` identifier or a six-bit
`A` identifier. Event order carries the boundary, so the schedule needs no
runtime search table. The independent-star stream is 2,000 bits; the shared
stream is 904 bits. If `c(B_j)` and `c(A_M)` are complete call prices, `lambda`
is the price per stored descriptor bit, `delta` is the per-event root-dispatch
price, and `I` and `P` are common admission and one-time coefficient preparation,
then

```text
C_shared = I + P + 4*c(B_0) + 2*sum_{j=1..6} c(B_j)
           + 2*sum_{M in S} c(A_M) + 904*lambda + 136*delta
C_stars  = I + P + 42*c(B_0) + 42*c(B_1) + 42*c(B_2)
           + 40*c(B_3) + 42*c(B_4) + 42*c(B_5) + 40*c(B_6)
           + 2*sum_{M in S} c(A_M) + 2000*lambda + 410*delta
C_shared - C_stars = -38*c(B_0) - 40*c(B_1) - 40*c(B_2)
                     -38*c(B_3) - 40*c(B_4) - 40*c(B_5) -38*c(B_6)
                     -1096*lambda -274*delta.
```

Each complete call includes source or target access, arithmetic, target update,
hosting, private-scratch restoration, and head return. All `A_M` calls remain
paid in both programs. This is a componentwise cost reduction for every
nonnegative descriptor and dispatch price and every positive complete map-call
price. No supplier in the selected assembly is shown to instantiate this
connector, so the result supplies no κ change.

## Why 140 and 142 full-batch calls are excluded

In this connector contract every active `B_j` and every required `A_M` must be
called an even positive number of times: arbitrary source contributions and
arbitrary dirty source/target rows must cancel. The 140-call floor is therefore
14 source calls plus 126 target calls. The exact 14-toggle predecessor census
has maximum pairwise-prefix-difference coverage 56 of 63, so it cannot attain
that floor.

At 142 complete map calls, the extra pair of calls has only two possible
allocations:

1. **16 source calls and 126 target calls.** Every target is read twice. The
   complete 16-event census here proves maximum coverage 60, so the full family
   is impossible in this profile.
2. **14 source calls and 128 target calls.** The 14-toggle census leaves at
   least seven targets without a pair of prefix boundaries. Only one target
   map can receive the extra two calls, so at least six targets still cannot be
   produced.

There is no 143-call profile because the complete map-call total is even. These
arguments exclude 140 and 142 only for the original source-toggle/single-target
event alphabet and the stated arbitrary dirty connector contract. They do not
exclude other operation alphabets, longer schedules, a 144-call schedule, or a
supplier outside this interface.

## Exact search and reproduction

The first search tests all 840 insertions of one extra source-toggle pair into
the pinned maximum 14-toggle predecessor word. It finds no full cover and a
maximum of 58 masks. The exact fallback enumerates every normalized word with
one four-use source and six two-use sources. The domain size is

```text
C(16,4) * 12! / (2^6 * 6!) = 18,918,900.
```

`search.py` generates the pair partition for the six two-use sources and
canonicalizes by first appearance. `verify.py` independently generates
restricted-growth source words, checks the full coverage histogram with a
bitset difference representation, and replays the prior 14-toggle census. It
also checks the 60-output dirty-state identity in dimensions 1, 2, and 3 and
four failure controls.

From the repository root:

```sh
python3 -I -B research/seven-source-16event-connector-seeda7de5e/search.py
python3 -I -B research/seven-source-16event-connector-seeda7de5e/verify.py
python3 scripts/research_package.py --package research/seven-source-16event-connector-seeda7de5e --check-only
```

Expected markers:

```text
SEVEN_SOURCE_16EVENT_SEARCH insertions=840 insertion_hits=0 fallback_examined=18918900 fallback_complete=true full_cover=0 best=60
PASS_SEVEN_SOURCE_16EVENT_BOUND old_domain=135135 old_max=56 new_domain=18918900 new_max=60 full_hits=0 max_words=8 outputs=60 calls=136 savings=274 controls=4
PASS_PACKAGE_METADATA_AND_PINS (not a mathematical acceptance check)
```

## Pins, overlap and limits

Public review: [PR #2236](https://github.com/CrocSwap/integer-mult-bounds/pull/2236), research commit `6687dfdd084a465582194258f416f24604136aaa`.

Cycle 28 used seed `a7de5e16e6ab896abb6ef4a0dc88a174`, track
`recursive-interfaces`, task `connector-alphabet-change`, priority revision 4,
selector scope key `0c9f43f3c7d61edb36fe`, refined scope key
`778d279ecd9a5bb9118d`, and base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. The selected-record SHA-256 is
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`; the
baseline binding check passed. The selected review, source manifest, certificate,
and reproduction command are pinned in `TASK.json` and `SOURCES.json`.

The predecessor is open PR #2229 at head
`b4eab83755969d406edba9f25b7890e4db4c4931`, with
`RESULT.json` SHA-256
`7e6ddf449de9c9a5c4a408346f9c172a48fcb1ae97075b055797a39fa91c1011`. That PR
is author-checked but not merged; this package independently replays its
14-toggle census for the 140/142 call split argument. The refreshed overlap scan
covered 470 open PRs and 931 Discussion/comment/reply records with complete
pagination and no warnings. Closest work includes #2128 (six-source universal
DUO path) and #2146 (six-source TRIO exclusion); the exact 16-event
seven-source multiplicity class was not present in the scan. The scan is a
novelty lead, not a certificate.

Local exact search and verification use CPython 3.14.7. The repository package
runner requests Python 3.12, which is unavailable in this environment; its
registered replay was not run. The package pin check and direct search/verifier
commands were run locally. The selected cold replay `make frontier1094-verify`
was not rerun because this research does not change the selected source,
certificate, or assembly. No independent human review or proof-assistant
formalization is claimed. Prepared by Cinna Davis with substantial OpenAI Codex
assistance in scope selection, proof derivation, exact search, verification,
cost accounting, overlap checks, and writing.

## Open next questions

Can any 144-call profile attain the lower bound for all 63 masks? First test the
18-source-call multiplicities `(6,2,2,2,2,2,2)` and `(4,4,2,2,2,2,2)` with all
target maps called twice. Separately bound or search the mixed profiles with 16
source calls and 128 target calls, or 14 source calls and 130 target calls.
The complete 16-event class is settled, but no 144-call construction or selected
supplier placement is known.
