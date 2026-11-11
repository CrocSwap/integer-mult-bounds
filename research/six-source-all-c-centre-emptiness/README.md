# The centre of the six-source diagonal, in every characteristic

**Scoped classification. No new κ.** On the six-source diagonal
`s + t = 6c + 3`, the residue-legal centre pair of the frozen-coordinate
argument is classified for every characteristic `c >= 2`:

- even `c >= 4`: there is no residue-legal centre at all;
- odd `c >= 5`: there are exactly **300** residue-legal centres, all of
  weight 3, in exactly two count shapes (`180 + 120`);
- `c = 3`: 366 residue-legal centres, 300 of weight 3;
- `c = 2`: 450 residue-legal centres, none of weight 3.

The c=6 emptiness of merged PR #6955 is therefore an even-characteristic
phenomenon, not a property of the value six. Every odd characteristic at least
three has weight-3 centres, and at odd `c >= 5` the weight-3 centre always
carries the value `2c` that the frozen-coordinate step needs. The selected
conditional κ stays `63005817/100000000000`.

This package studies the residue-legal centre pair only. It does not search
words, does not rerun the solver verdict of PR #6141, and does not claim a
depth-two exclusion.

## Interface, unchanged

The interface is the one used by merged PR #6955, which follows PR #4231 and
PR #4248. A floor word on `k = 6` sources in characteristic `c` has length
`6c` and calls each source exactly `c` times. `q_t` counts the first `t`
letters, so `q_0 = 0`, `q_{6c} = (c,...,c)`, each step adds one basis vector,
and every count lies in `{0,...,c}`. Boundary `6c` is identified with `0`.

On the diagonal `s + t = 6c + 3` the centre pair is

    (3c+1, 3c+2),   q_{3c+2} = q_{3c+1} + e_j,

so the centre sum is `2r + e_j` with `r = q_{3c+1}` and `r_j <= c-1`.

A pair realizes a **weight-3 mask** when every coordinate of `q_s + q_t` lies
in the residue set

    A_c = {v in 0..2c : v = 0 or 1 (mod c)}

and exactly three coordinates are `1 (mod c)`. The mask bit is the residue 1;
this is the weight identity of PR #6107 as specialized in PR #6955. A sum of
two counts in `{0,...,c}` lies in `{0,...,2c}`, so `A_c` is exactly the range
of residue-legal values.

## Even characteristic

**Lemma 1.** For even `c >= 4` every residue-legal centre count is a multiple
of `c/2`, while the centre length `3c+1` is not.

*Proof.* Take a coordinate `j`. Off the centre the sum is `2r_j`, which is
even; among the elements of `A_c` congruent to 1 modulo `c`, the odd ones are
`1, c+1, ..., 2c+1`, so an even element is congruent to 0 and lies in
`{0, c, 2c}`. Hence `r_j` is `0`, `c/2` or `c`. At the centre the sum is
`2r_j + 1`, which is odd; the odd elements of `A_c` are `1` and `c+1`, so
`r_j` is `0` or `c/2`. Every count is therefore a multiple of `c/2`. But
`r` is a prefix count of length `3c+1`, and `3c+1 = 1 (mod c/2)` with
`c/2 >= 2`. A multiple of `c/2` cannot equal `3c+1`. ∎

So no residue-legal centre exists for any even `c >= 4`, and in particular no
weight-3 centre does. The c=6 case of PR #6955 is the instance `c = 6`.

## Odd characteristic

**Lemma 2.** For odd `c >= 3`, off the centre `r_j` lies in `{0, h, c}` with
`h = (c+1)/2`, and at the centre `r_j` lies in `{0, a}` with `a = (c-1)/2`.

*Proof.* Off the centre `2r_j` is again even. The even elements of `A_c` are
`0`, `c`, `c+1` and `2c`; `2r_j = c` has no integer solution because `c` is
odd, so `2r_j` is `0`, `c+1` or `2c`. At the centre `2r_j + 1` is odd; the odd
elements of `A_c` are `1` and `c`, giving `r_j = 0` or `a`. ∎

Write `m` for the number of non-centre coordinates equal to `c` and `k` for
the number equal to `h`; the remaining `5-m-k` non-centre coordinates are 0,
and the centre count is `xi` in `{0, a}`. The prefix length gives

    m c + k h + xi = 3c + 1.

Substituting `2h = c+1`, `2a+1 = c` and checking every `m, k` in `0..5`:

- `xi = 0` forces `(m,k) = (2,2)`;
- `xi = a` forces `(m,k) = (1,3)`;
- for `c = 3` only, two further solutions appear, `(m,k) = (3,0)` and
  `(0,5)`.

**Counts.** The `(2,2,0)` shape has count vector `{0,0,h,h,c,c}` with the
centre on one of the two zero coordinates: `6!/(2!2!2!) · 2 = 180`
realizations. The `(1,3,a)` shape has `{0,a,h,h,h,c}` with the centre forced
at `a`: `6!/3! = 120` realizations. Both have exactly three coordinates
`1 (mod c)`: in the first shape the centre contributes `1` and the two `h`
coordinates contribute `2h = c+1`; in the second the centre contributes
`2a+1 = c = 0 (mod c)` and the three `h` coordinates contribute. Hence, for
odd `c >= 5`, there are exactly 300 residue-legal centres and all have
weight 3.

At `c = 3` the two extra families are `{0,0,a,c,c,c}` with the centre at `a`
(60 realizations, weight 0) and `{0,h,h,h,h,h}` with the centre at `0`
(6 realizations, weight 6). The census below confirms 366 legal centres, of
which 300 have weight 3. At `c = 2` the step `c/2` is 1, every count is legal,
and the centre is odd at exactly one coordinate, so the 450 legal centres all
have weight 1.

## What this changes

The c=6 centre is empty because 6 is even, and the same holds for every even
characteristic. The frozen-coordinate induction needs a weight-3 centre
carrying `2c`; at odd `c >= 5` the `(2,2,0)` shape supplies two coordinates
equal to `2c` and the `(1,3,a)` shape supplies one, so this residue count is
not an obstruction there. Any claim that the centre route is universally dead
would be wrong. The next step for odd characteristic is the induction itself,
not another centre census.

At even characteristic the centre slot is unavailable, so the induction has to
start elsewhere or change mechanism. That is a statement about this centre
pair only; it is not a depth-two exclusion.

## Census

`verify.py` enumerates every count vector with sum `3c+1` and every centre
letter with `counts[centre] <= c-1`, and tests every coordinate of `2r + e_j`
against `A_c`. Exact totals:

| c | count vectors | centre letters | legal | weight-3 |
|---:|---:|---:|---:|---:|
| 2 | 126 | 450 | 450 | 0 |
| 3 | 546 | 2346 | 366 | 300 |
| 4 | 1686 | 7926 | 0 | 0 |
| 5 | 4221 | 20916 | 300 | 300 |
| 6 | 9156 | 46956 | 0 | 0 |
| 7 | 17892 | 93996 | 300 | 300 |
| 8 | 32292 | 172692 | 0 | 0 |
| 9 | 54747 | 296802 | 300 | 300 |
| 10 | 88242 | 483582 | 0 | 0 |

The c=6 row reproduces the predecessor's `9156 / 46956 / 0` totals. Beyond the
census range the two lemmas and the two linear equations are checked for every
`c = 3, ..., 999` by integer arithmetic, so the classification is a written
proof for all `c`, with the census as corroboration on a small range.

## Reproduce

From the repository root, with CPython 3.12 and the standard library only:

```sh
python3.12 -B -W error research/six-source-all-c-centre-emptiness/verify.py
python3.12 -B -O -W error research/six-source-all-c-centre-emptiness/verify.py
```

The marker is `PASS_ALL_C_CENTRE_CLASSIFICATION`. Nothing here reads a live
service or a frozen archive; the two hash-pinned provenance files are listed in
[SOURCES.json](SOURCES.json).

## Open next questions

1. At odd `c >= 5`, does the `(2,2,0)` or the `(1,3,a)` centre actually extend
   to the frozen-coordinate induction from `s = 3c+1` down to `s = 4`? The
   residue count supplies the `2c` coordinate but not the intermediate
   weight-3 indices.
2. Which off-centre indices `s != 3c+1` carry residue-legal weight-3 masks at
   even `c`? The c=6 examples in PR #6955 sit off the centre, and a complete
   index classification is the natural replacement for the dead centre slot.
3. Do the c=3 families of weight 0 and weight 6 interact with any mask
   identity, or are they excluded by a different hypothesis?

## Credit

Merged PR #6955 by unpaidmoon supplies the six-source model, the residue set,
the c=6 centre classification and the description of the c=7 frozen-14 step;
this package generalizes its c=6 statement and does not replay it. The weight
identity is PR #6107. The interface is PR #4231 / PR #4248. The solver verdict
for the characteristic-six depth-two exclusion is PR #6141 and is cited, not
rerun. The c=7 off-diagonal question is left open by discussion comment
19493159 and fork PR #156. No characteristic polynomial, no word search and no
supplier admission is claimed.
