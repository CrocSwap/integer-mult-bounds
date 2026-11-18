# NATIVES: which word-level premises of the reader ceilings were computed on each word, and the script and method that computed it

Five word files were checked against the word-level premises of `ceiling_reader_GD`, `ceiling_reader_GD_w10` and `ceiling_reader_GD_w16` (the inherited ones are those of `ceiling_native_J`, #7668, and of #7678; the new ones are the reader/tied-register facts, the owned-layer facts behind `omega`, and the paper figures):

| name | word | file |
|---|---|---|
| st1 | the word of #7641 | `st1.json.gz` |
| w7637 | the #7637 word | `w7637.json.gz` |
| x1t2a | the x1t2a word | `x1t2a.json.gz` |
| e1 | the #7660 word | `e1.json.gz` |
| t7669 | our reproduction of the #7669 word (not the #7669 file itself) | `t7669.json.gz` |

All five share one port set of 104 odd-weight vectors and are close to one data point for port-set-dependent facts. They differ in the owned layer: `t7669` has 23 rises / 23 descents (46 owned moves), the other four 23 / 24 (47); `w7637` has 233 INIT = CLEAR pairs, `t7669` 235, the other three 234; `w7637` holds G' tokens in 24 more owned CLEARs at dim 9 (42 token-bearing CLEARs against 18). **Lean treats every object in the three theorems as abstract; nothing in Lean ties a word to these hypotheses (in particular not `T`, `T.S`, `T.J`, `Q`, `Uo`, `π`, `ω`).** "Result" means the premise as computed, not a Lean fact. Not-run items are listed at the end.

Scripts and methods (all are Python 3 with exact integer / rational arithmetic unless stated; one core each; none is part of this package, the word files are not either):
- `own.py WORD` (written for this package, independent of the lane scripts): public register chart sequences from the MOVE events; `hmono` (non-strict and strict), `hd9`; the mixed set (`1 <= d r 0` and `d r end <= 8`, the Lean `Mixed`); births and ends of X, X2, Y; the Lean `Tied` predicate on every public register; for each reader t the set of Tied registers whose chart list contains Y_t's final dim-8 chart, and a maximum bipartite matching (augmenting paths) of readers to such registers (the existence of the injective `π` of `hπinj`); registers visiting more than one dim-8 chart; the owned layer: INIT / CLEAR counts, last event of every owned register, owned moves by (source dim, target dim), moves from dim <= 7 to dim 9, moves into dim-8 charts.
- `f2chk.py WORD` (re-run; written for the F2* count): exact replay of G'-token rows modulo p (p = 2^61 - 1 and, as a copy with p = 2^64 - 59, both give identical output on all five words): G' = public helpers born at dim >= 2 (230); B-exit rows; `omega := |G'| - rank pi(G' and P exit rows)`; TL-b (no register ending below V holds a foreign G' token) and TL-a's public clause. A rank modulo p is at most the rank over Q, so `omega = 0` modulo p implies `omega = 0` over Q. Its last printed line is labelled "omega = rank pi(owned exit rows)" and shows 16 (35 on w7637); that label is misleading: the quantity that defines `omega` is the line before it ("rank pi(G' + P rows) 230 = |G'|", hence `omega = 0`); 16 and 35 are the ranks of the owned rows alone, which the argument for `omega <= 10` bounds differently (CLEAR rows contribute nothing).
- `a1.py` (re-run, word list extended by w7637): roles and births of every main, the mixed list, and per reader the registers tied to its final chart with `R = (sum of |beta| steps - beta(birth) - beta(end)) / 2 >= delta` (floating point, `delta = 7^s + 2^s - 8^s - 1` at s = 1 - .0118103 = .018734).
- `tp1.py WORD PRIME` (re-run, both primes 2^61 - 1 and 2^64 - 59; output identical): `J^arr` and the OUT-side tree premises of #7678 (Tr out-trees under `cgR`, `gaR`, `gbR`, `hnd`, `hcap`, `hMv`, `hdim`, `hcell`, `hxk`, `hJS`, `hfib`, `hScard`, `hB`, `hBcard`, `hMsub`, and the word side of `hP1`). The word side of `hP1` samples `Omega - sum of owned-rise c2` at points of the window; for the reader window (lower end `a0RD` = .0115262, i.e. s up to .9884738) a copy with the point set (.9881897, .98832, .98845, .9884738), spacing at most 1.3e-4, gives a minimum of 47.42 (47.38 on t7669) against a Lipschitz loss of at most .37.
- `a2.py t NMIX` and `c3f.py` (re-run; `c3f.py` = the master-LP script with `READER=1`, `NDL` as the allowance, `TREE=1 SIDE=two MODE=own56 M=5`, about 3 minutes each): at t = .0118103, OUT 29.7252, IN = sum H_t = 29.6542, delta .018734, c18 .035040, capv .020074, IN' = 31.5089 (5 allowances), 31.3215 (15), 31.2091 (21); the largest `H_t / (K_t min(c18, capv))` is .3109 and no reader is on the dim-1 branch. Ceiling for `NDL = 15, 25, 31`: .011525000780, .011541666284, .011551595956. These are float computations of the master problem (the paper figures); the Lean digits are the certified ones.

## Premise x word

| premise (Lean name) | st1 | w7637 | x1t2a | e1 (#7660) | t7669 (repro of #7669) | script |
|---|---|---|---|---|---|---|
| `hmono` (strict: no equal or falling dims), `hd9` | 0 violations | 0 | 0 | 0 | 0 | `own.py` |
| `hmix` (<= 5) | 5 (tight), all helpers | 5 | 5 | 5 | 5 | `own.py`, `a1.py` |
| mains X (104), X2 (96): born at dim 1, V-class (end 9) | yes | yes | yes | yes | yes | `own.py`, `a1.py` |
| Y (104): born at dim 0, end at dim 8 | yes | yes | yes | yes | yes | `own.py`, `a1.py` |
| Lean `Tied` registers (public) | 427 | 427 | 427 | 427 | 427 | `own.py` |
| each reader has a tied register on its final chart; injective choice (`hπR`, `hπinj`, `hTied`) | matching 104 / 104; 104 distinct final charts | 104 / 104 | 104 / 104 | 104 / 104 | 104 / 104 | `own.py` (matching), `a1.py` (payer with `R >= delta`) |
| every register visits at most one dim-8 chart | 0 exceptions | 0 | 0 | 0 | 0 | `own.py` |
| owned lifetimes end in CLEAR (INIT = CLEAR; last event of every owned register) | 234 = 234; 52 / 52 | 233 = 233; 52 / 52 | 234 = 234; 52 / 52 | 234 = 234; 52 / 52 | 235 = 235; 53 / 53 | `own.py` |
| owned moves from dim <= 7 to dim 9 (none needed for `omega <= 10`) | 0 | 0 | 0 | 0 | 0 | `own.py` |
| owned moves into dim-8 charts (`<= 10` owned last movers) | 8 (all from dim <= 7) | 8 | 8 | 8 | 8 | `own.py` |
| owned layer: rises / descents, mass up / down | 23 / 24, 56 / 56 | same | same | same | 23 / 23, 56 / 56 | `own.py` |
| `omega = |G'| - rank pi(G' and P exit rows)` (`hω : ω <= 0`) | 0 (rank 230 = \|G'\| = 230) | 0 | 0 | 0 | 0 | `f2chk.py` (both primes) |
| TL-b: no register ending below V holds a foreign G' token; all Y_t clean | 0 violations | 0 | 0 | 0 | 0 | `f2chk.py` |
| TL-a public clause | 0 violations | 0 | 0 | 0 | 0 | `f2chk.py` |
| TL-a "only public registers hold e_g" (NOT used) | fails: 15 owned registers hold tokens | fails: 28 | fails: 15 | fails: 15 | fails: 15 | `f2chk.py` |
| every high reader has a payer in S_t (a check of the false F2 form, for information) | 104 / 104 | 104 / 104 | 104 / 104 | 104 / 104 | 104 / 104 | `f2chk.py` |
| OUT-side tree premises of #7678 (`htreeA/B`, `hnd`, `hcap`, `hcell`, `hxk`, `hJS`, `hfib`, `hScard`, `hB`, `hBcard`, `hMsub`, `hdim`), \|J^arr\| = 4962 | PASS, trees valid under `cgR`, `gaR`, `gbR`: 104 / 104; max usage / n(A) = 1.0 | PASS | PASS | PASS | PASS | `tp1.py` (both primes) |
| word side of `hP1` on `[a0RD, tJ0]`: `Omega - sum c2(owned rises)` | >= 47.42 (loss <= .37) | same | same | same | >= 47.38 | `tp1.py` (point set extended) |
| `hcstLo`: `0 <= cstF` on the window | not a word fact | | | | | a paper statement, now a hypothesis (it follows from `cst(t) >= c2(7,8) > 0`) |
| `hP2` residue `0 <= cstF` | not a word fact (`Mun` empty on all five) | | | | | `tp1.py` |
| paper ceiling for NDL 15 / 25 / 31 | .011525000780 / .011541666284 / .011551595956 (word-independent master problem at the tabulated `K_t`, `H_t`) | | | | | `c3f.py` |

Inherited premises (`hk`, `hmass`, `hmd`, `hmr`, `hY`, `hF`, `hEex`, `hst`, the Cap margin, `hcong`/`hdist` support, the 48-cells law, E48): taken from `NATIVES.md` of #7678 and #7668; not re-run here.

## Not covered, not run
- The IN-side analogues of the tree premises (`T` for the readers, the I-class edge set of the 48-port readers, the reflection symmetry of the DP table): not extracted from any word and not enumerated; the OUT-side premises above are what was run. The Lean-kernel IN tables differ from the OUT tables in 18 of 230 rows of the I-class set, with the same root value.
- `omega <= 10` for the class: proved on paper only; on the five words `omega = 0`. A word with an owned rise from dim <= 7 into V, or an owned lifetime that does not end in a CLEAR, is outside the premises.
- Words other than these five; port sets other than the one 104-port set; decoders other than rank 8 with C = 56 (`ceiling_native_J` hard-codes `corrC <= 8 cH`, `capC >= unLo / 48`).
- `hmix = 5` is tight on all five words.
