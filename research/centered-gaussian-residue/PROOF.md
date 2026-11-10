# A centered child for the paid Gaussian residue lane

This proof was produced by Nick Petalas. Apache-2.0.
Claim type: scoped constructive written proof with finite exact corroboration.

The question is PR3926 Open next question 2. ToikY supplies the attained
unsigned child-size theorem. David Ganz / Dugongue's PR3881 supplies the paid
residue-assisted Gaussian lane and its numerical recovery theorem, building
on Mason Hale's Gaussian backend, normalization, CRT ordering and carry scan.
Those results are cited premises. The new step replaces only the exact lane's
packing and extraction. Signed Kronecker substitution is classical.

## Signed coefficient separation

Let two nonempty arrays have lengths A and B, and let k>=1. Put

```text
q = 2^k, a = q/2, m = min(A,B), h = ceil(log2 m),
w = 2k-1+h, beta = 2^w.
```

Replace every original nonnegative digit x by its unique congruent value
`c(x)` in `[-a,a-1]`. Pack the centered arrays as the signed integers

```text
U = sum_i c(x_i) beta^i, V = sum_j c(y_j) beta^j.
```

One multiplication of the nonnegative magnitudes |U| and |V|, followed by
the known product sign, supplies UV. Sign handling, packing and extraction
are additional work, not free operations or extra recursive products.

For output coefficient j let nu_j be its number of summands. Each summand
lies in `[-a(a-1),a^2]`, so its exact signed convolution coefficient C_j is
in the integer interval

```text
l_j = -nu_j a(a-1) <= C_j <= u_j = nu_j a^2.
```

This interval has diameter

```text
u_j-l_j = nu_j(2a^2-a) < 2m a^2 <= 2^(2k-1+h) = beta.
```

Consequently at most one integer in this interval represents a given residue
modulo beta. Starting with P=UV, recover successive coefficients by

```text
C_j = l_j + ((P-l_j) mod beta),
P = (P-C_j)/beta.
```

The first congruence identifies the genuine C_j because every higher term
is divisible by beta. After subtraction and division the same argument
applies to the next coefficient. Induction recovers every coefficient and
leaves P=0. This argument works with negative packed values and floor
division because the numerator is exactly divisible. Reducing C_j modulo
q gives the original unsigned convolution coefficient modulo q.

The asymmetry is necessary at this width. For k=2 and two entries per
array, the arrays (-2,-2) have convolution (4,8,4), with middle coefficient
exactly beta/2=8. A symmetric half-open decoder would choose -8. Using
ordinary unsigned extraction on a negative packed product can also introduce
spurious higher coefficients. The interval algorithm addresses both cases.

The retained unsigned lane uses w_old=2k+h. The construction therefore saves
exactly one bit per slot at every k and positive overlap. This is a sufficient
new slot rule, not a claim of minimum width over every possible packing.

## Attained magnitude bit length

Now both arrays come from a declared n-bit integer in base 2^b, with
1<=k<=b. Let

```text
L = ceil(n/b), t = n-b(L-1), h = ceil(log2 L), w = 2k-1+h.
```

The exact largest bit length of the packed magnitude, with bit_length(0)=0,
is

```text
D_center(n,b,k) = min(k,t) + (L-1)(2k-1+h).
```

For L=1, reduction and centering give a maximum magnitude-bit length k if
t>=k, attained by the digit a. If t<k the top digit never reaches a, and
its largest possible bit length is t. This proves the formula for L=1.

Suppose L>=2. If t>=k, every centered digit has magnitude at most a, so

```text
|U| <= a sum_(i=0)^(L-1) beta^i < 2a beta^(L-1).
```

Thus its magnitude-bit length is at most k+(L-1)w. A top digit a and all
lower digits zero give U=-a beta^(L-1), attaining this bit length.

If t<k, the top digit is nonnegative and at most 2^t-1. Also beta>a+1,
because L>=2 implies h>=1 and beta>=2^(2k). The lower part has magnitude

```text
a sum_(i=0)^(L-2) beta^i < beta^(L-1).
```

The complete magnitude is therefore strictly below 2^t beta^(L-1).
A top digit 2^(t-1) and all lower digits zero attain bit length
t+(L-1)w. These input digits are legal in the declared n-bit domain.
This proves the formula and its attainment, including partial top digits.

Subtracting it from ToikY's cited unsigned formula gives exactly L-1 saved
operand bits. Both recursive child operands use nonnegative magnitudes.
The product may have twice their bit length; no output-size or total-cost
reduction is inferred from the input bound alone.

## The new uniform tail in the retained box

Retain b=64 and the PR3881 source box of size 455, which permits
L<=228 because 2L-1<=455. At k=28 the new width is w=55+h<=63.
For L>=2,

```text
D_center <= t+63(L-1) < t+64(L-1) = n.
```

For L=1 and n>=29, D_center<=28<n. Therefore every declared width
29<=n<=14592 has a strictly smaller k=28 child. The old fixed uniform
tail used k=27; its k=28 layout fails at n=8193, as already proved in
PR3926. This is a changed layout, not a correction of that exclusion.

At n=14592, L=228 and t=64, the new k=28 child has sharp maximum
28+227*63=14329 bits. The cited unsigned bound is 14556 bits.
At n=8193, L=129 and t=1, the new sharp bound is 8065 bits.

The new layout does not permit a uniform k=29 tail: at n=8193 its
sharp bound is 1+128*65=8321 bits, which exceeds the parent width.
The formula increases with k, so every k>=29 also fails there. Hence
28 is the largest fixed k in this new slot scheme with strict shrinkage
throughout its supported tail k+1..14592. This is not a bound on other
packing algorithms or Gaussian certificates.

PR3926's cited fixed numerical certificate has least p=208-k. Its
Gaussian proof depends on the residue value modulo 2^k, not on this lane's
choice of representatives. The new lane supplies exactly the same residues,
so its recovery implication applies at k=28,p=180 for the entire new uniform
tail. The previous k=27 uniform tail used p=181. This is one fewer rounded
payload bit under that sufficient certificate; Q=448 is unchanged.

The universal recovery statement remains conditional on the credited backend
and numerical proof premises. The new boundary replay replaces the lane in
the unchanged source caller and executes p=180 at n=8193 and n=14592,
including an attaining packed magnitude and negative packed operands.
Reference products and schoolbook coefficients are used only after recovery.

## Remaining obligations

This settles a changed-packing/strict-child interface question. It does not
price the complete numerical transforms, pointwise products, sign handling,
packing, signed extraction, lifting, carry, preparation, physical movement,
storage or restoration. In particular a smaller child need not reduce total
time. No all-size recursion/base-case policy, actual native supplier, selected
admission, new kappa or complete multiplication theorem follows. The five
selected framework assumptions remain open. Independent human and formal
proof-kernel review are unclaimed.
