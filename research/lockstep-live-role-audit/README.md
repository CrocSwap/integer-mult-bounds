# Live roles in the lockstep compiler, and the #4470 outer-reserve constant

**Audit with a positive scoped result; no new κ.** The selected κ is unchanged.

Base: `b58ad9ef4`. This package answers the two open questions of our
`research/bit-row-stock-atom-audit` package (#4612):

1. Does the finite lockstep compiler give every simultaneously live child role
   a distinct physical array? This is DELAYED-COVER-BRIDGE open question 1.
   Both the delayed BIT cover and the row-digit reserve argument assume it.
2. What is the outer-reserve constant `C` of OUTER-TRANSFER-AUDIT §5 for the
   actual #4470 templates?

## 1. Live roles in the lockstep compiler

**Why it matters.** The delayed cover routes a child target role by
`x_g -> y_{gS}` on the *whole* cover fiber of its physical array
(DELAYED-COVER-BRIDGE §3). Suppose two roles that are live at the same level
sat on one array and needed different matchers. Their routes would then
conflict on a single fiber. Nested roles are harmless: a child role sits on the
array of the job its suspended parent issued, so the routes compose as
`g -> gS1 -> gS1S2` and are undone in LIFO order.

**What already existed.** `transfer-audit/finite_dag_audit.py` checks that the
input fields inside each class are distinct, and it counts batches. It does not
execute the schedule across classes. It also does not execute replication,
source complements or exit substitution at field level, and it does not run any
BIT-shaped rule.

**What is checked here.** `live_roles.py` is an independent implementation of
the FINITE-PRECOMPILATION compiler. It covers the Theorem 1G lockstep flow, `a`
lockstep replicas, source complements, and exit batches substituted by the
smaller uniform program. It **executes** the compiler event by event. For every
physical field (productive array or owned center) it keeps the stack of live
roles: a push is one whole-fiber route and a pop is its inverse. At every event
it checks:

| Invariant | Meaning |
|---|---|
| I1 | The roles and owned centers of the units in one class lie on pairwise distinct fields. |
| I2 | A child role enters a field only when the top of that field's stack is the suspended parent that issued the job, and only at equal rank (whole-job substitution). A source enters on its program's array. |
| I3 | A unit issues a paid job only on a field whose top is itself, and never while its previous child class is live. The jobs of one round lie on distinct fields. |
| I4 | Every pop is LIFO. After every class and every program, all stacks are exactly as they were on entry. |
| I5 | Exit and complement batches hand `B_e` distinct fields to the smaller program, each still owned by its issuer. |
| I6 | Every top-level array receives exactly one complement and exactly one source job. |

Results (`verify.py`):

- Counting reproduces the repository receipt: the toy rule at rank 40 gives
  `B = 91,854` and `P = 2,242,264`, and the actual complex p2 rule at rank 41
  gives `B = 1397` and `P = 57,149`.
- All cases pass:
  - the toy rule at `N = 4..64`, with full width executed up to `N = 40`
    (6.9M events, 88,687 nested programs executed);
  - BIT-shaped rules with target ranks `{8, 22, 50}` and paid ranks `1..7` (the
    BIT p3 rank sets with reduced multiplicities), random owner chronologies and
    two adversarial ones (every round on one role; every round on the owned
    center), at `N = 50, 400, 3200, 25600`, up to three generations;
  - the actual complex p2 rule with its native owner order.
- Where the width is astronomical (`B` up to about `10^254`), two lockstep
  replicas are executed, and the smaller programs are checked through their
  interface (I5 plus a LIFO push/pop).
- Rejecting controls (`test_verify.py`):
  - one owned center per recursion depth, instead of one per unit instance,
    is rejected. This is the allocation that FINITE-PRECOMPILATION §6 already
    calls insufficient.
  - an eager parent that issues round `j+1` before child class `j` finishes is
    rejected.
  - an exit batch that repeats a field is rejected.

**General argument.** Induct over the events.

- Sources are fresh arrays.
- Each unit issues exactly one job per round, on a field it currently owns.
- The units of a class own pairwise distinct fields when the class starts.
- Owned centers are allocated per unit instance.

Hence the roles of the next class again lie on distinct fields, and the live
roles on any one field form a chain parent → child → … . Lockstep suspension
pops that chain before the parent issues again. This is exactly the
nested-route structure that the delayed cover needs.

The #4470 compiled unit is a 1024-fold product with completion and splitting
(higher-moment-strictification). The product is itself a two-level lockstep
substitution: `B_V` copies of `U`, one job per copy per paid position, and never
two paid positions of one suspended copy. Splitting and completion add
sequential paid rounds on the same owner. The generic rule format here covers
these. The 1024-fold word itself is not materialized, so its owner chronology is
represented only by BIT-shaped rules of the same structure.

## 2. The outer-reserve constant C for #4470

`constant_c.py` bounds `C` in `q0(h,p) <= C(log2 h + h^δ (log2 p)^3 + 1)`
(δ = 0.004). The inputs are the #4440 BIT ranks that #4470 keeps (`N_b = 2^25986965159937`) and the
#4470 complex word (`v = 1024`, `N_c = 2^64215200000000`), together with the
#4436 nested widths `B_N <= C_N^N`. Every rounding is upward.

| Quantity | Bound |
|---|---|
| BIT share | `log2 <= 51,973,930,319,885` |
| Complex share | `log2 <= 64,215,200,000,086` (at least `2^64215199999954` in the same realization) |
| **C** | **`log2 C <= 64,215,200,000,088`** |
| `H(p) = [1024 C L^3]^(1/(1-δ))` fits the group width `p^β` | from `log2 p = 64,473,100,659,114` (#4612's illustrative value was `5.2·10^13`) |

The complex row stock dominates, by more than `10^13` bits. With the #4440
complex word instead, the fit point would be `1.05·10^16`. For this `C` the
displayed `H` already dominates the #4618 term `4096 C log2(4096 C)`, and
`q0 <= h/512` holds at `h = H` for every tested `L`. Two coefficients are
inherited, not re-derived: the complex row proportionality `c_row <= 2^64` and
the old-supplier stock `A_old <= 2^64`.

## Replay

```sh
python3.12 -B research/lockstep-live-role-audit/verify.py
python3.12 -B research/lockstep-live-role-audit/test_verify.py
```

## Open next questions

1. Derive the two inherited coefficients of `C` (`c_row <= 2^64`,
   `A_old <= 2^64`) from the #4470 sources. They affect only lower-order bits
   of `log2 C`.
2. Emit the raw #4440 BIT paid-owner list and confirm the two local premises
   of the live-role argument (one job per round on a currently owned field;
   per-instance owned centers) for a `v = 2` product. The argument needs
   nothing else from the native word.

## Credit

zxv for #4359, the delayed-cover bridge and the finite compiler; Jacob Alan
Sussman for the Theorem 1G flow; Cinna Davis for the #4440/#4470 chain;
the transfer-audit authors for `finite_dag_audit.py`, whose counting this
package reproduces. Prepared by Mark (Matarener) with substantial Claude Code
(Claude) assistance. Apache-2.0.
