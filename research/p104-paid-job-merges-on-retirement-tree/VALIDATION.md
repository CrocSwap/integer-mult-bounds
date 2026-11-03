# Validation record

Environment: CPython 3.12 on macOS, November 3, 2026 (UTC).

The complete direct generation run and the registered replay were run from
the repository root:

```sh
python3.12 -I -B research/p104-paid-job-merges-on-retirement-tree/verify.py --write-result
python3.12 -I -B research/p104-paid-job-merges-on-retirement-tree/verify.py
python3.12 -I -O -B research/p104-paid-job-merges-on-retirement-tree/verify.py
python3.12 -B scripts/research_package.py --package research/p104-paid-job-merges-on-retirement-tree
```

Marker: `PASS_PAID_JOB_MERGES_KAPPA_00329700`. Normal and optimized replay both
passed, as did the registered hook.

Coverage is that of PR6551, with the native layer replaced by the edited
word: full PR6529 regeneration compared with `BASEWORD.json.gz`, the edited
word's 799 native columns, owned lifetimes, helper maps and absolute phases,
all 7,488 physical contacts, the PR6545 caller replay, both 1,225-coefficient
caller engines, the dual pairs, the exact complete invoice, both rational
price engines, the compiler and all 58 outer predicates. Every retained
source receipt is checked after its scientific checks.

The two correction-drop controls and the injection controls run on the edited
word, and each must be rejected. The local profile checks compare the edited
word with the base word and require exactly the delta in README.md. The
pricing check requires 67,042 paid jobs and 13,756 productive fields.

Not claimed: hosted CI, independent scientific review, the optional
full-history preflight, formal-kernel verification or a materialized
multiplier. All five source framework assumptions remain.
