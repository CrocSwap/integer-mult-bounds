# A diagonal gauge for every real body-sign profile

## Frozen model and claim

Use the Type A component of the literal caller in
[inputs/CALLER.json](inputs/CALLER.json). Its source is Rohan Arun's #7113,
retained by ToikY in #7439 at
`ba83c9bebd99502cd64bb1cab2bc4e5336d9d7b2`.
[The origin record](inputs/ORIGIN.json) identifies the exact file and bytes.
There are 36 gathered roles, 17 body variables, and 38 relative paid factors.
Type B events have no action on these Type A roles. The scalar LAMBDA
actions vanish because this component has beta squared equal to zero.

Each body variable is an independent real sign `D_j` for `1 <= j <= 17`.
At host J_j, first apply the two query shears to its four roles, then
multiply all four roles by `D_j`. At IDLE_ONE, multiply its role by the
product of the listed body signs. Retain every ordinary ADD, SCALE,
SWAP and standalone QUERY. The central query parameter is `q = +1` or
`q = -1`. This is precisely the real-sector scalar model used by #7439.
It is not a native implementation of these signs.

Number the relative factors from zero. Let `A_i(D)` be the normalized
factor defined below, and set

```text
S_i(D) = A_37(D) ... A_(i+1)(D)
T_i(D) = S_i(D) A_i(D) S_i(D)^(-1)
I = (0,1,2,4,6,8,10,12,14,18,19,20,22,24,26,28,30,32,34,36).
```

`I` is the fixed 20-factor selection of #7439. No optimization of that
selection or replay of its factor-length result is part of this package.

**Theorem.** For every choice of the 17 independent signs, all `i` in `I`
satisfy

```text
T_i(D) = E(D) T_i(1) E(D)^(-1),
```

where `E(D)` is diagonal and, for `0 <= j <= 17`,

```text
E_jj = E_(18+j,18+j) = product_(r=1 to min(max(j-1,0),8)) D_r.
```

An empty product is one. In particular, the gauge depends only on the
first eight signs. Every later body sign is still applied at every
literal contact in the calculation.

## Transported factors from positive prefixes

Expand a J event into its two commuting shears followed by its body
scales. At the i-th query, let `P_-` and `P_+` be the literal prefix
operators at `q=-1` and `q=+1`. Write `e_d e_s^T` for its destination/source
matrix and `sigma` for its sign. The two query operators are
`I - sigma e_d e_s^T` and `I + sigma e_d e_s^T`. Their relative operator is

```text
L_i = I + 2 sigma e_d e_s^T.
A_i = P_-^(-1) L_i P_-.
```

Factoring the relative complete word gives, by chronological cancellation,

```text
H_i = A_(i-1) ... A_0 = P_-^(-1) P_+.
Q = A_37 ... A_0 = F_-^(-1) F_+.
```

The symbolic endpoint check described below gives `F_- = -F_+` for every
body-sign profile, hence `Q = -I`. As `Q` is central,

```text
S_i = Q H_i^(-1) A_i^(-1)
T_i = H_i^(-1) A_i H_i
    = P_+^(-1) L_i P_+.
```

Consequently the transported factor can be obtained directly from the
positive prefix as

```text
T_i = I + u_i v_i,
u_i = P_+^(-1) e_d,
v_i = 2 sigma e_s^T P_+.
```

This derivation avoids any assumption that a unit-body prefix remains
unchanged when bodies are nonunit. At a J event its two shears have
disjoint source/destination pairs, so extracting each factor just before
its own shear agrees with the common pre-J prefix convention in #7439.

## Exact certificate over the sign character ring

The primary verifier works in

```text
R = Q[D_1,...,D_17] / (D_1^2-1,...,D_17^2-1).
```

It represents a polynomial by a dictionary from a 17-bit character mask
to its exact rational coefficient. Character multiplication is bitwise
XOR. Distinct characters are linearly independent in R. Evaluation on
all real sign profiles is faithful, by the inverse Walsh transform over
Q. Thus equality of these dictionaries proves equality for every profile;
the verifier does not extrapolate from single-sign tests.

Starting with `P=P^(-1)=I`, each expanded action updates both matrices.
For `P'=(I+c e_d e_s^T)P`, row d of P gains c times row s and column s
of the inverse loses c times column d. A scale multiplies its forward row
and divides its inverse column. A swap exchanges the two rows and the
two inverse columns. These rules maintain the exact prefix/inverse
invariant by induction. All body signs are units in R.

At both central signs, the verifier compares all endpoint entries with
the diagonal declared by the literal caller. In this model the endpoint
is `q` times the declared body monomial on each role. This establishes
the `Q=-I` premise used in the transport calculation.

For each selected i and every ordered role pair `(a,b)`, it checks

```text
(u_i)_a (v_i)_b = E_aa E_bb (u_i(1))_a (v_i(1))_b
```

as an equality in R. The complete check has 659 nonzero and 25,261 zero
displacement entries. It includes the zero entries, so no new support
can appear in a mixed profile. This is the claimed computer-assisted
proof of the theorem. No numerical tolerance or sampled sign identity
decides acceptance.

## Consequence for the existing witness

Let `R(D)` be the product of the selected `T_i(D)` in increasing index
order, from left to right. Adjacent gauge factors cancel, giving

```text
R(D) = E(D) R(1) E(D)^(-1).
```

Any unit-body factorization `R(1) = product_k (I+x_k f_k)` therefore
extends by replacing each factor with
`I + (E x_k)(f_k E^(-1))`. Nilpotence, factor count, displacement rank
and minimum length over unrestricted rational transvections are preserved
by this conjugation. Combining this new identity with #7439's cited
unit-body 19-factor witness supplies a normalized 19-factor witness for
every real body-sign profile. The original 19-factor witness and its
length theorem are predecessor results, not independently certified here.

The `D_8=-1` and otherwise-unit profile gives exactly the sign flips on
roles 9 through 17 and 27 through 35 stated by #7439. That special case
is a control; the extension to independent simultaneous signs is the
new result.

## Independent corroboration and limits

The second implementation uses ordinary rational numbers. It builds the
negative prefixes, extracts their relative factors, and literally
transports each selected image and covector through all later relative
factors. It does not use the positive-prefix transport formula to obtain
the tested factors. Twenty-one nonunit profiles cover the 17 individual
signs and four mixed profiles. It checks 544,320 displacement entries,
the complete selected products on every basis column, and one omitted
factor per profile. These finite checks corroborate the ring certificate;
they do not replace its all-profile argument. Both implementations were
produced by the same contributor.

The theorem covers this fixed 20-factor circuit and real scalar body
signs. It does not establish an identity at `q=+i` or `q=-i`, arbitrary
complex body phases, a legal host replacement, physical sign synthesis,
ownership/restoration, a complete cost improvement, a new kappa or a
complete multiplication theorem. In particular, the negative full-host
price comparison in #7439 is not changed by a conjugacy identity.
