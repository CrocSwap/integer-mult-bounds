# Nine further paired helper extractions

This construction starts from Jeremy Diviney's PR2908 at
`51309592971e3b5be935599eed2a95404dc7781e`, including its restored helper408.
It restores nine further arbitrary dirty helper inputs at rank8 instead of
rank9. Three directions fit the predecessor's terminal frames. Six more become
available after explicit changes to thirteen inherited gate frames. Every new
restored endpoint gets its own charged private zero buffer.

The paired input/output method, its structural checker and its compensation
rule are inherited from PR2908. The new contribution is the ordered nine-step
composition, the six directions enabled by the declared frame changes, and
their complete allocation and admission. Jeremy Kothe's PR2894 supplies the
frame-accounting and inverse-cleanup routines. Further attribution is recorded
in `CREDITS.md` and retained source notices.

## Exact two-sided certificate

Fix the current word immediately before one extraction. Let `M` be its
complete non-target forward operator: the A gates after the entry prelude,
the B gates with their formal invertible warps, and the restore gates. Omit
target writes from this definition. Coefficients belong to the exact rational
free algebra of the warp operators and their inverses. Distinct operator words
are not identified by numerical evaluation.

Let `H` contain the live, zero-entry helpers except for previously restored
helpers and the sources of the initial operator corrections. Let

```
E_n = {x in F_2^9 : x dot n = 0}.
```

For a nonzero nine-bit normal `n`, this is a rank8 hyperplane. The admissible
output registers `R` have terminal frames contained in `E_n`, after any
declared frame changes for this step.

Choose a scalar row `alpha` and scalar column `y` supported on `R`, and scalar
vectors `u,v` supported on `H`, with

```
alpha M = u,       M v = y,       alpha y = 1.
```

These identities imply `u v = 1`. We also require `C v = 0`, where `C` is the
current scalar target-compensation map. The input and output changes `S,T`
are literal invertible dyadic gate sequences satisfying

```
S e_h = v,        u S = e_h^T,
T y = e_h,        e_h^T T = alpha.
```

Consequently,

```
(T M S) e_h = T M v = T y = e_h,
e_h^T (T M S) = alpha M S = u S = e_h^T.
```

Both the entire column and the entire row of helper `h` are therefore the
corresponding identity column and row. Its original arbitrary dirty input is
restored, and no other non-target output depends on that input. Restoring the
row alone, or preserving only the target map, would not establish this
isolation property.

The unchanged PR2908 `structure.py` derives `S,T,M,alpha,y,u,v` from the
literal gates. It checks all seven displayed identities defining the paired
certificate over exact rational free-operator coefficients. It does not
accept search vectors or a numerical nullspace as evidence. `producer.py`
separately requires that the new compensation has no column for `h`;
because `S e_h = v`, this is the condition `C v = 0`. The full local auditor
checks the target map and its dual orientation separately.

## Legal insertion and composition

The input gates are inserted immediately after the unchanged entry prelude.
They use only unprotected live zero-entry helpers and have frame zero. Their
coefficients are dyadic. Thus they neither modify a prior restored endpoint
nor alter an initial operator-correction source. All output gates for a step
use its single rank8 frame `E_n` and are appended to the current restore
sequence.

The target compensation is replaced by `C S`. The producer computes this
right multiplication by visiting the literal input gates in reverse order.
The initial operator corrections are unchanged. The cut, warp interfaces,
ports, target levels, removed helpers and entry prelude are also unchanged.
Exactly these six word sections change: `A`, `restore`, `helper_final`,
`compensation`, `report` and `cleanup`.

Inverse-reverse cleanup is regenerated from the full new word at every step.
The new isolated cold coordinate is included in its protected cold set and
receives one additional private zero buffer. The local auditor checks the
resulting restore/isolation and zero-buffer identities; native admission
checks the realized operator program and its complete physical contract.

Composition is sequential. Each certificate is derived against the result
of the preceding step, and its protected set includes every endpoint already
extracted. The producer enforces this exact helper order:

| Step | Helper | Hyperplane normal | Inherited frame edits | Per-call profile change | Private buffers |
| --- | ---: | ---: | ---: | --- | ---: |
| Parent PR2908 | 408 already present | 52 | — | — | 73 |
| 1 | 424 | 52 | 0 | `3H1 - 2H2` | 74 |
| 2 | 428 | 76 | 0 | `3H1 - 2H2` | 75 |
| 3 | 412 | 127 | 0 | `3H1 - 2H2` | 76 |
| 4 | 331 | 30 | 2 | `H2 + 3H3 - 3H4` | 77 |
| 5 | 299 | 51 | 2 | `H2 + 3H3 - 3H4` | 78 |
| 6 | 320 | 75 | 2 | `H2 + 3H3 - 3H4` | 79 |
| 7 | 511 | 85 | 2 | `H2 + 3H3 - 3H4` | 80 |
| 8 | 304 | 102 | 2 | `H2 + 3H3 - 3H4` | 81 |
| 9 | 499 | 120 | 3 | `H2 + 3H3 - 3H4` | 82 |

Here `Hr` denotes one rank-r term in the paid profile. The changes in the
table include the complete local frame bill for each step, not just its
new output gates.

## Why the six frame changes expose new directions

An extraction search restricted to the current literal terminal frames can
miss a direction whose supporting registers were lifted unnecessarily early.
For each of the last six steps, two inherited A additions can instead use a
particular rank7 frame. Their scalar coefficients and order stay unchanged.
The complete frame replay checks the resulting inclusions at every use and
the unchanged later cut and warp requirements. These substitutions allow the
small output support of the paired certificate to meet in its rank8
hyperplane without the previous terminal-frame obstruction.

The sparse output rows and columns for the six steps are:

| Helper | `alpha` | `y` |
| ---: | --- | --- |
| 331 | `e331^T + e22^T - e34^T` | `e22` |
| 299 | `e299^T + e40^T - e54^T` | `e40` |
| 320 | `e320^T - e324^T + e326^T` | `e320` |
| 511 | `e511^T + e23^T - e322^T` | `e23` |
| 304 | `e304^T - e308^T + e310^T` | `e304` |
| 499 | `e499^T + e35^T - e306^T` | `e35` |

The full input vectors generally have larger support; the literal dyadic
input gates in `data/TRANSFORM-<helper>.json` define them exactly. They are
checked against the current composed word, not reused from an earlier
nullspace computation.

There are twelve rank8-to-rank7 edits in A. The thirteenth edit lowers the
existing `scale 499 by -1` restore gate from the full rank9 frame to the
normal120 rank8 frame. That scale is retained, and its coefficient is
unchanged. Omitting this edit would retain an unnecessary full-frame touch
and would not implement the stated endpoint and bill.

Each transform records the section, index in that step's immediate parent,
complete scalar gate, old frame and new frame. `producer.refit` checks the
exact old gate and frame before applying the substitution. It applies the
edits before inserting that step's input and output gates. Verification uses
these fixed records and does not run a frame optimizer. Frame-only edits
leave the formal scalar/warp operator `M` unchanged; their geometric legality
and paid cost are separate obligations checked from the complete word.

## Complete local accounting

The predecessor and final local profiles are respectively

```
PR2908: 2407 H1 + 640 H2 + 262 H3 + 128 H4 + 26 H5 + 8 H8
final:  2416 H1 + 640 H2 + 280 H3 + 110 H4 + 26 H5 + 8 H8.
```

Thus the exact local difference is

```
3(3H1 - 2H2) + 6(H2 + 3H3 - 3H4)
    = 9H1 + 18H3 - 18H4.
```

The helper-width inventory changes from

```
{4:26, 5:2, 7:62, 8:87, 9:231}
```

to

```
{4:26, 5:2, 7:62, 8:96, 9:222}.
```

There remain 408 live helper roles per call and 632 independent inputs.
Exactly nine width9 roles become width8; no role disappears. The local
rank-mass decrease is nine, consistent with those nine endpoint changes.
The buffer count increases from 73 to 82.

In the unchanged T74 architecture there are 666 calls and 271,728 helper
roles. Its complete physical stock is

```
66304 live families + 408 helper slots + 8 centres
    + 82 private zero buffers + 2 scratch = 66804.
```

The saved local rank mass must reappear in the owner residual accounting.
Accordingly, the local difference alone is not a claim of a higher kappa.
The literal allocation must fit all whole-width roles in legal owner windows,
respect same-call family exclusions, and charge every unused remainder. Its
actual profile, physical stock and complete outer inequalities determine the
conditional exponent.

## Evidence and scope

`verify.py` authenticates every shipped vendor/data byte, derives each
transformation in order, checks its exact paired identities, reproduces both
published words, and runs the inherited full local auditor on both provider
variants. The auditor covers all 632 independent columns and the dual
orientation. The verifier also regenerates cleanup for 36 semantic mutants
and requires rejection: in each provider and at each step, it either removes
the final output gate or reverses that gate's sign. These checks establish
finite symbolic identities and local invoices, rather than tests of a sample
of integer inputs.

`tools/build_extension.py` binds the local parent words to the exact PR2908
export and appends this stage to its complete rebuild chain. The remaining
native, literal-owner, block-norm, physical-stock, prefix and outer-admission
checks are separate from the local certificate. Their final receipts, not
the local proof alone, authorize a published conditional kappa. No allocation
optimality or impossibility of further paired extractions is claimed.

Even after complete finite admission, the multiplication bound remains
conditional on the repository's inherited all-size, compiler and outer-theorem
assumptions. This construction does not close those assumptions or establish
a measured practical multiplication speedup.
