# Fixed-output resynthesis of one historical R480 Q-node

This is a finite bit-circuit construction, conditional on the inherited
mutable-source and native bit interfaces. It changes one historical PR503/510
R480 block, not the selected PR589 supplier or PR942 exponent. All arithmetic
endpoint equalities below are over F2 unless explicitly described as positive
integer growth bounds. No full multiplication theorem is proved here.

## Exact object and changed mechanism

The source is the immutable R480 word in `SOURCES.json`, at base
`407d52ff15b2217b6e22bce44728b4c3907b6515`. Phase A events `[2250:2302]`
(zero based, upper endpoint excluded) form Q-node2 at frame484. Its ordered
source registers are

```text
17, 25, 32, 43, 52, 58, 64, 77, 82, 90, 99, 104.
```

Every input is arbitrary. These are existing source registers, not clean
ancillas or freely initialized work. The old block has 52 one-source XORs.
Writing its twelve outputs as row bitmasks in the above input order gives

```text
4095, 2390, 3835, 3831, 1625, 3935,
3951, 16, 207, 4, 1023, 1.
```

The new construction allows cancellation within a complete twelve-source
invertible F2 transform. This differs from preserving a positive integer
transfer, and from substituting the six-wire helper quad in PR823. It uses
the same common frame and the same twelve registers. `RECIPE.json` lists
all 43 new XORs with their actual global register identifiers.

## Fixed outputs and complete restoration

An elementary row operation `d ^= s` is its own inverse over F2. Gauss-Jordan
elimination reduces the source matrix M to I by a recorded chronological
sequence of these operations. Every required row swap is implemented by
three charged XORs; row labels are never silently permuted. Reversing that
sequence therefore implements M on the original, fixed output registers.
The verifier compares all twelve output rows, rather than only their span,
rank, output multiset or values on clean source inputs.

For any surrounding linear context, substituting an equal matrix at the
same boundary preserves its F2 state. The local Boolean check also enumerates
all 4,096 inputs and the literal inverse. In the complete word, D and every
part of A outside the block remain unchanged; B, the nine retained totals,
scatter, frame definitions and source/final frame labels remain unchanged.
The new C is the literal full-frame reverse of the entire modified A.
Since B writes only targets, this is precisely the inherited cleanup rule.
It restores the mutable sources and all 480 arbitrary dirty helpers.

The primary bitset interpreter and the separate support-set interpreter
check all 720 independent persistent input columns: 120 sources, 120 targets
and 480 helpers. In both forward and inverse scalar replay the endpoint is

```text
(x, y, h) -> (x, y XOR x, h),
```

with every external copied-center temporary erased. Both interpreters enforce
immutable copied centers between COPY and ERASE. The inverse reverses ADDs
and interchanges COPY with ERASE, using the original center binding. All nine
copy lifetimes close. This is finite F2 evidence, not equality of the old and
new integer or real coefficient matrices.

## Complete local price and frame obligations

The source block is 52 XORs; the replacement is 43. Reverse cleanup therefore
costs 43 instead of 52 as well. The complete local bill is

```text
33,958 - (52 - 43) - (52 - 43) = 33,940 ADDs.
```

The saving is eighteen, including restoration. No scratch register, COPY,
ERASE, source-access instruction or recursive call is introduced. Every
source use appears as a charged ADD operand. This is a primitive count,
not an elapsed-time improvement or a physical hosting invoice.

All twelve source registers still visit frame484, and they do so within
the same uninterrupted block. The complete per-register frame paths are
identical, which preserves the nested climb bill. The sequence in which
different registers first move can change; equality of individual paths
does not assert byte equality of the interleaved MOVE stream. Exact frame
legality must be checked on the emitted candidate records.

The native legality and column checks retain nine copies/erasures and the
paid local histogram

```text
{1:1200, 2:1440, 4:180, 6:120, 8:9}.
```

The selected supplier and the recurrence moment receive no proposed change.
There is no claim that eighteen fewer scalar ADDs improve kappa.

## Positive growth is a separate admission

F2 equality alone gives no useful bound on the signed lift's intermediate
magnitudes. In independent local block-input coordinates the forward
cancellation-free maximum row sum actually rises from **25 to 99**. The
inverse value falls from **1,721 to 29**. Neither the old integer transfer
nor entrywise forward domination is preserved. A local-domination argument
would reject or fail to justify this candidate.

The complete chronological word, including D, A, all copied-center work,
scatter, B and C, is evaluated separately in both directions. Its exact
positive scalar bounds are

| Bound | Original | Replacement |
| --- | ---: | ---: |
| Forward F | 176,135 | 176,135 |
| Inverse B | 3,751,204 | 3,682,548 |
| `64 F^3 B^2` | 4,921,056,267,806,722,187,755,121,024,000 | 4,742,570,525,118,367,822,773,353,856,000 |

Both payload bounds have bit length102 and are strictly below `2^104`.
The Python implementations independently reproduce them; the retained C++
column checkers enforce that same complete inequality. Checking it is
essential: an additional repeated six-XOR identity cycle preserves every
F2 endpoint but can exceed the 104-bit cap. That endpoint-valid counterexample
is an explicit negative control.

This comparison does not prove that every new intermediate is smaller, nor
does it supply a new hosted-parent chronological precision invoice. The local
bound, the finite multistage column checks and a global hosted invoice are
different obligations. Only the executed checks in `VALIDATION.md` are claimed.

## Bounded search and what it establishes

Assignment seed2 selected the bit track and this twelve-source object. The
frozen search uses Python `random.Random(2)` for exactly 1,000 trajectories,
starting from this single matrix each time. It shuffles pivot-column order,
keeps a nonzero diagonal pivot when possible, otherwise chooses a nonzero
unprocessed row, pays every three-XOR swap, and eliminates the other rows.
The first shortest encountered word is retained. No early restart, search
across source reorderings after the run, or favorable seed selection is used.
The separate preliminary Q-node1/8 orientation probes are disclosed in
`VALIDATION.md`; they are not part of this admitted result.

Trial860 (zero based) gives the unique 43-XOR word encountered. The complete
length histogram and sequence of improvements are retained, and
`search.py` recomputes them exactly. This is a bounded witness search, not a
proof of a 43-XOR minimum, an exhaustive enumeration of all elimination
orders or a lower bound on arbitrary XOR circuits.

## Failure detection and scope

Every one of the 43 candidate-gate deletions changes the local map. Independent
controls additionally check fixed output ordering, arbitrary source/helper/
target dirt, omitted compensation and cleanup gates, an incorrect frame and
an unclosed copied-center temporary. The growth control above separates
endpoint validity from precision admission.

One subtle control retains the old 52-gate cleanup after installing the new
43-gate forward block. It still has the correct endpoint, because the two
local F2 matrices agree, but its complete bill is **33,949** and it violates
this construction's literal-inverse rule. It is rejected by the explicit
cleanup contract, not falsely reported as an endpoint failure. A correct
endpoint alone would not certify the claimed eighteen-ADD saving.

The unchanged native checkers cover finite legality, source ownership,
copied-center lifecycle and 5/9/11-stage columns. Remaining obligations include
full hosted-parent/whole-owner reconstruction, revised supplier bindings and
invoice/outer assembly, and the inherited all-size/compiler, common-label/
mutable-source realization, rounding/tape/recovery and analytic assumptions.
No unconditional multiplication result or formal proof of that theorem follows.

## Credit

The Q-node matrix and its original construction come from eumemic's PR493
carrier skeleton and DreamingOfClouds's PR503/510 R480 adaptation. Hao Yan's
PR823 supplies related six-wire R480 resynthesis; the recipes are separate.
Jeffrey Cox's PR754 and Gareth Davidson/Ross Richardson's PR904/936/952
provide bounded XOR-resynthesis precedent. PR857/906/980 demonstrate why
complete precision admission may be useful without local domination; no
priority claim is made for that general idea. Native checks retain Dylan
Crow, Zhihao Chen, DaysSky and the inherited contributors' notices.

Prepared for ToikY with substantial OpenAI Codex assistance, including separate
implementation and mathematical review; no independent human review claimed.
Apache-2.0.
