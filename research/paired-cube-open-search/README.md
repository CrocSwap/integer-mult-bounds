# Open search tooling for paired-cube complex words

Discovery tooling only. **No new κ is claimed**, and no certificate or verification group is changed.

Until now, the physical frame descents and compensated reuse pairs in the paired-cube complex words (#157, #161 and later) were shipped as frozen inputs, `references/paired-cube/physical/{frames,pairs}.json`; no producer is included in the repository. New modules also needed frozen carrier arcs. This package supplies open producers for both and a parallel search over module choices. Every result is accepted or rejected by PR161's unchanged checker, `scripts/paired_cube_physical.py`.

| File | Contents |
|---|---|
| `generator.py` | Physical frame descent: alternating passes, each move to the lower bound (previous frames + value span) or the upper bound (next-frame intersection) when nested and cheaper. Reuse pairs: maximum-weight assignment of ungauged donors to gauged recipients (donor dead before recipient's first op, donor frame inside gauge). Runs the checker on its own output. |
| `frames_open.py` | PR161's `paired_cube/frames.py` plus open maximum carrier matching (Hopcroft–Karp) when no frozen arcs are given; identical with frozen arcs. |
| `modules_open.py` | All-but-one variants: cyclic intervals, prefix/suffix, tunable tree split. |
| `search.py` | Genetic search over triple coordinates and all-but-one module, scored by the generator; persistent worker pool. |
| `reproduce.py` | The results below, through the checker with exact replay. |

## Results (float discovery scores of the complex supplier)

```sh
python3 -m pip install -r research/paired-cube-open-search/requirements.txt
python3 -B research/paired-cube-open-search/reproduce.py        # about 40 s
```

| Word | Frames moved | Pairs | W | Complex saving | vs PR161 |
|---|---:|---:|---:|---:|---:|
| PR161, frozen plan (equals its certificate) | 7,880 | 2,970 | 15,681 | 5.8856699e-4 | — |
| PR161, open generator | 8,221 | 2,970 | 15,681 | 5.8905532e-4 | +0.083% |
| Cyclic all-but-one, open matching and generator | | 2,970 | 14,361 | 5.9306799e-4 | +0.765% |

The cyclic module builds each root `Σ_{j≠i} x_j` from shared cyclic intervals. It needs 1,320 fewer roles than PR161's balanced tree. A two-generation search smoke run (`search.py --generations 2`, 65 s on 6 workers) reached 5.9334228e-4 with `tk = [0,2,3,4,5,6,9,11,12,14,16]`, still cyclic.

Since #163 the bit supplier binds, so these complex-side gains do not raise κ by themselves. They are offered as tooling for the next stacked word, not as a record.

## Speed

One configuration takes about 7 s once worker caches are warm (17 s cold), against about 74 s for a straightforward loop. Two changes give this:

- `basis()` returns the unique reduced row-echelon form of a span, so it is memoized exactly. The cache is shared with PR161's gauge selector and checker.
- Donor-in-gauge containment is computed for all distinct frame pairs at once, as one F2 parity matrix (frame rows × gauge annihilators) in numpy.

Each worker settles at about 2.6 GB, so `--jobs` should be about RAM / 3 GB.

## Scope and credits

The scores are float roots of the complex moment. Turning any configuration into a κ needs the usual exact supplier, bit and assembly certificates (for example `scripts/paired_cube_network.py` or #163's package). Base: PR161 at `d14e29157bc905be1ced0776dd893d0714013f3a`. The word, modules, gauges and checker are icekylinx's (#144) and eumemic's (#157/#161). The frame and reuse lemmas are #130/#131, jamesyc's #124 and #143. `frames_open.py` is a modified copy of icekylinx's Apache-2.0 file, with notice retained. Prepared by Joel Pulikkan (GamingPuzzled) with Anthropic Claude assistance; Apache-2.0.
