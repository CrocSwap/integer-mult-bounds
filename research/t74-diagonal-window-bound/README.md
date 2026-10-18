# A chronological packing bound for every uniform initial shift of the source-partner T74 schedule

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

**Scoped proof and exact finite certificate; no new κ.** For PR2530's fixed
422-helper words and the uniform initial-shift order family containing PR2571,
every legal whole-helper fill has complex primitive endpoint

\[
 b < \boxed{0.001714127696}.
\]

The source's window-free estimate is about 0.00171422836. The new bound comes
from an unavoidable shortage of width-eight roles in a named collection of
windows. It applies to **every nonnegative integer uniform shift**, including
the original order (`s=0`) and PR2571's shifted order (`s=4`). It does not claim
an attainable optimum, a better supplier, or a bound on other local words.

The exact rational certificate is [CERTIFICATE.json](CERTIFICATE.json).
The code uses the standard library, exact rational arithmetic, explicit
logarithm/exponential remainder bounds, and no LP solver or predecessor checker.
Evidence is author-checked, with no independent human review claimed.

## Statement and fixed inputs

There are 74 replicas, 666 calls, 112 ports per idle-child group, ambient width
73 and 66,304 live families. The per-call helper inventory is
`{4:33, 5:9, 7:62, 8:78, 9:240}`, and the local paid profile in **both** providers
is `{1:2369, 2:632, 3:320, 4:118, 5:26, 7:8}`. There are respectively
49,728, 33,152, 33,152 and 33,152 bins of capacities 8, 16, 32 and 48.
The resulting rank mass is 4,816,512 and deficit 23,680, independently recounted
from these quantities.

For integer `s >= 0`, sort calls `(stage, replica)` by

```
(4*stage + replica + s*[stage >= 1], stage, replica).
```

A helper occurrence must be placed whole into one bin inside its strict
source-event window. The bin's unused capacity contributes its remaining rank
to the global profile. These are necessary conditions of the physical
contract. The proof drops family, port-assignment and other admission
restrictions, so it applies to every fill satisfying the stronger contract.
Adding nonnegative charges cannot weaken this obstruction.

Source pins and provenance are in [INPUTS.json](INPUTS.json):

- PR2530, zxv, `b4012098048e12500b2d33d2e84be281915a27ac`: provider inventories,
  paid profiles and original call order.
- PR2571, Rohan Arun, `faff03cf5c29dadd6e0eb51e406efdc921bfa683`: shifted call
  order and comparison endpoint. Its actual README/build/order files use
  `s=4`; this package binds the bytes, rather than the older PR description.
- The immutable PR2435 source archive (`324d7d3590dc21003940a44cb0cbdc32b3620f25`) retained by PR2530, from Jeremy Kothe's
  supplier: its `inputs/GLOBAL-TEMPLATE.json.gz` supplies the 30-event recipe,
  idle-child capacities and 112 ports. Its historical replica count and bank
  stock are not substituted for the declared 74-replica, 66,304-live model.
  Both container and extracted-member hashes are recorded. The raw member is
  retained verbatim so no network access or historical archive unpacking is
  needed during verification.

The new work starts at main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
The selected record is unchanged. The claim is in [discussion #2608](https://github.com/CrocSwap/integer-mult-bounds/discussions/2608).

## 1. A cut forces 114 non-width-eight bins

Take this fixed set of 102 rank-eight groups:

| Idle children | Owner replicas, inclusive | Groups |
| --- | --- | ---: |
| 1, 3 | 0 through 24 | 50 |
| 5, 7 | 0 through 16 | 34 |
| 9, 11 | 0 through 8 | 18 |

For children 1/3, a legal call is strictly after that replica's stage-1
bridge and no later than its stage-2 call. For 5/7 replace stages 1/2 by 3/4;
for 9/11 use 5/6. The event interpreter reconstructs these strict windows and
a separate stage-position calculation checks all 444 rank-eight windows.

The union of the 102 groups' eligible calls is the interval strictly after
call `(1,0)` through call `(6,8)`, inclusive. For each pair of children,
consecutive owner windows overlap: their opening keys increase by one while
the closing key is four larger. The three resulting intervals also overlap.
Their last closing keys all equal `32+s`, with stage 6 ordered last.

Inside this union the counts from stages 1 through 8 are

```
28 + 25 + 21 + 17 + 13 + 9 + 4 + 0 = 117.
```

The stage-zero calls have replica indices from `s+5` through `s+32`,
intersected with `0..73`. Thus the number of eligible calls is exactly

\[
 U_s=117+\max(0,\min(28,69-s))\le145.
\]

Each eligible call supplies only 78 width-eight roles. Each of the 102 groups
has 112 distinct bins, and a rank-eight bin can contain at most one
width-eight role. Therefore at least

\[
 102\cdot112-145\cdot78 = \boxed{114}
\]

of these bins must contain **no width-eight role**. The exact bound at shift
`s` is `11424 - 78*U_s`; it is 114 for `0 <= s <= 41` and only grows later.
For `s=0` the interval is call indices `[6,150]`; for `s=4` it is `[10,154]`.

The checker enumerates shifts 0 through 70. For `s >= 70`, every stage-zero
key is smaller than every later-stage key, and later stages all receive the
same shift. The entire call order is consequently constant. This proves the
infinite tail; the large-shift replay is an additional control.

This is **not a claim of 114 empty bins**. A bin without a width-eight role
may, for example, contain two width-four roles. Its cost is charged through
the full width-inventory dual below.

## 2. Convert the cut into a complete moment lower bound

Let `h_a(r)=(r/73)^(1-a)` for positive `r`, and `h_a(0)=0`. Enumerate every
whole-helper pattern `p=(R,n4,n5,n7,n8,n9)` with total width at most `R`.
There are exactly 1,163 patterns. Let `rem(p)` be the remaining capacity.
Find bin prices `y_R`, width prices `z_w`, and a positive `delta` such that

\[
 y_R+\sum_w n_wz_w+
 \delta\,\mathbf1_{R=8,\ n_8=0}\le h_a(\operatorname{rem}(p))
\]

for **all** 1,163 patterns. Sum over all physical bins. All helper roles are
used exactly once, and the cut supplies at least 114 indicator terms. Hence

\[
 66304\,\mu(a)\ \ge\
 666\sum_r P_rh_a(r)+\sum_R N_Ry_R+
 666\sum_w I_wz_w+114\delta.
\]

This includes the complete fixed local profile and every residual bin.
It does not infer a moment gain from scalar operation counts.

A convenient dual nomination has `t=(h_a(3)-h_a(48))/5` and
`Y=h_a(5)-3t`, with

```
(y8,y16,y32,y48) = (Y/4,Y/2,Y,h_a(48))
(z4,z5,z7,z8,z9) = (h_a(1)-h_a(5),-h_a(5),(t-h_a(5))/2,-Y/4,t).
```

The checker derives this both by exact elimination and by these formulas.
It then uses rational **lower** enclosures for the costs, repairs each bin
price downwards if needed, and checks every inequality. `delta` is the
smallest remaining slack of a rank-eight pattern without width eight; no
floating-point optimizer is trusted. Exact prices and repairs are saved in
the certificate.

At `a=0.001714127696`, the following displayed decimals are only summaries
of the exact rational comparisons:

| Certified quantity | Value, approximately |
| --- | ---: |
| Per-defect penalty `delta` | 0.000167626935270 |
| Window-free dual lower bill | 66303.9808907017 |
| Chronological lower bill | 66304.0000001723 |
| Strict excess above 66304 | 0.000000172320646 |

Thus `mu(a)>1`. Every positive-rank cost is increasing in `a`, so no fill in
the stated family can have endpoint `b >= a`.

The strengthening is genuine even against the window-free **fractional**
pattern LP. A separate exact feasible primal, on the nine patterns used in
the dual nomination, has counts

```
49728, 33152, 555, 1110, 3515, 5994, 21978, 132793/5, 32967/5.
```

The checker verifies all bin and width equations. Using **upper** cost
enclosures, its total bill is below 66304 at the excluded threshold. This
primal is an LP witness, not a physical fill. It violates the chronological
cut because every rank-eight bin uses a width-eight role.

The pinned PR2571 complex endpoint is
`428508074646920477229/250000000000000000000000`. It is below the new cap by
less than `9.54e-8`, and the checker confirms that this bound does not reject
that endpoint. Its construction and native admission are not reverified here.

## Reproduction and controls

From the repository root, with Python 3.12 and no third-party dependencies:

```sh
python3 -B scripts/research_package.py --package research/t74-diagonal-window-bound
python3 -I -O -B research/t74-diagonal-window-bound/verify.py
```

Expected output includes:

```
PASS_T74_DIAGONAL_WINDOW_BOUND shifts=71+stable_tail groups=102 deficit>=114 patterns=1163 b<0.001714127696 controls=10 no_new_kappa
```

The default replay is read-only and compares every field of the regenerated
certificate, including JSON types. `--write-certificate` explicitly regenerates
it. Input pins check the retained bytes; direct Git-source inputs also carry
Git blob identities.

Positive checks include the two window derivations, the closed-form union
count, the exact primal/dual equations, square-root/linear/constant identities
for the transcendental bounds, and non-rejection of the predecessor endpoint.
Ten failure controls reject changed source bytes, reversed replica stages,
an inclusive bridge endpoint, an omitted source bridge, a duplicate cut group,
a claimed defect of 115, unbound width-eight supply 79, an inflated bin dual,
an inflated defect penalty, and an unbalanced fractional primal. The checks
remain enabled under `python -O`.

## Limits

This is a lower bound for fixed whole-helper widths, the named source recipe,
fixed live stock and this order family. It neither constructs nor optimizes
a physical fill. Arbitrary nonuniform shifts, other interleavings, split
helper reservations, different stocks and changed local profiles are outside
its numerical theorem. In particular, PR2588 changes the local profile: its
claimed endpoint is not contradicted by this bound. The reusable 114-bin cut
can be repriced for a changed profile only after binding the new inputs.

The provider profiles are pinned declared inputs, not an independent replay
of their scalar/native words. No complete cold supplier replay, physical
hosting admission, all-size/compiler proof, precision/exact-recovery audit,
outer transfer audit, bit-supplier audit, Lean proof, or full multiplication
theorem is claimed.

## Open next questions

- **Escape the cut with a nonuniform stage shift.** It matters because every
  uniform initial delay retains the shortage. Start by giving the named 102
  groups at least 147 eligible calls, or deriving a different inventory-aware
  cut if the groups change. This only removes this necessary obstruction;
  any candidate still needs a fully charged fill and native/global admission.
- **Tighten the fixed-order bound with coupled width constraints.** Width-seven
  shortages alone do not imply a positive reduced cost: a rank-16 bin can use
  two width-eight roles at zero reduced cost. A feasible first step is to
  couple that substitution to the rank-eight cut in one exact dual. The
  blocker is a checked stronger inequality, not another moment root search.

Structured versions of these questions are in [TASK.json](TASK.json).

## Credit

Rohan Arun's PR2571 supplies the shifted-order question; zxv's PR2530 supplies
the source-partner words, diagonal order, interval search and owner pipeline.
Jeremy Kothe's PR2435 and T74 supplier lineage supply the retained source
recipe. The window-free pattern-dual method is due to Ali Romman (PR1129),
Jeremy Diviney (PR2360), and Sagar Thakrar (PR2387/PR2442). This contribution
adds the named chronological cut, its uniform-shift formula, the strengthened
exact dual and a separately written standard-library checker.

Jeremy Kothe/PR2575 and PR2588, Philippe Van Velzen/PR2559, Tekalign/PR2436,
Vlado Vojdanovski/PR2322, Cinna Davis/PR2226, and the retained supplier authors
are credited for the neighboring constructions and mechanisms. No such
construction is imported as a newly proved result. Retained input bytes keep
their repository Apache-2.0 provenance; the new work is also Apache-2.0.
