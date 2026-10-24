# Paid two-target CRT stencil and repair join

A protected unary producer now supplies the two-target stencil consumed by
ToikY's existing dense scanner. Its actual mask is then consumed by the retained
reverse-key repair. This answers open question 1 of unpaidmoon's
[PR4644](https://github.com/CrocSwap/integer-mult-bounds/pull/4644), which joined
one target only. The result is a scoped construction and cost proof with finite
implementation checks; it is not a new generic repair theorem or a new bound.

## Interface and result

The seven protected unary inputs `(G,H,K,Y,J0,J1,B)` satisfy

```text
G>=1, H>=2G, K>=G+4, J0>=0, J1>=J0+K, Y>=J1+K, B>=0.
L=2H+Y+B, M=2^L; compact radix b=2^G.
```

`B` is a spectator width. Inputs have canonical LEFT/unary/END representation
and initially blank tails. The validator checks the word and its immediate
blank successor, not an arbitrary infinite tail. Addresses have fields
`(u,t,y,back)` of widths `(H,H,Y,B)` with arbitrary dirty values.

For target `Ji`, digit `i` of both `u,t` must be less than `b-1`, and the
`K-1` guard bits above `Ji` must lie in `[2b,2^(K-1)-2b)`. The good set is the
intersection of the two predicates; the hole mask is the **union of their
failures**. The two source functions may depend on both guard windows but
must omit **both active target bits**, not merely their own bit.

[producer.py](producer.py) uses eleven fixed private words, inherited paid
unary arithmetic and emission helpers, and only read/write/unit-move ports.
It preserves all seven inputs, erases its private data and END markers, and
returns every head. It also cleans up grammar/arithmetic rejection under the
representation contract. No host geometry test supplies the emitted stencil.

[PROOF.md](PROOF.md) derives, for every admitted geometry:

```text
Producer actions = 46H+20K+38Y-24G-J0+12J1+12B+438 <= 70L+438.
Producer visited cells = 5H+K+4Y-3G+J1+2B+47 <= 6L+47.
Producer + unchanged scanner actions <= 8ML+15M+83L+456.
Producer + scanner visited cells <= M+7L+51.
```

The producer/scanner composition has 21 fixed tape roles. The stencil and mask
are owned outputs. The retained repair consumes the real mask, uses
`T(S^-1(x))` keys at holes, restores all payloads and erases repair scratch.
This caller also retires its stencil for exactly `5L+7` further actions.
These counts charge reads, writes and unit moves; finite-control transitions
are not an exact physical transition-table tariff. The repair still has its
separate opaque-record/width-weighted model and host key arithmetic. Adding
those meters does not produce a complete bit-step invoice.

## Evidence and reproduction

[RESULT.json](RESULT.json) records:

- 972 small geometries plus one long stencil, with independent interval-oracle
  comparison, exact action/space formulas and opaque producer ports.
- Four full address spaces below: **180,224 addresses, 177,408 repaired holes**.
  Every actual mask bit, forward/reverse macro, good-set invariant and final
  payload is checked, including input/head restoration and scratch cleanup.
- Nine cleanly rejected geometry/grammar cases. Omitting the second digit test
  misses 768 holes; omitting the upper guard misses 256. The paired choice
  `f0=y[J1], f1=y[J0]` violates all-target independence and yields an actual
  collision of the ideal map.

| `(G,H,K,Y,J0,J1,B)` | Addresses | Holes |
| --- | ---: | ---: |
| `(1,2,5,10,0,5,0)` | 16,384 | 16,128 |
| `(1,2,5,10,0,5,1)` | 32,768 | 32,256 |
| `(1,3,5,10,0,5,0)` | 65,536 | 64,512 |
| `(1,2,5,12,1,7,0)` | 65,536 | 64,512 |

The full replay uses cross-guard sources `f0=y[J0+1] xor y[J1+2]` and
`f1=y[J1+1] xor y[J0+2]`. Its complete-address cases have `G=1`; larger `G`
is covered only by the stencil grid and the quantified proof, not a larger
repair census. Universal inversion and repair statements remain cited from
the pinned predecessors. Finite examples do not prove those statements.

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/crt-two-target-stencil --check-only
python3.12 -B scripts/research_package.py --package research/crt-two-target-stencil
```

The registered runner executes ordinary and `-O` replay; both print
`PASS_CRT_TWO_TARGET_STENCIL`. Direct replay also works in a Git-free export:
`python3.12 -O -B research/crt-two-target-stencil/verify.py`.
The verifier authenticates thirteen live inputs before compiling their captured
source bytes, avoiding predecessor bytecode-cache imports. Ordinary replay
compares the frozen receipt and writes nothing; `--write-result` is an explicit
authoring operation. [SOURCES.json](SOURCES.json) pins base
`b91956876e5b4122fd89179f1b57557ff8378f15`, blobs and SHA256 values.

## Scope, overlap and expansion decision

[Task metadata](TASK.json) refines priority-revision-7 `uniform-transfer-audit`
to the producer boundary. [Discussion4985](https://github.com/CrocSwap/integer-mult-bounds/discussions/4985)
is the canonical claim/result. PR4201 already scans multi-target stencils and
PR4328 already repairs host-built multi-target masks. PR4904's two-target sharp
window audit concerns macro algebra and excludes tape repair. This package's
added value is paid stencil admission and its actual join, not those existing
capabilities. PR4716's current-state key audit and JoyboyBrian's newly published
[PR4982](https://github.com/CrocSwap/integer-mult-bounds/pull/4982) remain separate:
PR4982 lowers the key port at fixed `(u2,t2,y8)` geometry with a supplied ROM;
it does not supply this unary two-target stencil producer.

The family decision is **narrow**: retain this local interface and stop. Caller
descriptor construction/transport and binary keys remain unknown here; the
existing record repair allowance is retained, not replaced. Variable target
count, last-`K` boundary targets, physical placement, ordinary interchanges and
a common complete machine invoice remain open. No full supplier, native/Lean
replay, proof-assistant acceptance or selected-frontier change is claimed.
Selected conditional kappa remains `.00302015`.

## Open next questions

1. Can one actual CRT caller construct, transport and restore these seven unary
   descriptors within its complete allowance? First pin that caller and its
   binary-to-unary representation; this package begins after that boundary.
2. Can a variable-size ordered target descriptor stream admit disjoint windows
   with fixed tape roles and paid cleanup? First specify descriptor ownership,
   overlap rejection and last-`K` handling. A fresh overlap/family decision and
   full allowance must precede another implementation round.

[The structured questions](TASK.json) state relevance and blockers. The current
[Discussion4709](https://github.com/CrocSwap/integer-mult-bounds/discussions/4709)
handoffs and PR4982 should be checked before assigning related key work.

## Credit

Cinna Davis/#4100 supplies the compact CRT caller. ToikY/#4208 and #4201 supply
the unary helpers and scanner; unpaidmoon/#4644 supplies the one-target join
and this handoff; Ryanson Jonathan/#4328 supplies the repair schedule/tariff;
Hiroki KUMAZAKI/#4169 supplies the arbitrary-source inverse. Douglas Colkitt and
John-Michael Smith/#763 supply the inherited compact and exceptional-repair
argument. All predecessor sources remain unchanged and pinned.

Prepared by Hiroki KUMAZAKI (@kumagi) with substantial OpenAI Codex assistance,
including separate agent checks of the geometry and cost algebra. No independent
human review is claimed. Apache-2.0.
