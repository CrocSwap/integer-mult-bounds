# Validation and handoff

Base: `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`.
Branch: `research/jp8-clean-work-seed33`.
Local validation on 2026-10-13 used macOS and Python **3.11.17 / 3.15.0**.

The following completed successfully:

```sh
python3 -I -B research/jp8-clean-work/verify.py
python3 -I -O -B research/jp8-clean-work/verify.py
python3.11 -I -B research/jp8-clean-work/verify.py
python3 -I -B research/jp8-clean-work/test_package.py -v
python3.11 -I -B research/jp8-clean-work/test_package.py -v
make selected-record-check
git diff --cached --check
```

The two complete scalar orientations pass all 716 native plus nine arbitrary
private columns. The exact receipt reports 9,228 additional real-component
primitive savings per orientation, 15 rejection controls, 574 coefficient
identities and 13,728 integer/Fraction intermediate-state comparisons. Every
omission agrees with a separate backward census; every addition still ends
with zero coefficient work. The charged 192-bit allowance and paid profile
are retained. [EXPECTED.json](EXPECTED.json) contains the precise bills,
stream/witness digests, prefix bounds and per-phase savings.

All four package tests pass on both Python versions. They run an optimized
isolated subprocess, relocate only the nine declared input files plus this
package, recompress gzip containers with different headers/streams, and reject
an altered predecessor before import, a forged invoice and an unsound clean-state
assumption. No test failure or skipped case remains.

The incorporated #696 lowerer was additionally fetched from its declared source
commit `5a3f983715027c4fd83f50bc9001d4b18463bed1` through GitHub and compared
byte-for-byte. Its SHA256 is
`eb37d00063dc09323e9aca041d23da749ce17fbd71dade9aaf1c059cab0b9753`.

The final upstream fetch reached
`f567884aeb8851b6e794af1184119a3bfbe1e631`. Its selected record has advanced
to #799, conditional κ = `1661634653669567/10^18`; its construction/review was
read. All nine dependency pins of this historical JP8 contribution still agree
with that tree. The branch deliberately retains its exact original base.
The fresh open-PR snapshot and source inspection of #755 found no matching
known-zero unit-clear specialization; [OVERLAP.json](OVERLAP.json) records the
related work and limits of that inspection.

Repository-wide `make verify`, fresh native/global supplier regeneration, remote
Linux CI and Lean were not run for this isolated circuit package. It changes
neither an existing generator nor the selected construction. The native macro
stream and its admission remain inherited; this is a finite primitive-lowering
result and local invoice, not a refreshed global artifact binding or a full
formal multiplication proof.

The bounded experiment ended before verification began at approximately
06:47 UTC, leaving more than the final quarter of the actual session for
verification and submission. No delegated agents were used. Contributor and
substantial AI-assistance disclosures are in [README.md](README.md).
