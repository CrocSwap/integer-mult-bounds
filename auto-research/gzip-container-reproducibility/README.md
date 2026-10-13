# Hashes of regenerated gzip containers: audit and convention

**No κ, no certificate change, no new mathematics.** This is a reproducibility audit of
one pattern in this repository, plus a convention and a scanner for it, prompted by an
observed failure and an independent replay.

## The pattern and why it breaks

A package writes a container with `gzip.compress(...)`, hashes the **compressed** bytes,
and requires that hash to equal a value committed or pinned when the container was
produced elsewhere. The deflate stream of a gzip container depends on the writing
interpreter's zlib build (and on block splitting), so the check can fail on unchanged
inputs and can hide a real change behind an environment difference.

Two observations in this repository establish the failure mode, from opposite directions:

1. **A check that fails on unchanged inputs.** #202's headline verifier,
   `research/source-assisted-v4/verify.py`, stops at line 162 with
   `AssertionError: Canonical certificate does not reproduce`. Exactly seven certificate
   leaves differ and all of them derive from one value: the sha256 of the compressed
   lift certificate, written by
   `research/source-assisted/decision/exact_complex_flow_lift.py:409`
   (`gzip.compress(encoded, compresslevel=9, mtime=0)`) and recorded at line 419 as
   `certificate_sha256=digest(cert_path)`, where `digest()` is a sha256 of the **file**
   (line 40-41). Every other leaf, including κ, the complex saving, the bit effective
   saving and the assembly records, is equal. The independent replay in PR #214
   reproduces this on CPython 3.13.16 with the pinned numpy 2.3.5 / scipy 1.17.0, and
   reports the same failure under CPython 3.12.3 for #194's own verifier, whose lift
   inputs are unchanged between the two commits. #194's CI passed the same check under
   the same interpreter and package versions.
2. **A rebuild instruction that does not reproduce.** PR #212 documents its pinned
   archive as byte-for-byte rebuildable with
   `git archive --format=tar a1175449 <paths> | gzip -n -9`. The **tar payload** is byte
   identical to the commit (verified), but the shipped container is not: it hashes
   `316aa694…` at 1,405,363 bytes, while a rebuild here gives `cb71d72d…` at 1,404,558
   bytes, and no zlib level 1-9 reproduces the shipped length. The archive's own file
   hashes are still checked by `ceiling.py`, so no number changes.

## What the repository already does correctly

The right shape is not new here, and it is used in more than one place:

* **Compare the payload.** The regeneration check in `paired_cube_bit_word.py` (present at
  #194's head and carried into the packages that inherit it) carries the reason in a
  comment:
  ```python
  if name.endswith('.gz'):  # gzip bytes depend on the zlib build; compare the compressed content
      old, data = gzip.decompress(old), gzip.decompress(data)
  require(old == data, 'byte-identical regeneration of ' + name)
  ```
  and #194's `bit/prove.py` does the same (`assert record == json.loads(gzip.decompress(target.read_bytes())), 'Exact prime witnesses changed'`).
* **Pin payload hashes or semantic fields.** #217's `expected-bit.json` pins the payload
  hashes of `graph_p12.json`, `word_p12.json` and `frames_p12.json` (its `emitted_sha256`),
  and `run_bit.py` records `prime_canonical_sha256 = sha256(witness_bytes)` next to the
  container digest. #207's `verify_inner.py:23` and `29-30` check
  `exact_scalar_program_sha256` and the complex profile's mathematical fields instead of
  a container.
* **Pin committed containers.** Pinning the sha256 of a `.gz` file that is committed is
  safe: those bytes are fixed in the repository and no check regenerates them. That is
  what `research/aligned-final-pricing-result/SOURCE.json:12-21` and the vendored
  upstream `SOURCE.json` files do.
* **Record both, and require only the payload.** `research/pair-assembly/frame/frame_compile.py:41-49`,
  inherited by #194, #202, #207, #212 and #216, writes `frame-word-{h}.json.gz` and records
  `gzip_sha256=sha256(path.read_bytes())` next to `word_sha256=sha256(raw)`; #217's
  `run_bit.py:151` records `prime_witness_sha256` next to `prime_canonical_sha256`. Both
  make the payload the canonical value; PR #207/#210/#216's
  `chart_witness_sha256=hashlib.sha256((HERE/'pr200-gauge-charts.json.gz').read_bytes())`
  and #194/#202's `certificate_sha256=digest(cert_path)` record a container digest alone.
  Recorded-only digests do not fail in the runs we read, but a future comparison could
  mistake one for a canonical check.

## Scanner

`gzip_hash_audit.py` is a heuristic reader that locates the pattern and prints the
evidence. It is not a proof of absence: it flags a file when it hashes a container path,
separates files that also decompress, and reports comparisons it can see in the same
file. Cross-file comparisons (a digest recorded in one file and required in another, as
in observation 1) must be read by hand, which is why the two observations above are
stated as chains of file and line rather than as scanner output.

```sh
python3 research/gzip-container-reproducibility/gzip_hash_audit.py <checkout>
```

Findings from a run on the exact heads, each checked out as a full tree
(`git worktree add --detach <dir> <head>`), on 2026-10-09. "Risky" is the scanner's
`RISK` class: a file that writes a container and records a digest of it.

| Head | `.py` files | `RISK` | flagged |
|---|---:|---:|---|
| this repository's `main` `3b6b668` | 639 | 3 | `research/pair-assembly/frame/frame_compile.py:48`, `research/machine-transfer-verification/stream-transfer/experiments/balanced_split.py:64`, `scripts/experiments/probe_pair_ranked.py:41` |
| #194 `a8c8778` | 578 | 3 | those three, with `frame_compile.py` inherited, plus `research/source-assisted/decision/exact_complex_flow_lift.py:419` |
| #202 `8d8d67b` | 605 | 3 | the same three; the `exact_complex_flow_lift.py` record is the one observation 1 follows |
| #207 `cd14825` | 650 | 4 | the merged tree's three plus `research/coordinated-crossover-pr200/geometry/audit-gauge-charts.py:50` |
| #212 `9b6ad03` | 640 | 3 | the merged tree's three |
| #216 `34abdc5` | 660 | 5 | the merged tree's three plus `audit-gauge-charts.py:50` in `coordinated-crossover-pr200/` and in its vendored `coordinated-crossover-pr200-v2/baseline/` |
| #217 `b739fc2` | 654 | 3 | the merged tree's three; its `run_bit.py:151` records the container digest *and* the payload digest, and the scanner does not flag it |

Three files are flagged at every head, and they read differently once opened:

* `frame_compile.py:41-49` writes `frame-word-{h}.json.gz` and records
  `gzip_sha256=sha256(path.read_bytes())` next to `word_sha256=sha256(raw)`. The payload
  digest is the canonical one; the container digest is a record. It has observation 1's
  shape only if a later check regenerates that container and requires the recorded value,
  which is what the `#202` chain does for a different file, and what nothing does for this
  one in the trees scanned here.
* `balanced_split.py:64` records `gzip_sha256` of the container it writes, and
  `stream-transfer/experiments/verify_balanced_split.py:67` — run with
  `--candidate <dir>` — asserts `digest(word) == meta['gzip_sha256']` against the receipt
  in that directory. Both files travel together out of the same run, so this is a pinned
  container in the sense of the convention below; it becomes observation 1 if a harness
  regenerates the container from the candidate's inputs while keeping the receipt. It is
  the one place in the merged tree where a container digest is *required* against a stored
  value, so it is the first thing to check if the pattern bites again.
* `probe_pair_ranked.py:41` records `profile_sha256=sha256(path.read_bytes())` for a file
  it writes, into its own `screen.json`. The merged tree only pins the script's own digest
  (`research/coordinated-frames-and-entrance-banks/SOURCE.json`) and points at it from a
  review note; no reader of the recorded value appears in the trees scanned here.

`audit-gauge-charts.py:50` (`#207`, `#216`) records `chart_witness_sha256` of a
regenerated `.gz` in a committed audit JSON. We found no run that requires it; it is a
record of the environment in which the chart was produced, which is what the convention
below asks such a record to say.

## Convention

1. **A check must compare payloads, not containers.** Decompress before comparing, or
   compare a deterministic uncompressed serialization. `#194`'s
   `gzip.decompress`-then-`require` is the precedent to copy.
2. **A pin should name a payload or a semantic field.** Pin the payload's sha256, or the
   mathematical fields, or the interpreter-independent values (as #207's
   `exact_scalar_program_sha256` and #217's `emitted_sha256` do). Pinning the sha256 of a
   **committed** container stays fine.
3. **A container digest may be recorded, but only as an environment receipt.** If a
   submission keeps one, it should say so, record the interpreter and zlib versions
   beside it, and never require it to match across environments - otherwise an
   environment difference is indistinguishable from a changed input.
4. **Prefer the payload check when a canonical check fails this way.** Re-point the check
   at semantic fields (the fix #207 already implements for #202's supplier), rather than
   regenerating the container in the reference environment, which leaves the same fault
   for the next reader.

`CONTRIBUTING-note.md` carries the same rule as a paragraph written for
`CONTRIBUTING.md`, after the paragraph that asks contributors to include regenerated
certificates. Placing it there is the maintainers' call.

## Scope and credits

This note audits a pattern, not any author's mathematics; nothing here contradicts a
submitted number or a verifier that passes. Observation 1 is PR #214's diagnosis,
reproduced here by reading the cited lines; observation 2 is from the audit of PR #212.
The convention follows the practice already present in #194, #207 and #217. Scanner and
note prepared with Anthropic Claude assistance; Apache-2.0.
