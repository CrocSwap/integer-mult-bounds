# Exact orders for nonsplit Frobenius algebra symmetries

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped written counting proof with exact finite corroboration.

For B=L[x_i]/(x_i^(p^h_i)), with |L|=Q, put

```text
N = p^(sum_i h_i),
r_e = number of variables of height e,
k_e = N - p^(sum_j max(h_j-e,0)),
C = sum_i k_(h_i) - sum_e r_e^2.

|Aut_L(B)| = Q^C product_e |GL_(r_e)(L)|.
```

[PROOF.md](PROOF.md) derives the count by enumerating the full power kernels
and all lifts of the allowed invertible tangent matrices. The higher terms
are counted, including unequal heights. For a product over K=F_q with
m_tau copies of each type tau=(d_tau, height multiset), it gives

```text
|Aut_K(A)| = product_tau (d_tau |Aut_(F_(q^d_tau))(B_tau)|)^m_tau m_tau!,
|Stab(mu_A)| = |A^times|^2 |Aut_K(A)|,
|GL_n(K)^3 . mu_A| = |GL_n(K)|^3 / |Stab(mu_A)|.
```

These are cardinalities of the complete groups and tensor orbit. They add a
new quantity to apoursh's PR5663 determinant-image interface. That structural
theorem, its coefficient field and its full-type matching remain credited
premises. No predecessor verifier, recognizer, determinant census or norm
witness routine is imported or replayed.

## Evidence and reproduction

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -E -W error -X dev -B research/nonsplit-frobenius-orders/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -E -O -W error -X dev -B research/nonsplit-frobenius-orders/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/nonsplit-frobenius-orders
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/nonsplit-frobenius-orders --check-source-history
```

Another CPython 3.12 path can replace the local interpreter. Both registered
commands must finish with `PASS_NONSPLIT_FROBENIUS_ORDERS` in generated JSON;
the launcher must print `PASS_REGISTERED_RESEARCH_PACKAGE`. Each direct run
generates its receipt from the current eight package-file hashes, writes no
files and also works in a Git-free package export. No receipt is hand-written.

`oracle.py` constructs the literal quotient rings independently of `orders.py`.
It searches every algebra element for the coefficient-generator relations
and nilpotent images. Invertibility and every basis product are checked on
each accepted small map. The examples distinguish relative q-Frobenius,
repeated full types and equal dimensions with different types.

For F2[x,y]/(x^2,y^8), a factorized census visits every one of the 65,536
elements for each generator, groups admissible images by tangent row, and
counts pairs of independent rows. This gives 33,554,432 maps without expanding
all their 16-by-16 matrices. Selected literal nonlinear witnesses have every
basis product checked. This is explicitly a factorized count, rather than
33,554,432 individually executed maps. The written proof justifies the lifting
criterion. The report contains the actual histograms and check counts.

## Scope and limits

The theorem covers every finite base field and every finite supplied type list.
The count implementation has explicit small-domain guards. The literal binary
oracle admits dimension at most sixteen and uses fixed field moduli; an
additional ternary fixture checks the odd-characteristic boundary. These
finite checks do not replace review of the universal proof.

This is an algebraic side result for the coverage-law-change card, whose current
first-step binding check passed. It does not change productive target credit,
supply a physical coefficient/transport program or improve kappa. Recognition,
field embeddings, native execution, physical routing, dirty restoration,
precision/tape costs and a complete recursive/caller invoice remain outside
scope. All five selected framework assumptions remain. No selected cold replay,
Lean or Docker build is run. Independent human and formal proof-kernel review
are unclaimed; the selected frontier is unchanged.

Power of Ten inspection bounds the oracle at sixteen binary coordinates,
65,536 elements per generator, at most three generators, eight substitution
relation coefficients and 882 product maps per product domain. Every function
is below sixty lines. No recursion, network or subprocess occurs. Python's managed integer
and container allocation is an explicit rule-3 deviation, with live state
bounded by these fixture domains. The rejection dispatcher has only the
locally named validation functions as targets, a bounded rule-9 deviation.
Warning-strict development-mode normal and optimized runs supply runtime
diagnostics. Explicit exception checks remain enabled under optimization.

## Credit and overlap

Main predecessor: Armin Pourshafeie / apoursh,
[PR5663](https://github.com/CrocSwap/integer-mult-bounds/pull/5663), at
`d72b2e42a4cf53ae85f5276da65c5cc84e17b253`. Its intrinsic coefficient-field,
type and autotopism results are used for the product and tensor consequences.
Credit its retained Ali Romman / PR5459 local height-flag and PR5637 arithmetic
lineage, apoursh / PR5502 and PR5656, Nick Petalas / PR5252 normalization,
David Ganz and the tensor-atlas predecessors. The new local count is proved
directly here. Monomial Frobenius, finite filtrations, parabolic group orders,
finite-field Galois groups and orbit-stabilizer are classical; general
literature priority is unclaimed. No third-party implementation is copied.

[SOURCES.json](SOURCES.json) pins the exact retained source texts, task catalogue
and selected record at base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
All pins are provenance-only; the executable has no external scientific inputs.
The selected binding check resolves to PR6030, under priority revision 8.

The question is a self-posed cardinality extension of PR5663, rather than one
of its already addressed recognition questions. Recent account work on
recognition runtimes, residue-presentation determinants and norm witnesses
concerns other quantities and is not extended. Live PR bodies, recent account
work, main/merged general-form searches, handoff posts and local reservations
were checked. Sparse local notes, arbitrary historical diffs and unpublished
work remain limits of those overlap searches.

Advance [CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19371146).

## Open next questions

Can one recover a uniformly sampled automorphism directly from these fibers,
without constructing the algebra's full table? Begin with a bijective ordered
encoding of each allowed tangent matrix and power-kernel fiber. This could
supply varied changed-basis test inputs; a concrete consumer and its physical
coefficient costs are still missing. No sampler or further construction is
reserved. [TASK.json](TASK.json) records the first step and blockers.
