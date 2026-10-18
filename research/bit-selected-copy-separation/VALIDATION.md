# Validation receipt

Environment: Windows, CPython 3.12.7, standard library only. Canonical main
checkpoint: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.

Passed commands:

```text
python3.12 -I -B research/bit-selected-copy-separation/verify.py
python3.12 -I -O -B research/bit-selected-copy-separation/verify.py
python3.12 -B scripts/research_package.py --package research/bit-selected-copy-separation
```

Both registered commands pass, as do source/provenance and manifest checks.
No mathematical checks depend on assertions. The primary receipt has nine maps,
36 pairs, four controls and 20,736 literal F3 Boolean-input/U/V comparisons.

A separate Codex subagent reviewed the proof, verifier, retained PR2088 README,
source pins and complete credited abstract-intertwiner README, then independently
ran the optimized verifier. No blocking finding was reported. It confirmed the
36 witness differences are seventeen `-1/4`, fifteen `+1/4`, three `+1/2` and
one `-1/2`; all nine chosen normals have squared norm four. This is assisted
independent review, not independent human review or proof-assistant verification.

The card's initial `r439-bsection-stars-seed01/verify.py` replay also passed
after TEMP/TMP were directed into a writable workspace. Its initial sandbox
temporary-directory permission failure was environmental. The replay is
orientation evidence, not a new result or selected-supplier cold replay.

Not run: the full PR2088 physical interpreter, selected cold replay, native
compiler, child scratch allocator, hosting/tape/precision or outer theorem.
Hosted CI and maintainer acceptance are not claimed by this local receipt.
