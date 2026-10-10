# Discovery

Not executed by verify.py.
* twin-census.txt: twin census on the post-target gen5 word (alt272/scripts/gen4_census2.py).
* coll/: collective census (load.py -> helpers.pkl, families.py -> families34.json, pack.py -> selG5.selection.json); logs families34.txt, selG5.txt.
* build_selection.py PACKED [OUT]: freezes kernel-selection.json bound to the fresh post-target word.
* generate_pins.py OUT: records expected/kernel-pins.json from a fresh replay.
* make_manifest.py: rewrites MANIFEST.json.
* build_restore_selection.py: freezes restore-selection.json (PR280 screen on the fresh kernel word).
* build_sink_selection.py: freezes sink-selection.json (PR283 sink screen on the fresh restored word).
