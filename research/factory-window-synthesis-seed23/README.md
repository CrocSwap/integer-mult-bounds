**Scoped negative result: short-window minima for the contracted complex factory.
No new kappa.**

The PR922/924 factory retained by PR949 contains **27 short sections that already
use the minimum number of scalar macros in the alphabet checked here**. Eighteen
four-macro sections also attain the minimum PR696 primitive cost at that length.
Five additional six-macro sections need at least five macros; a five-macro
replacement remains open. This adds local topology coverage around the existing
32-macro circuit costing 73 primitives per real component. It proposes no
replacement supplier.

| Original section length | Eligible sections | Exact macro minimum or interval | Primitive minimum |
| --- | ---: | --- | --- |
| 4 | 18 | 4 | Original cost is minimal at length 4 |
| 5 | 9 | 5 | Not determined at length 5 |
| 6 | 5 | [5, 6] | Not determined at length 5 or 6 |

The census includes every contiguous section of length four, five or six in the
fixed circuit that touches at most four registers. A replacement may use any
ordered, distinct source/target pair within those **same registers**. Its ADD
coefficients belong to `{-2,-1,-1/2,1/2,1,2}`; its SCALE factors belong to
`{-2,-1,-1/2,1/2,2}`. All words of length **zero through four** are covered.
No extra register, borrowed untouched register, clean-data assumption, changed
boundary frame, larger coefficient or longer replacement is included.

The nine five-macro sections have exact minimum length five because no word of
length at most four has their map, and their original words attain five. Their
best primitive cost at length five is not determined. The five six-macro sections
have only the interval `[5,6]` certified. These finite-alphabet statements are not
an unrestricted circuit minimum or an impossibility result for improving the
supplier.

Python 3.9+ and the standard library suffice, with no network or solver. From the
repository root:

```sh
python3 -I -B research/factory-window-synthesis-seed23/verify.py
python3 -I -B research/factory-window-synthesis-seed23/independent.py
python3 -I -O -B research/factory-window-synthesis-seed23/test_package.py
```

Expected markers are `PASS_FACTORY_WINDOW_SYNTHESIS`,
`PASS_FACTORY_WINDOW_MODULAR` and `PASS_FACTORY_WINDOW_PACKAGE`. The first reports
32 windows, 128 orientations, 27 macro minima and 12 controls; the last reports
ten rejection controls. Normal verification writes nothing. `verify.py --write
/path/to/new.json` regenerates the complete development receipt and refuses an
existing destination.

The primary implementation represents matrices using integer numerators and a
shared power-of-two denominator. It constructs a table of every prefix of length
at most two, retaining the lexicographically cheapest `(macro count, primitive
cost)` witness for each exact matrix. For each target it removes every suffix of
length at most two and queries that table. Every word of length at most four has
such a split. Replacing a prefix with a cheaper prefix for the same map cannot
worsen the length bound or the lexicographic objective. This establishes complete
coverage of the declared finite search. There is no timeout, sampling or unvisited
remainder.

The two-, three- and four-register alphabets contain 22, 51 and 92 gates. Their
prefix tables contain 296, 1,687 and 5,443 distinct matrices. There are one, seven
and 24 sections of those respective register dimensions. Forward, inverse,
transpose and inverse-transpose searches cover **128 targets and 897,784 suffix
probes**. OS assignment seed 23 rotates the complete visit order without reducing
coverage. [EXPECTED.json](EXPECTED.json) records every section, orientation, exact
minimum or exclusion, attaining short witness and source-bound matrix digest.

The separate checker imports no constructor, predecessor implementation or cost
function. It uses dense matrices over the prime field with 65,537 elements,
emits its own literal primitive lists for prices, and factors targets on the right
using generic matrix multiplication and Gaussian inversion. Every allowed rational
gate reduces into this field because its denominator is a power of two. A cheaper
rational word would give a no-more-expensive modular word. Collisions can weaken
this lower bound but cannot create a false exclusion. All 128 modular bounds
agree with the rational results. Both implementations find a planted noncommuting
three-to-two contraction and the empty identity word. These are separately written
implementations by the same AI agent, not independent human review.

The complete eight-register map is checked against PR681. All consumed gates carry
the same original frame. Pinned PR696 lowering charges **two** primitives for a
unit ADD and **four** for coefficients of magnitude two or one-half. A SCALE costs
its shift count plus one for a negative sign. All primitive prices here are for
one real component; complex execution uses two such components.
Source copies, arithmetic, signed
accumulation and the final private-work clear are included. Each original section
and nominated witness is replayed on every data-input column plus arbitrary dirty
coefficient work. Public data has the prescribed exact map; private work is
erased, not restored to its initial dirt. No helper or restoration is free.

Under the retained local adapter formula, an additional emitted macro costs
`16*(64*74^3) = 414,949,376`. Macro count therefore takes priority over these small
primitive differences; primitive cost still breaks ties. The source formula is
pinned, and its arithmetic is recorded in the receipt. The global invoice script
is not executed. Inversion and transposition preserve the alphabet and prices;
both inverse and inverse-transpose cleanups are checked explicitly. A proposed
substitution would still need native admission, prefix accounting and complete
supplier replay. None is proposed here. No full invoice is issued, the recursive
profile is unchanged, and scalar work alone does not establish a new exponent.

Exact base: **`2921874911956718fcaaaf9396fe8267b3cfa9f0`**. The selected PR942
conditional kappa at that base is **0.001661960547713947**. Its 876-file source
manifest and assembly hash were checked, and its construction and maintainer
review were inspected. This is context, not a cold supplier replay.
[SOURCES.json](SOURCES.json) pins the PR924 composition, PR681 map, PR696 lowering
and retained adapter formula. The composition is byte-identical to the fetched
PR924 Git object at `d02d83332581f6a23616c1366c6b3901d42f4b06`. Its internal
`pr924_head` denotes the earlier standalone revision; the retrieval head denotes
the later composition. No pending executable implementation is imported.

[CLAIM.json](CLAIM.json) records the three candidate tasks and overlap checks.
No pinned sprint coordination issue existed. [PR922](https://github.com/CrocSwap/integer-mult-bounds/pull/922)
contracts movable triples; [PR924](https://github.com/CrocSwap/integer-mult-bounds/pull/924)
relocates scales; [PR949](https://github.com/CrocSwap/integer-mult-bounds/pull/949)
keeps the ordered ADD topology fixed; and [PR931](https://github.com/CrocSwap/integer-mult-bounds/pull/931)
searches butterfly recipes. Here the replacement may change the local gate
topology within the explicit alphabet. This is not a closed search repeated with
another seed. The final overlap check through PR1028 and all 50 all-state factory
search hits found no same-scope contribution; main remained at the exact base.

Validation passed with **CPython 3.14.6 and 3.9.6 on macOS arm64**. It includes the
complete primary and modular checks, 12 mathematical/admission controls including
positive detection examples, ten package rejection controls, optimized offline
relocation, exact receipt regeneration, source Git-byte comparison, Ruff and
`make selected-record-check`. The package tests check missing windows and
orientations, undercharged and mistyped receipts, corrupt/missing sources and
existing-output preservation. The repository-wide `make verify`, selected cold
replay, hosted CI and Lean were not run. All-size compilation,
common-label/mutable-source realization, hosting, precision/tape, analytic
transfer and bit H1-H5 obligations remain inherited. Finite search is not formal
verification of the multiplication theorem.

Prepared by **Hanson Sun (@bbMisk)**, with substantial **OpenAI Codex assistance**
in selection, mathematics, implementation, verification and writing. Apache-2.0
under the repository [LICENSE](../../LICENSE). Credit **Alluri** for PR681,
**Sagar Thakrar** for PR696, **CubeJerry** for PR922/924, **Ross Richardson** for
PR949 and PR931, **Jeremy Kothe** for PR622, **icekylinx** for the factory/scalar
architecture, and **Chafik Boukhalfa** and the retained supplier contributors.
Their source files, licenses and notices are unchanged. No delegated agent or
independent human review is claimed. Only this research directory is added;
the selected frontier, production sources and `upstream/` are unchanged.
