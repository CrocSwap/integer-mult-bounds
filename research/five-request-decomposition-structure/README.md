# Structure of the 24 five-request threshold decompositions

**Task:** independent-moment (an answer to #4598's open question 1). **Base:** canonical main `f626db5c`. **No κ is claimed.**

## Background

petalas's #4598 counts 2,880 complete passing headers for five orthogonal binary requests in dimension six. They come from 24 unordered decompositions

```text
J − I₅ = Σ 1_S 1_Tᵀ   (five rectangles, S ∩ T = ∅, over F₂),
```

each giving 5! ordered headers. Its open question 1 asks to explain the 24, starting with coordinate-permutation and transposition orbits. My #4605 recounted the total by a different method.

## Classification

Under S₅ × ⟨transpose⟩, the decompositions fall into exactly three orbits, 24 = 2 + 10 + 12. Here V = {0, …, 4}.

| family | decompositions | description | headers |
|---|---|---|---|
| **stars** | 2 | {i} × (V∖i) for all i, and its transpose | 240 |
| **mixed** | 10 | for a centre c: {c} × (V∖c), together with (V∖{c,y}) × {c,y} for the four y ≠ c; plus the transposes. One S₅-orbit of size 5 per orientation | 1,200 |
| **pentagons** | 12 | the five edges {u,v} of an undirected Hamiltonian 5-cycle, each with T = the two cycle-neighbours of the edge outside it. One per undirected 5-cycle (4!/2 = 12), stabiliser D₅, closed under transposition | 1,440 |

- **Pentagons and stars sum to J − I over the integers.** #4598's hand counterexample is a pentagon.
- **The mixed family is genuinely characteristic 2.** Column c is covered 1 + 3 times, so its sum equals J − I only modulo 2.

So the 22 non-star subsets that refute the 2·k! pattern consist of **12 integral pentagons**, one per Hamiltonian cycle of K₅, and **10 characteristic-2 mixed decompositions**, one per centre and orientation.

The verifier enumerates the 24 decompositions independently, by its own rectangle search. It then checks:

- the explicit families, and that they partition the 24;
- that the orbits are exactly these families;
- the integer-sum and mod-2 distinction;
- that the hand counterexample is a pentagon.

## Verify

```text
python3 -B research/five-request-decomposition-structure/verify.py
```

The check takes about 1 s and uses the standard library only.

## Limitations

- **k = 5 only.** No all-k formula is given, and the k ≥ 6 count is not computed.

## Open next questions

- **Larger k.** The classification suggests a candidate pattern. For general k, the decompositions should include stars, "centre" families mixed modulo 2, and cycle-type families indexed by structures on K_k. First step: enumerate the k = 6 decompositions of J − I₆. There are 3⁶ − 2·2⁶ + 1 = 602 rectangles, so a meet-in-the-middle search over 6-subsets is needed. Then test whether Hamiltonian-cycle-type and centre-type families account for them.

Credit: petalas (Nick Petalas) for #4598, #4275 and the threshold framing. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
