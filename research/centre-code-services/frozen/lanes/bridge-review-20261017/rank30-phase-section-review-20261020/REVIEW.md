# Independent review of the rank30 translation section

The translation inverse is valid at every tensor width. The exact physical
inverse has 2,712 nonzero coefficients, common denominator 120, and array
infinity norm 88/5. The odd denominator 15 is necessary for this inverse.
These statements concern the actual serialized U, V, and 112 directions.
They do not certify a complete supplier.

The newer constant-reader section is a separate construction. It can
avoid this inverse for the current terminal reader. The result here
remains useful when the reader V must stay fixed.

## Sources and independent checks

`CHECKS.json` gives each source path and SHA256 pin. The checker reads the
actual U and V, the 112 native directions, the root inverse certificates,
and the D25 stage-zero views. It compares all 112 directions with those
views. It does not import or execute the producer checker.

For each of the 512 characters, the checker constructs T_chi directly.
It treats the producer inverse as a certificate, not as trusted output.
For the large block it forms the integer matrices

```text
M = 2 T_chi,             B = 60 T_chi^-1,
```

and checks MB=BM=120I by integer multiplication. It checks all fourteen
scalar blocks directly. Thus this review uses an independent certificate
check. It does not claim a second independent inversion algorithm.

The review then performs an integer Walsh transform, checks its inverse,
constructs the physical inverse kernel, and constructs D=T^-1 V. It
checks 421,888 entries of D by direct character evaluation. The source
pins include the root normal and optimized receipt. The review itself
also has normal and optimized runs with identical output bytes.

## Why the finite certificate proves every width

Let X_g translate each tensor column by the same g in F2^9. Then
X_g X_h=X_(g+h), at every width. On a frequency tuple
(chi_1,...,chi_f), X_g has eigenvalue

```text
(-1)^(g dot (chi_1+...+chi_f)).
```

Only the XOR of the frequency vectors matters. The cross matrix is

```text
T = V diag_p(X_(q_p)) U.
```

Its 512 character matrices are precisely the matrices in the certificate.
Put

```text
R_g = (1/512) sum_chi (-1)^(chi dot g) T_chi^-1.
```

Character orthogonality gives both products

```text
(sum_g R_g X_g) T = I = T (sum_g R_g X_g)
```

in the finite group algebra. Every representation of the translation
group preserves this identity. This includes every tensor width and
extra supplier coordinates on which these maps act as the identity.
No sample of widths is used to prove the extension.

At positive width, each orbit has 512 points. For a fixed output address,
distinct pairs (input field, g) are distinct input entries. Thus the
physical infinity norm is exactly

```text
max_i sum_(j,g) |R_g[i,j]|.
```

It is not the largest character matrix row norm.

## Exact numerical consequences

The character inverse has common denominator 60 and largest row norm
53/5. Its inverse Walsh formula initially has denominator 30,720. Exact
reduction gives:

| Operator | Nonzero translated coefficients | Common denominator | Physical infinity norm |
| --- | ---: | ---: | ---: |
| T^-1 | 2,712 | 120 | 88/5 |
| T^-1 V | 15,688 | 120 | 1666/15 |

All nonzero inverse translations have odd Hamming weight. This also
follows from T_(chi+all_ones)=-T_chi, since every q_p has odd weight.
The inverse has the same sign relation, which removes the even-weight
Walsh coefficients.

The character-zero inverse contains -1/3 at entry (0,0) and -1/5 at
entry (16,16). A coefficient ring without 1/3 or without 1/5 cannot
contain this inverse: evaluation at the trivial character would give
an inverse over that same ring, contrary to uniqueness. Thus the odd
part 15 is necessary. The physical kernel also has explicit witnesses
-1/30 and -1/20 in the receipt.

The fourteen small blocks are negative sums of three or five signs.
Every such sum is odd and nonzero. The large 16-dimensional block
requires the exact 512-character certificate. This review does not
replace that certificate with the odd-clique argument.

## A paid additive query service

The emitted program gives an actual additive service on disjoint physical
arrays a[112] and z[30]. It does not require a zero value in z.

To implement z <- z-Da, where D=T^-1 V:

1. Multiply every z field by 15.
2. For each source-field and translation pair, apply the translation to
   that source, add all corresponding coefficients of -15D to z, and
   undo the translation.
3. Divide every z field exactly by 15.

Every coefficient of 15D is dyadic. During each group the source has
no scalar write, so the second translation restores it exactly. The
endpoint is (15z-15Da)/15=z-Da for arbitrary a and z.

The program has 5,812 source-view groups. Under the inherited dyadic
ADD count

```text
cost(c) = 2 (1 + bitlength(|num(c)|)
               + popcount(|num(c)|) + bitlength(den(c))),
```

the service uses 204,768 real dyadic primitives and 11,624 translation
map calls. It also uses 30 complex multiply-by-15 scans and 30 complex
divide-by-15 scans. It uses no additional owned array.

The odd scans are separate operations. The integer representation must
have enough reserved powers of 3 and 5 before a division. For one such
service, one additional factor 15 in a common exact coefficient grid
is sufficient once the input grid is fixed; a composition must price
the maximum denominator height of all its prefixes. The bit width,
scan cost, finite map compiler, root-grid conversion, and recursive
depth bound are not included in the dyadic primitive count above.

## The full section swap and its limit

Set J=Q^2 U, D=T^-1 V, so DJ=I. On arbitrary a and z, use the ordered
word

```text
a += Jz
z -= Da
a += Jz
z = -z
```

The second line reads the updated a. It leaves z=-Da_original. The
third line then gives

```text
S(a,z) = ((I-JD)a+Jz, Da).
```

The checker derives this endpoint in a noncommutative polynomial
calculation that uses only DJ=I. It also checks S^2=I. A single use
does not restore z: its arbitrary initial value is stored in the data
section. A later consumer must preserve or restore that value.

Each J shear can use one translation before and one after its scalar
scatter on every data field. With the direct D service above, the
complete swap therefore has 208,028 dyadic primitives, 12,072
translation map calls, and the same 30 complex multiply and 30 complex
divide scans. These are component counts, not a complete finite cost.

At the physical input a=Qx, this section reads T^-1 VQx. The terminal
correction requires VQ^-1. The two readers cannot be identified without
another operation or a changed input code. The later constant-reader
construction changes that code and is reviewed separately.

## Reproduction and scope

```text
python3 -I -B check_phase_section.py
python3 -O -I -B check_phase_section.py
```

Both runs print `PASS_INDEPENDENT_RANK30_PHASE_SECTION`.
`FREEZE.json` pins the proof, checker, receipt, and emitted program.
The proof uses the root exact inverse certificate and the actual
response supplied by the new-core-transfer lane. It also uses the
earlier simultaneous-translation method and exact odd-grid contract.
This review does not repeat the large native phase checks.

The result supplies an exact all-width inverse and an explicit additive
array service. It does not supply a productive centre cohort, its birth
or retirement, legal global routes, a complete finite precision proof,
or the final recursive invoice. No frontier or kappa claim follows.
