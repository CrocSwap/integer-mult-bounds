# A fused nearest Gaussian grid map

All claims in this note use indexed integer words. They do not give a reversible
Boolean circuit, a tape route, a funded native provider, or a new kappa value.
The grid spacing is h. The code uses h = 1; scaling gives the other grids.

## The four-point map

Let L = Z[i]^4. Let C have diagonal (1+i)/2 and off-diagonal (1-i)/2.
For F = C tensor C, the numerator matrix 2F is

```
i   1   1  -i
1   i  -i   1
1  -i   i   1
-i  1   1   i
```

Thus F is unitary, fixes the sum, and has F^2 equal to simultaneous exchange
of both bits. In particular, F^4 = I. These are classical radix-four identities.

For x in L, define the two bits

```
a = (Re x0 + Im x1 + Im x2 + Re x3) mod 2
b = (Im x0 + Re x1 + Re x2 + Im x3) mod 2.
```

Direct multiplication of the displayed matrix shows that
K = L intersect F^-1 L is the class (0,0). It has index four. Moreover F(K) = K:
if x is in K, then Fx is integral and F(Fx) = F^2 x is integral. Apply the same
argument to F^-1 for equality. Complex conjugation leaves K unchanged, so the
same statement holds for F^-1.

Set c_ab = (a,b,0,0), with real entries, and let sigma(a,b) = (b,a). Define

```
G_s(x) = F^s (x - c_ab) + c_ba,       s in {-1,1}.
```

The first term is in K. The output class is therefore (b,a). Applying G_-s
subtracts exactly c_ba, applies F^-s and adds c_ab. It returns x. This proves
bijectivity and the stated inverse on all of L, without a rounding transcript.
The same calculation four times gives G_s^4 = I. Both representatives have
complex sum a+b. Since F fixes the sum, G_s fixes the sum exactly.

The error is the constant vector c_ba - F^s c_ab on each class. Substitution
in the matrix shows that every real component is 0 or plus or minus 1/2, and
that its squared norm is a+b. The fractional parts of F^s x are the same as
those of F^s c_ab. Thus each output component is a nearest grid point.
Every integral output has squared error at least a+b. This kernel attains
that minimum for every input. The uniform block bound sqrt(2) h is sharp on
class (1,1). This is a local optimum among all integral outputs, even if no
inverse or sum condition is required.

## Literal implementation and range

Write D = diag(1,-i,-i,-1). Then F = i D H4 D / 2, where H4 is the unnormalised
Walsh matrix. The code subtracts the two input bits, applies these phases,
uses the two-stage Walsh circuit, divides its eight even real entries by two,
applies the output phases and adds the exchanged bits. For s = -1 it uses the
conjugate phases. This is the displayed map, with no floating-point arithmetic.

Each block uses 20 real additions or subtractions, six real negations, four
component exchanges, eight exact half shifts, six parity XORs, eight parity
bit reads, eight input component reads and eight output component writes.
There are 42 checked intermediate values. The code also tests the eight
half-shift parities. Loop, index, format and width-test work is additional.
No allocation, branch, address calculation or check is assigned a zero tape
cost. The retained source uses 40 real additions and eight half shifts for
its four pair calls on the same two axes. Only the additions are halved.

If every input component has absolute value at most the integer A, then every
centred Walsh intermediate has absolute value at most 4(A+1). The output
components have absolute value at most 2A: the exact component lies in
[-2A,2A], and a nearest integer stays in that interval. A signed width B with
2^(B-1) > 4(A+1) suffices. The implementation checks all actual intermediates
and rejects overflow. It does not saturate or wrap. This bound is sufficient;
it is not a minimum-width claim.

## Whole calls and ports

For a field with N = 8^f entries, pair active axes in their literal order. Apply
G on the N/4 blocks of each pair. Use the retained conservative C kernel on a
last unpaired axis. Reverse the group order and signs for the inverse.
Each group has error at most E0 = h sqrt(N/2), including a singleton group.
The ideal groups are unitary. Induction and the triangle inequality give

```
||rounded_call(x) - ideal_call(x)||_2 <= ceil(f/2) E0.
```

The retained stagewise certificate is f E0. This reduces that certificate
by a factor two when f is even. It does not prove that the complete-call
worst case attains either triangle bound. For one four-point block, each
old stage has error at most sqrt(2) h. The receipt gives an input and sign
with squared error 8 h^2. Thus the old block maximum is exactly 2 sqrt(2) h,
and the new sharp block maximum is smaller by a factor two. This conclusion
uses both the all-input old bound and the exact attained witness; it is not
an extrapolation from the finite box.

Each complete call uses 5 N ceil(f/2) data additions and N f half shifts.
Each paired group also uses 3N/2 negations, N exchanges, 3N/2 parity XORs,
2N parity reads, 2N component reads, 2N component writes and 21N/2 width checks.
It scans N indices and executes N mask tests. The final singleton uses the
unchanged source pair implementation, including its centre selection.
Every block preserves its sum. Hence every one of the 4^f spectator-fibre
complex sums is preserved. The literal reversed call returns every input.

The retained ports use the exact monomial routes and the mix P + 2Q. Its
operator norm is at most three. Write E = ceil(f/2) E0. In a forward port,
the first bank has error at most E; the second has at most 3E+E, or 3E+E+E
for the three-call port. In a reverse port the first bank still has at most E
and the second has at most 2E. Thus 5E bounds either bank in both directions.
The code checks every paid cut against the independent direct-convolution
oracle. Reversing the exact port order cancels the bijective calls, monomials
and integer mix. Both dirty banks return exactly. This argument does not use
linearity of the rounded map. The inherited indexed routes are not a physical
tape or Boolean implementation.

## Lost identities and scope

The representative choice changes the contract. With e0 = (1,0,0,0),
G(e0) = e1, but G(i e0) = i e2. Global Gaussian phase covariance fails.
Also G^2(e0) = e0, whereas F^2(e0) = e3. The ideal square rewrite fails.
The checker retains both counterexamples. The order-four identity and the
literal inverse still hold. Do not replace a selected native child with this
kernel until all caller uses of these lost identities have been checked.

The residue census checks 65,536 inputs and both signs. It is finite evidence,
not the proof of the all-input statements. The coset calculation above is that
proof. Complete call and dirty-port tests cover f = 1,2,3. The extension to all
f follows from the displayed tensor grouping and inverse-order argument.
