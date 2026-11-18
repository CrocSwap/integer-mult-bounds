# Full-endpoint words on the shared-hub six-projector pool

**Scoped negative proof; no new kappa.** The exceptional complete pool in
[PR #7707](https://github.com/CrocSwap/integer-mult-bounds/pull/7707)
has two orthogonal normal triples that share one coordinate. Its sixth
projector is outside the preceding bridge-family theorem. This package
settles its word question at the actual four-dimensional pattern budget.

For every word that uses all six types and has at most four saturated
exponent relations in the paid-generated torsion-free group, a full
original-coordinate diagonal monomial endpoint forces two blocks:
all calls from one triple, then all calls from the other. The three
totals in each triple must be exactly equal. If those totals are S and T,
the five targets are `(S,S,S+T,T,T)`. Each target is a sum of a disjoint
subset of paid exponents, so total target rank cannot exceed paid rank.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json),
[verify.py](verify.py) and [CREDITS.md](CREDITS.md). The proof covers
arbitrary repetitions, coordinate permutations and unused spectators.
It excludes extra or omitted types, arbitrary changes of ambient basis,
larger relation budgets and other maximizing pools. The exact alphabet is

```text
(6,5), (5,6), (7,7), (12,20), (20,12), (28,28).
```

Pairs give binary image and covector masks on coordinates 0 through 4.
The paid factors are `I+([a]-1)P` over F2[H]. The endpoint requirement
applies to every ambient input. It does not assume clean spectator state.

## Reproduce

Use CPython 3.12 and its standard library:

```sh
python3 -B scripts/research_package.py --package research/shared-hub-triple-word-obstruction
```

The registered normal and optimized commands print:

```text
PASS_SHARED_HUB_TRIPLE_WORD_OBSTRUCTION
68760 complete Laurent words; 1584 two-block endpoints
24 larger fixtures; disjoint paid-subset targets and all boundary controls pass
```

The five exhaustive multiplicity domains have lengths six through nine.
Each word has a degree-two and full Laurent check. Independent multinomial
counts agree with each passing count. The commutator check tests all 511
nonempty subsets and finds exactly the one dependence used by the proof.
Twenty-four larger fixtures reach 17 ambient coordinates and 15 calls.
They include both block orders and coordinate permutations. Every target
is reconstructed from its assigned paid subset. Every crossed-boundary
mutant changes a recorded input column.

The controls distinguish parity from exact exponent equality, and the
paid-generated exponent group from a larger ambient group. At five
relations, an interleaved diagonal control has three zero calls. At six
relations, an interleaved identity has all calls nonzero. These controls
do not prove any rank saving above four relations. Omitted-type and
wrong-common-coordinate target controls also fail their endpoint checks.

The unbounded conclusion rests on the written proof. The finite word
census uses the universal exact common-total lattice, not every integral
lattice with its modulo-two reduction. Full predecessor suites, selected
cold replay, native/physical replay, Lean, Docker, independent human and
formal-kernel review were not run. The adapted checker is not independent
review of its sources. The selected kappa remains `0.00363005817` and all
five assumptions remain. No complete recursive invoice is supplied.

## Open next questions

Other complete pools can attain the same geometric maximum. To test one,
state its exact alphabet and relation budget, derive its first-order
kernel, and check a full endpoint before claiming a saving. The present
two-triple commutator lemma need not hold there. Source-specific evidence
must justify a new round; another parameter or seed is not enough.

A larger relation budget on this pool also changes the problem. The
control identities show that the two-block conclusion can fail, but
they save no rank. A useful next step needs an explicit nonzero paid
profile and full target bill. Native cost and supplier admission would
remain additional obligations. No follow-up is reserved.

Prepared by Ali Romman with substantial OpenAI Codex assistance.
Apache-2.0. Exact predecessor credit is in CREDITS.md.
