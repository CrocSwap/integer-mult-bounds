# Literal recursive descriptor production at fixed width

This scoped physical implementation advances the one-edge PR6719 shape
bridge: every live child now generates its own grandchildren's descriptors
on the actual suspended path. A single literal finite table controls the
whole recursion. It uses no runtime host multiplication/division, decoded
descriptor, callback, host recursion or per-depth tape allocation.

The actual stopped-recursion source keeps w fixed. The machine therefore
generates H=q^(N²(w−1)) once from the physical root width and preserves it
through all nodes. It does not invent a changing-width domain. Current A/R
headers, generated grants, guides and return fields have real physical frame
lifetimes. Every output is protected before pop.

For L=4,q=3,N=1 the table has 20,897 instructions and 25 fixed tapes,
independent of width and depth. The actual two-level case w=2,D=3 executes

    (A,R,V)=(144,3,1728) -> (12,9,432) -> (1,27,108)

with seven node entries and six complete physical returns. The same table
also executes w=1 and w=3. A deliberately stale H wire passes one edge but
fails on actual grandchildren; missing output protection and depth restoration
also fail. All original source/header bytes remain unwritten, and every
owned grant, guide, relay, phase/control region and generated H is retired.

`PROOF.md` gives the all-depth contract, source address induction and complete
occurrence-sum time/active-chain space bill. `CONTRACT.md` records the scope
chosen before implementation. `TABLE.json.gz` is the exact emitted literal
table, compared to the compiler before fixture execution. `RESULT.json`
contains actual microtransition, return, grant and backing observations.

Run with Python 3.12, standard library only:

```sh
python3.12 -I -B check.py
python3.12 -I -O -B check.py
```

Default execution is read-only, Git-free and HERE-relative. `--write` is
explicit authoring mode. The sources are exact committed PR6719 inputs at
`3bad39ffd4faf7e8cb1bc5b47769cbb28511f797`; no historical suite or native
Gaussian replay is called. The generic counter, stack, codec, shape arithmetic
and whole-high address theorem retain their predecessor credit.

## Remaining production boundary

The literal leaf complements bits; it is not an ordinary BIT or Gaussian
supplier. Root w/depth production from an external integer input, numerical
ancestor weight descriptors, final-template matcher/fallback macros, stock
and precision remain separate interfaces. The shape headers do not determine
those numerical weights. No new paid invoice, kappa, selected result, final
production theorem or scientific admission is claimed.

The useful next gate is an independent static review of the emitted codec,
CALL/RETURN and all-depth bounds, followed by binding one actual final-template
leaf/control descriptor to this already literal recursive skeleton. There are
no official repository edits in this workbench.

Prepared for thu-nmrc with substantial OpenAI Codex assistance, Apache-2.0.
