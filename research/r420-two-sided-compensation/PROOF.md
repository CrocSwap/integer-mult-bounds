# Restored helper matching and shared target donors for R420 compensation

This is a proof of a finite circuit substitution over **F2**. It applies to the
pinned PR543 word in `../e8-bit-r420/data/bitE8mut-r420.json.gz`, at the base
commit recorded in `CLAIM.json`. It does not establish a new kappa, an optimal
circuit, an integer endpoint identity, or an all-size multiplication theorem.
The numerical receipt and the frozen recipe must be checked separately against
the emitted word; the argument below explains the exact identity they certify.

## Interface and notation

Write the initial state as `(x, s, y)`, with 120 source coordinates, 420 arbitrary
helper coordinates, and 120 arbitrary target coordinates. These are the native
register ranges `0:120`, `240:660`, and `120:240`, respectively. The order in
this mathematical tuple is not the order of the native register numbers.
Every helper and target starts at frame zero. The original D consists of 120
grouped gates, containing 19,922 binary ADDs, and has the map

```
(x, s, y) -> (x, s, y + K s),       K in F2^(120 x 420).
```

Here `K[t,j]` is the parity of occurrences of helper register `240+j` in
original D gates with target destination `120+t`. Counting parity rather than
presence is necessary for a general extractor. The pinned source has the
literal helper-to-target form, so its 19,922 binary ADDs equal `wt(K)`.
`wt` denotes the number of nonzero matrix entries, not a gate-record count.

The semantic replacement for the original syntactic H2 condition is:

1. D runs first, and each of its operands is a helper or target at frame zero.
2. D uses legal binary XORs with distinct source and destination registers.
3. Its complete operator is `(x,s,y) -> (x,s,y+Ks)` for arbitrary inputs.
4. Every field outside D is identical to the pinned source word.

The original H2 demands only helper-to-target gates. The replacement contains
helper-to-helper and target-to-target gates and therefore needs this explicit
semantic interface. The original H2 predicate and its literal D extractor do
not become proofs for the replacement merely because the endpoints agree.
No alteration of a predecessor checker is justified by this argument.

## Basis identity

For distinct coordinates `a,b`, let `E_ab` be the matrix with a single one in
row `a`, column `b`. The instruction `s_a += s_b` applies
`I + E_ab`. Since `E_ab^2 = 0` and the characteristic is two,

```
(I + E_ab)^2 = I.
```

Choose `p` oriented helper pairs with disjoint endpoints and let `H` be the
product of their transvections. The factors commute and are involutions, so
`H^-1 = H`. No helper may appear in two helper pairs.

For targets choose a donor set S and a receiver set R with `S intersect R`
empty. Each receiver a has exactly one assigned donor b in S, while the same
donor may serve several receivers. Let q be the number of receivers, set
`N = sum E_ab` over these assignments, and set `T = I + N`. For any two
selected terms,

```
E_ab E_cd = delta_(b,c) E_ad = 0,
```

because b is a donor and c is a receiver. Thus `N^2=0`; all these target
transvections commute; their product is `I+N`; and `T^2=I` over F2. A target
may occur as a donor many times, but no receiver may be used as a donor.
The helper and target transformations act on distinct register banks.

Set `L = K H` and `M = T L = T K H`, with all products over F2. The replacement
executes these stages:

1. Prepare helpers: `s' = H s`.
2. Prepare targets: `y' = T y`.
3. For each nonzero entry of M, add that prepared helper to that target:
   `y'' = y' + M s'`.
4. Restore targets with the chosen target transvections in reverse order.
5. Restore helpers with the chosen helper transvections in reverse order.

The two restoration stages may be exchanged because they have disjoint
register banks. In either order the final state is

```
s_final = H H s = s,
y_final = T (T y + (T K H)(H s)) = y + K s,
x_final = x.
```

Writing `H=I+Q` makes the required middle matrix explicit:

```
M = (I+N) K (I+Q) = K + KQ + NK + NKQ.
```

The mixed term `NKQ` cannot be omitted when combining the two sides. This is
also why target scores must be recomputed on KH.

Thus this realizes the required D operator for **all** helper and target
inputs. Target preparation is essential: performing only the feed and target
restoration would give `T y + K s`, which can pass a test initialized with
`y=0` while failing the required arbitrary-input contract. Helper restoration
is independently essential to the state presented to phase A.

All feed operations write a target and read only a helper. Their effects
commute, as no feed writes a source for any other feed. The proof therefore
permits their deterministic order in the frozen recipe. Preparation and
restoration are distinct paid operations even though each pair composes to
the identity when the feed is absent.

## Exact scoring and paid cost

An oriented helper operation `s_a += s_b` replaces **column b** of K by
`K_b + K_a`; column a is unchanged. Consequently its reduction in feed cost,
after paying its preparation and restoration, is

```
g_H(a,b) = wt(K_b) - wt(K_b + K_a) - 2.
```

This orientation matters. The coordinate changed in the helper state and the
column changed in the feed matrix are different. Disjoint pairs modify
different columns without changing the columns used by another pair, so the
helper gains add exactly. This gives

```
wt(K) - (wt(KH) + 2p) = sum g_H(a,b).
```

An oriented target operation `y_a += y_b` replaces **row a** of L by
`L_a + L_b`; row b is unchanged. Its paid gain is

```
g_T(a,b; L) = wt(L_a) - wt(L_a + L_b) - 2.
```

These gains remain additive with shared donors: each receiver row is changed
once, and every donor row remains unchanged. They must be scored on `L = KH`,
after helper factoring. Adding a target-only saving measured on K to a
helper-only saving measured on K would not establish the saving of the
combined construction. For the actual combined word,

```
D_ADDs = 2p + wt(TKH) + 2q,
saved  = 19,922 - D_ADDs
       = sum g_H(a,b) + sum g_T(a,b; KH).
```

Every grouped gate contributes one binary ADD per listed source. The complete
source word has 26,916 binary ADDs, of which 6,994 lie outside D, hence
`complete_ADDs = 6,994 + D_ADDs`. A strict finite improvement requires a
positive computed saving after all four basis passes are included.

For the final frozen `recipe.json`, `p=202`, `q=68`, `wt(KH)=12,584`, and
`wt(TKH)=10,970`. There are 47 nominated donors, all of which are used, and
68 distinct receivers; the two sets are disjoint. Thus the helper-only cost
is `12,584+404=12,988`, and the final D cost is `10,970+404+136=11,510`.
This saves 8,412 ADDs relative to the source, including 1,478 beyond this
recipe's own helper-only pass. The full word has `6,994+11,510=18,504` ADDs.
These counts were independently checked by set-valued matrix updates and an
all-input D replay. They do not depend on assuming that the 202-pair helper
matching equals PR694's different, 201-pair matching with the same 12,988
helper-only cost.

## Fixed-donor assignment and bounded search

Fix L and a nominated donor set S. The admissible target class in this
section has at most one donor per receiver, no receiver in S, no constraint
on donor reuse, and the two paid ADDs already included in each gain. For
each target a outside S, the best available contribution is

```
f_a(S) = max(0, max_(b in S) g_T(a,b; L)),
F(S) = sum_(a not in S) f_a(S).
```

For empty S take each `f_a(S)=0`. Every admissible assignment has a contribution
at most `f_a(S)` at receiver a. Conversely, choosing a maximizing donor for
each a with positive `f_a(S)` attains every term simultaneously: donor reuse
is allowed, receivers are distinct, and no receiver changes a donor. The
sum F(S) is therefore the exact best saving **for this fixed donor set and
this one-donor-per-receiver class**. The independently checked final value
is `F(S)=1,478`.

The construction first uses the seed-3 greedy helper matching, followed by
the original greedy disjoint target matching on KH. Its 56 target donors
seed S. Allowing their reuse yields an initial fixed-donor optimum of 1,401
saved ADDs beyond the helper-only word, compared with 1,395 for the original
disjoint target matching. The bounded refinement examines single-donor
additions and removals, chooses a strictly improving toggle, and recomputes
the fixed-donor best assignment. It allows at most 30 such improvement
iterations. The frozen trace contains the initial state and 15 strict
improvements, ending at 47 donors and saving 1,478. Thus the final circuit
saves 83 ADDs beyond the initial 8,329-saving disjoint construction.

The fixed-S argument is a restricted optimality statement about assignments,
not about choosing S. Neither the greedy helper choice nor this bounded
donor refinement proves a global donor-set optimum, optimality among
two-sided bases, or optimality among arbitrary D circuits. Allowing more
than one donor at a receiver would change the admissible class and its cost
calculation. The construction makes no claim for that larger class.

## Composition with the unchanged suffix

The pinned PR543 scalar interface gives its raw `(A, scatter, B)` suffix the
form

```
(z, y) -> (U z, y + J x + K s),       z = (x,s), J = I,
```

and its cleanup C restores z by applying `U^-1`. In particular, the raw
target-to-target operator is the identity. At the end of the replacement D,
the helpers equal their original arbitrary input, while the target input to
the suffix is `y+Ks`. The unchanged suffix therefore returns

```
(x, s, y + K s + x + K s) = (x, s, y+x)
```

over F2. This argument uses the pinned suffix's verified interface; it does
not infer correctness from a zero-helper or zero-target simulation.

Since all 660 initial coordinates are independent and every operation is
linear, exact agreement on their 660 basis columns proves agreement for
every F2 input. A verifier should check the D operator itself and replay the
whole changed word. The direct matrix proof and the full replay have
different roles: the former explains the substitution, while the latter can
detect an incorrect extractor, orientation, recipe, or emitted instruction.
Reverse replay must also use the actual reversed word; involutivity of the
desired endpoint alone is not a check of the emitted reverse stream.

## Frames, resources, and the conditional boundary

Every inserted operation touches only helpers and targets before their first
climb. They all occupy the identical zero frame. No inserted operation
requires a MOVE, COPY, ERASE, new register, or nonzero-frame source support.
At the D boundary the helper contents and all register frames equal those
of the original D boundary. Fields outside D are unchanged, so the existing
frame paths, nine retained copies, 420 helpers, and local rank histogram are
preserved. The histogram is

```
{1:1320, 2:1440, 4:60, 5:120, 8:9},
```

with rank mass `1*1320 + 2*1440 + 4*60 + 5*120 + 8*9 = 5,112`.
Literal stream comparison should confirm that its MOVE/COPY/ERASE subsequence
is unchanged. Merely retaining the same histogram would be weaker evidence.

Extending this finite scalar substitution to the project's physical
realization still invokes the inherited common-label/mutable-basis interface:
an XOR of coordinates sharing a label must implement that XOR regardless of
the current meaning or role of those coordinates. Frame-zero helper mixing
and target mixing do not prove that all-size interface. This package does
not discharge the hosted-parent reconstruction, physical owner routing,
whole-owner invoice, precision/tape bounds, or changed-word outer assembly.

## Positive integer prefix accounting is separate

The cancellation `H^2 = T^2 = I` holds over F2. It does **not** mean that two
positive integer ADDs undo each other. For example, over integers the pair
`s_a += s_b; s_a += s_b` leaves `s_a + 2s_b`. It consumes two ADDs and can
increase a cancellation-free prefix bound despite being F2-neutral.

The changed stream therefore needs fresh forward and reverse positive-prefix
calculations. In a native record replay initialize each live input bound to
one and scratch to zero; for an ADD of coefficient c use
`bound[dst] += abs(c)*bound[src]`, for COPY copy the appropriate bound, and
for ERASE reset scratch to zero. Record the maximum throughout the actual
chronological stream. Apply the same rule to the actual reversed stream,
including the reversed COPY/ERASE lifecycle. For the all-positive local
stream these are its exact cancellation-free row-sum bounds; taking absolute
values in a signed reverse stream gives the corresponding safe majorant.

A lower XOR count, an unchanged endpoint matrix, or an unchanged movement
profile implies no reduction in this prefix quantity. A verifier must derive
any stated local payload allowance from the changed bounds and check its cap
afresh. Passing the inherited local 104-bit cap would be a local condition,
not permission to reuse a hosted global invoice. No signed integer endpoint
equality or preservation of the old positive-prefix bound is asserted here.

The final changed-word native replay reports cancellation-free prefix bounds
203,415 forward and 4,284,358 reverse, and a local payload allowance of 103
bits. These are changed-stream accounting results, separate from the F2
basis identity; they remain below the 104-bit local cap without establishing
a revised hosted or global invoice.

## Attribution and scope of the extension

The underlying R420 word and its scalar-interface proof are eumemic's
[PR543](https://github.com/CrocSwap/integer-mult-bounds/pull/543), with its
cumulative predecessor lineage and conditional interfaces retained.
[PR686](https://github.com/CrocSwap/integer-mult-bounds/pull/686), by Mikhail R.
Gadelha, establishes restored one-pair helper factoring and the semantic D
contract; [PR694](https://github.com/CrocSwap/integer-mult-bounds/pull/694), by
Greer Guthrie, extends that helper mechanism to a disjoint matching.
[PR713](https://github.com/CrocSwap/integer-mult-bounds/pull/713), by Scott
Woolsey Biggart, supplies restored target-basis factoring; and
[PR716](https://github.com/CrocSwap/integer-mult-bounds/pull/716), by Sagar
Thakrar, supplies a stronger target-only matching with a certificate of
optimality restricted to that one-sided class. The reversible target-factoring
precedent [PR476](https://github.com/CrocSwap/integer-mult-bounds/pull/476) is
also credited through that lineage.

[PR733](https://github.com/CrocSwap/integer-mult-bounds/pull/733), by Scott
Woolsey Biggart, already combines a restored helper matching with a restored
disjoint target matching on the transformed matrix. Its reviewed head is
`dfe84e09298abc5c5e0074afda59a821e10abfb4` and it reports 8,368 saved ADDs.
[PR742](https://github.com/CrocSwap/integer-mult-bounds/pull/742), by
`@ellipsi2`, permits shared target donors while leaving helpers unchanged;
its reviewed head is `6e7a5d271a123886dc7b54ca3180d0b9f9beda5a`. It also
provides the fixed-donor best-assignment argument. Both appeared in the
overlap evidence before finalization and are credited directly.

The limited extension studied here is a frozen **helper matching plus shared
target donors** on KH, with target gains recomputed after the helper pass,
one bounded donor-set refinement, and every operation paid. Neither the
two-sided composition from PR733, shared-donor mechanism and fixed-donor
lemma from PR742, earlier one-sided mechanisms, reversible basis changes,
nor the semantic D contract is claimed as new. The 8,412 saved ADDs are 44
more than PR733's reported 8,368, but its helper basis is different; that
comparison does not isolate a 44-ADD effect of shared donors on its circuit.
The controlled comparison on this package's own fixed helper basis is the
83-ADD reduction above. This proof establishes neither priority nor an
overall circuit record, and any later overlap remains a submission concern.
