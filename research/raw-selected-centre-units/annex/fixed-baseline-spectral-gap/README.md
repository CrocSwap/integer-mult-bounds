# A spectral gap for fixed selected baselines

For the fixed A,T source interface below, every admissible selected set
has at least 27 ports. Sizes 28, 29, 30, and 31 are also impossible.
Thus its size must be 27 or at least 32. Existence at size 27 remains
open; its determinant must equal `2^42` in the normalization below.
This is a scoped lower bound. It is not a minimum over arbitrary
selected sets, a native cost bound, or a complete kappa improvement.

Read the exact [source proof](frozen/work/centre-encoding-campaign-20261014/lanes/schur-selection/SPECTRAL-BOUND.md),
[independent proof review](frozen/work/centre-encoding-campaign-20261014/lanes/temporal-reuse/SPECTRAL-BOUND-REVIEW.md),
[selected-baseline necessity lemma](frozen/work/centre-encoding-campaign-20261014/lanes/cover-algebra/SELECTED-BLOCK-NECESSITY.md),
and [fresh validation](VALIDATION.md). The [source manifest](SOURCE-MANIFEST.json)
binds all replay inputs. The [annex manifest](ANNEX-MANIFEST.json) binds
all annex files except itself.

## Exact allowed class

Use the historical integer matrix R of size 8 by 112, with
`R R^T=56I`, `K=R^T/4`, and `J=I-KR`. The selected set S contains both
of these disjoint sets:

```text
A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]
```

Each fixed minor has Gram matrix `4I`. Selection outside A and T is
unrestricted; complete split-sign pairs are not required.

Let E be a supplied unit that writes a systematic query in A and fixes
all other rows. A source unit F must satisfy `F_S=E_S` and
`(JF)_U=selector_U`, where U is the complement of S. Thus all selected
baseline rows outside A retain their specified values. The necessity
lemma proves that the ordinary block must be a unit. This is equivalent
to the unit condition on `D=I-R_U K_U`.

Write V for the extra selected columns, `v=|S|-16`, and
`M=R_V R_V^T`. Then:

```text
D = -11I + M/4
B = -4D = 44I - M
```

A dyadic-unit D requires `det(B)` to be a nonzero power of two. For
`v<8`, the determinant lemma leaves an uncancelled factor of 11.
This excludes all sizes below 24 in this class. The spectral proof gives:

| Selected size | Strict determinant interval |
| --- | --- |
| 24, 25, 26 | `2^42 < det(B) < 2^43` |
| 28, 29, 30, 31 | `2^41 < det(B) < 2^42` |

At size 27 the only remaining power is `2^42`. This is a necessary
condition, not an existence result. Sizes 32 through 39 also remain
open in this unpaired class. The separate 40-port split-pair bound
has additional pairing restrictions.

The proof uses a graph bound: fifteen distinct roots in dimension eight,
with squared norm four and pair products in `{0,2,-2}`, have at most
93 nonorthogonal pairs. Exact rational logarithm intervals then exclude
the listed powers of two. For size 31, the independent 64-term interval
gives a lower logarithmic margin greater than `1/1250`. No numerical
eigenvalue estimate or determinant search is used.

## Relation to the main package

The S38 construction uses a different allowed class. It does not contain
these fixed A and T, and its two unit tests do not impose this selected
source-baseline contract. The annex does not prove that S38 is optimal.
It also does not adopt the separate dyadic producer's lower-twelve claim
or later separator claims.

The original proof and review remain byte-exact. Their references to
earlier review or publication status record that historical state. The
selected-block normalization note is retained to support the ordered
unit identities. Its scalar invoice and implementation claims are not
part of this annex's fresh replay.

All 256 files in the accepted main package manifest remain unchanged,
as does that manifest. The earlier manifest freezes the original file
set. The annex manifest gives separate coverage for these additions.
The main eight-stage replay and its receipts are unchanged.

## Replay

Use Python 3.10 or later, the standard library, one process at a time,
and at least 3 GiB free disk space. From the repository root, run:

```sh
python3 -I -B research/raw-selected-centre-units/annex/fixed-baseline-spectral-gap/replay.py --out /tmp/fixed-baseline-spectral-gap
```

Use a new output directory outside the annex. The final line is:

```text
PASS_FIXED_BASELINE_SPECTRAL_GAP
```

The wrapper runs the original producer with assertions enabled, then
the independent checker. Add `--optimized` to run the independent
checker with `-O`. The producer still runs without `-O`, even if the
wrapper itself runs with `-O`. Both receipt files must match the
historical bytes exactly.

The independent checker reconstructs all 112 source columns by backward
propagation of eight forms through the 12,550-event prefix. It checks
the fixed minors, all 6,216 root pairs, 2,187 possible residual patterns,
2,248 degree inequalities, and all 16 size intervals from 24 through 39.
It uses a separate 64-term rational logarithm routine and also checks
the producer's saved 32-term margins exactly. It imports no producer
code. The factor-11 and selected-baseline necessity arguments are proof
steps retained in the independent review; the finite checker does not
enumerate all selected sets.

The [portable adaptation](PORTABLE-ADAPTATION.json) replaces only Git
and full-archive reads with the two exact compressed members. The
[diff](PORTABLE-ADAPTATION.patch) records that change. All source
reconstruction and mathematical checks remain unchanged. Each replay
checks the compressed and decoded member hashes. The historical
archive hash in the independent receipt identifies the source archive;
the portable replay does not read that full archive.

The [extraction receipt](provenance/SOURCE-EXTRACTION.json) records a
fresh comparison with the full local archive and the earlier separate
[pinned-source check](provenance/PRIOR-PINNED-SOURCE-CHECK.json). The
source commit is `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`, and the
[source archive](https://github.com/CrocSwap/integer-mult-bounds/blob/bce54fb3f895cbe5cd4c0eb477c3afeed100190f/research/community-frontier1042-audit/selected-replay.tar.gz)
has SHA256 `22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754`.
This historical source is not the selected PR #4470 construction at
publication base `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`.

No million-vector split-pair enumeration, native interface replay,
ownership schedule, routed caller, recursive invoice, current supplier,
or complete kappa calculation ran for this annex. The exact notices and
source credit are retained in [NOTICE.md](NOTICE.md).
