# Validation record

Final checks of the actual staged Git blobs completed **2026-10-13 05:20:43
UTC**, with all six targeted checks passing or rejecting as intended. The
post-staging section below records the final artifact hashes and LF-normalized
manifest. The earlier, broader validation remains recorded separately.

The initial full validation completed **2026-10-13 05:14:34 UTC**. That run began
at 05:10:13 UTC and took **260.823 seconds**. All **21 external QA cases**
had the expected outcome: 11 successful executions and 10 deliberate
rejections. No verifier, receipt, or pinned input in the checkout was edited
during this run.

This validates the package's independent reconstruction of the Gaussian
copy bound and its weighted inclusion-maximal-clique method ceiling. It
does not establish priority for the bound, produce a physical supplier, or
improve the selected multiplication constant. Concurrent work is discussed
in the README and proof.

## Environment and executed commands

- Python **3.12.15**, GCC 14.2.0 build; standard library only.
- Linux 6.18.33.2-microsoft-standard-WSL2, x86-64, glibc 2.41.
- Existing image:
  `python@sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1`.
- Docker flags: `--pull never --network none --read-only --cap-drop ALL
  --security-opt no-new-privileges --cpus 2 --memory 1g --pids-limit 64
  --tmpfs /tmp:rw,size=128m`.
- The checkout was mounted read-only at `/repo`. Only the external local QA
  output directory was mounted writable, at `/output`. Working directory:
  `/repo`. No dependency installation or network access occurred in the run.

The following commands were executed with absolute script paths:

```sh
python -I -B /repo/research/gaussian-e8-copy-bound/verify.py
python -I -B -O /repo/research/gaussian-e8-copy-bound/verify.py
python -I -B /repo/research/gaussian-e8-copy-bound/independent_check.py
python -I -B -O /repo/research/gaussian-e8-copy-bound/independent_check.py
python -I -B /repo/scripts/verify_selected_result.py
```

| Check | Seconds | Outcome |
| --- | ---: | --- |
| Primary, default | 22.750 | PASS; 8 internal negative controls |
| Primary, optimized Python | 21.750 | Same PASS |
| Independent, default | 4.407 | PASS; 10 internal negative controls |
| Independent, optimized Python | 4.377 | Same PASS |
| Selected-result integrity | 79.664 | PASS; selected witness unchanged |

Observed success lines:

```text
PASS_GAUSSIAN_E8_COPY_BOUND lower=40 upper=60 flats=2272 pairs=2582128 controls=8
PASS_INDEPENDENT_GAUSSIAN_COPY_BOUND lower=40 pairs=2582128 maximal_cliques=8704 controls=10
PASS selected record, exact kappa, original source inventory and proof supplement: 51110230636731/31250000000000000
```

The primary calculation uses real-coordinate subspaces and computes the
exact pairing-rank census. The independent implementation regenerates the
geometry and flats using Gaussian-integer arithmetic, cofactor normals,
and exact nonzero minors. It certifies the required rank lower bound for
each of the 2,582,128 flat pairs; it does not claim to reproduce the primary
rank histogram. Its 8,704 inclusion-maximal cliques also verify the method
ceiling. Both implementations check source hashes and deterministic
receipts, and neither imports predecessor code or the other verifier.

## Relocation, mutations, and regeneration

An external QA driver copied only this package and the seven files listed
in `SOURCES.json` into `/tmp/relocated`, preserving their relative paths.
Both default commands passed there before any mutation: primary **21.204 s**,
independent **3.933 s**. This minimal tree contains no Git checkout or other
repository source packages.

Each mutation below was made separately to that temporary tree and then
restored from the original bytes. The checkout remained read-only. Each
verifier returned a nonzero exit status with the indicated reason, rather
than merely failing later on an unrelated receipt comparison.

| Deliberate mutation | Primary rejection | Independent rejection |
| --- | --- | --- |
| Append bytes to the pinned extension-ring `REPORT.md` | `source hash mismatch` | `source pin mismatch` |
| Change the default receipt's claimed bound from 40 to 41 | `computed receipt differs from RESULTS.json` | `independent receipt differs from complete exact replay` |
| Remove the pinned `REPORT.md` | `FileNotFoundError` | `FileNotFoundError` |
| Change a manifest path to `../outside-pinned.txt` | `source path escapes repository` | `source path escape` |

For the last case, the outside file existed and its declared hash was
correct; both verifiers rejected the path itself. These tests invoked the
ordinary default command, so the receipt tests exercised the committed
default receipt paths rather than a special test-only comparison.

Both verifiers were then run with `--write` pointing to a new file under
`/tmp`. The generated receipts were **byte-identical** to `RESULTS.json`
and `INDEPENDENT.json`, respectively. Repeating each command with the same
output path produced `FileExistsError`, confirming exclusive creation.
Final default runs after restoration passed again: primary **21.091 s**,
independent **3.829 s**.

The internal controls cover mathematical failures as well as artifact
integrity. Examples include an orthogonal pair presented as a clique, an
incomplete flat, the unsupported denominator 191, a wrongly charged Gram
block, and decoder fitting violations. The independent controls additionally
exercise Gram normalization and symmetry, a dependent flat basis, receipt
corruption, and modified pinned bytes. These guards remain active under
optimized Python.

## Initial full-run bytes and scope

The following historical SHA-256 values were recorded before the initial
execution and confirmed unchanged afterward, together with all seven pinned
inputs. The manifest and receipt hashes changed in the later normalization
step; use the final hashes in the next section for the submitted artifacts.

| File | SHA-256 |
| --- | --- |
| `verify.py` | `dbdd82e853b5c19420d6f3d145342f48102edcbfbb6effa1e76a71d4e97032a1` |
| `independent_check.py` | `8704c9517c94809e91de407c79891cebb5b03cb2cfda8435153c92c7fee60cdf` |
| `RESULTS.json` | `d9195a37cba97e089a7bc5362c1a53dca47d1994e691a4f8bb57c44a8dfb84c3` |
| `INDEPENDENT.json` | `23fd1b11cef67de3f9896b896f911063914f8b1573b8358961da04bb8694964e` |
| `SOURCES.json` | `3656cd4cccebff87c30f10c5ecf05f61fe76961c8432f0dee9621bd1cfa556e3` |

The unchanged base is recorded in `SOURCES.json` as
`66849e1475c930fd7732b1a0067ffee7e1e95f60`. The selected-result integrity
check verifies its source inventory and proof bindings; it is not a fresh
execution of the selected supplier's full physical replay.

Neither stage executed `make verify`, the full selected-frontier cold
replay, or remote CI. It does not discharge the repository's inherited
compiler, realization, hosting, precision, tape, or analytic assumptions.
The two verification implementations were produced with substantial Codex
assistance; no independent human or proof-assistant review is claimed.

## Final staged-blob checks after LF normalization

Packaging detected that the initial `SOURCES.json` had CRLF line endings,
while Git normalized its staged contents to LF. The manifest was normalized
to LF in the working tree, and only the manifest-hash field in each receipt
was updated to
`cc694727a7f6b8705549918f2bb991be5968f37cbf73ae15df0642e30a7b7191`.
Both verifier scripts and all seven pinned inputs were unchanged. No
mathematical result or other receipt field changed.

To check the bytes that would actually be submitted, the package files and
seven pinned inputs were exported from the index using `git show :path`.
The exporter captured subprocess output as bytes and wrote bytes directly,
avoiding text-mode newline conversion. This produced a fresh minimal tree
containing 17 distinct files, mounted read-only at `/repo` in the same
digest-pinned container with the same restrictions. The writable QA output
directory was a separate sibling of the exported tree, so there was no
writable mount alias to the staged inputs.

The targeted run began **2026-10-13 05:19:24 UTC**, finished at **05:20:43
UTC**, and took **79.337 seconds**. The ordinary commands against this
export were:

```sh
python -I -B /repo/research/gaussian-e8-copy-bound/verify.py
python -I -B /repo/research/gaussian-e8-copy-bound/independent_check.py
```

Both produced the same success lines recorded above, including all 8 and
10 internal controls. A temporary copy under `/tmp/relocated` was then
used to change each default receipt's claimed bound to 41, invoke that
verifier's ordinary command, and restore the receipt bytes. Each rejected
the corrupted default receipt for the intended mismatch. Finally:

```sh
python -I -B /tmp/relocated/research/gaussian-e8-copy-bound/verify.py --write /tmp/staged-RESULTS.json
python -I -B /tmp/relocated/research/gaussian-e8-copy-bound/independent_check.py --write /tmp/staged-INDEPENDENT.json
```

Both generated files were byte-identical to their actual staged receipt
blobs, including the updated manifest digest.

| Staged-blob check | Seconds | Outcome |
| --- | ---: | --- |
| Primary default | 22.366 | PASS |
| Independent default | 4.167 | PASS |
| Primary altered default receipt | 21.387 | Intended receipt-mismatch rejection |
| Primary receipt regeneration | 22.771 | PASS; byte-identical |
| Independent altered default receipt | 4.213 | Intended receipt-mismatch rejection |
| Independent receipt regeneration | 3.878 | PASS; byte-identical |

Final tested SHA-256 values, unchanged throughout the staged-blob run:

| File | SHA-256 |
| --- | --- |
| `verify.py` | `dbdd82e853b5c19420d6f3d145342f48102edcbfbb6effa1e76a71d4e97032a1` |
| `independent_check.py` | `8704c9517c94809e91de407c79891cebb5b03cb2cfda8435153c92c7fee60cdf` |
| `RESULTS.json` | `3cbdaeddb56a7cc2a5a5743efcfa6621e1140f4d1bf74e8f15bdcc8c09b14d52` |
| `INDEPENDENT.json` | `05074c91e8578c31867081109e8efefedf2200db7c7e8a6b701c7165faa063a2` |
| `SOURCES.json` | `cc694727a7f6b8705549918f2bb991be5968f37cbf73ae15df0642e30a7b7191` |

The seven pinned input hashes also matched the initial stage. Optimized
Python, source/path mutation cases, and selected-result inventory validation
were not repeated in this targeted stage because their executing code and
pinned inputs were unchanged; their actual earlier results are recorded
above. No submitted script or receipt was modified by this final validation.
