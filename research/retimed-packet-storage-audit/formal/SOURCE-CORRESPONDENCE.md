# Kernel proof of the retimed capped-power predicate

Status: scoped Lean 4.36.0 proof, with an inspected and hash-checked correspondence
to the predicate resolved by Ali Romman's #8042. This is a follow-up to the
stopping-control audit in #8091. The orchestrator independently replayed the kernel and source checks;
ROOT-REVIEW.md records the accepted publication boundary. The completed earlier compiler and analytic reviews are
unchanged.

## 1. Exact theorem and its domain

`CappedPower.lean` imports only `Lean` and uses natural-number arithmetic. Its
main state theorem is

```lean
theorem loop_correct (h a b p : Nat) (ha : 1 ≤ a) (hb : 1 ≤ b)
    (hah : a ≤ h) : loop h a b p = true ↔ a * b^p ≤ h
```

Here `a` is the accepted accumulated product, `b` the current possibly capped
power, `p` the remaining exponent and `h` the unchanged ceiling. The theorem is
universal in all four natural numbers subject to these three premises. There is
no upper bound on the exponent or input size.

The source-chronology version, `sourceLoop_correct`, has the same statement for
`sourceLoop`. The wrapper starts the accumulator at one and has the source's
argument order:

```lean
theorem power_le_correct (base power ceiling : Nat) (hb : 1 ≤ base)
    (hh : 1 ≤ ceiling) :
    power_le base power ceiling = true ↔ base^power ≤ ceiling
```

`retimed_stop_correct` specializes the exponent to `10^21`. `callerStop_correct`
also includes the actual caller's carrier short circuit, proving

```text
callerStop M e h D = true  ↔  e ≤ M ∨ e^D ≤ h.
```

Under the same `1 ≤ e`, `1 ≤ h` premises, `callerContinue_correct` proves

```text
callerStop M e h D = false ↔ M < e ∧ h < e^D.
```

This supplies precisely the strict parent relation used by the written
stopping-volume argument when a parent continues. It does not formalize the
recursive call geometry or field allocation.

The wrapper theorem needs a positive ceiling even when the exponent is zero.
The source returns `True` immediately for exponent zero, including when the
initial value one exceeds the ceiling. The formal `accumulator_premise_needed`
control records this behavior at `h=0,a=1,p=0`. The theorem therefore does not
silently assert equivalence on that invalid initial state. `exponent_zero` and
`base_one` separately state the valid source special cases. The actual
nontrivial supplier calls have positive selected width and positive original
root width; their reachability is the caller contract retained by this package.

## 2. Pinned sources and overlap

The source repository is `aliromman/integer-mult-bounds`, PR #8042 at
`dfd25d553a843a946ca0b94130a5ff8943e98fdd`. Canonical selected main remains
`e54523517d0f03e58352e647c403a5af3e525a57`.

| Source | Role | SHA256 |
|---|---|---|
| Resolved `positive.py` | Actual inherited `power_le` implementation | `a1b5d1725c6230667646d3e50551d566e2faac39bc39a02c703c3da065f4db5c` |
| `retimed_supplier.py` | Actual `_run` stop guard | `4bd969e3f1cfdcdf26c36e5fa7ab64c8e72904f516a51af6b2a29524e1cf8eb2` |
| `installations.py` | `RESOLUTION` supplies `10**21` | `2244e7e27f7348575944eb652a741861a0a04d77b18c297db221ef74b3116a16` |
| Resolved `band_product.py` | Forwards the profile's denominator into the supplier | `98595de1aa89a158cfddeb462f9a87bad4a8d59c0d1eb01f24790cb46050044d` |
| `lean/OuterStop.lean` | Existing abstract volume inequalities; overlap boundary | `1cbaf689d8bb02722e0361376780b326872f5e4775b30c6c5ae10a98c5994930` |

The directly fetched `OuterStop.lean` Git blob is
`fc2cf156fb0e2da844a7f1640bb17eabbc5414ec`, matching the local source. It already
proves `stopped_test_volume`, `stop21_physical_scan` and the root/child comparison
inequalities. It contains no definition or correctness proof of `power_le`.
This contribution adds the universal correctness proof of the capped predicate;
it does not reclaim those volume inequalities as new results. The source files
are retained through #8091's hash-checked runtime restoration; this supplement
does not alter them.

## 3. Python-to-Lean correspondence

The exact predicate extracted from the pinned resolved source is:

```python
def power_le(base, power, ceiling):
    value = 1
    while power:
        if power & 1:
            value *= base
            if value > ceiling:
                return False
        power //= 2
        if power:
            base = min(ceiling + 1, base * base)
    return True
```

All source inputs in the theorem's domain are ordinary nonnegative Python
integers, interpreted as Lean naturals. This correspondence uses the standard
integer meanings of multiplication, nonnegative floor division, bitwise AND,
comparison and `min`. It is an inspected source translation with exact hash and
AST checks, not a mechanization of Python's complete operational semantics.

| Pinned source action | Lean construction and justification |
|---|---|
| `value = 1` | `power_le base power ceiling := sourceLoop ceiling 1 base power` |
| `while power` | Zero exponent returns `true`; positive exponent enters the step |
| `if power & 1` | `sourceLoop` uses `p &&& 1 ≠ 0`; `low_bit_branch` proves equivalence to `p % 2 = 1` |
| `value *= base`, then rejection if above ceiling | The odd branch tests `h < a*b`; rejection returns `false`, acceptance passes `a*b` |
| `power //= 2` | The remaining exponent is `p/2` |
| Square and cap only when remaining exponent is nonzero | `sourceLoop` returns directly when `p/2=0` and otherwise passes `min (h+1) (b*b)` |
| Final `return True` | Zero remaining exponent returns `true` |
| Caller `selected <= n or power_le(...)` | `callerStop` is the corresponding Boolean disjunction |

For a convenient induction, the auxiliary `loop` recurses once with exponent
zero even after the final bit. Its would-be next square is irrelevant to its
Boolean value. `sourceLoop_eq_loop` proves their equality for **all** natural
states, without the positivity or accumulator-bound premises. Consequently the
correctness theorem applies to the actual chronology, which omits this final
square. Neither the auxiliary definition nor this equivalence is used to count
machine operations.

The caller imports `power_le` from `positive`. Its `_run` first sets
`n=self.carrier`, then uses exactly
`selected <= n or power_le(selected, self.denominator, root_width)`.
`band_product.production_supplier(rank_log, stop_denominator)` returns
`Positive(rank_log, stop_denominator)`, and the `RESOLUTION` profile supplies
`10**21`. These are the bound source interfaces for the specialization; the
generic Lean theorem also covers the other natural denominators.

## 4. Proof structure and well-foundedness

The cap lemma proves, for every natural `h,b,n` and positive accumulator `a`,

```text
a * min(h+1,b)^n ≤ h ↔ a*b^n ≤ h.
```

If `b≤h+1`, the factors are equal. If `n=0`, both factors are one. Otherwise,
when `b>h+1`, each side's product is strictly above `h`: a positive power is at
least its positive base and multiplication by `a≥1` cannot reduce it. The proof
also covers equality at `h+1`; it never replaces the sentinel by `h`.

The loop proof is strong induction on `p`, with recursive measure `p/2<p` for
`p>0`. The even and odd exponent identities are proved in naturals:

```text
b^p = (b*b)^(p/2)             when p % 2 = 0,
b^p = b*(b*b)^(p/2)           when p % 2 = 1.
```

Every accepted odd step preserves `1≤a*b≤h`. Every next capped base is positive
because both `h+1` and `b*b` are positive. The even step retains the accepted
accumulator. If an odd multiplication exceeds `h`, the unconsumed positive
power cannot bring the product back below the ceiling. At exponent zero, the
accepted accumulator premise is exactly what makes the unconditional `true`
return agree with `a*b^0≤h`. All uses of induction therefore preserve the
declared state domain.

## 5. Kernel audit, controls and reproduction

The proof contains no new axioms, `sorry`, `admit`, `native_decide`, unsafe
declarations or external proof oracle. `#print axioms` covers all principal
theorems and semantic controls. The allowed reported dependencies are the
standard Lean axioms `propext`, `Quot.sound`, and, for the source bitwise-AND
lemma and the theorems depending on it, `Classical.choice`. The core cap and loop
theorems report only `propext` and `Quot.sound`. These dependencies are stated
explicitly; this is not an axiom-free development.

Four kernel-checked controls address specific failure modes:

1. `cap_mutation_rejected`: capping at `h` falsely accepts `2^2≤3`, while the
   correct source predicate rejects it.
2. `equality_boundary_retained`: `2^3=8` is accepted; replacing the target by a
   strict inequality would fail.
3. `early_reject_retained`: state `h=3,a=2,b=2,p=3` rejects at its first selected
   multiplication.
4. `accumulator_premise_needed`: exponent zero returns `true` even when the
   initial accepted-accumulator condition is false, so that premise must remain.

`verify.py` checks all five source hashes, the exact predicate AST, the actual
caller guard, exponent selection and parameter forwarding. It executes eight
targeted source boundary cases, including the fixed `10^21` exponent, and
rejects cap, equality and initial-domain mutations. These source checks support
the translation boundary; they are not the proof of the universal theorem.
The script then compiles the Lean file with `LEAN_PATH` removed and checks that
all fifteen axiom reports contain only the listed standard dependencies.

The self-contained publication wrapper restores the pinned runtime offline.
From the repository root, with an installed Lean 4.36.0 binary, run:

```sh
python3 -B research/retimed-packet-storage-audit/formal/replay.py \
  --lean /absolute/path/to/lean \
  --output /tmp/retimed-capped-power-review
```

Expected marker: `PASS_CAPPED_POWER_KERNEL_AND_SOURCE_BINDING`. The proof hash,
Lean version, source hashes, controls and complete axiom inventory are saved in
`RESULT.json` and `lean-check.txt` under the supplied output directory.
Frozen original and orchestrator receipts are retained under `author-evidence/`
and `root-evidence/`. The
direct proof command is `env -u LEAN_PATH LEAN_BINARY CappedPower.lean`.

## 6. Limits and open next question

This theorem establishes the returned Boolean on the declared natural-number
domain. It does **not** formalize the written serial-bit lowering, its transition
count, the 98-product bound, head restoration, temporary cleanup, the recursive
width relation, global allocation or the full multiplication theorem. Existing
physical field and header contracts remain where the stopping audit uses them.
There is no new kappa or removal of a canonical foundational premise.

The next useful formal step is a cost-annotated transition system for the exact
source chronology, proving its product count and then connecting it to the
serial-bit implementation in `verify_stopping.py`. Its first feasible sublemma
is that nonzero exponents cause one selected multiplication per set bit and one
square per bit except the last, with early rejection only reducing that count.
The remaining blocker is the explicit machine representation and cost model;
it is not supplied by the present Boolean theorem.

Credit Ali Romman for the retimed supplier, inherited capped predicate and
existing `OuterStop.lean` development, and the credited authors of the inherited
positive runtime. Prepared for Jerry Chen / @CubeJerry with substantial OpenAI
assistance. The source correspondence is model-assisted review; kernel
acceptance applies to the stated Lean propositions. Apache-2.0.
