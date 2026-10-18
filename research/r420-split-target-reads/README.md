# R420 split target reads cannot lower the paid moment

**Scoped negative result, no new κ.** In the selected PR543 R420 bit word,
splitting the final three-source target gates into separately framed reads
does not reduce the local paid recursive moment. This covers all six source
orders and every admissible real subspace at each read, with the earlier
schedule and full-frame cleanup fixed.

Each target has eight legal schedules. Six have the original profile. Two
have strictly greater moment for every exponent `0 < p < 1`. The 120 targets
use disjoint source registers, so the result covers all `8^120` simultaneous
choices, without enumerating that Cartesian product. It also permits
interleaving reads of different targets within this final segment.

## Reproduce

From the repository root, with Python 3.9+ and no third-party packages:

```sh
python3 -B research/r420-split-target-reads/check.py
python3 -B research/r420-split-target-reads/independent_check.py
```

The first command checks the source payload, reconstructs the certificate,
replays all 660 symbolic dirty-input columns for both the original word and
the word using every early read, and runs four negative controls. Expected:

```text
PASS_R420_SPLIT_TARGET_READ_BOUND targets=120 schedules=8^120 controls=4 kappa=unchanged
```

`independent_check.py` uses rational Gaussian elimination and exhausts all
`6 * 2^3 = 48` candidate schedules per target. It does not import the primary
checker or predecessor checkers. The primary checker uses integer row
elimination and the two possible local profiles. Neither implementation
samples floating-point exponents to establish the inequality below.

## Scope and provenance

The exact base is `66849e1475c930fd7732b1a0067ffee7e1e95f60`. Its selected
conditional κ is `51110230636731/31250000000000000`, or
`0.001635527380375392`, from PR626 with the PR543 bit supplier. The selected
certificate points to `research/community-k492-audit/pr626/replay/ASSEMBLY.json`
and `docs/research/community-k492-review.md`. This experiment follows the
actual bit source, `research/e8-bit-r420/data/bitE8mut-r420.json.gz`, from
PR543 commit `2065fe4f72a914d907f1046603f5a36f17018535`.

PR661 by Tuomo Kiiskinen / yuj1r0, inspected at
`9ca7aa3ab0a3260a2f36ac86b9911a31fd88bd89`, proves fixed-gate phase-B frame
optimality. It preserves each gate's operand list. Here a three-source gate
becomes three single-source gates with potentially different frames. This
is a separate family outside that claim, and the present result closes
only this additional case. No code or certificate from PR661 is imported.

The experiment changes no scalar source value, helper count, decoder,
COPY, earlier gate, final frame, or cleanup gate. It adds no source-access
operation, helper or recursive child beyond the frame climbs counted below.
The same three XORs execute in a different grouping. Every source still
reaches the full frame in C or its final climb. The 420 helpers and nine
retained-total COPYs are unchanged. No alternative owner map or assembly is
claimed. See `SOURCES.json` for byte pins and `CLAIM.json` for the assignment,
candidate selection and overlap checks.

## Complete geometry argument

The final 120 B gates are `B[717:837]`, one per target. The checker establishes
the following facts from the exact eight-dimensional label vectors:

1. A target enters this segment at a rank-two cell `C` and must end at its
   fixed rank-seven hyperplane `H`.
2. Its three sources enter at distinct rank-six subspaces `S0, S1, S2`
   contained in `H`. Each pair spans `H`.
3. Exactly one source space contains `C`.
4. The 360 source registers are distinct, none is a target, and each appears
   once in this segment. Their fixed endpoint is rank eight. Every C-phase
   gate has the full frame.

At a single-source read the common gate frame `F` must contain that source's
rank-six space and the target's current frame. The target's monotone path
requires `F` to lie inside `H`. Thus `F` is either the source space itself
or `H`: a rank-six space has codimension one in `H`. This accounts for all
real subspaces, including ones outside the retained frame catalogue.

The first read can use rank six only when its source is the unique space
containing `C`. There are two orders with that source first. After this
read, either remaining source joins the target's rank-six frame to `H`.
The remaining reads therefore use `H`. In every other schedule all reads
use `H`. There are six all-`H` orders and two early-read orders per target.
Disjoint register sets make these choices independent across targets.

## Full cost of an early read

A climb of dimension `d` contributes `d^p` to the unnormalized recursive
moment. In the inherited price engine, the exponent is `p = 1 - a` and the
common positive normalization is `m^(a-1) / W`. The child-count fallback
term is also unchanged here. These statements concern the paid moment,
not a new admission theorem for a physical implementation.

Count the target and its three sources, including their later full-frame
cleanup:

| Schedule | Target climbs | Source climbs through cleanup | Combined profile |
|---|---|---|---|
| Original or all reads at `H` | `5` | three copies of `1, 1` | `{1: 6, 5: 1}` |
| One early rank-six read | `4, 1` | one `2`, two copies of `1, 1` | `{1: 5, 2: 1, 4: 1}` |

The exact profile change per early read is
`{1: -1, 2: +1, 4: +1, 5: -1}`. Both profiles have seven paid calls and
rank mass eleven. The changed pair of ranks is `(5, 1) -> (4, 2)`.
Strict concavity gives

```text
2^p - 1 > 5^p - 4^p,             0 < p < 1,
2^p + 4^p - 1 - 5^p > 0.
```

For example, integrate the strictly decreasing derivative `p*x^(p-1)`
over `[1,2]` and `[4,5]`. Their equal lengths give the first inequality.
This proves the sign for the full open interval; finite exponent samples
are unnecessary. The difference is zero at `p=0` and `p=1`, which are
outside the strict claim.

The complete baseline local profile is
`{1:1320, 2:1440, 4:60, 5:120, 8:9}`. Taking all 120 early reads gives
`{1:1200, 2:1560, 4:180, 8:9}`. Both have 2,949 paid calls and rank mass
5,112. All fixed A/D/scatter/C/final work and the nine rank-eight COPYs are
included in this recount. If exactly `k` targets use the early read, the
moment increases by `k * (2^p + 4^p - 1 - 5^p)`.

Seed 3 selects target 3 as the worked example. Its register is 123, its cell
is frame 145, and `H` is frame 555. Sources 10, 290 and 340 enter at frames
380, 383 and 384; only source 10 can be read early. These identifiers and a
digest of the complete geometry census are retained in `CERTIFICATE.json`.

## Checks and limits

The primary replay checks exact F2 identities with arbitrary initial bits
in every register. It rejects an incompatible source read at rank six, a
missing target read, source reuse that would invalidate independent choices,
and a cost certificate omitting the rank-two cleanup. The independent
checker tests the entire finite frame/order domain by a different method.
`VALIDATION.json` records execution results and checks that were not run.

This is a proof for the stated finite family, supported by exact geometry
and scalar replays. It is not a formal Lean proof of the multiplication
theorem. It does not cover changes to earlier frames, source circuits,
decoder totals, helper allocation, non-monotone frames, cleanup, or the
recursive interface. It does not claim global bit optimality or a new κ.
All inherited all-size/compiler/common-label/mutable-basis, pooled hosting,
residual, precision/tape/exact recovery and analytic assumptions remain.

## Credit and license

The R420 word and its interleaved cleanup are eumemic's PR543 contribution,
building on the PR493 carrier skeleton. Dylan Crow's PR370 supplies the E8
decoder; DreamingOfClouds' PR510 supplies the nine-stage pricing lineage.
PR589 explores a different punctured bit word and is not a dependency of
this experiment. Tuomo Kiiskinen's PR661 supplied the fixed-gate boundary
that motivated this distinct split-read question. Concurrent PR670,
PR674, PR686, PR688, PR691 and PR694 change scalar circuits or compensation;
their constructions are not imported here.

Prepared for Sagar Thakrar / thakrarsagar with substantial OpenAI Codex
assistance, including a separate Codex worker for independent exact
enumeration. New files are under the repository's Apache-2.0 license.
Original supplier files and `upstream/` are unchanged.
