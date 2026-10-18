# Exact owner-profile optimum for the PR741 supplier

**No new κ.** With PR741's native supplier, 72 complete calls and capacity inventory fixed, its idle profile `{48:2396, 44:1, 3:1, 1:1}` maximizes the complex moment root over every owner reassignment. Other maps with the same profile tie. Every different profile fails the moment at PR741's already admitted endpoint.

The certificate uses five integer helper-width prices, four capacity prices, and exact rational moment bounds. It needs no optimizer. It makes PR699's earlier packing-optimality claim independently checkable for the shared width inventory and the stronger PR741 word.

```bash
python3 -B research/sw4-owner-optimality/verify.py --out /tmp/sw4-owner-proof
python3 -B research/sw4-owner-optimality/independent_check.py --out /tmp/sw4-owner-proof/INDEPENDENT.json
python3 -B research/sw4-owner-optimality/controls.py --out /tmp/sw4-owner-proof/CONTROLS.json
```

Python 3.11+ and the standard library suffice. The first command requires a new output directory outside the package. All three commands also work with `-I -O`; admission checks use explicit exceptions. No generated output is written into the package.

The main proof excludes two exceptional profiles with a width-price inequality, then uses concavity and 13 strict moment inequalities to cover the remaining profiles. The independent checker enumerates width patterns by count vectors, uses a separate base-two interval engine, and runs an integer dynamic program over all 115,057 masses from zero through 115,056. It checks every possible count of rank-48 idle children. Eight mutations test widths, ownership, chronology, native billing, dual weights and endpoint hypotheses.

`PROOF.md` states the reduction. `SOURCES.json` pins every copied input and interval engine to PR741 commit `e516b1463606840a15f80aac1995d64ce0092e89`. The input checks recompute native widths and paid profiles and inspect all 36,288 literal owner roles for the abstract packing conditions. The complete native scalar, phase, controller and global-admission replay remains in PR741; this package does not rerun it.

This result excludes further gains from owner reassignment within the fixed whole-call capacity model. It does not constrain changed helper widths, local programs, provider mixtures, dispatch counts, capacity inventories, or a different hosting contract. It does not establish an unconditional multiplication theorem or κ = 1.
