# NATIVES: which word-level premises of the tree ceilings were computed on each word, and the script that computed it

The tree premises themselves (`Tr` out-trees `htreeA`, `htreeB`, `hcap`, `hnd`, `hP1`, `hP2`, `hcell`) were NOT checked on any word; see the end of the table section.

Five word files were checked against the word-level premises of `ceiling_tree_CG` and `ceiling_tree_GD` (the old ones are those of `ceiling_native_J`, #7668; the new ones are the junk count, the per-source partner bound and, for GD, the realised-edge set E48):

| name | word | file |
|---|---|---|
| st1 | the word of #7641 | `st1.json.gz` |
| w7637 | the #7637 word | `w7637.json.gz` |
| x1t2a | the x1t2a word | `x1t2a.json.gz` |
| e1 | the #7660 word | `e1.json.gz` |
| t7669 | our reproduction of the #7669 word (not the #7669 file itself) | `t7669.json.gz` |

All five share one port set of 104 odd-weight vectors (identical lists, same order; checked with `cmp`/`md5` on the `ports_*.txt` files extracted from the word files; no script beyond that command). The owned layers agree in mass 56 / 56 but not in shape: `t7669` has 23 rises / 23 descents and `len ks` = 36, the other four 23 / 24 and 37. Because of the shared port set the five words are close to one data point for the port-set-dependent facts (E48, the 230 shapes, the 48-cells law). **Lean treats every object in the two theorems as abstract and nothing in Lean ties a word to these hypotheses (in particular nothing ties `T`, `T.J` or `J` to a word).** The results below come from Python and C programs run on the five word files, one core each: exact integer / rational arithmetic, except that `aud.py` replays the arrival contents modulo two primes (2^61 - 1 and 2^64 - 59; both agree), so its outputs are modular, not exact-integer, computations. The programs and word files are not part of this package. "Result" means the premise as computed, not a Lean fact.

Programs. `aud.py`, `aud2.py`, `j13.py` and `e48.c` were re-run on all five words for this package; `aud2a.py` was re-run on e1 and t7669 only (the st1, w7637, x1t2a entries are reused from #7668); `hc12.py` was re-run on t7669 only (the st1, w7637, x1t2a, e1 entries are reused from #7668); `aud2d.py` (48-cells law) was NOT re-run for this package (reused from #7668; it depends on the port set only, and t7669 shares it). Two small scripts written for this package: `cmp.py` (E48 and Lean-mask comparison, below) and `cgcmp.py` (parses the Lean `Row` definitions of `cgR`, `gaR`, `gbR`). Outputs are identical across words where stated:
- `aud.py WORD PRIME` (p = 2^61 - 1 and p = 2^64 - 59, both agree): per-arrival content replay, `J^arr`, rank M, arrival vectors, even partners per row, non-nested owned moves, chart mismatches.
- `aud2.py WORD`: public register dimension sequences (hmono, hd9, hmix) and the owned rise/descent split.
- `aud2a.py WORD`: FIX-1 split (ks, mr), hmass, hmd, hmr, hY, owned moves, Cap class.
- `j13.py`: hF and hEex as exact identities of exponential polynomials, hst ingredients, Cap margin on s in [.9, 1 - tJ0].
- `hc12.py WORD`: `J^arr` and legal-path reachability for every junk cell.
- `aud2d.py`: the 48-cells law (max n*m over port-spanned subspaces of dimension <= 4). Reused from #7668, not re-run.
- `cmp.py`: loads the `e48.c` outputs and the `(i, dim, n, m, mask)` rows of the Lean `gaR` and `gbR` tables, decodes each row's `mask` bit by bit into the edge set `{(shape r, shape r') : mask(r) bit i(r') set}`, and compares: the 230 realised shapes equal the 230 Lean `(dim, n, m)` rows; the 48-port class equals the `gbR` edge set; each port's realised set is inside the `gaR` edge set. (Its Lean rows were read from a pickle extracted from the Lean text by an ad hoc step that was not kept as a script.)
- `cgcmp.py`: parses the rows straight from `CTree{cg,ga,gb}Defs.lean`; confirms 230 rows each with the same `(i, dim, n, m)`, `cgR` masks equal `gaR` masks (16,871 edges each), `gbR` has 11,043 edges and each `gbR` mask is a subset of the `gaR` mask. This is the only check of `cgR` (used by `ceiling_tree_CG`): it shows `cgR` has the same shapes and masks as `gaR`; no word or port set was run against `cgR` separately (the mask equality makes the `gaR` comparison apply).
- `e48.c` (new, independent of the earlier realised-edge program): for each port s and each of its 48 even partners t, all 29,212 subspaces of the 7-dimensional quotient u_t^perp / <u_s>, all 2,350,136 proper nested pairs X < Y, the shape (dim + 1, n, m) of each, and the union of the (shape X, shape Y) pairs over the 48 cells of s. Run on the `ports` list of each word file.

## Premise x word

| premise (Lean name) | st1 | w7637 | x1t2a | e1 (#7660) | t7669 (repro of #7669) | script |
|---|---|---|---|---|---|---|
| `T.hJcard`: \|J^arr\| >= 4962 | 4962 | 4962 | 4962 | 4962 | 4962 | `aud.py` (both primes), `hc12.py` |
| `T.hfib`: each source has <= 48 partners | 48 even partners per port (4992 even cells) | 48 | 48 | 48 | 48 | `aud.py` |
| `T.hScard`: <= 104 sources | 104 ports | 104 | 104 | 104 | 104 | `aud.py` |
| hmono, hd9 | 0 violations | 0 | 0 | 0 | 0 | `aud2.py` |
| hmix (<= 5) | 5 (tight) | 5 | 5 | 5 | 5 | `aud2.py` |
| hk, hmass, hmd, hmr | true; 102; 37; 10 | same | same | same | true; 102; 36; 10 | `aud2a.py` |
| hY (104 <= st + len ks + mr) | st = 1266: 1313 | 1313 | st = 1265: 1312 | 1312 | st = 1264: 1310 | `aud2a.py`, `j13.py` |
| hF, hEex (exact identities) | coefficient difference {} | {} | {} | {} | {} | `j13.py` |
| hst | gaps >= 1, every main moves | same | same | same | same | `j13.py` |
| owned layer (rises / descents, mass) | 23 / 24, 56 / 56 | 23 / 24 | 23 / 24 | 23 / 24 | 23 / 23, 56 / 56 | `aud.py`, `aud2a.py` |
| non-nested owned moves; chart mismatches | 0; 0 | 0; 0 | 0; 0 | 0; 0 | 0; 0 | `aud.py` |
| every J^arr cell has a legal owned-descent-free path | 0 cells without | 0 | 0 | 0 | 0 | `hc12.py` |
| Cap margin on s in [.9, 1 - tJ0] | 19.349538 | 19.349538 | 19.349538 | 19.349538 | 19.017022 | `j13.py` |
| 48-cells law (max n*m over port-spanned subspaces, dim <= 4) | 48 | 48 | 48 | 48 | 48 (same port set) | `aud2d.py` (depends on the port set only) |
| **E48** (GD): port classes by realised edge set | 24 / 32 / 48 ports with 10,729 / 10,619 / 11,043 edges | identical | identical | identical | identical | `e48.c`, `cmp.py` |
| **E48** = edge set of `gbR` (the mask of each `gbr_i`, decoded) | the 48-port class equals it exactly (11,043 edges) | same | same | same | same | `e48.c` + `cmp.py` (mask decoding) |
| every port's realised set is contained in the edge set of `gaR` (16,871 edges) | yes, all 104 | yes | yes | yes | yes | `e48.c` + `cmp.py` |

Reading the table against the Lean statements:
- E48 depends only on the port set. The five `ports` lists are identical (same order), so the five `e48.c` outputs are byte-identical (same md5). The shape list produced (230 shapes) has exactly the (dim, n, m) triples of the Lean rows. In Lean, `ceiling_tree_GD` assumes `|S| <= 104`, `Bset ⊆ S` with `48 <= |Bset|` (trees from `gbR`, `gbr0`) and trees from `gaR`, `gar0` for `S \ Bset` (`ceiling_tree_CG` uses `cgR`, `cgr0` for all sources). The check shows that the 48 ports of one class have a realised edge set equal to the `gbR` mask, and the other 56 ports have realised sets inside the `gaR` mask. Which sources go in `Bset` is part of the hypothesis `T`.
- The count behind E48 (a (3,4,12) chart and a (5,8,6) chart cover only 1,344 of the 4,992 even cells) was not recomputed here, no script of this package checks it, and it is not in Lean; `e48.c` recomputes the edge sets themselves, which is what `gbR` encodes.
- The edge sets were computed over all 4,992 even cells, a superset of J^arr (4,962 cells), so they are an upper set of the realised edges of the junk cells; that direction is the sound one for a relaxation.
- `hcong`, `hdist`, `hspMono`, `hcstMono`, `hcstMonoT`, the spF / cst brackets (`hcst0`, `hcst1`, `hspTab*`, `hcstTab*`) are word-independent or paper statements, as in #7668. **The tree premises `Tr` out-trees (`htreeA`, `htreeB`), `hcap`, `hnd`, `hP1`, `hP2`, `hcell` are open hypotheses: no script was run to check them on any of the five words, and none is verified.** The same holds for the remaining `TreeData` fields that concern trees and charges (`hMv`, `hMsub`, `hdim`, `hxk`, `x`, `R`, `ms`); `hJS`, `hB`, `hBcard` and `T.J`, `T.S` are likewise not tied to a word in Lean (only the counts 4962, 48, 104 were computed, in the table). `e48.c` checks all nested quotient pairs on 4,992 even cells, not the arrival trees of any word. The premises are the paper premises (nested moves, the I2 capacity n(A) per move, the I2 charge aggregated by moves) in the form of `PROVED.md`. This table therefore does not show that any word satisfies all hypotheses of the tree theorems.
- On t7669, `aud2d.py` was not run (port set only), and `hc8.py`, `hc11.py`, `aud2c.py` (forced cells, decoder-route ranks, informational route checks) were not run; none is a premise of the two theorems except through the table rows above.

## What is not covered

- Words with |J^arr| < 4962 and decoders that are not rank 8 with C = 56: outside `hJcard` as stated (the class-wide bound is a conjecture, as in #7668).
- Decoders with 9 or more rows: `ceiling_native_J` hard-codes `corrC <= 8 * cH` and `capC >= unLo / 48`, and the tree theorems inherit this.
- That the tree premises hold for any word, these five included, is not checked.
- Port sets other than the one 104-port set: the 230 shapes, `E48` and the 48-port class were computed for this port set only. `hmix` is 5 (tight) on all five words, so a word with `hmix > 5` is outside the hypotheses.
