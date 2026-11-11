# Involutive source reflection for the current two E8 supplier words

**Draft local construction; no new kappa or admitted routed supplier.**
The eight rank-eight centre children of each pinned local word can be replaced
by eight rank-one target repairs if the source may leave under an explicit
involution. All 480 arbitrary helpers are restored and all eight owned private
outputs are zero. This changes the local interface, so its rank saving cannot
be inserted into the selected invoice without further work.

For the source query matrix R and injection K, RK = 14I. Choose the eight
orthogonal compensation ports A and the supported right inverse P, RP = I.
Set U = K - 12P and F = I - UR. Then

```
F^2 = I,     RF = -R,     (I-KR)F - I = 12PR.
backward: (x,y,h,c) -> (x-y, Fy, h, 0)
forward:  (x,y,h,c) -> (Fx, y+Fx, h, 0)
```

This specializes the source-preparation freedom in
[Ali Romman's PR1862](https://github.com/CrocSwap/integer-mult-bounds/pull/1862)
at `bb29ea73ad9be9a0c3d53cdcb1d22b2ee9ffe42f`, dropping its fixed selected
full-query logger requirement. We claim the explicit involution, its emitted
current-word instances and their local checks, not priority for general
low-rank source preparation. See [PROOF.md](PROOF.md).

## Local result

The current inputs are replay artifacts of
[PR1800](https://github.com/CrocSwap/integer-mult-bounds/pull/1800)
at `46d865ab92e58098538b8c5348b6a131c99abf45` (pivot-566 and pivot-554 lineage).
Every entry below applies in each orientation.

| Provider | Original recursive profile | Reflection profile | Rank mass |
|---|---|---|---|
| base | {1:2348, 2:500, 3:416, 4:130, 5:82, 8:8} | {1:2356, 2:500, 3:416, 4:130, 5:82} | 5590 -> 5534 |
| extra | {1:2340, 2:508, 3:420, 4:126, 5:82, 8:8} | {1:2348, 2:508, 3:420, 4:126, 5:82} | 5594 -> 5538 |

The complete emitted scalar allowance is 217,622 real primitives per coordinate
per call under the retained dyadic tariff. This is not the recursive cost,
a precision bound, or a total hosted supplier cost. Retained climb/adapter
sequences are unchanged. Added operations use the existing C0 field.

## Alternative with restored sources

`--interface reflection-shear` emits a second interface:

```
backward: (x,y,h,c) -> (x-Fy, y, h, 0)
forward:  (x,y,h,c) -> (x, y+Fx, h, 0)
```

It retains the same 56-unit local rank-mass saving and eight rank-one repairs,
restores all source rows, and lowers the scalar allowance to **208,310**.
The literal implementation negates the target repair and omits source
preparation; `PROOF.md` derives the maps. This is a changed transferred
operator, not a restored identity-shear supplier. Full routed composition
and a valid final correction remain unresolved. Uniform-cover cancellation
alone is insufficient.

## Reproduce the local checks

Standard library, Python 3.11 or newer; run without optimization:

```sh
python3 -I -B research/involutive-source-reflection/verify.py
```

Default execution is read-only. Optionally append `--out /path/to/fresh-output`
to retain RESULT.json; an existing output directory is refused. `-O` and `-OO`
are explicitly refused because this verifier uses assertions. There is no
network dependency or Git-history dependency during replay.

Append `--interface reflection-shear` to check the second interface.

The verifier checks raw input and vendor hashes before imports, then:

- Reconstructs the clean-J scalar interfaces from both frozen local programs.
- Derives R, K and the compensation minor; verifies F squared, RF and JF identities.
- Replays all 712 independent scalar input columns of four complete words.
  A separately implemented backward/adjoint interpreter must agree.
- Checks inherited core frame access and the added boundary access separately.
- Checks 16,384 exact Gaussian basis columns for added positive/inverse native
  line recipes across both providers, including phase/sign mutation controls.
- Recounts profiles and scalar allowance; rejects omitted target corrections.

These checks do **not** replay the full native operator composition, source
routing across different charts, global controller, owner hosting, precision,
or outer reduction. The default interface changes all 112 source rows; the alternative
restores them and transfers F instead of identity. Local success is not a proof of the all-size multiplication theorem.

[SOURCES.json](SOURCES.json) distinguishes generated replay inputs from Git
source provenance and records compressed and decompressed hashes. The frozen
current inputs are checked here, but their upstream generators are not rerun.
The historical archive pins inside unchanged vendor modules are unused metadata,
not certificates for these current words.

## Comparison and overlap

The selected main record at base `0b1cccf8` remains conditional kappa
0.001672660197076918. Pending PR1928 claims a finer endpoint beginning
0.00167975495612554452133567099392070257 for the existing T74 construction;
that decimal is not a result of this package. The latter retains all inherited
all-size and prime-theorem assumptions and is not independently replayed here.

A snapshot of 580 open PR bodies and 40 recently updated Discussion bodies was
searched before submission. PR1862 is the direct predecessor. PR1719's
involutive Walsh frame lift changes a different frame model. PR1918 studies
composed scalar centre-query rank, not this source involution. This bounded
search does not establish novelty or exhaust all Discussions.

The local default and source-restored replay receipts are `LOCAL-REPLAY.json`
and `RESTORED-LOCAL-REPLAY.json`; their hashes identify the exact checker
versions used. Earlier receipts may refer to an earlier checker revision.

## Open next questions

1. **Can source reflection be removed across actual stage routes?** This decides
   whether the local saving survives composition. First construct the exact
   routed two-call boundary using these F matrices. Blocker: F mixes ports with
   different cover routes; F squared in one chart does not justify cancellation
   across stages.
2. **Can the repaired nine-call controller retain an improved paid invoice?**
   First derive and price the required decoder on actual routed data. Full
   native/hosting replay and source restoration are blockers; a constant-cover
   scalar decoder is insufficient.
3. **Can the complete new supplier pass precision and outer admission?** Run
   those checks only after obtaining the routed controller and owner map.
   Neither a new kappa value nor a ready-for-review supplier claim is justified
   by the current local result.

## Credit

Prepared by Rohan Arun with substantial OpenAI Codex assistance. No independent
human review or Lean proof is claimed. Apache-2.0. Ali Romman's PR1862 supplies
the source-preparation interface and vendored algebra/checkers. Current words
retain mdumitrean's pivot-566 work, Jeremy Kothe's composition/replay lineage,
Rohan Arun's T74 owner construction and the earlier gauge44, icekylinx,
Hao Yan/FanPUYen, Chafik Boukhalfa and retained supplier lineage. Exact original
notices are preserved in `notices/` and `vendor/pr1862/NOTICE.md`.
