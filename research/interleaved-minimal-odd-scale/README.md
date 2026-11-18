# Minimal physical odd scale for the interleaved graph

Use native scale 176715 in the exact graph from
[PR #7726](https://github.com/CrocSwap/integer-mult-bounds/pull/7726).
Keep binary height 21 and the source caller, root grid and complete invoice.
The conservative scalar rate falls from `2^30` to `2^26`. No new kappa
follows. The normalized minimum was already known; the physical substitution
and complete finite comparison are the result here.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json) and
[CREDITS.md](CREDITS.md). The proof states the five inherited interfaces,
the independent-input contract and the finite fixture limits.

Python 3.12 and its standard library are sufficient. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/interleaved-minimal-odd-scale
```

Both normal and optimized commands print:

```text
PASS_MINIMAL_ODD_PHYSICAL_SUBSTITUTION 176715 16
```

The verifier checks every separate coefficient product, all public endpoints,
five sharp physical witnesses, the complete addressed schedule, all scalar
cases, the full ordinary bill and the retained depth guard. It authenticates
63 retained files. The fixed source constructor and engines are shared
dependencies. No independent human or formal-kernel acceptance is claimed.
Hosted CI and selected cold replay are separate checks.

## Open next questions

The structured questions are in [TASK.json](TASK.json).

- Can a new bound reduce the physical binary height or root magnitude while
  preserving every partial product and unfinished recursive context? Begin
  with the actual physical component maximum, not the normalized grid alone.
- Can a uniform tape implementation replace the inherited scalar and
  whole-extent assumptions with a proved finite transition cost? Preserve
  source owner lifetimes, restoration and all conversions.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
