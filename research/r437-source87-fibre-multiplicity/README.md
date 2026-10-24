# SOURCE87 fibre multiplicity

**Partial certificate. No new κ.** The selected conditional result stays
`60403/20000000` (`0.00302015`, #4470).

## Result

On the pinned SOURCE87 rank-2 entry of the R437 carrier integration, the
parent packet is exactly

```text
M = 9475 * 3^124
```

copies of the executed 972-bit fibre. Both arms C and D have this same `M`.
A leaf scan that charges one common per-fibre vector on every copy therefore
has C-minus-D difference zero on this entry.

The published extent triple `(2, 3 * 3^124, 2)` holds for the call
`(first, second, width) = (0, 126, 2)` at parent size 64 and atom size 3
exactly when the plan dimension is 64, and at no smaller positive dimension
through 64. The proof is [PROOF.md](PROOF.md). The checker recomputes the
integer map, rejects the neighbouring dimensions and a doubled gap, and reads
the compiler receipt.

## What stays open

The integration's whole-construction inequality is not settled. Gather,
routing, parking, and blank-return between the `M` fibres are not priced.
The compiler profile still changes by `{1: +288, 2: -576, 3: +288}`. Those
other requests are outside this entry. The reverse-row coefficient is not
rederived. No supplier and no new exponent is claimed.

## Task and overlap

- Task: `r437-carrier-integration`, scope **refined**.
- Base: canonical main `ff3cc58e370d0f678e529246f8c73e8094e18fcf`, priority revision 7.
- Ordered eligible list, the priority table in `docs/research/current-priorities.md`, then catalogue tasks that are not already in that table. A row stays while its stated next decision is still open:
  1. `uniform-transfer-audit` — #4100 still has caller-bound implications.
  2. `supplier-boundary-audit` — the full mixed engine has not been rerun.
  3. `joint-query-controller` — the matched whole-caller comparison remains stated.
  4. **This package.** `r437-carrier-integration`.
  5. `p104-side-correction`.
  6. `independent-moment`.
  7. `formal-interface-lemma`.
  8. `bit-helper-contract`.
  9. `bit-new-register-model`.
  10. `complex-rank-shape-decoder`.
- #4067 is the paid exchange. #4147 is the reverse coefficient, reused and not recomputed. #4176 (`research/r437-carrier-integration`) regenerates the compiler and checks the extent triple on one execution. This package classifies the dimension, names `M`, and separates this entry's zero leaf-scan difference from the nonzero profile delta.
- #4160 prices a different constructor tape and is not this geometry.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/r437-source87-fibre-multiplicity --check-only
python3 -B scripts/research_package.py --package research/r437-source87-fibre-multiplicity
```

`verify.py` prints `PASS_R437_SOURCE87_FIBRE_MULTIPLICITY`. Not run: the
integration's `physical.py` replay, Lean, Docker, and the selected cold replay.
The universal statement on dimensions `1..64` is the finite check in
`verify.py` together with the closed form in `PROOF.md`.

## Open next questions

1. Price the fixed-tape gather, routing, parking, and blank-return that
   separate these `M` fibres. That bill is what the integration still names
   as blocking a global paid improvement. Start with one spectator step on
   the pinned layout. Blocked here because no tape machine for the `3^124`
   gap is executed.
2. Apply the same extent map to one request in the profile delta. SOURCE87
   does not account for the `288` extra rank-1 requests or the `576` missing
   rank-2 requests. Blocked because the compiler receipt does not list those
   plan coordinates.

## Credit

Chris R / Clear1nsight, PR #4067 and PR #4176, for the carrier, the compiler
receipt, and the extent assertion. The reverse coefficient remains
unpaidmoon's PR #4147. The layout and plan sources are the retained
selected-bit caller. Prepared by unpaidmoon with substantial Cursor Grok
assistance. Apache-2.0. No independent human or formal-kernel review is claimed.
