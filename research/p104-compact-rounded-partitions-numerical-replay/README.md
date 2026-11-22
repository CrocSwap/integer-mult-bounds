# Full-width compact numerical replay split

The previous hosted numerical job stopped at its 35-minute wall limit without a scientific verdict. This repair keeps the production sources and original `gaussian` replay byte-identical. It runs the two original full-width signed numerical witnesses and the unchanged phase census as three separate registered jobs. Each receives its own 600-second command cap. [Cancelled job](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/45077684057/job/137379564429)

| Signed copy | Columns | Owner positions | Paid cuts | Output axes | Nonzero cuts |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 6 | 52,608 | 282,576 | 4,480,128 | 16 |
| 1 | 474 | 52,608 | 281,568 | 353,930,112 | 15 |
| Union | | 105,216 | 564,144 | 358,410,240 | 31 |

The installed `Raw.native` iterates whole copies sequentially. Within each copy it invokes the same signed physical generator, using one consecutive interval of the original owner IDs. Only the scale-one copy splits the first 1,008 rank-one cuts into quarters and complements. Each projection resumes at the start of that same native copy using the original ordered grades, all original output axes, and the original witness seed for its absolute copy index. The other copy's fields stay allocated, untouched and held outside the projected operator, preserving the shared stock reserve. A runtime guard rejects access to the other owner's interval. Both states must match their exact expected output or preserved dormant input, and all initial and temporary owners must be restored and retired. The published aggregate owner-write and peak-handle controls are retained.

The phase job executes the complete original `check_phase_passes.py`, including the 48 native graph census, residue delta 189,072 and exact 80,165 and 84,104 callback controls. The arbitrary signed probes in the numerical fixture retain every 512-assignment first-column check, both additional addresses in every physical column and both mixed-register checks. The original signed price negative controls in the main registered package remain untouched. The optional receipt union check rejects omission of an original paid event.

Use CPython 3.12 from the repository root. The three commands below exercise the published registered manifests. Their inputs pin the same original scientific source at `81f578a512bac27b373cc7868981e45b62f2ce3d`.

```sh
python3.12 -IB scripts/research_package.py --package research/p104-compact-rounded-partitions-numerical-replay
python3.12 -IB scripts/research_package.py --package research/p104-compact-rounded-partitions-numerical-copy-474
python3.12 -IB scripts/research_package.py --package research/p104-compact-rounded-partitions-numerical-phase-census
```

For separate exact receipts and the union check, use the same script with explicit output paths.

```sh
out=$(mktemp -d)
runner=research/p104-compact-rounded-partitions-numerical-replay/project.py
python3.12 -IB "$runner" 0 --out "$out/copy-0.json"
python3.12 -IB "$runner" 1 --out "$out/copy-1.json"
python3.12 -IB "$runner" phase --out "$out/phase.json"
python3.12 -IB "$runner" union --receipts "$out/copy-0.json" "$out/copy-1.json" "$out/phase.json"
```

OpenAI Codex assisted the verifier split and coverage check. The original reported κ and five inherited signed premises remain the scope of the main package. [Original package and credits](../p104-compact-rounded-partitions/README.md)

## Open next questions

Can the separate hosted jobs complete under their command caps with the same signed receipt union?
