# Complete multi-donor, multi-writer helper-star absorption linear system and star-leaf-injection gain-0 chaining census under fixed frames

**Scoped replacement-interface census and linear-algebraic exclusion; no new $\kappa$.** The selected result (`certificates/selected-result.json`), the selected bit supplier (`https://github.com/CrocSwap/integer-mult-bounds/pull/589`), and `upstream/` are unchanged.

Under the twisted helper contract (`H2-tw / H4-tw / K-tw` of Sagar Thakrar's [https://github.com/CrocSwap/integer-mult-bounds/pull/1868](https://github.com/CrocSwap/integer-mult-bounds/pull/1868), head `6b222d01fee072bcd3a680e6a96ae7d22e13bcac`), omitting a subset $L_a \neq \emptyset$ of terminal `D` helper-star restorations on a centre $a$ leaves $a$ twisted by $d_a = \bigoplus_{b \in L_a} e_b$ at the `D/A` boundary. Toggling donor subsets $D_i$ across existing pre-first-read `A` writes $i \in W(a)$ to $a$ restores $a$ before its first read—and therefore preserves the exact 661-column arbitrary-dirty boundary $(x, y, h) \mapsto (x, y + x, h)$ with the parent's literal cleanup `C` unchanged—if and only if the binary indicator vector $c \in \mathbb{F}_2^{|P(a)|}$ over the frame-legal donor pool $P(a) = \{(i, r) : i \in W(a),\ r \text{ legal at } A[i]\}$ satisfies

$$\sum_{(i, r) \in P(a)} c_{i, r}\,\operatorname{val}_i[r] = d_a \quad \text{in } \mathbb{F}_2^{661},$$

with exact net scalar ADD change

$$\Delta\text{ADDs}(c) = -|L_a| + \sum_{(i, r) \in P(a)} w_{i, r}\,c_{i, r}, \qquad w_{i, r} = \begin{cases}-1 & \text{if } r \in S_i,\\ +1 & \text{if } r \notin S_i.\end{cases}$$

Open [https://github.com/CrocSwap/integer-mult-bounds/pull/1868](https://github.com/CrocSwap/integer-mult-bounds/pull/1868) tested single-writer substitutions ($|W'(a)| = 1$) and left open multi-gate splits of $S$ and chaining the gain-0 moves. Open [https://github.com/CrocSwap/integer-mult-bounds/pull/1913](https://github.com/CrocSwap/integer-mult-bounds/pull/1913) (Adam Gall, head `6cde2d14f0090f51672feae32a04f3145e70f595`) excluded two-writer single-donor-per-writer corrections ($|D_i| = |D_j| = 1$) on the 11,500-ADD word and left open arbitrary multi-donor correction sets over full-itinerary-legal donors.

This package solves the complete unconstrained-size multi-donor, multi-writer $\mathbb{F}_2$-linear system across all pre-first-read writers ($1 \le |W(a)| \le 5$) on all three repository-pinned R439 helper-star words:

- `pr967`: `research/r439-helper-stars-seed19/candidate.json.gz` ([https://github.com/CrocSwap/integer-mult-bounds/pull/967](https://github.com/CrocSwap/integer-mult-bounds/pull/967), 11,783 ADDs, 221 star edges, 157 centres: 93 one-leaf, 64 two-leaf);
- `pr1062`: `research/r439-bsection-stars-seed01/candidate.json.gz` ([https://github.com/CrocSwap/integer-mult-bounds/pull/1062](https://github.com/CrocSwap/integer-mult-bounds/pull/1062), 11,500 ADDs, 236 star edges, 162 centres: 88 one-leaf, 74 two-leaf);
- `pr1122`: `research/r439-abc-semantic-bridge/inputs/candidate.json.gz` ([https://github.com/CrocSwap/integer-mult-bounds/pull/1122](https://github.com/CrocSwap/integer-mult-bounds/pull/1122) / [https://github.com/CrocSwap/integer-mult-bounds/pull/1311](https://github.com/CrocSwap/integer-mult-bounds/pull/1311), 10,652 ADDs, 236 star edges, 162 centres: 88 one-leaf, 74 two-leaf).

## Complete linear-system census

We evaluate two fixed-frame donor pools at every pre-first-read write $i \in W(a)$ (with gate frame $f_i$):

1. `same_path` (full-itinerary-legal): $r \neq a$ is a source or helper whose inclusion at $A[i]$ leaves all 661 ordered register frame paths `frame_paths(w)` and the paid profile `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}` (rank mass `5,129`) identical (`pre_frame[i][r] == f_i`, or $r \in S_i$, or `pre_frame[i][r] < f_i` and `next_touch[i][r] == f_i`).
2. `monotone_all` (monotone-climb-legal): $r \neq a$ is any source or helper whose current and next frames satisfy $\operatorname{span}(F_{\text{pre}}(i,r)) \subseteq \operatorname{span}(F_{f_i}) \subseteq \operatorname{span}(F_{\text{next}}(i,r))$.

| Word | Mode | Star edges | Two-leaf centres | Pool pairs $\sum_a |P(a)|$ | Zero-bit $b$ | Nonzero-bit unsolvable | Solvable single edges | Solvable two-leaf pairs | Extra from chaining | Dual witnesses |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `pr967` (11,783) | `same_path` | 221 | 64 | 1,287 | 147 | 69 | **5** | **0** | **0** | — |
| `pr967` (11,783) | `monotone_all` | 221 | 64 | 1,744 | 146 | 70 | **5** | **0** | **0** | 280 |
| `pr1062` (11,500) | `same_path` | 236 | 74 | 1,412 | 158 | 73 | **5** | **0** | **0** | — |
| `pr1062` (11,500) | `monotone_all` | 236 | 74 | 1,894 | 157 | 74 | **5** | **0** | **0** | 305 |
| `pr1122` (10,652) | `same_path` | 236 | 74 | 1,484 | 134 | 97 | **5** | **0** | **0** | — |
| `pr1122` (10,652) | `monotone_all` | 236 | 74 | 2,013 | 133 | 98 | **5** | **0** | **0** | 305 |

### Exact findings

1. **Dual hyperplane certificates for all unsolvable single-leaf and two-leaf targets.** Placing $P_{\text{mono}}(a)$ in reduced row echelon form over $\mathbb{F}_2^{661}$ certifies that 216 of 221 single edges on `pr967` and 231 of 236 single edges on `pr1062` and `pr1122`, plus all 64 (`pr967`) and 74 (`pr1062`, `pr1122`) simultaneous two-leaf omissions $d_a = e_{b_1} \oplus e_{b_2}$, lie outside $\operatorname{span}_{\mathbb{F}_2}(P_{\text{mono}}(a))$. Every unsolvable target (890 total across the three words) carries an explicit canonical dual functional $u \in \mathbb{F}_2^{661}$ in `CERTIFICATE.json` with $\langle u, d_a \rangle = 1 \pmod 2$ and $\langle u, \operatorname{val}_i[r] \rangle = 0 \pmod 2$ for all $(i, r) \in P_{\text{mono}}(a)$. In particular, for the two-writer scalar witness `231 ^= 459` of [https://github.com/CrocSwap/integer-mult-bounds/pull/1913](https://github.com/CrocSwap/integer-mult-bounds/pull/1913) (`writers = [9, 527]`), donor `459` at `A[527]` holds $e_{459} \oplus e_{109}$ while source `109` is outside `A[9]` and `A[527]`'s frames; the two-bit dual functional $u = e_{109} \oplus e_{459}$ annihilates all 13 monotone-legal `(writer, donor)` pairs in $P_{\text{mono}}(231)$ and evaluates to $1$ on $e_{459}$.
2. **Complete affine solution spaces for the five solvable edges.** Across all three words and both frame modes, the only solvable edges are the three gain-1 edges of [https://github.com/CrocSwap/integer-mult-bounds/pull/1868](https://github.com/CrocSwap/integer-mult-bounds/pull/1868) and two gain-0 edges:

| Edge $a \mathrel{\oplus}= b$ | `pr1062` $W(a)$ | `same_path` pool / rank / solutions | `monotone_all` pool / rank / solutions | Min $\Delta\text{ADDs}$ | Canonical `same_path` toggle witness $(i, r, r \in S_i)$ |
|---|---|---|---|---:|---|
| `514 ^= 367` | `[304]` | `3 / 3 / 1` | `4 / 4 / 1` | `-1` | `(304, 360, False), (304, 367, True)` |
| `506 ^= 374` | `[288, 1033..1036]` | `24 / 9 / 32,768` | `26 / 11 / 32,768` | `-1` | `(288, 69, False), (288, 374, True)` |
| `507 ^= 355` | `[290, 989..992]` | `24 / 9 / 32,768` | `30 / 12 / 262,144` | `-1` | `(290, 72, False), (290, 355, True)` |
| `264 ^= 536` | `[38, 346]` | `5 / 5 / 1` | `9 / 7 / 4` | `0` | `(346, 536, False)` |
| `326 ^= 530` | `[98, 334]` | `4 / 4 / 1` | `7 / 6 / 2` | `0` | `(334, 530, False)` |

   Exhausting all $2^{\dim \ker}$ affine solutions shows that single-edge corrections built from multi-donor and multi-writer splits never reach $\Delta\text{ADDs} \le -2$ on `506 ^= 374`, `507 ^= 355`, or `514 ^= 367` (the 256 minimum-cost solutions on `506` and `507` under `pr967`/`pr1062` arise from cancelling pairs of identical donor states across the consecutive same-frame writes `1033..1036` and `989..992`), and never reach $\Delta\text{ADDs} \le -1$ on `264 ^= 536` or `326 ^= 530`. This covers each edge's own defect restored through its own frame-legal donors; multi-centre corrections that consume intermediate defect vectors of in-flight multi-write corrections are outside this census (see [Scope limits](#scope-limits-and-remaining-obligations)).
3. **Why the early `monotone_all` gain-0 solutions are strictly worse on the paid profile.** For `264 ^= 536` and `326 ^= 530`, `same_path` admits a unique solution (`A[346]` at rank-2 frame 153 for `536`, and `A[334]` at rank-2 frame 147 for `530`), where the leaf is already scheduled to climb `0 -> 2 -> 8`. The additional `monotone_all` solutions at `A[38]` (rank-1 frame 21) and `A[98]` (rank-1 frame 51) insert an intermediate rank-1 station (`0 -> 1 -> 2 -> 8`), replacing one $H_2$ child by $2 H_1$ in the paid profile (`{1:1325, 2:1341, ...}`, child count `2,920 -> 2,921` at fixed rank mass `5,129`).
4. **Cross-centre chaining and composed 5-edge words.** Even if any unread star centre $a' \in P_{\text{mono}}(a)$ ($i < \text{first\_read}(a')$) is allowed to inject arbitrary combinations of its own star leaves $\{e_{b'} : (a', b') \in E\}$ into $a$, adjoining all such leaf vectors to $P_{\text{mono}}(a)$ yields **zero** new solvable single-leaf or two-leaf targets on all three words. The chained pool adjoins only these original star-leaf vectors; intermediate defect vectors of in-flight multi-write corrections at other centres (twist plus partial donor-toggle sums) are generally different vectors and are not modelled (see [Scope limits](#scope-limits-and-remaining-obligations)). Composing the three gain-1 moves with both `same_path` gain-0 moves (`composed_all_5`, 5 twisted centres) leaves ADDs (`11,780`, `11,497`, `10,649`), forward/reverse integer bounds `F / B` (`72,831 / 10,356,226`, `25,717 / 5,858,638`, `15,223 / 3,897,422`), local/nine-stage guard bits (`102 / 192`, `95 / 182`, `91 / 176`), frame paths, and paid profile mass `5,129` identical to the 3-edge composition (`composed_gain1_3`).

## Reproduce

From the repository root, using Python 3.12 (standard library only):

```sh
python3.12 scripts/research_package.py --package research/r439-multi-donor-star-absorption --check-only
python3.12 scripts/research_package.py --package research/r439-multi-donor-star-absorption
```

Direct execution (also passes under `-O`):

```sh
python3.12 -I -B research/r439-multi-donor-star-absorption/verify.py
python3.12 -I -B research/r439-multi-donor-star-absorption/test_package.py -v
```

Expected output line from `verify.py`:

```text
PASS_R439_MULTI_DONOR_STAR_ABSORPTION words=3 edges=221,236,236 pr1062_pools=1412/1894 solvable=5 two_leaf=0 chained_extra=0 duals=305 ADDs=11500->11497 controls=10 no_new_kappa
```

## Scope limits and remaining obligations

- **No $\kappa$ or frontier claim.** The bit supplier does not bind, and no candidate word is promoted to the selected record.
- **Unrun obligations.** Native 5/9/11-stage C++/Boost replay (covered for the 3-edge words by Hanson Sun's open [https://github.com/CrocSwap/integer-mult-bounds/pull/1902](https://github.com/CrocSwap/integer-mult-bounds/pull/1902)), whole-call hosted emission/invoice, all-size compiler/common-label realization, precision/tape rounding, and outer analytic transfer are not run here.
- **Boundary of the exclusion.** The linear-system exclusion applies to pre-first-read `A` writes to the star centre under fixed gate frames and unchanged literal `C`. It does not cover edits that cross a read of the twisted centre and simultaneously compensate downstream reader gates, or edits that rebuild `B`/`C` or alter gate frames.
- **Cross-centre chaining coverage.** The cross-centre chaining check adjoins only the original star-leaf vectors $\{e_{b'}\}$ of unread centres. A centre under an in-flight multi-write correction carries intermediate defect vectors (twist plus partial donor-toggle sums) that are generally not star-leaf vectors, and injections of such vectors into another centre's correction are not covered by the checked pools. The exclusion of cross-centre chained absorptions is therefore proved only for star-leaf-vector injection.

## Open next questions

- **Question:** Can absorbing a `D` helper-star restoration *after* the centre's first `A` read succeed by simultaneously compensating the downstream reader gates under fixed frames?
- **Why it matters:** Within the checked model — star-leaf defects $d_a = e_b$ or $e_{b_1} \oplus e_{b_2}$ corrected by pre-first-read frame-legal donor toggles at one centre at a time, with cross-centre injection limited to original star-leaf vectors — the five edges certified here are the only solvable absorptions. Intermediate defect vectors from in-flight multi-write corrections at other centres are generally different vectors and are not covered (see [Scope limits](#scope-limits-and-remaining-obligations)), so this census does not prove that every further twisted-`D` absorption into `A` must cross at least one read of the twisted centre.
- **Feasible first step:** For each star edge $(a, b)$ whose first `A` read is a single-target `z`-write $A[r_0]$ ($c \mathrel{\oplus}= a$), propagate the defect to the two-register state $(a, c)$ and test whether $e_b$ lies in the joint frame-legal donor span before the next read of $a$ or $c$.
- **Blocker:** Crossing a read of $a$ branches the defect into every reader register, requiring simultaneous multi-register restoration before any reader feeds a retained total at the scatter.

## Credit

Prepared by **Aaron Wang**, with help from opencode. Apache-2.0.

Credit **Sagar Thakrar** ([https://github.com/CrocSwap/integer-mult-bounds/pull/1868](https://github.com/CrocSwap/integer-mult-bounds/pull/1868) for the twisted helper contract `H2-tw / H4-tw / K-tw`, the single-writer absorption census, and the multi-gate/gain-0 open question; [https://github.com/CrocSwap/integer-mult-bounds/pull/1062](https://github.com/CrocSwap/integer-mult-bounds/pull/1062) for `r439-bsection-stars-seed01`), **Adam Gall** ([https://github.com/CrocSwap/integer-mult-bounds/pull/1913](https://github.com/CrocSwap/integer-mult-bounds/pull/1913) for the two-writer single-donor exclusion on `PR1062` and the multi-donor open question), **Hanson Sun** ([https://github.com/CrocSwap/integer-mult-bounds/pull/1902](https://github.com/CrocSwap/integer-mult-bounds/pull/1902) for native replay of the `PR1868` words), **woklerx** ([https://github.com/CrocSwap/integer-mult-bounds/pull/1194](https://github.com/CrocSwap/integer-mult-bounds/pull/1194) for `H2-sem`), **Arham Tahir** ([https://github.com/CrocSwap/integer-mult-bounds/pull/1311](https://github.com/CrocSwap/integer-mult-bounds/pull/1311), [https://github.com/CrocSwap/integer-mult-bounds/pull/1580](https://github.com/CrocSwap/integer-mult-bounds/pull/1580), [https://github.com/CrocSwap/integer-mult-bounds/pull/1592](https://github.com/CrocSwap/integer-mult-bounds/pull/1592)), **Gareth Davidson** ([https://github.com/CrocSwap/integer-mult-bounds/pull/915](https://github.com/CrocSwap/integer-mult-bounds/pull/915), [https://github.com/CrocSwap/integer-mult-bounds/pull/926](https://github.com/CrocSwap/integer-mult-bounds/pull/926), [https://github.com/CrocSwap/integer-mult-bounds/pull/1122](https://github.com/CrocSwap/integer-mult-bounds/pull/1122)), **Sricharan Vagvala** ([https://github.com/CrocSwap/integer-mult-bounds/pull/967](https://github.com/CrocSwap/integer-mult-bounds/pull/967)), **Ross Richardson** ([https://github.com/CrocSwap/integer-mult-bounds/pull/923](https://github.com/CrocSwap/integer-mult-bounds/pull/923)), **DreamingOfClouds** ([https://github.com/CrocSwap/integer-mult-bounds/pull/589](https://github.com/CrocSwap/integer-mult-bounds/pull/589)), **eumemic** ([https://github.com/CrocSwap/integer-mult-bounds/pull/555](https://github.com/CrocSwap/integer-mult-bounds/pull/555), `xcheck_p.py`), and **Zhihao Chen** ([https://github.com/CrocSwap/integer-mult-bounds/pull/425](https://github.com/CrocSwap/integer-mult-bounds/pull/425)).
