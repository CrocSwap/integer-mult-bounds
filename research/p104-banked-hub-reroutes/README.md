# Hub reroutes on the chart-595 banked circuit

**Conditional κ ≥ 0.0037291618601.** This is 0.0000025329831 (0.0680%) above the #7697 upper endpoint 0.0037266288770. The parent is the #7697 circuit (Clear1nsight), which builds on #7682 (Clear1nsight), #7674 (aliromman) and the #7669 word (SYLforge). Twenty-one exact **hub reroutes** change the route of 42 paid edges. The edge count, the paid job count, the public boundary, all targets and the rank mass are unchanged. [Construction](PROOF.md) · [Physical accounting](PHYSICAL.md) · [Check](verify.py)

| Per native invocation | #7697 | This circuit |
| --- | ---: | ---: |
| Paid edges | 6,142 | 6,142 |
| Paid histogram change | | `{1:+8, 2:+6, 3:−26, 4:+5, 5:+6, 6:−1, 7:+2}` |
| Weighted change at exponent one | | 0 |
| Public roles (mains / helpers) | 1,502 (400 / 1,102) | 1,502 (400 / 1,102) |
| Nonzero local terms | 170,652 | 170,719 |
| Coefficient bits / native grid | 13 / 2,083,725 × 2¹⁸ | 13 / 2,083,725 × 2¹⁸ |

The complete 16-call invoice keeps 101,824 paid jobs, 21,168 targets and rank-mass surplus 1,328. The crossing is certified in (0.00372916186012, 0.00372916186013). It is computed with an error-bounded Decimal bisection, and uniqueness is proved by interval bounds. The result rests on the same five selected-framework assumptions as #7674, #7682 and #7697.

## Reproduce

```sh
python3.12 -I -B verify.py
```

From the repository root, run `python3.12 -B scripts/research_package.py --package research/p104-banked-hub-reroutes`. The check uses only the standard library and takes about 100–130 s on one core. It first authenticates every file listed in [ASSETS.json](ASSETS.json), then does the following:

- Rebuilds the #7669 word from K372-2 and its twelve published edits, with both SHA-256 pins checked.
- Loads the circuit and checks locality and an acyclic schedule.
- Checks that every paid edge is GF(2)-nested with positive rank. The symplectic rank of each transfer `T_b T_a⁻¹` must equal the dimension difference.
- Simulates exact Gaussian-dyadic states for the 25 chart pairs that are not MOVEs of the #7669 word. All 512 columns must spread over exactly `2^r` equal-modulus basis states. A non-nested control pair is rejected.
- Proves exact rational outputs: all 400 main outputs equal those of the #7669 word, and every helper, including fresh role 1501, returns its own input.
- Prices the literal 16-call caller.

`data/CIRCUIT.json.gz` (decompressed SHA-256 `f4954e25…51a2`) holds the full circuit. `data/MOVES.json` lists the 21 reroutes.

## Open next questions

- Can two hubs per cut, or hubs outside the charts that Q already feeds, give further rank-mass-preserving gains? Start by extending the screen to pairs of hubs and to all nested charts R, then rebuild each candidate exactly against all 1,502 outputs.
- Do the snapshot-sharing questions of #7674 and #7697 change for the rerouted edges? Begin from the last uses on the rerouted rows.

## Credit

The parent constructions are Clear1nsight's chart-595 split (#7697) and role-230 reroute (#7682). The latter is the first hub reroute, and this package generalises it. They build on aliromman's banked-transfer circuit and fifteen pivots (#7674) and on SYLforge's #7669 word and 16-call caller, whose provenance credits DreamingOfClouds, Clear1nsight, Rohan Arun, CubeJerry, Douglas Colkitt and others. The reroute search, exact builder and checks are by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Predecessor notices are in [credits/](credits/) and [NOTICE](NOTICE).
