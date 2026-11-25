# Independent CNF certificate for the Turyn profile obstruction

**Independent verification; no new κ.** This package corroborates the
single-profile eight-bit fitting obstruction in DominikScholz's [PR598](https://github.com/CrocSwap/integer-mult-bounds/pull/598),
using new integer geometry, a Boolean CNF encoding, and a locally checkable
contradiction certificate. It imports no predecessor Python code or NumPy.

The 24 actual ports have seven mutually adjacent anchors. With all anchor
constraints retained, the original 71 variable-to-variable edges reduce to
an **inclusion-minimal 57-edge core**. For every one of the 57 retained edges,
an explicit eight-bit fitting satisfies the core after that edge is deleted.
This does **not** show minimum edge count, minimum vertex count, or minimality
when anchor constraints may also be deleted.

An explicit nine-bit fitting satisfies the **original full 171-edge graph**.
Together with the eight-bit contradiction, this establishes that this exact
24-port graph has standard-dot binary fitting dimension nine. Cyclic block
permutations place a copy in each of the three profiles. It does not prove
that their dimensions add to 27 for arbitrary global nonlinear labels.

## Reproduce

Python 3.10 or later, standard library only, from the repository root:

```sh
python3 -I -O -B research/turyn-profile-cnf/verify.py
```

Expected marker: `PASS_TURYN_PROFILE_CNF`. The deterministic receipt is
compared with `EXPECTED.json`. Verification checks:

- 24 explicit norm-32 integer vectors in the two relevant Turyn shell
  families, using an independently constructed 12-row binary code
- All 276 unordered vector pairs, with graph edges defined by three
  nonzero exact integer block products
- Seven anchor-clique labels, 79 anchor-to-variable constraints, and all
  71 original variable-to-variable edges
- The reduced 118-variable, 1,837-clause CNF and its entire 85-node proof:
  1,042 justified unit deductions and 43 contradicted-clause leaves
- All 57 single-edge-deletion eight-bit fittings, one fully relaxed
  eight-bit fitting, and a nine-bit fitting for the original graph
- Seven corruption controls, including a missing proof branch, a wrong
  unit sign, changed coordinates, and applying the proof to a relaxed graph

The default checker does not rerun a SAT search. On the development machine
the complete check took about 0.25 seconds; this is a descriptive observation,
not a benchmark or speedup claim.

The new package's test suite also runs under optimized Python:

```sh
python3 -I -B research/turyn-profile-cnf/test_verify.py -v
python3 -I -O -B research/turyn-profile-cnf/test_verify.py -v
```

Eight test groups include all 512 two-variable CNFs, 512 seed-78
three-variable CNFs checked against exhaustive truth tables, two separately
implemented encodings, and rejection of the old proof after each core edge
deletion.

## Regenerate the evidence

```sh
python3 -I -B research/turyn-profile-cnf/build.py --reduce
```

The new producer constructs all 23,040 canonical integer ports independently
and compares the whole coordinate array's SHA-256 with the frozen predecessor
receipt. It then selects the exact original port indices, uses ordinary
Boolean DPLL to produce the proof, performs one seed-78 edge-deletion pass,
and emits all positive controls. It writes only this package's generated
JSON files. Generation took about 26 seconds in the recorded run.

The default verifier proves membership of the 24 explicit coordinates
directly; it does not reconstruct the entire array merely to recheck their
enumeration indices. The full-array hash comparison and index-to-coordinate
binding belong to the separately reproducible generation step. The finite
theorem depends on the explicit coordinates and edges, not their index names.

## Sources and scope

- Exact base: `91a2094f2e022930069e8cfdc810a3ea1b81cd09`
- PR598 incorporated head: `615ca6f06fdea0c50dbef733370c47349e25c555`
- Selected frontier at that base: PR799,
  conditional κ = `0.001661634653669567`; unchanged
- `SOURCES.json` pins the consumed predecessor fixtures and the reference
  code read for semantics. None of that code is imported or executed
- `CLAIM.json` records assignment seed 78, the three candidates, overlap
  checks and stopping rule. `PROOF.md` gives the complete reduction
- `WITNESS.json`, `CORE.cnf`, `PROOF.json`, and `CONTROLS.json` are the reviewable evidence;
  `BUILD.json` records the new producer's deterministic statistics

This contribution supplies exact, finite, computer-checked evidence. It is
not a Lean formalization or a proof of the full multiplication theorem. It
does not construct a supplier, improve the selected exponent, rule out an
arbitrary global 25-dimensional Turyn fit, or discharge the inherited
compiler, hosting, precision, tape, or analytic obligations.

All changes are confined to this directory. `upstream/`, selected records,
predecessor programs and global verification targets are unchanged. The
new focused checks were run; `make verify`, selected-supplier cold replay,
and Lean were **not** run. No external repository code was executed in
preparing this isolated contribution. See `NOTICE.md` for credits and the
substantial AI-assistance disclosure.
