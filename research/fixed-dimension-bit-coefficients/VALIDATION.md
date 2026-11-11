# Executed validation and limits

CPython 3.12.14 on Linux, standard library only, 2026-11-10.
Scientific base: e54523517d0f03e58352e647c403a5af3e525a57.

Executed from the repository root:

```sh
python3 -B scripts/research_package.py --package research/fixed-dimension-bit-coefficients --check-only
python3 -B research/fixed-dimension-bit-coefficients/verify.py --write-result
python3 -B scripts/research_package.py --package research/fixed-dimension-bit-coefficients
```

The metadata/live-pin gate passed. The final registered run passed fourteen
positive exact cases and ten controls in both normal and optimized modes,
with identical typed receipt digest
`afd86ba5470b877b6cad58a86fe26a58d98bb7e81129be4f1db47fd1a285a39a`.
The final marker was
`PASS_REGISTERED_RESEARCH_PACKAGE research/fixed-dimension-bit-coefficients outcome=partial`.

The positive suite uses dense N=2/3 fields and a separate signed-permutation
determinant/cofactor oracle, plus the exact two-axis block formula with fixed
middle pivots for large N. It covers Good, Pair in both physical orientations,
Unit and halved Unit, global fields before a reset, inverse offset, actual
leaf calls, repeated fixed-role reentry and warm erased numerical backing.
N=44/rank43, N=65 and N=130 test the three historical finite limits. Actual
pending demand is observed before the allocation guard, and runtime word
decoding and fresh Tape construction are prohibited during every measured
call. Borrowed record bytes/heads, empty stacks and live numerical retirement
are checked on normal return.

Ten controls reject three invalid dimension inputs, genuine numerical quota
exhaustion, a wrong original label in a dead earlier field, a truncated
materialized field, the old 128 multiplier guard, the old rank-42 guard, the
old 64² reader and fresh continuation tape construction. These controls
exercise runtime guards and instrumentation; they are not an exhaustive
malformed-input theorem.

The separate boundary suite builds a Git-free mirror of this package and
exactly its fifteen declared scientific source inputs. It passes normal and
optimized replays, then requires failing subprocesses after (1) changing
receipt integer schema 1 to Boolean true, (2) appending a source byte, and
(3) replacing the residue pending allowance by one. These are actual failed
replays, not tests that merely expect a Python exception from the same helper.

The written proof, not bounded examples, supplies arbitrary finite depth and
dimension. The exact selected `.0034` catalogue/Program mapping, actual root
coupling, literal transition-table lowering, varying-precision physical bank,
all caller/producer/payload histories and the complete supplier remain open.
No selected cold replay, practical huge compiler instance, formal-kernel
verification or independent human review has been run or claimed.

A separate research worker completed independent review of author commit
edb41e730cf23e82c6a20d57f21434beb769781b. Its rank-two I-J/3 and
permutation-projector oracles cover14 exact calls, original17-bit labels,
complete prefix restoration and fixed-tape reentry. Ten compilation boundary
probes extend through N=65536; three actual constructors cross old limits.
Its source derivation checks pre-guard capacity and all four stack histories.
Normal and optimized checks print PASS_INDEPENDENT_COEFFICIENT_REVIEW 10 14 3 816 12.
The lease control confirms stale abort is not generation-guarded; only the
explicit normal linear-use interface is admitted. Exact code/proof pins and
review artifacts are under independent-review. This separate AI-assisted
review does not alter the author receipt or claim human/kernel acceptance.
