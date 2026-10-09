# bit-frame-ceiling-200

A rigorous ceiling on the bit coarse saving, and hence on κ, for every operation-frame layout of #200's physical bit
word, the word shared by #200, #205, #206 and #207. **No new κ; no existing file changes.** The method is DaysSky's
#192 (`research/kappa-ceiling`), carried from #168's complex word to this bit word.

## Result

For every admissible choice of operation frames on this word (its DAG, operations, sources, gauges, 1,760 reuse pairs,
partner chronology and 34 sinks fixed, as in #200, #205, #206 and #207):

    bit coarse saving < 6.904e-4  under #200's own ledger,
    bit coarse saving < 6.964e-4  under the completed-entrance-bank ledger of #205/#206/#207,

and hence κ < 6.900e-4, respectively κ < 6.959e-4, for any assembly built on it. #207's bit side (coarse 6.8366e-4,
κ = 6.8319e-4) is 98.2% of its ceiling, so frame work on this word is worth at most +1.8% more. The ceiling sits
below the complex supplier those PRs use (7.009e-4), so that complex word can never become the binding branch on
this bit word. Going further needs a different bit word, a bank construction that removes other children, or a
different design. [PROOF.md](PROOF.md) has the statements, proofs and the full table.


## Verify

    python3 research/bit-frame-ceiling-200/ceiling.py --check        # stdlib only, about 2.5 minutes; -O is refused

The script rebuilds the eight pinned files of #200 it reads (frozen physical bit word, frames, partner chronology,
graph, profile, sinks, certificate and the retained PR168-v4 exact integer checker) in a temporary directory from
`baseline-pr200.tar.gz` after checking the archive's and every file's sha256 against `SOURCE.json`, whose hashes are
those of commit `a1175449`. Reviewers can confirm the pins with `git show a1175449:<path> | sha256sum`, or rebuild
the archive byte for byte with `git archive --format=tar a1175449 <paths> | gzip -n -9`. A tampered archive is
rejected. `--tree PATH` runs on a checkout of #200 instead. `--overrides FILE` prices another layout of the same
word, for instance #207's `frames/opframe-bases.json`, and checks it against the bounds and the floor.

Self-tests: #200's layout lies inside every derived frame bound; its slot chains reproduce #200's certified pre-sink
ledger child for child and the terminal substitution; every per-slot floor and every Lagrangian round lies below the
actual cost. All bounds use exact integers with rounded-down logarithms, so the printed ceilings are upper bounds.

## Files

- `ceiling.py`: the computation; `PROOF.md`: statements and proofs; `expected.json`: the results `--check` compares.
- `SOURCE.json`, `baseline-pr200.tar.gz`: the pinned inputs.
- `.github/workflows/bit-frame-ceiling.yml` runs `--check` on Python 3.11 and 3.14.
