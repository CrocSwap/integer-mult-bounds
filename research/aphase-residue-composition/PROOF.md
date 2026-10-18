# Two vacancy paths on the PR2853 word

The scientific source is Philippe Van Velzen's PR2853, head
`d01045dfb67428679618027dff552f1d032fa999`. Its two dirty-A native words,
provider dispatch, chronological call order, local profiles and physical stock
are retained. The construction changes four owner assignments and five offsets
in its literal T74 allocation. All 271,728 roles are subsequently checked.

A bin is `(owner replica, child, port)`. The two initially partial bins
`(0,0,2)` and `(0,0,3)` each contain one width-9 helper in capacity16, leaving
width7. Move the following actual width-7 roles:

| Actual call time | Helper index | Old bin | New bin |
|---|---:|---|---|
| 0 | 228 | (66,10,90) | (0,0,2) |
| 29 | 327 | (7,4,34) | (66,10,90) |
| 0 | 227 | (62,10,94) | (0,0,3) |
| 30 | 360 | (7,4,34) | (62,10,94) |

The two intermediate capacity48 bins start full. Removing and replacing a
width-7 role leaves them full. The terminal capacity32 bin starts with widths
`[9,9,7,7]`; the final contents are `[9,9]`, leaving width14. The two initial
bins become full. Thus the complete idle-profile change is exactly
`H14 - 2 H7`. There are five affected bins; their strict source windows are:

| Bin | Capacity | Legal call times |
|---|---:|---|
| (0,0,2) | 16 | -1 < t <= 9 |
| (0,0,3) | 16 | -1 < t <= 9 |
| (66,10,90) | 48 | -1 < t <= 606 |
| (62,10,94) | 48 | -1 < t <= 586 |
| (7,4,34) | 32 | -1 < t <= 50 |

These windows are reconstructed from actual source events. The independent
event checker additionally enforces exclusion of the active physical family,
one helper per physical family at a call, complete helper coverage, capacity,
nonoverlap, and compact pending prefixes. Numeric times alone do not prove
those conditions. `data/CANDIDATE.json` pins the complete four payloads;
`generate.py` starts with pinned source bytes and reconstructs the change.

For `0 < a < 1`, write `H_r=(r/73)^(1-a)`. The change in the unnormalized
moment is

```
H14 - 2 H7 = (2^(1-a) - 2) (7/73)^(1-a) < 0.
```

The rank mass is unchanged because `14-2*7=0`. The call count remains666,
live stock66304, total physical stock66794 (including490 private families),
and rank mass4816512. No local operation, centre, bridge or cleanup cost is
removed. The complete paid profile is

```
{1:1616713, 2:424908, 3:183207, 4:85249, 5:26625,
 6:58, 7:1, 8:5328, 14:1, 32:47, 48:26703}.
```

Independent directed rational arithmetic places the complex moment root in
`(0.001719378870495538841812, 0.001719378870495538841813)`.
The proposed modern outer target is the lower endpoint minus `10^-46+10^-70`.
Its comparison uses the full P53 rational, not its rounded decimal headline.
Complete native/global/outer admission is a separate obligation checked by
`reproduce.py`; the finite profile argument alone does not discharge it.

The exact fixed-bin continuous packing cap is in
`(0.001719637819314309441628, 0.001719637819314309441629)`.
The cap verifier enumerates all1163 patterns for capacities8,16,32,48, checks
all1152 strict dual slacks, and solves the primal exactly with actual P53
width inventory `{4:26,5:2,7:62,8:84,9:234}`. Its normalized idle profile is
`{1:234,3:432/5,5:120,48:1808/5}`. This relaxation omits chronology and is an
upper bound, not a realizable allocation. The looser local-word ceiling from
the repository calculator is in `(0.001758353980844,0.001758353980845)`.

The larger T122/T77 flow searches returned UNKNOWN within their recorded
limits; they neither constructed this cap nor proved it unattainable. The
relay is a separate explicit construction on the original T74 source.

This is a finite conditional composition. The inherited all-size/compiler,
common-label/mutable-source, whole-call hosting, precision/tape, analytic and
bit H1-H5 obligations remain. No complete multiplication theorem or new Lean
kernel audit is claimed.
