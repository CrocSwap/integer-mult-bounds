# Clean queries in 512 old idle fields

The selected schedule has enough unused old fields to store all 512
selected query rows from the end of a backward call to the start of the
next forward call. The construction uses 512 distinct donors. It adds
no native child, productive field, or physical field. Two complete
physical swaps per row cost 26,624 real scalar primitives in the finite
template. The full address and precision bill remains open.

This result gives access to a clean saved query during an open interval.
It does not invert the source code G, store the query through the next
forward call, or complete a Fourier supplier. The swapback returns the
data to the same state as the original query logger at that cut.

## Source and interval

The source premise is the exact original-complex local map in
[CARRIED-QUERY-ALIAS.md](../../residual-syndrome/physical-algebra/CARRIED-QUERY-ALIAS.md):

\[
 (x,y,h,c)\longmapsto(x-Jy,Gy,h,c),\qquad
 \pi_TG=Q_T=R_T^{-1}R,
\]

with the selected ports

```text
T = [21, 37, 47, 76, 81, 87, 92, 110].
```

The 480 ordinary helpers and all eight local C fields can have arbitrary
inputs. The source result preserves their required endpoints. This
storage construction does not alias an old donor to a local C field.

For each replica and each s in {1,3,5,7}, capture the query after the
complete B_s cover sweep and before the next original event. Erase it
before the complete F_(s+1) cover sweep. These are 64 intervals. The
selected Y field is physically unchanged during each interval. In the
first three intervals it is read by one plus bridge. There is no such
read in the last interval.

This interval differs from the one in
[RELATIVE-REUSE.md](RELATIVE-REUSE.md). That result captures a computed
query before B and carries it through eight native axes. Here capture
is after B. The required relative native map is the identity.

## Physical swap lemma

Let q be one physical selected-Y output after B. It already contains
the clean query, with its exact original complex phase and cover route.
Let a be the arbitrary physical value of an old donor. No relation
between their logical frames is required. Apply the raw array swap

\[
 (Y,C)=(q,a)\longmapsto(a,q).
\]

The letter C in this display denotes the chosen old donor, not a private
local C register. A literal swap is

```text
Y += C
C -= Y
Y += C
C = -C
```

It acts on the complete physical arrays at the same cover class and
native address. Its exact matrix is the unsigned exchange. Intermediate
ADDs do not need a common logical frame: the complete four-operation
block implements that physical exchange for all values.

Suppose that the donor has no original event use before erasure. The
parked old value a in Y must also have no use. If an original operation
reads Y, replace that read by a read of C at the identical physical
cover class and native address. This gives the same q to the original
target. The target operation and its native frame stay unchanged.

Before F, apply the same complete swap again. Then

\[
 (Y,C)=(a,q)\longmapsto(q,a).
\]

The donor is restored exactly, and the selected Y value is the original
post-B query. This holds for arbitrary a, including values correlated
with other inputs. The query stays in the selected-Y physical frame;
it is not normalized to I or to a full Fourier frame.

Any additional use of the stored query must preserve it, or must restore
it before the second swap. This result alone supplies no native access
in a different frame and no source correction.

## Exact old-owner allocation

The [producer](check_clean_idle_storage.py) reads the pinned historical
selected template and the frozen source-alias receipt. It checks all
482 events, 144 local calls, 160 idle events, 144 bridges, and both
terminal events in every replica. Every local call marks all 704
persistent owners, including all 69,120 complete helper occurrences.
An idle event marks all 224 fields of its pair, including fields with
zero residual rank and fields that receive only a phase translation.

For each interval, a candidate donor must satisfy all of these rules:

- It is one of the original 14,336 live fields.
- It has no original event use inside the storage interval.
- It is not one of the 704 owners of either endpoint call.
- It is not any of the 512 selected query-source fields.
- It has not been assigned to any other query row.

The endpoint exclusion is stronger than required by the swap lemma.
It ensures that no chosen donor is a helper, source, or target of the
two endpoint local calls. The global query-source exclusion prevents
one storage interval from placing its old value inside another
interval's query source. All 512 swaps have distinct source-donor
pairs. The old eight private C fields remain available and unchanged.

The [receipt](CLEAN-IDLE-STORAGE.json) gives every interval, chosen
family, literal swap, and changed bridge read. There are between 3,608
and 10,675 eligible old donors per interval before the global distinct
donor choice. A direct choice gives all 512 rows, so no failed-search
or optimality assertion is needed.

Each of the first three intervals per replica has the bridge

\[
 X_{\rm dst}\mathrel{+}=X_{\rm src},\qquad
 Y_{\rm src}\mathrel{-}=Y_{\rm dst}.
\]

The active query pair is dst. For its eight selected ports, the receipt
replaces the Y_dst source read by the assigned donor. There are exactly
384 such read replacements at 48 bridge events. The original target
family and coefficient -1 remain unchanged. The X operation remains
unchanged. All other uses of the parked Y value are absent, including
helper uses by a different replica.

The construction must perform each capture as a complete cover sweep
after B, and each erase as a complete cover sweep before F. A local
invocation-order insertion is not the stated contract. No cover
intertwiner is needed: both swaps and every changed read use g to g
and the identity native address map.

Since the source-donor pairs are globally disjoint, the new sweeps do
not change each other's storage fields. A donor cannot be an original
bridge target while it holds a query, because all original bridge uses
were excluded. Induction over the original events therefore preserves
every original output and every old owner value after each erase.

## Cost and validation

Across all 16 replicas, there are 1,024 physical swaps. Each uses three
complex unit ADDs and one complex sign SCALE. Under the selected scalar
lowering this gives

\[
 1024(3\cdot8+2)=26,624
\]

real scalar primitives, before cover and row multiplicities. There are
3,072 complex ADDs and 1,024 complex sign SCALEs. The construction adds
64 capture sweeps and 64 erase sweeps. It retains live stock 14,336 and
physical stock 14,826. The query logger, address sweeps, family-index
changes, and any later query use need their own complete invoice.

The producer passed under `-I -O -B`. It checks the complete swap matrix
and the three-variable swap/read/swap matrix on formal q, a, and target
inputs. Omitting the sign gives a wrong swap. Keeping the old bridge
read gives target-a instead of target-q. Independent schedule review
has been requested; it is not yet claimed here.

```sh
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/source-domain/carried-owner-reuse/check_clean_idle_storage.py --archive worktrees/k5-persistent-cleanup/research/community-frontier1094-audit/selected-replay.tar.gz --alias work/centre-encoding-campaign-20261014/lanes/residual-syndrome/physical-algebra/CARRIED-QUERY-ALIAS.json --out work/centre-encoding-campaign-20261014/lanes/source-domain/carried-owner-reuse/CLEAN-IDLE-STORAGE.json
```

Expected status: `PASS_ALL512_CLEAN_QUERY_IDLE_SWAPS`.

The selected archive SHA256 is
`f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6`.
The compressed GLOBAL-TEMPLATE member SHA256 is
`2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760`.
The source-alias receipt SHA256 is
`42fb664f2273bacdc04603c548961de4a75ec04d752974794f0f0b311ca18bd2`.
The source-alias payload SHA256 is
`677199e44967cb598bdd6b92f23400cf88ac40020e195f07a0c6e5244a3ace0d`
after decompression.

This result uses the selected historical owner schedule and the exact
source-alias theorem. It builds on the dirty-cache interval analysis,
but uses a separate post-B interval and a separate physical swap proof.
AI assistance was used to develop and check this research artifact.
