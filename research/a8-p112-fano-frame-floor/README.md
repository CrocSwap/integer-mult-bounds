# Independent check: A8 simplex cost 71 on every P112 frame puncture

For the fixed A8 simplex nine-term all-pairs decoder, the minimum separate-term
binary pairing-rank cost is **71 on every orthogonal eight-frame puncture of
P120**. The minimum is attained with all nine terms active. This is a scoped
proof with exhaustive finite lemmas, not a new supplier or multiplication bound.

[PR1304](https://github.com/CrocSwap/integer-mult-bounds/pull/1304), by
commdata2338, established 71 on the 945 matching-frame punctures and explicitly
left the other frame orbits open. This package proves 71 on the other 1,080
frames and checks that these two coordinate-permutation orbits exhaust all
2,025 frames. It replays the earlier orbit as a positive control. Since 71
exceeds the standard P112 copy cost 64, this family cannot lower that
copied-information bill.

**Concurrent work:** the final overlap refresh found a
[claim for the same remaining orbit](https://github.com/CrocSwap/integer-mult-bounds/discussions/1241#discussioncomment-18914233),
posted at 03:38 UTC on October 14 after this session's entry snapshot. That
claim reported the same frame census and cost-71 witness, with the lower bound
still being checked. This submission is therefore **independent corroboration**
with a completed lower-bound replay, not a claim of unique discovery. Its
separate Gram-derived checker and all-anchor source-bound replay are the
reviewable contribution; no unpublished implementation from that session is
imported or assumed correct.

## Reproduce

From the repository root, using Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/a8-p112-fano-frame-floor
```

The registered replay runs the primary verifier, a separate implementation,
and six package failure controls. For a standalone source export, these commands
need only this directory and Python 3.10 or later:

```sh
python3 -I -B research/a8-p112-fano-frame-floor/verify.py
python3 -I -B research/a8-p112-fano-frame-floor/independent.py
python3 -I -B research/a8-p112-fano-frame-floor/test_package.py
```

Expected markers:

```text
PASS_A8_P112_ALL_FRAME_FLOOR frames=2025 orbits=945,1080 planes=781830 sharp_cost=71 active_terms=9
PASS_A8_P112_INDEPENDENT frames=2025 anchors=4 transported=18 planes=173740 compatible_leaves=184628 sharp_cost=71
```

`verify.py --write` explicitly regenerates `CERTIFICATE.json`. Normal replay
compares the entire recomputed receipt without writing it. The generic package
metadata check needs the base Git history; standalone mathematical replay does
not need Git, network access, or another research package.

Local validation passed on macOS 27.0.1 arm64: the registered replay and all six
package controls on CPython 3.12.13, plus both mathematical checkers under
isolated, optimized CPython 3.14.6 from a relocated read-only package. The
selected-record integrity check also passed. Hosted CI and human review are
separate from this local evidence.

## Model and quantified statement

Use the sum-zero subspace V of C^9 and the 120 oriented E8 root lines:

- `e_a-e_b`, for `0 <= a < b <= 8`, in lexicographic order;
- `1_S-(1/3)1`, for three-element subsets S, in lexicographic order.

Remove an orthogonal frame F of eight lines and let R contain the 112 surviving
roots. Fix the nine simplex normals `b_k=e_k-(1/9)1`, so `T_ik=r_ik`. Allow
arbitrary complex D satisfying `D T^t = 2 R R^t` on **all** live pairs, with
ordinary transpose. Charge each term separately by the F2 rank of
`(r_i dot r_j + 1) mod 2` restricted to its actual nonzero row and column supports.

**Theorem.** For every such F and D, the total charge is at least 71. For every
F there is a rational D attaining 71 with all nine terms active.

This changes the eight-term hypothesis of the earlier decoder floor. It does
not relax exactness to a masked graph. The theorem concerns the fixed simplex
normals, not every nine-term decoder.

## Proof

### 1. Exactly two frame orbits

Exhaustive increasing-index clique enumeration in the exact orthogonality graph
finds 2,025 frames. Adjacent coordinate transpositions generate S9. Closing the
following representatives under those generators gives disjoint sets of sizes
945 and 1,080, whose union equals the complete frame census:

```text
matching: [0,15,26,33,42,89,112,119]
Fano:     [0,85,94,99,105,108,112,113]
```

The matching representative has four pair roots. Its frames are described by
one singleton coordinate and a perfect matching of the other eight coordinates,
as in PR1304. The Fano representative has the pair root `e_0-e_1`, together with
triple roots on

```text
234, 256, 278, 357, 368, 458, 467.
```

These are the seven lines of a Fano plane on coordinates 2 through 8.
Independently generating the 30 labelled Fano planes for each of 36 coordinate
pairs produces the same 1,080 frames. The separate checker also reconstructs all
945 matching frames and compares their union with its own orthogonality census.

Coordinate permutations preserve the simplex family and root lines, possibly
reversing pair-root representatives. Apply the corresponding row signs to both
factors. This preserves the all-pairs identity and every support. Signs also
preserve the binary pairing since the Gram entries are integers. Thus proving
the cost statement for both representatives proves it for every frame.

### 2. Deficiency spaces cover all complex shifts

The live roots span V; each representative is checked exactly. Therefore

```text
D_ik = 2r_ik + t_i,    t_i arbitrary in C.
```

Indeed every row of `D-2R` annihilates V and is a multiple of the all-ones vector.
Use binary labels `u_ab=1+e_a+e_b` and `u_S=1_S`. Their dot product equals the
binary Gram pairing on all 14,400 root pairs. For both representatives and every
column k, the labels on `{i:r_ik != 0}` span F2^9.

Let K_k be the annihilator of the labels on `{i:D_ik != 0}`, and write
`delta_k=dim K_k`. Full column span makes the cost exactly

```text
81 - sum_k delta_k.
```

If `w in K_j` and `z in K_k` both evaluate nontrivially on a live label u_i,
then `D_ij=D_ik=0`, which forces `r_ij=r_ik`. This necessary compatibility
condition applies to arbitrary complex shifts, including shifts with no zeros.

If every deficiency is at most one, their sum is at most nine. Otherwise choose
an anchor j and a binary plane U contained in K_j. There are exactly 43,435
planes, represented uniquely by `0<a<b<a xor b`. For each other k, compute
H_k(U), the annihilator of all labels u_i where `r_ij != r_ik` and some member
of U evaluates nontrivially. Necessarily `K_k subset H_k(U)`.

The complete census checks that every H_k has dimension at most two. Enumerate
every subspace L_k of each H_k: zero, its lines, and its whole plane when present.
Discard choices incompatible between two distinct non-anchor columns. Let Q
span all labels where some chosen L_k evaluates nontrivially and
`r_ij != r_ik`. Compatibility requires `K_j subset Q^perp`, giving

```text
sum_k delta_k <= 9 - dim Q + sum_(k != j) dim L_k.
```

The actual tuple `L_k=K_k` is included and survives the necessary tests. Thus an
upper bound on this finite relaxation bounds every complex decoder. The method
is PR1248/PR1304's; the new puncture's finite claims are recomputed. Grouping
identical ordered H_k tuples saves repeated work but does not omit any plane.

### 3. Exact finite bounds

The primary verifier checks all nine anchors in each representative. Counts
below are **per anchor**, not multiplied by plane multiplicities:

| Representative | Anchors | Planes | Distinct H tuples | Compatible choices | Maximum bound |
|---|---|---:|---:|---:|---:|
| Matching, earlier result | 0 through 7 | 43,435 | 2,131 | 52,832 | 10 |
| Matching, earlier result | 8 | 43,435 | 2,251 | 39,485 | 9 |
| Fano, new result | 0 and 1 | 43,435 | 2,131 | 52,829 | 10 |
| Fano, new result | 2 through 8 | 43,435 | 2,251 | 39,482 | 9 |

The new orbit therefore contributes 390,915 planes, 20,019 ordered H tuples and
382,032 compatible choices. In both representatives the deficiency sum is at
most ten, proving cost at least 71.

The separate implementation imports neither the primary nor predecessor code.
It derives nine-bit coordinates from independent columns of the binary Gram
matrix, obtains H_k by row reduction and nullspaces, and enumerates Cartesian
products. Compatibility is checked by agreement of forced per-row shift values.
It checks two anchors per representative and explicitly verifies puncture
stabilizers transporting them to every anchor. For the Fano frame the 168
automorphisms on its seven points and the pair swap give anchor orbits
`{0,1}` and `{2,...,8}`. All transported counts agree with the full primary census.

### 4. Attainment and controls

For each representative set `t_i=-2r_i0`, except on the live root `e_0-e_2`,
where set `t_i=-2r_i2`. The resulting nine active terms have costs

```text
(1,8,8,9,9,9,9,9,9), total 71.
```

Both implementations check every one of the 12,544 identity entries on each
representative. The separate checker prices actual pairing submatrices, without
using the full-column-span shortcut. Coordinate transport supplies the witness
for all other frames.

Controls reject a changed coefficient, deleted active term, corrupted label,
and nonorthogonal puncture. At Fano anchor 0, the plane `span(1,508)` gives the
false relaxed bound 11 when mutual compatibility is omitted; enforcing it
returns ten. A generic nonreal kernel shift is a positive cost-81 control.
Six package tests reject changed or missing predecessor bytes, wrong cost,
omitted anchor, and missing or malformed receipts. Optimized execution retains
all checks; no correctness condition relies on Python assertions.

## Scope, sources and credit

This closes PR1304's other-frame question for the **fixed A8 simplex and exactly
one orthogonal frame removed**. No real or complex coefficient sampling is used
for the quantified claim. The finite lemmas and the written argument together
constitute the scoped proof; it has not been formalized in Lean or independently
reviewed by a human.

It does not cover other normal frames, more terms, non-frame punctures, masked
identities, two unrestricted factors or shared-copy billing. No physical word,
full moment invoice, native admission or new kappa is claimed. The selected cold
replay is not run: selected and frozen inputs are untouched. All inherited
compiler, common-label, mutable-source, hosting, precision/tape, analytic and
bit H1-H5 obligations remain outside this result.

Base main: `ebedc0895eb4c06725af020bc1af165722b0a3ce`. The task selector's nonce
is `7b0bdc126cee1998eec8c3dc04fd305c`, card `complex-masked-decoder`, priority
revision 2. [TASK.json](TASK.json) records the refined scope, overlap coverage,
bounded cost gate and open questions. [SOURCES.json](SOURCES.json) pins provenance.
Main subsequently advanced to `81e81af67714bdc8d1693b0bf5c29468b92f62ff` and
priority revision 3, retiring that assignment card while retaining the same
selected record. This completed result is submitted as independent verification;
it does not claim a new mechanism or supersede the revised research priorities.

- commdata2338, PR1304, head `a052f0da36a3845c2ec785fd44e5b9e50de3b688`:
  the matching-frame theorem, explicit successor question, and subspace-product
  implementation. `vendor/pr1304_verify.py` is copied **byte for byte** from
  `research/a8-p112-decoder-screen/verify.py` (Git blob
  `188d3a8fda62067dd6f7c37e79a65a3e0cbe2fa7`, SHA256
  `c8dff5ebf75511bf7c5e962a42189977ef5b20ce02e6f9734e4648e695ca3148`).
  The primary verifies this pin before importing it.
- Philipp / mightyOil, PR1248, head `f226f4329a996b0a1bea8794179a91b5d0ed80bf`:
  deficiency-space method and the P120 simplex floor.
- joaqcoo, PR1224, head `00e6ed0810b8ebc7f6133e2c036d0f1c9a3a4162`:
  A8 normal frame and one-sided nine-term normal form.
- DreamingOfClouds, PR717/595/446: decoder and label-cost model; themilkman216,
  PR968, and woklerx, PR1077/1180: surrounding decoder bounds; classical E8/A8
  and Fano-plane geometry. The general real-flat classification premise of
  PR968 is not needed for this fixed-family proof.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance in research,
proof, both new implementations, verification and writing. The second
implementation is by the same assistant, not an independent agent or human.
New and vendored work is Apache-2.0; retain this attribution and the root license.

## Open next questions

1. Can another specified nine-normal family from PR1224 beat cost 64 on P112?
   This changes the fixed simplex hypothesis now excluded for every frame.
   First derive that family's exact kernel ratios and column spans on one
   named puncture. The common-shift compatibility reduction used here need not
   hold, and any favorable copy bill would still need physical realization.
2. Can this orbit census and deficiency argument be formalized as a small
   exact certificate theorem? That would reduce the proof's remaining reliance
   on handwritten coverage arguments. First formalize plane enumeration and the
   implication from compatibility to the deficiency bound. The current checks
   are Python evidence and require a trusted mathematical bridge to the theorem.
