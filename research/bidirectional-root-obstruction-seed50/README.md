# Bidirectional root shears cannot save a third transfer

**Scoped recursive-interface negative result; no new kappa or selected supplier.** For the signed 3x3 target

```text
M = [[1, 1, 1], [1, 1,-1], [1,-1, 0]],
```

retain the two arbitrary dirty roots and exactly twelve ordinary signed child queries

```text
root += s B_j x_j       or       y_i += s A_i root,   s in {+1,-1}.
```

The Ai and Bj are arbitrary fixed linear maps over Q or C; no commutativity or invertibility is assumed. Extend PR1651's root alphabet from `z += a*w` to also allow `w += b*z`, for any fixed nonzero rational or complex coefficient. Both roots must be restored for all dirty inputs. Each complete transfer costs one full-row pass plus its control and routing.

**Result:** three nonzero transfers cannot provide the proposed saving. Any restoring product of at most three elementary root shears uses one ordered pair of roots throughout. Under the 12-query source and reader constraints, the fixed target then reduces to the inherited one-root source-prefix problem. Its all-three-row obstruction rules out this target. Four transfers remain necessary; PR1651's credited four-transfer word still attains the count. The proof for at most three transfers holds with any finite number of dirty roots, although the fixed construction and recursive invoice here use two.

This establishes a transfer-count result under the stated query count and complete restored interface. It does not establish optimal cost among four-transfer words with changed ports, higher query counts, free root permutations/scalings, or arbitrary dense root maps. Child call prices may depend on ports. Compiler, hosting, precision and selected supplier admission remain separate.

## Why three restoring shears collapse to one pair

On any finite set of roots, an elementary shear is `T = I + a E_ij`, `i != j`, `a != 0`. For two shears on distinct ordered pairs, the product differs from identity by two uncancelled off-diagonal matrix entries, with a possible extra diagonal term from their product. It cannot equal one elementary shear. If the ordered pairs agree, the product is `I + (a+b)E_ij` (or identity). Therefore a product of three nonzero elementary shears equal to identity must use the same ordered pair for all three. One shear cannot restore; two restoring shears are inverse shears on the same pair.

With that pair fixed, normalize the root state by its cumulative shear height `h`. The roots' dirty-coordinate rows are `(1,h)` and `(0,1)`. A source written twice restores only when both writes use the same root and, for the second root, the same height; their signs are opposite. A reader used twice cancels arbitrary root dirt only on the same root and height, also with opposite signs. No other root port has an equal or opposite normalized unit direction in characteristic zero.

For three shears the height segments are either `0`, `0,a,0`, or `0,a,b,0`, with the nonzero heights distinct. Each nonzero height occupies one interval. If a source pair writes the second root at nonzero height, both writes lie within that interval, so it cannot send a net source term into the first root. If it writes at height zero, a paired first-root reader either sees zero cross coefficient or both reader calls lie inside one nonzero interval and cancel the same source interval. The first root never transfers into the second. Thus all cross-root source/output coefficients vanish. Every nonzero entry of M requires its Ai and Bj to use the same root. Since M has connected support, all six operators use the same root and the shear work can be removed. The result would be a one-root paired-query schedule.

The 12-query specialization forces each of the six operators to occur exactly twice: one source query leaves uncancelled arbitrary dirt, and one read leaves uncancelled root dirt. The one-root schedule is a six-step signed source walk. PR944's inherited obstruction is reproduced here: over all 720 orders of the three positive and three negative source steps, no path exposes all three rows of M as a difference of two visited prefixes. This is a complete finite enumeration of this one-root interface, not a general lower bound for other query alphabets.

## Exact controls and complete price

`verify.py` records independent checks in [EVIDENCE.json](EVIDENCE.json):

- 1–3 shear words for 2, 3 and 4 roots over coefficients `{-2,-1,1,2}`; direct matrix updates and an independent two-factor convolution agree. These finite controls support the written coefficient-independent matrix proof; they do not replace it.
- At four shears with two roots, the same coefficient set has 136 closed words, 64 mixing both directions. Direct enumeration and independent pair-product convolution agree. This records the boundary where the three-shear lemma stops; it does not show that these loops save child-query work.
- 6, 90 and 210 source/read/shear interleavings for the zero-, two- and three-shear height shapes, checked by a second exact rational engine. Admitted restoring orders have zero cross term. Dropping either source or reader restoration produces explicit nonzero controls.
- A mixed-direction four-transfer identity and the six-transfer heights `0,a,0,a,0` give nonzero cross controls. The three-shear obstruction is not extended past its stated boundary.
- The inherited one-root histogram over all 720 paths, independently reproduced by permutation and depth-first generators, is `[72,84,84,48,264,84,84,0]` by available-row mask.
- PR1651's exact witness is expanded to 300 factor calls and replayed as free noncommutative polynomials on all 11 independent dirty rows. Removing any one of its four passes or changing one pass sign fails. An exact dense integer replay with singular, noncommuting factor fixtures at lengths 2 and 3 also passes.

The complete recursive lowering follows PR1651: `C([f]) = complete leaf cost`; `C(F) = 2 C(F_left) + 2 C(F_right) + node dispatch`. Each inverse reverses the child word and signs. At lengths 2,3,4,5,6,7 this uses 4,10,16,28,40,52 leaves for each factor; the six operators occur twice, for 300 calls total. The four root transfers make 304 top-level factor/pass records, use two roots and three borrowed child rows (11 mutable data rows including sources and outputs). There are no free full-row copies or hidden child restores.

This prices the predecessor's four-pass endpoint exactly. The proposed optimistic three-pass budget is one complete full-row pass cheaper at the same 12 queries; the theorem rules out that endpoint under arbitrary dirt. Four-pass port pricing, admission and native realization remain open. See [TASK.json](TASK.json) for the candidate alternatives, stop rule and next question.

## Reproduce

From repository root in Python 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/bidirectional-root-obstruction-seed50
```

Expected: `PASS_BIDIRECTIONAL_ROOT_OBSTRUCTION monodromy_words=127952 one_root_paths=720 factor_calls=300 transfers=4`, followed by `PASS_REGISTERED_RESEARCH_PACKAGE`.

## Provenance and credit

OS assignment seed **50**, recursive interfaces track. Base `2de86c77b4127d2f01f504e0c7c5e4db737caa3c`; selected conditional kappa at base is `836330098538459/500000000000000000`, with the complex primitive binding. PR1651's source commit, blob IDs, SHA256 digests and retained notice are in `SOURCES.json` and `references/`; its proof, cost model and exact certificate are inputs, not imported code. Ross Richardson's PR1651 establishes the one-way four-transfer floor and supplies the witness; Charles Bethin's PR1637 supplies the two-root 12-query construction; Ross Richardson's PR944 supplies the one-root obstruction; woklerx's PR1438 source-port argument is credited there. New work: Cinna Davis (1337isnot1337), with substantial OpenAI Codex assistance; Apache-2.0.

## Open next questions

Can one of the six four-transfer bidirectional root-direction shapes lower
port-specific recursive costs, or reproduce the same target with a shorter
source walk? The transfer-count proof leaves this open. Enumerate the six
shapes, solve the paired source/read constraints for M, and expand each viable
word through its actual children before comparing port-specific charges.
The blocker is a complete four-transfer mixed-direction classifier and native
recursive tariff; a root-pass count alone cannot answer that question.
