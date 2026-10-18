# R480 quad 12: complete shortest-circuit census and prefix admission

This finite bit-supplier construction replaces the historical [PR503](https://github.com/CrocSwap/integer-mult-bounds/pull/503)/510 R480 quad 12 with 11 rather than 23 ADDs. Its mandatory literal cleanup saves another 12, reducing the complete local word from 33,958 to 33,934 ADDs. No new kappa is claimed.

The exact minimum has prior art in [PR1002](https://github.com/CrocSwap/integer-mult-bounds/pull/1002). After the first local experiment, an overlap comparison found that [PR1002](https://github.com/CrocSwap/integer-mult-bounds/pull/1002)'s R439 frame272 is the identical ordered circuit under a wire permutation. That contribution already establishes an unconstrained minimum of 11 and a reverse-guarded minimum of 12. Its committed witness is retained unchanged for comparison. This package credits that result and adds an exhaustive census of all 252 shortest programs, four reverse-transfer classes, and their admission in the historical R480 word. No new-minimum priority or combination with other suppliers is claimed.

Every shortest program increases three entries of the local reverse positive matrix. Nevertheless, all four reverse classes fit the complete R480 local prefix allowance. Their forward bound is 176,135, and their reverse bounds range from 3,723,720 to 3,729,576. The chosen class has the smallest reverse bound among the 252 shortest programs; its 108 members share that bound. The original reverse bound is 3,751,204. Both original and chosen words need 102 bits under the inherited 104-bit local cap. This is a concrete distinction between a sufficient local entrywise guard and complete-word precision admission.

## Reproduce

The primary replay requires Python 3.10+ and no additional packages. Run the command below from the repository root. It rebuilds the complete search and census, checks the independent breadth-first count, verifies every local Boolean input, emits and checks both complete words, and exercises 20 adverse cases. The optional native command needs a C++17 compiler and Boost headers. Set BOOST_INCLUDE to the directory containing boost/multiprecision/cpp_int.hpp; the default is /usr/include. CXX selects the compiler. Pass either command `--output /new/dir` to preserve all logs in a fresh directory. They reject an existing output directory. Certificate regeneration is explicit.

```sh
python3 -I -B research/r480-quad12-exact-seed12/verify.py --replay-search
```

Expected:

```text
PASS_R480_QUAD12 minimum=11 shortest=252 reverse_classes=4 block=23->11 ADDs=33958->33934 columns=720 controls=20 no_new_kappa
```

For the native replay:

```sh
BOOST_INCLUDE=/path/to/boost python3 -I -B research/r480-quad12-exact-seed12/native.py
```

Expected: `PASS_R480_QUAD12_NATIVE words=2 columns=960/1440/1680 bridge_controls=96 ADDs=33958->33934`.

Package failure-mode checks:

```sh
python3 -I -B research/r480-quad12-exact-seed12/test_package.py -v
```

Expected: four tests pass, including a minimal offline replay in a path with spaces under `-I -O`, a corrupted certificate, a corrupted source and existing-output preservation.

The chosen word preserves all 720 arbitrary-input columns, including 480 dirty helpers, every register's frame path, 2,940 MOVEs, nine rank-eight COPY/ERASE pairs, and the paid rank mass 5,592. Its paid histogram is unchanged. The C++ replay checks both words at five, nine and eleven stages, covering 960, 1,440 and 1,680 formal columns per word and rejecting 96 omitted-bridge controls. All 672 frame Gram checks and the retained mutable-source interface checks pass. Native bounds and bills agree exactly with the independent Python replay.

## Review map and limits

[WITNESS.json](WITNESS.json) contains the literal substitution and complete row-subtraction DAG counts. [MINIMUM-CENSUS.json](MINIMUM-CENSUS.json) lists all 252 distinct shortest programs. [CERTIFICATE.json](CERTIFICATE.json) binds the independent minimum/count, four contextual prefix checks, complete costs and negative controls. [NATIVE-CERTIFICATE.json](NATIVE-CERTIFICATE.json) retains every native receipt field except elapsed time and the input path. [PROOF.md](PROOF.md) explains the finite search class, completeness argument, composition and accounting. [SOURCES.json](SOURCES.json) records SHA-256 and Git-blob identities, with contextual sources separated from runtime inputs.

The exact base is 2921874911956718fcaaaf9396fe8267b3cfa9f0. Its selected [PR942](https://github.com/CrocSwap/integer-mult-bounds/pull/942) result remains conditional kappa 0.001661960547713947 with unchanged [PR589](https://github.com/CrocSwap/integer-mult-bounds/pull/589) bits. The R480 word is historical, and this contribution does not replace the selected supplier. Only this research package is added. No helper, source access, copy, frame change, restoration or recursive child is omitted from the complete local accounting.

The result is restricted to six existing wires, positive unit ADDs, one exact integer transfer and its literal cleanup. It does not minimize arbitrary XOR circuits, circuits with scratch, or the whole supplier. Full hosted emission, a global invoice, supplier binding and outer assembly remain separate. The inherited all-size/compiler, common-label/mutable-source realization, whole-call hosting, precision/tape and analytic obligations remain conditional. Finite tests do not formally verify the multiplication theorem. No selected cold replay, full-suite pass, remote CI pass or measured multiplication speedup is claimed. Validation details and the bounded repository-wide attempt are recorded in VALIDATION.json.

Prepared for Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance in research, implementation, verification and writing. One AI agent; no independent human review. Apache-2.0. See [NOTICE.md](NOTICE.md) for predecessor attribution.
