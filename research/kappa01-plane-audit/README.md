# Audit and repair of the paired-plane κ = 0.1 screen

**The proposed passing three-copy row fails when the inherited private-copy
charge is restored.** With all the same generous public-work assumptions, its
moment at `a = 1/9` changes from `0.995605075916` to **`1.091829820390`** when
the centre is retained. The centre-free version changes from
`0.984346481996` to **`1.080571226470`**. This repairs the accounting screen;
it does not repair the multiplication construction to κ = 0.1.

This is a local, source-pinned audit at main
`997e6a9ca7b4f95d50e366f61412fd640d72a88a`. The predecessor itself explicitly
claims a hypothetical screen, not an established supplier or new κ. The
finding identifies an additional missing structural premise in that screen.
It is not a universal obstruction to other multiplication algorithms.

Under the retained strict transfer `κ < a/(1+a)`, attaining `κ = 1/10`
requires **`a > 1/9`**. Failure already at `a = 1/9` therefore suffices to
reject the proposed profile. A passing row at that boundary is only a
necessary local screen; its strict margin, complete construction and the
bit side would still need checking.

## 1. What the existing exact algebra establishes

The [block fitting theorem](../paired-plane-block-rank/README.md) fixes the
same 56 two-dimensional binary planes and the same forbidden matrix blocks.
Its parameter `d` is the dimension of the arbitrary field-vector payload at
each port. The minimum scalar query rank is `49d`. The theorem explicitly
distinguishes this quantity from native child rank, physical copy cost and
the dimensions of the binary planes.

The credited rank-49 attainer partitions the 112 ports into 49 supports,
of sizes `{1:2, 2:31, 3:16}`. Within a support all complete binary planes are
pairwise orthogonal and nondegenerate. The full plane-span Gram matrix is
`I_(2s)` for support size `s`, so its inherited one-total copy charge is `2s`.
The resulting occurrence profile is

```
{2:2, 4:31, 6:16},       total private rank mass = 224.
```

The verifier reconstructs this from the pinned native labels, matching and
supports; it does not accept an asserted copy histogram. This prices this
particular disjoint-support implementation. It is not a lower bound of 224
for every jointly mixed fractional or nonlinear decoder.

## 2. The missing total-mass charge

Write `m=73`, `W=896`, `N=9`, and `w=W/N=896/9`. In the retained coverage
model, with `u` unpaid geometric coordinates per live family and `C` extra
private rank mass per invocation,

```
total paid mass per invocation = (m-u)w + C,
idle mass = total paid mass - explicitly listed local mass.
```

The original [plane-native invoice](../paired-plane-native-payload/README.md)
already records the relevant distinction: its two-unpaid version has total
mass `(m-2)W + 224N`, not `(m-2)W`. The
[earlier plane screen](../paired-plane-port-matching-seed6c563a/PROOF.md)
also places its proposed copy charge in both the local histogram and the
total paid-mass coverage law. These are two descriptions of the same work,
not two payments. The local histogram tells the moment which ranks carry
that mass; the total charge prevents private work from replacing unrelated
public work in the idle remainder.

In `block_anchor_case` of the [κ = 0.1 screen](../kappa010-complex-lever-floor/verify.py),
the new `{2:2d,4:31d,6:16d}` profile is included in local mass, but the
coverage-law charge remains only zero or the old 64. Therefore insertion of
each 224-unit private decoder incorrectly *removes* 224 units of idle public
work. A realization could justify that removal only by giving an explicit
replacement of those public operations, with endpoints and their new
coverage law checked. Neither the block-rank theorem nor the native
private-copy receipt supplies such a replacement.

The accounting repair sets `C=224d+C_old` while keeping the private profile
in local mass. Inserting private work then leaves public idle mass invariant.
For a direct comparison, continue granting the unsupported `u=2d` law,
seven anchor substitutions, all their scalar work outside the child moment,
and fractional rank-51 packing of all 3,982 remaining public local units:

| d | Granted u | Original, centre free | Repaired, centre free | Original, centre 64 | Repaired, centre 64 |
|---:|---:|---:|---:|---:|---:|
| 1 | 2 | 1.021884022053 | 1.053958936878 | 1.033142615974 | 1.065217530798 |
| 2 | 4 | 1.003115252025 | 1.067265081674 | 1.014373845945 | 1.078523675594 |
| 3 | 6 | 0.984346481996 | 1.080571226470 | 0.995605075916 | 1.091829820390 |
| 4 | 8 | 0.965577711968 | 1.093877371265 | 0.976836305888 | 1.105135965186 |
| 5 | 10 | 0.946808941939 | 1.107183516061 | 0.958067535859 | 1.118442109981 |
| 6 | 12 | 0.928040171910 | 1.120489660857 | 0.939298765830 | 1.131748254777 |
| 7 | 14 | 0.909271401882 | 1.133795805653 | 0.920529995802 | 1.145054399573 |

Each number is displayed from an outward-rational interval stored in
`RESULT.json`, using the source-pinned exact engine. All repaired lower
endpoints exceed one.

There is a simpler packing-independent obstruction. Even retaining the
unjustified `u=2d` benefit, the centre-free total moment at zero saving is
exactly

```
[(73-2d)W + 224d N] / (73W) = 1 + d/292 > 1.
```

For any positive saving and any positive child rank below `m`,
`(r/m)^(1-a) >= r/m`. Thus this *repaired fixed-invoice construction*
cannot support any positive saving, even if its public consumer were much
better than the proposed rank-51 relaxation. Retaining the centre adds the
further positive term `64N/(73W)`.

## 3. Payload replication and geometric enlargement are different repairs

There are three different meanings a proposed tensor operation might have:

1. **Vector payloads in the fitting theorem.** The planes stay two-dimensional.
   The theorem gives no implication `u=2d` and no native cost conversion from
   its rank `49d`. An array already carries many field-coordinate payloads;
   its payload dimension is not its unpaid geometric dimension.
2. **Literal independent copies of the same arrays.** Replicate every public
   and private operation, count `W'=dW`, keep `u=2`, and charge `C'=224d`.
   The normalized moment is unchanged because both numerator and denominator
   scale by `d`. The verifier checks exact interval equality for `d=1,2,3,7`.
   Replicating entire invocations instead also changes `N` and leaves the
   per-invocation normalized contract unchanged.
3. **True larger geometric subspaces.** Replace each `E_i` by a nondegenerate
   subspace of dimension `2d`. This needs a new native chart, ambient dimension,
   entry and exit words, public coverage and private-copy invoice. It cannot
   retain the current nine-dimensional chart and the same support attainer:
   a size-three support requires three pairwise orthogonal nondegenerate
   `2d`-spaces, so the ambient dimension is at least `6d`. Already `d=2`
   requires twelve dimensions. A full direct-sum lift of the original
   nine-dimensional geometry has ambient dimension `9d` and also changes
   its native ranks and template parameters.

This audit implements the first two consistent accounting interpretations.
The third is a separate construction problem, not a repaired use of the
old numerical row.

## 4. A second necessary gate for the unchanged native data legs

The [native implementation](../paired-plane-native-payload/README.md) uses,
for each of 112 ports, a source transition `E -> FULL` of rank seven and a
target transition `0 -> E^perp` of rank seven. Thus it retains 224 separate
rank-seven public child occurrences before pricing its private copies.

Assume those public legs remain separate and grant `u=2`, zero decoder and
centre cost, and arbitrary positive ranks below `m` for all other work.
Charge the other work only its linear rank-mass baseline, which is even
more favorable than rank-51 packing. The full moment is at least

```
L = 71/73 + (224/w)[(7/73)^(8/9) - 7/73]
  = 1.036807899645622... > 1.
```

The interval checker verifies this bound. Independently, elementary exact
rational arithmetic proves `L>1` because it is equivalent to

```
(73/7)^(1/9) > 71/63,
```

and `(71/63)^9 < 73/7` holds exactly. Factoring a rank-seven leg into smaller
children cannot lower this particular lower bound when the factors' ranks
sum to at least seven: for `0<p<1`, `sum x_i^p >= (sum x_i)^p`.

This excludes κ = 0.1 for the retained **separate native-leg interface**, even
if a new decoder were free. It does not exclude a genuinely fused consumer
that changes those mandatory occurrences, different geometry, different
coverage, or another outer reduction. The speculative rank-51 public
repacking in the predecessor already grants such a changed consumer;
the present gate must not be imposed on it as if that assumption were proved.

## Verification, sources and limits

Run from this worktree:

```sh
python3 -I -B research/kappa01-plane-audit/verify.py
```

The script authenticates every source in `SOURCES.json` before importing
the interval engine. It reconstructs the plane support profile, reproduces
the predecessor's three-copy numerical pass, repairs the charge, checks all
seven rows, proves the exact zero-saving obstruction, checks replication
invariance, and establishes the scoped native-leg gate. Five controls reject
an omitted private charge, replacement of the old centre charge, interpreting
payload copies as unpaid dimensions, omitting replicated families, and the
unchanged-nine-dimensional geometric lift. It uses explicit `require`
checks, so Python optimization cannot disable validation.

The default run compares the complete recomputed result with `RESULT.json`.
`--output NEW.json` writes an exclusive new receipt. No historical package,
selected record or source archive is modified. Native algebra, full supplier
placement, scalar/tape/precision bills, the bit side and selected cold replay
are not re-executed by this accounting audit.

Credit remains with the original paired-plane matching and endpoint work by
Cinna Davis; the strict scalar mask by Adam Gall; the native payload audit
by Jeremy Diviney, with ctoth's team and Philippe Van Velzen's preceding
cost observations; thakrarsagar's rank-49 fit; ywz65's block-rank theorem;
and Douglas Colkitt's exact interval engine. The selected supplier and anchor
retain their source attributions. Prepared with substantial OpenAI Codex
assistance. These are executable finite checks and hand arguments, not
formal-kernel or independent human verification. Apache-2.0.

## Open next questions

- Can a joint decoder replace identifiable public transform work, rather than
  add private descents, and furnish the resulting complete coverage identity?
  An answer needs an explicit operation trace and restored dirty endpoint.
- Can a different native consumer fuse the 224 data legs while preserving
  arbitrary independent payloads and the dirty target endpoint? Its complete
  rank histogram must replace the scoped native-leg premise above.
- Can a genuine higher-dimensional endpoint support more unpaid coordinates
  with a favorable private bill after enlarging its chart and recomputing the
  entire template? The old payload tensor theorem alone cannot supply this.

These are repair directions; none is claimed completed here. The bit-side
primitive still needs its own independent repair to reach the target.
