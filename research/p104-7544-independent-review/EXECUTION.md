# Exact local execution evidence

All three required cold commands passed serially on CPython3.12.3 / NumPy1.26.4,
with assertions enabled and fresh per-command bytecode namespaces. The local
owning process guard executed the VERIFY.json stage commands with the additional
`-X pycache_prefix=<fresh namespace>` isolation also supplied by the repository
runner. Each command extracted/authenticated a fresh exact source export.
The generic registration metadata check passed separately; hosted execution of
the repository launcher is a separate exact-PR-head check.

|Command stage|Whole-command cap(s)|Observed wall(s)|Observed child CPU(s)|Exit|
|---|---:|---:|---:|---:|
|native|480|351.326288|351.313302|0|
|signed|495|402.072353|401.911734|0|
|audit|225|60.935767|60.837300|0|

Total observed wall: **814.334409s**, under
1200s of declared command caps. The measured maximum RSS662564KiB is the
cumulative RUSAGE_CHILDREN high-water, not a separately measured peak for each
stage. Successful child CPU readings are differenced between stages. Raw
stage logs and receipts are in evidence/.

Every stage emitted the identical source/receipt binding
`3e9e4b83f85d4bc1a59d7f846dbfe826db414b8d83dd1d2c94b1aa81167ce4bc`. All executable and mathematical inputs remained at INTEGRITY.json
SHA256`ab9014757ae0f11b54fa0b14793a9a3570c1b7d349a5b3b7092c6f11384281a9`.
The package metadata, explanatory prose and subsequent execution evidence are
separate from that executable/input integrity manifest.

Fresh native receipt SHA256:
`a78ac7cae08d8e22124a9321a68882b44a716e3fbe9d92055c27a22d9c71b14c`.
Frozen native receipt actually consumed by signed SHA256:
`a4ecb5d836b7c2cd466e9ffb512229198795b87b9697a241dd373b3e4bfe8804`.
Both native mathematical projections, removing only top-level timings, have
SHA256`552e709e845c88307b6024aa18c5fa3b7f74ac750c077de8b7d110a1af38cd07`.
The frozen bytes retain their historical provenance; they are not relabelled
as the fresh execution receipt. Full generated adapter hashes/replacement
records and actual FINAL consumed native/signed hashes are in the stage reports.

The complete signed/final command regenerated κ0.003647969120276,
110485paid/22461productive positions, surplus1424, zeroemptycredits,
ordinary782757964, precision2430,3039catalogue maps,104boundary pairs,
54strict+4functional outer predicates, and the retained ceiling.
The final cold audit exactly reproduced expected/REVIEW.json, including all74
pre-CLEAR rows, the five immediately restored observer targets, all2253001
public endpoint coefficients, exact grid37748736000 and scaled row mass
841374570120675/8192, all seven retained word corruptions plus COPY/grid/invoice
controls. These finite results leave the five framework premises unchanged.

## Preserved failures and earlier scoped evidence

The original unmodified source exact stage passed79.265910573s. The original
unmodified aggregate complete stage timed out595.004037849s. Its native kernel
passed371.000641060s and its full mathematical receipt matched expected;
signed was incomplete. That original run remains failed. Its timeout resource
reading excludes unreaped descendant work and is not total-tree CPU/RSS.

The first separate audit stopped46.816204126s on an overly strict uniqueness
selector after the all74boundary and dense checks and four corruptions passed.
The994instruction occurs twice. Source7542check.py uses list.remove(first);
the correction binds that same first occurrence40962 to its exactunique
three-event context. The failed code/log hashes and unrun obligations remain
in evidence/SELECTOR-FAILURE.json and the donor checkpoint.

The repaired pre-freeze audit passed56.630047460s/56.556623CPU/149204KiB under225s.
Its code/input manifesta812199313f4243f46c4edd7601641e2e9d7fa1e1dc7ceffa5eb862a94bbf393
and receipt are retained. The final cold audit also enforces that each of the
five observer target-after deltas is empty. No failed or component-only run
is counted as the completed three-command review.
