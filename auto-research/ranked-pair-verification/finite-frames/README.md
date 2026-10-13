# Pinned finite construction and adversarial controls

The main package README gives the fresh replay and word-generation commands.
All executable upstream sources and source manifests are compared with the
immutable PR62 Git objects before import/compilation. Generated JSON receipts
may differ in that checkout; source changes are rejected without resetting it.
Run with Python assertions enabled.

The bundled four axis receipts record the original research runs, including
their elapsed-time observations. They are immutable evidence, not outputs
rewritten by CI. New generation/profiling writes only to the requested ignored
build directory. The decompressed word hashes and exact profile fields are
the reproducibility targets; elapsed times are not mathematical certificates.

## Seven additional tampering controls

These inherit the explicit negative controls from Chafik Boukhalfa's PR60.
Use a separate checkout; do not move the PR62 source used for reproduction:

```sh
git clone --no-checkout https://github.com/CrocSwap/integer-mult-bounds.git build/ranked-pair-pr60
git -C build/ranked-pair-pr60 fetch origin e7a492dd8bee4e6f574ced784a62af2ce735edc4
git -C build/ranked-pair-pr60 checkout --detach e7a492dd8bee4e6f574ced784a62af2ce735edc4
python3 research/ranked-pair-verification/finite-frames/test_new_words.py --pr60 build/ranked-pair-pr60
```

The tests attack omitted literal XORs, self XORs, illegal frame containment,
aliased terminal roles, missing copied centers, omitted charged transitions,
and understated physical width. All seven passed against the bundled ranked
words. The independent full audit additionally rejects an unrecorded pair of
identical cancelling scatter gates, which scalar algebra alone would accept.

The source guard was tested by altering one tracked upstream source in an
isolated temporary copy: verification rejected it before execution. The copy
was restored, then checked again. Optimized Python (`-O`) is rejected.

The rank-order patch and generator are an adaptation of the PR60 priority to
Avi Eisenberg's PR62 graph with eumemic's PR57 compiler. Concurrent PR63 has
the same decompressed words and profiles. See the parent PROOF.md for credit,
AI disclosure and the full-machine proof boundary.
