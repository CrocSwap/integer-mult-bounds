# Re-pinning the package for new module data

These steps install a new `pm_p10.json` or `qmod_p10.json` (or a new local design or cube orientation) and re-pin
the package. They are tools, not part of the proof: the result is accepted only by a fresh strict `verify.py` run.
This package's word was installed this way on #315's package.

Run all commands from the package root, with Python 3.11+ and sympy 1.14.0. Every `--work`, `--emit` and
`--output` directory must be new and outside the package.

1. **Install the data.** Copy the new files into `bitword/producer/data/` under the same names. The cube
   orientation `cube_orient_p10.json` is optional: without it the generator uses sorted cubes.
2. **Build the word.**

   ```sh
   python3 -B bitword/producer/regenerate.py --work W1 --solve-matching --emit E
   ```

   This runs on a scratch copy of `bitword/producer`. It recomputes the carrier matching and freezes it, then
   compiles on the frozen arcs, so frame ids follow the frozen arc order. It then runs `make_physical.py
   --bank-parity` (tiered maximum reuse matching) and `descent.py`.

   The log prints any `bank divisibility: dropped pair` lines. Pairs are dropped only when 60·width is not a
   multiple of m = 100; record the dropped pairs in `bitword/README.md` and `BANK-PROOF.md`. (For this
   package's word the log printed none.)
3. **Install the word.** Copy `E/selected/*` to `bitword/selected/bit/` and `E/arcs_p10.json` to
   `bitword/producer/data/`.
4. **Record the pins.**

   ```sh
   python3 -B discovery/repin.py --output R1           # dry run: prints every pin that changes
   python3 -B discovery/repin.py --output R2 --write   # writes word-pins.json and MANIFEST.json
   ```

   This runs `verify.replay()` with `word_pins.RECORD` switched on. Every structural assertion, control and exact
   certificate still runs and must pass, including the bank tiling, which needs no padding.
5. **Check the build.**

   ```sh
   python3 -B bitword/producer/regenerate.py --work W2
   python3 -B verify.py --output V
   ```

   The first command must report the byte-exact regeneration; the second must PASS under strict pins.
6. **Update the documents.** The numbers in `README.md`, `PROOF.md`, `BANK-PROOF.md`, `bitword/README.md` and
   `PR-STATEMENT.md` change with the word; every changed pin is printed in step 4. Then refresh the manifest and
   rerun the strict verification:

   ```sh
   python3 -B -c "import sys; sys.path.insert(0,'discovery'); import repin; print(repin.manifest(True))"
   python3 -B verify.py --output V2
   ```

Transplanting a different complex supplier is a separate operation. It replaces:

- the gcert, `source-pins.json` and provenance files in `inputs/complex/`;
- `code/complex_{labels,scalars,splice}.py`;
- the re-pinned literals of `portable_complex.py`;
- the `complex_supplier()` block of `math_check.py`, i.e. the profile pins and the fallback-inclusive and
  no-fallback roots.

Keep `code/complex_gx.py`, the vendored `inputs/complex/sources/tools__gx__gx.py` with its entry in
`source-pins.json`, and the program-check call in `portable_complex.py`. After a transplant, the dry run of step 4
must change only `kappa` and `binding`.

## This package

This package's stage selections were frozen with the builders in `discovery/README.md` and its pins recorded with
`repin.py --write`. Its complex supplier was transplanted as described above, from #327's p = 10 program; the
p = 11 literals of the five places were replaced by values derived from `word_pins.shape()` and strict `complex_*`
pins (`COMPLEX-P10.md`), so a later p = 10 complex program needs only a new certificate, its provenance files, the
`source-pins.json` certificate entry and a re-pin. The dry run then changes only the `complex_*` pins, `kappa` and
`binding`.
