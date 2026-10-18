# Exact scale-placement floor for the contracted factory

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
This is a scoped circuit/accounting result, not a multiplication lower bound.

## Object and class

The object is the complete ordered eight-register map in PR924's
`COMPOSITION.json`, retrieved at
`d02d83332581f6a23616c1366c6b3901d42f4b06`. It combines PR922's two
contractions with PR924's two scale relocations. Its 26 ADD source/target
pairs remain in their prescribed order. Its six SCALE macros may be moved,
split, combined, or supplemented by **signed integral powers of two** on the
same eight wires. ADD coefficients are conjugated by those diagonal gauges.
The entering and exiting gauges are identity. All operations have the same
original frame; coefficient work uses PR696 and is cleared after each ADD.

No ADD insertion, deletion, reordering, changed source/target pair, non-diagonal
basis, extra register, cross-ADD coefficient sharing or alternative lowering
is allowed. Circuit identities outside this gauge class can still improve the
factory. This is a new class calculation on the contracted 26-ADD topology;
PR924's earlier 67-primitive unrestricted certificate concerned 28 ADDs and
explicitly did not establish a macro-budget optimum.

## Why the unbounded gauge class has a finite minimum-macro slice

For an original prefix, let its product of SCALE factors on wire r be S_r.
For a proposed prefix, write the corresponding product S'_r. The physical
values differ by the diagonal gauge G_r = S'_r/S_r. An original ADD
`x_t += a*x_s` must therefore become

`x'_t += a*(G_t/G_s)*x'_s`.

This is an exact identity on arbitrary correlated inputs. The final condition
G_r = 1 requires that the total SCALE product on each wire equal the original
one. The products, in wire order 0 through 7, are

`(2, 2, 2, 1, 1, -1, 2, -2)`.

Six wires have nonidentity totals, so every circuit in this class has at least
six SCALE macros and hence **32 macros**. At equality, each of those six wires
has exactly one SCALE, with its prescribed factor; wires 3 and 4 have none.
This rules out arbitrarily large intermediate exponents at the minimum macro
count. A SCALE can be placed in any slot before, between, or after the ADDs
which touch its wire. Positions among intervening unrelated operations are
equivalent by commutation. The eight wire-use counts are

`(7, 7, 7, 4, 4, 7, 6, 10)`.

The five nonunit magnitude factors are on wires 0, 1, 2, 6 and 7. Consequently
their full placement domain is

`8 * 8 * 8 * 7 * 11 = 39,424`.

Wire 5 has a sign-only factor and eight slots. Moving it conjugates signs of
affected ADDs. PR696 charges positive and negative accumulation equally;
neither coefficient magnitudes nor primitive counts change. This is an exact
quotient by sign placement, not a sampled search. There are **315,392** complete
placement tuples. We do not claim that these are 315,392 distinct linear maps:
all deliberately implement the same map.

## Exact cost and complete census

A signed power-of-two SCALE costs its absolute binary exponent plus one if
negative. The six SCALEs therefore cost 7 real-component primitives. For an
ADD coefficient of magnitude 2^e, pinned PR696 costs

`c(e) = 2 if e = 0, and 3 + |e| otherwise`.

For e = 0 this is the signed accumulation and a work clear. For e != 0 it is
a source copy, |e| doubles/halves, signed accumulation, and a work clear.
No source read, shift, reset, cleanup or negative sign is omitted.

The primary checker evaluates these exact integer costs over the complete
Cartesian product. `EXPECTED.json` records every cost bucket and its
multiplicity, not only the winner. The minimum is **73**. The unique magnitude
placement is

| Wire | Scale | Number of preceding ADDs touching that wire |
|---|---|---:|
| 0 | 2 | 5 |
| 1 | 2 | 5 |
| 2 | 2 | 6 |
| 6 | 2 | 0 |
| 7 | -2 | 2 |

Each of wire 5's eight sign slots ties, including PR924's slot 5. The next
cost is 75, reached by thirteen magnitude placements. There is no cost-74
placement. The maximum in the declared slice is 108. Thus this is an exact
restricted optimum, stronger than merely failing to find a new circuit.

The separately written oracle commutes scales to the end algebraically,
materializes each of the 39,424 candidates with sign slot 3, expands an actual
primitive stream, and executes it on all nine input columns: eight data
columns plus arbitrary dirty coefficient work. It counts actual emitted
primitives and obtains the entire same histogram. It uses integers on a
2^128 grid; every halving checks divisibility, so no rounding, modular
collision, floating-point tolerance or height-bound inference is used.
The primary winner checker instead executes `Fraction` arithmetic through
the actual pinned PR696 lowering. It checks all eight sign placements in all
four orientations against both PR924 and PR681.

Inversion and inverse-transposition biject the gauge class to the matching
class for the transformed ordered topology. They preserve each primitive
cost: scale exponents reverse sign, while ADD magnitudes remain the same.
The minimum is consequently 73 in all four orientations. This bijection is
the argument for the full class; the four-orientation finite replay is an
additional check on the witnesses, not a formal proof of a general theorem.

## Extra macros cannot improve the retained complete local invoice

The pinned historical assembly checks

```
C = 64 * 74^3 = 25,934,336
A = 16 * (max(M_forward, M_backward) + children + registers + centers) + 64*73
local_bound = max(P_forward, P_backward) + A*C
```

The paired raw-factory invocation contains fourteen forward windows and their
fourteen inverse cleanups, each acting on two real components. All non-window
operations, child calls, source accesses, frame changes, registers, centers
and payload conventions remain fixed. The 32-macro optimum therefore spends
`14 * 2 * 2 * 73 = 4,088` real primitives in those windows.

Because each window already has its minimum macro count, an alternative that
uses an extra macro anywhere cannot offset it by deleting a macro in another
window within this class. Forward and inverse-transpose macro counts agree;
the maximum M rises. Even **one** extra emitted macro increases the retained
adapter charge by `16*C = 414,949,376`. Even eliminating all 4,088 primitives
in all windows saves less than that, by a strict margin of **414,945,288**.
This also covers nonuniform choices in different windows. It does not rely
on assuming the same alternative is installed fourteen times.

Hence the minimum-macro winner also minimizes this **fixed retained local
invoice over the whole declared gauge class**, including arbitrarily many
extra shifts and signed scales. This conclusion is conditional on that
invoice model and fixed outside costs. It does not state that its conservative
adapter charge is mathematically necessary in every implementation. A better
adapter/compiler model, changed topology or cross-window fusion is outside
the result and could change the conclusion.

## Precision and scope

The eight optimal representatives have exact local primitive row-l1 peaks
12, 8, 10, 12 and fractional depths 1, 2, 2, 1 for forward, inverse,
inverse-transpose and transpose respectively. Their exact endpoints equal
the original PR681 full eight-wire operator. PR924's already shipped slot-5
witness attains the floor; this package proposes no replacement and needs
no new physical admission. We do not claim every other placement satisfies
the production precision allowance: admitting all of them only strengthens
the lower bound, and the known admitted witness attains it.

The general reduction and integer cost argument are written mathematical
arguments with exhaustive finite computation; there is no Lean proof here.
The current accepted U8/T21 construction and its κ are untouched. Uniform
compilation, common-label/mutable-source realization, physical hosting,
precision/tape recovery, bit H1-H5 and analytic transfer remain inherited
obligations. This is not a new supplier exponent, runtime measurement or a
formal verification of the multiplication theorem.
