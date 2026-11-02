# Least subfield for every determinant norm witness

Let `K = F_q`, `L = F_(q^d)`, with `q` any prime power and `d >= 1`.
For every divisor `e | d`, write `E_e = F_(q^e)` for the unique intermediate
field inside L. All norms below act on nonzero elements. Define

```text
e_* = product over primes ell dividing q-1 of ell^v_ell(d).
```

The empty product is one. This statement concerns intermediate fields that
contain K, rather than arbitrary linear subspaces or subsets of L.

## Norm restriction and the minimum

The exact image of the restriction to `E_e` is

```text
N_(L/K)(E_e^*) = (K^*)^(d/e).
```

It has `(q-1)/gcd(d/e,q-1)` elements. Each element of the image has exactly

```text
(q^e-1) gcd(d/e,q-1) / (q-1)
```

preimages in `E_e^*`. Consequently the following are equivalent:

1. Every nonzero element of K has a norm witness in `E_e`.
2. `gcd(d/e,q-1) = 1`.
3. `e_* | e`.

Thus `e_*` is the unique least sufficient degree under divisibility, and also
the smallest numerical sufficient degree.

**Proof.** Set `m=d/e`. Each K-embedding of `E_e` occurs m times among the
d K-embeddings of L. For `z in E_e`, the product of conjugates therefore gives

```text
N_(L/K)(z) = N_(E_e/K)(z)^m.
```

The norm from `E_e` onto K is surjective. One elementary proof takes a
generator h of the cyclic group `E_e^*`: raising it to `(q^e-1)/(q-1)` gives
an element of order `q-1`. Hence the restricted image is the power subgroup
`(K^*)^m`. A power map on a cyclic group of order `q-1` has kernel size
`gcd(m,q-1)`, proving the image and fiber counts.

This image is all of `K^*` precisely when no prime dividing `q-1` divides
`d/e`. For each such prime ell, that requires
`v_ell(e)=v_ell(d)`. There is no requirement at other primes. These conditions
are exactly `e_* | e`, and `e_*` itself divides d. This proves all assertions.

A primitive target in `K^*` witnesses the lower bound: a proper power
subgroup cannot contain it. More generally, if any `z in L` has primitive
norm, the intermediate field `K(z)` must have degree divisible by `e_*`.
Indeed its degree r divides d, and the already proved image formula for
`E_r` forces `gcd(d/r,q-1)=1`. For `q=2`, the sole nonzero target is one and
`e_*=1`, as the formula says.

## An attaining constructor from a supplied primitive element

Assume a primitive `g in L^*` is supplied and certified. No efficient primitive
element discovery is assumed. Put

```text
h = g^((q^d-1)/(q^e_*-1)),
c = N_(L/K)(h).
```

Then h generates `E_(e_*)^*`. Its norm to K before the final `d/e_*` power
generates `K^*`, and that final power is coprime to `q-1`. Therefore c also
generates `K^*`. For requested `a in K^*`, enumerate
`1,c,...,c^(q-2)` until `c^i=a`, and return `h^i`.

This uses at most `q-1` target comparisons and returns a witness in the least
uniform subfield. It uses two initial powers, then successive products in L;
there is no traversal of all `q^d-1` or `q^e_*-1` elements. It is not a
polynomial-time claim in `log(q)`, a new discrete-log algorithm, or an
efficient construction of g. When `gcd(d,q-1)=1`, the witness may instead be
chosen directly in K as `a^(d^(-1) mod (q-1))`; for `q=2`, choose one.

`minimal_degree` computes the same degree without factoring d or q-1.
Repeatedly divide a remaining divisor of d by its gcd with q-1. Every
nontrivial step reduces it by at least two, so at most `floor(log2(d))`
divisions occur. The removed factor is precisely `e_*`.

## Application to the retained determinant interface

apoursh's PR5663 supplies the determinant identity for coefficient-unit
multiplication on

```text
A = L[x_1,...,x_s] / (x_i^(p^h_i)),
N = p^(sum h_i),  char(K)=p:
det_K(m_z on A) = N_(L/K)(z)^N.
```

This identity and the character/transport theorems of PR5663/5668 are cited
premises, not results re-audited here. Since `gcd(N,q-1)=1`, exponentiation
by N permutes `K^*`. For any requested determinant delta, first request norm
`a = delta^(N^(-1) mod (q-1))` and use the construction above. Thus the
least single intermediate coefficient field supporting every determinant
request is exactly `E_(e_*)`. Primitive determinant requests retain the same
degree obstruction, since the inverse N power preserves primitivity.

For a concrete new instance, take `K=F_3`, `d=6` and
`L=F_3[t]/(t^6+t^5+2)`. The verifier certifies that t is primitive by its
728-element multiplicative cycle. Here `e_*=2`: a norm-two witness exists
in F_9, whereas both nonzero base scalars have norm one. The constructor
returns `z=t^91`. The verifier displays its canonical polynomial encoding
and its literal 6 by 6 multiplication matrix, whose determinant is two.
On `L[x]/x^3`, the three diagonal residue blocks give determinant `2^3=2`
in F_3. There is no need to enumerate the earlier tensor atlas or replay
its character counts to test this new witness.

## Credit and scope

The finite-field subfield theorem, cyclicity, norm surjectivity, tower law
and cyclic power-map argument are classical. Keith Conrad's
[Finite fields](https://kconrad.math.uconn.edu/blurbs/galoistheory/finitefields.pdf)
gives the underlying field facts. No global literature priority is claimed.
The contribution is the explicit least-field criterion and its attaining
application at the repository's enumerative determinant-witness boundary.

This is a scoped written proof with finite corroboration. It supplies no
physical map tariff, native supplier, primitive-generator discovery bound,
rounded algorithm, new kappa or complete multiplication theorem. In
particular it does not eliminate PR5668's retained full-table construction.
Independent human and formal proof-kernel review are unclaimed.

This proof and the new constructor were produced by Nick Petalas. Credit
apoursh PR5663/5668, Ali Romman's recognition and coefficient-field lineage,
Nick Petalas PR5252, David Ganz and the retained tensor-atlas predecessors.
