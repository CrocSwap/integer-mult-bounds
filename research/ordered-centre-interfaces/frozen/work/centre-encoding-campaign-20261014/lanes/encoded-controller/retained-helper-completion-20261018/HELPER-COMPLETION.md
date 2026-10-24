# Retained helper progress for a new data word

The frozen independent-skeleton word contains a complete native path for
each of its 408 helper fields. These paths have no scalar connection to
the 224 data fields. This packet extracts those paths. A new data word
can run after them on the same local live stock.

The helper completion has 2,326 native children and rank mass 3,281. Thus
a data word with rank mass 1,792 gives a complete local mass of 5,073.
This statement does not require the new data paths to follow the old
data paths. It does require the same physical data entrance and exit
types. It is a local composition result. It does not prove a global
owner schedule, a controller, or a kappa gain.

## Source and extraction

The source is
[INDEPENDENT-SKELETON-PROGRAMS.json.gz](../../history-encoding/independent-skeleton-20261018/INDEPENDENT-SKELETON-PROGRAMS.json.gz).
Its decompressed SHA-256 is
`8fe1147e5cb80d9f1d9ef309b0ee6f42b1a64cc5ebabd19b818623c246c9fd64`.
The source proof is
[INDEPENDENT-SKELETON.md](../../history-encoding/independent-skeleton-20261018/INDEPENDENT-SKELETON.md).

For each provider, the extraction retains the following events in their
original order:

- Each child, warp, and endpoint adapter on live roles 224 through 631.
- Every helper residual wrapper, with its original entrance and exit.
- All 91 private-zero allocations and returns.
- All 16 clears of owned C0 and all phase markers.

It removes each event on a data role and each data transfer. No retained
event reads a data role. No retained event couples two helper roles.
The helper event list is byte-equal in both source orientations. Both
use the source's forward signed-K physical convention.

This extraction does not remove a private-zero allocation. It makes no
new claim that those allocations are unnecessary. The eight owned C
roles remain reserved. C0 returns zero; the other seven owned roles are
unchanged.

## Exact helper map

For a helper h, let T_i and T_f be its declared canonical entrance and
exit frames. A child is the exact map T_new T_old^-1. A signed warp is
the exact map T_new K^epsilon T_old^-1. The physical path therefore
telescopes to

```text
T_f W_h T_i^-1,
```

where W_h is the ordered logical warp word on that helper. The checker
reduces every such word by adjacent inverse cancellation. All 408 words
are empty, for both providers. The path is therefore exactly

```text
T_f T_i^-1.
```

Each native event and each wrapper is copied from the pinned source.
Thus this equality retains its exact phase, not only its binary frame.
The checker also pins every native recipe and checks that each recipe
acts on one array. It does not rerun the predecessor's native phase
compiler.

The old residual wrappers are retained on the same helper and at the
same endpoint pair. They give the same coordinate native operator as
in the source contract. In particular, a proper exit is not replaced
by FULL. The output is not physical identity when T_i differs from T_f.
It is the required productive helper map on arbitrary input contents.

The native helper widths, including proper exits, are:

| Productive width | Helpers |
| --- | ---: |
| 4 | 26 |
| 5 | 2 |
| 6 | 18 |
| 7 | 50 |
| 8 | 99 |
| 9 | 213 |

Their rank sum is 3,281. Every helper prefix is unitary. There is no
scalar growth in an arbitrary helper value.

## Composition with paired data paths

Let D be a checked data word on the same 224 data roles. Suppose that:

1. D does not read or write the 408 helper roles.
2. D starts with X_p at C_qp and Y_p at I.
3. D ends with X_p at F9 and Y_p at F9 C_qp^-1.
4. Each private or owned role used by D has a separate checked lifetime.
   It can reuse the helper completion's private stock after that stock
   has returned zero.

Run the helper completion first, then D. The first component is the
identity on the data. The second component is the identity on the
helpers. Their physical operators act on disjoint live factors, so the
complete map is their direct product. This proof holds for arbitrary
data and arbitrary helper contents. It does not use a clean helper
baseline or a cancellation of hidden helper terms.

For example, if D implements the original-frame reciprocal shears

```text
F_D: (x,y) -> (x, y + E x),
B_D: (x,y) -> (x - E^-1 y, y),
```

then this construction gives those exact data maps and all 408 old
productive helper maps. There is no need to move E through an intrinsic
Q_p or through a twiddle. Any later controller must still account for
those operators in their actual order.

This construction changes the data chronology and can change the data
child profile. It does not preserve the old mixed scalar tape. A later
global proof must admit the new complete local word and its recursive
stock. Keeping the helper endpoints makes that question concrete; it
does not settle it.

## Invoice and checks

The exact helper child profile is

```text
{1:1609, 2:512, 3:172, 4:33}.
```

There are 184 warp events, 530 endpoint adapter events, and 390 residual
wrapper events. A conservative map count, with two maps per child, is
5,756. The 16 owned clears cost at most 32 real scalar primitives.
The private-zero peak remains 91. These counts add to the checked data
word's counts; they are not zero-cost completion claims.

The checker verifies all 408 arbitrary helper columns through their
ordered warp words, all frames, all wrapper endpoints, all private
lifetimes, and all 224 untouched data columns. It rejects a missing
warp, a data read, and a missing residual wrapper. It imports no source
producer. Both normal and optimized Python runs must give the same
payload and receipt bytes.

```text
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -I -B work/centre-encoding-campaign-20261014/lanes/encoded-controller/retained-helper-completion-20261018/check_and_emit.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/encoded-controller/retained-helper-completion-20261018/check_and_emit.py
```

Expected final output starts with `PASS_RETAINED_HELPER_COMPLETION`.
`FREEZE.json` pins this proof, the checker, the receipt, and the payload.
