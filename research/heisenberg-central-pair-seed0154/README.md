# The order-27 central pair costs its direct bill

**Scoped exact register-model result; no new κ.** In the nonabelian group algebra `F2[UT3(F3)]`, two dirty scalar registers cannot jointly apply the central commutator with fewer calls than applying it to each register separately. The exact minimum is eight calls in the stated alphabet.

## Model and target

Represent `UT3(F3)` by triples `(a,b,c)` with multiplication

```text
(a,b,c)(a',b',c') = (a+a', b+b', c+c'+a*b')    in F3.
```

Let `x=(1,0,0)`, `y=(0,1,0)`, and `z=[x,y]=xyx^-1y^-1=(0,0,1)`. The group has order 27; `x`, `y`, and `z` have order three, and `z` is central. Work in the exact formal group algebra `F2[UT3(F3)]`.

For two scalar registers, a paid call is

```text
D_N(g) = I + ([g] + [e]) N,
```

where `g` is one of the four paid labels `x`, `x^-1`, `y`, `y^-1`, and `N=u v^T` is a binary rank-one idempotent (`v^T u=1`). There are six such `N`, hence 24 complete paid operations. The endpoint is

```text
diag([z], [z])
```

as a formal group-algebra matrix, so it is correct for arbitrary dirty register inputs. No extra register, free address operation, copy, clean allocation, or precision change is allowed. A call costs one unit.

A direct schedule applies `x y x^-1 y^-1` to the first register and then to the second: eight calls. Four letters are necessary for one copy of `z`: in the abelianization `C3 × C3`, a word for `z` has zero x and y exponents modulo three; every shorter such word either is the identity or has nonzero abelianization. The displayed commutator attains four.

Free scalar `GL2(F2)` changes of register basis do not enlarge the search. Since scalar matrices commute with the group algebra, they can be pushed through each factor, conjugating `N` to another rank-one idempotent. All six idempotents are enumerated. Any net scalar at the endpoint must be identity after augmentation, because every paid factor augments to `I` and the target augments to `I`.

## Exact lower bound by complete state splitting

Each factor is invertible:

```text
D_N(g) = (I-N) + [g]N
D_N(g)^-1 = (I-N) + [g^-1]N.
```

The verifier builds the exact set of 2×2 group-algebra product matrices for every word length through four. Equal matrices at the same length are merged; this preserves all possible continuations because future multiplication depends only on the current matrix. For each total length `n=0,...,7`, split a word into prefix `P` and suffix `S`, with lengths `floor(n/2)` and `ceil(n/2)`. The endpoint equation `P S=T` is equivalent to `S=P^-1 T`. The verifier checks every prefix state against the complete suffix-state set at that length. No match occurs at any length through seven.

`EXPECTED.json` retains the exact state counts and SHA-256 digests of the sorted states in each layer, plus every split's prefix/suffix coverage and result. The verifier regenerates these receipts and compares them exactly. The direct eight-call word gives the matching upper bound, so the minimum is exactly eight in this group, alphabet, register count and endpoint.

| Word length | Raw words | Distinct exact product states | Sorted-state SHA-256 |
|---:|---:|---:|---|
| 0 | 1 | 1 | `288b1793833bb59673891be54d485696d3f7d8ff9a9168758ef9d00b1bca8985` |
| 1 | 24 | 24 | `1ff8bf8693e35e212e976ec03752819f62a1533dfe648a7e0f232e15ddd6c26d` |
| 2 | 576 | 413 | `5d0f334f0ed44b3c126df7b80c426dbfe5f5003624e80044bdb00939393f481a` |
| 3 | 13,824 | 5,927 | `ab25c7dee773421bf8747865d325c920dc379e6e7e58389e9e9c39b5a290c52b` |
| 4 | 331,776 | 82,063 | `508a4fe9671ee72e2c3ddd45296736d1f510e69cfb3b9df3b6f82657440cc8df` |

The split sizes for lengths 0 through 7 are respectively `1×1`, `1×24`, `24×24`, `24×413`, `413×413`, `413×5,927`, `5,927×5,927`, and `5,927×82,063`. Every target lookup is negative. The full receipt, including exact per-length lookups, is in [EXPECTED.json](EXPECTED.json).

## Reproduce

From the repository root, with Python 3.10+ and no dependencies:

```sh
python3 -B research/heisenberg-central-pair-seed0154/verify.py
python3 -I -O -B research/heisenberg-central-pair-seed0154/verify.py
python3 scripts/research_package.py --package research/heisenberg-central-pair-seed0154 --check-only
```

Expected verifier line:

```text
PASS_HEISENBERG_CENTRAL_PAIR minimum=8 excluded_lengths=0..7 group_order=27 characteristic=2 registers=2 generators=4 idempotents=6 controls=6 matrix_crosschecks=144 state_counts=[(0, 1), (1, 24), (2, 413), (3, 5927), (4, 82063)]
```

The controls include the group presentation and noncommuting order, the inverse of every paid factor, an eight-call two-target positive word, a four-call one-target positive word, recovery of that one-target word by the split search, and rejection of its omitted-letter mutation. A separate 144-case check compares the optimized update with literal matrix multiplication. Equality is checked coefficient by coefficient in all 27 group coordinates.

## Result boundary and overlap

This answers only whether two registers can share a central-commutator implementation in this exact order-27 alphabet. It does not establish a general lower bound for nonabelian groups or another register count. The group algebra is an optimistic formal address model; no physical compiler, hosting, recursive supplier or analytic transfer is supplied. The result makes no κ or integer-multiplication claim. The selected construction remains unchanged and its complex supplier still binds.

The closest predecessor is [PR #1822](https://github.com/CrocSwap/integer-mult-bounds/pull/1822), which treats central/noncommuting pairs in Q8. Here the group has odd order 27 over coefficient field F2, the central target has order three, and its shortest generator word has length four. Other nearby work includes [PR #1716](https://github.com/CrocSwap/integer-mult-bounds/pull/1716) on the order-six coordinate-CNOT alphabet and active claims on D8, UT4 and four-register affine/rational targets. The final 15:22 UTC overlap refresh completely paginated 535 open PRs and 594 discussions without warnings; it found no Heisenberg-group scope. Exact base and source pins are in [SOURCES.json](SOURCES.json). The superseded Q16 screen and its corrected direct baseline are recorded in the released claim at [Discussion #1167](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18926868).

Prepared by Cinna Davis with substantial OpenAI Codex assistance. No predecessor implementation is copied. New work is Apache-2.0.

## Open next questions

[TASK.json](TASK.json) records one follow-up: test whether another odd-order class-two group has a central target whose direct generator word leaves room for register sharing. The first step is to specify the group and compute the exact direct word metric before building any register search. This is blocked until a group/target outside the active Q8, D8 and UT4 work has both a sufficiently long direct target word and a plausible shorter commutator schedule.
