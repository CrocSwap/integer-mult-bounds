# A finer split of one moved 48-eigenspace

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

For the historical 8-by-112 centre query, the involution `u = (4 7)(5 6)` with all signs `+1` lies in the order-`3072` stabilizer of sector `c = 1`, preserves both moved `192`-characters fixed by `s = (0 4 3 7)(5 6)`, and does not commute with `s`. On the eigenvalue-`1` space of `s` in each of those characters, `u` acts with trace `24` and cuts the `48`-dimensional space as `36 + 12`. The `12`-dimensional minus space is invariant under `A_1`.

The same census shows that this is not true of every noncommuting preserver: `64` of them preserve the `48`-space and act by `±1`, and `256` do not preserve it. Selected conditional kappa stays `781451/250000000`. The argument, the census, and the limits are in [PROOF.md](PROOF.md).

## What is certified

The live input is the query pinned in [SOURCES.json](SOURCES.json), SHA256 `5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.

`χ` is the sign character that sends the flips of coordinates `1` and `2` to `-1` and the flips of coordinates `5` and `6` to `+1`. Its twin `χ'` has those four values reversed. The predecessor involution `g` preserves both, and `t` swaps them, so the pair `<g, t>` moves both. PR #7009 already splits each by `s` into four complex eigenspaces of dimension `48` and shows that the centralizer of `s` acts by scalars. This package starts from that open question: a noncommuting element, and a basis the trace formula does not list.

On each eigenvalue-`1` space the `512` character-preserving elements of the stabilizer are:

| class | count |
|---|---:|
| centralizer, scalar `±1` | `32 + 32` |
| noncommuting scalar `±1` | `32 + 32` |
| noncommuting involution, split `36 + 12` or `12 + 36` | `48 + 48` |
| noncommuting order-`4` element, trace `±24`, multiplicities not listed | `16 + 16` |
| does not preserve the eigenspace | `256` |

The witness `u` is one trace-`+24` involution. For both characters the verifier builds a `12`-vector integral basis of its minus space, checks the geometric actions of `s` and `u`, and applies `B_1 = 4 A_1` with two implementations. Each image lies in that basis. The `Q`-span is therefore `A_1`-invariant.

This is an exhaustive finite census of those `512` restrictions, plus a direct invariance proof for the exhibited `12`-space. It is not a characteristic polynomial and not an irreducibility theorem.

## Scope

Catalogue card `formal-interface-lemma` asks for a formal caller binding. The open clause is question 1 of [PR #7009](https://github.com/CrocSwap/integer-mult-bounds/pull/7009), recorded in `research/centre-c1-moved-sign-split/TASK.json` and in [discussion comment 19507677](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19507677). The question asks whether one element of the `c = 1` stabilizer that preserves a moved `192`-character, and does not commute with `s`, meets a `48`-dimensional eigenspace of `s` in a smaller `A_1`-invariant subspace. The answer is yes: `u` meets the eigenvalue-`1` space in the `12`-dimensional minus space above.

The package does not recompute the moved-character split certified by PR #7009, the characteristic polynomial of the `48`-space, the `c = 3` sign split of PR #6965, or the `216`-space questions of PR #7008 and PR #6964. Selected-baseline orientation returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY` for kappa `781451/250000000`.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -B -W error research/centre-c1-moved-eigenspace-cut/verify.py
python3 -I -B -O -W error research/centre-c1-moved-eigenspace-cut/verify.py
python3 -B scripts/research_package.py --package research/centre-c1-moved-eigenspace-cut --check-only
```

The direct marker is `PASS_C1_MOVED_EIGENSPACE_CUT`. Acceptance uses explicit checks, so `-O` does not disable them. Rejection controls cover a coordinate transposition, a sign flip that removes `u` from the stabilizer, a truncated sign subgroup, the operator `s` itself (its minus space on this eigenspace is zero), and an off-support spike that must not be accepted as a character vector.

Not run: Lean, Docker, the degree-`881` replay, the degree-`410` minor, the selected cold replay, a `c = 3` census, and any characteristic polynomial. An exploratory intersection-dimension screen modulo `1000003` for `χ` is recorded in [PROOF.md](PROOF.md) and is not part of the registered verifier.

## Overlap

`scripts/find_overlap.py` was run on 2026-11-10 against upstream `17469fff78c22941280f04d39dc5a1faee09c840`. Coverage: local notes `10180` of `10178` HEAD paths, complete; `317` open PR records, pagination complete, fetched `2026-11-10T08:57:11Z`; `6973` discussion records, pagination complete, fetched `2026-11-10T08:58:06Z`.

The phrases `48-dimensional eigenspace`, `moved 192-character` and `centre-c1-moved-sign-split` match PR #7009 and discussion comment 19507677, which state the question and stop at the trace formula. No other open-PR record in that snapshot states this cut. Closed PRs were searched through local READMEs, task metadata, and the ledger only. No code diffs were searched.

## Open next questions

The structured list is in [TASK.json](TASK.json).

- Is the exhibited `12`-dimensional space irreducible under `A_1`? The invariance check does not produce the characteristic polynomial of `B_1` on that basis. This is smaller than, and not a substitute for, the characteristic polynomial of the `48`-dimensional space.
- For one element that preserves the character and does not preserve `E`, what is the exact dimension of `E ∩ h E`? The registered census only separates "preserves `E`" from "does not." The modular screen in [PROOF.md](PROOF.md) is not that rank.

## Credit

JoyboyBrian recorded the sign-character dimensions and the open decomposition question in discussion comment 19144258. The preserved-character split and the operators `g` and `t` are the census behind PR #6944. The moved-character split, the element `s`, and the centralizer obstruction are PR #7009, by unpaidmoon. Ali Romman's PR4958 and PR4720 retain the query and the Bell action. Nick Petalas's PR5120 is the degree-410 lower bound. Krzysztof Wojt's PR5168 is the degree-881 one-slot annihilator. The doubled representation comes from PR1719. New work is Apache-2.0.
