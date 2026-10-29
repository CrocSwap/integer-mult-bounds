# Retuned ordinary work in the unchanged T74 recursion

The new result is a conditional rate transfer and an opt-in factory binding.
It combines Jose Manuel's PR3562 ordinary bound at `c=1/577` with his
PR3477 T74 physical layer. It changes neither the T74 word, positive-child
histogram, recursion stop, guard nor root dimension. In particular, it does
not substitute an ordinary exponent directly for a supplier moment exponent.
The two exponents now have the opposite ordering from PR3477's proof.

PR3562 is pinned at `abb93be8b9ceca07a2b17f3a97db7bb6b074271d`; its complete
[proof](inputs/pr3562-PROOF.md) is retained verbatim with this package.
The canonical T74 inputs are
from main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`. `SOURCES.json` and the
factory verifier bind the precise executable and proof inputs.

## 1. Quantified conditional claim

Retain PR3477's fixed source-admissible prime `q=213*2^80+1`, T74 native
identities, same-label backward convention, chronological whole-owner
hosting, complete spectators, parent-return protocol, coefficient-height
induction and source-to-physical cost contracts. Retain the complete PR2753
C0 caller and PR2809/PR2899 ordinary/binary refinement, including the
compatible stock, preparation, elementary primitives, canonical contexts,
fixed tape inventory and successful-return ownership conditions.
PR3562 supplies the stronger ordinary exponent under these premises:

```
c=1/577,  a=c(1-c)=576/332929,
tau=1-a=332353/332929.
```

For the retained T74 root domain take `p>=2`, `d=floor(p^(997/1000))`,
`K=floor(d^(1/500))`, at most `d` selected axes `rho+jK`, and `0<=rho<K`.
Records have `r=2^Theta(p/d)` Gaussian fields, complete preceding/following
spectators, and `O(p)`-bit descriptors and addresses. Constants in these
domains are fixed before the input. The input coefficients lie on the
`p`-grid in the unit disk. Let `V` be the entire original serialized payload.

With the new ordinary profile, the same source-relative physical construction
has time and occupied/visited space

```
T_layer = O_q(V*d^(998273/1000000)),
S_layer = O_q(V)+F_q.
```

Its endpoint remains the normalized tensor Walsh transform
`H0^(tensor D)`, `H0=[[1,1],[1,-1]]/2`, with the same single final
truncation and error below `sqrt(2)*2^-p`. The layer saving is `.001727`,
compared with PR3477's `.001695`; their difference is `1/31250`.
These are layer bounds. No integer multiplication exponent, new supplier
admission or enclosing outer transfer follows from this result.

## 2. Exact complete moment

Keep `m=73`, `W=896*74=66304` and the full paid histogram

```
{1:1645680, 2:470196, 3:159468, 4:71928,
 5:13716, 8:5328, 48:28190}.
```

This is the global 666-call bill, including idle remainders. It contains
2,394,506 children and rank mass 4,816,512. It is not a per-call histogram
to be divided by 666 again. Set

```
sigma=998271/1000000,
mu_sigma=(1/W)*sum_r H_r*(r/73)^sigma.
```

`rate.py` authenticates the complete profile and nine-stage, 74-replica call
order. Douglas Colkitt's retained outward log/exp engine and Nick Petalas's
independently implemented PR3342 positive-series engine both enclose the
moment in

```
[999999903535664027556833879161,
 999999903535664027556833879162] / 10^30.
```

Consequently `mu_sigma<1` and `1-mu_sigma>9/10^8`. The geometric-series
constant below is finite, less than `10^8/9`; it is not dropped from the bill.
Both engines use rational arithmetic, with independent logarithm reductions
and outward tail bounds. Their source notices and mathematical attribution
are retained. This package claims no new interval method.

Two failed alternatives matter for acceptance. At the new ordinary exponent
`tau`, the complete moment is strictly greater than one:

```
mu_tau in [1000003022093731739239177793276,
           1000003022093731739239177793277] / 10^30.
```

At `sigma`, adding even one rank-one child makes the moment exceed one:

```
mu_sigma_with_one_extra_rank1 in
 [1000000111677363244276477808366,
  1000000111677363244276477808367] / 10^30.
```

Thus neither a direct ordinary-rate substitution nor an unpriced extra
recursive operation is covered. A physical linear cost remains a physical
linear cost; this test does not assign a rank-one tariff to an unspecified
operation.

## 3. The weighted tree when tau is below sigma

At an internal node of positive selected width `e`, put `f=floor(e/73)`.
Each rank-`r` child has width `r*f<=r*e/73<e`. The retained source volume
accounting, including all cover elements, gives the weighted estimate

```
sum_children V_child * e_child^sigma
    <= mu_sigma * V_node * e^sigma.                 (1)
```

Equivalently, each cover child has volume `V_node/(W*Gamma)`, where
`Gamma=|O(73,2)|`, and summing the complete cover removes `Gamma` once.
The full `H_r/W` factors in (1) already include every charged child.

The new ordinary contract supplies exactly the same nonchild operations
as PR3477, with cost

```
C*V_node*((e*log p)^tau+1).                          (2)
```

This includes complete native monomial routing, gather/scatter, scalar and
private-zero operations, replacement copies, parent parking and their
record-paid setup, under the retained uniform cost premises. The original
root precision and width remain fixed throughout the recursive call.

Here `tau<sigma`. For `e>=1`, `e^tau<=e^sigma`; hence (2) is at most
`C*V_node*e^sigma*((log p)^tau+1)`. Summing (1) over tree levels yields

```
T_internal <= C*V_root*d^sigma*((log p)^tau+1)/(1-mu_sigma).
```

There is no additional depth factor: the level potentials form a geometric
series. This is the changed step. The predecessor inequality
`e^tau<=d^(tau-sigma)*e^sigma`, useful when `sigma<tau`, reverses its useful
direction when `tau<sigma` and `e<d`. We do not reuse it. The present bound
has exponent `sigma`, not `tau`. A general sufficient version uses internal
exponent `max(tau,sigma)`; the replay checks that the new factory is required
to enter the branch used here.

## 4. Stopped leaves, root reservations and strict logarithmic slack

Keep the actual stopping test unchanged:

```
e<73 or e^1000<d,    beta=1/1000.
```

Every stopped positive width obeys `e<max(73,d^beta)<=73*d^beta` for
`d>=1`. Because `mu_sigma<=1`, the sum of the potentials
`V_leaf*e_leaf^sigma` over the stopped-leaf antichain is at most the initial
`V_root*d^sigma`. This follows by replacing any internal node by its
children in (1); the tree is finite because every positive child contracts.
The retained elementary leaf cost `O(V_leaf*e_leaf)` therefore sums to

```
T_leaf = O(V_root*d^(sigma+beta*(1-sigma))),
sigma+beta*(1-sigma)=998272729/10^9.                  (3)
```

The root's existing front/back/depth reservations retain their cost
`O(V*d^(499/500)*log p)` and all fixed-record setup charges. In the direct
branch, `D<=Q0` and the unchanged reservation formula gives
`Q0=O(log(2d)+d^(499/500)*log p+1)`. Its elementary `O(V*(D+1))` bill is
therefore covered by the same reservation bound, even when `D` grows.
An empty selected set still pays its copies. Only the finitely small `p`
range is absorbed by a fixed constant. Root padding by less than two occurs
once, multiplying the whole internal/leaf bill by a constant. It is not
applied afresh at each recursive child.

Put `alpha=998273/10^6`. The complete strict power margins are

| Contribution | Exponent before logarithmic absorption | `alpha` minus exponent |
| --- | --- | --- |
| Internal nodes | `sigma=998271/10^6` | `1/500000` |
| Stopped leaves | `998272729/10^9` | `271/10^9` |
| Root reservations | `499/500` | `273/10^6` |

Since `d=floor(p^(997/1000))`, `log p=O(log(2d))`. For any fixed positive
`delta` and fixed nonnegative `t`, `(log(2d))^t=O(d^delta)` as `d` tends
to infinity. Apply this with strictly positive margins to the internal and
reservation terms. Equation (3) is below `d^alpha` as well. This proves the
stated layer bound, with constants depending on the fixed margins and source.
There is no logarithm deletion at exponent `sigma`, and no claim that
`.001727` is an optimal layer saving.

The enlarged fixed precision guard, numerical height induction, root
normalization, one final truncation and pointwise spectator restoration are
unchanged. PR3562 preserves the ordinary endpoint and numerical/context
contracts; it changes the compiled width choice and its uniform cost. The
existing fixed role/parent-parking space proof therefore continues to apply,
with its fixed constants and successful-return interpretation. No complete
GL64/O73 production execution is inferred from this reasoning.

## 5. Factory binding, controls and remaining boundaries

`factory.py` supplies opt-in `build_native(q)` and `production_layer(prepared)`.
The factory creates the ordinary backend with the PR3562 profile
`numerator=1, denominator=577`, while retaining the selected row factor,
dimension/rank, catalogue, topology, compiled programs, capacities and
`fixture_index_floor=0`. This ordinary object must be the actual native
argument consumed by the T74 machine and root. An unmodified factory using
the old profile still has the old ordinary exponent and does not justify
this claim. The source-bound factory checks exercise this distinction;
they do not construct the impractical production catalogue. The unchanged
live T74 binding is loaded under a private module name, preserving the
native catalogue's distinct archived `binding` module. Scoped import paths
and module-identity checks bind both implementations without modifying
either source. The constructor recorders cover the complete production
entry point; the reduced-root receipt separately reports actual ordinary
method calls, rather than treating an installed object as an executed call.

The exact rate controls reject the old ordinary exponent at the proposed
final rate, an earlier `e^500<d` stop, a target that omits the actual leaf
penalty, and final exponents without the required internal/reservation
logarithmic slack. Both moment engines separately reject the direct
ordinary-moment substitution and one extra rank-one child. Contracts remain
active under Python optimization. These finite checks corroborate the
written all-size implication rather than establishing physical refinement
by enumeration.

The work retains all native/common-label and mutable-source realization,
whole-call hosting, ordinary/C0 physical refinement, complete linear bills,
precision/tape, restoration and recovery premises at their credited scope.
It supplies no actual outer synthetic round, integer packing/error transfer,
full transition table, independent human review or proof-kernel proof.
The selected frontier and predecessor packages remain unchanged.

Marius-Paul Dumitrean and the PR2979 lineage supplied the T74 construction.
Jose Manuel supplied PR3477's physical layer and PR3562's stronger ordinary
coupling; David Arias, Nick Petalas and the retained native/ordinary/compiler
lineage retain their source credit. New material prepared by Hiroki Kumazaki
with substantial OpenAI Codex assistance. Apache-2.0.
