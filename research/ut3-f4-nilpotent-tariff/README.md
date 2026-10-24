# Nilpotent calls do not lower the six-label UT3(F4) central tariff

The central triple in Wentao Li's [PR #3788](https://github.com/CrocSwap/integer-mult-bounds/pull/3788)
still needs exactly **twelve calls** after admitting every nonzero binary
rank-one scalar coupling, including nilpotents. Each letter class needs at
least six calls, for any finite number of restored dirty registers. This
answers that package's first Open next question.

Claim type: **scoped algebraic proof with exact finite corroboration**.
The new step removes the scalar-idempotence restriction. The predecessor's
twelve-call coordinate word remains the attaining construction and retains
its credit. This is no new kappa, physical supplier or complete multiplication
theorem. No predecessor executable is imported or replayed.

## Model and theorem

The proof has a short extension-field formulation. Let K be any field of
characteristic two and let G=UT3(K), with

```text
(x,y,z)(x',y',z') = (x+x', y+y', z+z'+xy').
X_alpha=(alpha,0,0), Y_beta=(0,beta,0), Z_z=(0,0,z).
```

Work in Mat_r(F2[G]). A paid call is

```text
D_N(g) = I + ([g]+[1]) N,
N = u v^T,  u,v in F2^r nonzero,
g = X_alpha or Y_beta,  alpha,beta in K nonzero.
```

No condition is imposed on v^T u. Trace one gives an idempotent N; trace
zero gives a nilpotent N. Both are valid reversible calls because
`([g]+[1])^2=0`, so `D_N(g)^2=I` regardless of N squared. Scalar GL_r(F2)
mixing is free in this formal model. There are no free address maps, clean
roles, COPY, ERASE, higher-rank calls or unpaid inverse calls.

For arbitrary finite r>=d>=1 and nonzero z_1,...,z_d in K, require equality
of the whole formal endpoint

```text
T = diag([Z_z1],...,[Z_zd],[1],...,[1]).
```

Every input, including every restored role, is arbitrary dirty data.

**Theorem.** Every realizing word has n_X>=2d and n_Y>=2d. If all nonzero
axis coefficients are available, the exact unit tariff is 4d, attained on
the d target coordinates without extra roles. With positive uniform
per-class prices A and B, the exact bill is 2d(A+B).

For K=F4=F2[omega]/(omega^2+omega+1), the available alphabet is precisely
the six labels of #3788. Setting d=3 and `(z_1,z_2,z_3)=(1,omega,omega^2)`
gives n_X,n_Y>=6 and exact minimum twelve. The extension to arbitrary K
uses the same proof, rather than an extrapolation from the F4 computation.

## Proof

First normalize scalar mixing. Moving each scalar map to the end conjugates
the scalar rank-one matrices, preserving the allowed set. Augmentation
`[g] -> 1` sends every paid call and T to I, so the residual scalar map is I.
It suffices to prove the bound for a word of paid calls alone. This
normalization is inherited from the register-model lineage.

Use the associative K-algebra

```text
Q = K<X,Y> / (X^2, Y^2, all words of length at least three).
```

Its basis is `1,X,Y,XY,YX`. Define the F2-algebra map

```text
phi([x,y,z]) = 1 + xX + yY + zXY + (z+xy)YX.
```

Here scalars are extended from F2 to K only in the necessary-condition
codomain; payloads and scalar couplings remain binary. Multiplication of
the displayed polynomials has first-order coefficients x+x' and y+y',
XY coefficient z+z'+xy', and YX coefficient

```text
z+xy+z'+x'y'+yx'
  = (z+z'+xy') + (x+x')(y+y').
```

These are exactly phi of the group product. Therefore phi extends linearly
and multiplicatively from the full formal group algebra. It need not be
faithful. In particular,

```text
phi(D_N(X_alpha)) = I + alpha N X,
phi(D_N(Y_beta))  = I + beta N Y.
```

Write the image of a realizing word as `I+AX+BY+CXY+DYX`. The endpoint gives

```text
A=B=0,  C=D=diag(z_1,...,z_d,0,...,0),  rank_K C=rank_K D=d.
```

For all X calls, factor N_i=u_i v_i^T and form the K-matrices

```text
U_X = [alpha_1 u_1 ... alpha_nX u_nX],
V_X = [v_1^T; ...; v_nX^T].
```

Their product is A, hence zero. Every contribution to C selects an X call
followed by a Y call, so its column space lies in col(U_X). Every
contribution to D selects a Y call followed by an X call, so its row space
lies in row(V_X). Noncommuting scalar matrix products keep their order;
only their image and row-space inclusions are used. Consequently

```text
rank_K U_X >= d,  rank_K V_X >= d.
```

Since U_X V_X=0, im(V_X) is contained in ker(U_X), inside K^nX. Rank-nullity
now gives `n_X >= rank_K U_X + rank_K V_X >= 2d`. Interchanging X and Y
uses the columns of D and rows of C and gives n_Y>=2d. No step uses
`v_i^T u_i=1`, any workspace dimension bound, or a split of coefficients
into complementary binary summands.

For attainment, on target coordinate i use the inherited coordinate word
`X_zi,Y_1,X_zi,Y_1`. Its group product is Z_zi and it acts identically on
all other coordinates. Concatenating the d words has exactly 2d calls of
each class and restores every extra dirty role. It also attains the
positive uniform-price lower bill. This completes the proof.

The degree-two quotient and rank-nullity strategy are credited to
steph4n-gh #1573, Arham Tahir #1589 and Hanson Sun #1607. The new use of
the address coefficient field in the quotient removes the idempotence
restriction in the F4 handoff and gives the characteristic-two formulation.
No novelty is claimed for rank-nullity or the inherited coordinate word.

## Exact finite evidence

[verify.py](verify.py) is a new standard-library implementation. It uses
F4 coefficient Gaussian elimination, a full F2 group-algebra operator, and
a separately implemented literal regular action. The latter applies each
axis update directly to every group address and dirty basis input. Both
implementations share the checked F4 multiplication table; they are not
independent human or proof-kernel reviews.

The generated [RESULT.json](RESULT.json) authenticates all five source and
metadata files and records:

- All 16 F4 products agree with polynomial reduction modulo
  `omega^2+omega+1`. All 4,096 group products satisfy the displayed quotient
  homomorphism. All 256 two-by-two F4 matrices have twice their F4 rank
  under an independent binary regular-representation rank calculation.
- All 160,435 two-role expanded-alphabet words through length three satisfy
  the extension-field coefficient-span inequalities. Of these, 112,446
  contain at least one nilpotent call. All 2,971 words through length two
  also agree between quotient and full formal implementations. For those
  words, the literal regular action additionally compares all 5,942
  identity-address input columns with the full formal coefficient vectors.
- Nine coordinate endpoint fixtures with one through four central targets
  and up to two dirty spectators agree formally. The separate regular
  action checks all 1,856 basis columns of these endpoints.
- All 294 six-label rank-one calls on three roles are formal involutions,
  including the 126 calls formed from the 21 nilpotent couplings. These
  counts are corroborating alphabet checks, not new idempotent-count results.
- Twelve deleted-call controls fail the required full endpoint. Additional
  named controls cover a wrong coefficient, an error visible only on dirty
  workspace, four illegal call descriptions, noncentral first-order terms,
  higher-rank parallel calls and a nonzero four-term formal polynomial
  killed by the quotient. Thus quotient equality alone never admits an
  endpoint.

The general coefficient-span checks use
`n_X >= rank[A C]+rank[A;D]-rank A` and its Y counterpart, the #1607
inequalities over the new coefficient field. They corroborate the proof's
matrix inclusions. The length-three enumeration is **not** a search through
length eleven and is not the reason the minimum is twelve.

## Reproduction

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/ut3-f4-nilpotent-tariff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/ut3-f4-nilpotent-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/ut3-f4-nilpotent-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/ut3-f4-nilpotent-tariff --check-source-history
```

Elsewhere replace the interpreter path with CPython 3.12. Normal replay is
read-only. `verify.py --emit` prints a freshly computed, source-bound receipt
to standard output. It does not overwrite package files. Expected marker:

```text
PASS_UT3_F4_NILPOTENT_TARIFF minimum=12 nX=6 nY=6 short_words=160435 involutions=294 no_new_kappa
```

Registered normal and optimized commands each have a 120-second timeout.
The source/history preflight applies after the package is committed.

## Scope, provenance and credit

This package was produced by Nick Petalas. Independent human and formal
proof-kernel review are unclaimed. Apache-2.0.

The explicit source context is canonical main
`624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
[SOURCES.json](SOURCES.json) pins the predecessor texts and historical
catalogue/selected-record provenance. They are context, not imported runtime
code or predecessor replay obligations. [TASK.json](TASK.json) records the
scope change from a new-alphabet card to #3788's explicit coupling extension.

Credit Wentao Li #3774/#3788 for the F4 target, six-label idempotent theorem,
coordinate words and nilpotent-coupling question; Cinna Davis #2261 for the
F4 central-pair and three-output direction; Arham Tahir #1589 for arbitrary
rank-one binary UT3 couplings and the two-corner quotient; Hanson Sun #1607
for nonzero-first-order coefficient-span bounds; steph4n-gh #1573 for the
all-register central rank proof; James Reed #3783-#3786 for parallel retained
F4 calculations; and the eumemic/woklerx/Gareth Davidson register-model
lineage. Nick Petalas #3800 is earlier finite reconstruction, not the proof
of this newly expanded alphabet. All predecessor notices remain unchanged.

Entry overlap used 365 open PR bodies and 3,819 Discussion records with
complete pagination. Sparse local coverage was only 80 of 6,319 note paths;
separate distinctive searches read all-main READMEs and merged PRs for this
object, and the touching F4 PR bodies were read. No matching delivered
nilpotent extension was found in that coverage. This is not a novelty
guarantee. The advance claim is in
[handoff #1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19133313).

No finite word census through length eleven, proof-assistant formalization,
native realization, compiler/hosting/precision/tape invoice, selected cold
replay or outer analytic transfer was run. The physical price of these
formal calls remains unknown. The selected conditional kappa stays
0.00302015. Hosted CI is separate from the local evidence.

## Open next questions

Can a physically realizable additional address operation escape this exact
axis-alphabet tariff with a favorable complete bill? Start with one pinned
supplier's literal entry/call/exit contract, and charge the new operation's
frames, preparation, dirty restoration, hosting and precision. This matters
because neither nilpotent scalar mixing nor extra workspace can save calls
inside the present model. The blocker is a legal physical realization and
a justified recursive price; a new abstract label alone is insufficient.
Structured details are in [TASK.json](TASK.json).

## Implementation bounds

The verifier has no recursion, subprocess, network or write path. Enumeration
is capped at three calls from 54 two-role factors; endpoint words have at
most 32 calls, five roles and 64 group elements. Rank matrices have at most
ten rows and ten columns. Source/receipt reads are bounded at 65,537 bytes,
with files over 65,536 rejected. Every function is shorter than 60 lines.
Checks use exceptions and remain active under optimized Python.

Power-of-Ten rule 3 has a managed-runtime deviation: Python dynamically
allocates integers, tuples and bounded temporary matrices. The fixed domains
above bound live algorithmic memory; Python allocator internals are not
instrumented. Rules concerning raw pointers and preprocessing have no direct
Python equivalent; calls are direct, with only fixed standard-library
iteration/JSON callbacks. Warning-strict normal and optimized execution and
AST inspection supply the available diagnostics. No static type checker is
configured for this standalone package; no shared tooling is changed.
