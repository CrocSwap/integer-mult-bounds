# Independent Laurent replay of #4470's p16 controller

**Claim type:** an independent literal replay by separately written code. **No new κ.** It covers the
p16 query-thinned complex controller of 1337isnot1337's
[#4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470) (conditional κ = 0.00302015). That is
the maintainers' next substantive review per `docs/research/pr-intake-checkpoint.json`. My #4478 checked
#4470's arithmetic but left this controller uncovered.

## What is checked

The verifier reads only `research/joint-helper-lattice/CONTROLLER.json`. Each of the 32 lines is replayed
as a linear combination of the initial lines, with exact Laurent coefficients in `Q, D_0, …, D_32`:

| Event | Effect |
| --- | --- |
| `LOCAL` / `QUERY_SHEAR` on pair `(x, y)` (swapped when backward) | `y += Q^{−1}x` (or `y −= Q·x` backward); `LOCAL` then multiplies both lines by `D_stage` |
| `IDLE` | multiplies both lines of the pair by the selected `D_s` |
| `ADD` | adds a signed line |
| `SWAP` / `SIGNED_SWAP` | exchanges lines, with a sign |

Results:

1. **Event counts.** The word has 18 `LOCAL` (exactly the 18 thick stages), 15 `QUERY_SHEAR` (exactly the
   thin stages), 15 `IDLE`, 90 `ADD` and 16 `SIGNED_SWAP`.
2. **The factorization.** For **every one of the 32 monomials**, `left · W_m · right` is exactly the
   indicator of the declared diagonal entries equal to `m`. The central `Q` exponents are `+1` (16) and
   `−1` (16), and no output credits a thin stage.
3. **The controller invoice.**
   - main ranks `1 + 8·|stages|` × 112 ports: `{17…65: 448 each, 73: 224, 145: 224}`;
   - whole-idle ranks `8·|stages|` × 2 lines × 112 ports: `{16…64: 448 each, 72: 224}`;
   - 15 × 112 = 1,680 thin queries.

   All reproduce `CONTROLLER.json`.
4. **Controls.** Flipping one query's orientation changes the operator. Promoting a thin query to a full
   stage is rejected.

**Note.** `CONTROLLER.json`'s embedded `paid` and `targets` use the THREE-base local profile (for example
`paid[1] = 18·2487 + 1680 = 46446`). #4470's `RESULT.json` substitutes the new joint-helper profile
(`41946`). Its arithmetic is checked in #4478.

## Not covered

- The native word, meaning the physical contacts, phases and helper boundaries. #4504 audits the
  chronological frames and local invoice.
- The BIT controller, which is unchanged from #4440.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/pr4470-controller-replay --check-only
python3.12 -B scripts/research_package.py --package research/pr4470-controller-replay
```

The verifier prints `PASS_PR4470_CONTROLLER_REPLAY` in about 2 seconds, using only the standard library.

## Open next questions

1. **An all-column native replay of #4470's patched word by a second implementation.**
   - *First step:* apply `PATCH.json`'s 38/47/414 frame changes to the THREE-base word, and recount the
     paid profile with nested-frame dimension gaps, as in #4475.

## Credit

- The controller construction is Cinna Davis's (1337isnot1337, #4440 and #4470).

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
