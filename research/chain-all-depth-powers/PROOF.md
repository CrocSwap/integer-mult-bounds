# Repetition at every depth of the balanced unsigned chain

For a balanced block with n copies of each of L letters, repeat it d times
and set m=dn. Define q to be the least prime divisor of d that does not
divide n. Set q=∞ when there is no such prime. The comparison of q with L
determines the power law. At q<L every block fails a proper interval. At
q>L the target is multiplied by d. At q=L exactly one shift survives. Its
value is (d/L)n^L modulo m.

This answers open question 1 of Nick Petalas's depth-four study. The
induction below handles every target, including zero, and the mixed products
of lower interval counts at every depth. [PR #6652](https://github.com/CrocSwap/integer-mult-bounds/pull/6652)

## Model and starting result

Let L≥2 and m≥2. Letter j is the complete call `z_j += B_j z_(j-1)`.
All roles are distinct, z_0 is immutable, their initial values are arbitrary
and the maps are arbitrary compatible linear maps over a nonzero unital
ring of exact characteristic m. The desired endpoint restores every
intermediate and adds c B_L ⋯ B_1 z_0 to z_L. A balanced word contains
m copies of each letter. Target residues include c=0.

Write N_I(v) for the number of scattered copies of the consecutive label
sequence I=[i,j]. Their positions in v need only increase. The coefficient
on the initial z_(i-1) in the final z_j is N_I(v) B_j ⋯ B_i. Appending
letter j proves this identity by induction. Thus all proper interval counts
must vanish modulo m, and N_[1,L] must equal c. Sufficiency follows from the
expansion. Necessity follows by choosing identity maps over the ring itself
and turning on each initial role separately. This is the credited chain
criterion. [PR #4249](https://github.com/CrocSwap/integer-mult-bounds/pull/4249) · [PR #4257](https://github.com/CrocSwap/integer-mult-bounds/pull/4257)

Let W_L(n,t) count literal balanced blocks correct modulo n for t. Use
W_L(1,0)=L! as a counting convention. When n=1 every permutation meets
the vacuous congruences. The physical ring contract starts at m=2.

In word combinatorics this interval encoding is the transpose of the
classical Parikh matrix for the ordered alphabet. [Mateescu, A. Salomaa,
K. Salomaa and Yu (2001)](https://www.numdam.org/item/ITA_2001__35_6_551_0/)

## 1. The first surviving coefficient

Write C(d,j)=0 for j>d. For 2≤j<q we have

```text
dn divides C(d,j)n^j.                                             (1)
```

It suffices to show that d divides C(d,j)n^(j−1). For j≤d, use
j C(d,j)=d C(d−1,j−1). At each prime ℓ|d with ℓ∤n, we have ℓ≥q>j, so j
costs no factor of ℓ. At ℓ|n, the factor n^(j−1) supplies at least j−1
powers of ℓ, which is at least the exponent of ℓ in j. This proves (1),
including when q=∞.

At finite q=p, write C(d,p)=(d/p)C(d−1,p−1). The last binomial coefficient
is 1 modulo p. Its numerator factors d−1 through d−p+1 reduce to the
nonzero residue classes, as do the denominator factors. Consequently

```text
C(d,p)n^p = (d/p)n^p (mod dn),       d does not divide (d/p)n^p. (2)
```

Indeed the difference on the left is a multiple of d n^p, and p∤n.
Equations (1) and (2) locate the *first* offending level. No conditions on
later pure coefficients are necessary.

## 2. Power law and fixed points

The integer composition identity used in #6652 is also the matrix power
formula in Theorem 3.1 of Atanasiu, Poovanandran and Teh. The contribution
here is its modular reduction under balanced endpoint constraints.
[Parikh Matrices for Powers of Words](https://arxiv.org/pdf/1808.04102)

The identity groups a scattered interval
by the distinct copies of v used in v^d. For every division of I into
j consecutive nonempty intervals I_1,…,I_j, its contribution is

```text
C(d,j) N_(I_1)(v) ⋯ N_(I_j)(v).
```

Summing over divisions gives N_I(v^d), including d N_I(v) from j=1.
Take all intervals in increasing length. Singletons have count n in the
block and dn in the repeated word. Suppose the smaller proper interval
counts in v are multiples of n. Each j-part product with j≥2 is then a
multiple of n^j. For length h<q, (1) removes every mixed term modulo dn.
Thus vanishing of a proper interval of length h in v^d is equivalent to
n dividing that interval count in v. Starting at singletons gives both
directions of the induction without assuming the candidate block is valid.

If q=p<L, correctness of v^d would first force all smaller interval counts
of v to be multiples of n. On any proper interval of length p, the terms
with 2≤j<p then vanish modulo dn. The unique p-part division consists of
singletons and contributes C(d,p)n^p. By (2) even divisibility by d fails,
regardless of the term d N_I(v). This rules out every target.

If q≥L, all proper intervals vanish in v^d exactly when v restores them
modulo n. At the top interval the j<L terms with j≥2 still vanish. Define

```text
s = (d/L)n^L  if q=L,             s=0 if q>L.                    (3)
```

Only the first case uses division by L, and L is then a prime divisor of d.
The top count of v^d equals d times the full-interval count of v, plus s,
modulo dn. This proves the full
repetition criterion.

**Fixed-count formula.** For d|m and n=m/d, the number F_d of correct words
fixed by a rotation of order d is

```text
0                                 if q<L, or if q≥L and d∤(c−s),
W_L(n, ((c−s)/d) mod n)           otherwise.                       (4)
```

A rotation of order d in the cyclic group on Lm positions has cycles of
size d, so fixed balanced words require d|m. Its subgroup is generated by
the shift Lm/d. Each fixed word is uniquely v^d. Equation (4) counts all
such blocks. Cyclic rotation preserves correctness because the universal
unitriangular target I+cE_(L,0) is central. The classical orbit formulas
already used in #6080 now apply at arbitrary depth. With φ and μ denoting
Euler's totient and the Möbius function,

```text
cyclic classes = (1/(Lm)) Σ_(d|m) φ(d) F_d,
words with maximal repetition d = Σ_(d|e|m) μ(e/d) F_e.             (5)
```

The first formula counts stabilizing pairs and divides by group size. For the
second, each word of maximal repetition e contributes to F_d exactly when
d|e. These are transforms of the underlying literal counts W_L. [PR #6080](https://github.com/CrocSwap/integer-mult-bounds/pull/6080)

## 3. One divisor for every arithmetically eligible order

Let R be the product of the **distinct** primes ℓ|m with ℓ≤L. Start with
D=gcd(c,m/R). If L=p is prime, p^a exactly divides m, a≥1 and
c=m/p modulo p^a, multiply D by p. The resulting integer satisfies

```text
the arithmetic gates of (4) pass for d|m  iff  d|D.                 (6)
```

To prove this, compare prime exponents in d and m. For ℓ<L, the gate q≥L
requires at least one factor ℓ to remain in n whenever ℓ divides d.
This caps the exponent in d at a−1 if ℓ^a exactly divides m. For other
ℓ≠L the cap is a. In a zero-shift case we also need d|c. These requirements
account for the gcd and the removal of one copy of each prime up through L.

The remaining question is whether one may use the *full* p^a when L=p.
Write d=p^a u, m=p^a N and n=N/u, with p∤uN. By (3) the shift is
s=p^(a−1)u n^p. It is zero modulo u and equals p^(a−1)N=m/p modulo p^a,
using n^p=n modulo p. The target gate requires both u|c and
c=m/p modulo p^a. The latter gives exactly a−1 factors of p in c, so all
smaller p-powers are eligible too. This restores precisely one factor p to D
in the displayed case. If the full power is not used then p|n, which gives
the zero-shift case for p. This proves (6).

Every actual maximal repetition divides D. Each orbit size is therefore a
multiple of Lm/D, so Lm/D divides W_L(m,c). For a nonzero target, realization
of a candidate d still depends on its root count in (4). For example,
L=5, m=10, c=7 gives D=5 but the required root count W_5(2,1) is zero.
There are valid primitive words for (5,10,7), as the retained depth-five
witness shows.

**Exact spectrum at target zero.** Here D=m/R. Every divisor d|D occurs
as a maximal repetition. Put n=m/d and take v=1^n 2^n ⋯ L^n. Each block
interval count of length h is n^h, giving root target zero. No prime ≤L in d
is absent from n, so the shift vanishes. The cyclic block v has exactly one
boundary from L to 1; any proper power would have more such boundaries.
Hence v^d has maximal repetition exactly d. This construction and (6) give

```text
attained least periods = { Lm/d : d|m/R },
shortest positive rotation period = L R.                            (7)
```

For depth 5 and modulus 360, R=30. The exact periods are 150, 300, 450,
600, 900 and 1800. Higher powers of the small primes affect which longer
periods occur but do not change the shortest period.

## 4. Unit targets and the exceptional prime depth

For gcd(c,m)=1, the initial gcd in D is one. A nonprimitive word can occur
only at prime depth L=p, with m=pn, p∤n and c=n^p modulo p. Indeed the
exceptional congruence in (6) is impossible for a≥2 at a unit target.
In the allowed case D=p. The number of repeated words is exactly

```text
B = W_p(n, ((c−n^p)/p) mod n).                                     (8)
```

Set B=0 outside this case. Every word counted by B has maximal repetition
p, hence least period m. All other words have least period Lm. The number
of primitive words is W_L(m,c)−B, and the cyclic count is

```text
(W_L(m,c) + (L−1)B)/(Lm).                                           (9)
```

In particular every unit-target word at composite depth is primitive. The
prime-depth possibility is attained at every prime p with m=p,c=1. The
p! permutations of the letters give p! repeated words, grouped into
(p−1)! orbits of size p.

An independent way to check the restriction uses the unitriangular block
matrix I+X. Choose a prime ℓ dividing the repetition and view the word as
an ℓ-th power. If ℓ² divides m, work modulo ℓ². In increasing interval
length, all proper entries of X are divisible by ℓ, since every product
of two or more strictly shorter entries is already zero modulo ℓ² at
that step. The proper-entry equation then reduces to ℓ times that entry
being zero modulo ℓ². At the top entry every term in (I+X)^ℓ−I is zero
modulo ℓ, contradicting the unit target. If ℓ divides m exactly once,
the entries of X on the first subdiagonal equal m/ℓ, nonzero modulo ℓ.
In characteristic ℓ the power is I+X^ℓ. When ℓ<L the ℓ-th subdiagonal
is noncentral and nonzero. When ℓ>L the power is the identity. Thus
ℓ=L, which recovers the only possible prime and the target residue.
The original balanced-word argument supplies the exact number in (8).

## 5. Concrete checks at depth five

At L=5 an order d is obstructed if a prime among 2 or 3 divides d but
not n. A surviving fifth-level shift occurs precisely when 5|d and 5∤n
under the lower gates. For d=10,n=2 the sorted block repeats correctly at
m=20,c=4 with period 10. This attains the divisor bound D=10 for a nonzero
nonunit target.

At the same depth with m=50, targets 5 and 10 agree modulo 5. They give
D=5 and D=25 respectively. At target 10 the block 1122334455 repeated
25 times attains period 10. This is where checking the congruence only
modulo 5 would lose the distinction modulo 25 in (6).

For a nonzero unit example, take Nick Petalas's (n,t)=(7,1) witness

```text
41545521341233132545311545421342223
```

Repeating it five times gives m=35 and c=5+7^5=12 modulo 35. The resulting
175-call word has least period 35. The verifier also executes it on every
dirty basis input with noncommuting two-coordinate maps. [PR #4281](https://github.com/CrocSwap/integer-mult-bounds/pull/4281)

At modulus 15, equation (4) reduces *all* nonprimitive depth-five targets
to a single three-residue row at modulus 3. Two complete counts give
4,697,520 words of least period 15 at target 3, forming 313,168 shorter
classes. Every other target has zero nonprimitive words. [Finite certificate](ROOT-COUNT.md)

The proof concerns the complete-call algebraic endpoint and its cyclic
multiplicities. Physical scheduling prices depend on the caller and its
implementation. The κ and supplier decisions belong to that separate cost
analysis.

The balance hypothesis matters. Nick Petalas's depth-six binary word
`(1234565432)^2` has unit target 1 and period 10. Its six letter counts
are (2,4,4,4,4,2), whereas a balanced binary word would have two of each
letter. The verifier replays its full endpoint as a boundary example.
[PR #4748](https://github.com/CrocSwap/integer-mult-bounds/pull/4748)
