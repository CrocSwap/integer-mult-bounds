# QQ16 ordinary-caller restoration root closure

The literal retained ordinary caller has one completed five-record generation
at dispatch boundaries and at most ten generation records during restoration.
This closes the caller-retention premise left explicit by
[#5362](https://github.com/CrocSwap/integer-mult-bounds/pull/5362), for the
specific [PR2809](https://github.com/CrocSwap/integer-mult-bounds/pull/2809) caller retained in the [PR3087](https://github.com/CrocSwap/integer-mult-bounds/pull/3087) archive. It also records a useful
negative result: root completion retains its final five wrappers.

Read [PROOF.md](PROOF.md) for the root table, concrete binding/stack audit,
induction and precise exclusions. [RESULT.json](RESULT.json) records the
original full physical replay and lifetime observation; [CONTRACT.json](CONTRACT.json)
records seven rejecting source/runtime controls. Sources are immutable and
package-local, with nested archive authentication and pending-source export pins.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/qq16-restoration-root-closure --check-only
python3.12 -B scripts/research_package.py --package research/qq16-restoration-root-closure
python3.12 -B scripts/check_research_commit.py --package research/qq16-restoration-root-closure
```

The registered replay runs source/alias controls and one serial original caller
calibration. Commands have finite timeouts; see [VERIFY.json](VERIFY.json).
No third-party packages, Lean or Docker are needed. [EVIDENCE.md](EVIDENCE.md)
records the environment, limits, coverage and unrun obligations. Weak references
and host GC belong only to the checker. The original repository-wide loader
authentication and production supplier replay are not claimed.

## Attribution

Builds on [#5362](https://github.com/CrocSwap/integer-mult-bounds/pull/5362)
by [@mihir-s-05](https://github.com/mihir-s-05),
[#5330](https://github.com/CrocSwap/integer-mult-bounds/pull/5330)
and the finite handle work by [@JoyboyBrian](https://github.com/JoyboyBrian),
and the caller sources retained in
[#2809](https://github.com/CrocSwap/integer-mult-bounds/pull/2809)
by [@jmbarrancoml](https://github.com/jmbarrancoml).
Retain Chris R / [@Clear1nsight](https://github.com/Clear1nsight)'s QQ16 caller
installation, Tekalign's finite-role work, ywz65 and all original notices in the
nested archives. New package by [@zxv](https://github.com/zxv), with substantial
OpenAI Codex assistance in investigation, implementation, proof and review.
Assisted review shares the source context; no independent human or proof-kernel
acceptance is claimed. Apache-2.0.

## Open next questions

1. Extend the root audit to the complete QQ16 Installation, including parent/cut
   storage and engine adoption. This matters because the ordinary caller is
   only one embedded component. First enumerate every outer root and mutator
   against its exact class/source; the [PR3464](https://github.com/CrocSwap/integer-mult-bounds/pull/3464) machine is a distinct class.
2. Derive the complete numerical `new_context` temporary bound and charge.
   Start with its computed highs Count and Ring/Context constructors; the
   five-generation-record result does not price those objects.
3. Integrate the caller invariant with the metadata constructor and initial
   boundary compilation. First establish a source-bound simulation and charge
   for every relevant mutator; the present ten-record argument alone is not F(K).
