# Sharp correction rank after one tensor child

Work over any characteristic-zero field containing i. Put
`C=((1+i)I+(1-i)X)/2`, `C_h=C^tensor h`, `q=2^s`, `h=s+1`,
`D=2q`, and `T=I_q tensor C`, with `s>=0`. All D inputs are arbitrary and
independent. There is no clean complement, dirty padding, or discarded output.
The tensor/spectator split is fixed.

The contract is

`T = F E^-1 (i^u C_h^eta) E`,

where `E` is any invertible D-by-D linear encoding, `u in {0,1,2,3}`,
`eta in {1,-1}`, and F is a subsequent nonreciprocal linear correction.
The quantity optimized is **rank(F-I)** over the stated field. It is not
the rank parameter of a recursive Clifford child, the number of ADD gates,
or the cost of reading or writing physical arrays.

## Phase-specific theorem

Define

`m_j = sum_{0<=k<=h, u+eta*k = j mod4} binomial(h,k)`.

For fixed u and eta, the exact minimum is

`min_E rank(F-I) = max(m_2,m_3)`.

In particular it is attained over Q(i), using explicit invertible encoders.

**Lower bound.** The eigenvalues of C are 1 and i. The child therefore has
eigenvalue i^j with multiplicity m_j, irrespective of E. The target T has
multiplicities `[q,q,0,0]`. If `B=E^-1(i^u C_h^eta)E`, then
`T-B=(F-I)B`, so both differences have the same rank. The elementary
rank perturbation inequality after subtracting `mu I` gives

`rank(T-B) >= |dim ker(T-mu I)-dim ker(B-mu I)|`.

This is PR1920's credited lower-bound method. In particular the two unwanted
eigenvalues -1,-i give `rank(F-I)>=max(m_2,m_3)`. Since h>=1, even and odd
binomial coefficients each sum to q; hence `m_0+m_2=m_1+m_3=q`.
The discrepancies at the two desired eigenvalues give the same lower bound.
No simultaneous diagonalization of T and B is assumed.

**Attainment.** Work first in the tensor child's Walsh eigenbasis, where its
matrix is diagonal D_H. Leave every eigenvector with eigenvalue 1 or i alone.
Pair `min(m_2,m_3)` of the -1 eigenvectors with -i eigenvectors. On each pair
apply the left correction

```text
J = [[1-2i, 2i],     J-I = 2i [[-1,1],
     [ -2i,1+2i]],             [-1,1]].
```

The difference has rank one and square zero; J is an invertible shear.
Moreover

```text
J diag(-1,-i) = [[-1+2i, 2 ],
                [  2i, 2-i]],
```

whose eigenvectors `(1,1-i)` and `(2,1-i)` have eigenvalues 1 and i,
respectively. Their determinant is `-(1-i)`, nonzero. Every remaining -1
or -i singleton is multiplied by -1, becoming 1 or i respectively; each
singleton contributes rank one to the correction difference.

Let F_spec be this block correction. Its difference from identity has rank

`min(m_2,m_3)+|m_2-m_3| = max(m_2,m_3)`.

The corrected operator `F_spec D_H` is diagonalizable. Its desired
multiplicities are `m_0+m_2=q` and `m_1+m_3=q`, so it is similar to T.
This proves attainment, including phases with unequal unwanted multiplicities.

For an explicit encoder let `W_h[x,y]=(-1)^popcount(x&y)` and
`U=I_q tensor [[1,1],[1,-1]]`. Assemble S from the unchanged eigenvectors,
the two displayed pair eigenvectors, and the corrected singleton eigenvectors,
ordered as q alternating eigenvalues 1,i. Then

`E=W_h S U/2`, `F_H=W_h F_spec W_h/D`,
`F_H (i^u C_h^eta) E = E T`.

Thus `F=E^-1 F_H E` realizes the stated contract. Conjugation preserves
rank(F-I). These are square, invertible maps on all D inputs. Walsh and
eigenvector conversion are explicit, but are **not** claimed free in a
physical supplier.

## Optimizing phase, and the sixteen-lane attainer

The four unphased multiplicities are the residue classes of `(1+x)^h`
modulo `x^4-1`. Write `M=2^(h-2)`. For even h, two opposite multiplicities
are M and the other two are `M +/- 2^(h/2-1)`. For odd h, two adjacent
multiplicities are `M-2^((h-3)/2)` and the other two adjacent ones are
`M+2^((h-3)/2)`. These formulas follow by evaluating at 1,-1,i,-i;
`(1+i)^2=2i` proves the signs by a four-step cycle. The h=1 values are
`[1,1,0,0]` and are treated directly.

Changing the phase rotates the four multiplicities. Minimizing the maximum
of two adjacent unwanted multiplicities therefore gives

```text
r(0) = 0,
r(s) = 2^(s-1)                          if s is odd,
r(s) = 2^(s-1) - 2^((s-2)/2)           if s>=2 is even.
```

Inverse children have the same optimized answer, because
`C_h^-1=(-i)^h Z_h C_h Z_h`; the verifier also checks their phases separately.
Even allowing an arbitrary nonzero global scale cannot lower this optimum:
unless that scale is a fourth root of unity, the child has neither eigenvalue
1 nor i, giving discrepancy q at either target eigenspace. The displayed
optimum is at most q. This observation is not needed for the finite fixtures.

For s=4, the native C5 multiplicities are `[6,6,10,10]`. PR1920's four
lower bounds are `[10,10,6,10]`. Choosing phase -1 yields
`[10,10,6,6]`, so **six disjoint rank-one shears and no singleton sign
changes attain six**. This closes the expressly unproved attainment in
PR1920; it does not improve or replace that predecessor's lower bound.

The complete 32-dimensional Gaussian-rational encoder and correction are
stored in WITNESS.json. In the native coordinate basis, `F_H-I=UV^T` with
six columns, `V^T U=0`, and both U,V of rank six. This uses ordinary
transpose, not conjugate transpose. The independent checker verifies all
matrix entries of `F_H H E=E T`, all stated ranks over Q(i), and the six
outer products without importing the builder.

## Operation interpretation, spectators, and the cost boundary

Any product of k rank-one updates `I+u_j v_j^T` has difference from I of
rank at most k, by telescoping and subadditivity. Thus the theorem also gives
the sharp number of *arbitrary linear rank-one updates*, when their linear
reads and writes are granted as primitive operations in this eigenbasis.
The construction attains it with paired shears and singleton sign changes.
It does not turn one rank-one update into one repository-native ADD, COPY,
line child or all-size stream operation. Linear forms may involve all D
coordinates after conversion to the native basis.

For a common unchanged spectator space of dimension t, tensor E and F with
I_t. The algebraic correction rank becomes t*r(s); the host's active width
stays s+1. In the sixteen-lane, nine-axis local example, keeping the original
eight spectator axes means t=256 and correction rank 1536, not six on the
whole 8192-coordinate space. This is an explicit extension of the displayed
construction and its eigenspace lower bound; no spectator reassignment is used.

Under PR679's inherited upper expression `A V width^sigma`, `0<sigma<1`,
the q original rank-one lanes cost `q A V`. The joined child alone costs
`q A V (s+1)^sigma`. For s>=1 its ratio exceeds one, even granting every
encoding, correction, decoding, phase, storage and frame operation for free.
Consequently the known joined-volume tariff still fails the card's favorable
5% construction gate. This is an inequality between available upper-bound
expressions, not an optimal-runtime lower bound. The contribution resolves
the exact algebraic adapter gap; a useful physical batching mechanism needs
a changed, justified volume or operation tariff in addition.

The all-size claims follow from the written construction and multiplicity
proof. The 1032 spectral cases and 48 complete operators are corroboration,
not an extrapolation from a finite search, a formal-kernel proof, or a full
supplier admission.
