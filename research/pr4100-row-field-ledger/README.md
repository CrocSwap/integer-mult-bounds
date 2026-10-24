# Short-field movement does not tighten the Strassen boundary row

**Scoped exponent comparison. No new κ.** #4100 is not accepted, and the
selected conditional result stays `0.00302015`.

## Scope and evidence

Card `uniform-transfer-audit`, scope **refined** to one substitution left
open by the boundary-arithmetic layout lemma. That lemma bounds one exposed
field by `8 max(1, ceil(log2 a))` times its real volume. #4100 already
writes the Strassen boundary cost

```text
O(V d W^(tau-1)/B polylog(p)),    tau = 45/16,
```

and the union movement `O(V d W/B polylog(p))`. This package compares those
two shapes after the layout factor is included. It does not replay the
carving program.

[PROOF.md](PROOF.md) records the argument. In the exponent dictionary of
FINE-PRIME.md §6–§7, a term `O(V (d/B) W^alpha polylog p)` has saving
`1 - epsilon + xi - alpha/2`. The layout movement is the `alpha = 1` shape,
because `ceil(log2 a) = O(log p)` for both named lengths: the
polynomial-width boundary row, using `W = O(sqrt(p) polylog p)`, and the
carved line `|E_i| = O(L W/B polylog p + W polylog p)` with
`L = 2^{ceil(400 log2 p)}`. Its saving exceeds the Strassen saving by

```text
1/2 - (3 - tau)/2 = 13/32
```

at `tau = 45/16`. The difference does not depend on `epsilon` or `xi`.
The printed `1/2` is the worst-case `log_p W`; a polylogarithmic factor
in `W` adds only `o(1)`, which does not close `13/32` for large `p`.
For every integer `W ≥ 1`, `W^{29} ≥ W^{16}`, so
`W^{tau-1} ≥ W` and the movement monomial is absorbed by the boundary
big-O. The exposed length is not set equal to `W` or to `B`.

The same gap is `5 · 10^{-65}` at the other printed exponent
`tau_eff = 2 + 10^{-64}`. Both exponents absorb the movement. Choosing
which exponent the ledger states is left open.

Charging the same logarithm on the full tensor volume, dropping the
written density `O(W/B polylog p)`, would leave saving `1 - epsilon`.
At the §7 parameters that quantity is strictly below the headline
`epsilon q`. The density is what keeps this charge off the binding row.

`verify.py` recomputes the rational identities, the integer bandwidth
comparison for `W = 1..256` and two larger widths, the named core-length
logarithm, and the two rejecting controls (`tau = 2` is not strict;
`tau = 7/4` makes movement the heavier row; the full-volume charge
undercuts the headline).

## Reproduce

From the repository root, on CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/pr4100-row-field-ledger --check-only
python3.12 -B scripts/research_package.py --package research/pr4100-row-field-ledger
```

The registered command is `verify.py`. It uses the standard library and
reads the pinned prose inputs. Expected first line:

```text
PASS_ROW_FIELD_LEDGER tau=45/16 c=3/32 movement_minus_boundary_saving=13/32 gap_independent_of_epsilon_and_xi=true integer_bandwidth_absorbed=true tau_eff_gap=5e-65 full_volume_charge_binds=true boundary_volume_charge_binds=false exposed_length_equals_W_or_B=false selected_decimal=0.00302015 no_new_kappa=true
```

## Open next questions

1. **Choose the boundary exponent.** GAUSSIAN.md uses `tau = 45/16` for the
   seven-product paragraph, while UNION-SCHEDULE §4 uses
   `tau_eff = 2 + 10^{-64}`. Both absorb this movement. The ledger row
   still has to name one of them before the layout lemma is copied in as
   a numeric coefficient. First compare those two sentences with the
   generated ledger at head `337d04939571a637aeab54a0f58f54fde811663a`.
   Blocked here because that ledger is a different program.
2. **Extract the density constant.** The `O(W/B polylog p)` factor is used
   as written. An explicit `C` such that `mu ≤ C (W/B) (log p)^k` would
   turn the `13/32` gap into a finite-`p` inequality. First pin `C` and
   `k` from the carving proof, not from another asymptotic sentence.

## Credit

The boundary and union sentences are Cinna Davis's #4100. The layout lemma
is `research/pr4100-row-field-movement` (unpaidmoon). The exponent table is
FINE-PRIME.md §6–§7, and the carved-line bound is CAPPED-SIGNOFF.md. The
coverage map that listed the row-field movement as unaudited is PR #4311
(Ryanson Jonathan). PR #4376 proved the layout count and left this
substitution open.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review and no formal-kernel acceptance are claimed.
