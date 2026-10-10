# Discovery

Not executed by verify.py. Run on the g5q10alt word after #287's descent and target stages (re-derived on this word).
* twin-census.txt: twin census on the post-target word (alt272/scripts/gen4_census2.py).
* coll/: collective census (load.py -> helpers.pkl, families.py -> families.json [numpy], pack.py -> selA.selection.json); outputs families-alt.txt, selA.txt, selA.json.
* build_selection.py PACKED [OUT]: freezes kernel-selection.json bound to the fresh post-target word.
* build_restore_selection.py: freezes restore-selection.json (PR280 screen on the fresh kernel word).
* build_sink_selection.py: freezes sink-selection.json (PR283 sink screen on the fresh restored word).
* generate_pins.py OUT: records expected/kernel-pins.json from a fresh replay.
* make_manifest.py: rewrites MANIFEST.json.
