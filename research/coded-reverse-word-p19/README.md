# The p=19 coded-reverse supplier: materialized word, paid accounting, kappa 0.0034

**The physical p=19 coded-reverse controller path is built and replayed: 259 gate
records (39 stages, their 36 retained idle calls, the bridges and the closing swap),
77 recodings, exact at p=2 and p=19. Its complex side is 0.007578535,
which funds the outer endpoint at the admitted BIT cap: kappa = 951999/280000000
= 0.0033999964, +12.58% over the selected frontier 60403/20000000 = 0.00302015.
The word carries no Gaussian rank — its 77 recodings are 17,248 monomial field
maps, 68,992 scalar adds and 1,232 owned clears per call — so the rank invoice
is unchanged by the code and the bill is charged in the nonrecursive budget.**

## The word

`P19_WORD.json` holds the listing and `p19_word.py` replays it: a gauge load on
each odd role, a forward stage, then per pair a reverse add, the stage letter,
the two bridges, the forward stage and the two bridges again, the reversed bridge
sweep, and the gauge unload.

| gate kind | count |
|---|---|
| `GAUGE_LOAD` C⁻¹ / `GAUGE_UNLOAD` C | 19 / 19 |
| `REVERSE` a −= Q C b | 19 |
| `LETTER` full Gaussian R on both roles | 19 |
| `FORWARD` b += C⁻¹ Q⁻¹ a | 20 |
| `IDLE` R^k on both roles of a pair: 9 initial, 18 middle, 9 terminal | 36 |
| `BRIDGE` | 108 |
| `SWAP` with the −1 sign, after the gauge unload | 19 |

The idle calls are the formal controller's own (`idle_call` at
`coded-reverse-controller/verify.py:44`, retained by `keep_of`): 198 rank applied
across 396 role-rank. Each is a power of the full Gaussian R, and `[R, C] = 0`
makes it gauge-neutral, so the idles add no recoding and no field map.

The final swap is the formal controller's closing `matrix[2j], matrix[2j+1] =
matrix[2j+1], -matrix[2j]`; it must sit after the gauge unload, otherwise the code
is applied to the wrong role. The 408 per-stage-unit helper jobs
(`{4:28, 7:7, 8:47, 9:326}`, 7,752 units) are inherited unchanged and priced only
by the invoice's T side; they are not materialized here.

Replay equals the standard word on 0 of 229,376 entries at p=2 and 0 of
2,179,072 at p=19. The invariant is stronger than the end-to-end equality: with
the per-role gauge `v = lam phi` the identity holds after every gate that writes
a role, so any failure localises to a gate. The stage letter must commute with
the code; on a dense bank `[C,D]` and `[C,Q]` disagree on every entry while
`[C,R]` agrees on all, and a rank-8 letter can still be carried by unloading the
code before the letter (transient gauge, 3 recodings per reverse).

## The code and its precision

`A = I - M Mᵀ/4`, `A⁻¹ = I + (A − I)/13 = I − M Mᵀ/52`, and `A A⁻¹ = I` exactly.
A recoding is monomial address maps and scalar adds only, so its component-l1
prefix bounds are the published 57 (forward) and 69/13 (inverse, output-only);
no recursive Gaussian child enters the word. Denominators are 1/4, 1/52 and the
controller's [1, 13].

## The complex side

The rank invoice takes the pattern, the thick stages and the paid profile, never
the code, and both counters pop rank 0. With the PR4929 profile the p=19 word
prices at 0.007578535 (the prior profile gives 0.003004145), so the complex side
is not the binding constraint. The ledger's tested saving is derived from the
endpoint on the source's integer grid, `TESTED = kappa + 7·gap` with
`gap = 1/1400000000`, and the raw moment sign there is positive in exact interval
arithmetic and in an independent 60-digit decimal engine, positive a step below
and negative above the root. At the
endpoint the charged ratios are alpha 0.99579414, gamma 0.963763, delta 0.951561;
both decay blocks are under 1/16 and the power-1024 tails are under 2⁻³².

## The paid accounting

- field-level bill: 77 recodings = 17,248 monomial field maps, 68,992 scalar
  adds, 1,232 owned clears per call, zero Gaussian rank;
- compiler: the receipt calls the source's own
  `power_majorant_comparison(1024, kappa+6*gap)` with the unit's tested saving,
  and it returns H0 = 497,275,706,368 and H1 = 4,734,066,216,450,479,105 with the
  previous threshold rejected. The source retains that power proof as "changing
  only the new unit's ranks", and the unit's ranks are the verified T/D census,
  which is why it is the majorant applied here. The ranks are finite but
  enormous, and this is the claim's largest open risk;
- BIT: atom 0.004 > ordinary saving 0.0034363538 > admitted cap 0.0034
  (`research/query-thinned-controllers/PROOF.md`);
- budgets: local routes 4,794,000 + local scalar 158,168 < 10⁷; raw
  190,766,976 + field bill 18,144,000 = 208,910,976 < 10⁹, so the bill is charged
  in the raw bucket;
- strict outer ledger: every predicate passes at the endpoint; at exactly 0.0034
  only `actual_bit_above_effective` fails, so the endpoint is
  `bit_saving − 5·gap`.

## What the audit changed

Three defects were found by auditing the word against the formal controller and
the source ledger, and are fixed here: the missing final role swap with its −1
sign; the missing declaration of the inherited helper block; and a ledger
parametrization that passed a tested saving far above the endpoint together with a
tiny grid gap, which the source does not allow (the gap is derived as
`(TESTED − kappa)/7` and must have numerator one).

## What this package corrected

The recovered p=2 baseline compared two builds that draw independent random
initial roles, so its residuals measured state mismatch, not the construction;
with a shared state the failure was the rank-8 letter and the thin read in the
wrong order (`Q⁻¹` then `C⁻¹` instead of `C⁻¹` then `Q⁻¹`). The earlier tariff
attempt charged the recodings as rank-1 mass; the invoice's own convention pops
rank 0 and `invoice()` takes no code argument, so monomial work cannot enter it.

## The three premises, discharged

1. **Tail limit.** The source tail argument closes at any limit `L` with
   `L^128 < 1/16` and `1/(1+1024·10⁻⁹) + 4·L^1024 < 1`. With `L = 97/100` both
   hold exactly (`0.97^128 = 0.0202666 < 1/16`, `0.97^1024 < 2⁻³²`), so the
   source's `19/20` is a stronger unused choice and `0.97` is sufficient.
2. **Compiler choice.** The source states the power majorant concerns
   normalised rank-one leaf counts in the finite compiler and applies it to a new
   unit's ranks. This unit's ranks are the verified census, so the substitution is
   the operation the source performs; the logarithmic route is not used and its
   cap (611329/200000000) is recorded. What is not supplied is a machine-checked
   proof that structural change is immaterial — that is an applicability judgment
   at the source's stated scope.
3. **Helper block.** `T` minus the role-only census equals exactly
   `19·{4:28,7:7,8:47,9:326}`, so the helper mass is additive and separate, and
   PHYSICAL.md declares the helper jobs autonomous with independent fields never
   used as scratch. No helper gate sits on a coded main role.

## Open next questions

- The field-level bill is exact but its admission under the caller's fixed-tape
  and precision ABI is a premise, not a proof here.
- The compiler's logarithmic majorant (theta 63/64, power 1000) caps the tested
  saving at 611329/200000000 = 0.003056645 at ambient rank 153, with an eta margin
  of −1.2e-7, so it cannot carry a unit tested at 0.0034000014286; the receipt
  records that cap and its endpoint (1194/390625 = 0.00305664, about +1.21%). This
  claim rests on the retained power majorant instead, which the source allows
  because only the unit's ranks change.
- The inherited all-size/compiler, hosting, tape and analytic interfaces, hosted
  CI and kernel review remain external obligations.
- The p=19 listing is replayed in one interpreter; a second implementation in a
  different language or data representation would strengthen the word receipt.

## Reproduce

```sh
python3 -B research/coded-reverse-word-p19/p19_word.py      # listing replay, ~2 min
python3 -B research/coded-reverse-word-p19/p19_claim.py     # code, invoice, bill, compiler, ledger, claim
python3 -B research/coded-reverse-word-p19/verify.py        # fast receipt over the package
python3 -B research/coded-reverse-word-p19/full_p19_diagonalization.py  # long formal p=19 run
```

## Credit

PR4940 coded reverse controller: Cayden Burkart / SethBurkart123. PR4933 signed
physical code: Dillon. PR4929 center-free producer: Dugongue / mdumitrean.
PR5036 physical gap: JoyboyBrian. PR4440/4470 controller and query thinning:
Cinna Davis / 1337isnot1337. PR4433 compiler majorant and PR4359 outer ledger are
retained with their own attribution. Retained lineage as credited in those
packages.
