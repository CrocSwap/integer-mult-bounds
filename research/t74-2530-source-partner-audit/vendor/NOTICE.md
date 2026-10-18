# Vendored files

Both files are earlier independent checkers by the author of this package (Sagar Thakrar / thakrarsagar),
Apache-2.0, prepared with substantial AI assistance (Claude Code, Anthropic). They are byte-for-byte copies,
used unchanged as libraries. `verify.py` checks each file's git blob id and SHA256 before loading it.
No code of PR #2530, #2462, #2435, #2269 or #2474 is vendored, imported or executed.

| File | Git blob | SHA256 | Origin |
| --- | --- | --- | --- |
| `pr2315/words_check.py` | `0b646b9d5583c75a78e0c2dd7e9cfffa02055058` | `b66414a39f5ac7b9cd32284027e13a550734901aca5f4457085a034689bc3ce6` | PR #2315, `research/t74-borrow43-independent-check/words_check.py` (fork branch `research/t74-borrow43-independent-check`, commit `4a2f20ea339e30348448096ca789d0efe55df9bb`) |
| `pr2387/fill_check80.py` | `557e0732bfe4c030436a11f5433143c10fa07821` | `1c4d30591969c6502605f239f40505261e99d025aa3b576a804332a6bc479b06` | PR #2387, `research/t74-80alias-owner-fill/fill_check80.py` (fork branch `research/t74-80alias-owner-fill`, commit `20fb6953b0d2077c19e45f731ec587ebefb9a380`) |

Both were copied with `git show` from `fork/research/t74-2435-fill-independent-check`
(PR #2446, head `a3aabff9471dfdc3e85b065616e45a317f38882e`):

- `research/t74-2435-fill-independent-check/vendor/pr2315/words_check.py`
- `research/t74-2435-fill-independent-check/vendor/pr2387/fill_check80.py`

The blobs are identical to the originals listed above.

**PR #2315 on main.** PR #2315 was integrated into main on 2026-10-15 (commit `7981b35eb`). Main's
`research/t74-borrow43-independent-check/words_check.py` (blob `180b5deac3e0114dc068f9f04ac5034431d023e3`) differs
from the vendored copy only in one docstring credit line. The maintainer corrected "icekylinx (Zhihao Chen)" to
"icekylinx and Zhihao Chen (jacklightChen)"; the code is identical. The vendored bytes are kept as pinned.
`fill_check80.py`'s docstring has the same conflated form. They are two contributors; the credits below give the
correct attribution.

## Predecessor credits

These credits are carried over from the files' own docstrings.

- `words_check.py`:
  - PR2269 (jeremykothe2): the borrow43 package and words.
  - PR2226 (Cinna Davis / 1337isnot1337, with OpenAI Codex): anticipatory dirty borrowing, the alias rule,
    K_G reference changes and the free-operator replay idea.
  - PR2260 (Dugongue).
  - The T74 lineage: PR1319/PR1297 (Rohan Arun) and PR1625 (mdumitrean).
  - icekylinx and Zhihao Chen (jacklightChen): Clifford-frame normal forms and the local-word checker lineage, as
    corrected on main.
- `fill_check80.py`:
  - PR2269 (Jeremy Kothe): the T74 template, windows, dispatch and owner-row format.
  - PR2322 (Vlado Vojdanovski): the private-namespace statement.
  - PR2226 (Cinna Davis).
  - The PR858 / complex-double-replica-owners hosting rules (Hao Yan).
  - The T16 owner audit (Josie Elliston; icekylinx and Zhihao Chen (jacklightChen) checker lineage).
