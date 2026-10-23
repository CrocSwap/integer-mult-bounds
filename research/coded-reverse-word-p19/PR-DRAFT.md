# PR draft: the p=19 coded-reverse supplier (draft, verification open)

**Status: draft. Not proposed for merge. Several links are exact, but the items in
"Still needs verification" are unresolved and a reviewer should not read this as a
completed supplier.**

Title:

```
Certify conditional kappa 0.0033999964 via the physical p=19 coded-reverse word (complex 0.007578535, BIT 0.0034)
```

The title follows the repository's own forms: `Construct conditional kappa 0.00302015
with joint helper boundaries` and `Certify conditional multiplication kappa
0.003020165 via critical-root transfer` for conditional kappa claims, and
`Quotient the complex ambient by span{511}: complex kappa 0.01209185 (outer capped at
0.0034)` for a high complex supplier whose outer value is capped. This one is both:
complex 0.007578535, outer `conditional kappa 0.0033999964`. Shorter alternative if
maintainers prefer the older style:

```
The physical p=19 coded-reverse word: complex supplier 0.007578535, conditional kappa 0.0033999964 (BIT-capped)
```

## Summary

`research/coded-reverse-word-p19/` materialises the p=19 coded-reverse controller
word and prices it. The complex side reaches 0.007578535, the BIT supplier is the
admitted 0.0034, and the strict outer ledger passes at
`kappa = 951999/280000000 = 0.0033999964` (+12.58 % over 60403/20000000), failing at
exactly 0.0034 only on `actual_bit_above_effective`.

## What is exact and replayed

| item | value | how |
|---|---|---|
| word | 259 gate records: 19 load, 19 unload, 20 forward, 19 reverse, 19 letter, 36 idle, 108 bridge, 19 swap | `p19_word.py` listing, replayed |
| replay | p=2: 0 of 229,376 entries differ; p=19: 0 of 2,179,072 (dense state) | gauge invariant after every write |
| code | `A = I − MMᵀ/4`, `A⁻¹ = I + (A−I)/13 = I − MMᵀ/52`, `A A⁻¹ = I`; prefix bounds 57 and 69/13 | exact rationals |
| idles | 36 retained (9 initial rank 90, 18 middle rank 18, 9 terminal rank 90) = 198 rank, 396 role-rank | `keep_of` census, materialised as R powers |
| field bill | 77 recodings = 17,248 maps + 68,992 adds + 1,232 clears, 0 Gaussian children | rank-free proof inside `p19_claim.py` |
| invoice | p16 published root reproduced; p19 complex root 0.007578535 | exact interval engine + 60-digit decimal control |
| guards | α 0.99579414, γ 0.963763, δ 0.951561 | exact intervals; decay blocks < 1/16 |
| compiler | power majorant H0 = 497,275,706,368, H1 = 4,734,066,216,450,479,105 | source function, previous threshold rejected |
| BIT | atom 0.004 > ordinary 0.0034363538 > admitted 0.0034 | inherited from `query-thinned-controllers` |
| budgets | local 4,794,000 + 158,168 < 10⁷; raw 190,964,096 + 18,144,000 < 10⁹ | exact |
| ledger | 54 strict + 4 functional predicates all positive at κ | `endpoint.py` |

Reproduce (about six minutes):

```sh
python3 -B research/coded-reverse-word-p19/p19_word.py
python3 -B research/coded-reverse-word-p19/p19_claim.py
python3 -B research/coded-reverse-word-p19/verify.py
python3.12 -B scripts/research_package.py --package research/coded-reverse-word-p19
```

## Still needs verification (why this is a draft)

1. **Compiler majorant applicability.** The claim rests on the retained PR4433
   *power* majorant, applied after setting the source module's `C` to this unit's
   tested saving. Its inequalities are verified and the source states the majorant
   concerns normalised rank-one leaf counts and applies it to a new unit's ranks —
   but no machine-checked proof is supplied that the coded-reverse structure
   (77 recodings, gauge, idles) is immaterial to it. The *logarithmic* majorant at
   ambient rank 153 caps the tested saving at 611329/200000000, and the endpoint it
   would force (1194/390625, ≈ +1.21 %) is recorded in the receipt.
2. **Tail limit.** The source certificates are written with δ < 19/20; this word has
   δ = 0.9515606085. The package substitutes 0.97 and shows the decay-block
   argument still closes (`0.97¹²⁸ < 1/16`). That is a re-derivation argument, not
   a citation.
3. **Helper block.** The 7,752 helper units of the invoice's T side are inherited,
   not materialised. The counter check shows they are additive, separate mass, and
   PHYSICAL.md declares them autonomous, but no helper gate is replayed.
4. **Field-bill admission.** The bill is exact and rank-free; its admission under
   the caller's fixed-tape/precision ABI is still a premise.
5. **Single implementation.** The listing is replayed by one interpreter and one
   data representation. The NumPy cross-check in the companion package cannot run
   here (no NumPy, and the package declares no dependencies).
6. **Kernel review, hosted CI, precision/tape/hosting.** Untouched by this package.

## Audit history

Three adversarial rounds. The first refuted the endpoint (compiler majorant,
completeness, guard convention); the second conceded the repairs but kept the
compiler and guard items conditional; the third is the prompt still outstanding. The
fixes it forced are in the package: the closing swap with its sign placed after the
gauge unload, the tested saving re-derived on the integer grid, the inherited
helper block declared, the compiler receipt calling the source function, and the 36
retained idle calls materialised.

## Reviewer's checklist

- Does the power majorant's scope statement license reuse for a structurally
  changed unit, or only for changed ranks?
- Is `0.97` an admissible tail limit for this family, or is `19/20` required by an
  inequality the package has not read?
- Is the helper block genuinely disjoint from the coded roles?
- Does the 396 role-rank from the idles agree with the invoice's role ranks?

Credit retained from PR4940/PR4933/PR4929/PR4433/PR4440/PR4470 as credited in the
package README.
