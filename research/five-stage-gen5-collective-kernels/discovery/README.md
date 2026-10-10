# Compatible composition discovery

Not executed by verify.py. Preserve a copy of the parent PR290
`kernel-selection.json` outside the package as the PACKED argument.

1. `select_compatible.py` derives exactly the 65 PR289 gates disjoint from the
   frozen PR290 pivots and donors.
2. `build_selection.py PACKED` binds those same kernel entries to the actual
   retimed word, recomputing the histogram delta.
3. `generate_pins.py OUT` replays the stages and records expected counts.
4. `make_manifest.py` pins the resulting package.
5. Run the public immutable `verify.py` into a fresh external directory.

All search and recording are outside admission; public verification forbids
pin recording and requires the independent composition stage.

---

# Discovery

Not executed by verify.py.
* twin-census.log: twin census on the post-target gen5 word (alt272/scripts/gen4_census2.py).
* coll/: collective census (load.py -> helpers.pkl, families.py -> families34.json, pack.py -> selG5.selection.json); logs families34.log, selG5.log.
* build_selection.py PACKED [OUT]: freezes kernel-selection.json bound to the fresh post-target word.
* generate_pins.py OUT: records expected/kernel-pins.json from a fresh replay.
* make_manifest.py: rewrites MANIFEST.json.
