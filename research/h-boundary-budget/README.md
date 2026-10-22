# The p3 H branch: exact boundary budget and three closed decoder routes

**Negative result, no new κ.** zxv's H branch of
[PR4359](https://github.com/CrocSwap/integer-mult-bounds/pull/4359) replaces the
local response by an involution `H = I + BC` (`CB = -2I`). Its raw rank surplus
is far above the current frontier, but the noncommuting p3 controller leaves three
interval endpoints of the form `Q K Q`. Their direct correction costs 672
rank-one requests in complex and 666 in BIT, more than the whole surplus.
[PR4431](https://github.com/CrocSwap/integer-mult-bounds/pull/4431) closed
completion-only fresh inverses. This package asks how much a corrected boundary
may cost and which decoders cannot meet that price.

## 1. Exact budget at the selected conditional κ

Each rank-one call has weight exactly 1 in the moment at every saving `s`, so
the largest affordable boundary bill is the certified moment of the uncorrected
profile. The profiles are the retained ones: complex
`controller_tariff.geometry(3, 43)` with kernel H, surplus 616, and BIT with
the three-row minimum completion, surplus 645 = 603 + 42.

| Saving | complex budget | BIT budget |
|---|---:|---:|
| 0.0023 | 392 | 456 |
| **0.00302015** (#4470) | **322** | **397** |
| 0.004 | 228 | 317 |

Saving roots for each boundary bill (certified brackets in `RESULT.json`):

| Boundary bill | complex | BIT |
|---|---:|---:|
| free | 0.0063799 | 0.0079333 |
| one shared head conjugation (224 / 222) | **0.0040422** | 0.0051761 |
| two (448 / 444) | 0.0017248 | 0.0024471 |
| direct, three (672 / 666) | negative at s = 0 | negative at s = 0 |

So a corrected H branch beats the frontier only if all three endpoints are
repaired for at most 322 complex requests, roughly 1.44 head conjugations.
These are raw rank screens. Outer rows, tails, compiler gates and the scalar and
movement costs of a new decoder are not included, so they are ceilings.

## 2. Whole-bank Q events cannot fit

One Q event on a complete bank costs 112 complex requests, so the budget admits
at most two (`224 <= 322 < 336`). PR4359's `universal_two_query_screen` already
shows that two complete-bank events give a coefficient span of at most 1 against
the required 3. Even three events would cost 336 and give a complex root near
0.0029, below the frontier.

## 3. Port subsets cannot be skipped

For the native H112, `rank(H - I) = 8` exactly, but all 112 rows and all 112
columns of `H - I` are nonzero. Every interval product `K` therefore moves data
on every port, so a correction touching only part of a bank leaves a nonzero
`Q`-dependent block.

## 4. Gather decoders through the rank-8 bottleneck cost at least the direct bill

The low rank suggests compressing: since `Q^2 = I`,

```
Q K Q - K = Q M Q - M,   M = K - I,
```

and `M` factors through 8 fields per stage. This fails for an elementary reason.
On port `p`, `Q` is one rank-one request along that port's own line `q_p`. Two
ports' requests can be merged by linearity only when their lines agree, because a
request along `q_p` and a request along `q_r` are different transforms. The
stage routes (`rho`, `Gamma_s`) fix each port's line, and the commutation
`[H_s, Q b_s] = 0` only provides the full call `Q b_s` on the compressed side.

The data leave no room:

| | complex | BIT |
|---|---:|---:|
| ports | 112 | 111 |
| distinct query lines | **112** | **111** |
| ports touched by `H - I` | 112 | (not computed) |

Computing `M (Q w)` for an arbitrary input therefore needs one request on every
port that `M` reads: 112. Writing `Q (M ...)` back needs one on every port that
`M` writes: another 112. The three bad roles have independent inputs, and a
request on a sum cannot be separated afterwards. Any decoder of this kind,
meaning free scalars and routes plus rank-one requests applied to linear
combinations, costs at least `3 * 2 * 112 = 672`, which is exactly the direct
bill. The direct correction is optimal within this class.

**Scope.** This is a lower bound for linear gather decoders at fixed H112, fixed
owners and the fixed p3 controller. It is not a theorem about every possible
algorithm. A construction that changes the local family, sends several ports'
lines to a shared line before the request, or changes the controller is outside
it.

## 5. No controller of this family has fewer Q-conjugated roles

The verifier enumerates the free noncommuting controller of
`bit/pr589_h_global_probe.py` for p = 1..4 and every idle keep mask. It keeps
those that diagonalize exactly with parity-preserving (Q-free) boundaries:
2, 3, 8 and 20 controllers. **Every one has exactly p roles ending as `Q K Q`
with nonempty K.** Each local call stamps its stage letter on both streams of
its pair, so the odd (Q-carrying) stream always has a nonempty word. The
p3 keep-43 controller reproduces the probe's parity `[0,1,0,1,1,0]`.

The H surplus of `mixed_forest_search.verify` is `224p - 8(2p+1)` (616 for
p = 3). A direct repair costs 224 per bad role, so after it

```
224p - 8(2p+1) - 224p = -8(2p+1) < 0      for every p.
```

Each pair brings exactly as much rank credit as its own endpoint repair costs.
Changing p or the idle mask cannot fund the direct boundary. Combined with
section 4, a funded H branch needs a changed port geometry (shared query lines)
or a changed pair structure of the controller. Both are new suppliers rather
than repairs of this one.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/h-boundary-budget --check-only
python3.12 -B scripts/research_package.py --package research/h-boundary-budget
```

`verify.py` uses only the standard library and imports the pinned
`research/kappa-rebuild` modules. Those modules expect `research/kappa-next-regime`
at the repository root; on main that tree is vendored under
`research/kappa-0023-productive-jobs/dependencies/kappa-next-regime`, and the
verifier adds that path. It runs in about 3.5 minutes on Windows / CPython 3.12.
Controls: a budget one above the certified value is certified negative, a
perturbed `H - I` is rejected, a duplicated query line is detected, and the
p3 keep-43 controller reproduces the probe parity.

## Open next questions

The structured versions are in `TASK.json`.

1. **A redesigned H local family.** Ports that share query lines, or an `H` whose
   `H - I` touches few ports, would break the bound of section 4. This needs a
   new H112 completion and native replay.
2. **A new port geometry or pair structure.** Section 5 closes controllers
   with fewer Q-conjugated roles for p <= 4 (each pair's repair costs exactly
   its credit). Only a supplier whose ports share query lines, or whose
   controller is not built from Q-gauged pairs, escapes both bounds. That is a
   new complex supplier, not an H repair.

## Credit

The H construction, the endpoint obstruction, the retained profiles and
receipts are zxv's (PR4359, PR4431) together with their cited predecessors.
This package adds the budget, the root table, the native rank/support and
query-line counts, the gather argument and the controller parity census. Prepared by Matarener (Mark) with
substantial Claude Code assistance. Apache-2.0. No independent human review.
