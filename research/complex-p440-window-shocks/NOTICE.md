# Attribution and license

New code, proof and certificates: Hanson Sun (@bbMisk), with substantial OpenAI
Codex assistance. Apache-2.0; see `LICENSE`. No independent human review is
asserted. The two checker implementations were written in the same assisted
session, using different response and linear-algebra methods.

`inputs/BASE-WORD.json.gz` is an unmodified copy of Rohan Arun's PR1297
`research/global-mixed-four-cold-kernels/gauge44-word.json.gz`, commit
`4abf710a7f0d2a46f522f3f13c15769d003f9495`, transported byte-identically through
Marius-Paul Dumitrean's PR1337 at
`abd7384d9a5e35048723512ae70d970909ffd522`. Both original and transported Git
blobs were checked. The source licenses and notices remain applicable.

The suffix-response method and the question follow PR1337's `census.py` and
README handoff. The new primary checker does not import predecessor code; the
separate checker derives every window response by direct forward pulse
execution and uses fraction-free integer ranks. Neither calls the PR1186
frame-pricing toolkit or makes a frame-admission claim.

Retained credit: Jeremy Kothe's PR1274 cold-kernel mechanism; Rohan Arun's
PR1286/1297 composition; Jeremy Diviney's PR1193 flow; Thomas DiFiore's PR1148;
chafreaky's PR1196; PR1195/1218 and the PR564/571/589/645 lineage. The original
PR1297 and PR1337 notices are preserved under `inputs/` without revision.
