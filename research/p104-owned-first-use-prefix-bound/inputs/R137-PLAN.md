# Round 137 · reconstruct one owned MOVE at the first actual use

Exact #7334 aaeec8c0acf01e99a5f331ef363a698d9c084ace and signed #7113 07a76c5e2738882c0cb322278e56f6cae3c9885d. On one of the exact 47 paid owned MOVEs, clear the existing field in its old chart at the MOVE clock and defer fresh INIT in its destination chart to immediately before the first literal later ADD or SCALE involving that field. Rebuild its old arbitrary-input row from any then-live unchanged cocharted public or owned donors, which are read-only. The mover's normalized row is unchanged before its first actual contact. A first MOVE/INIT/CLEAR/COPY is a barrier, outside this scope. All other original paths and field values stay fixed. #7308 excludes immediate reconstruction on #7277, R64 tests one constant donor for an entire lifetime, and R80 tests opposite turns.

Freeze exact per-rank deletion prices across all 17 copies before decoding. For one rank-r MOVE, P_r−17, T unchanged, paid 110,502, productive 22,461, surplus 1,424+17r. The whole optimistic bound charges every one of 47 MOVE deletions once, with no composition asserted. Every re-INIT, owner erasure, source ADD, destination chart routing, phase, restoration, precision and tape cost must fit the original admitted contract. An unchanged live donor can be used only if actual compiler ownership and coframe semantics allow the exact read.

Scan all 76,466 events, cap 47 MOVE keys and 35 runner seconds. Rebuild exact occupancy and first contact. Compare the old owned row to the full live destination bank using exact rational arithmetic. Preserve excluded, outside-scope and capped keys separately. A survivor must first provide at most 16 signed legal ADDs from unchanged sources and prove compiler-valid lifetime, all widths and restored arbitrary-input/adjoint action. At most one positive-price literal prototype, initial cap 120 seconds, then full independent native/caller/outer replay. Exact rational feasibility alone is provisional.

From this root with CPython 3.12 and assertions:

```sh
python3.12 -I -B lead/first_use.py --price-only > fresh-price.json
cmp lead/PRICE.json fresh-price.json
python3.12 -I -B lead/first_use.py > fresh-result.json
cmp lead/RESULT.json fresh-result.json
```
