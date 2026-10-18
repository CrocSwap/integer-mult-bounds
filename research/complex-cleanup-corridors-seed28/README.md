# An all-length read barrier in the selected complex cleanup

The fixed PR1094 complex supplier's FULL-frame cleanup contains 6,680 macros: 6,574 ADDs and 106 SCALEs. Its ADDs use 6,463 distinct ordered (destination, source) pairs. Exactly 111 pairs repeat, each exactly twice. Every repeated pair has an intervening explicit read of its destination. RESULT.json records a literal first and last read index and the read count for all 111 pairs.

Consequently no target-unread repeated-operand corridor exists at any length in this fixed cleanup. This excludes the declared endpoint-combination class before coefficients, source updates or profitability need testing. It is a finite obstruction for a particular rewrite class, not a lower bound on arbitrary cleanup circuits, commuting rewrites, or global refactorizations.

## Reproduction

From the repository root, using Python 3.10 or later and only the standard library:

~~~text
python -I -O -B research/complex-cleanup-corridors-seed28/verify.py
python -I -O -B research/complex-cleanup-corridors-seed28/test_package.py
~~~

The first prints PASS_CLEANUP_CORRIDOR_BARRIER with macros=6680, repeated=111, blocked=111 and controls=7. The second tests minimal relocation and five fail-closed corruptions. The verifier reads exactly the four mandatory sources in SOURCES.json; no mutable selected-result pointer is required. --write regenerates RESULT.json.

The forward engine enumerates every pair of ADD endpoints sharing a destination and source, then scans the intervening operations for reads. An independently written backward engine assigns an epoch to each register, changing that epoch on an explicit source read. It reports the same first-read indices and rejects any repeated pair in the same destination epoch. It imports no producer or forward-engine code. See PROOF.md for the coverage argument.

## Declared class and price

An endpoint pair is a += q*b ... a += p*b. The interior may add to a, but may neither explicitly read a as the source of an ADD nor scale a. The initial pilot also restricted the source to at most one ADD update and the interior to 64 operations. The tested relaxation allowed other additions to a and arbitrary endpoint coefficients. Both found zero improvements. The final certificate removes the length cap and source restriction entirely for the necessary target-unread condition. This is the one evidence-driven pivot from a bounded optimization pilot to a complete structural exclusion.

An ADD's implicit use of its old destination is permitted; explicit read means the source operand is a. The test does not equate an intervening read with impossibility of every conceivable algebraic rewrite. Such corridors are simply outside this class.

The unmodified cleanup costs 26,541 real-component primitives, or 53,082 complex primitives, under the pinned PR696 lowering. The local formula is checked against the complete emitted primitive list for every one of the 6,680 macros. Unit ADD costs two (accumulation and work CLEAR). For reduced q=n/2^d other than +/-1, ADD costs 3 + (bit_length(abs(n))-1) + (popcount(abs(n))-1) + d, including overwrite COPY, all doubles/adds/halves, accumulation and final CLEAR. A signed power-of-two SCALE pays its doubles/halves and optional NEGATE. No work-state saving or new macro/Clifford/provider invoice is claimed.

Seven semantic controls reject three damaged read certificates, detect and exactly replay three planted profitable corridors on every rational input column, and exhibit the failure of cancelling endpoints across a read. Five packaging controls reject a missing source entry, duplicate JSON key, nonfinite JSON, altered consumed source and Boolean-for-integer receipt substitution. Runtime checks remain active under -O.

## Provenance and limits

The frozen base is ce7ad1b6ab09452c3478723a2e96ed5ff212dc08. PR1094 keeps PR1042's seven-slot R480 local word while changing hosted ownership. Its selected-source manifest binds the same SLOT-PINS-k8 file. We read the named slots/local/CANONICAL-WORD.json.gz member from the retained PR1042 replay archive and require its decompressed SHA-256 4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c. All cleanup gates are verified to use the full nine-dimensional frame.

The word and assembly retain the LeaverSAT/LeaverSAT2, icekylinx, Jeremy Kothe and Rohan Arun lineage. PR696 supplies the paid dyadic lowering; this package does not claim that lowering or the scalar identities as new. The new result is the complete pinned obstruction certificate and independent replay. Factory-cache work PR1032/1064 and short-window factory minima PR1033 concern a different stream/class. Fresh PR1119 proposes a two-sided Markowitz refactor of a historical U8 cleanup; this certificate neither duplicates nor excludes its global matrix refactorization.

No word is replaced, no kappa is improved, and no all-circuit optimum is claimed. Native C++/provider invoices, Clifford phases, precision and H2 admission are not re-executed by this package. Contributor @woklerx, with substantial OpenAI Codex assistance; Apache-2.0. No independent human review is claimed.
