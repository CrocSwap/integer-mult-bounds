# Exact integer-transvection length of the shear powers

This proof was produced by Nick Petalas. Apache-2.0.

## Model and theorem

Use the faithful matrices

```text
X(t) = [[1,t],[0,1]],  Y(t) = [[1,0],[t,1]],  t in Z \ {0},
B = X(2)Y(2) = [[5,2],[2,1]].
```

Every letter costs one, independently of the size of its integer coefficient.
There are no free matrix operations. Let lambda(M) be the minimum letter count
for the exact matrix M. Then, for every integer k >= 1,

```text
lambda(B^k) = 2k.
```

The first previously unresolved power in unpaidmoon's PR4146 is k=3:
its exact length is six, rather than the inherited interval four through six.
This is a scoped group-word theorem. It does not price a physical operation or
establish a complete multiplication theorem.

## Cited classical theorem

For nonzero integers a,b, a division chain has successive equations
`r_(j-2) = q_j r_(j-1) + r_j`, starting at `(r_-1,r_0)=(a,b)` and ending
at the first zero remainder. The quotients may be arbitrary integers and
remainders need not decrease. **The least-absolute-remainder algorithm
minimizes the number of divisions among all such terminating chains.**
Either nearest quotient is allowed at a tie.

This is the classical shortest-division-chain theorem over Z, with the
arbitrary-remainder extension due to D. Lazard, *Le meilleur algorithme
d'Euclide pour k[X] et Z*, C. R. Acad. Sci. Paris 284 (1977), 1–4.
The distinction between unrestricted remainders and the older
Kronecker–Vahlen version is recorded in the introduction of
[M. Vaskouski and N. Kondratyonok, *Shortest division chains in unique
factorization domains*, J. Symbolic Computation 77 (2016), 175–188](https://doi.org/10.1016/j.jsc.2016.02.003).
We use that theorem as a cited mathematical result, not as a new result or
an implication established by our finite verifier. No monotone-remainder
assumption is imposed on a candidate matrix word.

## The two exact division lengths

Define the Pell sequence by `s_0=0`, `s_1=1` and
`s_(j+1)=2s_j+s_(j-1)`. Multiplying `[[2,1],[1,0]]` twice gives B, hence
induction gives

```text
B^k = [[s_(2k+1), s_(2k)], [s_(2k), s_(2k-1)]].
```

For j >= 2, `0 < s_(j-1) <= s_j/2`, with equality only when j=2.
Consequently quotient two is a nearest integer in every division

```text
s_(j+1) = 2s_j + s_(j-1),   j=2k,...,1.
```

The last equation is `s_2=2s_1+0`. This least-remainder chain has exactly
2k divisions. At the only tie, `s_3/s_2=5/2`, we choose quotient two.
Choosing three instead gives remainder minus one and the same two final
divisions.
Also `s_(2k)/s_(2k+1) < 1/2`, so the reversed starting pair has the
nearest quotient zero, followed by the same 2k divisions. The classical
theorem therefore gives the exact shortest chain lengths

```text
ell(s_(2k+1),s_(2k)) = 2k,
ell(s_(2k),s_(2k+1)) = 2k+1.
```

## Every matrix word yields one of those chains

Take any word `G_1 ... G_L = B^k`. Consecutive letters in the same family
can be merged by adding their coefficients; a zero sum deletes the pair.
Repeat until families alternate. This never increases L. Since B^k is
nonidentity, the resulting word is nonempty.

Let `(a,c)^T` be the first column of B^k. Remove letters from the left by
applying `G_1^-1`, then `G_2^-1`, and so on to this column. After all L
removals the column is `(1,0)^T`. An X(t) removal replaces a by `a-tc`;
a Y(t) removal replaces c by `c-ta`.

Stop at the first removal that makes either coordinate zero. The
coordinates were both nonzero beforehand, so every operation up to this
point is an ordinary integer division equation. Alternation makes the
successive remainders exactly a division chain. Its initial ordered pair
is `(a,c)` if the first letter is X, and `(c,a)` if it is Y. Its length
is at most L, even if the full word continues after that first zero.

Here `(a,c)=(s_(2k+1),s_(2k))`. Thus an X-first word has L >= 2k and a
Y-first word has L >= 2k+1. In particular every word has L >= 2k.
The literal word `(X(2)Y(2))^k` has 2k letters and endpoint B^k, proving
the theorem. The stronger Y-first inequality refers to a reduced
alternating word; it is not needed for attainment.

## Exact model-local bill and boundary

In PR4146's two-role reading, lambda letters are rank-one children of
width two and the untouched role is counted in W=2. The exact moment is
therefore `k*2^(a-1)`. With only the active role counted, W=1, it is
`k*2^a`. These substitute the new exact count into the inherited model;
they do not supply a native implementation or alter its admission status.

Integer coefficients are essential. Over Q the three-letter word

```text
X(12/5) Y(70) X(2/5) = B^3 = [[169,70],[70,29]]
```

is a literal endpoint identity. It is a scope control, not a word in the
integer alphabet. Similarly a quotient representation may erase B and
does not preserve the faithful length. Arbitrary free address maps,
extra matrix generators, or different coefficient tariffs change the model.

## Credit and proof status

unpaidmoon supplies the arbitrary-integer alphabet and unresolved length
interval in PR4146, and the unit-alphabet comparison in PR4126.
Cinna Davis / 1337isnot1337 supplies X, Y, B and the formal target in
PR3905. ToikY supplies the caller and quotient boundaries in PR3937 and
PR3947. The classical division-chain theorem retains Lazard's credit and
the Kronecker–Vahlen lineage described above. The new repository result
is its application giving the exact all-k faithful length and bill.
No literature-priority claim is made.

The universal lower bound is the argument above using the cited classical
theorem. Exact finite checks corroborate the Pell identities, chain lengths,
attaining words and hypothesis controls; they do not enumerate arbitrary
integer coefficients or prove Lazard's theorem. Independent human and formal
proof-kernel review are unclaimed.
