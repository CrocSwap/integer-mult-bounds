# Unsigned connector: depth blocks reach the floor for k ≤ 2c

Take the unsigned dirty connector over a ring of characteristic c ≥ 2, with k
immutable sources and all 2^k − 1 nonzero binary-mask outputs. Every legal word
needs at least c(k + 2^k − 1) complete calls
([#4231](https://github.com/CrocSwap/integer-mult-bounds/pull/4231)). Let N(c)
be the largest k at which that floor is attained. This package shows:

- **Theorem A** (proof, checked for c ≤ 7): N(c) ≥ 2c for every c ≥ 2.
  Concatenated two-source blocks give the floor word. This improves #4231's
  run walk, which reaches k ≤ c.
- **Lemma C** (proof, exhaustive control at k = 3): a block whose masks are
  all single prefixes has at most two sources. Beating 2c with blocks needs a
  depth-d block with more than 2d sources.
- **Characteristic four** (finite certificate plus proof): an explicit
  36-event walk attains the floor of 2,080 calls at k = 9. With the deletion
  lemma and a counting bound, **9 ≤ N(4) ≤ 21**. This answers part of
  #4231's open question 1, which asked where the c = 4 floor first fails.
- **Counting** (proof): N(c) is below the first k with
  C(ck + c − 1, c) < 2^k − 1. That k is 7, 14, 22, 30, 38, 47, 56, 65 for
  c = 2..9.

At c = 2, Theorem A is sharp: #943 shows that five sources fail. At c = 3 it
gives n ≤ 6, the range proved in
[#4232](https://github.com/CrocSwap/integer-mult-bounds/pull/4232). At c = 4
the nine-source walk shows that blocks are not optimal.

The claims are a scoped proof plus a finite certificate. There is no new κ, no
selected-frontier change and no multiplication theorem.

## 1. Interface and prefix criterion

The interface is #4231's. R is a nonzero unital ring of characteristic c. The
rows are k read-only sources x_j, outputs y_m for m = 1, …, 2^k − 1 and one
borrowed dirty connector z. For arbitrary R-linear maps B_j and A_m, the word
must implement

```text
y_m += sum_(j: bit_j(m)=1) A_m B_j x_j,   x_j and z unchanged.
```

The only calls are `B_j: z += B_j x_j` and `A_m: y_m += A_m z`. Signed calls,
extra connectors, scaling, frame changes and free copies are not admitted.

#4231 proves the floor: B_j and A_m each occur a positive multiple of c times.
A floor word therefore has a source walk w of length ck that uses each source
exactly c times. Let q_t ∈ (Z/c)^k count source events modulo c after t steps.
If A_m reads at boundaries t_1 ≤ … ≤ t_c, output m receives
A_m(c·z0 + Σ_j (Σ_i q_(t_i))_j B_j x_j). Since c·z0 = 0, the word is correct
exactly when

```text
q_(t_1) + ... + q_(t_c) = m   in (Z/c)^k     for every nonzero mask m.
```

z is restored because each B_j x_j is added c times. This is the c-fold form of
#4232's triple criterion. Integer coefficients act through Z/c, the prime
subring of R, so no commutation of A_m with B_j is used.

## 2. Theorem A: N(c) ≥ 2c

Say a walk on source set S has **depth d** if every nonzero S-mask is a sum of
at most d prefixes q_t.

**Concatenation.** Let P and P′ be walks on disjoint source sets, each source
used c times, with depths d and d′, where d + d′ ≤ c. In PP′, the prefix at a
boundary inside P′ is (0, q′) because P returns to zero modulo c. A mask
(m, m′) is the sum of the prefixes for m in P and for m′ in P′. The
remaining readouts go to boundary 0, which has prefix zero. So PP′ has
depth d + d′, and by induction blocks with total depth at most c give a floor
walk.

**Blocks of depth one.** For sources a and b, take

```text
a b a^(c-1) b^(c-1)
```

Its prefixes include (1,0) after one step, (1,1) after two and (0,1) after
c + 1. The one-source block a^c has prefix 1 after one step. Pair the k sources
into ⌈k/2⌉ ≤ c blocks. Each mask then reads once at one boundary in every block
where it is nonzero, and at boundary 0 for the remaining readouts.

The verifier builds this word for all 54 pairs (c, k) with 2 ≤ c ≤ 7 and
k ≤ 2c. It simulates each with generic coefficients and checks that every
operator is called exactly c times. At (c, k) = (3, 7), four blocks are needed
and the construction is rejected.

## 3. Lemma C: depth-one blocks carry at most two sources

In a walk that uses source j exactly c times, coordinate j of q_t is 0 before
its first event and after its last. It is 1 between its first and second
events, and lies in {2, …, c − 1} between its second and last. A prefix is
binary exactly when no coordinate is in that middle stage. Its support is
{j : first_j ≤ t < second_j}. That set changes only at the 2k first and second
events, so there are at most 2k distinct nonzero binary prefixes. Since
2^k − 1 > 2k for k ≥ 3, a depth-one walk has at most two sources.

As a control, the verifier enumerates all 90, 1,680 and 34,650 three-source
walks for c = 2, 3 and 4. None has depth one.

Under concatenation, a block of depth d therefore adds more than 2 sources per
unit depth only if it has more than 2d sources. The nine-source c = 4 walk
below has depth 4, so it is such a block.

## 4. Characteristic four: 9 ≤ N(4) ≤ 21

[CERTIFICATE.json](CERTIFICATE.json) gives the walk

```text
4 2 6 4 0 8 1 7 3 2 5 2 1 7 4 3 0 2 5 8 6 5 6 4 8 3 1 0 5 7 8 7 0 3 6 1
```

Each of the nine sources occurs four times. The verifier regenerates, for each
of the 511 masks, the lexicographically first boundary multiset of size four
that sums to it. It then builds the literal 2,080-call word, simulates it with
generic coefficients, and runs it on random singular, noncommuting 2×2
matrices over Z/4.

**Deletion lemma.** This is #4232's lemma; its proof does not use c = 3.
Delete the c events of source j from a floor walk. Each old boundary maps to a
new boundary with the same counts on the other sources, so every mask with bit
j zero keeps its readouts. The attaining set is therefore an initial segment
{1, …, N(c)}. The verifier checks all nine deletions of the certified walk.

**Counting.** Boundaries 0 and ck both have prefix zero, so the readouts of a
mask are a multiset of size c drawn from ck boundary indices. There are
C(ck + c − 1, c) such multisets. For c = 4, C(87, 4) = 2,225,895 ≥ 2,097,151
at k = 21, but C(91, 4) = 2,672,670 < 4,194,303 at k = 22. With the deletion
lemma, every k ≥ 22 fails. At c = 3 the threshold is 14, as in #4232. The
verifier checks the table for c ≤ 9 and that failure persists up to k = 200.

## 5. Search notes (local only, not proofs)

The nine-source walk came from simulated annealing over restored 36-event
walks. These are search failures, not exclusions:

- Eight annealing runs over 40-event walks did not reach all 1,023 masks at
  k = 10.
- No depth-two five-source block at c = 4 was found; the best run covered 28 of
  31 masks.
- No depth-three seven-source block was found; the best run covered 125 of 127.

Depth-two blocks on four sources and depth-three blocks on six exist at c = 4.
They reach only eight sources by concatenation. The search programs and logs
are not committed.

## 6. Reproduction

From the repository root:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/connector-depth-blocks/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/connector-depth-blocks
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/connector-depth-blocks --check-source-history
```

Expected marker:
`PASS_CONNECTOR_DEPTH_BLOCKS blocks_k<=2c c4_attained_k<=9 c4_counting_excludes_k>=22`.
The verifier uses only the standard library and takes about 3 s. It prints a
receipt hash bound to all six package files. Six mutation controls must be
rejected: a dropped call, a doubled readout, a relabelled source call, the
c = 4 word read in characteristic eight, the sorted run walk at k = 9, and the
block construction at (c, k) = (3, 7).

## 7. Limitations

The result covers only the unsigned, immutable-source, complete-call interface
of #4231. Theorem A is proved for every c; the word check runs for c ≤ 7.
Fixed call prices must include their full implementation. Input admission,
coefficient preparation, dispatch and physical costs are additional and
unknown. No consumer is instantiated. The exact value of N(4) and the growth
of N(c) remain open. Proof-kernel checks and independent human review are not
claimed.

## Open next questions

These are recorded with first steps in [TASK.json](TASK.json).

1. What is N(4) exactly, within 9 ≤ N(4) ≤ 21? Every ten-source floor walk
   restricts to a nine-source one, so an insertion search over nine-source
   floor walks is a natural first step.
2. How does N(c) grow? Theorem A gives 2c and counting gives O(c log c). A
   depth-d block with more than 2d sources, valid for every large c, would
   improve the constant.
3. Does any concrete consumer use a characteristic-c batch of more than c
   sources at a favourable complete invoice?

## Credit

Produced by Nick Petalas. The interface, the floor c(k + 2^k − 1) and the k ≤ c
run walk are #4231's. The prefix criterion, deletion lemma and counting
argument extend #4232's F3 versions. The connector interface and prefix-boundary
readout criterion come from Ross Richardson's
[#943](../universal-connector-boundary/README.md). Apache-2.0.
