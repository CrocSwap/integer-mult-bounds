# Exact contact-block contraction

The source is PR6353 at `db2a20bc50bc7a8a4db931af85ce7f012ae7c3c3`.
The consumer is the unchanged PR6348 binary query tree. The construction
extends the source's joint input and departure basis method. It changes a
contact block that earlier searches excluded. The complete endpoint and
native checks replace that earlier unchanged-contact restriction.

## 1. Two input directions

Transpose the source with the retained native rule: reverse chronology,
transpose scalar updates, complement native frames and exchange main roles.
Let `Z` be frame 3 and `Omega` be frame 127 in this transpose. Let `A` be the
complete scalar preparation at `Z`, including the nine old temporary rows.
No owned transport enters or leaves `Z`. All scalar work at `Z` can move to
the front in its original order. Each public field leaves `Z` at most once.

Use anchors `a=224` and `b=227`. Both are independent `Z -> Omega` helpers.
Let

```text
v = e227 + e228 - e229 - e232 + e233 - e238 + e239 - e449
u_a = 2e224 + v
u_b = 2e224 - v.
```

The reversible basis `B0` has these two columns. Its anchor block is

```text
[2  2]
[1 -1].
```

Its determinant is `-4`, a unit over the dyadic rationals. The other changed
rows add the new row 227 with the signs in `v`. BASIS.json and the constructor
give the exact ADD and SCALE sequence. Every basis coordinate is a full helper.

The first destination of both anchors is dual frame 1091, denoted `G`.
It has dimension five and contains `F=span([30])`, which is dual frame 245.
Rows 193, 169 and 742 have the same first destination `G`.

In the departure block at `G`, form the two rows

```text
row193 + row742/2
row169 + row742/2.
```

Move them into the physical anchor positions by reversible SWAP operations.
Their evaluations on `(u_a,u_b)` are `(1,0)` and `(0,1)`. Subtract multiples
of these rows from each other row in the same departure block. Call the
resulting block basis `C`. All other rows in that block now have zero response
to both directions. This basis can be applied at `Z` and reversed at `G`.

For each anchor row `c_r` of `C A`, exact rational calculation gives

```text
c_r B0 = e_r^T + d_r,
support(d_r) is contained in the other full helper coordinates.
```

Set `B2 = I - e_a d_a - e_b d_b`. Both `d` rows vanish on both anchors.
Thus `B2^-1 = I + e_a d_a + e_b d_b`, and `c_r B0 B2 = e_r^T`.
The constructor checks every coefficient, not a modular sample.

## 2. Arbitrary inputs and legal insertion

Keep both actual anchor inputs arbitrary at `F`. Use zero owned rows 779 and
780 in their places during `B2`, `B0`, `A` and `C`. The previous nine zero
temporaries use labels 770 through 778. These lifetimes are disjoint in label.
The constructor proves that all eleven temporary rows are zero at their
preparation CLEARs. It does not infer this from erasure permission.
This zero-row claim concerns the transposed preparation. A forward CLEAR can
erase a nonzero functional. The inherited owned-erasure assumption remains.

The missing columns are `C A B0 e_a` and `C A B0 e_b`. They have support only
in the two primary rows at `G` and in rows whose first destination is `F`.
The full response table is in BASIS.json. Move the latter rows from `Z` to
`F` with their unchanged paid transports. Add both missing input responses
there. Move each actual anchor directly from `F` to `G`. This replaces its
old rank-five `Z -> G` transport with a rank-four transport.

Move the remaining members of the `C` block to `G` and apply `C^-1`.
Every prepared value then agrees with the original source on input basis
`B0 B2`. Keep the rest of the source events in order. At `Omega`, apply
`B0^-1` and then `B2^-1`. These act only among equal full helper maps and
restore every independent endpoint.

This proves the construction for every public input. The common-frame
induction supplies the native relation at each tensor width. The unchanged
native checker verifies every local chart map and its absolute phase.
The argument does not distribute a tensor power over a sum of operators.

Transpose back and restore the source's exact coordinate bases. The scalar
endpoint remains the required identity plus the main updates. Inputs and
the main boundary are unchanged. Only helper outputs 224 and 227 change:
each now ends in source frame 245, of dimension eight, rather than `Omega`.

## 3. Complete signed improvement

Both output target ranks decrease from nine to eight. The only paid rank
changes are two rank-five transports replaced by rank-four transports.
With `H_r=r^t`, the local margin change is

```text
2(H8 - H9) - 2(H4 - H5)
= 2[(H5 - H4) - (H9 - H8)].
```

For `0<t<1`, the function `x^t` is strictly concave. Its increment on `[4,5]`
is larger than its increment on `[8,9]`. The displayed difference is positive.
This proof also gives weak improvement for every increasing concave tariff;
a linear tariff gives equality. Both paid and target rank masses fall by two.

There are 19 full copies in the fixed caller. Thus its exact paid change is
`38H4-38H5`, and its target change is `38H8-38H9`. All other paid jobs, queries,
paired idles, main outputs, routes and adapters remain in the bill. Recounting
the emitted caller agrees with its separate tree formula. The result has
70,656 paid jobs, 14,214 productive fields and rank-mass surplus 808.

The rational crossing lies strictly in
`(0.00315087900390, 0.00315087900391)`. Use tested saving `0.003150875` and
claim `0.00315087`. Two interval engines agree. The old supplier with this
same caller fails at the new claim. All completion, tail, compiler and outer
checks pass at the declared values.

The new word has 17,757 events and 43 owned lifetimes, with peak storage 13.
The scalar allowance is 129,618, up by 924. The retained ordinary-work reserve
funds this increase and both new lifetimes. No owned row receives a target
credit. The unchanged proof engines and all five framework assumptions remain.

## 4. Scope

This is a source-bound conditional improvement. It is not a proof of a global
optimum, a new selected frontier, a materialized rounded multiplier or a
practical speedup. The gain is about 0.00952 percent.
