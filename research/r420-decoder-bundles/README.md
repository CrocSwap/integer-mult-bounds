# Restored stars in the R420 decoder totals

**Finite bit-circuit construction. No new kappa.** Eleven disjoint restored
stars reduce the nine phase-A decoder totals in eumemic's PR543 R420 word from
321 to **257 binary XORs**, including preparation and restoration. Rebuilding
literal reverse cleanup doubles the saving to **128 native ADDs**, from 26,916
to **26,788**. No helper, source-access operation, frame move, copy, restoration,
or recursive child is omitted from the comparison.

This extends the disjoint-pair mechanism in
[PR708](https://github.com/CrocSwap/integer-mult-bounds/pull/708) at
`2ec522a466ec448f148d4355dc43b51c0ef1e0b5`. Its frozen recipe saves 114 native
ADDs. The present recipe saves 14 more by allowing a helper to accumulate several
leaves. This is a different circuit class, not another pair-matching seed. It
does not prove that either recipe is globally optimal.

## Base and accepted result

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The selected record at this base is conditional
`kappa = 51110230636731/31250000000000000 = 0.001635527380375392`.
Its complex supplier is PR626 at `660de893d27bb7abd1d5b01b1640207528a5c851`;
its bit supplier is PR543 at `2065fe4f72a914d907f1046603f5a36f17018535`.
See the actual [selected review](../../docs/research/community-k492-review.md)
and [bit construction](../e8-bit-r420/README.md). Historical frontier statements
inside the latter are not claims about the current selected result.

Only this research directory is added. The selected frontier, original supplier,
`upstream/`, and other concurrent packages are unchanged. Source and canonical
word hashes are in [SOURCES.json](SOURCES.json); compression headers are not used
to determine mathematical equality.

## Reproduce

Python 3.10 or later, standard library only:

```sh
python3 -B research/r420-decoder-bundles/verify.py
```

Expected final line:

```text
PASS_R420_DECODER_BUNDLES decoder=321->257 native_ADDs=26916->26788 saved=128 columns=660 controls=8 no_new_kappa
```

The command regenerates the nomination and circuit in memory, verifies all
pinned inputs, and compares every field of [CERTIFICATE.json](CERTIFICATE.json).
It invokes the unchanged PR543 E8 label, frame, dirty-column and H1-H5 checker,
then a separate set-valued interpreter in [audit.py](audit.py). Eight negative
controls cover omitted restoration, an uncancelled total operand, stale literal
cleanup, unpaid frame-zero preparation, a retained helper used as scratch,
overlapping stars, missing dirt compensation, and a changed source word.
Optimized Python is refused because inherited verification uses assertions.

For a fresh native nine-stage replay, also install a C++17 compiler and Boost
headers and choose two output directories that do not yet exist:

```sh
python3 -B research/r420-decoder-bundles/verify.py --output /tmp/r420-bundles-words
BOOST_INCLUDE=/path/to/boost CXX=c++ python3 -B research/r420-decoder-bundles/native.py \
  /tmp/r420-bundles-words/baseline.json.gz \
  /tmp/r420-bundles-words/candidate.json.gz /tmp/r420-bundles-native
```

Expected final line:

```text
PASS_R420_DECODER_BUNDLES_NATIVE_NINE_STAGE ADDs=26916->26788 columns=1380 controls=18/18 for both words
```

The runner checks canonical word identity before export and pins all six native
dependencies. [NATIVE.json](NATIVE.json) records the executed local replay with
Python 3.14.8, GCC 16.2.0 and Boost 1.85.0. Both words pass all 1,380 formal
columns, nine COPY/ERASE lifecycles, and all 18 omitted-bridge rejection controls.
Exported records fall from 29,874 to 29,746. The payload bound rises from 100 to
103 bits and still satisfies the inherited strict requirement `< 104`.

## Circuit and exact cost

A star has hub `a` and leaves `L`. All are distinct non-retained helpers already
used by the nine totals. At FULL, prepare

    a <- a XOR XOR(L).

In every total whose original source set contains `a`, toggle all members of `L`
in its source set. Leave other totals unchanged. After the nine totals, undo
the preparation. No star register is a total destination; different stars have
disjoint registers. The new total therefore reads exactly its original linear
form on arbitrary inputs, including arbitrary helper dirt. Every star helper
returns to its value before the totals, so the entire A operator is unchanged. The
existing D compensation still applies, and C is rebuilt as the literal reverse
of all A/B gates whose destination is a source or helper. Thus the original
H1-H5 interface applies without amendment.

Write `n_a` for the number of totals reading `a` and `n_ab` for the number reading
both `a` and `b`. Preparing and restoring an edge costs two binary ADDs. Toggling
`b` in the `n_a` affected totals removes it `n_ab` times and adds it
`n_a - n_ab` times. The fully paid phase-A saving per leaf is exactly

    w(a,b) = 2*n_ab - n_a - 2.

Disjoint stars make these savings additive. The selected 44 edges save 64 ADDs
in A and 64 in C. The decoder circuit has 44 preparation ADDs, 169 total ADDs,
and 44 restoration ADDs, summing to 257. Every selected register originally
climbed to FULL during these totals. Moving that climb earlier changes no
ordered register frame path. Both interpreters verify this on the literal word.

There is also a strict small-class separation. On registers `[515, 489, 347]`,
the two hub-515 edges each have weight 2; the other four oriented edges each
have weight 1. The star saves four ADDs in A. A disjoint-pair recipe on these
three registers can choose at most one edge and saves at most two. The verifier
enumerates all six oriented edges. This statement does not bound pair recipes
that use additional registers.

## Cost boundary and search coverage

| Quantity | Original | Restored stars |
|---|---:|---:|
| Binary decoder ADDs, including preparation/restoration | 321 | 257 |
| Complete native ADDs, including C and D | 26,916 | 26,788 |
| Helpers / retained copies | 420 / 9 | 420 / 9 |
| Scalar MOVE count / rank mass | 2,940 / 5,112 | 2,940 / 5,112 |
| Forward positive scalar maximum | 144,651 | 235,233 |
| Inverse positive scalar maximum | 2,270,064 | 3,088,728 |
| Nine-stage payload prefix bits | 100 | 103 |

The paid histogram remains `{1:1320, 2:1440, 4:60, 5:120, 8:9}`.
Unchanged recursive ranks give no recursive-moment gain by themselves. The
larger positive envelopes must be carried into any complete hosted invoice.
The #626 selected composition is complex-bound; these fewer local ADDs do not
establish a stronger exponent or a practical runtime speedup.

Assignment seed **19** was drawn from operating-system randomness. The search
scores all 6,320 oriented edges among the 80 eligible operands; 463 have positive
weight. One seed-19 ordering resolves ties. At each step it chooses the hub with
largest total positive weight over unused leaves and removes that whole star.
It stops when no positive edge remains on unused registers. Exactly one packing
was attempted: eleven stars, 44 edges, and 25 unselected operands. There is no
solver, restart, or optimality claim. Before nomination, an optimistic
common-incidence screen visited all 82,160 three-operand subsets. That score was
discarded because rows reading only part of a bundle must also be charged; no
word was constructed from that screen. The exact edge formula above includes
those costs. The frozen
[recipe](recipe.json) and its regeneration are checked byte-for-value.

The full hosted-parent construction, global finite invoice, changed-word outer
assembly, and remote CI were not run. Neither `make verify` nor a new selected
frontier replay is claimed for this isolated research addition. All-size
compilation, common-label/mutable-basis realization, whole-owner hosting,
normalized residuals, precision/tape/exact recovery, and analytic transfer
remain inherited assumptions. Finite checks do not formally prove the full
multiplication theorem.

## Attribution and concurrent work

The circuit is based on eumemic's PR543 R420 word and PR493 carrier skeleton,
Dylan Crow's bitE8 format and exporter, DreamingOfClouds' retained totals and
nine-stage pricing, Zhihao Chen's scalar interface, and the common-label and
whole-owner lineage credited in the original supplier. Preserve those notices.
PR708 supplies the immediate pair-sharing idea, relative set-replay precedent,
and the attributed native runner adapted here. Its sources are pinned above;
its pending review status is not treated as acceptance of this result.

Concurrent PR686/694 optimize frame-zero compensation, PR670/674/688 change
phase-B blocks, PR691 changes a phase-A quad, and PR713/716 change target bases
in D. None is imported or composed here. PR661's negative result fixes the B
gate stream and does not prohibit this A/C rewrite. The local sprint claim and
final overlap refresh are recorded in [CLAIM.md](CLAIM.md).

The final refresh found Chinmay Khaladkar's
[PR748](https://github.com/CrocSwap/integer-mult-bounds/pull/748), head
`0ccc0b425d2b9667108d3a0918a5cfa0aa7a5861`, which reports a larger 244-ADD
saving by changing one total's source representation and recomputing D for its
changed helper-dirt map. The present contribution preserves the complete A
operator and D, and adds fresh nine-stage C++ replay. It is not an overall
savings record. PR742's shared target donors and PR733's two-sided D basis also
give larger whole-word savings in different circuits. None of these concurrent
recipes is imported or assumed composable.

Prepared for **Sagar Thakrar, @thakrarsagar**, with substantial **OpenAI Codex
assistance** in construction, proof, checker implementation, independent replay,
and packaging. Separate AI workers checked the star identity, set-valued replay,
and native checker path. No independent human review is claimed. This new work
is under the repository's Apache-2.0 license.
