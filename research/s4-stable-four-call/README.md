# Four calls remain optimal with every odd S4 permutation

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration. For every
finite r>=2, every target diag([a],[b],1,...,1), with nonidentity even
permutations a,b in S4, has exact paid-call minimum four in the following
formal binary group-algebra model. A paid call is I+([g]+1)N, where g is
any odd permutation at unit cost and N is any binary rank-one idempotent.
Arbitrary scalar GL_r(F2) maps are free. Every extra register is dirty and
must return to its individual input value. The case a=b is included.

The changed hypothesis is the paid alphabet. All twelve odd permutations
are available, including six four-cycles. Cinna Davis's [#1749](https://github.com/CrocSwap/integer-mult-bounds/pull/1749) gives the
four-role adjacent-transposition case; Ross Richardson's [#1989](https://github.com/CrocSwap/integer-mult-bounds/pull/1989) already
settles adjacent-transposition tariffs with arbitrary dirty workspace.
Those theorems are cited, not replayed. The new maximum-alphabet result
covers all ordered pairs of the eleven nonidentity even S4 permutations.
No kappa, native supplier or selected-frontier change is claimed.

## Proof

[PROOF.md](PROOF.md) gives the complete argument. Augmentation normalizes
all free scalar maps away from the endpoint. The inherited sign-determinant
method forces an even number of odd-label calls. A two-call product has at
most one nonidentity even coefficient, of scalar rank at most one. The
target's even coefficient rank sum is two, including when a=b. Four
coordinate calls attain every target. The proof applies at every finite
register count; the finite checks below only corroborate it.

## Evidence and reproduction

From the worktree root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/s4-stable-four-call/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/s4-stable-four-call/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/s4-stable-four-call
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/s4-stable-four-call --check-source-history
```

A reviewer can substitute any CPython 3.12 executable. The expected marker
is PASS_S4_STABLE_FOUR_CALL. The verifier writes only stdout and prints a
generated receipt with the SHA256 of every package file. No receipt is
handwritten or committed. Explicit exceptions retain all checks with -O.

The verifier multiplies the full formal group-algebra matrices for all
118,080 two-call words in the larger alphabet at r=2,3. It checks (1) independently
against convolution and checks the even coefficient rank bound. It builds
363 four-call endpoints for all 121 target pairs at r=2,3,5 and checks
29,040 dirty basis columns through a separate literal permutation-action
implementation. All 484 single-call omissions are rejected.
It also checks 650 sign determinants at r=2,3,4,5, all 432 two-role scalar
covariances and five hypothesis controls. These
include two-call counterexamples if even paid labels or scalar rank two
are allowed, and a rejection of treating four-cycle calls as involutions.

The card's historical first command, scripts/research_baseline.py, was
attempted and failed with KeyError: 'bit_lower' under the selected schema.
The current scripts/research_selected_baseline.py passed with
PASS_RESEARCH_BASELINE_BINDINGS_ONLY. Neither is a scientific dependency
or an operator replay, and neither was changed here.

## Limits and implementation bounds

Only odd paid labels and rank-one idempotents are covered. Free address
maps, even paid labels, higher-rank paid calls, clean-only endpoints and
changed restoration contracts can change the answer. Nothing here prices
coefficient preparation, native implementation, scalar basis changes,
routing, physical restoration, tape, precision or a completed consumer.
These costs remain unknown. Independent human and formal proof-kernel
review are unclaimed. Lean, Docker and selected cold replay were not run.

The verifier has no recursion or subprocesses. Its loop domains are fixed
at 24 group elements and at most five roles. It streams two-call words,
retaining at most 24 scalar coefficient blocks per formal matrix. Finite
Python tuples, dictionaries, integers and JSON serialization require
managed allocation; this is a bounded-domain deviation from fixed
steady-state allocation. Each hashed file is limited to 256 KiB. No
shared code, pinned evidence or predecessor file changes.

The bit-new-register-model card is changed to a formal side result with
an enlarged paid-label set. It is not a physical construction expansion.
Historical provenance, source pins and structured next questions are in
[TASK.json](TASK.json) and [SOURCES.json](SOURCES.json).

## Open next questions

1. Can three nonidentity even targets share fewer than six calls in the
   maximal odd-label alphabet? Start with four calls, the only remaining
   candidate after parity. The two-call coefficient rank proof does not
   bound the even coefficient sum of a four-call word.
2. Can a physical interface supply any nonadjacent odd permutation below
   its complete adjacent-word price? Start with one four-cycle, accounting
   for address preparation, scalar maps, restoration and routing. No such
   implementation or complete consumer is supplied here.

These follow-ups are not investigated or reserved.

## Credit and overlap

Cinna Davis #1749 supplies the original three-cycle/extra-register question
and #1734 supplies the sign-determinant precedent. Ross Richardson #1989
supplies the exact adjacent-label theorem and normalization context, with
Adam Gall #1941 and Ross Richardson #1966 retaining the cut-method lineage.
Retain eumemic #288, Ali Romman #468, David Govea #720 and Gareth Davidson
#1333 for the register-model lineage. Original predecessor credit lines
and files remain unchanged. The new result is the enlarged-alphabet
four-call theorem and its coefficient-rank proof.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19145529).
Live open PRs, this account's recent work, the latest handoffs and local
reservations were checked before claiming. Distinctive searches covered
merged PRs and all main-branch README paths. The cached overlap report
covered 314 open PRs and 4,389 Discussion records, but only 178 of 6,996
main README paths in the sparse checkout; direct Git searches supplied
the main-branch coverage. Arbitrary diffs and unpublished work remain
outside that coverage. This is not a novelty certificate.
