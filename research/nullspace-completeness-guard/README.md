# Complete nullspace admission for the recycled-bit initializer

An opt-in guard closes the fail-closed completeness gap explicitly identified
in [PR2537](https://github.com/CrocSwap/integer-mult-bounds/pull/2537), Open next
question 4. A dropped null vector can make `inside()` accept more vectors.
Checking row count and annihilation alone also misses duplicate or zero rows.
This package certifies both independence and completeness before admitting a
candidate kernel. Production sources and their certificate pins remain unchanged.

## Scope and evidence

For an integer matrix A with n columns and k proposed integer nullspace rows B,
the guard requires exact AB^T=0, rank_Q(B)>=k and rank_Q(A)>=n-k. Rank-nullity
then forces row(B)=ker(A). [PROOF.md](PROOF.md) gives the elementary rank argument,
including empty/full kernels and zero ambient dimension. A diagonal minor or a
nonzero minor modulo a checked prime certifies a rank lower bound. Exact rational
elimination handles unlucky primes. No probabilistic rank equality is assumed.

The candidate function is extracted unchanged from PR2537 commit
`222063b96ec1a109a8c9f40e5d615498a737c6dd`, after authentication of its vendored
source. All executed upstream code and data are pinned before import. The
unchanged actual `frames147.Exact` initializer exercises **4,473 calls**, all
certified with a modular input-rank witness and a diagonal basis minor. The
ordered input/output SHA-256 is
`0525017d083c4485ee12e8e043902c74972efe17c39c568b3ba2f5a67043bdd1`.
Deletion and duplication of a basis row from an actual call are rejected.

Independent determinant enumeration checks all matrices with 0..2 rows,
0..3 columns and entries -1,0,1. Additional controls reject deleted, duplicated,
zero, nonannihilating, malformed and noninteger rows, invalid dimensions, too
many rows and a candidate that mutates its input. Both unlucky-prime fallback
routes are exercised. Signed, scaled and permuted valid bases are accepted:
this guards the rational row space, not canonical normalization or order.

This is a complete initializer census, **not** a replay of the 145,513-call
all-key audit, fresh/all ledger moves, scalar identity, nondegeneracy, pricing
or a complete multiplication theorem. The rank criterion has an all-size proof;
the implementation and inherited call-path evidence are finite. Existing
canonical-row equivalence checks remain useful and distinct. There is no new
supplier, native operation count, speedup claim or selected exponent.

Original picker card: `independent-moment`, seed
`02f687b97629cf91c38008d55a22321d`. Its baseline binding check passed. The scope
change from rank-ledger reconstruction to a missing annihilator trust guard is
recorded in [TASK.json](TASK.json). [SOURCES.json](SOURCES.json) pins base inputs;
[SNAPSHOTS.json](SNAPSHOTS.json) pins the external candidate and its explanation.
This is a continuation of the producer's documented gap, not a newly discovered
failure or a replacement for its full canonical-output audit.

## Reproduce

From the repository root, with Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/nullspace-completeness-guard --check-only
python3.12 scripts/research_package.py --package research/nullspace-completeness-guard
```

The registered replay preserves the inherited initializer assertions. A separate
`python -O -B research/nullspace-completeness-guard/verify.py --controls-only`
checks that the guard's own controls survive disabled assertions. Trying the
actual initializer under `-O` fails closed. Checks never rewrite the receipt;
`--write` explicitly regenerates it for review. No third-party dependency or
network access is needed.

## Open next questions

Should the guard be adopted in the production installer? The next step is to
wrap `null_fast`, replay the full `--all` ledger and measure total cost. That
requires a separate source/certificate-pin update and maintainer acceptance;
this opt-in package does not change the production default.

## Credit

The rank-nullity and modular-minor principles are standard linear algebra.
thakrarsagar's PR2537 supplies the fraction-free candidate, equality audit and
explicit missing-vector warning. Its source and notices are retained unchanged.
The recycled-bit integration is by Douglas Colkitt with OpenAI Codex assistance,
building on Thomas Marchand, William Porter, Rohan Gupta and DaysSky. PR97's
physical-ledger work is by Zhihao Chen; its frame/lifted sources and witness are
by Swapnil Jain. The imported `word147.py` retains its finer predecessor credits.
New guard, proof application and admission tests: ywz65 with substantial OpenAI
Codex assistance, Apache-2.0. Separate AI review is not maintainer acceptance.
