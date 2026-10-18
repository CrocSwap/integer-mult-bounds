# Selected PR1094 pending-axis and chronological reservation audit

**Independent finite verification; no new κ.** The selected PR1094 data passes
an exact cross-child Gram/rank audit and a separately implemented forward
reservation sweep. No discrepancy in the selected data was found.

This checks a concrete premise behind the owner boundary: distinct sets of
axis labels do not, by themselves, imply independent pending subspaces. The
inherited orthogonal-chart premise supplies that implication. The verifier
checks it explicitly, then follows every reservation to its actual idle sweep
without reading `PLAN.windows` or importing an existing owner checker.

## Result and reproduction

From the repository root, with Python 3.10 or later and no dependencies:

```sh
python3 -I -B research/selected1094-pending-axis-audit/verify.py
python3 -I -B research/selected1094-pending-axis-audit/test_audit.py
python3 -I -O -B research/selected1094-pending-axis-audit/verify.py
python3 -I -O -B research/selected1094-pending-axis-audit/test_audit.py
```

The verifier compares its deterministic output with [RESULT.json](RESULT.json).
`--out /tmp/pending-axis-result.json` writes a receipt for byte comparison.
The tests cover one complete positive fixture and 15 mathematical, temporal,
schema and source-pin controls. Checks use explicit exceptions and remain active
under `-O`. Typical runtime is about half a second for the verifier and one
second for the tests on the recorded macOS host; no performance claim is made.

| Finite coverage | Result |
| --- | ---: |
| Port/pair/side pending bases | 896 |
| Basis sizes | 224 of size 48; 672 of size 56 |
| Exact upper-triangular Gram entries, including diagonal | 1,335,936 |
| Replicated physical families represented | 14,336 |
| Whole-helper roles / complete calls | 69,120 / 144 |
| Reserved axis instances across all calls | 537,120 |
| Replica-local pre-bank source events / chronological cuts | 480 / 481 |
| Largest number of unreleased reservation marks | 110,488 after event 225 |
| Idle suffix profile | H1=2,276; H3=377; H7=7; H48=4,866 |

`cut_reserved_axes[i]` in the receipt counts marks after the first `i` events;
the initial cut is zero. Its canonical compact-JSON SHA-256 is
`f2585990a534ad239148145b37dc99def4ef81b2010914071f56c39f19d60c49`.
These are **accounting reservations until the owning idle sweep**, not an
execution trace, measured memory use, or a new physical invoice.

The whole profile, including the frozen local-word profile multiplied by 144,
is reproduced as H1=349,604; H2=60,192; H3=62,585; H4=20,448; H5=11,808;
H7=7; H8=1,152; H48=4,866. No endpoint or exponent is recomputed here.

## The checked implication

All vector operations are over F2, with the source's integer bit-vector labels
and dot product `popcount(x & y) mod 2`. For one port/pair/side, concatenate
the pending axes of **all** its idle children. The verifier checks that the
Gram matrix is the identity, and separately row-reduces the concatenation.

If vectors `v_i` have Gram matrix I and `sum c_i v_i = 0`, taking the dot
product with `v_j` gives `c_j = 0`. Thus they are linearly independent. In
particular, spans of disjoint subsets meet only in zero. This standard lemma
justifies treating the declared pending axes as independent coordinates.
The 896 checks apply to all 16 replicas because their phase input is identical;
replica identity is separately checked for each physical owner role.

Set disjointness alone does not imply this conclusion, even when each child
has an orthonormal basis. In F2^3, A=`[7]` and B=`[1,2,4]` are disjoint lists,
each locally orthonormal, but `7 = 1 xor 2 xor 4`. Their union has rank three,
not four, and their spans intersect in `<7>`.

The source-sized control uses port zero and children 0 and 14 of pair 1,
side 0. Replacing child 0's first axis by the XOR of three axes of child 14
preserves each child's rank, local orthonormality and distinct axis labels,
but decreases the concatenated rank by one. The cross-child Gram predicate
rejects it. This is a counterexample to the **weaker inference**, not to the
selected construction. The production lineage separately inherits checked
orthogonal charts; neither the selected certificate nor its source pins are
changed by the control.

## Chronological check

The verifier reconstructs the nine source blocks from the pinned parent
template and expands the pinned order into 480 replica-local events. Every
replica's projection must equal the original 30-event sequence. It rederives
the 480 helper widths by exact rank of the frozen initial/final spaces,
including initial-space containment, and requires every call to contain every
helper once at its exact width. Physical family and copy identities, active
pair exclusion, and one helper per family per call are checked explicitly.

A helper's declared slice is marked in the owner's actual pending-axis list.
Marks remain until that child's source idle sweep. A local call or bridge
touching the physical pair must find no marks on either side; an idle sweep
releases only its own child's marks. Roles after a child's sweep and overlapping
marks are rejected. Used offsets must form a prefix, and the remaining suffix
is independently counted. This direct sweep checks the same strict boundary
condition as an interval audit through a different implementation.

The bank-padding and final all-family translation tail is recognized in the
pinned template but not expanded: all marks must already be released at the
end of each replica's 30-event projection. This audit does not claim coverage
of that tail's scalar or phase behavior.

Failure controls inject an intervening bridge touch, move a deadline before
its call, create a cross-call coordinate collision and a prefix hole, drop a
role, duplicate a helper, alter a width/family identity, change a source pin,
replace an integer coordinate by a float, and falsify the claimed idle suffix.
Each must fail at its named predicate. The touch/deadline controls alter the
abstract event stream after expansion to test the boundary logic; they are not
presented as alternate source-valid constructions.

## Pins, overlap and credit

- Main base: `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`.
- Selected at that base: Rohan Arun's PR1094,
  `0fc329d0bec93ca7cd288eaea1295172e8789810`, on Jeremy Kothe's PR1087,
  `589d1cedf5ef5f231182f4ec86408616311a8af0`.
- Selected conditional κ: `836330098538459/500000000000000000`.
- All consumed data paths and exact bytes: [SOURCES.json](SOURCES.json).
  No GitHub access, extraction, native compiler or supplier execution is needed.
- The seven-slot word is Josie Elliston's retained PR1091 input, copied there
  from Sagar Thakrar's PR1049 and bound to the PR1018 decompressed word digest
  `c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8`.
- The task-selector nonce, fixed scope, stop rule and live overlap check are
  recorded in [TASK.json](TASK.json).

The nearest predecessor is [PR1091's independent owner audit](../t16-owner-audit-seed67/README.md),
whose X2 predicate checks distinct pending-axis labels and whose source imports
the orthogonal-chart premise. The maintainer already applied that audit to
PR1094. This package independently verifies the cross-child algebraic premise
and supplies the full forward cut census; it claims no priority for the strict
window principle or the standard Gram lemma.

Pending PR1149 independently checks **local canonical-frame recursive ranks**
on PR1042, rather than these global pending-child spans and source-touch cuts.
PR1183 recounts pending-child disjointness for a changed T37 mixed-provider
construction; this package deliberately audits the selected PR1094/T16 input.
Live PRs and the discussion board were read before work and refreshed before
submission. Claims are advisory; no exclusive reservation is asserted.

Credit remains with Josie Elliston, Sagar Thakrar, Rohan Arun, Jeremy Kothe,
Hao Yan, Douglas Colkitt and the retained compiler/geometry/source lineage.
Prepared for Akiva with substantial OpenAI Codex assistance. New material is
Apache-2.0; original source files and their license/notice records are retained.

## Limits and handoff

This establishes a finite independence and chronological reservation statement
for the named inputs. It does not execute the scalar programs, prove dirty-state
restoration, validate spectator charts or phase adapters, replay emitted/native
controllers, certify precision/tape/invoices, price either supplier, or prove an
all-size compiler or the full multiplication theorem. The frozen local paid
profile is read as data, rather than independently recounted from every edge.
Those obligations remain with the inherited source checks and proofs.

A maintainer can optionally compose these predicates with a future owner-map
review after explicitly repinning its geometry, word and owner inputs. No
selected-record promotion, maintainer acceptance or PR closure is implied.
