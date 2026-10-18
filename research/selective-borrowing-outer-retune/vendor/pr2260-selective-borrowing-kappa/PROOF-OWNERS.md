# Whole-family ownership and physical charts

The owner certificate `owners/OWNERS.json.gz` contains all **31,392 helper roles**
in the 72 inherited invocations of the selected local word. Each invocation uses
436 complete helper families and retains the parent's 224 literal active data
families. The source-bound check is:

```sh
python -I -O -B owners/verify.py
```

Run that command from this package directory. It reads only package inputs. An
optional `--out /path/outside/this/package` writes a fresh receipt and regenerated
chart certificate outside the package; an existing receipt is never overwritten.
Python 3.10 or later is required. The verifier uses only the standard library and
has no optimizer, solver, network, personal-library or Lean dependency. Explicit
checks remain enabled with Python's `-O` flag.

This proves the finite ownership and chart assembly below, conditional on the
retained exact chart/cover semantics and the local operator identities checked
separately in `PROOF-LOCAL.md`. It does not establish the all-size realization,
recursive work, precision, tape or analytic transfer interfaces by itself.

## Immutable inputs and actual time windows

`owners/SOURCES.json` records the source hashes and public ancestry. The actual
hosted parent is `owners/inputs/HOSTED-PARENT.json.gz`, SHA-256
`f713f8e66aaeaebb8202fe72bf36c7d23497152497342c27892e0fda3092f95b`.
The source DATA-PHASES is SHA-256
`c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa`.
The selected forward trace is SHA-256
`a9d513bc1d85eb11184d73242a4016119f3968bb2a1ff9b365e78109778c17ee`.
The canonical owner bytes are SHA-256
`892b49f97d4caa7e92918262ea3a8cfa8cbf273c92d574ae53bb89a61ee5e847`.
These pins are checked before parsing the corresponding inputs.

The verifier walks the complete serialized parent execution schedule. A local
invocation touches its data pair; each bridge touches both source and destination
pairs. For every inherited idle child it records the last physical touch and the
child's execution position. The supplied PLAN's allowed call indices must equal
the strictly intervening invocations, exactly. This reconstructs the windows from
the actual schedule, including every bridge, rather than trusting a PLAN interval.
The 160 derived windows include the zero-rank child entries; the PLAN records
only the 144 nonzero windows.

Every helper must lie wholly inside its assigned window and on a family absent
from all 224 active data families of that invocation. Family identities are
literal, not interchangeable rank counters. The public ABI is

```text
copy   = owner_replica * 112 + port
family = owner_replica * 896 + (2 * pair + side) * 112 + port.
```

The checker reconstructs and verifies both fields. It also checks exact role
completeness and at most one helper per whole physical family in an invocation.

## Actual chart construction

For each port, the actual DATA-PHASES `q` is first required to equal the retained
local word's port label. To construct its orthogonal 73-column binary basis,
choose the first zero bit `z` of `q` among bits 0 through 8, put
`a = q xor (1 << z)`, and move index `z` to the front of the nine local indices.
For these ordered indices `i`, use the vectors
`(1 << i) xor a` when bit `i` of `a` is set, and `1 << i` otherwise. Append
`1 << i` for indices 9 through 72. The checker verifies all 73 squared norms and
all pairwise binary inner products. Every literal inherited pending-child axis
must belong to this basis, with the exact inherited rank and no repetitions.

A width `d` helper's actual endpoint frames must be nested, and their dimension
difference must equal `d`. The separately checked whole-helper normalizer gives,
with its exact scalar phase,

```text
post * (T_final * inverse(T_initial)) * pre = C_d tensor I_(9-d).
```

The chart sends the `d` normalized coordinates to the helper's exact assigned
contiguous block of the pending child's axis list. It chooses the first `9-d`
unused actual basis axes as explicit spectators, and appends all remaining axes.
The resulting 73 indices must be a permutation. The checker regenerates all
7,150 distinct physical charts and every complete helper route, and compares the
complete payload with `owners/CHARTS.json.gz`.

The normalized whole-helper action therefore contributes precisely the assigned
pending coordinate factors and restores its spectators. Local helper inputs are
arbitrary inputs; the 76 separately owned private fields of the local trace do not
silently replace borrowed inputs by zero. Each invocation completes before the
next one begins. Intermediate spectator use consequently creates no concurrent
physical operation on the same family, even when different invocations use
different complete charts.

## Exact inherited parent action

Within each literal `(owner_replica, child, port)` the assigned axis blocks must
be pairwise disjoint and form an exact prefix. The residual child is the exact
suffix of the same inherited list. These commuting coordinate factors multiply
to the original child factor. Blocks are never transferred between different
children or families because their dimensions happen to match.

Each helper executes after the preceding physical-family touch and before the
pending child. Moving its completed factor to that child's location crosses no
physical-family operation except other completed factors on disjoint orthogonal
coordinates, which commute. The whole-helper identity is the identity on every
spectator. Thus composing the completed helpers and the residual suffix preserves
the original parent's physical data action under the retained exact semantics.

**All child phase and translation boundaries remain inherited, including children
whose residual rank is zero.** A rank-zero residual has no paid coordinate factor;
it does not authorize deleting its `translation_after` or other child metadata.
The complete unchanged hosted parent and DATA-PHASES carry these boundaries.
`owners/CHARTS.json.gz` is a coordinate-factor view, not a replacement serialized
parent program. The independent family-operator replay additionally checks the
complete factor partition and the zero-rank boundaries.

## Recount and controls

The selected local profile multiplied by 72 plus every actual residual suffix is

```text
{1:176252, 2:30096, 3:30908, 4:10152, 5:4493, 6:18,
 7:494, 8:576, 32:11, 39:7, 48:2493}.
```

Its rank mass is 520704, its inherited live stock is 7168, and its deficit is
`73*7168 - 520704 = 2560`. All counts and the entire deterministic receipt are
recomputed and compared with `owners/EXPECTED.json`. The profile is an actual
combined invoice; it is not a sum of separately advertised gains. The exact
moment and outer arithmetic, and the global work/precision invoice, are checked
separately.

Five negative controls alter the copy index, family, offset, width, or complete
role cardinality. Each must fail the same mathematical checker, without relying
on a mismatched input hash. Input-byte pins additionally reject changed retained
sources before certificate replay.
