# Selected BIT stage: two-sided parent stock and the exact fit band

**Scoped written proof with exact finite checks; no new κ.** The subject is
the current selected record #4470 (κ = 60403/20000000, base
`cef4b52f2a59009865bf8eabde1be3f159063703`). We look at its one ordinary-BIT
bootstrap stage: the delayed-cover BIT producer of uniform rank
`N = 2^H1`, `H1 = 25986965159937`, stopped at atom width `w = ceil(e^(1/250))`
with old ordinary leaves. That stage gives the ordinary saving
`0.0034363538396`. Its source stock prescription (DELAYED-COVER-BRIDGE §8,
`BIT-ALLSIZE-PARAMETERS.json` `stock`) borrows

    k = D*(N^2*(w-1) + ceil(log_q(B*|GL_N(F_q)|))) + ceil(log_q S_old) + 1,
    D = floor(log_N ceil(e/w)),

high digits, and needs `k < e/2` "for sufficiently large `e`".

## Result

Write `k_par` for the parent (cover) part and `n = ceil(e/w)`.
[PROOF.md](PROOF.md) proves:

1. **Two-sided envelope.** `D*N^2*w <= k_par <= D*(N^2*w + ceil(log_q B))`
   for every `N >= 1`, odd prime `q`, `B >= 1` and `e, w >= 1`.
2. **Depth classification** (`N >= 64`; the fit side also needs `c_B <= N^2`):
   * `D = 0` has no parent stock.
   * Every `D = 1` width overdraws the chunk: `k_par > e`.
   * Every width with `n <= 4N^2` is infeasible.
   * Every width with `n >= 16N^2+1` has `k_par < e/4`. This includes all
     widths with `D >= 3`.
3. **Selected bands**, with `t = log2 e`:

   | `t` (bits) | parent stock | status of the source prescription |
   |---|---|---|
   | `<= 26091330481863` | `D = 0`, `k_par = 0` | no cover level runs |
   | `26091330481866 ..= 52182660963729` | `k_par >= e/2` | **infeasible** for every `B`, `q`, `S_old` and every larger admissible depth |
   | `>= 52182660963735` | `k_par < e/4` | fits, given `c_B <= N^2` and `k_old <= e/4` |

So the least width at which the stated reserve can be borrowed lies in a
six-bit window of `log2 e`. #4612's estimate `≈ 5.2183·10^13` is confirmed,
and now has a matching lower side. The uniform word becomes applicable at
`t ≈ 2.609·10^13` (`n >= N`), but its stock fits only from `t ≈ 5.218·10^13`.
That leaves a band of `26091330481864` bits in which the producer must not be
run as prescribed, including **every** single-cover-level width. There the
conversion has to call the retained old supplier directly, which
`three-stage-cover-rows.tex` allows for small widths.

The threshold is fixed, so the exponent and κ are unchanged. This is a domain
statement about the source's "sufficiently large `e`", not a counterexample.
The infeasibility side uses only the high-matrix lift and one full low chart
per level. It needs no hypothesis about `S_old`, `B` or the prime beyond
`q >= 3`.

**Separating parent stock from inner borrowing.** The band's lower side does
not depend on the old-leaf factor at all. On the fit side, `S_old` (called the
"inherited old-leaf … logarithmic reserve" in the source) only has to obey
`log_q S_old <= sigma_old*(1+log2 e)` with
`log2 sigma_old <= 52182660963686` at the fit point. Its numerical value is
**not** derived here.

## Evidence and checks

`verify.py` (stdlib, about 0.4 s) does the following:

* **Source binding.** It authenticates all seven pinned inputs. It reads `H1`,
  the atom `1/250`, the prime rule and the stage saving from
  `query-thinned-controllers/RESULT.json`. It requires the exact stock formula
  strings and the cited source sentences.
* **Small-rank models.** It checks Lemmas 1 and 2(a)–(c) exhaustively on
  432,000 instances (`N ∈ {2,3,4}`, `q ∈ {3,5,7}`, four role counts,
  `w <= 6`, `e <= 2000`), using exact `|GL_N(F_q)|`. Three of these orders are
  confirmed by brute-force enumeration. It also checks Lemma 2(d) for
  `D = 3..399` at `N = 64`.
* **Selected-rank witnesses.** It evaluates exact witnesses at `e = 2^t`,
  `250 | t`, for the selected `N`, using integer exponent arithmetic. They
  cover the bands, the D=1 band, `D >= 3`, and every multiple of 250 within
  5000 bits of the transition. The last infeasible witness
  (`52182660963500`) and the first fitting one (`52182660963750`) bracket the
  proved window.
* **Reduced-rank oracle.** The witness shortcut is compared with fully
  materialized big integers at reduced ranks (`H1 ∈ {3,5,6,7,2000}`, several
  atoms), over 869 widths.
* **Rejection controls**, all of which must fail:
  * a tampered bridge byte;
  * omitting the high-matrix lift (the D=1 overdraw then fails);
  * role count above `q^(N^2)`;
  * the stale atom `3/1000`;
  * a rank off by one;
  * a fit slack one bit too small;
  * claiming a single-cover-level width fits.

  The stored [RESULT.json](RESULT.json) receipt must match exactly.

Mutation tests were done on the author's side: a doubled D=1 inequality, fit
slack 5, a tighter fit lemma, a shifted documented threshold and off-by-one
witness exponents. Each one makes the verifier fail.

## Reproduce

```sh
python3.12 -I -W error -B research/selected-bit-stage-stock-band/verify.py
python3.12 -I -O -W error -B research/selected-bit-stage-stock-band/verify.py
python3 scripts/research_package.py --package research/selected-bit-stage-stock-band --check-only
python3.12 -B scripts/research_package.py --package research/selected-bit-stage-stock-band
```

`verify.py --write NEW_PATH` writes a fresh receipt and never overwrites one.

## Limits

* No supplier replay, no Lean, and no selected-frontier or κ change. The
  rank-`2^25986965159937` word is not materialized.
* Infeasibility concerns the source prescription `W(w)^D S_old` (and any
  larger admissible depth). A different cover design is not excluded.
* The two fit-side hypotheses are not derived. `c_B <= N^2` holds if the prime
  is also chosen above `B`, and follows from the inherited nested-width bound
  used by `lockstep-live-role-audit`. The old-leaf stock value is the other
  hypothesis.
* The outer reserve constant `C`, the complex row stock, and the tape,
  precision and analytic premises are all inherited.

## Open next questions

1. **Derive the old-leaf reserve `S_old` numerically from the retained
   completed-leaf contract.** It is the last factor of the selected stage's
   stock that is not numerically derived. It also replaces the
   `log2 A_old <= 64` assumption in `lockstep-live-role-audit`. As a first
   step, trace which old-supplier calls (weighted leaves, peeled atoms, cover
   routes) run while the parent rows are borrowed. Then decide whether the
   PR185 wording "no *external* extra stock" makes `S_old = 1` admissible.
   The blocker is that the old supplier's own reserve formula is outside the
   pinned #4470 notes.
2. **Should the source text name the band?** The bridge says "for sufficiently
   large `e`". A precise statement would say that the stage runs only from
   `log2 e >= 52182660963735` and calls the retained supplier directly below
   that. As a first step, a maintainer should decide whether to record the
   threshold beside the #4470 review. This needs a maintainer decision; the
   pinned sources are left unchanged here.
3. **Close the six-bit window.** The exact least fitting width depends on
   `c_B` and the precise `S_old`. As a first step, fix `B` (from the compiler
   realization) and redo Lemma 2(c) with the exact chart digits. This is
   blocked on the same two factors.

## Credit

zxv: #4359 and the delayed-cover bridge, stock formula and finite compiler.
Cinna Davis and zxv: the #4440/#4470 chain, including the atom change to
`0.004`. Mark (Matarener): #4612, the δ-generic upper envelope and the
`5.2183·10^13` estimate, and `lockstep-live-role-audit`, the outer `C` and the
`A_old` assumption. The `three-stage-cover-rows` authors and the PR185
completed-leaf lineage retain their attribution. Earlier
selected-stock-envelope packages (`selected-bootstrap-stock-audit`,
`stock-margin-chain`, `selected-stock-sharp-integer`) concern the historical
#1094 chain. They are cited for context only.

Prepared by JoyboyBrian with substantial assistance from Anthropic Claude
(Claude Code, Opus 5.5). No independent human or proof-assistant review is
claimed. Apache-2.0.
