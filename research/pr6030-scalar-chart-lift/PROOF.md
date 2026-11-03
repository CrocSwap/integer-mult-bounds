# Scalar instructions of the selected PR6030 word lift at every column multiplicity

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No new κ. Assumption ID: `native_all_columns`. This is one implication of that assumption on the selected caller. It is not the assumption, and it is not any of the other four.

## 1. Proposition

Let the selected word be `research/p104-helper470-twin-rung-removal/WORD.json.gz` on canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a` (PR #6030, κ = 781451/250000000). Its schema is `p104-accumulated-block-composition/2`. It has 770 public registers, 29 owned registers and 22,803 events.

Use the convention in the selected PR6030 review and in #5837: a register at an invertible chart `C` stores logical coordinates `u`, the physical vector at column multiplicity `f ≥ 1` is `C^{(⊗)f} u`, and a scalar coefficient stays outside the tensor power. Equal frame indices name the same chart.

**Proposition.** Every `SCALE`, `ADD` and `COPY` in this word acts on those logical coordinates by the same rational matrix at every integer `f ≥ 1`.

The 3,453 `MOVE`s are not included. #5837 proved the same scalar sentence for the older selected #5599 word and stated that a different word still has to be proved on its own hypothesis. This note is that hypothesis for the word the selected record now uses.

## 2. Lemmas

The three identities below are the chart-algebra argument of `research/native-scalar-chart-lift/PROOF.md` (unpaidmoon, PR #5837). They do not depend on which word supplies the events. They are restated so this note can be read alone.

Let `C` be an invertible linear operator on a finite-dimensional space `V`. Write `C^{(⊗)f}` for its `f`-fold tensor power, and write `(C^{(⊗)f})^{-1} = (C^{-1})^{(⊗)f}`.

**Lemma A (scale).** For every scalar `q` and every `f ≥ 1`,

```text
C^{(⊗)f}(q u) = q C^{(⊗)f} u.
```

*Proof.* A scalar factors through every linear map, hence through each tensor factor and through their product. ∎

**Lemma B (common chart).** If both operands are logical coordinates of the same chart `C`, physical addition and return to that chart are

```text
(C^{(⊗)f})^{-1}(C^{(⊗)f} u + q C^{(⊗)f} v) = u + q v.
```

`COPY` of `q v` into a zero logical register is the same identity with `u = 0`.

*Proof.* `(C^{-1})^{(⊗)1} C^{(⊗)1} = I`. If it holds at `f`, the mixed-product identity `(A⊗B)(C⊗D) = (AC)⊗(BD)` gives

```text
(C^{-1})^{(⊗)(f+1)} C^{(⊗)(f+1)}
  = ((C^{-1})^{(⊗)f} C^{(⊗)f}) ⊗ (C^{-1} C) = I.
```

The scalar `q` then passes through that inverse. ∎

**Lemma C (distinct charts).** If the destination chart is `C_R` and the source chart is `C_S`, the same reading is

```text
u + q (C_R^{-1} C_S)^{(⊗)f} v.
```

This equals `u + q v` for every `f ≥ 1` and all vectors if and only if `C_R^{-1} C_S = I`. The "only if" is the case `f = 1`. The "if" is Lemma B.

*Phase trap.* If `C_R^{-1} C_S = -I`, the correction is `(-1)^f`. The width-free update `u + q v` is therefore right for every even `f` and wrong for every odd `f`. Agreement at width 2 does not imply agreement at width 1 or width 3.

## 3. Binding to the selected caller

The chart state of the word is the following finite machine. Public registers start at `initial`. Owned registers start with no chart. `INIT` on an unowned owned-index gives that register a chart and an empty logical row. `CLEAR` on an owned register at the named chart drops both. `MOVE` from the current chart replaces it. A scalar event is accepted only when every operand's current chart equals the event's frame tag, the coefficient is a nonzero rational, and a `COPY` destination is an owned register whose logical row is empty.

`verify.py` reimplements that machine and no endpoint arithmetic. On this word the walk accepts every event:

| Opcode | Count |
|---|---:|
| `ADD` | 18,404 |
| `SCALE` | 861 |
| `COPY` | 23 |
| `MOVE` | 3,453 |
| `INIT` | 31 |
| `CLEAR` | 31 |

All 29 owned indices in `770..798` occur. Register 778 is initialized three times and the other 28 once, always after a `CLEAR`, so the 31 lifetimes are serial. The peak number of simultaneously owned registers is 13. At the end no owned register remains, and every public chart equals `final`.

Each of the 23 `COPY`s writes an empty owned row, so its logical vector is `u = 0`. Each `ADD` and each `COPY` has one common frame index on its operands, so Lemma C's obstruction is absent and Lemma B applies at every `f ≥ 1`. Each `SCALE` is Lemma A at the destination chart. That is the proposition.

The same walk rejects a cross-chart `ADD`, a stale frame tag after `MOVE`, a zero coefficient, and a `COPY` into a nonempty owned row. Replacing the frame tag of the first `ADD` in this word is rejected. Those are finite rejection tests of the walker.

The tensor specimens in `verify.py` check Lemma A's commutation, Lemma B's pullback and the mixed-product step on Pauli `X`, the shear `[[1,1],[0,1]]` and `[[2,3],[5,7]]` at widths 1, 2 and 3. They also check the phase trap: `(-I)` matches the width-free replay at width 2 and misses it at widths 1 and 3. Those specimens support the tensor implementation. They are not the all-`f` proof. The all-`f` proof is the induction in Lemma B together with the common-chart and empty-`COPY` census above.

## 4. What remains

This does not prove that a `MOVE` from chart `A` to chart `B` equals `(chart_B^{-1} chart_A)^{(⊗)f}` with the signed Pauli image and absolute phase. #6293 records the phase factor `i^{p f}` for this same word and leaves the joint lowered recipe open. Spectators, whole-job adapters and the fixed-tape tariff stay open.

`INIT` and `CLEAR` are used only as the chart and emptiness state machine. That is not a proof of the physical erasure contract in `owned_erasure`. `compiler`, `precision_tape` and `analytic_recovery` are untouched. Dyadic denominator bounds are a precision obligation and are not re-audited here. No outer row, admitted BIT budget or selected κ changes.

#5625 (CRT row reentry) and #5707 (root-prefix lowering) are partial interfaces of other callers. The width-1 endpoint replay in `research/p104-6030-independent-audit` checks this word's charts and empty `COPY`s as part of a different obligation. It does not state the all-`f` scalar proposition. #6522 records the `precision_tape` envelope exponent and is not this implication.

## 5. Downstream effect

The width-free rational rows of this word's scalar program remain the logical coordinates at every positive column multiplicity, for `SCALE`, `ADD` and `COPY` only. A later all-width claim for a `MOVE`, a native adapter or another word still has to be proved on its own hypothesis. Discharging the scalar half does not remove `native_all_columns` from the selected record.
