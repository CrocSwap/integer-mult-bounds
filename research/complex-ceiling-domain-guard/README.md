# Physical-domain guard for the local-word packing screen

The frozen `complex-local-word-ceiling/ceiling.py` calculator assumes several
physical input conditions without checking them. For example it accepts the
selected local profile with `centre=-1` and returns a certified numerical root
strictly above the selected physical ceiling. The interval arithmetic answers
that algebraic input correctly; a negative copied-centre charge does not describe
the declared physical model. An accidental negative value can therefore look like
packing headroom. Zero/negative grids and nonintegral ranks also lack a complete
entry-domain contract.

This opt-in adapter checks the physical domain before invoking the original,
SHA-256-pinned calculator. It retains rational counts and nonnegative rational
centre charges (including zero) for deliberate relaxations. Width, live families,
stages, unpaid coordinates and ranks must be integers; booleans and binary floats
are rejected. It also checks positive bounded grid, the outer idle-rank guard,
and coverage mass. The original calculator and every predecessor pin are unchanged.

The independent replay reproduces both endpoints of the selected ceiling exactly,
reproduces the negative-centre example, and rejects 29 malformed cases. Three
positive domain cases preserve fractional counts, fractional/zero centre charges,
changed unpaid counts, a smaller rank cap and an empty local word.

```sh
python3 -I -B research/complex-ceiling-domain-guard/verify.py
python3 scripts/research_package.py --package research/complex-ceiling-domain-guard --check-only
```

`guard.ceiling(...)` has the source calculator's main arguments. The guard is an
opt-in boundary for future screens, not an in-place change to existing callers.
The calculator can still reject valid inputs outside its exponential enclosure or
root-search window. This checks exact input types and the stated algebraic model;
it does not certify realizability, coverage-law applicability, a supplier, all-size
admission or a new exponent. No current selected input is shown to be wrong.

## Open next questions

Should future proposal-screen entry points adopt this opt-in domain contract?
The first step is to identify mutable callers that accept external profiles and
add the adapter with their own valid fixtures. Frozen evidence must remain intact;
this package does not migrate any historical caller.

## Provenance and credit

The selected packing card was changed to a verifier-domain audit after inspecting
the reusable screen; this is an engineering side result. `SOURCES.json` pins the
calculator and its expected selected result at main commit
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4. The exact arithmetic
and original model are Douglas Colkitt's with Claude assistance, building on the
PR1012 coverage identity and static44/PR525/PR643 ceiling lineage. New adapter and
replay: ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
