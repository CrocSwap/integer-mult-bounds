# Accounting and finite witness (fusions + X54 on PR1193's mixed T37 construction)

This package keeps PR1193's dispatch, flow and owners unchanged. It replaces both local words:

- PR1195's two source-holder fusions (X=439 and X=444) are applied to each word.
- PR1130's X54/E589 slot, in PR1178's rebased recipe, is applied to each word.

The derivation below is PR1193's. Profiles and the final value have been updated to the composed words.
Section "Composition" at the end states the new parts.

Let D3 be the joint-entrance word from Thomas DiFiore's updated PR1148, with entrance groups 603, 611 and 635 demoted. Before composition its local profile is `{1:2364,2:498,3:412,4:130,5:82,8:8}` and its 480 helper widths have inventory `{4:44,5:44,7:38,8:114,9:240}`.

D4 additionally changes helpers 627, 629, 630 and 631 to entrance subspace `[68,34,24,1]`. Twelve B-frame assignments are refitted. The scalar operations, registers, coefficients, ordering, ports and centre interface stay identical. The explicit old/new recipe is in `data/FOUR-RECIPE.json`; fresh exact native replay decides validity, independently of the floating frame search.

Before composition D4's profile is `{1:2356,2:506,3:416,4:126,5:82,8:8}` and its width inventory is `{4:40,5:48,7:38,8:114,9:240}`. Thus each substitution changes the local profile by `−8H1+8H2+4H3−4H4` and increases occupied helper width by four.

The frozen dispatch has 125 D3 and 208 D4 calls on the PR1131/1152 wave order, sorted by `(37*stage+8*replica,stage,replica)`. The source-event geometry is the retained PR942 five-bank T37 lift. There are 33,152 live and 33,642 physical wires. No call is fragmented; each of its 480 helpers belongs to a distinct available physical family.

The flow uses these nine bin patterns (a zero-width pattern means empty):

| Capacity | Pattern | Count |
| --- | --- | ---: |
| 8 | 8 | 20,556 |
| 8 | 4+4 | 4,308 |
| 16 | 8+8 | 6,102 |
| 16 | 7+9 | 10,474 |
| 32 | 5+9+9+9 | 15,484 |
| 32 | 4+9+9+9 | 2 |
| 32 | 7+7+9+9 | 1,090 |
| 48 | empty | 11,374 |
| 48 | 4+8+9+9+9+9 | 5,202 |

`construct.py` checks exact pattern and call-width conservation, legal physical windows, and every integral flow entry. For each physical window group and pattern it completes the flow to a regular bipartite multigraph, decomposes it into perfect matchings, and assigns actual helpers of the nominated provider. This yields all 159,840 literal roles. The independent audit separately reconstructs the source events, strict bridge boundaries, physical family identities, 73-axis charts, occupied prefixes and complete per-call width inventories. It reads and recounts both admitted local words and selects them using the frozen call dispatch; it does not import the owner constructor or controller auditor.

The resulting idle profile is `{1:2,48:11374}`. Adding it to the two local profiles weighted by their exact call counts gives:

`{1:783552,2:169496,3:137362,4:42458,5:27306,8:2664,48:11374}`, using the composed profiles D3' = `{1:2358,2:504,3:410,4:130,5:82,8:8}` and D4' = `{1:2350,2:512,3:414,4:126,5:82,8:8}`.

Its rank mass is 2,408,256 and deficit is 11,840. The global prefix bound is 775 bits, below the charged 1,024; the finite physical row coefficient is 17,495, below 20,161. Those charges are checked by the complete retained invoice and independent owner audit, not inferred merely from profile feasibility.

The PR795/890 signed prices explain the choice of mixture. The uniform D3 inventory has rank-one dual credit 20,850 per replica. Each extra demotion group consumes 3,700 units. Across 37 replicas the budget is 771,450, permitting 208 such substitutions while leaving credit 1,850, exactly two rank-one idle units at 925 each. This guides the search; the literal witness and full admission are still required. It is not a proof of optimality for mixed suppliers.

The two retained rational engines bracket the complex root and the unchanged full PR589 supplier supplies the bit endpoint. `CLAIM.json` records the exact rational choices. The strict outer assembly selects κ = `1675809683500501/1000000000000000000`. The conditions and scope are the same as the retained framework; finite certificate success does not discharge the all-size multiplication theorem.

## Composition

Write J for PR1148's joint-entrance word.

- F is PR1195's two-fusion word. Its change from J is `{1:-6,2:+6,3:-4,4:+4,5:-2}`.
- X is J with PR1178's X54 recipe. Its change from J is `{3:+2,4:-4,5:+2}`.
- D4 is J with PR1193's group-627 recipe.

Relative to J, the three edit sets touch disjoint ranges of A and B. The only overlaps are:

- The cleanup front: X54 prepends its holder-335 FULL restore, and F reorders and inserts its holder restores.
- The early-cleanup list. Here X54 appends its holder-367 tail gate and registers it first.

The merged words keep:

- X54's prepend first and its tail gate last in cleanup;
- F's cleanup otherwise;
- F's early list, with the X54 tail entry first.

The composed words are D3' = J+F+X and D4' = D4+F+X.

Neither edit changes an entrance, an end frame, a port or the centre interface. Both widths are therefore unchanged, and PR1193's literal owners and flow remain valid without change. Validity is established by the exact checks, not by the merge rule:

- the exact independent local audit and the fresh native replay of both words;
- 28 composition controls: removing any inserted fusion or X54 gate from either word is rejected;
- strict global admission.

Both words' profile changes are exactly additive, `{1:-6,2:+6,3:-2}`.
