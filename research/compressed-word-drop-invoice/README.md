# Exact paid cost of level drops in the compressed Cao word

**Scoped finite exclusion; no new kappa.** In the forward word from
[PR5350](https://github.com/CrocSwap/integer-mult-bounds/pull/5350), no single
level drop in the retained [PR5426](https://github.com/CrocSwap/integer-mult-bounds/pull/5426)
move class lowers the complete paid moment for `99/100 <= t <= 1`.
This completes the exact-cost and independent-graph checks requested in
[Nick Petalas's released handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362363).
That handoff already reported the corrected profile. This package does not
claim priority for that lead.

The 151-ADD compression changes the dependency graph, but it does not unlock
an improving single-level move in this class. This answers the compressed-word
question in PR5426. It gives a stop condition for that fixed search class.
It does not restrict a new scalar program or another centre interface.

## Exact result

The verifier reconstructs the compressed word from the five pinned inputs in
[SOURCES.json](SOURCES.json). Its compact sorted JSON SHA256 is
`7eb2f5c6e3291be8bc266f76076d49565e0687eb56311facede72b368ed48773`.
The historical native word is from
[Cao Yifan's PR4610](https://github.com/CrocSwap/integer-mult-bounds/pull/4610).
It is not the current selected PR6030 supplier.

The complete enumeration has 2,526 candidate levels and 518,315 contact plans.
Of those levels, 322 have no frame option and 2,196 have no acyclic plan.
Eight levels each have one acyclic plan. Every such plan has the paid delta

```text
rank:   1   4   5   8   9
count: -1  -1  +1  -1  +1
```

Thus every surviving plan raises the paid moment by
`9^t + 5^t - 8^t - 4^t - 1`. Productive endpoints do not change.
No decimal root search is used to accept the sign.
[RESULT.json](RESULT.json) retains every feasible field, removed frame,
contact assignment and exact histogram delta. It also retains the full
partition into dependency rejection, cycle rejection and feasible plans.

The centre-free control has 51 feasible plans. Their deltas are
`{1:-1,3:-1,4:+1}` or `{1:-1,4:-1,5:+1}`. Each is negative for `0<t<1`
by strict concavity. This control removes a required contact constraint;
it does not construct a legal supplier.

## Declared move class

The source is the exact forward PR5350 word on 632 fields. The operation set,
coefficients, native maps and field endpoints stay fixed. The twelve fields
that revisit a frame and the native-warp frames cannot be dropped.

Choose one intermediate level of one field. Move every contact at that level
to another frame already in that field's chain. A partner may acquire that
frame only if the resulting partner chain is nested and the endpoint bounds
hold. No other level is removed. Every contact uses one common frame.
Centre reads can move to a positive-dimensional frame of their source chain.
Centre deliveries remain at frame zero. Value dependencies, warp anchors and
the three retained phase barriers stay in force.

This is the source model in PR5426. The package imports its `Word` and
`options_for` definitions. It does not claim an independent reconstruction
of those semantics. It adds an independent static graph implementation and
complete exact paid accounting. A graph-feasible plan is not a native
implementation certificate.

## Why the finite check is complete

For each eligible level, the verifier iterates the full Cartesian product
of the allowed frame options. There is no plan cap. The first rejection rule
uses a necessary condition: if contact A must precede B, A cannot use a higher
frame than B on the same monotone field chain.

For every remaining plan, two algorithms decide acyclicity. The retained
PR5426 method uses a dynamic topological order. The new method reconstructs
the changed field edges and runs a full Kahn deletion scan. It retains no
topological order from a previous candidate. The two answers must agree for
every candidate that reaches this step. The scan includes operations,
per-field level entry/exit nodes, value dependencies and warp anchors.

For each feasible plan, the verifier recomputes the paid histogram of all
632 fields. It adds every centre-read transport at its new rank. The full
source histogram must first match `ARITHMETIC.local_paid`. Rollback must
restore that histogram after the enumeration. This prevents a local climb
saving from hiding the added centre charge or a partner's inserted frame.

## Exact tariff proof

Integer arithmetic checks `100^100 > 9 * 97^100`. Hence
`9^(-1/100) > 97/100`. If `1 <= r <= 9` and `99/100 <= t <= 1`, then

```text
r^t = r * r^(-(1-t)) >= r * 9^(-1/100) > 97*r/100,
r^t <= r.
```

Apply the lower bound to the positive terms and the upper bound to the
negative terms. The paid increase is greater than

```text
97*(9+5)/100 - (8+4+1) = 29/50 > 0.
```

The argument covers the stated closed exponent interval. It does not price
an unspecified caller. A changed productive boundary, centre mechanism,
word or multi-level move requires a new complete invoice.

## Reproduce

Python 3.12; standard library only. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/compressed-word-drop-invoice
```

The registered replay runs both normal and optimized Python. Each run checks
all declared source hashes, the generated word hash, all plans, both graph
methods, every complete feasible histogram and the centre-free control.
The replay also rejects a false climb rank, an inserted graph cycle, the
withdrawn cost expression and a cost expression that omits centre transport.
Expected markers are `PASS_COMPRESSED_WORD_DROP_INVOICE` and
`PASS_REGISTERED_RESEARCH_PACKAGE`.

The verifier reads committed evidence by default. To generate a separate
receipt, pass `--output` with a new file path. Existing output files are
not overwritten. The receipt has no timestamps or machine-dependent fields.

## Limits

This is a finite decision about one historical word and one move class.
The forward direction is checked. The backward direction, simultaneous
level removals, changed operation sets and changed centre delivery are
outside scope. No selected cold replay, native-phase replay, compiler,
precision, stock, BIT or outer admission is performed. The five selected
framework assumptions remain. No independent human or proof-kernel review
is claimed.

## Open next questions

A useful next task is a coupled removal that changes the dependency graph
beyond a single-level move. Start with a fully specified pair of removed
levels, restore every arbitrary input, and derive the complete paid profile
before a wider search. This package gives no positive budget for that task.
Another search of the same single-level class is not justified by this result.

## Sources and credit

- Mark / @Matarener supplied the question, move model, graph method and
  original-word result in [PR5426](https://github.com/CrocSwap/integer-mult-bounds/pull/5426).
- @ahrazzle supplied the compressed word in
  [PR5350](https://github.com/CrocSwap/integer-mult-bounds/pull/5350).
  Cinna Davis / @1337isnot1337 supplied its compression methods in
  [PR4692](https://github.com/CrocSwap/integer-mult-bounds/pull/4692).
- Cao Yifan / @intqwq supplied the native word and arithmetic in
  [PR4610](https://github.com/CrocSwap/integer-mult-bounds/pull/4610).
- @DreamingOfClouds supplied the fragmentation accounting in
  [PR5226](https://github.com/CrocSwap/integer-mult-bounds/pull/5226).
- Nick Petalas / @petalas supplied the unfinished census and corrected
  cost expression in the linked handoff. Its earlier expression was
  withdrawn; this package uses the reconstructed histogram.

Credit also Dugongue, zxv, Jacob Alan Sussman and the retained centre,
Clifford, native, scalar, compiler and analytic source authors.
Prepared by Ali Romman with substantial OpenAI Codex assistance.
New code and prose are Apache-2.0. Frozen predecessor files are unchanged.
