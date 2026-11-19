# Final P104 helper audit

The final split in PR #7781 preserves every prescribed public coefficient
and adds one independent helper without a new paid MOVE. All three fixed
pulse weights are uniquely required over the rationals. No new kappa is
claimed. Read [the proof](PROOF.md), [certificate](RESULT.json),
[source pins](SOURCE-PINS.json) and [credits](CREDITS.md).

Use Python 3.12 and the standard library from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-final-helper-audit
```

Both modes print this prefix and elapsed seconds:

```text
PASS_P104_FINAL_HELPER_AUDIT 1279 owners 3 pulse rank
```

The package has no network or Git dependency at replay. It checks 19
retained files, both graph hashes, all 48 changed rows, 4,904,966 rational
coefficient positions, the rank-three pulse minor, all eight fresh-term
omission subsets and twelve rational pulse controls. It also checks
causal chart access, every public chart and the exact native invoice.

The full physical application and its ordinary costs remain outside this
audit. All five framework assumptions remain. The proof gives the open
next question. The selected frontier is unchanged.

## Open next questions

Does the full caller preserve this exact owner boundary with its stated
ordinary allowance? Inspect the published application and its owner and
cost obligations. The present audit supplies the scalar map and local
rank delta for that check.
