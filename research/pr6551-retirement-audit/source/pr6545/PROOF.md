# A Gaussian output before the suffix

## 1. Exact source and claim

The native source is PR6529 at
`44b0d0e8961201ac1656490b4384a7752e1cd9c5`. Its caller is the PR6398
34-field word. Number events from zero. Let P be its prefix through event 328,
`QUERY 20 21 -1`. Let q denote the central Gaussian Q in the replay.
All 18 stage variables D_j commute with q and with one another.

Set

```text
λ = (1+i)/2 + (1-i)q²/2,
S = λ q⁻¹.
```

Then λ⁻¹ is its complex conjugate, λ² = q², and S² = 1. Thus λ and its
inverse are ordinary linear combinations of the identity and the ordinary
translation q². The retained physical checker verifies the translation and
its absolute phase. These ordinary scalars stay outside tensor powers.

Fields 4, 20 and 21 have the same two-stage factor D = D_10 D_11. An even
central translation and λ normalize all three complete outputs to S D.
The other fields keep their source targets. All input fields are arbitrary.

## 2. Two exact dual pairs

Use row vectors a,c and column vectors b,d:

```text
a = e1ᵀ - 2e2ᵀ - λe20ᵀ + e21ᵀ,
b = -e2 - e21,
c = e20ᵀ - e4ᵀ,
d = -λ⁻¹e21 - e4.
```

The identities are

```text
ab = cd = 1,       aP = Sc,       Pd = Sb.
```

`check_caller.py` checks both pairings and both prefix identities over the full
central polynomial ring. It does not specialize q² to one or test only numeric
values of the D_j.

Let G and J be the literal ordinary basis words in `WITNESS.json`. The checker
also verifies

```text
e4ᵀG = c,     Gd = e4,
e4ᵀJ = a,     Jb = e4.
```

Every gate is invertible. ADD coefficients are dyadic; SCALE uses a dyadic
unit; λ has the stated ordinary inverse. G acts only on fields 4,20,21.

## 3. Separate the completed Gaussian from the remaining work

Apply G⁻¹ at the input. At the cut, apply J. The pivot row and column of
`JPG⁻¹` are both exactly `S e4`. Therefore the pivot has no coupling to the
other inputs or outputs at this cut. In block form, the prefix is `S ⊕ K`.

Let F be the complete source diagonal after the three output normalizations.
Since G mixes only equal S D targets, G commutes with F. Apply G at the output.
The complete map remains `GFG⁻¹ = F`. The suffix after J must therefore have
pivot block D and zero coupling to the other fields: its pivot block times S
is S D. This uses S²=1 and the exact arbitrary-input source identity.

Return the completed pivot output. Give the suffix a new independent input in
field 34. In the literal word, rename pivot 4 to 34 in J⁻¹ and every later gate,
including the output basis. Other fields still pass through K and its matching
suffix. This is a direct sum of two independent targets, S and D, in place of
one S D target. It is not a copy of one input to two output targets.

Finally apply λ⁻¹ to the three original group fields. The returned pivot has
target q⁻¹. The new field has target D_10 D_11. The complete 35-field word has
609 events. Both full forward replay and an independent reverse-row replay
check every one of its 1,225 coefficient positions. Deletion, sign and target
mutations reject the claimed identity.

## 4. Physical maps and all costs

For each of the 104 ports, the central q axis is orthogonal to the two fresh
8-axis stage blocks. The old Gaussian target has rank 17. The returned q⁻¹
target has rank 1 after an ordinary q² translation. The fresh target has rank 16
and no central factor. The physical checker compares complete phase polynomials,
including the absence of that central factor. It checks every port.

At each positive tensor width f, substitute q tensor f and D_j tensor f in
the same ring identity. Define the ordinary normalizer from the square of
that central operator. Do not tensor its scalar coefficients. The two new
Gaussian ranks are f and 16f. This retains the source tensor convention and
its framework assumptions.

The ordered full-stage calls, thin-query signs, and whole-idle stage sets stay
fixed. Only some role names change. Every native call still receives arbitrary
inputs and fresh independent helper fields. All 67,096 paid jobs and all native
helper credits stay in the source invoice. The productive change is exactly

```text
104(H1 + H16 - H17).
```

For H_r=r^t and 0<t<1, strict subadditivity gives H1+H16>H17. Rank mass stays
fixed. The gain comes from independent outputs, not from a larger rank count.
The total productive-field count becomes 13,756.

The caller has one extra public field per port. The native owned inventory is
unchanged: 29 labels, 45 lifetimes, peak 13. The complete ordinary-work upper
bound is 254,699,248, below the retained 10^9 allowance. It includes every scalar
basis gate, central normalization, route and output adapter. The coefficient,
storage, growth and precision estimates remain explicit in `pricing.py`.

## 5. Conditional κ and the fixed invoice limit

Two rational engines certify the positive complete moment at the tested saving
0.003293945. They independently certify both signs of the raw bracket stated
in the README. A negative derivative bound gives a unique crossing through the
retained BIT range. The old caller fails at the new claim in both engines.

The productive recursion, completion tails, uniform compiler threshold and all
outer inequalities are checked with the enlarged target count. The result is
conditional κ=0.00329394 under the same five framework assumptions. No selected
frontier change or independent scientific acceptance follows from this replay.

The fixed invoice cannot reach the current 1% target 0.00332118199. A larger
result must change the caller, source word or another charged interface. More
digits of this crossing do not provide that change.
