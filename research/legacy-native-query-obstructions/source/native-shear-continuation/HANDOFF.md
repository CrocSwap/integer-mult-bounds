# Native plane lower-bound handoff

This lane uses exact rational ADDRESS maps and binary DATA coefficients.
The root checkout and upstream source must stay unchanged.
The disk floor is 3 GiB. Use one CPU and no paid compute.

The target is three complete productive roles with plane endpoint -I2.
The new sharp result requires six rational rank-one ADDRESS queries.
It permits all determinant signs, all binary rank-one idempotents,
free binary DATA basis changes, and arbitrary dirty helper roles that
return identity on every input. Six coordinate-reflection queries attain
the bound. Read THEOREM.md first.

The exact five-map search in ../native-infinite-search/first-relation
tested 94,080 words and found none. It used two negative maps, two
reciprocal positive determinant magnitudes, and one unipotent. The two
negative maps shared one projector. The reciprocal positive magnitudes
also shared one projector. All 120 map orders and all 28 by 28 remaining
projector choices were tested. The search does not prove a general bound.

The proof covers each possible sign count among five queries:

- Four negative and one positive: a four-projector sum-zero factorization
  forces the sole positive image to be a coloop.
- All positive: ADDRESS subset extrema give two normal forms. Nonunit
  determinants give the same four-projector obstruction. Unit determinants
  give direct target coefficient contradictions.
- Two negative and three positive: the negatives must be opposite
  reflections. The positives must be three distinct unipotents with product
  -I2. At most one four-query target subset is possible. The first and last
  selected query indices then contradict each other.

The direct proof does not need a finite reflection classification, a
free-group theorem, a solver, or a finite DATA exhaustion. All statements
require exact formal binary group-algebra equality on arbitrary inputs.
A test in one finite field is not an exact native certificate.

Separate exact verification checks also pass:

- The new opposite-reflection and three-unipotent family tested all 120
  orders, all 28^3 positive projector choices before justified filters,
  and all 9,840 eligible words. There was no word. Independent direct
  dictionary replay agrees on every full coefficient and the digest.
- The two positive normal forms each tested 82,320 admissible choices
  from 28^4 choices after fixing the first projector. Neither had a word.
- The independent positive verifier checks all 32 ADDRESS subsets per
  form, symbolic target coefficient identities, the unique full-word
  coefficient, query determinants and rational conjugation identities.
- The independent six-query positive control passes. Each single-call
  omission gives the exact expected broken endpoint.

The independent proof reviews are in independent-audit/. The restored
dirty-helper extension is stated separately in HELPER-AUDIT.md there.
Initialized, discarded and other partial helper contracts are outside
the proof. No helper enumeration was used.

Run the standard-library checks from this directory:

    python3 -B search.py
    python3 -B positive_five_check.py
    python3 -B independent-audit/check.py
    python3 -B independent-audit/positive_five_check.py

The run paths and source hashes are in VERIFICATION.json.

No new native word, integer kappa gain, or PR is claimed in this lane.
Five plane queries plus three independent axis flips cannot give the
proposed eight-call three-coordinate word. A general eight-call
three-coordinate nonmonomial word remains open. There is no global
novelty claim. AI assistance was used in the proof and verification.

Run path:
/Users/aliromman/Documents/Codex/2026-10-10/hello-i-want-to-get-some/work/autonomous-kappa-run
