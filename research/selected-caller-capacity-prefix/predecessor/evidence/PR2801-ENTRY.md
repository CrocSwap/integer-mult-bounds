# Numerical entry state at the selected BIT adapter callback

At an adapter coefficient callback in unchanged PR2697 `Consumer.apply`, the
caller owns exactly **twelve additional index Words and no additional residue
Words** above its numerical entry residents. The twelve include the suspended
trace generator. Directory high matrices, validation Callbacks and numerical
extent temporaries have already been freed at this boundary.

Conditional on PR2781's adapter-local lifetime lemma, the resulting allowance
during each adapter coefficient call is **37,672 additional residue Words and
34 additional index Words above all `Consumer.apply` entry residents**. This
closes one caller-entry accounting gap in PR2781's handoff. It does not bound
other phases of `Consumer.apply` or establish a whole-node reserve or new kappa.

## Contract and source pins

The runtime source is Jose Manuel/jmbarrancoml's
[PR2697 at a53fdf4](https://github.com/CrocSwap/integer-mult-bounds/tree/a53fdf4bcbe33c6732f0bec1badc8c023380f9d1/research/selected-bit-node).
[SNAPSHOT.json](SNAPSHOT.json) pins nineteen unchanged runtime modules and the
complete predecessor [notice](vendor/NOTICE.md). These are the minimal top-level
import closure for `consumer.py`, with its actual root-level two-bank Layout
and packet engine. All bytes authenticate before any source module executes.
The loader compiles those bytes directly and ignores stale bytecode caches.

Fix the selected internal width range `64 <= n < 128`, dimension 64, a valid
compiled source/plan and chronological program/field prefix. Good ranks are
1 through 42. Arithmetic satisfies the predecessor's admitted odd-prime-power,
canonical-residue, word-margin and address contracts. Execution is sequential,
successful and has sufficient arena capacity. Residue and index arenas are
distinct. Use `observe=None`, or an observer that restores both numerical live
sets and values before returning. The fixed specification provider allocates
no numerical Words. Earlier completed coefficient calls restore their entry
live sets except for their owned result, which the stream frees before another
coefficient call. That successful-return contract for child coefficients is an
inherited premise, not a result of this adapter-only audit.

Let `B_R,B_I` count **all numerical slots live immediately before
`Consumer.apply`**. Include Ring and Context residents, parent size/depth,
unrelated caller matrices, suspended parent state and any other borrowed Words.
Do not set these quantities to zero. At every adapter `selected_coefficient`
entry, including each ADD's split and merge traversals, the live counts are

```text
residues = B_R
indices  = B_I + 12.
```

More directly, the caller-owned context increment is exactly `(0,12)` even
without assuming unrelated callees' cleanup; the equality for *all* live slots
uses that explicit cleanup premise. An observer retaining a new residue or a
child leaking a temporary would invalidate the equality.

Nick Petalas's [PR2781 at 9fdbd4b](https://github.com/CrocSwap/integer-mult-bounds/tree/9fdbd4b0429dbfcb4569f7768b66d318deacab6b/research/selected-adapter-numerical-lifecycle)
supplies the adapter-local excess `(37672,22)`. Its unchanged proof/contract is
retained at [evidence/ADAPTER-LIFETIME.md](evidence/ADAPTER-LIFETIME.md), pinned by
[DEPENDENCY.json](DEPENDENCY.json). This contribution inherits that lemma; the
new replay does not execute or independently recertify its numerical algorithm.
Combining the two entry conventions gives, during each adapter coefficient
lifetime,

```text
residues <= B_R + 37672
indices  <= B_I + 34.
```

Each live Word has `b+1` occupied non-LEFT symbols, including RIGHT. Each arena
also has a permanent template. Thus that phase's numerical occupied content is
at most

```text
(B_R + 37673)(b_R + 1) + (B_I + 35)(b_I + 1).
```

This excludes record/count/payload/control tapes, LEFT markers, retained erased
backing slots and Python heap objects. It is not a physical allocation bound.
The caller increment twelve is attained in the probes. No simultaneous or
whole-call sharpness claim is made for the composed allowance.

## Lifetime proof

The relevant numerical owners at a suspended adapter request are:

| Owner | Additional index Words | Source |
| --- | ---: | --- |
| `Consumer.apply` | 2, columns and current field count | [consumer.py](vendor/consumer.py), lines27 through33 |
| `Geometry` | 3, one, two and leaf cutoff | [numeric.py](vendor/numeric.py), lines14 and15 |
| Two-bank `Layout` | 3, core, extra and total | [layout.py](vendor/layout.py), lines13 through17 |
| Suspended adapter trace | 4, column, target, source and request coordinate | [trace.py](vendor/trace.py), lines136 through143 and160 through167 |

These twelve slots are distinct. `Geometry` aliases the borrowed columns/depth
rather than copying them. Event fields and suspended generator locals alias
the same owned words rather than allocating new ones. `Geometry.point` frees
its base and reversal intermediates before returning its owned point.

Directory production precedes Geometry/Layout execution. `produce` closes each
high Odometer and frees each decoded old Word before it returns, leaving only
serialized directory/count tapes. The validation Callback is closed before
`packet_engine.run`. Neither stage leaves a numerical high matrix or retained
Callback at an adapter site.

For good plans, `adapters` retains one column Word and yields a primitive owning
two point Words and the copied request coordinate. Forward and reverse adapter
passes have the same inventory. For fallback plans, the nonchild branch of
`execute` retains the same four Words. Any earlier leaf/pair iterator has fully
returned before that branch begins. In the first width range the column count
is one, but its numerical Word is still owned and charged.

`packet_engine.run` retains serialized data and Count/Counter tapes rather than
numerical Words. `stream_runner.action` calls the actual two-bank
`Layout.extents`; every numerical address/reversal/distance temporary is freed
before it returns. Its `multiply_atom_power` calls complete and close
`radix_power`, whose divisor, power, quotient and remainder do not survive.
The returned extents are independent count tapes, so they add no residue/index
slots at the callback.

In `stream.add_pass`, each `traverse` calls `prepare_coefficient` before it
receives the coefficient result or allocates x, offset or leading count. The first
traversal frees its coefficient and x before the second begins. Thus both
split and merge callback entries see the same caller-owned twelve slots and
no additional residue slots. Successful adapter return contributes one owned
result, subsequently freed by `traverse`. Prior child cleanup is kept as an
explicit premise instead of silently inferred from the adapter path.

The sum is `2+3+3+4=12`. Adding PR2781's separately pinned local allowance gives
`22+12=34` indices and the unchanged residue allowance. The proof uses source
lifetimes, not a finite enumeration as a universal argument.

## Replay and evidence

From the repository root, Python 3.12 and the standard library:

```sh
uv run --python 3.12 --no-project python -I -Werror -B \
  scripts/research_package.py --package research/selected-adapter-caller-entry
```

`verify.py --emit` prints a fresh receipt without writing. Ordinary replay
compares the complete typed [RESULT.json](RESULT.json). Direct `verify.py` and
optimized `test_verify.py` also run in a Git-free export.

The probes enter the actual pinned `Consumer.apply`, produce and validate a
complete source prefix, and execute every event of the compiled source trace.
They inspect numerical live sets at **every adapter trace event**. One example
of each adapter kind/orientation also executes actual `Layout.extents` and
`stream_runner.action`, with two callback samples corresponding to split and
merge. Literal cell scans check the occupied-content formula at those samples;
entry live sets, values, numerical heads and input tapes are preserved.

This is an instrumented numerical-lifetime check. Serialized prefix copying,
record-head movement and Boolean payload traversal are abstracted, and the
coefficient body returns a placeholder owned Word. Child bodies and nonadapter
payload actions are abstracted. The two callback samples exercise the closure
at the real action boundary; they do not execute `stream.add_pass`'s payload
loops. The unchanged source ordering in `stream.py` supplies the split/merge
lifetime argument. No complete selected Boolean run, numerical coefficient
correctness or movement-cost measurement is claimed.

Four fixtures cover complete 64-dimensional good ranks 1 and 42, a fallback plan,
widths 64 and 127, chronological depths 0 and 4, and three or seven unrelated
borrowed Words in each arena. F3 with a single high lift makes the numerical
boundary finite to execute. These are explicit source-contract fixtures, not
selected-catalogue membership or the outer large-prime coupling.

Controls undercharge the index context by one, retain an unpriced index Word
at the callback, corrupt source bytes, alter original source paths, remove a
source pin and mistype/change the receipt. A trace-capacity control checks both exact acceptance
and exhaustion with suspended-generator cleanup. Numerical failure cleanup is checked
before fixture teardown can erase evidence. Acceptance uses `ValueError`, so
optimized Python does not disable it.

Registered CPython 3.12.15 replay passes on macOS 27.0.1 arm64, including ten
optimized controls. The workflow suite has 67 passes and seven skips. Exact Git
byte comparisons authenticate every export; scoped Ruff lint/format and a
Git-free relocated optimized-control run pass. The complete receipt contains
213,944 source trace events, 48,476 adapter sites, 38 callback samples and 76
occupied-cell scans.

## Scope and engineering

The original recursive-interface draw and changed scope are recorded in
[TASK.json](TASK.json). The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18959666)
takes PR2781's caller-entry handoff, leaving the separately claimed child branch,
physical bank codec and compatible-row-padding work to their existing scopes.
No frozen predecessor, selected record or production verifier is modified.

Build the Lever led to the authenticated source-state probe. Prove It Works led
to actual suspended generators, callback-boundary cell scans and cleanup checks.
A separate internal source review verified the inventory and required explicit
arena, observer and prior-child-cleanup conditions. No independent human or
formal-kernel review is claimed.

Power of Ten limits fixtures to dimension 64, ranks 1/42, depths 0/4, two bounded
arenas, four cases and 200,000 trace events per case. Each new function fits 60
physical lines. Managed-runtime deviations to rules 3/8/9 cover Python heap
allocation, nineteen authenticated module executions and temporary replacement
of seven fixed methods/functions at documented numerical-neutral seams. Source
bytes authenticate before execution, fixture limits bound live replay data,
ExitStack restores methods on every exit, and the manifest bounds process
runtime. Scoped Ruff diagnostics include security checks; the sole S102 annotation
covers authenticated frozen-source execution. Git SHA1 is used only as a blob
identifier beside SHA256. This compensates for checker resource risks, without claiming fixed
heap allocation or physical tape costs. Replace these seams when a physical
caller compiler is available. Frozen source loops are input-bounded; source
functions and their legacy style are preserved rather than rewritten.

Submission overlap at 22:15 UTC covers 727 open PRs and 1,440 Discussion,
comment and reply records with complete pagination and no warnings. The nearest
child-coefficient claim explicitly excludes surrounding caller residents.
Canonical main refreshed to `df801f6da7b9aa8e01bd35decde7b1b1d45eec08`; relevant
guidance, selected record, runner and both dependency heads are unchanged.
TASK.json records exact coverage; searches exclude arbitrary diffs and
unpublished work.

The expansion decision is narrow and finish this boundary audit. The result
cannot be used as a complete `Consumer.apply`, first-node or all-size reserve
allowance. In particular, directory production and stream arithmetic have
numerical peaks outside the coefficient lifetimes addressed here.

## Open next questions

1. What numerical peak occurs in the remaining caller phases, including initial
   directory production, stream ADD arithmetic and child coefficient calls?
   Combine the separately claimed child result with Odometer/stream lifetimes
   under the same all-entry-residents convention. Missing phase inventory and
   a joined caller ledger block a complete reserve conclusion.
2. Can the joined inventory fit the fixed physical banks with the required
   movement cost? Bind the public numerical-bank codec to one complete phase,
   including slot identities, templates, markers and erased backing slots.
   Physical placement/movement and the complete phase inventory remain blockers.

These questions and first steps are also structured in TASK.json.

## Credit

Nick Petalas, Apache-2.0. Jose Manuel/jmbarrancoml supplies the unchanged PR2697
caller and its retained source, control, normal-form and hosting lineage; the
complete predecessor notice is preserved. Nick Petalas's PR2759/2770/2778/2781
supply the primitive, evaluator, constructor and adapter-local lifetime results.
David Arias's earlier PR2753 already supplies a coarser all-size logical
inventory. This contribution adds the exact surrounding adapter-entry context
and its conditional composition, not a first complete numerical reserve.
