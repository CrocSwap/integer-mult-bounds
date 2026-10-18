# Exact integer idle-histogram ceiling for the selected complex local word

**Scoped bound for one fixed local word. No new κ; the selected record is unchanged.**

`research/complex-local-word-ceiling` bounds how much any repacking of the selected complex
supplier can gain. Its proof puts the entire idle remainder of a call into `(1646/51)`
*fractional* rank-51 children, which minimises the per-call moment over all non-negative
**real** counts. That is the right optimistic relaxation, so its ceiling `a < 0.001690054109089`
is valid but not tight: a real packing uses a non-negative **integer** multiset of children,
because each rank-`r` child is an object.

This package replaces the relaxation by the **attained** optimum over integer idle histograms,
computed exactly by dynamic programming over the mass axis. The published ceiling therefore
becomes a statement about every realizable integer packing, certified without sampling, instead
of a statement about an unattainable fractional ideal.

## Result

Model inputs are unchanged and re-checked from the pinned certificate: the paid local word
`{1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}` per call, parent width `m = 73`, `2·4·112`
live data families per nine-stage replica (`w = 896/9` per call), centre charge 64, the
coverage identity `mass = 72·W + 64·N`, and the outer halving guard `R = 51`. The **only**
addition is that idle child counts are integers summing to `1646` rank units per call.

| Quantity | Fractional relaxation (`#complex-local-word-ceiling`) | Attained integer optimum (here) |
|---|---:|---:|
| Best idle histogram | 32.2745 rank-51 (fractional) | **32 rank-51 + 1 rank-14** (`1632 + 14 = 1646`) |
| Ceiling `a` | `< 0.001690054109089` | **`< 0.001688603446527`** |
| κ bound (`κ < a/(1+a)`) | `0.00168720264532540190` | **`0.00168575687166350251`** |
| Max gain over selected κ = 0.001672660197076918 | `+0.869420%` | **`+0.782985%`** |

Integrality costs `1.4507e-06` in `a`, i.e. **0.0858% of the relaxation ceiling**, and removes
**0.0864 percentage points** of the claimed packing headroom. The residual packing headroom of
the selected word is therefore **+0.783%**, not +0.869%.

The optimum `{51: 32, 14: 1}` is the same across the whole bracket and across both lever rows
below. It is also the largest-first greedy histogram; the greedy rule is *not* assumed optimal
— the dynamic program is the proof, and greedy is only a cross-check of the witness.

## Why the bracket is certified in both directions

`ceiling.py` supplies outward-rounded enclosures `(lo_r, hi_r)` of `(r/73)^(1-a)`. The dynamic
program returns

- `DP_lower(a) = min over integer histograms of Σ n_r · lo_r`, a certified **lower** bound on the
  attained per-call moment. If `DP_lower(a)/w > 1` then *no* integer histogram of any shape
  attains moment ≤ 1, so `a` is rejected.
- `moment_upper(H(a)) = Σ_{r ∈ H(a)} n_r · hi_r` for the dynamic program's argmin `H(a)`, a
  certified **upper** bound on that histogram's true moment. If it is `< 1` then `H(a)` is a
  genuine witness and `a` is accepted.

Bisection on those two predicates yields `a ∈ [0.001688603446526, 0.001688603446527]`. The
witness moment at the low end is `0.999999999999998779`; the certified lower bound at the high
end is `1.00000000000000178`. Both sides are witnessed, so the bound is neither vacuous nor
one-sided.

## The same correction on the centre-free lever

`levers.py` reports the centre-free row at `a = 0.00473765` (`κ` cap 0.00472). That row's
premises also admit integer idle counts, so it takes the same correction:

| Lever | `a`, fractional | `a`, integer | κ cap, fractional | κ cap, integer |
|---|---:|---:|---:|---:|
| selected word (baseline) | 0.001690054109089 | **0.001688603446527** | 0.00168720 | **0.00168576** |
| centre path free (no rank-8 copies, centre charge 0) | 0.004737653470 | **0.004733592412** | 0.00471531 | **0.00471129** |

The fractional column reproduces `levers.py` exactly, which is the cross-check that the two
rows use one model.

**Not listed: the two-unpaid-coordinates row (3.77×).** With `unpaid = 2` the per-call paid mass
is `71·(896/9) + 64 = 64192/9`, so the per-call idle mass is `13918/9`, which is **not an
integer**. A single call's child multiset cannot have a non-integral rank mass, so under this
per-call model that premise admits no integer packing at all. Its published `κ` cap is a
fractional-relaxation figure on a premise the parent README already labels a what-if for a
changed coverage law. This package reports the arithmetic and claims no integer ceiling for it.

## Controls

`verify.py` records thirteen control results; `RESULT.json` stores every one.

- The dynamic program agrees exactly with an independent exhaustive enumeration (plain descending
  recursion over counts, no shared code path) on three small domains: idle mass 30/cap 7,
  36/cap 8 and 45/cap 9.
- The certified integrality gap is positive on a 20-point grid of `a ∈ (0, ceiling]`; the
  smallest certified slack is `2.10e-07`.
- A rank cap of 48 is strictly worse than the cap-51 optimum, so the search is not silently
  truncated.
- The integer moment is strictly increasing in `a`.
- The optimum conserves the idle mass exactly and uses only ranks ≤ 51.
- The bracket is witnessed on both sides.
- The integer ceiling is strictly below the fractional relaxation.
- Tightening the guard to `R = 50` and adding one rank-1 local child each lower the integer
  ceiling (the parent's two monotonicity controls, now on the attained optimum).
- 25 randomly drawn integer idle histograms never beat the dynamic-program optimum — the
  parent's sampling control, retained only as a weaker statement.
- Largest-first greedy matches the dynamic program here, and greedy never beats it.

## Scope and limits

- This is a bound **within the existing ceiling model**: one fixed paid local profile per call,
  `m = 73`, 896 families over nine stages, centre charge 64, the coverage law and the halving
  guard. It is **not** a bound for other local words, port counts, templates, coverage laws or
  outer recipes, and it still allows every repacking without checking physical realizability.
  The DP optimum is an optimum over that combinatorial model; it is not a constructible circuit.
- The integrality constraint is only sound where the per-call paid mass is an integer. It is for
  the baseline and centre-free rows; it is not for `unpaid = 2` (above).
- The local word's own contribution is taken as fixed and exact from the pinned certificate. Only
  the idle remainder is re-optimised, which is precisely the degree of freedom the parent's
  ceiling allows.
- No κ is claimed, no supplier is admitted, and the selected frontier is unchanged. The result
  removes headroom from the incumbent word; it does not improve the construction.
- Predecessor ceiling arithmetic (exact interval primitives, coverage identity, halving guard,
  lever table) is Douglas Colkitt's `research/complex-local-word-ceiling`, unmodified and pinned
  in [SOURCES.json](SOURCES.json); this package imports `ceiling.py` rather than copying it.

## Reproduce

```sh
python3 -I -B research/complex-idle-integrality-ceiling/verify.py          # ~40 s, PASS_COMPLEX_IDLE_INTEGRALITY_CEILING
python3 scripts/research_package.py --package research/complex-idle-integrality-ceiling
```

`verify.py --write` regenerates `RESULT.json`. Standard library only; exact rational arithmetic
with outward rounding to 2⁻²⁵⁶, reusing `ceiling.py`'s logarithm and exponential chains.

## Open next questions

- **Extract the per-call idle mass of the pending local words (#1148/#1169/#1218 lineage) and
  screen them with `integrality.ceiling_int`.** Each will need its own idle mass to be integral;
  a word whose per-call idle mass is non-integral is a relaxation-only figure. The blocker is
  unchanged from the parent: the idle histograms live inside those packages.
- **How large is the integrality correction as the port count V varies?** The correction here is
  driven by `M mod R = 1646 mod 51 = 14`, the rank at which the fractional remainder must land.
  Fitting `ceil_int / ceil_relax` against `M mod R` across recorded words would say whether the
  0.086-percentage-point correction is typical or unusually large. Blocker: per-call idle masses
  for other words on a comparable template.
- **Does the selected record's own idle packing stay admissible under the attained ceiling?** It
  does: its certified moment there is `1.00003848944 > 1`, so the record is unaffected. A
  separate question is whether any *published* candidate packing of this word sits above the
  attained ceiling and would need re-screening. Blocker: the candidates' actual histograms.

## Credit

Prepared by Nick Petalas with AI assistance. Apache-2.0. The ceiling model, the coverage
identity (PR1012), the fixed-word packing-ceiling lineage (static44, PR525, PR643), the local
word and the selected record are Douglas Colkitt's and his credited predecessors'; see
`research/complex-local-word-ceiling/README.md` and
[the review through #2027](../../docs/research/community-efficient1000-review.md) for the
construction's credits. Retain those credit lines.