# Compose the restore edit and improved rank-seven packing

This package composes Jeremy Kothe's [PR3015](https://github.com/CrocSwap/integer-mult-bounds/pull/3015)
restore edit with the improving allocation journal from
[PR3018](https://github.com/CrocSwap/integer-mult-bounds/pull/3018).
The complete conditional moment endpoint increases from
`0.0017291509735342244286952...` to `0.0017291512039830184429986...`.
The certified root gain is between `2.304487940143033e-10` and
`2.304487940143035e-10`. The fresh native, complete finite admission and modern outer release pass.
The released conditional saving is
`0.001729151203983018442998 - 10^-46 - 10^-70`, exactly
`230448794014303/10^24` above PR3015. The selected record is unchanged.

The contribution closes PR3018's explicit composition/admission handoff. It uses
canonical main `d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.
The exact source heads are PR3015 `e244296debb45fe6f4da84d29e4d64fbab55fda0`
and PR3018 `ca7113157d7c959fdfa9d7cd17ef92d3877070d0`.
[Task and scope](TASK.json), [live-input pins](SOURCES.json), and
[exact vendor blobs](VENDOR.json) record the sources. The
[canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-18979353)
records coordination.

## Why the changes compose

PR3015's R1 restore edit changes the local profile of both providers by
`-2 H1 + H2` per call. It preserves every ordered helper width and its entrance
and endpoint, the order and dispatch, source windows, and the 91 private-buffer
namespace. Its inverse cleanup is rederived, so cleanup gate bytes do change.

PR3018's 103-row journal moves 44 roles, with the scalar words fixed. Its
complete effect is on idle children. With `H_r(b)=r(73/r)^b`, it changes the
bill by `4 H1 + 4 H3 - 6 H5 + H14`. The unchanged retained exact sign proof
makes this strictly negative for every `0 < b <= 1/100`, including both roots.
The two changes therefore add without paying either saving again.

The complete composed profile is

```text
{1:1644352, 2:470862, 3:159472, 4:71928,
 5:13710, 8:5328, 14:1, 48:28190}.
```

The finite moment gate is `sum_r n_r H_r(b)/(73*896*74) < 1`.
The source outer chain chooses its guarded saving below that root.
All 666 calls and 271,728 indivisible helper roles are included. Rank mass is
4,816,512. Physical stock is `66,304 + 408 + 8 + 91 + 2 = 66,813` families.
The finite checker verifies the exact R1 rational identity, both literal edited
words and inverse cleanup, the original and composed owner geometry, unchanged
ordered widths and complete local-plus-idle invoices. It retains PR3018's
source-authenticated geometry and interval implementations; it does not present
those implementations as a newly independent checker.

The inherited fixed-inventory fractional cap from PR3015 is about
`0.001729152756004330934535`. The composed endpoint is below it by about
`1.5520213125e-9` and realizes over 99.99991% of it. This package does not
recertify the fractional optimum or establish integral optimality.

## Reproduction

The bounded registered check needs Python 3.12 and its standard library:

```sh
uv run --python 3.12 --no-project python -B scripts/research_package.py \
  --package research/rank7-restore-packing-composition
```

The complete fresh source chain is separate. It exports authenticated Git
sources into a new workspace and uses PR3015's original twelve-stage recipe.
The only changed recipe argument is the complete admission's `--fill`, which
receives the journal-derived allocation. The source comparator remains its
pinned PR2969 record; a separate exact check requires the released result to
strictly exceed PR3015's pinned claim.

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git \
  e244296debb45fe6f4da84d29e4d64fbab55fda0 \
  e2ca469b08385d3d5e29a918d66dbefaf889e9f3 \
  e62d3eb9005117d82a9babcfa937ecc53237c490 \
  b74b25f3ccc84c16e1a801d73b2f47e5ea764c78 \
  a027b0f6fdb0ab2b42ba10fc31b53960166bf2bf \
  224bd5e56041c40078ff6b5fa7393733a215de5c \
  51309592971e3b5be935599eed2a95404dc7781e \
  18d03c447886895ef9abf888398178e0428533ca \
  e9307b48d7d1b690939935ecef0f8e524e6d92f4
uv run --python 3.12 --no-project \
  --with numpy==2.4.5 --with scipy==1.16.1 --with sympy==1.14.0 \
  --with mpmath==1.3.0 --with gmpy2==2.3.2 --with psutil==7.2.1 \
  python -B research/rank7-restore-packing-composition/reproduce.py \
  --repo . --work /tmp/restore-packing-complete
```

The workspace must not exist. Full process-group cleanup requires POSIX.
`--dry-run` authenticates and materializes the exact recipe without running its
mathematical stages. Inherited source validators require assertions, so the
full wrapper refuses optimized execution. The bounded finite check passes
with and without optimization. Exact frozen vendor bytes, including CRLF JSON,
are preserved by the package's attributes.

## Evidence and publication checks

[The fresh result](evidence/COMPOSITION-RESULT.json) records 648.30 seconds
on macOS arm64, CPython 3.12.15, with one source job. It includes a fresh
retained bootstrap and two fresh current-provider native chains, then complete
owners, parent lift, rebind, strict discovery, independent outer-ledger checks
and release. The current native stage authenticates and reuses the retained
native/parent evidence just produced by the same bootstrap.
[Admission](evidence/ADMISSION-RESULT.json), [native receipt](evidence/NATIVE-RECEIPT.json),
[outer claim](evidence/OUTER-CLAIM.json), [release](evidence/RELEASE-RECEIPT.json)
and the exact logs are retained. Receipts contain the actual run's paths.

Sixteen mathematical/behavioral tests pass, with four additional rejecting
controls on the published receipt relations. The registered replay repeats
the finite check and authenticates those stored relations; it does not rerun
the full chain. Canonical decompressed fill content binds the mathematical
allocation across compression implementations; exact container hashes remain
bound within the recorded full admission.

The public wrapper acquired stronger final source/native/profile guards and
process cleanup while the scientific recipe ran. Its final `check_release`
was then executed on the completed actual workspace, including all immutable
source trees and native provider hashes. A final dry run confirmed the same
scientific recipe, with only workspace and Python executable paths normalized.
[Validation](evidence/VALIDATION.json) binds that wrapper. The retained source
recipe and its mathematical checks were unchanged throughout.

## Scope and remaining limitations

The selected frontier is unchanged. The source-native and modern-outer
release remains a conditional finite certificate. Inherited
all-size/compiler, common-label/mutable-source, hosting, precision/tape,
analytic and universal block-energy hypotheses remain. No independent human
or formal-kernel proof of integer multiplication is claimed. A stored receipt
binding check does not rerun the source recipe.

## Open next questions

The inherited fractional packing gap remains. A larger replica construction
could reduce it, but it first needs an exact pattern relation and a legal
chronological owner allocation, including all local and idle charges. No
larger search or integral optimality claim is part of this result. The
[structured next question](TASK.json) records the blocker and a bounded first
step.

## Credit and implementation choices

Jeremy Kothe owns R1 and PR3015's declared-edit stage. Nick Petalas contributes
this composition, its source-bound replay wrapper and checks, and retains
PR3018's journal credit. Marius-Paul Dumitrean owns the underlying PR2979 joint
rank-7 construction. Credit remains with Mason Hale, Jeremy Diviney, Yiyang Lu,
Tekalign, Ross Richardson, Dugongue, icekylinx, themilkman216 and the retained
word, native, geometry and owner lineage. The exact source notice and credit
files are retained under `vendor/pr3015`. New work is Apache-2.0.
Substantial automated assistance was used; no independent human review is claimed.

Build the Lever led to a one-argument, replayable composition of the existing
source recipe. Prove It Works required all-role geometry and a fresh finite
release before a conditional supplier claim. Power of Ten led to finite input
and iteration limits, checks active under optimization in the new finite code,
and explicit process timeouts. Python managed allocation and authenticated
imports of two retained modules are documented runtime deviations from static
allocation and direct calls. Live memory is bounded by the fixed 666-call,
271,728-role domain and two words with fewer than 20,000 gates. Source recipe
subprocesses inherit their own existing implementation constraints; this
package does not rewrite frozen predecessors. Warnings are errors and Ruff's
correctness, import, bugbear and modernization rules apply to new code.
