# Primary runtime review after both sealed firsts

Verdict: **PASS for the frozen four-case finite audit; no correction requested**. This is static implementation review plus inspection of retained data after the coordinator released both firsts. It is not another interpreter run, an oracle-code review, independent end-to-end construction or a general theorem proof.

I read only the new PRIMARY runtime, its preseal/run metadata, frozen contract/clarification, FIRST-COMPARE.json and the actual retained first packets. I did not read the new oracle code or execute any engine, source constructor, checker, interpreter, compiler or scientific program. Read-only text, SHA/length and JSON data inspection support this review. The prior source semantics/entry exposure is recorded in CONTRACT-REVIEW.md.

## Exact reviewed artifacts

- `PRIMARY/primary.py` and `PRIMARY-FIRST/sealed/primary.py` both SHA256 `81fe817444ac435262a82999b031df8c17a682023b3c063c602e80784cd0e2ad`, matching the pre-first seal.
- CONTRACT.json SHA256 `3290f65dcdb7f7eae7d4ec741ec128d67822512a20b4977b30c84c7ce1f35035`; CASES.json `03d89ab4df0a679f3cbde69143a80ec65c07eb0186db6027d16344fef4b4e3d0`; SOURCE-PINS.json `46ef2331b7a636e025978d5fd9f5e638b375d28f1b1438699c8fbb8ed43b12dc`.
- Pre-first CLARIFICATION.json SHA256 `f203b4d35780ef1cdf39304e92be2a468e1a5424cb9d09568fefce06c12cc365` specifies literal bit lists, not counts.
- Actual PRIMARY-FIRST/CERTIFICATE.json and ORACLE-FIRST/ORACLE.json independently hash to `d41ee0c061414355b94aa082c7e44f79508b6b63942cf1bdd489f544bd40514b`, each392,273 bytes.
- FIRST-COMPARE.json SHA256 `e3252dcfba66e56428d0445e49efab92712819972629a2b355fa5a39b847aef0` records complete equality only after both firsts finished. I checked actual file hashes and packet projections rather than relying only on that summary.

## Implementation findings

**Source and complete table binding:** `authenticate()` checks all three literal metadata hashes before import, then every one of fourteen source object's exact byte length, SHA256 and Git blob, with unique relative paths. `candidate()` bounds gzip expansion, validates the original complete instruction grammar, and invokes the authenticated source `build(4,3,1)` once. It compares the entire constructed program and metadata with the original table, not just instruction counts or a digest. The interpreted program is the authenticated original data after that equality. The source constructor and its Program/Assembler classes are shared deliberately; no source Machine/Tape runtime or source checker/expected function is called.

**Literal runtime:** `Sparse.dispatch()` implements the source's explicit/default branch, write, unit move, goto, halt and reject semantics. The loop increments the transition count before every dispatch, so final HALT is charged. It checks PC and per-case step caps, records branch/write accesses and both move endpoints, and never removes visits on erasure. No observer supplies a program value, restored state, branch or continuation. The actual fixed source table has25 tapes, entry0 and20,897 instructions; its full program/metadata canonical hash is `25f310685f3465e329f6fdfbf4de4954f7d2eca2bbde78ff3d9ee7ee083e404f`.

**Ownership and endpoint:** fixture construction follows CASES, including canonical three-bit packets, raw unary depth, negative/prefix markers and far spectators. `write()` checks attempted writes even when idempotent against root prefixes/markers, spectators, root source/A/R packets and the complete width/depth tapes. Child segments beyond those root packets remain owned. `finish()` computes the semantic expected bit word, constructs the whole expected final25-tape state from an independent copy of the initial maps, and compares actual complete maps and heads. This checks all borrowed bytes, hidden leftover owned cells, guards and all heads, rather than only output decoding. Retained backing is the per-tape cardinality of initial support union persistent visits; final sparse support is not substituted.

**Actual observations:** node/grant methods decode live cells and check current shape and complete bank length. The snapshot builder creates new sorted cell lists and integer heads, so snapshots do not alias the subsequently mutable tape dictionaries. `pop()` compares the full actual restored snapshot object to its saved object before producing hashes and independently checks depth before the RETURN-left move. `save_output()` captures actual changed child bits; the pre-retirement observation compares the actual global relay bits to those captured bits. Matching observer stacks must be empty at final halt. The packet retains full source/bank/output bit lists, not lengths. These checks corroborate the finite execution; a patterned input still cannot establish every possible bit assignment or an arbitrary-input address theorem.

**Controls and parsing:** mutations are applied to deep-copied actual program rows and revalidated as legal instructions. The four negative controls count only `Semantic` failures from literal rejection, ownership, packet/observer or endpoint checks. A generic `Failure`, parser fault, bad mutation predicate, PC error, runtime step/visited-address gate or arbitrary exception does not become a passing negative control. Observer packet-decoding bounds are themselves `Semantic` guards, so the recorded class deliberately includes malformed observed packets and does not prove one specific rejection message. The positive wrong-H one-edge case executes all healthy checks. The receipt parser rejects duplicate keys, floats/nonfinite tokens and boolean substitutions for generated integers through recursive strict type comparison; final exact canonical bytes then enforce all values/keys/list lengths, not merely shape. No acceptance gate depends on Python `assert`. Default/check regenerate the complete packet; emission is explicit.

## Actual first evidence inspected

| Case | Steps including HALT | Node/grant/return rows | Retained backing |
|---|---:|---:|---:|
| w1d0 | 3,920 | 1/0/0 | 446 |
| w2d1 | 113,359 | 3/2/2 | 2,556 |
| w2d2 | 1,426,487 | 7/6/6 | 24,053 |
| w3d1 | 787,049 | 3/2/2 | 17,604 |

Each actual case retains25 cell maps,25 heads and25 visit lists. The fourteen source rows have the expected actual stream lengths; the ten grant/return bit lists retain complete streams (for depth two, lengths432,108,108,432,108,108 in grant order and108,108,432,108,108,432 in return order). All ten before/after restoration hash pairs in the actual packet agree. All five ordered control rows match the frozen outcomes: four semantic rejections and the positive one-edge wrong-H pass. The stored generic `semantic_rejected` outcome does not by itself identify the exact internal error message; do not claim a finer measured cause unless separately logged.

The primary first ran under managed Python3.12.14, 14:05:37.247945–14:05:38.411593 UTC, exit0, elapsed1.163676958s and peak RSS53,035,008 bytes. The retained oracle first summary records exit0, elapsed1.916957458s and56,377,344 bytes. Those are coordinator run receipts, not measurements from this review. They are below the frozen forecast/limits. I make no claim here about later normal/optimized modes, CLI mutation suites, registered checks, export/cold replay, publication or hosted CI.

## Correlation and remaining scope

No concrete runtime, observer or endpoint bug was found. Agreement alone is not the basis of this conclusion: the primary instruction loop, full object comparisons, ownership rules, finite expected model and control classifier were inspected against the frozen source contract. Nevertheless, construction and the declared semantics are shared inputs; both engines could inherit a wrong source/specification or a common conceptual mistake. The second engine's implementation is outside this review. The source's prior all-depth theorem and S4's written review retain their separate credit and premises.

The contribution is finite corroboration on these exact four prepared words, not a new recursion theorem, universal/native admission, resource-optimal algorithm, full outer supplier invoice, exponent or kappa. Root/marker preparation, natural-root/final-caller linkage, numerical weights, BIT/Gaussian behavior, stock/routes/precision/compiler costs and all five selected assumptions remain open. No frontier/adoption/merge change follows.
