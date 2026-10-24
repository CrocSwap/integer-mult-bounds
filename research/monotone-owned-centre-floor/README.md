# Monotone owned-center high-contact floor

Each of the eight owned high contacts in the actual round-three word must
have dimension at least eight under fixed main entrances, the fixed scalar
word and monotone persistent-field contact subspaces. This remains true after
discarding every native warp relation, freeing all helper boundaries and
freeing the other scalar contacts. The source attains all eight bounds.

Consequently, releasing only the high side of the centers while keeping the
other side at zero cannot reduce their paid rank mass below 64. The proof
does not give a global moment optimum or a higher kappa. The selected
conditional result at the base commit is kappa 0.00302015.

Read [PROOF.md](PROOF.md) for the mathematical argument, exact hypotheses,
source-contact table and limits. [WITNESSES.json](WITNESSES.json) contains
128 independent entrance-vector paths with 2,204 links, covering both actual
orientations and all eight owned lifetimes separately. Only fixed main
entrances supply seeds; no clean logical helper input is assumed.

Reproduce with standard Python 3.12 or later:

```sh
python3 -B scripts/research_package.py --package research/monotone-owned-centre-floor
python3 -I -B research/monotone-owned-centre-floor/verify.py
python3 -I -O -B research/monotone-owned-centre-floor/verify.py
```

The registered commands include the normal and optimized exact checks, the
complete source paid/helper baseline and 144 corruption, rank-seven-hyperplane
and warp-cut controls. `verify.py --write` regenerates the deterministic
witness artifact. Verification does not write it. This needs no solver,
network, imported predecessor executable or optional package.

Source: Cao Yifan / intqwq's round-three word, retained in
`research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz`, with compressed and
decompressed SHA256 bindings. The source manifest pins the base and exact live
input; all frozen predecessor bytes remain unchanged. Retain Cinna Davis's
native/controller/retiming lineage, Dugongue's transported-frame work, zxv,
Jacob Alan Sussman and the source's complete predecessor attribution.

This continues the owned-contact question from the
[bounded common-kernel prototype](https://github.com/1337isnot1337/integer-mult-bounds/tree/8052b4818738986960c5b243097b3fffb6d21139/research/owned-centre-kernel-retiming)
and [independent-contact claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4611#discussioncomment-19139586).
The former permits nonmonotone transitions and is not excluded by this proof.
The pending nearest-Clifford/split-contact work in
[discussion #5125](https://github.com/CrocSwap/integer-mult-bounds/discussions/5125)
also has a different boundary. Canonical investigation update:
[the scoped finding](https://github.com/CrocSwap/integer-mult-bounds/discussions/4611#discussioncomment-19143793).

Matarener's [PR5060 owned-wire floor](https://github.com/CrocSwap/integer-mult-bounds/pull/5060)
already proves a complete nested C-wire floor for the older #4470 word with
fixed native warps and helper boundaries, including variable low contacts.
Its interval-propagation/path argument is prior work. The present result
extends the high-contact part to the actual round-three word with every warp
relation removed and all helper boundaries free, using explicit paths seeded
only by main entrances. It does not extend PR5060's complete C-wire floor to
that larger domain. In particular, its open low-side/helper-boundary question
must not be reported as solved here.

Prepared by Cinna Davis / 1337isnot1337 with substantial OpenAI Codex
assistance; no subagents. Apache-2.0. Evidence is author-checked, not independent
human or proof-kernel acceptance. A package merge would not select a frontier.

## Open next questions

- Can changing both sides of an owned center job improve the complete moment?
  The high-side floor does not settle its relative rank. First reconstruct
  both owned macro itineraries with one variable low chart, charge all changed
  persistent bridges and the full center rank power, and gate the complete
  baseline before solving. Actual frame/phase, ownership, cleanup, precision
  and compiler/outer charges remain obligations.
- Can a changed scalar word or nonmonotone paid itinerary remove the forced
  entrance paths at a favorable total cost? Name the exact edit or descending
  bridge, emit both orientations, and reconstruct every paid/helper child.
  The present proof and the old floating common-kernel failure do not decide
  that question.

The structured questions, stopping rule and scope change are in
[TASK.json](TASK.json). No extra search is claimed by this package.
