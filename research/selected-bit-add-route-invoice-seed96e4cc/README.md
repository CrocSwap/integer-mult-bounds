# Selected BIT same-family ADD route invoice

**Partial, conditional cost result. No new supplier, kappa, or multiplication theorem.**

## Result

For the pinned PR589 selected owner layout, this package reconstructs every
same-family helper ADD in the 288 selected local calls. Each event receives the
three chart actions specified by PR2195's restricted-fibre XOR procedure:
target alignment, source alignment, and target return. The verifier replays
each captured route word over exact rationals, checks its selected GL64 chart
map and dyadic primitive bill, then sums the route actions in chronological
event order.

| Item | Exact result |
|---|---:|
| Selected local calls | 288 |
| Same-family ADD events | 11,072 |
| Target/source/return route actions | 33,216 |
| Distinct used route types | 43 |
| Ordinary route operations | 19,398,656 |
| Double-half operations | 3,407,872 |
| Negations | 417,792 |
| Controlled shifts | 4,177,920 |
| Constant shifts | 1,097,728 |
| Low permutations | 321,408 |

The ordinary route bill per selected call ranges from 18,432 to 103,552; the
median is recorded exactly in [RESULT.json](RESULT.json). These numbers are
the route compiler's charged primitive inventory, not a count of completed
recursive child executions.

The concrete first event is stage 0, replica 0, local position 19422: family
451, target role 243 on axes 1..8, source role 244 on axes 9..16. Its three
route bills are 192 ordinary operations for the target, 512 for the source,
and 192 for the target return, plus the exact dyadic and permutation counts
in [RESULT.json](RESULT.json).

## Scan-sharing screen

The selected word has 3,456 `(call, family)` groups for 11,072 ADDs. If each
group could be processed with one family selection scan, the arithmetic
ceiling would remove 7,616 repeated selection scans. This is not an admitted
saving. In family 451, the same-family ADDs at positions 19422 and 19448 are
separated by an ADD at position 19424 that also changes role 243. The exact
three-operation control shows that moving the later family ADD across this
update changes role 244 on a valid dirty input. A correct cache would have to
retain and update the intermediate payload state and pay for its restoration.
No such cache is claimed here.

## Exact scope and limits

The route inputs are the selected base files pinned in [SOURCES.json](SOURCES.json).
The 43 used route records are captured from Jose Manuel's PR #2157 at exact
head `eb1bf93950e9b14f7fadca7892866e9f29a26ad3` and independently rebound to
the selected owner supports and exact matrix products by this verifier.
PR #2195 at `3a1cf78a1ba6322129e42d80c50d21765524d612` supplies the selected
owner schedule and the restricted-fibre three-route formula.

This is the route component of the #2179 handoff. It does not price the
whole-family selector `C_select(q) V_F`, the payload XOR term, fixed-tape
parking, descriptor installation, precision, the ordinary recursive children,
or restoration. Therefore it is not a complete selected low-class invocation
bill and does not establish admission to a recursive moment. The selected
conditional kappa remains `0.001672660197076918`.

The 43 route records are a small captured input, not an independent replay of
PR #2157's full 1,123-type catalogue. The present verifier checks every used
word against its exact selected map and bill. It does not search for cheaper
route words.

## Reproduce

From the repository root:

```sh
python3 scripts/research_package.py --package research/selected-bit-add-route-invoice-seed96e4cc --check-only
python3.12 scripts/research_package.py --package research/selected-bit-add-route-invoice-seed96e4cc
```

The registered verifier runs normally and with Python optimization enabled.
It uses exact `Fraction` arithmetic and includes controls for a corrupted
route word, an omitted target-return action, and naive reordering across an
intervening owner update. `OVERLAP.json` records the complete refreshed PR and
Discussion search used for the claim; it is not a novelty certificate.

## Open next questions

See [TASK.json](TASK.json). The next required step is to attach whole-family
selection, payload XOR, depth-first parking, descriptors, and recursive child
costs to one selected low-class invocation. A separate construction question
is whether any persistent family cache can preserve the exact chronological
word while charging the retained state and restoration.

## Credit

This package builds on DreamingOfClouds' PR589 selected tuning on eumemic's
base and Jose Manuel's PR #2195 owner-packet integration; Jose Manuel's
PR #2157 supplies the selected route
compiler and PR #2171 the controlled-ADD preparation interface. Commdata2338's
PR #2188 was checked as nearby descriptor work, but its implementation is not
imported. The retained upstream depth-first parking schedule and PR1627/PR490
work remain their authors' contributions.

Prepared by OpenAI Codex with substantial AI assistance in scope selection,
mathematical analysis, implementation, verification, and writing. No
independent human review is claimed. New work is Apache-2.0.
