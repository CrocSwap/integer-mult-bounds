# Three factors for every two-role full-matrix target

Scoped algebraic proof with finite constructive corroboration. For every
field K, every m>=1 and every target M in M_2(M_m(K)), the paid right-vector
cost is at most three. Singular targets of every ordinary rank are included.
For every m>=2 the maximum cost is exactly three. No new kappa is claimed.

The alphabet is I+u y^T with u in M_m(K)^2, y in K^2 and arbitrary free
GL_2(K) maps anywhere. There are two data roles and no auxiliary roles.
After free block row and column swaps, the new construction gives

```text
[A B] = [I 0] [I B] [E 0],
[C D]   [b I] [0 d] [F I]

E=A-BF, d=D-bB, C-DF=b(A-BF).
```

[PROOF.md](PROOF.md) chooses a block row and column whose ranks sum to at
least rank(M). A common complement in im(M) then supplies F and b. The
classical complement argument works over every field, including F2.
The three right vectors are e1,e2,e1 in the transformed chart.

This removes the invertible-target hypothesis of Nick Petalas's #4749 for
a single full matrix algebra and resolves that algebra's case of the
three-factor question in #4276. Combined with #4276's cited exact zero,
one and two-factor criteria, it decides every two-role matrix-algebra cost.
The existing all-algebra question is false by #4763's polynomial examples.
The finite predecessor censuses and #4789's low-rank classification are
comparisons, not this contribution's deliverable. No predecessor verifier
is imported or replayed.

## Evidence

The standard-library verifier implements the complement and graph construction
directly. Every literal product matches its full target on all 65,536 binary
4 by 4 matrices. Their rank histogram is [1,225,7350,37800,20160]. The ordered
factors and free chart choices have SHA256
`e71204a01c63133a328e47180e395a3563dd0c5266c6c44a3f20a710b2c7c504`.
This is new constructive evidence for the universal upper bound, rather than
a new claim about the already known binary optimum.

There are 3,507 additional target executions: all scalar-block two-role
matrices over F2,F3,F5,F7, plus 24 fixed-seed samples at every combination
of those fields and m=1,2,3,4. Samples and scalar censuses can overlap;
3,507 is an execution count, not a count of distinct targets. Twelve
separate sharp witnesses cover those four fields and m=2,3,4. Each receives
an attaining word, and the cited two-factor rank criterion rejects it.
The binary m=2 witness also passes chronological execution on all 16 data
inputs. Five controls cover inconsistent equations, the binary union-of-two-
subspaces case, a free target, factor reversal and each factor omission.

The universal statement rests on the written proof. The exhaustive census
is only over F2,m=2, and the other stated domains are bounded corroboration.
The replay writes no files. Its generated receipt binds all six package
files, the two live predecessor documents and the executed results by SHA256.
Checks remain active under optimized Python. No receipt is handwritten.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/matrix-algebra-three-factor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/matrix-algebra-three-factor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/matrix-algebra-three-factor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/matrix-algebra-three-factor --check-source-history
```

Any CPython 3.12 installation can replace the local path. Expected marker:
`PASS_MATRIX_ALGEBRA_THREE_FACTOR binary_targets=65536 additional_targets=3507 sharp_witnesses=12 controls=5 no_new_kappa`.
Both registered commands run the complete verifier with separate 120-second
limits. [SOURCES.json](SOURCES.json) pins the exact source bytes.

## Scope and engineering notes

The historical card is connector-alphabet-change, explicitly changed to this
algebraic side question. Its first working example passed with
`PASS_UNIVERSAL_CONNECTOR_BOUNDARY pairings=945 max_coverage=31 queries=74 leaves=182`.
The base is canonical main `624de9dc66858af0945e5f8a0942488d62280d43`,
priority revision 7. [The advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19132042)
records the target. Live handoffs and PR bodies, main README terms and merged
PR searches were checked. The overlap helper's sparse local-note coverage is
incomplete; these searches are not a proof of novelty.

Native coefficient preparation, overwrite ownership, reversible restoration,
routing, frames, precision, stock and the complete supplier invoice remain
unknown. More roles, singular radical extensions and simultaneous products
are outside the theorem. No native supplier, selected-frontier change or
complete multiplication theorem follows. Independent human and formal
proof-kernel review are unclaimed. Lean, Docker and the selected operator
replay were outside scope and were not run.

The replay has no recursion or dynamic evaluation. All functions are below
60 lines. Its target loops have explicit fixed bounds, with matrices of at
most eight rows and columns, q in {2,3,5,7}, at most eight complement steps
and at most eight source manifest entries. It streams the binary census
without storing target matrices. Python's required dynamic allocation is a
managed-runtime deviation from static allocation; these fixed matrix domains
bound live memory. Package reads are capped at one MiB per file. Warning-strict
normal and optimized replays and in-memory compilation provide diagnostics;
no separate Python static analyzer is installed in the supplied environment.

## Open next questions

1. Which simultaneous complement conditions suffice for singular targets over
   a product of full matrix algebras? One free chart must work in every
   component. Start with two binary M2 components whose preferred swaps
   conflict and test a common three-direction word. The componentwise rank
   choices here need not coincide, so the present proof does not answer it.
2. Can a literal native producer and consumer implement these algebra-valued
   coefficients with a useful complete invoice? First specify and price
   coefficient preparation, overwrite ownership, routing and restoration.
   The unknown physical costs above block any supplier claim.

Structured questions are in [TASK.json](TASK.json).

## Credit

This contribution was produced by Nick Petalas. Nick Petalas #4276 supplies
the one/two-factor criteria; #4749 supplies the invertible semilocal comparison;
#4265/#4243 supply the exact-cost question and free-map framework. ToikY #4334
supplies the related field-product three-factor construction. Wentao Li #4099,
following #2513, supplies the alphabet and column bound. The complement lemma,
rank inequalities, linear sections and linear-map extension are classical
linear algebra. The new claim is their stated all-target restricted-alphabet
consequence and its literal constructor. Predecessor credit is unchanged.
Apache-2.0.
