# Exact cost of minimum-envelope three-source XOR fanout

**Scoped uniform theorem; no new supplier or kappa.** For every `n >= 2`,
adding the parity of three restored helpers to `n` dirty targets requires
exactly **`2n+2` unit XORs** when the forward positive envelope is at most four.
This remains true with any finite number of additional dirty auxiliaries,
arbitrary target feedback and arbitrary circuit length. The attaining word
also has reverse envelope four.

PR [#1520](https://github.com/CrocSwap/integer-mult-bounds/pull/1520), by
Hanson Sun (@bbMisk), already gave the eight-gate, peak-four construction for
three targets and the complete six-register cost/precision frontier. We
generalize its construction and replace its shortest-word census as the
peak-four lower-bound argument with a structural proof valid for all target
counts and extra dirty registers. We do not claim a new unconstrained XOR
minimum or repeat the finite 3x4 census in PR1557.

## Model and theorem

There are helpers `h0,h1,h2`, targets `y0,...,y(n-1)`, and any finite number of
auxiliaries. Initially every register is arbitrary and independent over F2
(equivalently any F2 module). The complete endpoint restores every helper
and auxiliary and maps each target to `y_j + h0 + h1 + h2`.

Every gate is an ordered `r_d ^= r_s`, with `d != s`, charged one unit. There
are no free permutations, basis changes, clean roles, COPY/ERASE operations,
recursive calls or frame changes. All roles use one common zero frame.
The positive lift replaces each XOR by integer row addition, starting from
the identity matrix. Thus every initial bound is one; the envelope `F` is
the maximum row sum over every prefix. All entries are nonnegative and
monotone, so the final maximum is also the prefix maximum. `B` is the same
quantity for the reversed word. This is a local majorant, not word size.

**Theorem.** For `n >= 2`, the minimum gate count among these circuits with
`F <= 4` is `2n+2`. Every such endpoint has `F >= 4` and `B >= 4`. The minimum
with `B <= 4`, or with both envelopes at most four, is also `2n+2`.

### Lower bound

Let `P` denote the nonnegative integer transfer matrix at a prefix. Reduction
modulo two is exactly that prefix's binary transfer. Each row retains its own
initial diagonal entry at least one, and every entry can only increase.

1. A final target row has four required odd entries: its own target column
   and all three helper columns. If `F <= 4`, those four entries must each
   equal one and every other entry must be zero. This also proves `F >= 4`.
2. A gate into a target cannot use another target or auxiliary as source.
   The source row contains its own original column with positive coefficient,
   which would permanently pollute the destination's final row. A helper
   source contaminated by any nonhelper column is likewise unusable: if that
   column is the destination's own, its already-present diagonal one would
   become at least two; otherwise a forbidden column becomes positive.
   Therefore every target gate uses a helper row containing only helper
   columns, and its contributions must fit within the three unit entries.
3. No helper row can ever contain all three helper columns positively.
   At the restored endpoint its own helper column is odd and at least one,
   while the two other columns must be even. If both had ever been positive,
   monotonicity would make each at least two at the end, giving row sum at
   least five, contrary to `F <= 4`. Consequently no single incoming gate
   can supply all three helper columns to any target. Each target needs at
   least two incoming gates, for at least `2n` target-destination gates.
4. If any helper is written, at least two helper-destination gates occur.
   Exactly one would change that helper by a nonzero binary source row;
   all prefix matrices are invertible because the allowed gates are
   invertible, so no source row is zero. With no later write to that helper,
   restoration would fail. These helper gates are distinct from target
   gates, giving at least `2n+2` total.
5. If no helper is written, every usable helper stays a single original
   basis row. Each target then needs at least three incoming gates, giving
   `3n >= 2n+2` for `n >= 2`. Auxiliary gates can only add to either count.

This proves the lower bound for arbitrary words; it is not inferred from the
finite checks below. In particular, extra dirty storage and target feedback
do not evade the positive-row obstruction.

### Attainment and reverse direction

Use the following paid word, leaving auxiliaries untouched:

```text
h0 ^= h1
for each j: y_j ^= h0
h0 ^= h1
for each j: y_j ^= h2
```

It restores the helper, adds all three original helper values to every target,
and costs `1+n+1+n = 2n+2`. Its final positive helper bounds are `(3,1,1)`;
each target bound is four and every auxiliary bound remains one. Reversing
the word gives the same final bounds. The endpoint is an involution, so
reversing any admissible word preserves its contract and gate count while
exchanging `F` and `B`. The forward theorem therefore gives the reverse and
simultaneous claims. For the excluded case `n=1`, three direct gates suffice;
the stated formula four would be false.

For four targets this proves the peak-four cost is ten. The familiar
eight-gate gather/fanout/restore word has both peaks five. Its unconstrained
minimality on exactly seven registers is prior finite evidence in PR1557,
not a new claim or an assumption of this theorem. No unconstrained minimum
with additional auxiliaries is asserted here.

## Reproduce and validation boundary

```sh
python3.12 -I -B scripts/research_package.py --package research/three-source-envelope-floor
```

The registered standard-library checks reconstruct the witnesses and their
exact binary endpoints and integer lifts, verify both directions on several
target/auxiliary counts, and independently enumerate full dirty truth tables
for small instances. Controls reject missing restoration, missing target
updates, incorrect cost/peak claims, malformed gates and the `n=1` extension.
Historical source pins identify the predecessor descriptions used for
attribution; those descriptions are not runtime proof inputs. These finite
checks support the construction and illustrate the
proof's hypotheses; they do not turn the prose uniform proof into a formal
kernel theorem. No full supplier replay or precision guard admission is claimed.

## Provenance, usefulness and limits

The base is `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision four.
The task nonce is `54ac0d737844a7825d9d6cbcee723dd8`; the prescribed PR1062
star verifier passed. `TASK.json` records the changed scope from the already
covered semantic H2/K repair to a positive-envelope interface bound. The
claim is [on PR1520](https://github.com/CrocSwap/integer-mult-bounds/pull/1520#issuecomment-6196577531).
`SOURCES.json` records exact predecessor byte identities and heads.

The theorem provides a stopping rule for searching peak-four parity fanout:
allowing more dirty helper space cannot beat the displayed cost in this
model. Unequal incoming bounds, clean initialized roles, nonmonotone bounds,
COPY/ERASE and nonzero frames are outside the theorem. The selected complex
supplier remains binding; this result neither admits a new bit supplier nor
changes the selected kappa. A hosted replacement must pay all surrounding
costs and pass its own chronological, native and precision checks.

## Open next questions

Can an actual native hosted occurrence benefit from replacing a peak-five
gather/fanout/restore word with the peak-four word after paying the extra
XORs? First locate a pinned occurrence with its real incoming bounds and
interior observations, then replay the complete surrounding word. No such
occurrence or completed invoice is established here. For unequal positive
bounds, the simple all-ones exact floor need not describe the correct objective.

## Credit and license

Credit Hanson Sun (@bbMisk) for PR1520's three-target precision frontier and
construction; @commdata2338 for PR1306's zero-frame feedback model and
substitution lemma; PR1557 for the seven-register finite census; and the
PR1062/PR555/PR589 contributors for the bit-supplier and positive-envelope
lineage. No priority is claimed for elementary monotone matrix arguments.
Prepared for @ywz65 with substantial OpenAI Codex assistance in proof,
implementation, testing and writing; no independent human review. New work
is Apache-2.0.
