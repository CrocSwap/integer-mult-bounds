# Vendored files

Every file below is an earlier independent checker by the author of this package (Sagar Thakrar / thakrarsagar),
Apache-2.0, prepared with substantial AI assistance (Claude Code, Anthropic). They are byte-for-byte copies of the
files integrated into main (`d8e0f83f00191df62174b641e9fff055c357f641`, package
`research/t74-2751-joint-twelve-audit/`, PR #2865, whose own `vendor/` carried the PR2315/PR2387/PR2804 copies).
`verify.py` checks each file's git blob id and SHA-256 and executes exactly the verified bytes as the module (no
import machinery, so no cached `.pyc` can stand in). No code of PR #3015, #2979, #3018 or of any PR they build on
is vendored, imported or executed.

| File | Module | Git blob | SHA-256 | Origin |
| --- | --- | --- | --- | --- |
| `pr2315/words_check.py` | `words_check` | `0b646b9d5583c75a78e0c2dd7e9cfffa02055058` | `b66414a39f5ac7b9cd32284027e13a550734901aca5f4457085a034689bc3ce6` | PR #2315 (merged), `research/t74-borrow43-independent-check/words_check.py`; this copy keeps the pinned bytes, whose docstring credit was corrected on main (see below) |
| `pr2387/fill_check80.py` | `fill_check80` | `557e0732bfe4c030436a11f5433143c10fa07821` | `1c4d30591969c6502605f239f40505261e99d025aa3b576a804332a6bc479b06` | PR #2387 (merged), `research/t74-80alias-owner-fill/fill_check80.py` |
| `pr2804/audit_common.py` | `audit_common` | `17c4064f01b110012b54c05e64bdee8ae498e0b2` | `7ced740252ac8d8a8c66ef3cc825008e0aacf080494d0e983fb322d7dcddbf42` | PR #2804 (merged), `research/t74-2530-source-partner-audit/audit_common.py` |
| `pr2804/check_accounting.py` | `check_accounting` | `e749057dd838b715d0630de618f32d66a38da931` | `fb6aef50da586f15cd60762edc074c20e300d65f1378a80160b3d4b840762548` | PR #2804, `.../check_accounting.py` (rigorous moment enclosure, 640-bit fixed point) |
| `pr2804/check_fill.py` | `check_fill` | `85d1f807c62e4ac3b5f5ec7a809333ca05d5a951` | `6abf2a574de50c71b46b502d322deab841cbaa0080e326262f346a96992878fb` | PR #2804, `.../check_fill.py` (own owner-fill rules R-a..R-e, windows, template) |
| `pr2804/check_words.py` | `check_words` | `451dbb82f147ef446a1819b1ed595b4bf5547583` | `5996e804fa006906abff63a982c272588a44c35dfc932fdf687ef98dd3e0905f` | PR #2804, `.../check_words.py` (extended parser, frame recount, replays, cleanup re-derivation) |
| `pr2865/audit_lib.py` | `audit_lib` | `e8e847cc89dae6bb4e90e2c3dbebc30f615b698f` | `e0cf84dd959d39e3f299c1e171753c29465fd5b4457561f4ab9ec0675d8e9dc1` | PR #2865 (merged), `research/t74-2751-joint-twelve-audit/audit_lib.py` (parse with initial corrections, own tracker, control bookkeeping) |

`pr2804/NOTICE.md` and `pr2865/NOTICE-2865-vendor.md` are the predecessor packages' own vendor notices, retained
verbatim for the credit chain.

## Predecessor credits

Carried over from the files' docstrings and the retained notices:

- `words_check.py`: PR2269 (Jeremy Kothe, jeremykothe2): the borrow43 package and words; PR2226 (Cinna Davis /
  1337isnot1337, with OpenAI Codex): anticipatory dirty borrowing, the alias rule, K_G reference changes and the
  free-operator replay idea; PR2260 (Dugongue); the T74 lineage PR1319/PR1297 (Rohan Arun) and PR1625 (mdumitrean);
  **icekylinx and Zhihao Chen (jacklightChen)** (two contributors): Clifford-frame normal forms and the local-word
  checker lineage. The pinned bytes of `words_check.py` and `fill_check80.py` still carry the conflated form
  "icekylinx (Zhihao Chen)" in their docstrings, which the maintainer corrected on main when integrating PR #2315;
  the correct attribution is the one here.
- `fill_check80.py`: PR2269 (Jeremy Kothe): the T74 template, windows, dispatch and owner-row format; PR2322
  (Vlado Vojdanovski): the private-namespace statement; PR2226 (Cinna Davis); the PR858 /
  complex-double-replica-owners hosting rules (Hao Yan); the T16 owner audit (Josie Elliston; icekylinx and Zhihao
  Chen (jacklightChen) checker lineage).
- `check_accounting.py`, `check_fill.py`, `check_words.py`, `audit_common.py` (PR #2804) and `audit_lib.py`
  (PR #2865): this contributor's own, built on the above and on the PR2462/PR2530/PR2733/PR2751 words they audited
  (tekuuu, jeremydiviney, mdumitrean, petalas and the retained lineage credited in those packages' READMEs).
