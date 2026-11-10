# The six-bit fit window of the selected BIT stage closes at log2 e = 500(H1+1)/249

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: scoped written proof with exact finite checks. No new kappa, supplier
admission or frontier change.** It answers open question 3 of
[PR #4954](https://github.com/CrocSwap/integer-mult-bounds/pull/4954) ("Close the
six-bit window"), which is also the first open question of the open PR #7101.

## Result

At the one ordinary-BIT stage that #4954 analyses (rank `N = 2^H1`, `H1 = 25986965159937`,
atom exponent `1/250`), the source prescription borrows

```text
k = D*(N^2*(w-1) + ceil(log_q(B*|GL_N(F_q)|))) + k_old,   w = ceil(e^(1/250)),
D = floor(log_N ceil(e/w)),   and it fits exactly when  k < e/2.
```

#4954 proved that it does not fit for `log2 e <= 52182660963729` and that its stricter
guard `k_par < e/4` holds from `log2 e = 52182660963735`, leaving a six-bit window. With
`S_old = 1` from [PR #4970](https://github.com/CrocSwap/integer-mult-bounds/pull/4970)
the window closes.

At depth two the criterion is exact: the prescription fits iff
`e > 4*N^2*w + 4*delta_B + 2*k_old`, where `delta_B` is the chart excess in `[0, c_B]`.
With `t* = 500*(H1+1)/249 = 52182660963730.9236947791...`:

| statement | range of `log2 e` | hypotheses |
|---|---|---|
| does not fit (depth at least one) | `<= t*` | none beyond `B >= 1`, `q >= 3` |
| fits | `>= t* + 2^(-2*10^11)` | `c_B <= N^2` and `k_old <= N^2` |

So the least width from which every larger width fits has `log2` in
`(t*, t* + 2*2^(-2*10^11)]`, whatever `B` and `S_old` are within those bounds.

At the integer widths `e = 2^t`, which are the ones #4954 tabulated:

| `t` | 52182660963729 | ...730 | ...731 | ...732 | ...734 | ...735 |
|---|---|---|---|---|---|---|
| `k < e/2` (this package) | no | no | **fits** | fits | fits | fits |
| `k_par < e/4` guard | no | no | no | **holds** | holds | holds |
| #4954 (proved) | no | open | open | open | open | fits |

The fit entries assume `c_B <= N^2` and `k_old <= N^2`; the `no` entries assume nothing
beyond `B >= 1` and `q >= 3`. The guard of #4954 therefore moves from `52182660963735` to `52182660963732`, which
answers the question of #7101 for the `e/4` form, and with `S_old = 1` the guard is not
needed at all: the stated reserve fits from `52182660963731`. Below the threshold the
conversion has to call the retained supplier directly, as #4954 already said; only the
location of the threshold is new.

## Evidence

`PROOF.md` proves the criterion, the translation from `log2 e` to integer comparisons
(Lemma 4) and the theorem. `verify.py` (standard library, about two seconds) authenticates the
pinned sources, checks 170 envelope cases and 336,636 depth-two instances of the
source formula against the criterion, scans the exact-integer translation chain on twelve
`(N, A)` pairs, computes the exact least fitting width with big integers at six ranks
between `2^40` and `2^101` (it lies `4N^2` to `18N^2` above the infeasible edge, a relative
offset of order `1/w`), evaluates exact exponent arithmetic at the selected rank, and runs ten
rejection controls. It matches the stored `RESULT.json`, which `verify.py --write`
regenerates.

## Reproduce

From the repository root, with CPython 3.12:

```sh
python3.12 -I -W error -B research/bit-stock-band-threshold/verify.py
python3.12 -I -O -W error -B research/bit-stock-band-threshold/verify.py
python3.12 -B scripts/research_package.py --package research/bit-stock-band-threshold
```

Each verifier run prints `PASS_BIT_STOCK_BAND_THRESHOLD`. No Lean, Docker or selected
cold replay is run.

## Limitations

* The result is for the **source prescription** with the exact depth
  `D = floor(log_N ceil(e/w))`. The parameters file allows a larger explicit depth bound;
  the infeasible side holds for it and the fit side as stated does not.
* `c_B <= N^2` (#4954; derived for this stage in the open #7101) and `k_old <= N^2`
  (#4970, `k_old = 1` or at most 103) are cited hypotheses, not replayed.
* A window of width at most `2*2^(-2*10^11)` in `log2 e` remains around `t*`. Its exact
  resolution depends on the realised `B` and on the ceiling in `w`.
* The sources pinned here are the #4470 stage of #4954. #7101 states that the same rank
  is retained by the later `frontier6030` stage. That statement is not checked here.
* The decision is arithmetic in the exponent of `2`. No rank-`2^25986965159937` word is
  built, and the work claims no multiplication bound.

## Open next questions

The structured list is in [TASK.json](TASK.json).

1. **Compiled depth bound.** Which depth bound does the compiled prescription use, and
   where does the fit start if it exceeds `floor(log_N ceil(e/w))`? First step: read it
   in the compiled stock formula; the first edge moves to `250*(2*H1 + log2(2*D'))/249`.
   Blocked by: that bound is not pinned in the sources used here.
2. **Last window.** Can the window of width `2*2^(-2*10^11)` be decided exactly? First
   step: fix `q` and `B` from the compiler realisation. Blocked by: `B` is not
   materialised.
3. **Current selected record.** Does the later `frontier6030`/`frontier7000` BIT stage use
   the same rank, atom and stock formula? First step: compare its stage record with
   `research/query-thinned-controllers/RESULT.json`. Blocked by: the later stage's source
   bindings are not pinned here.

## Credit

JoyboyBrian: PR #4954, the stock formula analysis, Lemmas 1 and 2 re-proved here, the band
and the open question. James Reed: PR #4970, `S_old = 1`. unpaidmoon: the open PR #7101,
the bound `c_B <= 2^(H1+13)` (cited, not replayed). Mark (Matarener): the nested-width
bound used there. The source stock formula is DELAYED-COVER-BRIDGE section 8 and the
selected-stage parameters are those of `research/query-thinned-controllers`.
