# Reproduction commands

Use Python 3.10 or later and its standard library. Keep at least 3 GiB
free disk. Use a new output directory outside the annex. Run one process
at a time from the repository root:

```sh
python3 -I -B research/ordered-centre-interfaces/annexes/rank-completions/replay.py --out /tmp/ordered-rank-completions-review
```

Expected final output:

```text
PASS_ORDERED_RANK_COMPLETIONS_ANNEX
```

The runner executes both unchanged independent checkers in normal and
optimized Python. Each fresh receipt must equal its frozen bytes. No
Git, network, or producer compiler is used.

The actual review command, working directory, and environment are in
[COMMAND.json](COMMAND.json). The local copy path is in
[RUN-LOCATION.json](RUN-LOCATION.json). Those paths record this run;
they are not source dependencies. The review used a relocated copy with
all package files set to mode 0444 and PATH set to /nonexistent.

The source audit compared all 34 manifest entries against the original
campaign or parent-package path, its byte count, its SHA256, and any
listed decompressed SHA256. It saved [SOURCE-CHECK.json](SOURCE-CHECK.json).
The preservation audit compared the 194 package files and 28 review files
in [PRESERVATION-BASELINE.json](PRESERVATION-BASELINE.json) with their saved
hashes. It saved [PRESERVATION.json](PRESERVATION.json).
