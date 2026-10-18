# Commuting ADDs cannot escape the selected R480 frame runs

For the PR1042 seven-slot word selected at the frozen base, every sequence of legal adjacent commuting-ADD moves with frame slots fixed stays within the original constant-frame runs. Consequently it preserves the entire paid local profile. The certificate exhausts all 11,811 commuting pairs that can be exposed across 1,666 frame boundaries, including arbitrary earlier commuting reorderings inside the runs. Every crossing fails an exact label-subspace containment check.

This is a scoped negative result for a scheduling mechanism, not general circuit or frame optimality. It improves on checking only the immediately adjacent pairs. A synthetic control demonstrates a legal crossing that becomes visible only after an exposure reorder, so the additional coverage is tested.

From the repository root, using Python 3.10+ and only its standard library:

```
python -I -B research/complex-frame-slot-transpositions-seed27/verify.py
python -I -O -B research/complex-frame-slot-transpositions-seed27/verify.py
```

Expected:

```
PASS_COMPLEX_FRAME_SLOT_S27 exposed=11848 commuting=11811 legal_crossings=0 controls=11
```

The verifier reads the archived word directly, checks its exact payload and container hashes, recounts the complete local profile, and checks every crossing with both an affected-register calculation and a separate whole-stage reconstruction. It also checks exact rational scalar commutation and eleven controls. No predecessor implementation is imported. Default replay compares the complete receipt; only explicit `--write` regenerates it. Acceptance remains active under `-O`.

The baseline is `ba82555c64e1879e4b7decce28186f208fcb8262`, selected PR1042 with unchanged kappa `1672188119205421/10^18`. The word is archive member `slots/local/FULL-WORD.json.gz`, decoded hash `c2b29430...`. This package does not use the stale R492 package evidence word. The selected assembly is an immutable provenance guard, not a fresh native admission.

Upstream subsequently moved to PR1094 at `ce7ad1b6`; this package deliberately remains a statement about the pinned PR1042 word and does not assert that it is the latest frontier.

The scope fixes the A and B stage boundaries, all ordered frame slots and all non-ADD operations. Each intermediate move must pass the label-span monotonicity checks. Those checks are necessary rather than a claim of full native, Clifford or physical legality. Frame reassignment, simultaneous multi-gate moves, invalid intermediate schedules and coefficient-prefix precision are outside the result. No new word, paid saving or kappa is claimed.

See `PROOF.md` for the completeness argument, `CERTIFICATE.json` for counts and rejection transcript hashes, and `OVERLAP.md` for related work. Prepared for @woklerx with substantial OpenAI Codex assistance; Apache-2.0.
