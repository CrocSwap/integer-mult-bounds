# Discovery (not run by verify.py)

`flow_frames.py` runs this package's descent (`harness.descend`: `physical_opt.py` endpoint moves of single
operations, `bundles.py` equal-frame components, `joint.py`/`deep.py` connected bundles, `pairs_mw.py` reuse
pairing; PR #200's physical layer code) on the source-aligned cache of PR #194's pipeline, writes the resulting
frames and pairs into a copy of the aligned tree and prices them with PR #184's `complex_frame_flow.py`:

    SA_TREE=<PR202 tree> SA_PY=<python with numpy/scipy> python3 -B flow_frames.py --aligned <aligned tree> --seed-frames --keep out/

With `--seed-frames` the descent starts from PR #168's physical frames (the aligned tree's own layer). Float screens:
unseeded light 7.0419e-4, unseeded full 7.0691e-4, seeded full 7.08613e-4, seeded light (`--light`) 7.0950e-4,
seeded light with a movability mask (`DESCENT_LIGHT_ROUNDS=1 DESCENT_FREEZE_FRAC=0.98 DESCENT_SEED=8`, i.e. 98% of
the operations frozen; `physical_opt.py`) 7.09767e-4, the layer certified in `../certificate.json`. The flow prefers
layers close to PR #168's; the sweep over freeze fractions 0 to 0.98 is monotone. `matching.py` and
`extend.py` are needed only to import `harness` (the matching itself is PR #168's frozen one here).
Prepared by Chafik Boukhalfa with Anthropic Claude and OpenAI Codex assistance; Apache-2.0.
