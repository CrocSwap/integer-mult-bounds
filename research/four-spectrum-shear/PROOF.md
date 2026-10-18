# Six same-phase reads for a full-spectrum rank-three shear



Let the required complete role map at character value z be

```text
S(z) = I + (z-1)N,       N^2=0,       rank_C N=3,
z in {1,i,-1,-i}.
```

The ordinary example has three independent dirty sources x_j and targets y_j,
with `y_j += (C-I)x_j`. Every x and every other workspace role is restored.
Arbitrary fixed invertible changes of role coordinates give the general N
above. The same constants must work at all characters.

The alphabet consists of constant invertible complex role gates and paid
single-role calls to C or C^-1. A call has determinant z or z^-1.
**The minimum is six calls.** Three separate compute/read/uncompute transfers
attain it using six calls and six signed role ADDs. The lower bound allows
more constant mixing and more arbitrary-dirty roles than that construction.

For spectrum {1,i}, CERTIFICATE.json contains eight four-call words. Rank
forces at least three calls, and determinant parity excludes three, so four is
minimal in that binary-spectrum alphabet. That shortcut fails under simultaneous four-value interpolation.
The result here does not assume constant mixers are unitary or well-conditioned.
It also does not apply if C^2, Pauli/address operations, or other
character-dependent gates can be inserted for free. Calls to other phase
functions are not covered. A fixed-spectrum read count is not an unrestricted
multiplier circuit bound or a rank-moment bound across heterogeneous children.

## Normalize the word and reduce to four calls

At z=1 all paid calls are identity and S(1)=I, so the product of constant
gates is identity. Absorb those gates into conjugations of the paid calls.
For four calls the whole word therefore has the form

```text
F(z) = R_4(z) R_3(z) R_2(z) R_1(z),
R_j(z) = I + (z^epsilon_j-1) a_j b_j,
epsilon_j in {+1,-1},       b_j a_j=1.
```

All a_j and b_j are constant complex vectors/covectors. The normalized
projectors need not be self-adjoint. This normalization accommodates any
number of interleaved constant role gates.

At z=i, rank(F-I)<=number of calls, whereas rank(S-I)=3. Determinant one
requires `sum epsilon_j=0 mod 4`, excluding every odd call count. Thus
fewer than six calls could only mean four.

Set `Y=im N` and `V=span(a_1,...,a_4)`. Since im(F-I) is contained in V,
Y is contained in V. Hence dim V is three or four. Also N vanishes on Y.
If dim V=4, then rank(N restricted to V)<=1. These statements use the full
restoration contract; a restricted clean-input subspace would not suffice.

## Case 1: four independent phase directions

Choose coordinates with a_j=e_j for j=1,...,4, extending them to all roles.
Later reflections modify only their own rows, so the first two rows of F
come entirely from the first two calls.

If every epsilon is positive, F is a matrix polynomial of degree at most
four. Agreement with S at all four roots gives the formal identity

```text
F(z) = I + (z-1)N + (z^4-1)K
```

for a constant matrix K. Row one has degree at most one and row two at most
two, so both corresponding rows of K vanish. Writing g=z-1, those rows are

```text
e_1^T + g b_1,
e_2^T + g b_2 + g^2 (b_2 a_1)b_1.
```

Coefficient comparison gives `N_row1=b_1`, `b_2 a_1=0`, and
`N_row2=b_2`. Since b_1 a_1=b_2 a_2=1, their first two columns have
determinant one. Thus rank(N restricted to V)>=2, a contradiction.
The all-negative case follows by applying this argument to the inverse word,
whose required endpoint is `I-(z-1)N`.

For two positive and two negative calls, F has Laurent support in [-2,2].
Multiplying F-S by z^2 and interpolating at the four roots gives

```text
F(z) = I + (z-1)N + (z^2-z^-2)K.                 (1)
```

The first row cannot have epsilon_1=-1: its nonzero z^-1 coefficient b_1
has no counterpart on the right of (1). Applying the same argument to the
inverse word forces epsilon_4=-1. The remaining patterns are ++-- and +-+-.
For ++-- the first-two-row argument above again gives rank at least two on V.

For +-+-, row two has z^-1 coefficient `b_2-(b_2 a_1)b_1`.
Equation (1) forces that coefficient to vanish. Put d=b_2 a_1. Then
`b_2=d b_1`, and direct multiplication gives the formal identity

```text
R_2 R_1 = I + (z-1)N_1,
N_1=(a_1-d a_2)b_1,       rank N_1=1,       N_1^2=0.
```

The remaining product `R_4 R_3 (I+(z-1)N_1)` has no z^-2 term,
so (1) forces K=0. Thus F=S as a Laurent identity for every nonzero z.
Apply the same first-pair argument to the inverse word. It gives
`R_4 R_3=I+(z-1)N_2` for another rank-one square-zero N_2.
Comparing coefficients in

```text
I+(z-1)N = (I+(z-1)N_2)(I+(z-1)N_1)
```

gives N=N_1+N_2, hence rank N<=2. This final contradiction excludes dim V=4.

## Case 2: the phase directions span exactly the target image

Now V=Y and all calls preserve every role modulo Y. On Y alone, their
product is identity at every character because N restricted to Y is zero.

Every a_j lies in the span of the other three. Otherwise choose a covector
on Y that annihilates the other three but not a_j. At an active root, apply
it to the target word: all other calls leave it unchanged, and the jth call
contributes a nonzero multiple of b_j times an invertible prefix. The target
word cannot be identity. This contradicts b_j a_j=1.

Consequently any three directions are independent, and their unique
dependency uses all four. In coordinates a_1=e_1,a_2=e_2,a_3=e_3, write
`a_4=(c_1,c_2,c_3)` with every c_j nonzero. Restrict the covectors to Y
and denote them f_j. From `R_3 R_2 R_1=R_4^-1`, row one says

```text
(z^epsilon_1-1)f_1 = (z^-epsilon_4-1)c_1 f_4.
```

At two distinct active values this forces epsilon_1=-epsilon_4 and
f_1=c_1 f_4. Row two then forces
epsilon_2=-epsilon_1 and `f_2=-(c_2/c_1)f_1`.
Determinant closure forces epsilon_3=epsilon_1. Row three gives
`f_3=(c_3/c_1)f_1`. These are equalities of covectors, not an assumption
that their entries are rational.

Rescale the directions, and choose them as target coordinates. Both possible
alternating orientations now have the canonical form

```text
a_1=e_1, a_2=e_2, a_3=e_3, a_4=e_1-e_2+e_3,
f_1=f_2=f_3=f_4=f=(1,1,1).
```

The part of each covector acting on roles outside Y is an unrestricted
constant row beta_j. Let B(z) be the resulting outside-to-Y block. Set
t=z^-1 and H(z)=B(z)/(z-1). For each outside input column, direct multiplication
gives the following rows, where the beta_j may be arbitrary complex numbers.

For +-+-:

```text
H_1 = t beta_1 + (1-t)beta_2 - (1-t)beta_3 - t beta_4
H_2 = -beta_2 + (1-t)beta_3 + t beta_4
H_3 = t(beta_3-beta_4).
```

The required H is constant at i,-1,-i. The coefficients of t therefore
vanish: beta_1=beta_2 and beta_3=beta_4. Every output column lies in
span(e_1-e_2), so the possible constant transfer has rank at most one.

For -+-+:

```text
H_1 = -beta_1 + (1-t)beta_2 - (1-t)beta_3 + beta_4
H_2 = t beta_2 + (1-t)beta_3 - beta_4
H_3 = -beta_3 + beta_4.
```

Constancy forces beta_2=beta_3. Every output column lies in
span(e_1,e_2-e_3), so its rank is at most two. Neither case can supply
the required rank-three transfer. This excludes dim V=3 and completes
the four-call exclusion. Together with parity/rank and the direct upper word,
the minimum is exactly six.

The arbitrary-dimension argument above is written mathematics, not a proof-assistant formalization. The finite verifier checks its canonical interpolation core and literal upper words.
