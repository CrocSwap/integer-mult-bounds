# Independent review: ordered centre interfaces

Status: **ACCEPTED after one metadata correction**.

The reviewed package is `../../ordered-centre-interfaces`.
Its `PACKAGE-SHA256.json` has SHA256
`a215deb84824b4549ced931b702fd16bc5af8978b3b5e46efba5ae475f36fac9`.
The manifest covers 139 files. The package has 140 files with the manifest.
All checks below use this final version. No proof or certificate issue remains.

## Resolved issue

The first `RESULT.json` used `required_terminal_native_mass: 5600`.
This label could state a terminal lower bound that the proofs do not give.
The two specified complete constructions each have rank mass 5600.
Their terminal rank mass is 224.

The producer replaced that field with `complete_native_rank_mass: 5600`
and `terminal_native_rank_mass: 224`. The new `native_mass_scope` states
that these values apply to the separated and mixed constructions. It
excludes a lower bound for every terminal. No proof, checker, or source
changed. The producer then made the final manifest above.

## Proof review

I read the package proof and its direct proof dependencies. I also read
the independent ordered normal forms, decoder reduction, current and
general unit codes, physical monomial codes, helper completion, one-pair
admission, D25 access, terminal hosting, native review, and primary row
split and LIFO text. The source list is in
[`DIRECT-SOURCES.json`](../../ordered-centre-interfaces/DIRECT-SOURCES.json).

The raw and weighted endpoint results have induction proofs for every
positive pair count. They do not depend only on finite test cases. The
raw decoder determinant uses the matched local Schur complement. Its
exact nullity modulo 3 also uses the explicit unit-triangular reduction.
The determinant alone does not give that nullity. These results concern
content maps. They do not prove a native decoder cost or idle access.

The general-unit one-pair construction preserves multiplication order.
The chronological word gives `(-y, T x)`, where
`T = E2 G1^-1 E0`. The physical residual is
`diag(Q T Q^-1, I)`. Its decoder has the stated reverse order.
The result requires the stated local responses and common-frame scalar
access. It gives no general multicall or decoder lower bound.

The monomial compiler acts on the complete state, including helpers and
owned fields. Its recurrence is `C_(j+1) = C_j H_j`. Admission of the
composed maps remains a premise. Every later use of a helper must use
the same coordinates. The line result is scoped to the stated transfer.
Under `b^T G a = 0`, the two ranks are `n-2` and 2. The zero-rank flag
condition is `G^T b = a`. The finite prefix screen only tests its stated
canonical prefix choices. It does not cover all stabilizer choices.

The retained 408-helper result is a separate local composition result.
Its profile has 2326 children and rank mass 3281. It is not an extra
charge in the data-only D25 word. The latter uses exactly 224 roles and
has local profile `{1:160,2:48,5:48,7:112,8:64}`, with 432 children and
rank mass 1792. Endpoint adapters are part of this contract. The D25
role and row proof uses the inherited serial cover and LIFO premises.
It does not supply an all-size native phase compiler or a full price.

The separated terminal has 224 rank-one children. The mixed terminal
has 96 rank-one and 64 rank-two children. Each adds rank mass 224.
Their complete profiles have mass `3*1792 + 224 = 5600 = 224*25`.
Each child has rank strictly between 0 and 25. Thus, for every `b > 0`,
`r^(1-b) > r*25^(-b)` for every child. Summation proves that both
specified complete words fail the strict positive native moment test.
This is not a lower bound for every terminal. The scalar subtotals,
28264 and 25896, are exact under the stated scalar primitive prices.
The mixed map-call inventory is not a complete operation price.

## Fresh independent evidence

The fresh copy used an unrelated directory, an absolute Python 3.14.7
path, `-I -B`, and `PATH=/nonexistent`. It had no Git metadata. All ten
checks ran in normal and optimized modes. All 20 runs passed in
98.034 seconds. Their outputs agree across modes. All 140 package files
remained unchanged. The source package and the copy matched before and
after replay. See [`COLD-PORTABILITY.json`](COLD-PORTABILITY.json) and
[`COLD-REPLAY.json`](COLD-REPLAY.json). Runs were serial.

I independently compared all 128 frozen inputs with their source bytes.
They match. I also rehashed the historical source archive and its exact
`DATA-PHASES.json` member. The archive SHA256 is
`f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6`.
The member SHA256 is
`c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa`.
See [`SOURCE-ORIGINS.json`](SOURCE-ORIGINS.json).

The separate [`independent_check.py`](independent_check.py) imports no
package code. Exact rational matrices verify the noncommuting unit
word, physical residual, decoder order, and full-state compiler order.
Seven negative controls reject omitted scalar codes and wrong orders.
An exhaustive three-bit matrix check uses all 168 invertible maps and
all odd line pairs. It verifies 2688 full symplectic compositions,
including 1152 orthogonal-line cases. It checks the zero-rank flag by
full matrix multiplication. It does not merely evaluate the displayed
block formulas.

That checker also reads the exact native payload and independently
replays all four words on all 224 data columns. It checks role bounds,
local profiles, unchanged helper frames, and the forward and backward
endpoints. It derives both complete profiles, both terminal masses,
and both scalar subtotals. It passed under `-I -O -B`. See
[`INDEPENDENT-CHECK.json`](INDEPENDENT-CHECK.json). These finite checks
support the separately read algebraic proofs; they do not replace them.

## Source and scope boundaries

The historical provider pins, source credit, and license notices remain
intact. The sole checker adaptation changes where the exact archive
member is read. The patch retains the source hash and all mathematical
checks. Receipt comparison excludes only that checker's own source hash.
The original source and complete adaptation patch are in the package.

The packaging base `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51` and
selected PR #4470 give context only. This review does not transfer the
historical results to that construction. No selected replay, new native
phase compiler sweep, all-size compiler proof, finite map/tape price,
precision proof, or exact integer-recovery proof ran in this review.
No complete kappa improvement follows. No commit, push, publication,
merge, or frontier change was made.
