# Nullspace admission over Q

Let A be an integer matrix with n columns, and let B contain k proposed
integer basis rows. Accept only when:

1. A B^T = 0, checked by exact integer products;
2. rank_Q(B) >= k, certified by a nonzero k-minor;
3. rank_Q(A) >= n-k, certified by a nonzero (n-k)-minor.

The first condition gives row(B) contained in ker(A), so
rank_Q(A) + rank_Q(B) <= n. Conditions 2 and 3 attain n. Thus
rank_Q(B)=k, rank_Q(A)=n-k, and row(B)=ker(A). This proves both
independence and completeness, including n=0, k=0 and k=n.

A nonzero minor modulo a prime is a nonzero integer minor. Modular rank is
therefore a rigorous lower bound, not a probabilistic equality claim. The two
fixed primes are checked by trial division in the executable controls. If
neither prime supplies the required minor, rational Gaussian elimination is
used. Hence unlucky primes do not produce false rejection of a valid basis.
The optional diagonal witness chooses, for each row i of B, a column supported
only on i. These columns are distinct and form a nonzero diagonal k-minor.

Counting rows and checking annihilation alone is insufficient: duplicates or
zero rows could replace a missing basis vector. Dropping a vector makes the
usual test `all(dot(v,b)==0 for b in B)` more permissive. The guard checks both
rank inequalities rather than trusting the candidate's free-column structure.
It does not demand the reference kernel's primitive normalization, signs or
row order. Any integer basis of the same rational kernel is valid.

`guarded_kernel` snapshots A before calling the candidate and certifies against
that snapshot. A candidate cannot substitute another input by mutating its
argument. The finite implementation tests and actual initializer census support
the implementation; this elementary proof supplies the all-size mathematical
criterion. Neither is a formal proof of the entire inherited verifier.
