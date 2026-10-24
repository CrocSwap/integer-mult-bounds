# Publication checks and source records

The independent package review covers the original 29-file package.
Its manifest is `REVIEWED-PACKAGE-HASHES.json`. The publication copy
changes the README review-status paragraph and adds two open next
questions. The other 28 original files are unchanged.
The five main executable files and all mathematical input files are
unchanged.

`PACKAGE-REVIEW.md` and `PACKAGE-REVIEW.json` retain the accepted review
bytes. `COLD-REPLAY.json`, `INDEPENDENT-ALGEBRA.json`,
`NEGATIVE-WITNESSES.json`, and `PINS-AND-INVOICE.json` retain its checks.
`PAIR-CHECKS.json`, `NATIVE-CHECKS.json`, `ALGEBRA-CHECKS.json`, and
`REPLAY.json` are the exact producer outputs. The coordinator and the
independent cold run reproduced all four output hashes.

The two supplementary Python scripts accept explicit paths in this
copy. Only argument parsing and input/output paths changed. Their
mathematical code is unchanged. The source hashes and complete small
diffs are in `PUBLICATION-PROVENANCE.json`. Their outputs must match
the retained independent receipts byte for byte.
`SUPPLEMENTAL-IO-REVIEW.json` accepts these path changes after a separate
exact replay. `SUPPLEMENTAL-IO-ADAPTATION.json` retains the reviewed diff.

From the repository root, create an external output directory and run:

```sh
mkdir -p /tmp/original-paired-gap-supplements
python3 -I -O -B research/original-paired-gap/evidence/independent_algebra.py --out /tmp/original-paired-gap-supplements/INDEPENDENT-ALGEBRA.json
python3 -I -O -B research/original-paired-gap/evidence/check_negative_witnesses.py --package research/original-paired-gap --repo . --out /tmp/original-paired-gap-supplements/NEGATIVE-WITNESSES.json
cmp research/original-paired-gap/evidence/INDEPENDENT-ALGEBRA.json /tmp/original-paired-gap-supplements/INDEPENDENT-ALGEBRA.json
cmp research/original-paired-gap/evidence/NEGATIVE-WITNESSES.json /tmp/original-paired-gap-supplements/NEGATIVE-WITNESSES.json
```

The main replay command is in the package README. It uses the unchanged
five executable files. `WORKTREE-REPLAY.json` records that command and
the exact four output comparisons from the publication worktree.

`COLD-REVIEW-SOURCE.txt` preserves the independent cold-run driver byte
for byte. It records historical machine paths and is archival source.
It is not a runtime input. The same applies to the machine paths in
historical cold receipts and the source-campaign paths in owner evidence.
The original review JSON pins the original script filenames and hashes;
the publication record gives their new paths and the two I/O changes.

The package review did not rerun the separate owner schedule or a global
supplier. This publication check does not add such a claim. Global
closure, a complete recursive invoice, and a kappa improvement remain
unproved by this package.
