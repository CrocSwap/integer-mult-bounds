# Sharp arithmetic scratch bound for the selected BIT caller

The binary arithmetic used by Jose Manuel's pending [PR2697](https://github.com/CrocSwap/integer-mult-bounds/pull/2697) needs at most **ten additional numerical words during modular inversion**, including nested division and multiplication. The actual routine attains ten at modulus 5 and operand 2. This is a written, source-bound liveness lemma with literal finite checks, not a total caller reserve or new kappa.

The [first-node handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18957966) separates payload/key content, count tapes and the still-unpriced numerical category. This contribution bounds one reusable part of that last category. It does not bound the caller's simultaneously retained coefficient matrices, callback frames or index words. Existing payload and count bounds are not reproved here.

## Exact contract and result

The source is `research/selected-bit-node/vendor/words.py` at PR2697 commit `a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`. [SNAPSHOTS.json](SNAPSHOTS.json) pins its original path, Git blob and SHA256. The two retained files are byte-identical exports, not a modified arithmetic implementation.

Fix one initialized `Arena` of width `b` and a valid `Ring`. Its modulus `M>1` has exactly one leading zero bit, so `b=bit_length(M)+1`. Modular operands are canonical residues in `[0,M)`. Division admits any unsigned `b`-bit numerator and a nonzero denominator below `2^(b-1)`. Assume ordinary sequential execution, valid complete words, enough arena capacity and no concurrent mutation or instrumentation that allocates in that arena.

Let `L` count **all** live arena words on entry, including the borrowed modulus, `ring.one`, operands and unrelated caller residents. The following additional-word bounds include returned words, but exclude the arena's permanent template:

| Actual entry point | Maximum above L | Live returned words |
| --- | ---: | ---: |
| `Unsigned.divmod` | 4 | 2 |
| `Ring.add` | 2 | 1 |
| `Ring.subtract` | 2 | 1 |
| `Ring.negate` | 3 | 1 |
| `Ring.multiply` | 4 | 1 |
| `Ring.inverse`, unit | 10 | 1 |
| `Ring.inverse`, nonunit | 10 | 0 |

Each bound is attained by the pinned routine, as the literal checks below show. Borrowed operands retain their values and return with heads at cell 1 on successful completion. Inversion returns an owned inverse for a unit and `None` for a nonunit. It releases every other temporary in either case. Aliased binary operands and using `ring.one` itself as the inverse operand are allowed.

For inversion, occupied numerical content excluding LEFT markers is at most

```text
(L + 11) * (b + 1) symbols.
```

The `+11` is ten temporary/result words plus the permanent template. Each complete word has `b` binary symbols and one RIGHT delimiter. The input and constants are already in `L`; they are not free. A fresh arena capacity of at least `L+10` numerical slots suffices for this isolated call. Its fixed backing capacity and LEFT markers are a separate accounting category.

## Proof by actual allocation lifetimes

The proof is inspection of the authenticated source, not an inference from the finite census. Every `Arena.zero` allocates one fresh word, and `Arena.free` erases it before releasing its slot. Source arithmetic does not create words outside this arena. Apart from allocation initialization and final erasure, each live word occupies exactly `b+1` nonblank cells excluding LEFT. No allocation occurs inside erasure. Therefore occupied content can peak at a completed allocation; counting live words there gives the stated symbol bound, including the template.

### Division and modular primitives

`Unsigned.divmod` first owns `scan`, `quotient` and `remainder`, three additional words. A digit step allocates `shifted` before freeing the old remainder, reaching four. On the subtraction branch, the old remainder has already been freed before the new remainder is allocated, so that branch also reaches four. On return, `scan` is freed and only quotient and remainder remain. The scan visits exactly `b` digits. Validity of the high-bit margin keeps `2*remainder+bit` inside the word extent.

`Ring.add` owns its raw sum. Reduction may allocate the result before freeing that sum, reaching two. `Ring.subtract` either allocates one exact difference or owns `larger=a+M` while allocating the difference, reaching two. `Ring.negate` retains its newly allocated zero while calling subtraction, reaching three. Canonical operands ensure these additions fit the reserved high bit.

For nontrivial `Ring.multiply`, the persistent locals are `scan` and `result`. Doubling calls modular addition while both remain live, reaching `2+2=4`. The old result is freed immediately after doubling. An optional addition of the multiplicand likewise starts with only `scan` and `doubled`, so again reaches four. The scan has `b` digits; its disposal leaves one owned result. Zero and unit fast paths allocate only the returned word. No branch accumulates a word from one digit to the next.

### Inversion, including nested primitive interiors

`Ring.inverse` maintains four words `r0,r1,t0,t1`. At each Euclidean loop boundary there are exactly four additional live words. The complete iteration is:

| Interval | Additional words above the original L |
| --- | ---: |
| Four persistent Euclidean words | 4 |
| Division interior | at most 4+4 = 8 |
| Returned quotient and r2 | 6 |
| Optional quotient reduction before freeing its old value | 7 |
| Multiplication interior, with all six still retained | at most 6+4 = **10** |
| Returned product | 7 |
| Subtraction interior for t2 | at most 7+2 = 9 |
| Returned t2 | 8 |
| Free quotient, product, old r0 and old t0 | 4 |

The four-word loop invariant is restored before the next iteration. Quotient reduction needs only one subtraction since `quotient<=M`; the equality case occurs at divisor one. Both Bezout coefficients remain canonical residues. Standard Euclidean descent terminates: every two remainder steps at least halve the previous positive remainder, giving the conservative bound `2b+1` iterations. Neither the number of iterations nor `b` increases the simultaneous scratch-word bound.

At termination the source frees `r0,r1,t1`. A unit returns only `t0`; a nonunit also frees `t0`. Every nested arithmetic routine restores borrowed heads, so the original inputs are unchanged. Copies of the Euclidean locals are fresh even when external operands alias constants.

The ten-word multiplication overlap is real. The exact `inverse(2)` at `M=5` returns 3 and reaches ten additional words. Its three borrowed words are modulus, `ring.one` and operand. Including the template, fourteen complete four-bit words occupy **70** non-LEFT symbols. Seven unrelated borrowed words increase that peak to **105**, without changing the ten-word scratch bound. The nonunit call at `M=15,a=6` also reaches ten and releases all temporary words.

### Failure boundary

These are successful-execution and ordinary nonunit-return guarantees, not exception-safety guarantees. A capacity failure inside inversion can leave temporaries live. The caller must explicitly use the source arena's `rollback(protected)` before resuming. A twelve-slot arena rejects the three-borrowed-word witness; thirteen slots suffice. The rejection control checks explicit rollback, exact borrowed-value preservation and final erasure. It does not silently claim that inversion rolls itself back.

## Reproduce and evidence

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -Werror -B scripts/research_package.py --package research/selected-word-scratch --check-only
python3 -I -Werror -B scripts/research_package.py --package research/selected-word-scratch
```

Direct commands also work in a Git-free exported package:

```sh
python3 -I -Werror -B research/selected-word-scratch/verify.py
python3 -I -O -Werror -B research/selected-word-scratch/test_verify.py
```

The verifier authenticates both snapshots before importing source code. It runs **12,345** finite calls over moduli 2 through 19, checks outputs with Python integer arithmetic and `gcd`/`pow`, and reproduces every sharp bound. Another 56 alias and width cases reach 17-bit words and retain seven unrelated borrowed words. Selected cases use a direct occupied-cell census, independently of the source meter. Returned ownership, borrowed values/heads and full scratch erasure are checked on every successful fixture. The unit and nonunit sharp witnesses are additional cases. [RESULT.json](RESULT.json) is a fixed receipt; normal replay is read-only and `verify.py --write` explicitly regenerates it.

Thirteen focused tests cover each one-word-underbudget rejection, exact arena capacity, aliased operands, constant aliasing, nonunit cleanup and caller rollback. Export controls reject altered source bytes before execution, a wrong Git blob, a changed dependency or original path, a missing pin and an understated receipt. A positive optimized export is checked for unchanged file bytes. The checks remain enabled under `-O`.

The registered replay passed on CPython 3.12.15, and optimized direct replay passed on CPython 3.13.5, on Linux x86_64 under WSL2. The repository's `python -B -m unittest discover -s tests -p 'test_research_*.py'` suite also passed all 70 tests. New checker code passes `ruff check --select E4,E7,E9,F,I,UP,B,RUF`; source snapshots are deliberately not reformatted.

This is author-checked source analysis and finite execution. No separate reviewer process or formal proof kernel was used. The theorem uses the written loop invariants for arbitrary legal widths; the finite domain alone does not prove that theorem. Native selected GL64 execution, a complete caller replay, physical placement, precision/tape admission, outer transfer and the selected cold replay were not run for this arithmetic component.

## Engineering scope

The new checker uses bounded fixture domains, a 64-slot arena, subprocess timeouts and functions below 60 lines. It uses runtime errors rather than removable assertions for acceptance. Power-of-ten rule 3 has a managed-runtime deviation: Python and its standard library allocate dynamically. The resource theorem counts source tape content, not Python heap capacity. Finite domains and fixed per-fixture slot capacity bound the replay; heap allocation is not asserted to satisfy the physical tape model. Retained predecessor loops are data-bounded by admitted word extents and Euclidean descent, and the snapshot is not edited. Revisit this deviation only when implementing the physical allocator, rather than inferring a machine-storage theorem from these Python traces.

Build the Lever led to a rerunnable allocation checker rather than a hand-recorded peak. Prove It Works led to direct occupied-cell checks. Test Behavior Not Implementation led to independent integer outputs, ownership and one-word-underbudget failures rather than checks of meter constants alone.

## Open next questions

1. How many numerical words are retained by a complete coefficient callback when it invokes inversion? Bind the actual form matrices, generated-program frames and index residents to `L`, then add this ten-word interior. This would advance the numerical category of the first-node reserve. The blocker is the caller-level simultaneous lifetime inventory, not another inverse census.
2. Can total caller reserve be admitted after joining numerical, count, directory, control and marker categories with payload? First reconcile exact source heads and simultaneous lifetimes at peel, callback and final merge. Physical placement and the complete retained inventory remain unproved here.

The structured questions and the explicit change from the drawn helper-contract card are in [TASK.json](TASK.json). This package stops at the arithmetic component and does not expand the supplier family or change the selected frontier.

## Credit

Nick Petalas. New material is under Apache-2.0. Credit Jose Manuel `jmbarrancoml` for PR2697 and the binary-word implementation retained through PR2569/2501, with the full source/stream/hosting lineage preserved unchanged in [vendor/NOTICE.md](vendor/NOTICE.md). The arithmetic algorithms and their tape implementation are predecessor work. This contribution adds the simultaneous-lifetime proof, exact scratch invoice and failure-sensitive checks.

The surrounding handoff includes Nick Petalas's PR2708/2743 payload audits, starship-s's PR2731 residual audit, and PR2749's separate countdown-storage component. None is relabelled as this arithmetic result or as full supplier admission.
