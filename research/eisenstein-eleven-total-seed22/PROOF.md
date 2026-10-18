# One extra total cannot reduce a frame-partition decoder's copy charge

## Statement

Let q and d be positive integers.
Let V be a d-dimensional real or complex inner-product space with a positive-definite form.
Partition qd distinct port indices into q sets F_1,...,F_q of size d.
The vectors at each F_a form an orthogonal basis of V; their norms may differ.
Different ports may represent the same geometric line.
For a support R, let X_R be the span of its port vectors.
Define c(R,A) as the rank of the inner-product pairing between X_R and X_A.
Equivalently, choose bases and take the rank of their Gram block.

Let B be the binary qd-by-qd matrix with an all-ones block on each F_a-by-F_a and zero elsewhere.
All matrix identities in the decoder factorization are over F2, regardless of the geometric field.
For arbitrary port subsets R_j and A_j, suppose

```
B = sum_{j=1}^m 1_(R_j) 1_(A_j)^T  over F2,
m <= q+1.
```

Then the total abstract copy charge satisfies

```
sum_j c(R_j,A_j) >= qd.
```

The q frame rectangles attain qd. Thus the bound is sharp, even when non-clean rectangles and cancellation are allowed.
For d>=2, split one frame reader support into two nonempty parts with the same full-frame source support.
This gives q+1 active totals at the same charge qd. The verifier checks both E8 witnesses.
The theorem fixes B. It does not bound other fitting matrices or decompositions with q+2 or more totals.
It assumes additive pairing-rank charges, not a physical supplier implementation.

For the pinned Eisenstein E8 frame partition, q=10 and d=4 over Q(omega), giving charge at least 40 for every decomposition with at most eleven totals.
For a direct rational interpretation, each port represents the two-dimensional subspace span_Q(r_i,Jr_i) in Q^8.
Each frame partitions Q^8 into four mutually orthogonal two-dimensional subspaces.
The complement argument below remains valid for such subspace ports: replace each vector by its entire subspace.
Its unnormalized dimension bound is eight; divide all pairing ranks and deficits by two to obtain charge 40.
The binary factorization argument is unchanged: its dimension q counts frames, not geometric coordinates.
The pinned geometry verifies J^2+J+I=0 and orthogonality of J.
Thus all support spans and pairing kernels are J-invariant and have even rational dimension.
This also justifies the Eisenstein rank normalization without choosing complex floating-point coordinates.
The current necessary construction screen needs charge at most 31, before other obligations.
Hence this complete one-extra-total mechanism cannot pass that screen.
No new kappa, supplier, global decoder optimum, or full multiplication theorem follows.

## The frame code

Let C be the binary span of the q disjoint frame indicators.
It has dimension q. Both the row space and column space of B equal C.
Every nonzero word in C contains a complete frame, so its geometric span is V.
This uses the orthogonal-basis condition only through full spanning.

Remove any zero rectangle from the factorization.
This preserves B and its charge and cannot increase the number of totals.
Write B=U Vt, where U's columns are the reader indicators and Vt's rows are the source indicators.
Both factors have rank at least q, and rank(B)=q.

If m<q, no such factorization exists.
If m=q, both factors have rank q; their column and row spaces equal C.
Each nonzero factor support therefore spans V, so each rectangle costs d and the total is qd.

Now suppose m=q+1.
The factors cannot both have rank q+1, since then U is injective and Vt is surjective, forcing rank(B)=q+1.
At least one factor has rank q.
If both have rank q, both support families lie in C and every active rectangle costs d.
That gives (q+1)d, already at least qd.

It remains to consider rank(U)=q+1 and rank(Vt)=q; the opposite case follows by transposition.
Since U is injective, rowspace(Vt)=rowspace(B)=C.
Each nonzero source support A_j spans V, so

```
c(R_j,A_j) = dim X_(R_j).
```

The column space of U is a one-dimensional binary extension of C.
Choose any p outside C in that extension. Each reader support lies in C or p+C.
The columns of U are independent, so all reader supports are distinct.
Supports in C have geometric rank d. Only distinct supports in p+C can reduce the charge.

## Orthogonal-complement lemma for one coset

For every distinct support R in one nonzero coset p+C, put Y_R = X_R^perp.
These subspaces are pairwise orthogonal.

Indeed, R and S differ by a nonzero codeword, which is a union of complete frames.
Choose a frame F on which their bits differ.
Because the coefficient field is F2, S intersect F equals F minus R.
The frame vectors form an orthogonal basis of V. Therefore

```
Y_R is contained in span(F minus R),
Y_S is contained in span(R intersect F).
```

The two right-hand spaces are orthogonal.
This proves the claim for each distinct pair R,S, even though the chosen frame may depend on the pair.

Pairwise orthogonal subspaces in a positive-definite d-dimensional space have a direct sum.
Consequently, for any finite set of distinct coset supports,

```
sum_R (d - dim X_R) = sum_R dim Y_R <= d.
```

Apply this to the outside-code columns of U. Inside-code columns have deficit zero.
There are q+1 active rectangles, so

```
sum_j c(R_j,A_j)
 = (q+1)d - sum_j (d - dim X_(R_j))
 >= (q+1)d-d = qd.
```

This completes the proof. It does not rely on the finite census below.
Distinctness is necessary in the lemma: repeating one support can repeat the same nonzero complement without bound.
The full-column-rank reduction supplies exactly that distinctness.

## Exact E8 corroboration

The pinned PR798 geometry and PR1794 deterministic cover specify the concrete ten frames.
The primary check enumerates all 772 line-spanned flats.
Every support with geometric rank below four lies in a proper flat, so enumerating every subset of every proper flat is complete.
Rank-first enumeration assigns each support its least spanning rank.
The result contains 164110 nonempty supports: 40 of rank one, 1230 of rank two, and 162840 of rank three.

The quotient map toggles a frame whenever its chosen pivot bit is one.
The disjoint frame indicators make this a canonical representative modulo C.
There are 159270 nonzero cosets among the proper-span supports.
Their aggregate deficits are one for 153920 cosets, two for 4950 cosets, and four for 400 cosets.
No coset has deficit above four. Some contain four rank-three supports.
This is a check of the lemma on the exact E8 instance, not a new assumption in its proof.

An independent traversal examines all 10700 sets of one, two or three port generators.
It uses Gaussian elimination modulo the prime 65537, rather than the primary rank-adjoining integer traversal.
Every input row has squared norm eight, so Hadamard bounds each minor of at most eight rows by 4096.
No nonzero minor can vanish modulo 65537; all these ranks and membership tests equal their rational values.
Every proper support span has an Eisenstein basis of at most three ports, so this generator traversal covers every proper flat.
It finds 770 nonzero proper flats and generates their subsets by combinations of port indices.
The resulting full support-to-rank dictionary agrees with the primary dictionary on all 164110 entries.
The two traversals share only the pinned geometric input, not enumeration or row-reduction functions.

The independent coordinate check groups its own support list using per-frame numeric complements, rather than pivot elimination.
Separate Fraction Gaussian elimination checks all 9200 complements in the 4360 cosets with multiple members.
It checks all 5470 complement pairs for orthogonality.
This checks ranks and the lemma on every nontrivial coset after the separate complete-support comparison.

A separate direct factorization model uses two orthogonal bases of Q^2: (e1,e2) and ((1,1),(1,-1)).
It computes the pairing charge for all 225 nonzero binary rectangles on four ports.
It exhausts 50625 ordered rectangle pairs, then obtains the uniquely required third rectangle by matrix XOR.
This finds all six ordered two-term decompositions and all 618 ordered three-term decompositions of the frame-block target.
Both minimum charges are four; one term is impossible.
That enumeration uses neither the factor-rank reduction nor the coset lemma.
It corroborates the reduction through a different mathematical model on a small geometry.
Neither finite check proves the universal theorem; the written argument above supplies that proof.
The expected-output file records regression values from the checks, not independent evidence by itself.

## Cost and research decision

The known ten-frame construction costs 40, and adding one total cannot lower that amount.
The necessary PR1794 threshold is at most 31 across its allowed stage/window template.
Helpers, source access, frame changes, routing, restoration, recursive children, and assembly obligations can only add to this abstract copy bill.
Thus physical synthesis stops for this fixed B with at most eleven totals.
A changed fitting matrix or at least two extra totals is outside this theorem.
Even those changes still need a complete physical invoice; this result does not certify that they can succeed.

## Credit and limits

Jonathan Lam / PR798 supplies the Eisenstein geometry, pairing-rank model and general clique certificate.
Joel Pulikkan / GamingPuzzled / PR620 supplies the retained order-three construction.
Maximooch / PR1794 supplies the orthogonal-frame witness and the necessary cost threshold.
Josie Elliston / PR1977 reports a stronger general lower bound through different non-clique minrank certificates; this work does not repeat that search.
The new result is the general one-extra-total obstruction and its fixed-decoder specialization.
The source methods retain their original attribution and licenses.

Substantial OpenAI Codex assistance covers derivation, implementation, verification, and writing.
The proof is written mathematics, not a proof-assistant certificate or independent human review.
Finite replay does not verify the entire conditional multiplication theorem.
