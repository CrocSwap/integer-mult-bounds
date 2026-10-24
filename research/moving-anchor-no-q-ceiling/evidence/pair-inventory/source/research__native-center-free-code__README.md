# A center-free native producer with an explicit eight-mode port code

This emits an exact changed native word with all eight rank-8 owned-center calls removed. All 632 persistent inputs remain arbitrary and independent, all 408 helper jobs remain autonomous, and the actual entrance/exit charts stay unchanged. The main logical endpoint is

```text
(X, Y, H) -> (X, Y + A X, H).
```

The explicit 112-by-112 code is `A = I - 14 P`, where `P` is an orthogonal projection of rank 8. Its eigenvalues are 1 (104 times) and -13 (8 times), with `A^-1 = I + (A-I)/13`. The forward and actual raw-dual paid profile is `{1:2201, 2:412, 3:510, 4:127, 5:40}`: eight rank-8 children disappear, with no new Gaussian child. The simple compensation uses 6,596 fixed dyadic ADDs.

**No improved κ or complete multiplier is established.** This code changes the cross-transfer. Treating it as the old uncoded supplier would be wrong. Its inverse is an exact rational matrix, not a free dyadic operation across distinct physical input charts.

Read [CODED-PROOF.md](CODED-PROOF.md) for the constructive theorem and [ATTRIBUTION.md](ATTRIBUTION.md) for overlap and predecessor credit.

## Reproduce

Only Python 3.12 and its standard library are required; there are no Windows paths, external commands, GPU libraries or platform-specific native binaries in the scientific verifier.

```sh
python3.12 -I -B research/native-center-free-code/coded_verify.py
python3.12 -I -O -B research/native-center-free-code/coded_verify.py
python3.12 -I -B research/native-center-free-code/verify.py
python3.12 -B scripts/research_package.py --package research/native-center-free-code
```

The written all-width proof uses evaluation of a rational free-group identity and authenticated existing native operations. Finite replay is evidence for that identity; it is not a Lean kernel or independent human audit. The inherited source physical implementation and analytic multiplication hypotheses are not independently reproved. No selected cold replay or hosted CI pass is claimed.

## Open next questions

The structured questions are in [TASK.json](TASK.json). The immediate target is a paid, source-compatible adapter or caller exploiting the eight-mode code. An actual output/input chart conversion, odd-denominator implementation, full moment, storage, precision and outer budget must be supplied before claiming a κ improvement.

Prepared by Dugongue with substantial OpenAI Codex assistance from the lead and three workers. Apache-2.0.
