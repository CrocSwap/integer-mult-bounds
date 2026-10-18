# Fan out a shared product through an arbitrary dirty output

**Exact local construction; no selected-provider admission or new `kappa`.** A shared bilinear term can be delivered to any number `q` of arbitrary-dirty output rows using one common multiplication child and two affine fanout waves. The entry value of the anchor row cancels between the waves, so the construction needs no clean output and no private helper.

Within the target-row XOR alphabet and with only one common-product child, the proof also shows that the `2(q-1)` row ADDs are minimal. The result does not claim a lower bound for larger alphabets or extra helper rows.

For outputs

```text
A_i' = A_i XOR p(x,y) XOR t_i(u_i,v_i),  i=0,...,q-1,
```

the direct schedule uses `2q` complete rank-one child calls. The construction uses `q+1` calls and `2(q-1)` full-width row ADDs. At `q=112`, that is 224 calls versus 113 calls, plus 222 explicitly charged ADDs. The exact net saving is `(q-1)*(mu - 2*alpha(w))`, where `mu` is the complete shared-child price and `alpha(w)` is the complete price of a width-`w` row ADD. No finite price ratio or provider occurrence is assumed.

| `q` | Direct children | Dirty-anchor children | Full-width ADDs | Saved children |
|---:|---:|---:|---:|---:|
| 2 | 4 | 3 | 2 | 1 |
| 8 | 16 | 9 | 14 | 7 |
| 112 | 224 | 113 | 222 | 111 |

At `q=112`, the same target family exposes the contract tradeoff:

| Schedule for this same map | Rank-one children | Row ADDs | Extra state |
|---|---:|---:|---|
| Separate calls | 224 | 0 | none |
| Clean-helper sharing | 114 | 112 | one clean helper, compute and inverse cleanup |
| Clean-anchor adaptation | 113 | 111 | `A_0` must be clean at entry |
| Dirty-anchor schedule here | 113 | 222 | no clean row or helper |

For the same endpoint, the dirty schedule uses the same number of multiplication children as a clean-anchor adaptation, but spends 111 more ADDs at `q=112` to remove the clean-entry condition. Against the clean-helper schedule it saves one child and the helper/cleanup, at the cost of 110 more ADDs. PR #1907's published map has `A_0=p` with no private `t_0`, so its 112-child invoice is a different endpoint; the comparison above adds the private `t_0` call to make the outputs match. These are operation-count comparisons; the complete finite price condition remains `mu > 2*alpha(w)`.

The reversible schedule and complete invoice are proved in [PROOF.md](PROOF.md). The OS seed, exact base, selected-record hash, task claim, source pins and scope limits are in [TASK.md](TASK.md) and [SOURCES.json](SOURCES.json).

Selected context is the maintainer-reviewed conditional construction with `kappa = 836330098538459/500000000000000000` (decimal `0.001672660197076918`): the accepted record points to `docs/research/community-batch1099-review.md`, source manifest `research/community-frontier1094-audit/SELECTED-SOURCE.json`, certificate `research/community-frontier1094-audit/ASSEMBLY.json` (SHA-256 `1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045`), and reproduction command `make frontier1094-verify`. This research package leaves each unchanged.

## Conditional profile screen

If eight hypothetical 112-port blocks of this form occur in the selected rank profile, the rank-one child count changes from 2,412 to 1,524. The pinned rank-only `complex-local-word-ceiling` model gives exact `a` brackets:

| Profile | Exact bracket |
|---|---|
| Current fixed profile | `[1690054109/1000000000000, 169005411/100000000000]` |
| Candidate rank profile | `[2026751029/1000000000000, 202675103/100000000000]` |

The dirty-anchor schedule also adds **1,776 scalar XORs** for those eight blocks (or 1,776 width-`w` row ADDs at the abstract vector interface). These are retained as an additive linear term; they are not folded into the rank-only brackets. The selected source's actual bilinear operand pairs and output-target lifetimes have not been mapped to this interface, so no supplier saving, frontier change or `kappa` follows.

## Verification

From the repository root, the registered replay is:

```sh
python3.12 -B scripts/research_package.py --package research/dirty-output-anchor-seed-da1ec3f0
```

Expected final line:

```text
PASS_REGISTERED_RESEARCH_PACKAGE research/dirty-output-anchor-seed-da1ec3f0 outcome=completed
```

The direct verifier uses only the Python standard library plus the pinned local ceiling model:

```sh
python3 -I -B research/dirty-output-anchor-seed-da1ec3f0/verify.py
```

It exhausts **281,600** arbitrary oracle-output/dirty-target assignments across `q=2..5` and widths one or two, checks the inverse map, rejects four malformed schedules, checks all cost formulas for `q=2..112`, and replays both exact profile brackets. The symbolic proof covers the full declared q range. The local session has Python 3.14; the registered Python 3.12 replay remains the CI command.

## Related work and limits

This changes the output-state contract used by [PR #1907](https://github.com/CrocSwap/integer-mult-bounds/pull/1907): its anchor output is clean at entry, while every target here may be arbitrary dirty. It avoids the clean helper and inverse cleanup in [PR #1872](https://github.com/CrocSwap/integer-mult-bounds/pull/1872). [PR #1930](https://github.com/CrocSwap/integer-mult-bounds/pull/1930) composes a three-stage linear prefix chain; [PR #1917](https://github.com/CrocSwap/integer-mult-bounds/pull/1917) compares a cross-fed parity-connector handoff against a closed-call baseline. The closest concurrent mechanism is [Discussion #1167 comment 18926048](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18926048), which broadcasts a common linear map from a separate dirty scratch row across different source-prefix states, then restores that scratch with another map call. This package instead uses a required output as the carrier for one common bilinear term, includes a private product per target, and proves the minimum row-ADD count for the single-common-child alphabet. The overlap search and limits are recorded in `TASK.md`.

The result does not establish that the selected provider has a batch of targets sharing one product, that the required row routing is available, or that a finite leaf implementation satisfies `mu > 2*alpha(w)`. A provider-specific port map, routing/head invoice, and complete charged child-cost comparison remain open. No changes are made to frozen sources or the selected result.

## Open next questions

- Does the selected source contain an operand-compatible block of 112 arbitrary-dirty outputs with the required independent private terms and a legal two-wave target route?
- At the first actual source width, does the complete shared child price exceed both full-width affine fanouts, including head movement and any interface transitions?
- Can a second dirty output anchor reduce the fanout diameter without increasing the number of common child calls?

Prepared with substantial OpenAI Codex assistance. No independent human review is claimed. Apache-2.0.
