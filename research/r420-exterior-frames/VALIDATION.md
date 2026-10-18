# Validation receipt

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Environment: Ubuntu 24.04 WSL, Python 3.12.3, standard library only for this
package. Validation performed 2026-10-13. No selected source or `upstream/`
file was changed. Python 3.10 grammar compatibility was checked, but that
interpreter was not run. A scoped workflow was drafted but omitted because
the available GitHub token lacks workflow-upload scope. No remote CI success
is claimed in this receipt.

Commands run from the repository root, all successful:

```sh
python3 -I -B -O research/r420-exterior-frames/verify.py
python3 -I -B -O research/r420-exterior-frames/ghost_screen.py
python3 -I -B -O -m unittest discover -s research/r420-exterior-frames -p 'test_*.py' -v
make selected-record-check
python3 -I -B research/e8-bit-r420/code/xcheck.py research/e8-bit-r420/data/bitE8mut-r420.json.gz --json /tmp/r420-original-xcheck.json
python3 -I -B research/e8-bit-carrier-skeleton/code/bit/export_records.py research/e8-bit-r420/data/bitE8mut-r420.json.gz /tmp/r420-exterior-reference-records
python3 -I -B research/e8-bit-carrier-skeleton/code/bit/checkers/gram_frames.py /tmp/r420-exterior-reference-records --gram e8ham --h 8 --positive
```

The package runs ten tests, eight direct mathematical rejecting controls, and
two failed-return controls. It matches every field of both committed exact
receipts. Alternate root order, exact small determinant/rank oracles,
recompression acceptance, corrupted-source/receipt rejection and no-overwrite
behavior pass. Both main checkers also pass from `/tmp` with `-I -B -O`.

The unchanged R420 checker passes all 660 symbolic columns and its H1–H5
interface decomposition. The unchanged Gram checker reports 672 positive,
nondegenerate frames, valid prime witnesses, and primes `[2]`. The selected
record remains `51110230636731/31250000000000000`. All 11 source SHA-256/Git
blob pins and both semantic hashes match the recorded base and local inputs.

Seven GPT-6 Astra subagents provided bounded AI-assisted review:

1. A separate Bareiss-minor/Fraction inverse-Gram calculation matched all 672
   blades, basis determinants, projectors, denominators and 80,640 residuals.
2. A dense 660-by-660 F2 implementation independently confirmed restoration
   debt rank 539, correct first target output, equal child profiles and all
   seven selected assembly iterates.
3. A z-only transvection product found source drift rank 120 and the helper
   251 counterexample; the fixed child/copy interface and full moment were read.
4. An overlap review inspected #737, #710 and #731 at the heads in README.md.
   The result is expressly narrowed and those concurrent authors credited.
5. A provenance/CI review checked pins, source notices, local links, action
   pins (for the subsequently omitted workflow), isolation, optimized execution
   and Python syntax compatibility.
6. An independent scalar-bit-list replay checked the literal two-call helper
   251 counterexample, every basis input's first target output, source drift
   ranks and the positive full-cleanup two-call control.
7. An exact-fraction review checked the complete moment, finite-overhead
   dependence, complex-bound ceiling and encoded-state obligations.

These additional implementations were scratch review tools, not dependencies
of the submitted checker; the ten-test package above is the durable replay.
No independent human review, full theorem formalization or new exponent is
claimed. The full repository suite, selected cold replay and Lean build were
not rerun: this package is an additive fixed-input audit and changes no
generator, supplier, assembly or selected record.
