# Preserve Git path identity in local overlap coverage

`find_overlap.py` could report complete local coverage after searching only one
of three distinct tracked notes. Its `git ls-tree -z` subprocess used text mode,
which converts both CR and CRLF to LF before the NUL-separated paths are parsed.
For package names `line\rbreak`, `line\nbreak` and `line\r\nbreak`, the old
inventory therefore counted one README instead of three. Supplying only the LF
note as searched evidence incorrectly set `complete_head_inventory` to `true`.

The repair captures Git output as bytes and decodes UTF-8 with `surrogateescape`
explicitly. NUL separation, raw path identity and non-UTF-8 names survive.
Diagnostics are decoded before checking the return code, preserving the existing
unknown-coverage warning on a failed Git command. Repository binding, file-mode
filtering, timeout and no-lazy-fetch policy are retained.

This is a tooling reliability result, not a mathematical result or a new kappa.
The counterexample is a constructed Git tree; no claim is made that current
research notes contain these particular filenames.

## Task and overlap

- Base and pre-submission canonical main:
  `a7638a4ce2a29947457ae8d6bf8cd70a234dfeac`, priority revision 8.
- Card: `portable-replay`; scope key `831cc1a3c8f9ff01b197`;
  selector nonce `bd69a8030a3b52bb30f357b20185e131`.
- Scope status: **changed** from the card's compressed-artifact example to an
  exact path-inventory comparison failure. The verifier-engineering expertise
  override followed the initial bit-mechanisms suggestions. Reliable overlap
  coverage is required by the contribution workflow before choosing research.
- Concrete question: does the local HEAD inventory preserve distinct CR, LF and
  CRLF Git names and leave unsearched notes visible? Success requires exact
  counts/paths and rejection of the false-complete example. Bound: one local
  inventory helper, Git-object fixtures and its existing consumer tests.
- Checked the start-here board, active Discussions and newest visible #1166
  handoffs before selection. The local offline overlap report explicitly lacked
  remote snapshots and omitted sparse notes. Targeted live all-state PR searches
  covered `local_coverage`, `carriage`, `overlap` in titles, and `find_overlap.py`
  with `newline`/`CRLF`; an open-PR search for `find_overlap.py` found five unrelated
  mathematical contributions. This is bounded overlap evidence, not an exhaustive
  novelty claim. Discussion search URLs were unavailable; no complete comment
  census or authenticated `gh` refresh is claimed.
- [#4419](https://github.com/CrocSwap/integer-mult-bounds/pull/4419), by lee-phys,
  introduced the local coverage contract and checkout fixtures. It tested LF
  names but not CR/CRLF collisions.
  [#5725](https://github.com/CrocSwap/integer-mult-bounds/pull/5725), by Ali Romman,
  excludes directory aliases. Those checks remain.
  [#6161](https://github.com/CrocSwap/integer-mult-bounds/pull/6161), by Nick Petalas,
  optimizes text matching, a separate scope. The existing invoice-output repair
  [#5973](https://github.com/CrocSwap/integer-mult-bounds/pull/5973) concerns emitted
  JSON bytes, not Git path decoding.

## Evidence and reproduction

Windows 11 build 26300, CPython 3.12.10, Git 2.56.0.windows.2. The seven new
tests use native `hash-object`, `mktree -z`, `commit-tree` and `update-ref`, with
no checkout of the unusual filenames and no remote access. They cover the
three-name collision, a false-complete negative control, exact positive coverage,
tabs/Unicode/non-UTF-8 names, the complete JSON CLI and Git failure handling.
Four of the first five tests fail on the original helper; the unchanged-byte
positive control passes. All seven pass after the repair, also under `-O`.

The existing working-tree fixture retains its LF filename on POSIX and uses a
space on Windows, where the OS rejects LF filenames. The new object fixtures
check all three newline forms on both platforms. Its missing-repository fixture
moves the owned `.git` directory within its temporary directory instead of trying
to delete read-only Windows object files. Search, sparse restore, deletion and
unknown-coverage assertions remain intact; no new skip is added.

```sh
python -W error -B tests/test_research_overlap_git_paths.py -v
python -I -O -W error -B tests/test_research_overlap_git_paths.py -v
python -W error -B -m unittest discover -s tests -p 'test_research_overlap_local.py' -v
python -I -O -W error -B tests/test_research_overlap_local.py -v
python -B scripts/research_selected_baseline.py
git diff --check
```

Additional normal-mode runs used `python -W error -B -m unittest discover -s tests
-p FILE -v` for `test_research_overlap_terms.py`, `test_research_git_root_binding.py`,
`test_research_local_aliases.py`, `test_research_overlap_cache.py`,
`test_research_overlap_closed.py`, `test_research_overlap_pagination.py` and
`test_research_onboarding.py`. Together with the two path suites, these exercise
83 tests; five existing symlink tests are skipped because this Windows account
cannot create symlinks. The selected baseline authenticates source bindings and
metadata only. Its initial sparse-input/Windows long-path failures were resolved
by materializing the declared inputs with `core.longpaths=true`.

POSIX execution, a complete remote overlap census, historical pinned-package
replays and a cold scientific replay are outside this validation. Frozen source
pins, selected certificates and the five framework assumptions are unchanged.

## Open next questions

Run both path suites on POSIX to independently exercise materialized LF names,
the CR/CRLF object fixtures and symlink controls. The first step is the four
test commands above; runtime here was under 30 seconds in total. A POSIX runner
is the remaining environment requirement. This repair does not make unsupported
Git filenames materializable on Windows or certify source content from a
coverage inventory.

Credit Douglas Colkitt's overlap tool, lee-phys's #4419, Ali Romman's path and
coverage repairs, Nick Petalas's matching work and the retained contributors.
Prepared for josecarlosgonzalezroque-design with substantial OpenAI Codex
assistance, one agent. Apache-2.0. Evidence is author-checked.
