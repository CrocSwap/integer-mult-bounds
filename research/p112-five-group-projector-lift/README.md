# A sharp five-group P112 floor for low-tariff factors

On the five explicit triads in [CANDIDATE.json](CANDIDATE.json), every finite
rational `I15` decoder using only whole-group tariffs at most 3 costs at
least **45**. Direct copies attain 45. The result allows any number of
terms and arbitrary rational coefficients, denominators and payload mixing.

The auxiliary lift has four exceptional support rectangles. A projector
rank argument bounds how often they can occur, proving the floor even
though the lift does not dominate them individually. A cheaper decoder
on these triads must use at least one term costing 4 or more.

This is a scoped obstruction, not a cheaper construction. Frames containing
higher-tariff terms remain outside the theorem; the general local minimum
and global 296 target are unresolved. No improved native supplier or
multiplication bound is claimed.

## Evidence and replay

[PROOF.md](PROOF.md) proves the all-term theorem. [CERTIFICATE.json](CERTIFICATE.json)
stores the integer matrix `3H` and the complete four-defect catalogue. Two
standard-library replays independently check all 961 support rectangles,
including all 20 tariff-2 rectangles. The original 21-branch exclusion for
16 terms (two tariff 1, fourteen tariff 3) is retained as secondary evidence.

From the repository root with Python 3.12:

```sh
python3 -I -O -B research/p112-five-group-projector-lift/verify.py
python3 -I -O -B research/p112-five-group-projector-lift/independent.py
python3 scripts/research_package.py --package research/p112-five-group-projector-lift
```

Both mathematical replays are read-only and accept `--repo-root PATH`.
A Git-free export needs only this package and the exact archived input path
in [VERIFY.json](VERIFY.json). The container/member and local data are
hash-authenticated. No unpublished geometry list, predecessor partition,
solver or search output is required. Registered metadata checks additionally
resolve historical provenance through Git.

The primary uses Fraction elimination; the independent checker uses
primitive integer elimination and reverse-order enumeration. Neither
imports the other. Controls include direct-copy attainment, a literal
45-dimensional lifted identity, rational factors, repeated-type surplus
projectors, and material rank/endpoint mutations.

## Open next questions

[TASK.json](TASK.json) asks whether higher-tariff terms or a changed geometry
can yield a fully priced saving. The auxiliary lift has additional excess
rectangles at tariffs 4 and higher, so the present counting argument must
not be extrapolated to those families.

## Sources and credit

The binary labels come from the immutable selected replay archive recorded
in [SOURCES.json](SOURCES.json), with its original attribution retained.
The five custom triads are explicit package data. The broader rational
decoder investigation follows flyingviper's [PR 2757](https://github.com/CrocSwap/integer-mult-bounds/pull/2757),
historical head `18da668a4f248f5c0cf3fc94355068ead4db3476`; that head is context,
not a replay dependency or scientific admission. This package starts from
canonical main `d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.

Author: flyingviper, with substantial OpenAI Codex assistance. Separate AI
agents developed and reviewed the proof and independent implementations.
Human mathematical review remains open. License: Apache-2.0.
