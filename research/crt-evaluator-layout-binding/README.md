# Constant-1 CRT evaluator on accepted reservoir layouts

**Scoped counting proof. No new κ.** The selected conditional exponent stays
60403/20000000. This does not accept PR #4100.

## Result

PR #4377 proves that #4100's control evaluator costs at most
`E(p, ell) = 2^{4 ell} (p+2)^{16}` bit-steps, so `C_E = 1`, when the CRT
group has bit length `W <= p` and the batch has at most `8(p+2)` axes. Its
open question 2 asked to use `C = 1` inside §3–§4, starting with `H >= G`.
That was blocked on placement geometry. PR #4174 has since been merged.
PRs #4646, #4921 and #4923–#4926 kept `C_E` as an unevaluated factor.

[PROOF.md](PROOF.md) shows the following for every layout accepted by the
#4174 constructor with `L <= p`. That hypothesis is #4328's, and it holds
at the actual #4100 caller.

| Part | Statement | Sharp at |
|---|---|---|
| 1 | `ell >= 21`, `p >= 1310720`, `G >= 2688` | `p = 1310720`, `ell = 21`, `d = 2^16`, widths 20 |
| 2 | `W <= p`, `r_max <= p/268800`, `d <= p/20`, all below `8(p+2)`, so `C_E = 1` applies | — |
| 3 | `H >= G` and `2^{-H} E <= 2^{-G} E <= 2^{-60 ell - 48 λ} <= 2^{-2268}` | `p = 2^{21} - 2`, `ell = 21` |
| 4 | per-record bad-key charge `r (2/B + window) E < (p/89600) 2^{-G} E < 2^{-2263}` | not sharp |

Part 4 holds for both the sharp window `β` and the published `8B/2^K`. It
replaces #4646's printed `(C_E p / 6400) 2^{-60 ell} (p+2)^{-48}`.

**The hypothesis `L <= p` is needed.** The constructor also accepts `p = 2`,
`ell = 2`, `d = 2^19`, widths 2. There `L = 2^20`, `r_max = 40 > 32 = 8(p+2)`,
and the root control group has `W = 2^19 > p`. So `C = 1` does not transfer to
that layout. Also, #4845's two `p = 2` exceptions are outside `L <= p`. With
`L <= p` we have `p >= 1310720`, so #4845's full-batch fit for `p >= 3` applies.

With the actual caller's stronger `L <= b + 1` and `p = 6b`, the same argument
gives `ell >= 24`. The #4174 production plan `p = 9240576`, `ell = 24` attains it.

Not proved here: the ordinary H-bit interchange callee, sparse sorting and
reinsertion, the elementary finite range, and #4377's bit-step model. The
last is used as stated and not replayed.

## Evidence

[verify.py](verify.py) loads the #4174 allocator on main. It checks the
following:

- the thresholds `ell >= 21` and `ell >= 24` for every `ell <= 256`;
- the minimal, `2^{21} - 2`, production and #4926 edge layouts, including
  the first 64 plans on the bottom and root levels;
- equality `2^{-G} E = 2^{-2268}` at `p = 2^{21} - 2`, with exact
  rational part-4 bounds for both windows;
- the accepted counterexample;
- four rejection controls. These are an `ell = 20` layout, the sharper
  bound `2^{-2269}`, the cap off `L <= p` and the coefficient `1/268800`.

Input pins and quoted source phrases are checked first. The finite checks
corroborate the written proof; they do not replace it.

## Scope

Card `uniform-transfer-audit`, scope **refined** to the evaluator-to-layout
binding. Canonical main fetched 2026-10-23 at
`cef4b52f2a59009865bf8eabde1be3f159063703`, priority revision 7. Source
pins are in [SOURCES.json](SOURCES.json).

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 scripts/research_package.py --package research/crt-evaluator-layout-binding --check-only
python3.12 -B scripts/research_package.py --package research/crt-evaluator-layout-binding
```

The direct command `python3.12 -B research/crt-evaluator-layout-binding/verify.py`
prints `PASS_CRT_EVALUATOR_LAYOUT_BINDING` in well under a second.

## Open next questions

1. **Does one ordinary H-bit interchange of `CRT.md` §3–§4 fit its stated
   `O(V H^{1-a} + V)` bill at the actual #4174 width `H = r_max G`?**
   - *Why it matters:* it is the reservoir-side remainder of #4377 and #4650
     open question 2. Under `L <= p`, the evaluator side is closed here.
   - *First step:* write one #4174 three-field exchange as ordinary
     interchange calls. Count its placement and restoration actions against
     `V H^{1-a}` on `p = 1310720`, `ell = 21`.
   - *Blocked by:* nothing.

## Credit

Cinna Davis, PR #4100, for the CRT construction, `E(p, ell)` and the
reservoir parameters. unpaidmoon, PR #4377, for the constant-1 evaluator and
the open question. PR #4646 (unpaidmoon) for the absorption and the printed
product line. PR #4328 for the `L <= p` hypothesis. Hiroki KUMAZAKI
(@kumagi), PR #4174, for the constructor and the production plan. PR #4650
and PR #4845 for the shared-arena bills. James Reed, PRs #4921 and #4923–#4926, for
the reservoir-constant chain that left `C_E` open.

Prepared by JoyboyBrian with substantial Anthropic Claude (Claude Code)
assistance. Apache-2.0. No independent human review and no formal-kernel
acceptance are claimed.
