# Validation record

Environment: CPython 3.12 on macOS, November 3, 2026 (UTC).

The complete direct generation run, the replays and the registered hook run
from the repository root:

```sh
python3.12 -I -B research/p104-helper-split-on-retirement-tree/verify.py --write-result
python3.12 -I -B research/p104-helper-split-on-retirement-tree/verify.py
python3.12 -I -O -B research/p104-helper-split-on-retirement-tree/verify.py
python3.12 -B scripts/research_package.py --package research/p104-helper-split-on-retirement-tree
```

Marker: `PASS_HELPER_SPLIT_KAPPA_00329760`. Normal and optimized replay both
exit 0 and print it from a fresh copy of the package. The registered hook
(`scripts/research_package.py`) is run from the repository root when the
package is placed there.

Coverage is that of PR6621, with the native layer replaced by the edited
word: full PR6529 regeneration compared with `BASEWORD.json.gz`, the edited
word's declared public boundaries, its 800 native columns, owned lifetimes,
helper maps and absolute phases, all 7,488 physical contacts, the PR6545
caller replay, both 1,225-coefficient caller engines, the dual pairs, the
exact complete invoice, both rational price engines, the compiler and all 58
outer predicates. Every retained source receipt is checked after its
scientific checks.

The two correction-drop controls and the injection controls run on the
edited word, and each must be rejected. Dropping the first event after the
raw construction is rejected by the row check ("All public and owned rows")
and dropping the final event by the exit check ("All public and owned
exits"), with the same messages as for the PR6621 word. The local profile checks compare the edited word with the
base word and require exactly the deltas in the verifier. The pricing check
requires 67,060 paid jobs and 13,774 productive fields.

Two verifier literals of the retained sources are changed, as declared in
README.md and PROOF.md: public registers 770 to 771 and owned peak 13 to 14.
The tail decay of the completion test is 33/34.

Not claimed: hosted CI, independent scientific review, the optional
full-history preflight, formal-kernel verification or a materialized
multiplier. All five source framework assumptions remain.
