# Frozen PR62 word verification

This local research adapter consumes immutable upstream PR62 commit
`ad0f25ff7b23cff7f08ad237c2254e6ecf74257e`. It performs no network access and
does not modify that checkout. The selected graph is unchanged; candidate XOR
words change only the frame compiler's clearing/reclamation choices.

`verify_words.py` independently checks complete source, target, and arbitrary
dirty auxiliary basis vectors in both orientations. It reconstructs frame
transition incidences from the literal XOR word and compares them with the
compiler's event list. Explicit index and scatter guards reject negative
indices or additional uncharged scatter operations. The unchanged upstream
C++ profiler computes all actual fixed-I+J profiles. The arithmetic checker
also verifies the bounded-minor modulus inequalities and Lucas–Lehmer prime
certificates, and requires zero CRT disagreements.

The collected characteristic derives W and rank mass from the checked axes;
it has no assertions forcing the baseline W or baseline rank mass. Every
copied center, endpoint copy, side growth, and external transition retains the
upstream accounting. Exact rational bisection selects a saving for which the
Padé/logarithm upper moment is below one. The balanced assembly then checks
47 strict inequalities, seven margins, and eventual threshold arithmetic.

Build the profiler with any compatible C++17 compiler supporting unsigned
128-bit arithmetic (e.g. the installed Zig C++ driver):

```sh
c++ -O3 -std=c++17 \
  -I UPSTREAM/references/frame-compiler/pr48/scripts/partial_swap \
  UPSTREAM/scripts/experiments/binary_frame_profiles.cpp -o frame-profiles
```

Freshly verify a selected pair of deterministic words:

```sh
python verify_words.py --upstream UPSTREAM --profiler ./frame-profiles \
  --word23 CANDIDATE/h23/word.json.gz \
  --word25 CANDIDATE/h25/word.json.gz --output RESULT
```

`frozen-sources.json` checks the exact HEAD and hashes of all consumed local
upstream code, native certificate, and compiler header before importing.
`RESULT/h23/verified-axis.json` and its h25 counterpart retain the full word,
profile, and replay receipts. The final `candidate-certificate.json` contains
the exact child list, complete characteristic, rational moment bounds,
assembly inequalities, source pins, and word hashes.

For fast search recomposition, `--receipt23` and `--receipt25` may reference
previously freshly checked axis receipts. This mode reuses their recorded
validation and freshly recomputes the combined rational characteristic and
assembly. Use the two word arguments above for a complete final replay.

Scope: unchanged geometry for all 4,073,300 data pairs and its rational
recovery cases is inherited from frozen PR62. The all-size analytic
enclosures, frame/compiler transfer, finite-alphabet tape implementation,
routing, prime selection, recovery, and eventual setup arguments remain
conditional. These finite checks do not establish an unconditional integer
multiplication theorem or practical runtime improvement. More primitive XORs
can coexist with a better recursive block profile; their counts are recorded.

Credit PR62 to Avi Eisenberg/ikeboy and PR57 to eumemic; the inherited exact
profiler and arithmetic retain their upstream contributor notices. New local
verification adapter prepared with OpenAI Codex assistance.
