# Fixed-clock BIT balanced chart reassignment ceiling

The exact retained BIT word has 60 paid nested ingress slots and 20 compatible rank-seven destination charts. This package exhausts all 1,200 slot/chart pairs at the original clocks and tariffs. The 20 admissible arcs are ten disjoint two-cycles within individual singleton banks. Even granting every timely cyclic source to its recipient independently and retaining its old library for free, no bank gains a direction in the marked quotient. **Verified conditional κ change is 0%.**

## Replay

From the repository root in a clean checkout, use CPython 3.12 with assertions enabled.

```sh
python3.12 -B scripts/research_package.py --package research/bit-balanced-retarget-bound
```

The standalone replay also works offline from an exported package.

```sh
python3.12 -I -B research/bit-balanced-retarget-bound/replay.py --controls
```

The replay authenticates its bundled source closure by relative path and SHA-256, regenerates five pinned predecessor receipts and the independent carrier audit, and compares the census and independent price audit byte for byte. It checks an early delivery that relies on a late balancing arc. A changed native input and a fabricated cycle incidence must both fail. No package installation, mutable remote data or user-specific interpreter path is required.

The proof describes the relaxation, exact bounds and remaining obligations. The two JSON receipts contain the full incidence, source and price evidence. [Proof](PROOF.md) · [Census](RESULT.json) · [Independent audit](AUDIT.json) · [Exact-source provenance](PROVENANCE.tsv)

## Open next questions

- Can coupled lineages preserve one intervening ADD while reducing the paid MOVE count? The separate local-only Round 29 unread-chain census exhausted all 2,871 paid MOVE paths and found every path a singleton. Start with the full census of consecutive same-lineage paid MOVE pairs with exactly one intervening coframed ADD. Cap at 2,871 pairs or 240 seconds. Track the other ADD operand at the cut, account for any paid transport needed to bring both operands into one chart and return them, and price disjoint savings across all 36 copies. A negative directed whole-word bound closes the scope. A survivor still requires an exact arbitrary-input signed, ownership and restoration check before a build. [Campaign handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111)
- Can a changed chart set, an altered arrival count or a different unmarked library enlarge the marked quotient? Recompute the complete cost of new delivery before testing a site. This proof fixes those inputs. A changed route also requires full signed and timing checks, erasure, precision and tape accounting.

Jerry Chen / CubeJerry supplied the retained native word, invoice and interval implementation. The contribution builds on the marked geometry, source and tariff audits in #7209, #7258, #7260, #7271, #7272, #7273 and #7275. Nick Petalas supplied the stock sharpness comparison in #7264. Clear1nsight's #7244 and #7274 provide the complete peer comparisons and retained BIT premise. OpenAI Codex and subagents materially assisted the proof, implementation, audit and packaging. [Notice](NOTICE)
