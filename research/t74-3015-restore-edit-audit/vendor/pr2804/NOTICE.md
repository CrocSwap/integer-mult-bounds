# Reused modules (PR #2804)

The four files in this directory are this contributor's own checkers (Sagar Thakrar / thakrarsagar), Apache-2.0,
prepared with substantial AI assistance (Claude Code, Anthropic). They are byte-for-byte copies of the PR #2804
package `research/t74-2530-source-partner-audit/` at commit `feb727ba471b5dc3f057f867804aa70ae58b2e71` (fork branch
`research/t74-2530-source-partner-audit`), copied with `git show` and not modified. `verify.py` checks each file's git
blob id and SHA256 (table `VENDOR`) and executes exactly the verified bytes.

| File | Git blob | SHA256 |
| --- | --- | --- |
| `audit_common.py` | `17c4064f01b110012b54c05e64bdee8ae498e0b2` | `7ced740252ac8d8a8c66ef3cc825008e0aacf080494d0e983fb322d7dcddbf42` |
| `check_accounting.py` | `e749057dd838b715d0630de618f32d66a38da931` | `fb6aef50da586f15cd60762edc074c20e300d65f1378a80160b3d4b840762548` |
| `check_fill.py` | `85d1f807c62e4ac3b5f5ec7a809333ca05d5a951` | `6abf2a574de50c71b46b502d322deab841cbaa0080e326262f346a96992878fb` |
| `check_words.py` | `451dbb82f147ef446a1819b1ed595b4bf5547583` | `5996e804fa006906abff63a982c272588a44c35dfc932fdf687ef98dd3e0905f` |

What this package uses from them:

- `audit_common.py`: the failure type, the control counters, `git_env` (GIT_* redirection and config-injection
  variables removed, `GIT_NO_REPLACE_OBJECTS=1`, `GIT_NO_LAZY_FETCH=1`), `ensure_commits` (the only writing call:
  `--fetch` into `refs/audit/prN` with `--no-write-fetch-head`, `-c gc.auto=0 -c maintenance.auto=false`) and
  `PinnedInputs` (every PR file read with `git show <commit>:<path>` and checked against its git blob id and SHA256).
- `check_words.py`: `parse_ext` (A-phase warp items), `frame_recount` (literal climb chain and COPY paths),
  `a_warp_algebra`, `run_replay`, `rederive_cleanup`, `inserted_gate_label`, `label_formula`, `reject_stage` and
  `climb_split_mutant` (for a control). Its PR2530-specific constants are not used.
- `check_fill.py`: `template_structure`, `order_projection`, `block_windows`, `windows_agree`, `word_widths`,
  `check_rows` (rules R-a..R-e and the R-c recount) and `fc_row`. `check_rows` reads its helper count from the
  module-level `CLAIM['helpers']`; `audit_pricing.own_rows` sets that value to the recounted helper count (415) for
  the duration of each call and restores it afterwards. The file bytes are unchanged.
- `check_accounting.py`: `moment` (exact atanh logarithms and a 2^-640 fixed-point directed-rounding exponential),
  `accepts`, `rejects` and `dec`.

The credits of the PR #2804 package and of the vendored PR #2315 and PR #2387 checkers (see `../NOTICE.md`) apply.
No code of PR #2751, #2733, #2720, #2696, #2269, #2766 or #2767 is vendored, imported or executed by this package.
