# Five plane queries for the selected P111 bit decoder

**A finite bit-decoder construction and favorable coverage-law screen. No new supplier or `kappa` is claimed.**

This package factors the exact 111-port decoder from the selected merged PR589 bit word into five rank-two queries. It uses one explicit 9-to-10 Parseval frame and keeps both source and target endpoint maps. The construction is at the decoder boundary; its plane-frame route, physical streaming schedule, hosting and precision invoice remain open.

## Construction

The frozen word has nine retained source channels. Write their target and source factors as matrices `P` and `Q`, so the scatter map is `P Q^T`. The ten columns below are vectors in `F2^9`:

```text
a1 = e1 + e2       a2 = e1 + e3
a3 = e2 + e3       a4 = e1 + e2 + e3
a5 = e4            a6 = e5
a7 = e6             a8 = e7
a9 = e8             a10 = e9
```

They satisfy the exact identity

```text
sum(j=1..10) aj aj^T = I9  over F2.
```

Transform both factor lists by these ten columns, then group columns `(1,2)`, `(3,4)`, `(5,6)`, `(7,8)`, `(9,10)`. Each pair gives one rank-two plane query. Therefore

```text
(P A)(Q A)^T = P (A A^T) Q^T = P Q^T.
```

The verifier reconstructs the nine original channels from the pinned word and checks the equality on all 661 formal input columns at once, including dirty targets and helpers. It also checks the expected `B0 = (1 + G) mod 2` map on all 111 by 111 source-target pairs. The five transformed source and target factor pairs each have exact F2 rank two.

## Copy and ADD invoice

The original decoder has nine rank-seven B14 pairing terms, for copy charge `63`. For each new plane, the rational pairing rank between the union of its target support and the union of its source support is exactly eight. The five plane queries therefore cost `40`, saving 23 copy-rank units (36.51%) at the algebraic decoder boundary.

Forming the ten frame channels from the nine old channels takes five XOR additions on each side, ten ADDs total. The favorable local profile charges those ten as rank-one children, removes nine rank-seven copy children, and adds five rank-eight plane children:

```text
before: {1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}, mass 5129
after:  {1:1333, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:10, 8:5}, mass 5116
```

This charges the binary basis change and every B14 copy rank in the proposed decoder. It does not charge physical frame transitions, temporary storage and cleanup, hosting, precision/tape, or composition with the rest of the bit word. Those costs can only reduce the favorable ceiling below.

## Replacement coverage identity and budget

For the pinned bit profile, `m=64`, `v=111`, `K=4`, and nine stages give `W=2 K v / 9 = 888/9 = 296/3` live families per local call. The selected line-port law is

```text
paid mass = (m - 1) W + 63 = 6279.
```

The proposed two-unpaid-coordinate plane law is

```text
paid mass = (m - 2) W + 40 = 18472/3.
```

The exact local profile leaves idle masses `1150` and `3124/3`, respectively. Applying the pinned ceiling routine with its selected nine-stage guard `R=42` gives:

| Model | Certified `a` bracket | Idle mass |
|---|---:|---:|
| Existing line decoder | `[973733779/500000000000, 1947467559/10^12]` | `1150` |
| Five-plane decoder, all other new interface costs set to zero | `[4260424781/500000000000, 8520849563/10^12]` | `3124/3` |

At `a=1/99`, the favorable plane relaxation is already greater than one (`1.0047022529...`), so this construction does not reach that planning target. The result is a decoder-cost mechanism, not a replacement bit supplier. The selected result remains complex-bound; no overall `kappa` improvement follows from this screen.

## Reproduction

From the repository root:

```sh
python3 -B research/bit-p111-parseval-plane-decoder-seedceccc765/verify.py > research/bit-p111-parseval-plane-decoder-seedceccc765/RESULT.json
python3 scripts/research_package.py --package research/bit-p111-parseval-plane-decoder-seedceccc765 --check-only
python3.12 scripts/research_package.py --package research/bit-p111-parseval-plane-decoder-seedceccc765
```

The verifier uses exact F2 and rational arithmetic. [RESULT.json](RESULT.json) is its deterministic output. Four negative controls check a broken frame, an omitted plane, a switched source factor and a collapsed rank-two factor. Expected status is `PASS_BIT_P111_PARSEVAL_PLANE_DECODER`; the report includes the dirty-map SHA-256 and exact ceiling brackets. The registered replay uses Python 3.12; this local environment currently provides Python 3.14, so the command-level verifier and metadata check are the local evidence.

## Provenance and scope

- Cycle seed: `ceccc7658dd89c833863007fb63ad7b2`; track `recursive-interfaces`; task `coverage-law-change`; priority revision 3.
- Base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; selected-record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Bit input: merged PR589's `research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz`, content SHA-256 `5642fd0e35a1acc11acff8d0c08350c1617e95f310d4d35ad63a651f9eeeba0b`; archive SHA-256 `e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f`.
- Discussion claim: [#1587 comment 18924772](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-18924772). The fresh 2026-10-14 overlap refresh covered 540 open PRs and 524 Discussions with complete pagination and returned no exact term matches. PR #1825 remains the selected complex-side paired-plane construction and lists this bit-side physical realization as open.
- The work builds on PR589/PR555's bit word and PR1084's exact line-decoder pricing model. The plane endpoint question is from Discussion #1587; no code from PR #1825 is used.
- Prepared by Cinna Davis with substantial OpenAI Codex assistance in construction, exact arithmetic, verification and writing. No independent human review is claimed. New work is Apache-2.0.

## Open next questions

- **Can these five coefficient planes be placed in a legal nested-frame schedule with streamed cleanup and whole-call hosting?** The exact decoder equality makes this the physical blocker. First derive source and target frame paths for each pair from the pinned 111-port geometry and test a two-plane dirty-register schedule. The current selected word records line-port routes only.
- **Can a completed bit plane supplier compose with the complex paired-plane construction to improve the selected conditional bound?** The selected result is complex-bound, so this decoder alone cannot move `kappa`. First combine both all-cost invoices in one exact assembly after the route and precision obligations close. PR #1825 still leaves its all-cost complex route open.
