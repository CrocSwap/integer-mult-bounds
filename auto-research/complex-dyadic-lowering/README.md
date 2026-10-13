# Smaller dyadic circuits for the selected complex suppliers

This finite circuit improvement reduces the scalar primitive bill of the
selected PR626 complex programs by 22.1–24.6%. It replaces coefficient work
inside each scalar macro, preserving the exact macro, its frame and its source
and target registers. It does not claim a new κ or a measured runtime speedup.

| Provider | Orientation | Original real primitives | Replacement | Saved |
| --- | --- | ---: | ---: | ---: |
| CK | Forward | 224,938 | 169,618 | 55,320 |
| CK | Backward | 224,986 | 169,634 | 55,352 |
| JP8 | Forward | 257,232 | 200,380 | 56,852 |
| JP8 | Backward | 257,280 | 200,396 | 56,884 |

These counts include all scalar macros in each complete emitted local program,
including preconditions, compensation, centers and cleanup. They count both real
components of the complex streams. They exclude the unchanged recursive children,
frame adapters and residual wrappers, exactly as the original
`real_component_primitive_bound` field does.

## Reproduce

From a checkout containing this contribution, with Python 3.11+ and no external
dependencies:

```sh
python3 -B research/complex-dyadic-lowering/verify.py
```

Expected:

```text
PASS_COMPLEX_DYADIC_LOWERING programs=4 columns=716 savings=55320,55352,56852,56884 controls=10
```

The command is offline and writes no files. `--json` prints the deterministic
receipt after checking it against [EXPECTED.json](EXPECTED.json). It verifies
source hashes before replaying; gzip pins cover decompressed payload bytes.
It can be run from another working directory by using the script's absolute path.

## Circuit and cost

For a nonzero dyadic coefficient `q = ±a/2^k` in reduced form, a scalar macro
updates `T ← T + qS`. The existing binary Horner implementation first clears
private work `W`, then adds `S` for the leading binary digit of `a`. Both
instructions together set `W = S`, even for arbitrary initial `W`. The
replacement uses one copy instruction for that assignment and retains every
remaining binary digit, halving, signed accumulation and final work clear.

For `q = ±1`, the replacement is simply `T ← T ± S; W ← 0`. The clear is still
charged, so this circuit does not assume a clean private input. Both replacements
have the complete three-register map

```text
(T, S, W) → (T + qS, S, 0).
```

The original cost per real component is
`3 + floor(log2(a)) + popcount(a) + k`. Copy initialization saves one primitive
for every nonunit coefficient. The unit replacement costs two primitives,
instead of four. Thus a program with `A` additions, of which `U` have unit
coefficients, saves exactly `2(A + U)` real-component primitives.

The executable replacement is [lower.py](lower.py). Its primitive vocabulary is
clear, copy, doubling, halving, negation and signed addition. Scale macros retain
their original signed-power-of-two lowering. Each primitive stays at the scalar
macro's frame. No source is temporarily modified; no helper, source access,
frame change, center copy, restoration or recursive child is added or omitted.
The existing two real coefficient-work streams suffice.

## Prefix bound and substitution argument

For a nonunit coefficient, the new copy reaches precisely the old state after
the leading addition. The rest of the instruction sequence is identical. Each
new register value therefore occurs in the old prefix trace, including the
arbitrary initial private-work value.

For a unit coefficient, the target reaches its old final value directly. The
source remains unchanged. Work retains its initial value until the clear.
Each of these register values also occurs in the original trace. This proves
containment of the maximum over prefixes and registers; it does not assert
entrywise domination of simultaneous transfer matrices.

The argument holds for arbitrary real or complex inputs and correlated input
values. In particular, it preserves the inherited maximum-row norm bound.
The verifier also reconstructs the original nonnegative scalar/Horner envelope
from the full macro stream and matches the pinned independent replay's exact
`prefix_l1_upper`. Its existing 192-bit charged payload allowance is retained.
This is an exact-arithmetic circuit argument. The all-size rounding and tape
interfaces remain inherited, as they are in the selected result.

Replacing a macro by a circuit with the same source, target and cleared-work
boundary preserves every following macro's inputs. Induction over the fixed
event stream then preserves the complete scalar program. Frame events,
normalization wrappers, center lifetimes and recursive calls are unchanged.
The existing geometric and physical admission is inherited from the pinned
selected supplier; this package does not independently prove it.

## Evidence and limits

[verify.py](verify.py) expands every scalar macro into primitives and executes
those primitives with exact rational sparse rows. Each of the four programs
checks all 716 input columns, including 492 arbitrary dirty helper columns,
plus an arbitrary coefficient-work input column. It verifies the required
forward or backward shear, restored helpers, and cleared private registers.
The imaginary component uses the same real-coefficient circuit, so the exact
linear identity applies separately to it.

For all 686 distinct addition coefficients, a separate three-register check
compares every candidate register row with the complete reference Horner trace.
This includes the initial state. It checks the full boundary and exact primitive
count. The receipt records hashes of the expanded primitive words, their
operation counts, unchanged paid profiles and inherited prefix bounds.

Ten controls reject missing cleanup, missing initialization, a wrong sign,
unnecessary work, excessive intermediate growth with a restored endpoint,
uncleared private dirt for a unit coefficient, a nondyadic coefficient, zero,
and source/target or source/work aliasing. The growth control must fail the
prefix check specifically; the unnecessary-work control must fail the count.

This is deterministic complete coverage of these four frozen programs and their
686 coefficients. There is no randomized circuit search and no optimality claim.
Seed 22 selects the first provider and a coefficient for mutation controls; it
does not stand in for coverage. The general leading-bit proof above is distinct
from the finite replay and does not formalize the multiplication theorem.

The paid profiles and assembly parameters are unchanged, so the accepted
conditional κ remains `51110230636731/31250000000000000`, or
`0.001635527380375392`. This package supplies an executable local lowering and
an independently reviewable receipt. It does not replace the selected emitter,
regenerate its certificates, or change the accepted frontier.

## Provenance and sprint scope

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
[SOURCE-PINS.json](SOURCE-PINS.json) pins every consumed source, the original
lowering and invoice code, and the selected record. The selected PR626 head is
`660de893d27bb7abd1d5b01b1640207528a5c851`; its construction descends from PR622
at `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`.

Credit goes to icekylinx for the scalar operation and coefficient-work lineage
through PR425/433/531, Jeremy Kothe for the K492 construction and schedules,
Chafik Boukhalfa for the selected PR626 packing, and the predecessors retained in
the [maintainer review](../../docs/research/community-k492-review.md), including
DreamingOfClouds' cold-helper construction and Rohan Arun's recurrence correction.
The retained bit supplier is eumemic's PR543.

Eumemic's historical [PR411](https://github.com/CrocSwap/integer-mult-bounds/pull/411)
at `f58d95f2c5da03445e704ea9c72cc55df9e68190` already used paid copy, halving,
accumulation and clear for quarter/eighth coefficients. It is related prior work,
not a code dependency. This contribution specializes the fixed selected macro
streams and covers all their coefficients, arbitrary private dirt and prefix
containment. It makes no priority claim for copy-based coefficient preparation.

Current [PR681](https://github.com/CrocSwap/integer-mult-bounds/pull/681), reviewed
for overlap at `80d4edbc2d53f058787cb5c43bd0fc22c7e7fdff`, resynthesizes an
87-operation factory window into 35 scalar operations. That changes a scalar
word. This contribution reduces the primitive cost inside unchanged macros and
does not depend on PR681. PR667 concerns exact logarithm evaluation. Raw-face
sharing, cold-end scheduling and closed packet-factory searches are not reopened.

The [local claim](CLAIM.json) records seed 22, the three candidate tasks and the
absence of a pinned sprint issue. Contribution by Sagar Thakrar / `thakrarsagar`,
with substantial OpenAI Codex assistance in research, implementation, proof
writing and review. New files are under the repository's Apache-2.0 license.
