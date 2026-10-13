# X54 on the joint-entrance k8 word: all-replica owner optimum and attaining T37 map

This note follows Ali Romman's #1129 `PROOF.md` (kept as the method reference in
`README-R480-OWNER-OPTIMUM.md` and in that package). Only the local word, the width inventory, the
right-hand side and the attaining flow change. The signed prices are Chafik Boukhalfa's #795 prices, and the
all-replica argument is that of #890/#942/#1129. The result is conditional on the inherited interfaces. It is
not an unconditional multiplication theorem.

## 1. Local word

The base is Thomas DiFiore's joint-entrance word in #1148 (`research/k8-joint-entrances`, content
`1f666402…`). Its paid profile is `{1:2364,2:498,3:412,4:130,5:82,8:8}` and its widths are
`{4:44,5:44,7:38,8:114,9:240}`.

Jeremy Kothe's #1130 X54/E589 slot (holders 335 and 367) is applied with NewBArch's unchanged
`build_tri.py`. The edits and frames are those of #1178's `RECIPE-X54-dem.json`; only the pins change. The
result has content `ac95ff95…` and profile `{1:2364,2:498,3:414,4:126,5:84,8:8}`. The recount is
`{3:+2,4:-4,5:+2}`, as in #1157 and #1178. The slot changes no helper start or end frame, so the widths are
unchanged.

The following checks pass on the result:

- the independent exact `audit_local`, both orientations on all columns;
- NewBArch's controls: the recipe passes and all eight drop/restore/pre-read/donation mutants are rejected;
- PR635's native chain with 2,904 directed phase edges.

## 2. Necessary inequality

Each replica has 672 bins of capacity 8 and 448 bins of each of capacities 16, 32 and 48. The widths per call
total 3,734. The residual mass per replica is

```
M = 8*672 + 96*448 - 9*3734 = 14778.
```

The signed widths `(4,5,7,8,9) -> (-1,-20,-8,-2,4)` and bonuses `(8,16,32,48) -> (2,4,8,-13)` give the actual signed price

```
S = 672*2 + 448*(4+8-13) + 9*(-44 - 20*44 - 8*38 - 2*114 + 4*240) = -3568
```

per replica. With `u(r)` as in #1129 (1,163 patterns, `u(1)=19`, `u(48)=-13`) and `v(r)=48u(r)+13r`, `v(1)=925`:

```
sum_(0<r<48) v(r) n_r >= (48*S + 13*M) T = 20850 T.
```

The supporting moment inequality (#1129 §3) then gives

```
sum phi_b(r) n_r / T >= (834/37) phi_b(1) + (11374/37) phi_b(48)
```

over the whole certified root interval. Equality needs `37 | T`. #1148's `ALL-T-BOUND.json` states the same
normalized idle for its inventory, and the X54 slot does not change that inventory.

## 3. Attaining flow

`PATTERN-FLOW.json` keeps #1129's T37 call order, its 333 source-event groups (each with two equivalent child
sides and 224 ports) and its 20 tight patterns. Only the integer entries are new.

For each group, the counts of the patterns used sum to 224. For each pattern with multiplicity `N` and each width `w`, the time flow
totals `N*n_w`, and at each time the flow is at most `N`. Every call receives exactly `{4:44,5:44,7:38,8:114,9:240}`.

The aggregate is in `CERTIFICATE.json`: 15 tight patterns, 834 bins with residual 1, 11,374 empty 48-bins and every
other bin full. `construct.py`, unchanged from #1129, expands the flow by repeated bipartite matching into
159,840 literal roles. It checks every window, family, slice and per-call helper coverage.

## 4. Complete admission

The complete profile is

```
{1:788046, 2:165834, 3:137862, 4:41958, 5:27972, 8:2664, 48:11374},
```

with live stock 33,152 and deficit 11,840. Both exact engines certify

```
0.001678420962050942454559 < b < 0.001678420962050942454560.
```

The unchanged PR589 bit endpoint is `1733427039589844234749/10^24`. All 47 outer inequalities hold, and both ends of the
interval give

```
kappa = 335121717095377/(2*10^17) = 0.001675608585476885.
```

The next grid value is rejected. The strict replay uses #1129's admission code without change:

- bind and lift to the #942 bank envelope;
- emit;
- controller audit with 15 mutations;
- finite invoice: prefix 775 < 1024, row 17,495 < 20,161;
- assembly;
- 69 admission and 12 bit controls;
- the independent owner audit, including 2,016 disjoint pending-axis relations.

This is the grid maximum for this word, inventory, bin family and outer recipe. Different words, mixed providers,
split helpers or other recursion geometries lie outside this scope.

## 5. How the flow was found (discovery only)

An aggregate integer program over the 20 tight patterns is feasible. A chronology MILP restricted to #1129's nine-pattern basis is
infeasible for this inventory: there are 12 more width-five helpers per call. The full 20-pattern chronology LP is
feasible with zero shortfall (HiGHS IPM, 333,061 variables). A HiGHS MILP over the LP support (695 group-pattern
pairs) then gave an integer solution in 125 s. Verification runs no solver.
