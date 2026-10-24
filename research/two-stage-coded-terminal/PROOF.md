# Two distinct physical code stages cannot be postdecoded by a fixed native scalar word

Cinna Davis, with substantial OpenAI Codex assistance. Apache-2.0.
The code and normalizers are Dillon/PR4933's, built on Dugongue/PR4929.
The matrix support argument is elementary; no general circuit lower bound is claimed.

## Exact statement and quantifiers

There are 112 independent owners. Let `A` and the signed real orthogonal
monomials `K_i` be the authenticated PR4933 data. For distinct stage blocks
`s,t`, embed each nine-axis `K_i` on the common central axis and its own eight
fresh axes. Unused axes are spectators. For every positive digit-column width
`f`, set

```
Q_f = Q^tensor(f),    Q = (1+i)/2 I + (1-i)/2 T_e,
(C_s,f)_ij = A_ij (K_s,i^-1 K_s,j)^tensor(f).
```

The scalar owner coefficient is applied **once**. In particular `C_s,f` is
not `C_s,1^tensor(f)`. The source identity `A^2+12A=13I` implies

```
C_s,f^-1 = (C_s,f+12I)/13.
```

For either sign `ε,η ∈ {+1,-1}`, let

```
B_f = C_t,f^ε C_s,f^η,    J_f = Q_f^-1 B_f Q_f.
```

Then a row of owner block `(0,1)` of `J_f` has at least `4^(f-1)` nonzero
input coordinates. The same conclusion applies to `Q_f^-1 B_f^-1 Q_f`:
reverse the stage labels and negate the signs, which remains within these
four cases. Consequently any exact implementation by whole-field scalar
ADD/SCALE, monomial address maps and owned COPY/CLEAR needs at least
`2(f-1)` ADDs. A fixed finite native word in that alphabet, independent of
`f`, is impossible. This includes all four sign choices, either ordering of
two distinct fresh stage blocks, and the required inverse postdecoders.

This does not bound the cost of a paid Gaussian decoder, prohibit words whose
number of scalar operations grows with `f`, or classify longer code products.
It does not exclude a changed whole-controller boundary or recursive job type.

## Owner-path expansion

Use coordinates `0,...,16`, with central vector `e=1`, the left stage on
bits `1,...,8` and the right stage on bits `9,...,16`. For owner block `(0,1)`
write

```
M_k = K_t,0^-1 K_t,k K_s,k^-1 K_s,1,
N_k = Q^-1 M_k Q,
(B_f)_01 = Σ_k a_k M_k^tensor(f),
(J_f)_01 = Σ_k a_k N_k^tensor(f).
```

The first expansion follows directly by multiplying owner blocks. The second
uses tensor multiplication **inside each monomial term**, never tensoring a
sum. If `m` is the number of negative exponents, then

```
a_k = [(2A_0k + 24[ε=-1][k=0])
       (2A_k1 + 24[η=-1][k=1])] / (4*13^m).
```

The diagonal terms in the inverse are retained. There are 26,27,27,28 distinct
nonzero monomials after exact collection for signs `++,+-,-+,--`.

For a signed binary monomial `M|x> = (-1)^(β·x)|Gx>`, put `s(x)=(-1)^(β·x)`.
Direct expansion gives

```
2 N|x> = s(x)|Gx> - i s(x+e)|Gx+Ge>
          + i s(x)|Gx+e> + s(x+e)|Gx+Ge+e>.
```

This formula includes absolute signs. The verifier independently checks it
against the four actual Q/inverse-Q terms and the four successive signed K
actions, without using the composed 17-axis matrices.

## One marker column eliminates every competing path

The exact frozen data give the following finite identities, checked against
**all 112** intermediate owners for each of the four signs:

```
<2048|N_k|0> = 0 for every active path k != 31,
<2048|N_31|0> = -i/2,
a_31 = 1/(4*13^m).
```

Here active means `a_k != 0`; zero paths contribute nothing. The selected
port triple is `(q_0,q_31,q_1)=(11,26,19)`. The selected monomial has

```
G columns = [2048,28,14,22,1,32,64,128,256,5146,5632,4634,1562,
             8192,16384,32768,65536],
β = 1038,    Ge=2048,    G^-1 e=16.
```

These lists specify the literal signed monomial, not a rank label. Fix input
`0` and output `2048` in the first digit column. This coordinate restriction
is only a proof device. It is not a free emitted projector, owned input,
measurement, or decoder. On the remaining `f-1` columns, the restricted block
is exactly

```
(-i)/(8*13^m) * N_31^tensor(f-1).
```

Thus the other paths cannot cancel the selected contribution, even at larger
widths. This is stronger than a one-column numerical discrepancy.

## The surviving row

Row zero of `N_31` has four nonzero inputs:

| Input | Coefficient |
|---|---|
| 0 | 1/2 |
| 1 | -i/2 |
| 16 | i/2 |
| 17 | 1/2 |

Choose output zero in every remaining column, and independently choose any
of these four inputs in each column. They give `4^(f-1)` distinct nonzero
entries in one actual row of the full block. Their absolute values are
`1/(2^(f+2)*13^m)`. All other marker-input coordinates are irrelevant to this
lower bound. The verifier independently evaluates every such entry through
`f=4`, in addition to checking the finite identities used in this all-width
argument. The finite checks corroborate the proof, rather than replacing its
quantified tensor argument.

Initially a row of the full input-to-state map depends on at most one input
coordinate. Scalar SCALE and monomial maps preserve the maximum support;
COPY/CLEAR cannot increase it. An ADD at most doubles it, even with owned
scratch and arbitrary owner mixing. A program with `g` ADDs has support at
most `2^g`. Hence `2^g >= 4^(f-1)` and `g >= 2(f-1)`.

## Actual caller consequence and limits

PR4933's emitted `GAUGE.json` contains negative output roles

```
role 0: B = C_32 C_31^-1,
role 8: B = C_1^-1 C_0.
```

They act as `E=Q^-1 B D`, with invertible `D` the authenticated product of
those stages' transverse Gaussians. For the prescribed ordinary output
`Q^-1 D`, the unique postdecoder on that bank is

```
(Q^-1 D) E^-1 = Q^-1 B^-1 Q.
```

That operator is covered above. Therefore neither bank can be converted by
a fixed finite postdecoder in the stated alphabet. The result applies to
arbitrary independent input fields, not just initialized scratch. A change
to the entire entrance, exit, chronological word, or recursive target family
is outside this argument. No independence credit is assigned to the failed
recipe, and no complete moment or new κ follows.

The positive control uses the **same** fresh block: `C_s C_s^-1=I` and its
owner `(0,1)` block cancels after collection. Distinct-stage and same-stage
products must not be interchanged. Signed-phase, scalar-substitution and
owner-tensorization controls are also retained.
