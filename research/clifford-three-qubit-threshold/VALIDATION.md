# Validation and reproduction record

Date: 2026-11-04 UTC. Environment: Windows, CPython 3.12.2, standard library
only. Scientific base: canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
The canonical head was fetched again before publication; the fork's main
was already synchronized with it. This package was built in an isolated
worktree. No predecessor, selected certificate, or shared code was edited.

## Scientific replay

The following registered command passed, running both scientific checkers
in isolated Python mode, normally and with optimization:

```sh
python -B scripts/research_package.py --package research/clifford-three-qubit-threshold
```

Its terminal result was
`PASS_REGISTERED_RESEARCH_PACKAGE research/clifford-three-qubit-threshold outcome=completed`.
The primary result is `PASS_THREE_QUBIT_CLIFFORD_THRESHOLD_TEN`; the separate
checker returns `PASS_INDEPENDENT_CLIFFORD_THRESHOLD_TEN`.
[RESULT.json](RESULT.json) records the primary scientific output.

The primary checker authenticates four predecessor proof files, the published
table bytes, all character inner products, the complete quotient extraction,
odd-width phase controls, the width-nine defect, quadratic-form counts and
the rational spectral bounds. Its eight deliberately false controls reject.
It uses explicit exceptions, so optimization does not remove checks.

The independent checker imports no primary or predecessor executable. It
uses column orthogonality and a direct 67-class `Ad^5` average for width nine,
instead of the quotient-table and fixed-space calculation. It independently
acts on complete quadratic-form truth tables, checks 4,096 Pauli products
and 64 signed phase-gate conjugations, and rejects a corrupted transvection
character. One- and two-qubit form actions serve as smaller controls.
Both checkers nevertheless share the cited published character table.

Separate mathematical review is in [REVIEW.md](REVIEW.md), including exact
reviewed scientific hashes. Two separate agents checked the width-ten
reciprocity and transvection argument. These are AI-assisted reviews, not
independent human acceptance or proof-assistant verification.

## External data provenance

Both optional parsers matched all 4,489 entries of the retained table:

```sh
python -I -B research/clifford-three-qubit-threshold/extract_table.py /path/to/paper.html
python -I -B research/clifford-three-qubit-threshold/extract_tex.py /path/to/paper.tex
python -I -O -B research/clifford-three-qubit-threshold/extract_tex.py /path/to/paper.tex
```

The inputs were downloaded from the versioned HTML and source URLs in
[EXTERNAL.json](EXTERNAL.json). The original source download was a gzip
stream containing one TeX file. Recorded hashes distinguish the download,
decompressed TeX and HTML. The source articles are not bundled. These
optional checks need locally acquired article files; the scientific replay
needs no network.

## Selected result and overlap

The selected binding baseline returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`.
On this Windows checkout the ordinary path first encountered a long-path
limit. Invoking the unchanged baseline through an extended absolute path
resolved it:

```text
python -B \\?\C:\Users\rafag\AgentsCode\Research_integer-mult-bounds\.worktrees\theory-sprint-180\scripts\research_selected_baseline.py
```

That baseline authenticates selected bindings only. The selected PR6030
review and actual source manifest were read. The accepted
`kappa=781451/250000000` and all five framework assumptions are unchanged.
No selected cold replay was run or needed for this isolated algebra package.

[OVERLAP.json](OVERLAP.json) records the 09:06 UTC prepublication overlap
refresh: complete pagination of 664 open PRs and 6,789 discussion records,
plus the local inventory and targeted all-state PR searches. The explicit
three-qubit question in the retained PR5675/PR5967 lineage was open in that
coverage. Search coverage is bounded evidence, not proof of novelty; no
global literature-priority claim is made.

## Publication and Git-free replay

The following preflight checks the final committed package against the
working bytes and verifies that source-pin commits occur in its ancestry:

```sh
python -B scripts/check_research_commit.py --package research/clifford-three-qubit-threshold --check-source-history
```

For a portable source bundle, export the publication commit and its four
explicit inputs, then verify its manifest and hashes:

```sh
python -B scripts/export_research_package.py export --package research/clifford-three-qubit-threshold --ref HEAD --output /new/path/package.tar
python -B scripts/export_research_package.py check --check-inputs /new/path/package.tar
```

Extract that checked tar into an empty directory and run `verify.py` and
`independent_check.py` from the extracted `research/clifford-three-qubit-threshold`
directory with `python -I -B` and `python -I -O -B`. No `.git`, installed
dependency, dense tensor matrix, network or predecessor program is needed.
The PR records the publication commit and actual export/preflight results;
this avoids a self-referential commit hash inside the package.

## Limits and remaining obligations

The written proof establishes the all-width theorem using classical
representation theory and the cited character table. Exact finite arithmetic
supports its explicitly finite steps. We did not reconstruct the published
table from group multiplication, enumerate the full Clifford group, build a
dense Gram matrix, or run a proof assistant. Orthogonality alone would not
prove the external table's identification with the named group.

There is no physical caller, paid supplier improvement, universal compiler
claim, or multiplication-exponent improvement in this result. The threshold
is sharp; the stated conditioning constants are sufficient and nonoptimal.
The next mathematical and caller-binding questions are listed in README.md.
