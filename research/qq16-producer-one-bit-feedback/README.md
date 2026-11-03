# One fewer guard bit for the bounded-dirty QQ16 producer

For the literal QQ16 F0 followed by B_1_2 producer of
[commdata2338's PR3235](https://github.com/CrocSwap/integer-mult-bounds/pull/3235),
the common completed-operation relative tolerance

```text
u <= 2^(-beta-delta-101)
```

suffices for the same completed-stage allowances. The predecessor supplies
the sufficient offset 102. This result doubles the permitted local defects,
for every integer beta, delta >= 0, with the same bounded dirty inputs,
destination-local error contracts, exact private CLEARs and native isometry
premises. It changes no word or recursive invoice.

Claim type: a scoped written proof conditional on the cited producer ledger,
with exact rational corroboration. The new step retains the ledger's exact
derivative values and bounds feedback by 17/16 instead of two.
[PROOF.md](PROOF.md) gives the all-parameter argument and inherited premises.
No minimum guard or physical accuracy implementation is asserted.

## Exact margin

After dividing the B1 error bound by its allowed `H 2^(-beta-13)`, the new
upper bound is

```text
591238384001709400030154487 / 618970019642690137449562112 < 1.
```

The strict slack is
`27731635640980737419407625 / 618970019642690137449562112`.
This is a sufficient upper bound, not a realized rounding error. The decoder
transfer, if separately implemented to its existing allowance, still gives
the credited `7587/8192` original-input error ratio.

## Reproduce

From the repository root with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/qq16-producer-one-bit-feedback/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/qq16-producer-one-bit-feedback/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/qq16-producer-one-bit-feedback
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/qq16-producer-one-bit-feedback --check-source-history
```

Any standard-library CPython 3.12 executable may replace the local path.
The direct marker is `PASS_QQ16_PRODUCER_ONE_BIT_FEEDBACK`. Replay reads
three authenticated predecessor files, imports no predecessor executable,
checks the new rational implication and bounded polynomial/parameter controls,
and prints a generated receipt bound to nine file hashes. It writes no files.
The 100-bit rejection only shows that this fixed sufficient certificate
cannot justify that stronger tolerance. It is not an impossibility theorem.

## Scope and remaining obligations

The predecessor derivative ledger and native/owner/sweep semantics are cited
premises. They are not audited or recomputed here. The result permits all five
declared defect categories and carries F0 helper errors into B1. It supplies
neither finite component widths nor a native implementation achieving those
defects. Exact borrowed-bit restoration, native interiors, grid/overflow,
physical storage/movement, a paid F17 consumer and supplier admission remain
open. No new kappa or selected-frontier change is claimed. The five framework
assumptions retain their status. Independent human and formal proof-kernel
review are unclaimed.

The current joint-query-controller card is explicitly changed to this small
producer-precision side theorem. It does not meet the card's complete physical
caller gate. The first selected-baseline control passed at main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8, selected PR6030.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19363489)
states the exact numerical target.

## Open next questions

1. Can one actual finite native child meet the enlarged destination-local
   defect allowance, including all scratch effects? Begin at a literal child
   followed by a half-ADD. The absent physical child implementation and its
   tariff block a supplier consequence.
2. Can a complete producer/decoder/consumer exploit the relaxed tolerance in
   a priced format? Begin with a single reached grid/range contract, exact
   helper return and every conversion charge. A relative tolerance exponent
   alone does not determine a register width or recursive saving.

## Credit

This contribution was produced by Nick Petalas. Credit commdata2338 / PR3235
for the positive path-polynomial method as applied to the complete producer,
the exact derivative ledger, operation contract and noisy-helper composition;
Nick Petalas / PR2965 for the completed-output decoder transfer; Ali Romman
and the joint-query team, ywz65 / PR2540 and PR2707, Arham Tahir / PR2681,
and the retained native, geometry and supplier lineage. Positive majorants
and elementary geometric-series estimates are classical. The new contribution
is this source-bound one-bit sufficient guard improvement. Apache-2.0.

## Verification bounds

Power-of-Ten rule 3 deviation: Python allocates integer, Fraction, JSON and
collection objects during verification. Each input is bounded to 2 MB; only
five source rows, three live inputs, 243 coefficient vectors of length five,
five tolerances per vector and 24 parameter cases are visited. No recursion,
subprocess or unbounded work queue is used. The largest fixture exponent is
127+64+101. The fixed capacities and read-only execution bound live work;
this is not a physical-memory invoice. A native fixed-storage implementation
would require its own representation and allocation proof.
