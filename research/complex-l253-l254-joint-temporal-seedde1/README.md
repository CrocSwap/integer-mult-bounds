# Joint temporal gauges on L253 and L254

**Finite scalar construction on the selected PR1263 word; no new κ.** The two
coordinate schedules reduce the complete scalar invoice by **364 complex
primitives per invocation in each orientation**. The recursive paid profile
and selected conditional κ remain unchanged.

## Result

The baseline is the exact 218-helper static word from PR1263 on the selected
PR1094 source, pinned at `5fbaca13028846bddbb001e8e07addc2ab8e5816`. We add a
time-varying dyadic offset to L253 and L254 while leaving the other 216 static
gauges fixed. The supports contain 96 and 120 ADDs and share one source ADD,
event 19427 in both orientations.
In PR1263's static word, both helpers have gauge `-1` forward and `+1`
backward; the new schedules add offsets to those retained gauges.

| Orientation | Static complex invoice | Joint complex invoice | Saving | Formal columns | Prefix bits |
|---|---:|---:|---:|---:|---:|
| Forward | 136,002 | 135,638 | 364 | 712 | 52 |
| Backward | 136,018 | 135,654 | 364 | 712 | 68 |

The exact joint DP covers offsets in `[-4,4]^2` at every one of the 215 union
ADDs. It evaluates 156,663 legal transitions per orientation and charges every
entry change, intermediate SCALE, and terminal restoration. Its minimum
complete bill equals the bill obtained by composing the separate L253 and
L254 one-coordinate schedules. At the shared ADD, both optimal offsets are
zero, so that event's joint coefficient cost equals its baseline cost. The
joint search finds no additional saving over the composed witness inside this
box. The pair uses 45 inserted SCALE macros and 52 real-component SCALE work;
changed ADD coefficients save 234 real primitives before those SCALE costs.

The real-component invoice falls from 68,001 to 67,819 forward and from 68,009
to 67,827 backward. The 192-bit payload charge remains in force, and the paid
recursive profile is identical to PR1263's. No new κ, selected-result change,
or native/hosted supplier admission is claimed.

## Reproduce

With Python 3.12 and the standard library:

```sh
python3.12 -I -O -B research/complex-l253-l254-joint-temporal-seedde1/verify.py
python3.12 -I -O -B research/complex-l253-l254-joint-temporal-seedde1/test_package.py
python3.12 scripts/research_package.py --package research/complex-l253-l254-joint-temporal-seedde1 --check-only
```

The verifier reconstructs the pinned PR1263 baseline, checks the L253 receipt,
recomputes the L254 one-coordinate optimum, solves the joint box, emits both
complete words, and checks their exact lowerer invoices and all 712 formal
columns. It also corrupts the shared ADD coefficient and omits a required gauge
transition SCALE while retaining its planned coefficient change in each
orientation; both mutations must fail the formal replay.
The tiny recurrence test compares the joint DP against direct exhaustive
enumeration.

Expected verifier summary:

```text
PASS_L253_L254_JOINT_BOX forward_saving_complex 364 backward_saving_complex 364 shared [19427] joint_box [-4, 4] events 215
```

## Scope, prior work, and limits

The result is exact for schedules whose two per-event offsets lie in the
declared `[-4,4]` box. The predecessor's exact L253 schedule and the exact
single-coordinate L254 breakpoint intervals lie inside it. No global optimum
over arbitrary joint integer exponents is claimed. The package keeps the
PR1263 source word and every other static gauge fixed; all original scalar,
frame, copy, and recursive events are preserved.

PR1350 supplies the L253 temporal schedule and explicitly deferred the
neighboring L253/L254 pair. PR1376 composes the disjoint L248/L253 supports on
the same PR1263 word. PR1380 jointly optimizes a different interacting pair,
L225/L350, on the older PR1094 word. PR1388 prices a shared ADD for L348/L359
on PR1263, and PR1408 composes the disjoint L248/L253/L259 schedules. This
package treats L253/L254, including their shared ADD, on the selected PR1263
word.

The selected result remains κ =
`836330098538459/500000000000000000`. The work does not establish native
emission, whole-call hosted admission, all-size compilation, or a multiplication
theorem.

## Credit and disclosure

Credit PR1263 and Philipp / @mightyOil for the frozen 218-helper word; Sagar
Thakrar / @thakrarsagar and PR1350 for the L253 schedule; Sagar Thakrar and
PR1259 for the exact temporal-gauge method; and PR1161 for the retained lowerer
lineage. Prepared by Cinna Davis / @1337isnot1337 with substantial OpenAI Codex
assistance in research, exact optimization, implementation, verification, and
writing. No independent human review is claimed. New work is Apache-2.0.

## Open next questions

- Can the `[-4,4]^2` optimum be promoted to an all-integer joint optimum? First
  step: derive a coercive exponent bound that includes the single shared ADD,
  both transition paths, and terminal restoration. The current result is exact
  only inside its declared box.
- Can this scalar schedule be admitted by the native hosted supplier with a
  complete source, frame, precision, and restoration invoice? The present
  package replays the exact formal word but does not implement that adapter.
