# Conditional κ = 0.003643438506419: endpoint and temporal composition

This composes Rohan Arun's completed [#7142](https://github.com/CrocSwap/integer-mult-bounds/pull/7142)
endpoint-funded split with [#7143](https://github.com/CrocSwap/integer-mult-bounds/pull/7143)'s
temporal source. Both directed prices give **κ=0.003643438506419**, a gain of
**.000000221683943 over #7142** and **.000000257834774 over #7143**.
All three direct CPython 3.14.7 checks passed. Final registered isolated
Python 3.12.16 replay passed all three commands and every frozen receipt field. No admission or selected-frontier change is claimed.

The exact cut moves to44638, with the output coefficient -349/32 translated
from retired 648 to 1449. The whole rational cut identity is checked again.
A paid input extension1479:3→595 funds the rank 9→7+2 helper split at 529;
role 228's contact-free path preserves its paid rank 2. The native delta relative
to #7143 is ΔP={1:+1}, ΔT={2:+1,7:+1,8:−1}. All666added ADDs,4 SCALEs and one
MOVE are charged; owned inventory remains 55 labels / 58 lifetimes / peak 44.
[PROOF.md](PROOF.md) gives the identity, chronology and limits.

## Exact sources and reproduction

INPUTS.json retains all 31 files from #7143 at
`9ff298bd6547299dc5b263873bf8a400909e5501`. PEER-INPUTS.json retains all 30 files from
completed #7142 at `316b93f25361c0fd1b3a50e1180bd59096c3e45e`. Nested closures and notices are included.
REUSE.json authenticates five byte-identical peer implementations. The candidate
native SHA256 is `8f5c08866c50070c8579d0dc230bc2941ec3669d643ba373ac4b1d59b423446d`.
The signed17-stage caller is unchanged.

```sh
git fetch --no-tags https://github.com/CrocSwap/integer-mult-bounds.git main
python3.12 -B scripts/research_package.py --package research/p104-endpoint-temporal-composition
```

The registered early/native/application gates compare every frozen receipt.
[VALIDATION.md](VALIDATION.md) states actual coverage; [APPLICATION.md](APPLICATION.md)
records the full bill when completed. The claim's BIT headroom is
.000123251493581; its invoice crossing lies in (0.0036434385064194522455189967132841, 0.0036434385064194522455189967132842).
This is one constructive composition, not a search exhaustion or optimum.

## Credit and open obligations

Rohan Arun supplied the endpoint extension and constructor, Ali Romman the
helper/causal-history identities, CubeJerry the retiming and verification
engines, Matarener the kernel methods, ToikY earlier chart120 and pricing.
Credit dillona's #7143 source, Cinna Davis/1337isnot1337, Dugongue,
DreamingOfClouds, Douglas Colkitt/#7000 reviewers and every retained author.
Substantial OpenAI Codex assistance; no subagents. Apache-2.0.

Five inherited assumptions remain: native_all_columns, owned_erasure, compiler,
precision_tape, analytic_recovery. Independent human/formal review, maintainer
admission and compiled top-level execution remain open.

## Open next questions

Independently replay the translated boundary vector and complete combined bill,
especially the paid input conversion and unchanged owned census. Start with
VERIFY.json and the untranslated-column corruption control. Before another
optimization, refresh canonical guidance and live overlap and freeze this source.

[Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19520521).
