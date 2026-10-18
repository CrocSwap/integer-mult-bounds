# Maintainer corollary: no 17-point cover, without the predecessor census

This deduction uses Aaron Wang's Fourier/Parseval lemma in PR #2870.
The application to every nonzero linear functional below was added during
maintainer integration. Credit for the decisive local Fourier obstruction
and the preceding 17-point investigation remains with Aaron Wang (navinor),
with the query-model lineage credited in the package's NOTICE.

Suppose a set S of 17 points satisfies S+S = F2^7. For any nonzero linear
functional u, write s = |S intersect ker(u)| and t = 17-s. Every vector
with u(x)=1 must be a cross sum, so st >= 64. Consequently s is one of
6, 7, 8, 9, 10, 11.

The package's lemma applies to this hyperplane, not only to Hamming parity.
Indeed, choose a basis of ker(u) and one vector on which u is 1; this gives
an invertible linear change of coordinates taking its two cosets to the
standard two cosets. Such a change preserves addition and covering. Equivalently,
the Fourier transform of the nonzero coset's indicator is supported at 0
and u, which is the only hyperplane-specific fact in the lemma.

If (s,t)=(11,6) or (6,11), let C be the six-point side. Away from the two
characters 0 and u, the lemma gives |C_hat(v)| <= 2. Parseval gives

    sum_{v not in {0,u}} C_hat(v)^2 = 128*6 - 2*6^2 = 696,

whereas the upper bound is 126*2^2 = 504. Thus neither split is possible.
At the two distinguished characters, C_hat is 6 and either +6 or -6;
the sign depends on the coset and does not affect its square.

It follows that for every nonzero u the Fourier coefficient of S is

    S_hat(u) = s-t in {-3,-1,1,3}.

A second application of Parseval, now to S, gives

    sum_{u != 0} S_hat(u)^2 = 128*17 - 17^2 = 1887.

But there are 127 such characters and each square is at most 9, giving
at most 127*9 = 1143, a contradiction. Therefore no 17-point set covers
F2^7. No Sidon, near-Sidon, word, or search census is used in this deduction.

This is a written finite-dimensional proof, not a Lean formalization or a new
multiplication bound. The maintainer replay of the registered commands checks
the package's arithmetic, identities, vendor bindings and small controls.
The older long census receipts remain historical evidence; their optional
recomputation has not been run in this integration. The two earlier PRs are
not thereby fully reviewed or incorporated: their other claims and tools keep
their separate review obligations.
