# Two odd prime blocks and capacity under prime powers

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

Write `mu_s` for the group of complex s-th roots of unity. Let p<q be distinct
odd primes, let a,b>=1, and put `m=p^a q^b`. All orthogonality below is exact.
A phase change multiplies a row or a column by a root in mu_m.

## Theorem

Let H have p+q rows, c pairwise orthogonal columns and entries in mu_m.
If H cannot be changed by row and column phases to have entries in mu_(pq),
then c<=p. More precisely, a row permutation and phase changes put H in the form

```text
H = [ A D ]
    [  B  ],

A: p by c, entries in mu_p, A* A = p I,
B: q by c, entries in mu_q, B* B = q I,
D: diagonal, entries gamma_j in mu_m.
```

Here `*` is conjugate transpose. At least one ratio `gamma_j/gamma_k` is outside
mu_(pq). Conversely, every such pair of orthogonal prime blocks and diagonal D
gives an orthogonal-column matrix. It fails to descend exactly when some such
ratio is outside mu_(pq).

It follows that every H with at least p+1 columns descends. This threshold is
sharp whenever m>pq: there are p-column matrices that cannot descend, even if
arbitrary unit-modulus row and column phases are allowed.

Let `C(n,s)` denote the maximum number of pairwise orthogonal n-entry columns
with entries in mu_s. Then

```text
C(p+q, p^a q^b) = C(p+q, pq).
```

The theorem removes all higher prime powers from this capacity question. It
does not compute the squarefree capacity for every p,q. In the known case
p=3,q=5, that capacity is four by the retained finite source certificate.
No physical supplier or complete kappa gain follows.

## 1. The classical two-cycle input

[T. Y. Lam and K. H. Leung, Corollary 3.4](https://arxiv.org/pdf/math/9511209#page=8)
classify minimal positive zero sums for an alphabet with two prime divisors as
rotated prime cycles. A zero sum of length p+q therefore splits into one
p-cycle and one q-cycle: the only nonnegative solution of `pu+qv=p+q` is
u=v=1. To check uniqueness, v<=1 since p<q; v=0 would require p to divide q.

Each cycle has distinct roots. A p-root coset and a q-root coset have at most
one common root because p and q are distinct primes. Each full cycle lies in
one coset of mu_(pq) in mu_m.

This classical input is not new work. The remaining proof concerns the
simultaneous column constraints and their block form.

## 2. All nonconstant quotient columns use one p-row subset

Make the first column constant one. Work additively in the quotient group
`K=mu_m/mu_(pq)`, of odd order `p^(a-1) q^(b-1)`. Section 1 says that each
column is constant in K, or has two quotient values with multiplicities p and
q. Apply a column phase so its q-fold value is zero. Each nonconstant column
has the form `t 1_S`, where t is nonzero and S has p rows. Constant quotient
columns become zero.

Consider two such columns `t 1_S` and `u 1_T` with S different from T. Put
`k=|S intersection T|`, so 0<=k<p. Their difference has these values and counts
before equal values are combined:

| Region | Value | Count |
|---|---|---:|
| Outside both subsets | 0 | q-p+k |
| S only | t | p-k |
| T only | -u | p-k |
| Intersection | t-u | k |

The outside region is nonempty since q>p. If k>0, the only possible collisions
are t=u and t=-u. These cannot both hold for nonzero t in an odd-order group.
At least three values remain. This conflicts with the two-cycle quotient type.

If k=0, there are again three values unless t=-u. That exception gives two
counts, q-p and 2p. They cannot be p and q: equality would require q=2p, which
is not prime. The difference cannot be constant either. Thus all nonconstant
columns have one common subset S of p rows.

If no nonconstant quotient column remains, all entries already lie in mu_(pq).
Otherwise write every quotient column as `t_j 1_S`, including t_j=0. The
first column has t_j=0, so at least two distinct phase classes occur.

## 3. The product invariant replaces the special p=3 argument

For two columns in different phase classes, their inner-product terms have
separate quotient values on S and its complement T. The p-cycle lies on S
and the q-cycle lies on T. Thus those column restrictions are orthogonal on
each block.

Take columns x,y in the same phase class. Choose z in another class. On S,
the ratios x/z and y/z are scalar multiples of permutations of all p-th roots.
It follows that the ratios x/y on S lie in one coset `gamma mu_p`, and

```text
product over S of (x_r/y_r) = gamma^p.
```

The permutation products cancel. The full x/y zero sum is one p-cycle and
one q-cycle. The q-cycle has at most one term in `gamma mu_p`. Since S has
p>=3 terms in that coset, the p-cycle must be in that same coset. All terms
on S come from that full p-cycle and at most one extra term from the q-cycle.

The product of all roots of an odd prime cycle `gamma mu_p` is gamma^p.
Choosing p terms from the cycle plus one extra term can only keep the full
cycle, or remove one root u and insert one root v. In the latter case the
product changes by v/u. The displayed product identity forces v=u.
Consequently the multiset of terms on S is exactly the full p-cycle. Its sum
is zero. Thus x and y are also orthogonal on S. Their full inner product is
zero, so their restrictions to T are orthogonal as well.

All c nonzero column restrictions are now pairwise orthogonal in C^p. Hence
c<=p. This argument works for every odd p. It does not rely on the two Fourier
lines that suffice in the p=3 source proof.

The oddness is necessary for this argument. For p=2,q=3, the two-cycle zero
sum with mu_6 exponents `(0,3,3,5,1)` contains the two terms `(3,3)`. Their
product is one but their sum is -2. The checker verifies this failure of the
product implication. It is not a counterexample to a full capacity theorem
for even-prime alphabets.

## 4. Extract the two prime blocks

For columns in different phase classes, their entrywise ratios on S lie in
a single mu_p coset, and their ratios on T lie in a single mu_q coset. The
same coset statement holds for columns in the same class: divide their ratios
to a third column from another class.

Make the first column one by row phases. For each column, divide by its entry
at one fixed row in T. All entries on T then lie in mu_q. On S, divide each
column separately by its value gamma_j at one fixed row of S. The remaining
entries on S lie in mu_p. This gives `[A D; B]`. The phase operations preserve
the block orthogonality proved above, so `A* A=p I` and `B* B=q I`.

Conversely, orthogonal A and B imply orthogonality of the stacked matrix for
any unit diagonal D. If every gamma_j belongs to one common mu_(pq) coset,
a single row phase on the top block puts every entry in mu_(pq).

If `gamma_j/gamma_k` is outside mu_(pq), take any top row and any bottom row,
and columns j,k. The multiplicative two-by-two cross ratio is that phase ratio
times an element of mu_(pq). It is outside mu_(pq). Cross ratios are unchanged
by row and column phases. Descent is therefore impossible. This proves both
directions of the block classification.

## 5. Sharpness and equality of capacities

Let eta be a primitive m-th root, omega a primitive p-th root and zeta a
primitive q-th root. Index columns by j=0,...,p-1 and use

```text
first p rows: H_rj = eta^j omega^(rj),       r=0,...,p-1,
last q rows:  H_rj = zeta^(2*r*j),          r=0,...,q-1.
```

Each block has orthogonal columns, since p and q are odd primes and a nonzero
column-index difference has absolute value less than p<q. The first row of
each block and columns 0,1 give cross ratio eta. If m>pq, this is outside
mu_(pq), so the p-column example cannot descend.

Replacing eta by 1 gives p orthogonal columns already over mu_(pq). Therefore
`C(p+q,pq)>=p`. Any matrix over the larger alphabet has at most p columns,
or descends by the theorem and has at most `C(p+q,pq)` columns. The reverse
inequality follows from the inclusion `mu_(pq) subset mu_m`. This proves the
claimed equality of capacities for all positive a,b.

## Evidence and limits

The checker validates exact cyclotomic Gram matrices, the common-subset
counts, the product invariant and the extracted normal forms. The common-subset checks include every unordered pair of five-row subsets
of twelve rows, with all four nonzero value pairs in the odd quotient group
Z/3. This tests the combinatorial lemma beyond the quotient orders that occur
for primes 5 and 7. It enumerates
all relative permutations for p=3,5,7; common row permutation reduces an
arbitrary pair of permutations to this domain. It checks every pair of rotated
prime cycles in the stated twelve finite alphabets, and every p-term selection
inside the relevant p-root coset. These finite checks support the written
proof; they do not enumerate all root-phase matrices or replace the classical
two-prime theorem.

The full predecessor verifier and its nested eight-row capacity source run
unchanged. No independent human or formal-kernel acceptance is claimed. The
squarefree capacity for general p,q, even-prime cases, a third prime divisor,
other row counts and approximate orthogonality remain open here. The block
classification does not classify the smaller matrices A and B. Native
preparation, restoration and a complete caller price are outside scope. All
five multiplication-framework assumptions and the selected frontier remain.

## Open next questions

Determine one new squarefree capacity, or identify a different zero-sum type
for a changed alphabet or row count. Do not repeat prime-power searches in
this exact class. The structured questions are in [TASK.json](TASK.json).
