# Gauge44: a changed factory forward map with 44 rank-four cold ends

Prepared for icekylinx with OpenAI GPT-6 Astra assistance. Apache-2.0. This note describes the new complex local construction. The package's global evidence supplies the resulting global bound and retains the upstream conditional assumptions.

## 1. Exact result and comparison

The final word has 112 source ports, 112 target ports and 492 helper registers. It implements the same arbitrary-dirt scalar endpoint as the upstream word,

$$
(X,Y,H)\longmapsto(X,Y+X,H),
$$

and its inverse-transpose orientation is checked separately. All 204 nonzero entrance frames remain valid. The new ending set consists of **44 cold helpers at rank-four frames**, together with the 34 entering-helper ends inherited from the JP8 HPE stage.

The precise comparison is with the JP8 provider reconstructed from PR635, commit `a6895a69f8ad98ab45777b03e9e6f48888c39f6f`:

| Local quantity | PR635 JP8 | Gauge44 |
|---|---:|---:|
| Helpers | 492 | 492 |
| Nonzero entrance frames | 204 | 204 |
| Rank-four cold ends | 22 | 44 |
| Rank-seven cold ends | 2 | 0 |
| Rank-eight cold ends | 4 | 0 |
| Entering helpers ending below FULL | 36 | 34 |
| Total residual helper width | 3894 | **3794** |
| Local paid rank mass | 5750 | **5650** |

Thus the new word saves **100 units of residual width per invocation** against the complete PR635 provider. It replaces that provider's cold-end construction; the old six higher-rank cold ends and two additional entering ends are not added to the new count.

The exact paid-child profiles are:

| Child rank | PR635 count | Gauge44 count |
|---:|---:|---:|
| 1 | 2518 | 2514 |
| 2 | 402 | 404 |
| 3 | 448 | 448 |
| 4 | 164 | 160 |
| 5 | 68 | 56 |
| 6 | 4 | 0 |
| 8 | 8 | 8 |

The final residual-width inventory is `{4:52, 5:48, 7:34, 8:114, 9:244}`. Both the profile and the inventory are recomputed from the literal native frame chains. They are not inferred from the nominal number of ended helpers.

## 2. What changes in the forward factory

The inherited K-triangle schedule and its 492-helper allocation remain the starting construction. Within each of the fourteen eight-source packet factories, three changes alter the arbitrary-dirt forward map while retaining the required clean packet values.

### A. Exchange a source with an equal clean copy

After the sixteen initial copy gates, local source position `j` and its two helper copies have clean values `(x_j,x_j,x_j)`. For positions `j = 4,5,6,7`, exchange the original source register with its second helper copy. The exact register pair in the constructor is `mp[j]` and `mp[2*j+9]`.

For arbitrary helper dirt the triple is instead

$$
(x_j,\;x_j+h_{j,1},\;x_j+h_{j,2}).
$$

The exchange changes where the second dirty direction enters the subsequent factory. It does not change any clean operand. Both exchanged registers already have the same rank-one frame, so the exchange adds no frame climb. Each exchange is emitted as three additions and one sign change; these scalar operations remain part of the finite implementation invoice.

This is a change of the forward map, not an output relabeling. In particular, the inverse recovery functional for the original source changes from the original branch to a different combination of the three equal-clean branches. That changes which cold input directions can have their entire final support inside a low frame.

### B. Change the complement to the four coordinate totals

Eight retired factory rows already span the eight source coordinates. The first four rows of their replacement basis are the four required coordinate totals. The remaining four rows are chosen by exact row-rank extension, first using the ordered clean linear forms recorded in `construction/COMPLETION-PRIORITY.json`, then using coordinate rows if an extension is still needed.

These candidate forms are the future low-frame leaver forms used during discovery. The frozen priority data are the complete input to the final constructor: no discovery search is run in reproduction. Every accepted row must increase the rational rank; the resulting eight-by-eight basis is explicitly applied by elementary operations.

All eight retired registers are already at the block's rank-four frame. Consequently this basis replacement also adds no frame climb. It gives the low final rows more independent linear combinations that annihilate the original source data.

### C. Place coordinate totals on the available source carriers

The retired registers are ordered with source registers first. Three available source carriers and one helper carry the four coordinate totals, leaving the four complementary rows on physical helper registers. This lets the new cold directions end on helper wires under the unchanged native endpoint interface.

A carrier permutation alone does not increase the available cold space. Its role here is to realize the independent directions created jointly by the source-copy exchange and the new complementary basis.

## 3. Exact cold-space calculation

Let `P` be the non-target forward matrix after parts A and B and the 34 inherited HPE tail gates. It has 604 rows and columns: 112 original sources and 492 helpers. Let `J` be the 316 protected initial columns consisting of the 112 original sources and all 204 entering helpers.

For a block frame `F`, let `I` be every non-target output register whose current frame is contained in `F`. Source output rows are included in this set. Define

$$
L=\operatorname{leftker} P[I,J],\qquad
K=\ker P^{-1}[J,I].
$$

Rows of `L` are low output linear forms with no protected initial dependence. Columns of `K` are low-supported output directions whose inverse images have no protected component. The rank of the pairing `LK` counts the simultaneously usable cold directions in this fixed forward word.

The changed forward map has the following exact block data:

| Block indices | Number of blocks | Low registers `|I|` | `dim L` | `dim K` | `rank(LK)` |
|---|---:|---:|---:|---:|---:|
| 0, 1, 2, 11, 12, 13 | 6 | 6 | 2 | 4 | **2** |
| 3 through 10 | 8 | 8 | 4 | 4 | **4** |

The count is therefore `6*2 + 8*4 = 44`. The fixed upstream rank-four cold construction supplied one and two directions respectively, for `6*1 + 8*2 = 22`.

The complement change by itself improves the available low annihilating rows but leaves the inverse-support obstruction. The source-copy exchanges remove that obstruction: `K` has dimension four in every block and pairs with all the available rows of `L`.

## 4. Realizing the directions with legal dyadic operations

`construction/build_gauge_cold44.py` recomputes these spaces over exact rational numbers. It selects columns of `K` and normalizes them to a matrix `U` satisfying

$$
LU=I_r,
\qquad q=P^{-1}[:,I]U.
$$

The constructor checks that `q` is supported entirely on that block's sixteen initially cold factory helpers, denoted `H_b`. Put

$$
R_b=LP[I,H_b].
$$

Then `R_b q[H_b,:] = I_r`. A sixteen-by-sixteen input basis `Q_b` places the columns `q[H_b,:]` at the designated ended-helper positions and fills the other columns with a basis of `ker R_b`. The resulting input basis is explicitly invertible.

For the low-frame output transformation, the ended-helper rows are replaced by the rows of `L`; each remaining low row `i` becomes

$$
e_i-U_iL.
$$

The actual chosen helper positions give an invertible tail matrix. Its nonsingularity and dyadic implementation are checked by exact elimination, rather than assumed from a dimension count. The construction receipt records every `Q_b`, tail matrix and selected endpoint.

Every `Q_b` is emitted at frame zero, at the head of A **after** the entry normalization wrappers. Every low tail is emitted at its block frame. The remaining cleanup is rebuilt as an exact dyadic Gauss-Jordan inverse on the non-ended registers at FULL. It is not obtained by blindly reversing a changed partial schedule.

Before forming the FULL inverse, the constructor verifies both the row and the column identity of each of the 78 ended helpers. Thus no protected data or other helper dirt remains in an ended helper, and its initial dirt remains nowhere else. The FULL inverse skips these isolated rows and columns entirely.

The realized word has:

| Construction component | Scalar gates |
|---|---:|
| Frame-zero helper premix | 1489 |
| New rank-four tail | 60 |
| Inherited HPE tail | 34 |
| Refactored FULL inverse | 28056 |
| Additional target compensation after wrappers | **0** |

All selected new cold directions have zero target response. The independent scalar auditor nevertheless recomputes the complete existing dirty-response compensation, obtaining 7348 additions, and checks both orientations on all 716 input columns.

Relative to the HPE-stage word before any cold-end construction, the aggregate chain delta is `N_1 += 44, N_6 -= 44`, reducing rank mass and residual width by 220. PR635 had already saved 120 units through its complete cold/extra-HPE construction. The net new saving is therefore 100. There is no omitted cost for lifting the low tails: their rank-one increments are included explicitly.

## 5. Native interface and validation

The transport preserves the exact ordered list of 112 ports and the exact ordered eight center frames. The center carriers change because some totals now reside on sources. In native coordinates they are

```
[92, 57, 81, 224, 11, 240, 9, 256]
```

A global interface check must compare the ordered center frames and port geometry, and use the provider's actual center carriers. Equality of carrier numbers with an old provider is not a mathematical requirement. The local event ledgers explicitly clear all private center channels in both orientations.

Completed checks for the frozen word include exact forward and inverse-transpose scalar replay on all 716 columns; every literal native frame chain; the 204 zero-response entrance conditions; the 44 cold and 34 entering endpoint cones; wrapper placement and normalized wrapper identities; both emitted local ledgers; and exact phase lowering for 3019 directed edges and 224 endpoint adapters. The independent audit does not import the new constructor.

This local result does not by itself certify a global exponent. Physical whole-family owners, actual residual/spectator routing, idle remainders, global scalar assembly and the complete finite invoice are the separate global checks reported elsewhere in the package.

## 6. Compact reproduction

Only Python's standard library is needed for this construction and the retained local pipeline. Do not use `python -O`. The reproduction driver checks byte hashes of every named upstream input and the changed code, then checks the content hash after each construction step. Its two source checkouts are:

| Argument | Repository commit |
|---|---|
| `--main` | `17ce0c79b7b51c2634b439ea5a2b754f09909693` |
| `--pr635` | `a6895a69f8ad98ab45777b03e9e6f48888c39f6f` |

Starting from a clone of `https://github.com/CrocSwap/integer-mult-bounds` containing those commits, prepare detached worktrees:

```bash
git -C integer-mult-bounds fetch origin main refs/pull/635/head
git -C integer-mult-bounds worktree add --detach ../integer-main 17ce0c79b7b51c2634b439ea5a2b754f09909693
git -C integer-mult-bounds worktree add --detach ../integer-pr635 a6895a69f8ad98ab45777b03e9e6f48888c39f6f
```

From the directory containing those worktrees and this delta package, run:

```bash
python -B research/gauge44-global/construction/reproduce.py \
  --main integer-main \
  --pr635 integer-pr635 \
  --out gauge44-reproduction
```

The default stops after regenerating the exact final scalar word and comparing the newly derived cold recipe with the frozen recipe. It rebuilds only the two short shadow steps needed by the four port transfers. It does not rerun the ancestor admission stack, search for a basis, optimize owners, or replay global assembly.

Use `--frozen-cold` to splice the included recipe instead of re-deriving its small exact linear systems. Use `--until local` to add native transport, emitted ledgers, independent local replay and wrappers. Use `--until phases` to add the complete phase lowering. Every invocation needs a fresh output directory; these are alternatives, not resumable increments. On the research machine, exact cold derivation took about 2.6 seconds, native transport/ledgers/replay/wrappers about 41 seconds, and complete phase lowering about 198 seconds.

The exact dependency chain is:

1. Construct the changed raw R492 factory from the pinned Hamming inputs, frozen priority and pinned K-triangle schedule.
2. Apply the four inherited port stages.
3. Apply the inherited B-frame regroup and 34-HPE construction.
4. Derive the exact block premixes, cold44 tails and FULL inverse.
5. Optionally emit and check the native ledgers, wrappers and complete phase lowering.

`construction/INPUTS.json` gives the input hashes and every intermediate content hash. The key decompressed content identities are:

| Word | SHA-256 |
|---|---|
| Changed raw factory | `0ac47f92fc2e3f5aa457d78f7b8a5c785bf140c546932b9dfcd9e610ad319180` |
| Changed HPE forward | `42fb8b3aa314593fe976820cf65824f5fce0ee4f95281796992d4809709864cc` |
| Final cold44 word | `78c7aadacb6eec2eeecc124ca236e5bcfdba6a52b30c2971aaa596d1d119b290` |
| Native canonical word | `e6daee410e04d5e023faf21144081534ad222d334ce786e6b5f52407e6b3c41f` |

## 7. Attribution

The original 504-helper factory and borrowed-register construction are icekylinx's PR531 lineage, prepared with OpenAI Codex/GPT assistance and retaining the earlier PR425/PR514 credits. The inherited K-triangle atom and frozen read schedule are credited in PR635 to AtomScout, a Claude Code research agent. The porting routine is credited there to Port480. This package does not claim those as new work.

The reused JP8 ancestry includes the PR558/PR552 supplier, the earlier-cut and multicold kernels, and the joint prefix adapted from Dominik Scholz's PR571 work. Native HPE and cold-end transport, frame and wrapper machinery come from the credited PR635 lineage, including DreamingOfClouds, jeremykothe2, chafreaky and their disclosed assistants. The retained `construction/UPSTREAM-NOTICE.md` and `construction/LICENSE` preserve the upstream notice and Apache-2.0 license.

The new contribution here is the combination of source-copy exchange, changed retired-row completion, source-carried coordinate totals, and the explicit exact cold44 realization. Those changes were developed for icekylinx with OpenAI GPT-6 Astra assistance. The upstream notices, proof scope and conditional assumptions continue to apply.
