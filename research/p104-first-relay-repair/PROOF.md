# A required repair in the first PR7774 substitution

## Exact scope

Fix the first additional edit in PR7774 at head
`22fff773f897e70a2c346d09de62515fadb1c445`. The input is the joint graph with
SHA256 `126352b5e607b9d8a5863a02ee667de389655e81cfa4175e70e1aa5d0a264771`.
This audit concerns its rational data-flow operator. It does not admit the
complete physical application or change kappa.

The checker rebuilds that input from the published parent graph, the two PR7767
differentials and the reversible PR7774 bridge. It retains those constructors
without changes. The operator expansion, residual calculation and bank
separation below use a separate implementation. This is a source-aware check.

## Substitution and full operator

Let `x` be the value of the removed send 99771. Its source form at chart 712 is

```text
x = value(94070) + value(94072)/2 + 2*value(98998).
```

The edit changes the value sent by 96048 from `y` to `y - 4*x`. It removes
99771 and terminal pivot 104247. It installs paid leg 53 from chart 712 to
chart 127 with value `x`. The other changed rows use the source journal's exact
terminal quotient and restoration coefficients. The checker separately verifies
`old_value(104247) = -new_value(103626) + 2*new_value(103736) + 2*x`
on all input roles. This identity uses the fully edited donor values.

The two removed ranks are 2 and 3. The new rank is 5. There are 5,712 paid
positions before this edit and 5,711 after it. The public boundary is unchanged.
The checker validates every old coefficient before it applies a change. It
checks chart locality, strict transfer nesting and an acyclic order. It expands
every row over all 1,264 independent inputs with exact rational arithmetic.
All 1,264 output rows agree before and after the edit. The two expansions use
23,563,352 scalar coefficient products. This is an exact operator comparison,
not a random-input test.

## Unique slope and repair coefficient

Keep all other edited rows fixed. Replace the source substitution by
`y - lambda*x`, and multiply the value on leg 53 by `rho`. Let `a_i` be the
response of output `i` to a unit pulse at 96048. Let `b_i` be its response to a
unit pulse at leg 53. Leg 53 has only terminal readers. Linearity gives the
complete error on every output:

```text
error_i = x * ((4 - lambda)*a_i + (rho - 1)*b_i).
```

The certificate records all 69 outputs with a nonzero response. Two of them
suffice to prove uniqueness:

| Output role | Chart | a | b |
|---|---:|---:|---:|
| 186 | 196 | -1/4 | 0 |
| 38 | 127 | 2 | 16 |

This two-by-two minor has determinant -4. Also, the coefficient of input role
25 in `x` is -1/2. Thus the operator is correct for every input if and only if
`lambda = 4` and `rho = 1` in this two-parameter family.

Direct rational runs check four wrong parameter pairs and the correct pair.
For example, `lambda = 0` and `rho = 1/2` cancel the error at output 38 but leave
error 1/2 at output 186 on input 25. This control prevents a check of only one
repaired output from accepting an incorrect slope.

## The receiving banks cannot supply the repair for free

Remove leg 53 from the set of available banks. Keep every other paid bank's
function fixed. Allow all 907 retained banks at chart 127, including banks
that might be too late for a specific output. This relaxation gives a proposed
free reconstruction more inputs, so a failure here also applies to any earlier
causal subset.

Exact row elimination gives rank 907 for these 907 bank functions. The required
value `x` is outside their span. The certificate gives an explicit assignment
`w` to 62 of the 1,264 input roles such that

```text
value(bank, w) = 0  for every retained bank at chart 127,
x(w) = -1/16.
```

The checker evaluates both statements directly. Therefore no rational linear
combination of those banks can produce `x`. Adding the required direction
raises the rank to 908. Free scalar operations at chart 127 preserve the
available span. At least one new paid delivery is necessary when the other
bank functions are fixed. The source leg 53 supplies that missing direction.

This statement does not prove that rank 5 is the cheapest possible paid repair.
Several new transfers, changed earlier banks, nonlinear operations and a new
supplier are outside this fixed-bank model. An optional search for a stronger
quotient cost bound was stopped without a result; it supplies no evidence here.

## Relation to the complete submitted word

The checker applies the remaining nine journal entries, validates their old
coefficients and checks the final graph digest
`c048d660a0e77925a91597c3a554c736bab11d870c1753c2c35e5657a4974f48`.
On input role 1, omission of leg 53 changes final output role 19 by -8. This
agrees with the deposited omission witness. It is a separate final-word check;
the first-edit parameter certificate above uses the graph before those nine
later edits.

## Remaining obligations

The proof covers the rational rows, transfer ranks and fixed receiving banks.
Signed Pauli realization, physical integer execution, caller assembly, ordinary
services, directed price and compiler closure are not replayed here. The source
reports those checks. Its five framework assumptions remain. The audit gives
no new complete kappa and no selected-frontier change.

## Open next questions

A cheaper repair requires a changed bank interface or additional paid routes.
Price that change on the complete supplier and caller before it is treated as
a gain. The structured question is in [TASK.json](TASK.json).
