# An exact Max Cut reduction for constant integer gauges

This contribution was produced by Nick Petalas. Apache-2.0.

## Priced problem

Fix a finite chronological scalar word on rational registers. Its only
instructions are `v_t += 2^e v_s`, with t distinct from s and
`e in {-1,0,1}`. One reference register r has fixed exponent zero.
Each other register i may choose any integer exponent k_i. Apply the entry
scale `v_i *= 2^k_i`, replace each coefficient by
`2^(e+k_t-k_s)`, and apply the exit scale `v_i *= 2^(-k_i)`.
The instruction order and identities of all registers remain fixed.

The tariff is the real-component copy-init tariff declared in Philipp /
mightyOil's [PR1310](https://github.com/CrocSwap/integer-mult-bounds/pull/1310),
README section "Why the finite pair census covers all integer exponents".
For a positive power of two it is

```text
ADD(2^z) costs 3 + |z| - [z=0].
SCALE(2^z) costs |z|.
```

Every ADD includes its coefficient-work cleanup. A unit ADD is a direct
ADD followed by CLEAR of that work register, costing two. A nonunit ADD
copies its source to the work register, applies |z| doubles or halves,
adds it to the target, and clears work, costing 3+|z|. The work register
can start arbitrary and ends zero. Its entry value is disposable under
this owned-work contract. It is not an extra restored donor. All data
registers, including the reference, start arbitrary.

This is an optimization over representations of a fixed word. Combining
repeated ADDs, changing the algorithm, replacing the lowerer, removing
CLEARs, free renaming, free scales and changing the reference gauge are
outside the problem.

Let `f(z)=|z|-[z=0]`. For N instructions the complete scalar bill is

```text
B(k) = 3N + 2 sum_i |k_i| + sum_(t,s,e) f(e+k_t-k_s).       (1)
```

The 2|k_i| term pays both boundaries. No boundary cost is omitted.
The source's tariff and scalar conjugation interface are premises here;
its historical k8 word, counts and stationarity proofs are not replayed.

## The construction and exact optimum

Let G be any nonempty finite simple graph with n vertices, m edges and
maximum degree Delta. Isolated vertices are permitted. Put
`A=2 Delta+1`. Use one data register for each vertex and one reference r.
First, in vertex order, emit for every i

```text
A copies of       v_i += v_r,
A+1 copies of     v_i += (1/2) v_r.
```

Then, in lexicographic edge order, emit for every edge i<j

```text
v_i += 2 v_j,
v_j += 2 v_i.
```

These are chronological shears. The second reads the updated v_i; no
commutation or simultaneous-assignment interpretation is used. There are
`N=n(2A+1)+2m` ADDs. The reference is never written.

**Theorem.** Every globally optimal integer gauge of this word is binary,
and its complete minimum scalar bill is

```text
min_(k in Z^n) B(k)
    = n(6A+4) + 8m - MaxCut(G)
    = n(12 Delta+10) + 8m - MaxCut(G).                  (2)
```

Moreover, the optimizers are exactly the indicator vectors of maximum
cuts, including the complementary indicator of each cut.

### Two elementary estimates

The contribution of one vertex, including both scales, is

```text
U_A(x) = 2|x| + A f(x) + (A+1) f(x-1).
```

It has `U_A(0)=U_A(1)=1`. Let `c(x)=min(1,max(0,x))` on integers.
For x>=2 and x<=-1, respectively, direct substitution gives

```text
U_A(x)-1 = (2A+3)(x-1) + A+1,     x>=2,
U_A(x)-1 = (2A+3)(-x)  + A,       x<=-1.
```

Consequently, for every integer x,

```text
U_A(x)-U_A(c(x)) >= (2A+3)|x-c(x)|.                   (3)
```

The two directed instructions of an edge together contribute

```text
H(d) = f(1+d)+f(1-d)
     = 2            if d=0,
       1            if |d|=1,
       2|d|         if |d|>=2.
```

Its consecutive differences have absolute value at most three. By a
finite telescoping sum, `|H(u)-H(v)|<=3|u-v|` for all integers u,v.
This estimate includes the unit-coefficient discount at d=+1 and d=-1.

### Clipping proves the unrestricted integer result

Write `F=B-3N`. Clip one coordinate k_i to c(k_i), leaving every other
coordinate fixed, even if the other coordinates are unbounded integers.
The unary part decreases by at least `(2A+3)|k_i-c(k_i)|`. The incident
edge terms together can increase by at most
`3 degree(i)|k_i-c(k_i)|`. Thus the total decrease is at least

```text
(2A+3-3 degree(i)) |k_i-c(k_i)|
    >= (Delta+5) |k_i-c(k_i)|.                        (4)
```

This is positive for every nonbinary k_i. Clipping each coordinate once
therefore gives the quantitative inequality

```text
B(k) >= B(c(k)) + (Delta+5) sum_i |k_i-c(k_i)|.        (5)
```

No finite search box is assumed. A minimum exists because the finite
binary domain contains a point at least as good as every integer point.
Every minimizer is binary by the strict part of (5).

For binary k, each unary term is one. Each edge contributes two when
uncut and one when cut. Hence

```text
F(k)=n+2m-cut_G(k),
B(k)=3[n(2A+1)+2m]+n+2m-cut_G(k).
```

This proves (2) and the optimizer characterization. In particular, the
ungauged bill B(0) is `n(12 Delta+10)+8m`, so the maximum obtainable saving
is exactly MaxCut(G).

## Complexity consequence

The decision problem for the declared fixed-word gauge tariff is
NP-complete, even when every original coefficient belongs to {1/2,1,2},
there is just one fixed reference, and both boundary scales are charged.

For hardness, use the classical Simple Max Cut decision problem. Given
G and integer q, construct the word above and set
`K=n(12 Delta+10)+8m-q`. Equation (2) gives

```text
MaxCut(G)>=q  if and only if  some integer gauge has B(k)<=K.
```

The word has O(n Delta+m) instructions, hence polynomial size. Repeated
instructions are explicitly present in this count. All original scalar
coefficients have constant bit length, and the threshold has polynomial
bit length. This is a many-one reduction.

For membership in NP of the full declared problem, each ADD costs at
least two and every other charge is nonnegative. A witness with bill at
most nonnegative K must satisfy `2 sum_i |k_i|<=K`. Therefore every
exponent has O(log(K+1)) bits. Evaluating (1) requires only integer
arithmetic polynomial in the word length and these bit lengths. Negative
K is immediately infeasible. Thus a polynomial-size exponent witness
exists for every yes-instance. The same conclusion holds for the
constructed subfamily, whose witnesses can be chosen binary.

Classical hardness is cited from Garey, Johnson and Stockmeyer,
[Some simplified NP-complete graph problems, Theoretical Computer Science
1 (1976), 237-267](https://doi.org/10.1016/0304-3975(76)90059-1),
Section 1's Simple Max Cut theorem. Their theorem is a premise, not a new
complexity result here. The new result is its exact realization in (1).
No literature-priority claim is made for graph reductions or nonconvex
integer-potential optimization in general.

## Complete endpoint and limits

After entry scaling maintain the invariant that represented register i
is `2^k_i` times its original-word value at the same cut. A transformed
ADD preserves this invariant because

```text
2^k_t v_t + 2^(e+k_t-k_s) 2^k_s v_s
    = 2^k_t (v_t+2^e v_s).
```

The reference has k_r=0. The exit scales remove every remaining factor.
This proves equality of the whole linear endpoint for arbitrary rational
data, with arbitrary initial coefficient-work contents cleared as charged.
It restores the intended original-word outputs, not the initial data
registers individually. The finite checker executes the literal primitive
words on all basis columns of its endpoint fixtures, including the work
column, and on signed rational dirty states.

The theorem is about worst-case constructed words. It proves neither
hardness of the actual 237-helper instance nor a new bound on that word's
minimum. It does not supply a faster multiplication algorithm, native
admission, a changed productive or paid rank profile, rounded precision,
physical hosting, stock, tape costs, compiler closure or a new kappa.
The five selected framework assumptions remain. A different tariff or
unrestricted circuit resynthesis can escape this obstruction.
