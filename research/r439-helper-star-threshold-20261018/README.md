# First profitable helper-star wrap: three target rows

**Scoped positive interface and invoice; no supplier or κ claim.** This package
specializes the existing H2-sem interface to one small helper-mixing word and
prices the exact word. It does not repeat the source-bound R439 pair census or
claim that the fixture occurs in the selected circuit.

## Question and result

Let `x` be an untouched source, `a,h` two arbitrary dirty helpers, and
`y1,y2,y3` three arbitrary targets. Each scalar ADD is `d ^= s` over F2. The
direct D word performs `yi ^= a; yi ^= h` for each target, six scalar ADDs.
Replace it with the helper-star word

```text
h  ^= a
y1 ^= h
y2 ^= h
y3 ^= h
h  ^= a
```

This five-ADD word implements exactly

```text
(x, a, h, y1, y2, y3)
  -> (x, a, h, y1+a+h, y2+a+h, y3+a+h).
```

It holds for every dirty input: the first and last gates prepare `h+a` and then
restore `h`; each target receives that prepared value. The semantic helper map
is the 3-by-2 matrix `N` with every row `[1,1]`. Thus it satisfies the
H2-sem boundary `(x,y,H) -> (x,y+N H,H)` with semantic `K=N`.

The word is at frame zero, uses only target/helper operands, has distinct source
and destination on every gate, and never feeds a target into a helper. There is
no allocation, COPY, ERASE, child call or frame change inside D. The state at
the D cut is exactly the state expected by the unchanged continuation. This is
the needed replacement for the inherited gate-local H2/K comparison on this
instance; a source-read tally is not used as the interface proof.

## Full local price

For `q` targets with the same two-helper response, direct writes cost `2q` ADDs.
Prepare/restore around `q` target writes costs `q+2`, so it first saves ADDs at
`q=3`: `6 -> 5` (one ADD saved). At `q=2` it ties (`4 -> 4`), and at `q=1` it
costs one extra (`2 -> 3`). This is the threshold for this fixed direct word and
this fixed wrap, not a lower bound for every circuit.

| Local bill | Direct word | Helper-star word |
|---|---:|---:|
| One-source scalar ADDs | 6 | 5 |
| Local role histogram | `{ADD1: 6}` | `{ADD1: 5}` |
| Forward positive envelope `F` | 3 | 3 |
| Reverse positive envelope `B` | 3 | 3 |
| Peak from all-one register weights | 3 | 3 |
| Binary boundary | exact `N` | exact same `N` |

`F` and `B` execute the listed scalar additions over positive integer weights,
starting every coordinate at one; `B` executes the inverse word in reverse
chronological order. These values fully price this local fixture. They are not
the selected supplier's nine-stage profile, and no 104/192-bit supplier guard
or hosted invoice is inferred from this six-coordinate example. The one-ADD
local saving may not survive frame, placement, copy/erase, cleanup, precision,
or consumer costs in a real word.

The verifier enumerates all 64 binary states in both chronological directions,
checks the exact boundary and helper restoration, and rejects omitted-restore
and wrong-target controls. The algebraic identity extends from F2 to any
F2-module by the same cancellation, as in the H2-sem contract.

## Reproduction

From the repository root, Python 3.12 standard library only:

```sh
python3 -B research/r439-helper-star-threshold-20261018/verify.py
python3 scripts/research_package.py --package research/r439-helper-star-threshold-20261018 --check-only
python3.12 scripts/research_package.py --package research/r439-helper-star-threshold-20261018
```

The first command should print:

```text
PASS_HELPER_STAR_Q3 states=64 direct=6 mixed=5 saving=1 F=3/3 B=3/3 controls=2
```

## Relation to the pinned project result

At base `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, the selected record is
`certificates/selected-result.json` (SHA-256
`bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129`),
reviewed in `docs/research/community-batch1099-review.md`. Its exact source
binding is `research/community-frontier1094-audit/SELECTED-SOURCE.json`; the
manifest SHA-256 is
`79b3de5db3dbcb9829789ba58e9e45758926031e2a7d80667a08429d369be53b`. It binds
the selected bit word `research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz`
to SHA-256 `e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f`,
`xcheck_p.py` to `af3decc877e27c00001cf56f50c6c09566e8e101297ab34c7860aed96a06d80e`,
and the exporter to `8a5999601f917dbb492bb9ae9a344611f18cc7cedc53dc3c76496a369e530eb3`.
The record's reproduction command is `make frontier1094-verify`. The selected
conditional κ is `836330098538459/500000000000000000`. This local lemma neither
changes that record nor supplies a new bit word.

The broad H2-sem contract and chronological substitution theorem are woklerx's
PR1194 (`research/r439-semantic-d-contract-seed10/PROOF.md`). Aaron Wang's PR848
and PR1782 supply the R439 copy-sharing obstruction and a source-bound
H2-sem-admitted wrap; the latter already checks a full dirty boundary. Sagar
Thakrar's `r439-bsection-stars-seed01` package provides the card's positive
orientation example and unchanged paid profile. This note adds only the
three-target break-even arithmetic and its complete local invoice; it does not
claim the H2-sem interface itself as new.

At the final live overlap check (2026-10-19 UTC), open PR [#3533](https://github.com/CrocSwap/integer-mult-bounds/pull/3533)
at head `c61d746404e534affd9fbcba1f2e448e45c06e42` examined a single restored
helper edge against the literal K mask on a source-bound word. Open PR [#2721](https://github.com/CrocSwap/integer-mult-bounds/pull/2721)
at head `6b14e212a1aba401d29f2bf7378e745ee2aed7f2` examines whether H2-sem's
no-target-feedback clause is needed at a framed level. This package claims
neither result: its word is an abstract three-target microinstance, and it
retains the no-target-feedback condition.

## Open next questions

Does any still-uncovered source-pinned D cut in the R439 helper-star lineage
contain this exact three-target/two-helper response with a full framed bill
that retains the one-ADD saving? This matters because only an actual charged
caller can turn the local saving into bit-circuit work. First step: find a
candidate D cut not already covered by PR1782, PR1805 or PR2033, then replay the
same semantic `N=K` boundary and recompute its forward/reverse integer envelope.
Blocked by the need for a distinct source cut and the full continuation,
cleanup and guard accounting; no construction search is justified until that
instance exists.

## Credit and disclosure

Credit to woklerx (PR1194 H2-sem contract and bridge), Aaron Wang (PR848/PR1782
source-bound helper-wrap analysis), Sagar Thakrar (PR967 helper-star lineage
and the assigned positive orientation package), DreamingOfClouds (PR589), and
eumemic (PR555/checker lineage). Their artifacts are cited and remain unchanged.
Prepared by OpenAI Codex (GPT-6 Luna xhigh) with substantial AI assistance; no
independent human review is claimed. Apache-2.0.
