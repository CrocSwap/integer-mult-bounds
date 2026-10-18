# Validation record

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. macOS 26.5.2 arm64.
No source outside this research package is modified.

## Completed mathematical checks

- Primary exact replay on CPython 3.14.4: PASS (about 8 seconds).
- Isolated optimized replay (`-I -O -B`): PASS; checks use explicit exceptions.
- Independent arithmetic checker: PASS on all 298,378 primal inequalities
  using modular rank lower witnesses, 772 flat ranks using Fraction column
  elimination, and 241 exact tight pair ranks. Neither checker module is
  imported by the arithmetic implementation. Enumeration completeness and
  the all-width argument remain the main replay and written proof's scope.
- The exact geometric domain is 772 flats, 30,880 line extensions, 2,970
  maximal cliques (2,880 of size seven and 90 of size four), and 298,378
  unordered flat pairs including empty supports. No numerical tolerances,
  incomplete solver search or unproved orbit-transitivity shortcut is used.
- The nonlinear control covers all 4,096 twelve-bit inputs and 303,104
  conditional transcripts; the unequal-width control covers 64 inputs
  and 192 transcripts. The excluded extra-side-information code is checked
  on all 128 inputs. All 12 mathematical rejection controls pass.
- `scripts/verify_selected_result.py`: PASS, selected record and source
  inventory unchanged at kappa 51110230636731/31250000000000000.

## Commands

Use Python 3.10+; the host's `/usr/bin/python3` is 3.9 and is not suitable.
The executed primary interpreter is `/opt/homebrew/bin/python3` (3.14.4).

```sh
/opt/homebrew/bin/python3 -B research/eisenstein-message-copy-bound/verify.py
/opt/homebrew/bin/python3 -I -O -B research/eisenstein-message-copy-bound/verify.py
/opt/homebrew/bin/python3 -B research/eisenstein-message-copy-bound/crosscheck.py
/opt/homebrew/bin/python3 -B research/eisenstein-message-copy-bound/test_package.py
/opt/homebrew/bin/python3 -B scripts/verify_selected_result.py
```

## Packaging and structured review

- Relocated minimal-input replay from an unrelated working directory with
  `-I -O -B`: PASS. Regenerated receipt bytes equal the committed receipt.
- Existing output preservation, altered-certificate rejection and altered
  source rejection: PASS; failed validation creates no output.
- CPython 3.12.13 isolated optimized primary and independent arithmetic
  replays: PASS. No Python installation or package dependency was added.
- Documentation links and staged whitespace: PASS.
- Structured autoreview: PASS, no accepted/actionable findings. It checked
  the proof, exact arithmetic, enumeration, controls, source pins and output
  handling. It was read-only and did not run tests; the executed checks above
  are separate evidence. The configured Codex engine/model was retained.
  The shell CLI was too old, so the helper used the already-installed app
  CLI (0.162.0-alpha.17.2); no software or settings were changed.

No hosted CI or independent human review is claimed.

The unchanged expensive `make verify` and `make frontier626-verify` suites
are not run: no generator, supplier, assembly, shared verifier, selected
certificate or upstream file changes. This package's affected checks run
locally, including the selected-record integrity check. Finite checks do
not prove the full multiplication theorem.

## Upstream refresh

During closeout, origin/main advanced from the recorded base to
`7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`. The fetched selected
record now names PR741, kappa 1661202643272239/1000000000000000000, with
`make frontier741-verify`. The new selected review was read. This note stays
on its exact starting base; it neither assumes an open-title frontier nor
changes the accepted record. All three pinned base-tree geometry sources
are byte-unchanged across that range. New PR801 concerns conditional format
ceilings and coordinate-total costs; it does not cover the nonlinear
message/unequal-demand extension and is not a dependency here.

The successful review command was:

```sh
~/.codex/skills/autoreview/scripts/autoreview --mode local \
  --codex-bin /Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex \
  --prompt-file /tmp/imb-review-seed41.md \
  --json-output /tmp/imb-autoreview-seed41.json \
  --output /tmp/imb-autoreview-seed41.txt --stream-engine-output
```

The prompt restricted review to this package and emphasized the explicit
pricing assumption, exact coverage, attribution and controls. No findings
were accepted or rejected because the result contained none. Subsequent
changes only record completed validation, upstream status and the PR handoff.
