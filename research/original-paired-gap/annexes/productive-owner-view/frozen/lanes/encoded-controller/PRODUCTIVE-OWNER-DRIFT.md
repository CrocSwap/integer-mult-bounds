# A check of the unchanged productive-owner word

The original paired graphs do not restore the old productive inputs
when their mode roles use the unchanged 280-slot owner assignment.
An exact unit input in family 13005 gives output -1/4 in family 112.
The required output there is zero. The result also holds if every
promoted mode occurrence is negated after each paired suffix.

This rejects these two complete scalar words. It does not reject a
changed owner assignment, a new controller, or a paid correction.
The source inventory also has unresolved cross-core native aliases.
The calculation does not admit those aliases.

## Exact sector and event order

Use arrays that are constant on the native payload and on the cover.
Every native line, complete child transform, address permutation and
translation fixes this sector. Thus the actual source inventory gives
a finite rational scalar word on all 14336 productive families.
No family is treated as a clean mode or as an additional input.

The checker pins the source-domain skeleton. It has 144 calls and 626
paired event positions. Each call has 704 distinct owners. Across the
two cores there are 36 promoted-mode incidences, including family 991
used as a mode by both cores at times 64 and 65.

The checker executes the emitted paired prefix gates, the first raw
core, the second raw core, and the emitted paired suffix gates in that
order. It maps every local role to the actual old owner. It does not
replace an aliased pair by the endpoint formula for sixteen independent
modes. A mode negation, when enabled, occurs once per local mode role.
Therefore a shared role receives both literal negations.

At each raw core, its separately checked content map is

```text
F: x'=x, y'=y+(I-KR)x-Kz, z'=-z-2Rx;
B: y'=y, x'=x-(I+KR)y-8Kz, z'=-z-Ry/4.
```

Here `K=R^T/4` is the pinned actual coefficient matrix. The other
ordinary helper values are unchanged in this sector. Each raw core
receives the current values after all earlier operations.

## A unit-input witness

Set family 13005 to one and every other productive family to zero.
Family 13005 is the first mode of call zero. The main path is

| Position | Operation | Change |
| --- | --- | --- |
| 1 | First raw F0 core | Family 112 becomes -1/4; owner 13005 becomes -1 |
| 3 | Paired suffix | Counterpart family 7280 becomes -1/4 |
| 9 | Raw B1 core | Family 0 becomes 1/4 |
| 29 | Raw F2 core | Family 112 returns to zero |
| 324 | Replica-zero terminal | Family 112 becomes -1/4 from family 0 |

Family 0 has no further change between positions 9 and 324. Family 112
has no further change after position 324. The counterpart output gets
the same defect at position 333.

Owner 13005 has no other promoted occurrence. Its first later active
data use is at time 117, stage five, replica fourteen, X port thirteen
of pair two. That event is at position 460, after the defective output
has closed. Its next active use is time 127. A sign flip at position
three restores this old owner's value to one, but does not change the
early data path in the table.

The original-sign word changes 177 output families on this input. The
post-suffix-sign word changes 176. Both have the same first output
defect, family 112 with value -1/4. The JSON receipt gives hashes of the
complete exact defect vectors and the selected event traces.

## Controls and scope

The checker reverses every scalar graph, raw core and bridge in the
complete aliased word. Both variants restore the witness input exactly.
Thus the observed failure is an output-restoration defect of a
reversible word. It is not caused by a noninvertible update.

An independent eight-by-eight bank replay for every replica replaces
the raw core by the ordinary signed shear and removes the paired
graphs. All 128 independent bank columns return to their inputs. Since
those operations do not mix port coordinates, this checks the ordinary
event order on all 14336 productive coordinates.

Run `python3 -I -O -B check_productive_owner_drift.py` from this directory.
The expected status is `PASS_EXACT_PRODUCTIVE_OWNER_DRIFT_COUNTEREXAMPLE`.
The proof uses one explicit admissible input, which suffices to refute
the claimed identity for this fixed word. It does not test every input
or establish a limit for every productive-owner controller.

The surviving path identifies a concrete obligation for a changed
construction: remove the first mode owner's contribution before the
first replica's terminal, or change how that contribution is stored and
used. The much later data use of that owner cannot repair this path in
the unchanged scalar schedule.
