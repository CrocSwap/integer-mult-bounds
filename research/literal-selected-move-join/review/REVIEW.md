# Independent orchestration review

This is a separate AI-assisted review of the frozen graph, not independent
human review or proof-assistant acceptance. It checks the contribution on
canonical base `e54523517d0f03e58352e647c403a5af3e525a57`; every predecessor
source pin remains in SOURCES.json.

## Critical checks

1. Every one of the 82,748 retained instructions is compared against the
   unchanged predecessor table under the explicit injective port/PC map.
   Module order, all targets, port bounds and absence of factor writes to
   public DATA are checked. The 65 new wrapper instructions remain the only
   composition logic.
2. A separate forward-address exact Gaussian-integer oracle uses dense binary
   matrices and integer component arithmetic, rather than the author's inverse
   addresses/CNOT words/butterfly implementation. A new full nonzero f=1 packet
   agrees, with exactly 4,096 public writes, all after the final commit boundary.
   The execution interpreter is the author's bytearray runner; this is not an
   independent implementation of that interpreter.
3. The all-f proof was checked separately: the port map has disjoint public,
   whole-call and module roles; success restores the next module's entry;
   Gaussian-unit phases and permutations preserve the reserve; each central
   axis consumes one power of two and grows the component bound by at most two.
   The exact outer overhead 31V+27 and conservative sum
   65536(3fV+132V+6E+7) are below 2^24(fV+E+1). Historical backing is added,
   never released by erasure. These universal statements inherit the cited
   unchanged predecessor graph lemmas; the finite replay is corroboration.
4. The original complete source archive was re-extracted through the pinned
   existing source repository, independently passing the source binding check.

No issue was found within the stated supplied packed entry, numerical reserve
and fixed leaf cutoff. This does not prove the selected caller supplies that
entry, a nonleaf recursive tariff, all five retained assumptions, or a new
multiplication bound. Rejection preserves public values but need not retire
private banks; the package states this limitation explicitly.

## Reproduce

From the package directory:

```sh
python3 -I -W error -B review/check_join.py
```

Expected marker: `PASS_ROOT_NATIVE_COMPOSITION_REVIEW`. The checked instruction
count is 82,813, graph SHA256 is recorded in RESULT.json, and the full fixture
uses 14,429,950 local transitions. `review/RESULT.json` records this execution.
Author regression checks and their mutations are documented separately.

Prepared by the Astra orchestration agent with substantial OpenAI Codex
assistance. Original implementation and mathematical lineage credit to
@CubeJerry and the exact predecessor authors is preserved in NOTICE.md.
