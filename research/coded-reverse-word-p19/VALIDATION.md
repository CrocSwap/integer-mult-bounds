# Validation

| Command | Result |
|---|---|
| `python3 -B research/coded-reverse-word-p19/p19_word.py` | PASS: 259 gate records, 77 recodings, listing replay equals the standard word on 0 of 229,376 entries at p=2 and 0 of 2,179,072 at p=19; writes `P19_WORD.json` |
| `python3 -B research/coded-reverse-word-p19/p19_claim.py` | PASS: code and prefix bounds, raw moment sign in two engines, charged tail ratios, compiler ranks, BIT admission, budgets, strict outer ledger, three rejection controls; writes `P19_CLAIM.json` |
| `python3 -B research/coded-reverse-word-p19/verify.py` | PASS: formal p=19 controller diagonalization and local pair, the word receipt and the claim receipt |
| `python3 -B research/coded-reverse-word-p19/full_p19_diagonalization.py` | PASS: p=19 std outputs `[(1,4)...(19,2)]`; coded same with denominators `[1,13]`; diagonalized True |
| `python3 -B scripts/research_package.py --package research/coded-reverse-word-p19 --check-only` | PASS_PACKAGE_METADATA_AND_PINS |
| `python3.12 -B scripts/research_package.py --package research/coded-reverse-word-p19` | registered replay; the runner requires the registered Python 3.12 |
| `python3 -B scripts/check_research_commit.py --package research/coded-reverse-word-p19 --check-source-history` | requires the bytes to be committed first |

The two long commands are the listing replay (about four minutes on a dense p=19
state) and the formal p=19 diagonalization. The fast verifier reads the two saved
receipts instead of re-running them. No command performs a git write.

Open premises carried by the claim: admission of the field-level bill under the
caller's fixed-tape/precision ABI, the inherited all-size/compiler, hosting, tape
and analytic interfaces, hosted CI and kernel review.
