# Owned first-use reconstruction bound

**NO VERIFIED GAIN.** Exact #7334 `aaeec8c0acf01e99a5f331ef363a698d9c084ace` and signed caller #7113 `07a76c5e2738882c0cb322278e56f6cae3c9885d` remain the comparable construction at κ = 0.00364665195644.

Can a paid owned MOVE be deleted if the old owner row is rebuilt in the destination chart just before its first use? All 47 first contacts are immediate, comprising 43 ADDs and four SCALEs. Each old row is outside the rational span of all then-live cocharted public and other owned donor rows.

For the 11 cases beginning with a private owner write, the replay also skips the maximal owner-only ADD/SCALE prefix. Its first barrier is an outward ADD in seven cases and the next MOVE in four. There is no unobserved CLEAR. All 11 required rows are outside their delayed banks. Every fixed-bank key has an exact signed separator, and no key remains unresolved. The replay leaves changed donor itineraries, later observation boundaries and jointly modified state outside scope.

Use CPython 3.12 with assertions from a clean checkout.

```sh
python3.12 -I -B research/p104-owned-first-use-prefix-bound/replay.py
```

The Git-free command authenticates exact inputs, regenerates both directed invoices and all four scientific receipts, then checks two altered-input controls. Use `--out fresh-directory` to retain the six deterministic receipts. [Proof and accounting](PROOF.md) and [verification](VERIFICATION.md) describe the exact obligations.

#7307 and #7308 supply the earlier owned transport checks. #7355 supplies the snapshot engine, #7384 the signed separator reducer, #7362 the rank stock, #7338 the exact signed admission, and #7298 the directed tariff. #7334 and #7113 supply the current word and caller. OpenAI Codex and subagents materially assisted.

## Open next questions

Could a different donor itinerary or a further observation-neutral prefix make one priced owner reconstructible? Freeze one exact case and price its complete changed contract before support. The two unchanged-live-bank families are exhausted.
