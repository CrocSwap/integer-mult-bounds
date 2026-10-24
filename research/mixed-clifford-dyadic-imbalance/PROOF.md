# Mixed Clifford lanes at widths congruent to two

This contribution is produced by Nick Petalas. Apache-2.0.

## Contract and theorem

Work over a characteristic-zero field containing i, where i^2=-1. Put

```
C = ((1+i) I + (1-i) X)/2,  X = [[0,1],[1,0]],  C_f = C tensor ... tensor C.
```

Fix f>0 with f=2 modulo 4, nonnegative integers a,b with q=a+b>0,
and delta=a-b. The independent payload operator is

```
T = (I_a tensor C_f) direct-sum (I_b tensor C_f^-1).
```

All q 2^f coordinates are arbitrary independent inputs. Identity complements
also hold arbitrary dirty data. Allow any invertible square encoder E and its
exact inverse as decoder. One candidate child has operator
H=lambda (C_h tensor I_t), with h,t positive integers and nonzero lambda.

There is a full-space identity

```
T direct-sum I_d = E^-1 (H direct-sum I_e) E
```

if and only if d=e and there is an integer j>=0 such that

```
q = 2^j |delta|,   4^j divides q,
h = f+2j,         t = q/4^j,
lambda = sign(delta) i^(-j).
```

In particular, delta cannot be zero. These conditions determine the candidate
uniquely. They classify a forward child; allowing an inverse child adds no
widths because C_h^-1 is similar to (-i)^h C_h, as in Arham Tahir's PR1920.
The theorem does not classify other congruence classes of f.

## Necessity

The source facts used here are PR1920's reciprocal full-space contract,
Walsh eigenbasis and trace method. Their application to arbitrary directional
multiplicities, and the resulting integer conditions, are the new step.

Since C has eigenvalues 1,i, all payload eigenvalues are fourth roots of
unity. Taking fourth powers of the identity forces lambda^4=1 on the
nonempty child operand. Therefore lambda belongs to {1,i,-1,-i}.
The traces of C_f^2 and C_h^2 are zero, since they are positive tensor powers
of the traceless X. The square traces of the two full operators are d and e,
so d=e. Dimension equality then gives

```
q 2^f = t 2^h.                                      (1)
```

Write z=(1+i)^f. Since f=2 modulo 4, its Gaussian conjugate is -z. After
subtracting the equal complement traces, the first trace identity becomes

```
delta z = t lambda (1+i)^h.                         (2)
```

The right side is nonzero, so delta is nonzero. Taking the algebraic Gaussian
norm of this equality gives

```
delta^2 2^f = t^2 2^h.
```

Combine this with (1) to obtain q^2/delta^2=2^(h-f). Because |delta|<=q,
h>=f. A rational square that is a power of two has an even exponent, by
the exponent of the prime 2 in its numerator and denominator. Thus h-f=2j
for an integer j>=0, and q=2^j |delta|. Equation (1) now gives t=q/4^j;
its required positive integrality is exactly 4^j dividing q. Finally,
(1+i)^(f+2j)=z (2i)^j in (2) gives the asserted lambda, including its sign.

No positivity, ordering or analytic norm on the ambient field was used.
The norm calculation is in its embedded copy of Q(i).

## Sufficiency and explicit basis

Assume the displayed integer conditions. The dimensions agree. Substitution
shows the first traces agree, since

```
(q/4^j) sign(delta) i^(-j) z (2i)^j = delta z.
```

The square traces vanish. The third traces are the Gaussian conjugates of
the first traces, so they agree as well. The zeroth traces are dimensions.
The four-point Fourier matrix recovers eigenvalue multiplicities from these
four traces. Since x^4-1 has distinct roots in characteristic zero, both
operators are diagonalizable and equal multiplicities suffice for similarity.

This is constructive with rational dyadic matrices. Let
W_f[x,y]=(-1)^popcount(x&y). Its column y has C_f eigenvalue
i^popcount(y), and W_f^-1=2^-f W_f^T. Let U be the direct sum of q copies
of W_f, retaining the inverse direction in the eigenvalue list for the last
b copies. Let V be W_h tensor I_t, with columns reordered to match U's
eigenvalues after multiplication by lambda. Equal multiplicities guarantee
this matching. Then

```
E = V U^T / 2^f,    E^-1 = U V^T / 2^h,
H E = E T.
```

Both products of the unscaled encoding and decoding numerators equal
2^(f+h) I. Extend E by I_d to retain any dirty complement. Thus the identity
holds for every input column, including arbitrary independent dirty data.
This construction does not require that E itself be a native operation.

## First new identity and sharp minimum batch

Taking f=2, a=3, b=1 gives q=4, delta=2 and j=1. Therefore

```
C_2 direct-sum C_2 direct-sum C_2 direct-sum C_2^-1
    = E^-1 (-i C_4) E.
```

This is a 16-coordinate identity. PR1920's balanced opposite pair has zero
first trace at f=2 and cannot do this. Any proper width upgrade in the
present model has j>=1 and hence q>=4^j>=4. The four-lane batch is minimal.
More generally the conditions give a minimum q=4^j for a width increase 2j,
attained by a=(4^j+2^j)/2 and b=(4^j-2^j)/2 for every j>=1.
This minimum is an algebraic batch size, not an operation-cost claim.

## Cost and applicability limit

Under the inherited PR679 expression A V f^sigma per full lane, with
A,V>0 and 0<sigma<1, the q separate lanes have expression q A V f^sigma.
The joined child occupies all qV coordinates and has expression
q A V (f+2j)^sigma before encoding, decoding and every other extra cost.
For j>0 its ratio is (1+2j/f)^sigma>1. This is a comparison of available
upper expressions, not a lower bound on optimal runtime. The identity
does not establish the card's favorable complete-invoice gate.

The congruence condition applies to the literal tensor width f. An operation
whose literal width varies with a column parameter would need an implementation
for every required width. This package supplies no such uniform supplier,
native encoding, physical placement, scalar-read tariff, precision/tape proof,
restoration schedule for the encoder, new kappa or multiplication theorem.
Independent human and formal proof-kernel review are unclaimed.

## Proof versus finite corroboration

The preceding argument proves the quantified statement. The standalone
verifier independently compares its integer classification with literal
binomial eigenspace counts, and constructs four dense rational encoders.
It checks both inverse orders and every coefficient of H E=E T using
Gaussian integer tensor coefficients, including identity complements.
Those finite checks corroborate the proof; they are not extrapolated to
unbounded widths or converted into physical costs.
