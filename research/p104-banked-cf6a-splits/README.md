# Three helper splits on the #7708 cf6a banked circuit

**Conditional κ ≥ 0.0037427697512.** This is 0.0000023796607 (0.0636%) above #7708's crossing 0.00374039009047 (claim 0.00374039009039). The parent is aliromman's #7708 circuit: the #7700 cf6a word (SYLforge), Clear1nsight's role-1256 relay (#7704), and 46 relay-cut recodings. Three exact **causal helper splits**, in the style of Clear1nsight's chart-595 split (#7697), each replace one rank-nine helper job by two independently owned smaller jobs. Every paid edge and route is unchanged. [Construction](PROOF.md) · [Physical accounting](PHYSICAL.md) · [Check](verify.py)

| Cut chart | Retired role (new exit) | Fresh role (route) | Target ranks |
| --- | --- | --- | --- |
| 498 | 126 (3 → 498) | 1501 (498 → 127) | 9 → 4 + 5 |
| 480 | 239 (3 → 480) | 1502 (480 → 127) | 9 → 2 + 7 |
| 595 | 281 (3 → 595) | 1503 (595 → 127) | 9 → 1 + 8 |

Per native invocation, the paid histogram is unchanged at 6,121 edges. The productive targets change by `{1:+1, 2:+1, 4:+1, 5:+1, 7:+1, 8:+1, 9:−3}`, which leaves the rank mass unchanged. The complete 16-call invoice has 101,488 paid jobs, 21,200 targets and S = 1,328. The crossing is certified in (0.00374276975125, 0.00374276975126).

## Reproduce

```sh
python3.12 -I -B verify.py
```

From the repository root, run `python3.12 -B scripts/research_package.py --package research/p104-banked-cf6a-splits`. The check uses only the standard library and takes about two minutes on one core. It does the following:

- Authenticates every asset and the #7700 word (canonical SHA-256 `ae62d5d8…1472`).
- Checks locality and an acyclic schedule.
- Checks that every paid edge is GF(2)-nested with positive rank and that the symplectic rank of each transfer equals the dimension difference.
- Runs an exact Gaussian column simulation of every chart pair that is absent from the word, with a non-nested control.
- Proves exact rational equality of all 1,504 public outputs: the 400 mains equal the word's, and every helper, including the three fresh roles, returns its own input.
- Prices the literal caller.

## Open next questions

- Do two-role splits at one chart, or splits of the smaller helper groups (exits 245, 243, 240), give further target gains? Start by extending the split screen to rank-two pairings and to the other groups.
- Do the relay-cut and hub-reroute classes find new edits after the splits? The splits change input coordinates and inject into departures from charts 498, 480 and 595.

## Credit

aliromman supplied the relay-cut recodings and their algebra (#7708) and the banked-transfer circuit (#7674). Clear1nsight supplied the role-1256 relay (#7704), the chart-595 split method (#7697) and the role-230 reroute (#7682). SYLforge supplied the cf6a nine-swap word (#7700) and the 16-call caller. The contributors credited in their notices supplied the predecessor constructions; their notices are in [credits/](credits/). The split search, exact builder and checks are by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
