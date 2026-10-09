# Discovery (not run by verify.py)

`flow_frames.py` runs this package's descent (`harness.descend`: `physical_opt.py` endpoint moves of single
operations, `bundles.py` equal-frame components, `joint.py`/`deep.py` connected bundles, `pairs_mw.py` reuse
pairing; PR #200's physical layer code) on the source-aligned cache of PR #194's pipeline, writes the resulting
frames and pairs into a copy of the aligned tree and prices them with PR #184's `complex_frame_flow.py`:

    SA_TREE=<PR202 tree> SA_PY=<python with numpy/scipy> python3 -B flow_frames.py --aligned <aligned tree> --seed-frames --keep out/

With `--seed-frames` the descent starts from PR #168's physical frames (the aligned tree's own layer) and the flow
root rises from 7.00918e-4 to 7.08613e-4; without seeding, 7.0691e-4; the light descent alone, 7.0419e-4. These
numbers are float discovery screens; the certified value is in `../certificate.json`. `matching.py` and
`extend.py` are needed only to import `harness` (the matching itself is PR #168's frozen one here).
Prepared by Chafik Boukhalfa with Anthropic Claude and OpenAI Codex assistance; Apache-2.0.
