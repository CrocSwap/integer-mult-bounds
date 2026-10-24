# Exact rank-two right-vector costs on two roles

Claim type: scoped proof with an exhaustive finite certificate. No new kappa.

For every field K and block size m>=3, every ordinary rank-two target over
M_m(K), on two roles, has exact paid cost two or three. The alphabet is
I+u y^T with u over M_m(K) and y over K; arbitrary common GL_2(K) maps
are free anywhere. There are no auxiliary roles.

Choose a rank factorization M=A B, with A=[A_1; A_2] injective and
B=[B_1 B_2] surjective through K^2. The exact classification is

```text
cost(M)=3 iff
  B_1=c_1 b and B_2=c_2 b for a common nonzero row b and a basis c_1,c_2;
  every nonzero scalar combination s A_1+t A_2 has rank two.
Otherwise cost(M)=2.
```

[PROOF.md](PROOF.md) proves both directions and gives attaining words.
The criterion is independent of the chosen rank factorization. This answers
the rank-two, two-role part of Open next question 1 of
[Nick Petalas's #4772](https://github.com/CrocSwap/integer-mult-bounds/pull/4772).
It uses the two-factor criterion of
[#4276](https://github.com/CrocSwap/integer-mult-bounds/pull/4276) as a cited
theorem. It does not re-audit that predecessor.

In particular, over every field and every m>=3,

```text
M = [[E_11,E_21],[E_21,E_31]]
  = [[I,0],[E_21,I]] [[I,E_21],[0,E_31]] [[E_11,0],[0,I]]
cost(M)=3, ordinary rank(M)=2.
```

Here E_ij denotes an m by m matrix unit. Each factor changes one block
column, with right vectors e_1,e_2,e_1 in algebraic product order.
Column-data execution applies the rightmost factor first.

## Finite evidence

The independent standard-library verifier enumerates all 2,542,806 ordinary
rank-two binary 6 by 6 targets, with blocks of size three. Exactly
2,535,162 cost two and 7,644 cost three.

Coverage uses all 651 two-dimensional column spaces, each represented by
its two least nonzero vectors, and all 3,906 surjections from K^6 to K^2.
Each target occurs exactly once: its column space determines the chosen
A, and the injectivity of A determines B uniquely. The verifier builds
every complete target, applies the cited two-factor criterion directly to
its full blocks, and separately evaluates the new rank-factor classification.
All records agree. It hashes the entire ordered target/cost table, whose
SHA256 is `37a68b33c4175157da0147c0b165f82909956a87750ff354a366f542f432c623`.
The 182 exceptional column spaces pair with 42 common-row surjections.
Every one of the 7,644 cost-three targets has its literal legal attaining
word multiplied and compared with the complete target.

A separate dense linear solver constructs the two-factor words in the
three passing rank-factor categories and rejects the fourth category.
The explicit exceptional target and its legal word pass over F_2, F_3,
F_4, F_5 and F_7 at m=3 and m=4. All 64 binary dirty inputs of the
displayed m=3 word pass chronological execution. The replay checks seven
additional boundary/solver/alphabet controls, plus omission and reversal
controls in each of the ten field/block cases. All checks remain active
under optimized Python.

The printed receipt is generated from executed checks. It binds all six
package files and both live predecessor proof files by SHA256; no receipt
is handwritten. The verifier writes no files.

## Reproduce

From the repository root, with the Python 3.12 standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/right-vector-rank-two/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/right-vector-rank-two/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/right-vector-rank-two
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/right-vector-rank-two --check-source-history
```

Any CPython 3.12 installation can replace the local interpreter path.
The scientific marker is
`PASS_RIGHT_VECTOR_RANK_TWO targets=2542806 cost2=2535162 cost3=7644`.
Both registered warning-strict commands replay every check, with separate
120-second limits. Exact sources are in [SOURCES.json](SOURCES.json).

## Limitations and engineering notes

The universal statement is a written scoped proof, with finite corroboration.
The exhaustive target census covers only F_2 and m=3. Other finite fields
have the stated explicit examples, rather than full target censuses.
The block-size condition matters: at m=2 the ordinary rank-two target
diag(0,I_2) costs one. More roles and other ordinary ranks are unclassified.

These factors overwrite data. Native coefficient preparation, routing,
reversible dirty-state restoration, precision, stock and the complete
recursive invoice are unknown. No native supplier, selected-frontier change
or complete multiplication theorem is claimed. Independent human and formal
proof-kernel review are unclaimed. Lean, Docker and the selected construction
replay are outside this isolated result and were not run.

The verifier has no recursion or dynamic evaluation; all functions are below
60 lines. Its loops use fixed finite domains, at most 2,542,806 target visits,
nine binary chart pairs per target and 64 dense chart pairs in the largest
field example. Matrices have at most eight rows and columns. The two rank
tables have 262,144 and 512 bytes; the census retains only 651 bases, 3,906
surjections, four sample targets and one streaming digest. Python's required
dynamic allocation is the managed-runtime deviation from static allocation;
these fixed domains bound live memory. File reads are limited to one MiB and
the source manifest to eight entries. The direct and optimized warning-strict
replays and in-memory compilation are the interpreted-language diagnostics.
No separate Python linter is installed in the supplied environment.

## Open next questions

1. Which ordinary rank-three targets on two roles over M_m(K), m>=4,
   cost two or three, and can any cost more? Start with the rank-three
   factorization and a named deficient 3 by m matrix pencil. The rank-one
   pencil lemma used here no longer classifies that pencil.
2. Can a literal native producer/consumer realize one of these formal
   factors with a useful complete invoice? First specify coefficient
   preparation, overwrite ownership and restoration. All physical costs
   above remain blockers; no construction expansion is proposed here.

## Credit

This contribution was produced by Nick Petalas. Nick Petalas's #4772
supplies the open higher-rank question and rank-loss bound; #4276 supplies
the two-factor criterion and its attaining formula; #4265 and #4243 supply
the general-target question and free-map normal form. Wentao Li's #4099,
following #2513, supplies the right-vector alphabet and column bound.
ToikY's #4334 supplies the related field-product cost framework, followed by
Nick Petalas's #4601/#4749 local-product and semilocal results. Rank
factorization and the rank-one pencil lemma are classical linear algebra.
The new claims are the stated rank-two classification and exceptional
attaining words. Apache-2.0.
