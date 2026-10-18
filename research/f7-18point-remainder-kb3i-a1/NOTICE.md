# NOTICE — third-party and predecessor attribution

This package (`research/f7-18point-remainder-kb3i-a1`) is a set-level research
contribution by **Aaron Wang**, with help from opencode (substantial AI
assistance; no model named; no independent human review claimed). Apache-2.0.

## Vendored engines (byte-exact, SHA-256 pinned in `verify.py`)

The six files under `vendor/` are copied byte-for-byte from the predecessor
research packages and are credited to their authors. They are re-verified by
`verify.py check_pins` on every run.

| File | sha256 (prefix) | Source PR | Author | Contents |
|---|---|---|---|---|
| `vendor/tight.py` | `14670ef2…` | [PR 2961](https://github.com/CrocSwap/integer-mult-bounds/pull/2961) | Aaron Wang (navinor) | bitmask primitives, the (7,1) Fourier identity, rho classification |
| `vendor/cover18.py` | `24c6a2f4…` | [PR 2961](https://github.com/CrocSwap/integer-mult-bounds/pull/2961) | Aaron Wang (navinor) | reduced (A,D) covering model, Fourier profile system, squeeze numbers, pair-representation rows, bounded search |
| `vendor/vanish.py` | `6c605c54…` | [PR 2961](https://github.com/CrocSwap/integer-mult-bounds/pull/2961) | Aaron Wang (navinor) | vanishing-character class tables, L7 Sidon tight-equality lemma |
| `vendor/agent64_cover17.py` | `082bc838…` | [PR 2773](https://github.com/CrocSwap/integer-mult-bounds/pull/2773) | Aaron Wang (navinor) | profile_c_values (pair-representation shape primitives) |
| `vendor/agent64_search17.py` | `9eb1bf79…` | [PR 2773](https://github.com/CrocSwap/integer-mult-bounds/pull/2773) | Aaron Wang (navinor) | 17-point search primitives |
| `vendor/anchors.py` | `73d73a9b…` | [PR 2961](https://github.com/CrocSwap/integer-mult-bounds/pull/2961) | Aaron Wang (navinor) | anchor-reproduction helpers |

The engines were extracted with `agent_tools.py pr-tree-extract` from the
immediate predecessor [PR 3023](https://github.com/CrocSwap/integer-mult-bounds/pull/3023)
(Aaron Wang), which itself vendored them from PR 2961/PR 2773 with the same
pins. This package never imports them from a predecessor tree at run time; the
copies are local and pinned.

## Model and predecessor credit

- **PR 943** (Ross Richardson): the prefix-walk model (`research/universal-connector-boundary`), in which a restored seven-source singleton word is universal exactly when its prefix set `P` covers `P + P = F2^7`.
- **PR 1185** (Mister-Meeseeks, per current ground truth): the pinned `f(5) = 12`, `f(6) = 16` record (`research/universal-connector-six-source`).
- **PR 2542 / 2634 / 2773 / 2870 / 2911 / 2933 / 2961 / 3023** (Aaron Wang): the 17-point exclusion chain, the KB3b search ceilings (`119/128` at `k=18`, `124/128` at `k=19`), the pair-representation rows, the odd-coverage Fourier/Parseval identity, the `(A,D)` reduction and vanishing-character restriction, the class floors, the tight-class decisions, and the `(5,1)` decision whose recorded remainder ((4,2)/(3,3)/(11,7)/(9,9)) this package takes.
- **PR 2691 / 2973** (Nicholas Stone, NicholasStone) and **PR 3005** (Nick Petalas, petalas): the word-level census line and its false-prune correction (`22 <= f(7) <= 24`, corroborated). PR 2973's scope note explicitly leaves the set-level chain PR 2773-3023 unaffected. This package is set-level only and enumerates no words.

Every cited PR author was verified against current ground truth with
`gh pr view NNN --json author,title` at writing.
